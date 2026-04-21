"""
cli.py — Command-line interface for pdf_extractor.

Usage:
  python -m pdf_extractor <input> [options]

Examples:
  python -m pdf_extractor doc.pdf
  python -m pdf_extractor docs/*.pdf --output-dir ./output --workers 4
  python -m pdf_extractor doc.pdf --features text_fast,tables --format json
  python -m pdf_extractor doc.pdf --profile
  python -m pdf_extractor doc.pdf --dry-run
  python -m pdf_extractor doc.pdf --quality-threshold 80
"""

from __future__ import annotations

import argparse
import glob
import json
import sys
import time
from pathlib import Path

import importlib.util

from .core import progress as prog
from .core import cache, preflight, detector
from .core.pipeline import run as pipeline_run, dry_run_plan, select_features
from .core.platform import detect as platform_detect
from .output import assembler, frontmatter, fixer, validator

# Map feature name → Python package that must be importable for it to work.
# Features not listed here (text_fast, markdown_llm, tables) rely on packages
# that are declared as base requirements and assumed to be present locally.
_FEATURE_DEPS: dict[str, str] = {
    "ocr_tesseract":  "pytesseract",
    "ocr_easy":       "easyocr",
    "ocr_img2table":  "img2table",
    "tables_camelot": "camelot",
    "tables_tabula":  "tabula",
    "docling_feat":   "docling",
    "markitdown_feat":"markitdown",
}


def _missing_local_features(names: list[str]) -> list[str]:
    """Return features whose required package is not importable locally."""
    return [
        n for n in names
        if (dep := _FEATURE_DEPS.get(n)) and importlib.util.find_spec(dep) is None
    ]


def main(argv: list[str] | None = None) -> int:
    args = _parse(argv)

    prog.configure(json_mode=(args.format == "json"))

    # Resolve input files (supports glob)
    pdf_files = _resolve_inputs(args.input)
    if not pdf_files:
        print(f"ERROR: No PDF files found matching: {args.input}", file=sys.stderr)
        return 1

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    platform = platform_detect()
    forced_features = [f.strip() for f in args.features.split(",")] if args.features else None

    # --docker flow: ensure Docker then delegate
    if args.docker:
        from .core.docker_setup import ensure_docker, run_in_docker
        if not ensure_docker(platform):
            return 1
        extra = _build_extra_args(args)
        for pdf_path in pdf_files:
            rc = run_in_docker(pdf_path, str(output_dir), extra, platform)
            if rc != 0:
                return rc
        return 0

    results = []
    exit_code = 0
    total = len(pdf_files)

    for idx, pdf_path in enumerate(pdf_files, 1):
        if total > 1:
            prog.emit({"event": "batch_progress", "current": idx, "total": total,
                       "file": Path(pdf_path).name})
        rc, result = _process_one(pdf_path, output_dir, platform, args, forced_features)
        if rc != 0:
            exit_code = rc
        if result:
            results.append(result)

    if args.format == "json" and results:
        print(json.dumps(results if len(results) > 1 else results[0],
                         ensure_ascii=False, indent=2))

    return exit_code


# ---------------------------------------------------------------------------
# Single-file processing
# ---------------------------------------------------------------------------

def _process_one(
    pdf_path: str,
    output_dir: Path,
    platform,
    args,
    forced_features,
) -> tuple[int, dict | None]:

    file_label = Path(pdf_path).name

    # --- Pre-flight ---
    pf = preflight.run(pdf_path)
    for w in pf.warnings:
        prog.error(file_label, w)

    if not pf.ok:
        for err in pf.errors:
            prog.error(file_label, err)
        if pf.is_encrypted:
            prog.emit({"event": "error", "reason": "encrypted", "file": file_label})
        return 1, None

    prog.start(file_label, pf.page_count)
    prog.preflight(file_label, "ok", is_scanned=pf.is_scanned)

    # --- Cache check ---
    mode = ",".join(forced_features) if forced_features else "auto"
    cache_key = cache.compute_key(pdf_path, mode) if not args.no_cache else None

    if cache_key and cache.hit(cache_key):
        prog.cache_hit(file_label, cache_key)
        md, meta = cache.load(cache_key)
        output_path = output_dir / (Path(pdf_path).stem + ".md")
        if args.format in ("md", "both"):
            output_path.write_text(md, encoding="utf-8")
        prog.done(file_label, str(output_path), meta.get("features_used", []))
        if args.format == "json":
            return 0, _build_json_result(md, meta)
        return 0, None

    # --- Profile ---
    page_range = _parse_page_range(args.pages)
    profile = detector.run(pdf_path, page_range)
    prog.detect(file_label, profile.to_dict())

    # --profile mode: just print and exit
    if args.profile:
        print(json.dumps(profile.to_dict(), ensure_ascii=False, indent=2))
        return 0, None

    # --- Auto-docker: route to container when local deps are missing ---
    if not getattr(args, "no_docker", False):
        planned = select_features(pf, profile, platform, forced_features)
        missing = _missing_local_features(planned)
        if missing:
            prog.emit({"event": "auto_docker", "file": file_label,
                       "reason": "missing_local_deps", "features": missing})
            from .core.docker_setup import ensure_docker, run_in_docker as _docker_run
            if ensure_docker(platform):
                extra = _build_extra_args(args) + ["--no-docker"]
                rc = _docker_run(pdf_path, str(output_dir), extra, platform)
                return rc, None
            else:
                prog.error(file_label,
                           f"Docker unavailable and local deps missing: {missing}. "
                           "Install them (see requirements/ocr.txt) or install Docker.")
                # fall through — will produce empty BLOCKED output

    # --dry-run mode
    if args.dry_run:
        plan = dry_run_plan(pf, profile, platform, forced_features)
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return 0, None

    # --- Extract ---
    t_start = time.monotonic()
    pipeline_result = pipeline_run(
        pdf_path, pf, profile, platform,
        page_range=page_range,
        forced_features=forced_features,
        with_images=args.with_images,
        table_appendix=not args.no_table_appendix,
    )
    extraction_time = time.monotonic() - t_start

    # --- Validate (before fixes) ---
    # plan already built incrementally; render to markdown for validation
    raw_markdown = assembler.assemble_from_plan(
        pipeline_result.plan,
        frontmatter_str="",   # no frontmatter yet
        table_appendix=not args.no_table_appendix,
        with_images=args.with_images,
    )

    val_result = validator.run(raw_markdown)
    prog.validate(file_label, val_result.status, val_result.quality_score)

    if val_result.status == "BLOCKED":
        prog.error(file_label, "Validation BLOCKED: output empty or unreadable. No file written.")
        return 1, None

    # --- Fix (after validation scoring) ---
    fix_result = fixer.run(raw_markdown, skip_fixes=args.no_fix)
    fixed_markdown = fix_result.content
    for fix_name, count in fix_result.fixes_applied.items():
        prog.fix_applied(file_label, fix_name, count)

    # --- Build frontmatter ---
    fm = frontmatter.build(
        source_file=Path(pdf_path).name,
        page_count=pf.page_count,
        file_size_mb=pf.file_size_mb,
        language=profile.dominant_language,
        tables_found=sum(
            len(v) for v in pipeline_result.plan.table_pages.values()
        ),
        has_images=profile.has_images,
        has_scanned_pages=bool(profile.scanned_pages),
        features_used=pipeline_result.features_used,
        extraction_time_sec=extraction_time,
        quality_score=val_result.quality_score,
        is_valid=(val_result.status != "BLOCKED"),
        from_cache=False,
        warnings=val_result.warnings + pipeline_result.warnings,
    )

    final_markdown = fm + fixed_markdown

    # --- Cache write (only after PASS) ---
    if cache_key and val_result.status in ("PASS", "ISSUES_FOUND"):
        meta = {
            "features_used": pipeline_result.features_used,
            "quality_score": val_result.quality_score,
            "pages": pf.page_count,
            "file_size_mb": pf.file_size_mb,
        }
        cache.save(cache_key, final_markdown, meta)

    # --- Write output ---
    output_path = output_dir / (Path(pdf_path).stem + ".md")

    if args.format in ("md", "both"):
        output_path.write_text(final_markdown, encoding="utf-8")

    # Quality gate
    if args.quality_threshold and val_result.quality_score < args.quality_threshold:
        prog.error(file_label,
                   f"Quality score {val_result.quality_score} below threshold {args.quality_threshold}")
        return 1, None

    prog.done(file_label, str(output_path), pipeline_result.features_used)

    if args.format in ("json", "both"):
        result_dict = _build_json_result(final_markdown, {
            "features_used": pipeline_result.features_used,
            "quality_score": val_result.quality_score,
            "quality_label": frontmatter.quality_label(val_result.quality_score),
            "is_valid": val_result.status != "BLOCKED",
            "profile": profile.to_dict(),
            "pages": pf.page_count,
            "from_cache": False,
            "validation_issues": [
                {"code": i.code, "severity": i.severity, "description": i.description}
                for i in val_result.issues
            ],
            "warnings": val_result.warnings,
        })
        return 0, result_dict

    return 0, None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resolve_inputs(pattern: str) -> list[str]:
    if "*" in pattern or "?" in pattern:
        return sorted(glob.glob(pattern))
    p = Path(pattern)
    if p.is_file():
        return [str(p)]
    return []


def _parse_page_range(pages_str: str | None) -> tuple[int, int] | None:
    if not pages_str:
        return None
    try:
        parts = pages_str.split("-")
        return int(parts[0]), int(parts[1])
    except (IndexError, ValueError):
        return None


def _build_extra_args(args) -> list[str]:
    extra = []
    if args.features:
        extra.extend(["--features", args.features])
    if args.pages:
        extra.extend(["--pages", args.pages])
    if args.no_cache:
        extra.append("--no-cache")
    if args.no_fix:
        extra.append("--no-fix")
    if args.with_images:
        extra.append("--with-images")
    if args.no_table_appendix:
        extra.append("--no-table-appendix")
    if args.format != "md":
        extra.extend(["--format", args.format])
    # always pass --no-docker inside container to prevent re-entry
    extra.append("--no-docker")
    return extra


def _build_json_result(markdown: str, meta: dict) -> dict:
    sections = _parse_sections(markdown)
    return {
        "file": meta.get("source", ""),
        "pages": meta.get("pages", 0),
        "from_cache": meta.get("from_cache", False),
        "profile": meta.get("profile", {}),
        "features_used": meta.get("features_used", []),
        "quality_score": meta.get("quality_score", 0),
        "quality_label": meta.get("quality_label", ""),
        "is_valid": meta.get("is_valid", True),
        "sections": sections,
        "markdown": markdown,
        "warnings": meta.get("warnings", []),
        "validation_issues": meta.get("validation_issues", []),
    }


def _parse_sections(markdown: str) -> list[dict]:
    import re
    sections = []
    parts = re.split(r"<!-- Page (\d+) -->", markdown)
    i = 1
    while i < len(parts) - 1:
        try:
            page_num = int(parts[i])
            content = parts[i + 1].strip()
            if content:
                # Detect tables in content
                table_blocks = re.findall(r"(### Tabla[^\n]*\n\n(?:\|.*\n?)+)", content)
                for tb in table_blocks:
                    sections.append({"page": page_num, "type": "table",
                                     "content": tb.strip(),
                                     "backend": _detect_table_backend(tb)})
                # Text (minus tables)
                text_content = content
                for tb in table_blocks:
                    text_content = text_content.replace(tb, "")
                if text_content.strip():
                    sections.append({"page": page_num, "type": "text",
                                     "content": text_content.strip()})
        except (ValueError, IndexError):
            pass
        i += 2
    return sections


def _detect_table_backend(table_str: str) -> str:
    import re
    m = re.search(r"vía ([^\)]+)\)", table_str)
    return m.group(1) if m else "unknown"


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def _parse(argv) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m pdf_extractor",
        description="Modular, cross-platform PDF-to-Markdown extraction",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("input", help="PDF path or glob pattern (e.g. 'docs/*.pdf')")
    parser.add_argument("--output-dir", default="./output", metavar="DIR",
                        help="Output directory (default: ./output)")
    parser.add_argument("--features", metavar="FEAT,...",
                        help="Force specific features: text_fast,tables,ocr_tesseract,...")
    parser.add_argument("--pages", metavar="N-M",
                        help="Page range, e.g. 1-10")
    parser.add_argument("--workers", type=int, metavar="N",
                        help="(reservado — procesamiento secuencial; ignorado)")
    parser.add_argument("--format", choices=["md", "json", "both"], default="md",
                        help="Output format (default: md)")
    parser.add_argument("--with-images", action="store_true",
                        help="Extract and save embedded images")
    parser.add_argument("--no-table-appendix", action="store_true",
                        help="Omit auxiliary tables section")
    parser.add_argument("--no-cache", action="store_true",
                        help="Bypass SHA256 cache")
    parser.add_argument("--no-fix", action="store_true",
                        help="Skip safe-fix pass")
    parser.add_argument("--docker", action="store_true",
                        help="Force Docker for all PDFs regardless of local deps")
    parser.add_argument("--no-docker", action="store_true",
                        help="Disable auto-Docker fallback (run locally only)")
    parser.add_argument("--profile", action="store_true",
                        help="Only run preflight + detector, print PDFProfile, exit")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print pipeline plan without extracting")
    parser.add_argument("--quality-threshold", type=float, metavar="N",
                        help="Exit non-zero if quality_score < N (CI use)")
    return parser.parse_args(argv)


if __name__ == "__main__":
    sys.exit(main())
