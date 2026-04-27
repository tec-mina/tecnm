"""
app/use_cases.py — Pure business logic for the PDF extraction application.

SOLID design:
  S — Each class has exactly one responsibility.
  O — New use-cases added without modifying existing ones.
  L — Use-cases are interchangeable via their execute(request) interface.
  I — Clients depend only on the use-case they need.
  D — Use-cases depend on IEventEmitter (port), not on concrete transports.

Three use-cases:

  ExtractUseCase     — extract one PDF to Markdown
  InspectUseCase     — profile a PDF without extracting
  CapabilitiesUseCase — inventory available system tools + Python packages

Event contract (all events have at least {"event": str, "ts": str}):

  preflight    {"ok":bool, "pages":int, "size_mb":float, "is_scanned":bool}
  profile      {"scanned":int, "text":int, "tables":int, "lang":str}
  cache_hit    {"key":str}
  strategy_plan {"strategies":[...]}
  feature_start {"name":str, "tier":str}
  feature_done  {"name":str, "confidence":float}
  feature_skip  {"name":str, "reason":str}
  validate     {"status":str, "score":float, "issues":int}
  fix          {"fixes": {name:count}}
  done         {"output":str, "quality":float, "elapsed_sec":float}
  error        {"msg":str, "phase":str}
  dry_run      {"plan":{...}}
  inspect      {"profile":{...}, "suggested_strategies":[...]}
  capability   {"tool":str, "available":bool, "version":str|None}
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .ports import IEventEmitter, noop_emitter


# ── Shared helpers ────────────────────────────────────────────────────────────

def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def _emit(fn: IEventEmitter, event: str, **data: Any) -> None:
    fn({"event": event, "ts": _ts(), **data})


# ═══════════════════════════════════════════════════════════════════════════
# ExtractUseCase
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class ExtractionRequest:
    """All parameters for a single PDF extraction.  Immutable value object."""
    pdf_path: str
    output_dir: str
    strategies: list[str] | None = None    # None → auto-select
    page_range: tuple[int, int] | None = None
    with_images: bool = False
    output_format: str = "md"              # "md" | "json" | "both"
    no_cache: bool = False
    no_fix: bool = False
    apply_spell: bool = True              # OCR artifact correction
    quality_threshold: float | None = None
    dry_run: bool = False
    no_docker: bool = False
    with_toc: bool = True
    with_structure: bool = False          # include pdf_structure feature


@dataclass
class ExtractionResult:
    """Structured result of one extraction.  Serialisable to JSON."""
    status: str                           # "ok" | "error" | "blocked" | "cached" | "dry_run"
    output_path: str | None = None
    artifacts: list[str] = field(default_factory=list)
    quality_score: float = 0.0
    quality_label: str = ""
    features_used: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    issues: list[dict] = field(default_factory=list)
    from_cache: bool = False
    elapsed_sec: float = 0.0
    pages: int = 0
    file_size_mb: float = 0.0
    dry_run_plan: dict | None = None
    error_message: str | None = None
    # When the pipeline substituted a failing forced strategy with a same-tier
    # alternative, each substitution is recorded as "<requested>->{<used>}".
    fallbacks: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "output_path": self.output_path,
            "artifacts": self.artifacts,
            "quality_score": self.quality_score,
            "quality_label": self.quality_label,
            "features_used": self.features_used,
            "warnings": self.warnings,
            "issues": self.issues,
            "from_cache": self.from_cache,
            "elapsed_sec": round(self.elapsed_sec, 2),
            "pages": self.pages,
            "file_size_mb": round(self.file_size_mb, 2),
            "fallbacks": self.fallbacks,
        }


def _cache_options(req: ExtractionRequest) -> dict[str, Any]:
    return {
        "page_range": list(req.page_range) if req.page_range else None,
        "with_images": req.with_images,
        "with_structure": req.with_structure,
        "with_toc": req.with_toc,
        "skip_fixes": req.no_fix,
        "apply_spell": req.apply_spell,
    }


def _primary_output_path(output_format: str, md_path: Path, json_path: Path) -> Path:
    return json_path if output_format == "json" else md_path


def _artifact_paths(output_format: str, md_path: Path, json_path: Path, images_dir: Path) -> list[str]:
    artifacts: list[str] = []
    if output_format in ("md", "both"):
        artifacts.append(str(md_path))
    if output_format in ("json", "both"):
        artifacts.append(str(json_path))
    if images_dir.exists():
        artifacts.append(str(images_dir))
    return artifacts


def _mark_cached_markdown(markdown: str) -> str:
    return markdown.replace("\nfrom_cache: false\n", "\nfrom_cache: true\n", 1)


def _json_output_payload(
    *,
    file_name: str,
    output_path: str,
    features_used: list[str],
    quality_score: float,
    quality_label: str,
    pages: int,
    warnings: list[str],
    issues: list[dict[str, Any]],
    from_cache: bool,
    artifacts: list[str],
) -> dict[str, Any]:
    return {
        "file": file_name,
        "output": output_path,
        "artifacts": artifacts,
        "features_used": features_used,
        "quality_score": quality_score,
        "quality_label": quality_label,
        "pages": pages,
        "warnings": warnings,
        "issues": issues,
        "from_cache": from_cache,
    }


class ExtractUseCase:
    """Extract one PDF to Markdown.

    Parameters
    ----------
    on_event : IEventEmitter
        Callback invoked for every structured event.  Inject a JSON-lines
        writer for agents or a Rich-formatter for the terminal.
    """

    def __init__(self, on_event: IEventEmitter = noop_emitter) -> None:
        self._emit = on_event

    def execute(self, req: ExtractionRequest) -> ExtractionResult:
        t0 = time.monotonic()
        result = ExtractionResult(status="error")
        out_dir = Path(req.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        stem = Path(req.pdf_path).stem
        md_out = out_dir / f"{stem}.md"
        json_out = out_dir / f"{stem}.json"
        images_dir = out_dir / "images"
        primary_out = _primary_output_path(req.output_format, md_out, json_out)

        # ── 0. Output rules config ────────────────────────────────────────
        from ..output.config import OutputConfig as _OutputConfig
        _out_cfg = _OutputConfig.load(
            getattr(req, "output_rules_path", None) or "output_rules.yaml"
        )

        # ── 1. Preflight ──────────────────────────────────────────────────
        from ..core import preflight as _pf
        pf = _pf.run(req.pdf_path)
        result.pages = pf.page_count
        result.file_size_mb = pf.file_size_mb

        _emit(self._emit, "preflight",
              file=Path(req.pdf_path).name,
              ok=pf.ok,
              pages=pf.page_count,
              size_mb=round(pf.file_size_mb, 2),
              is_scanned=pf.is_scanned,
              warnings=pf.warnings)

        if not pf.ok:
            msg = "; ".join(pf.errors) or "preflight failed"
            _emit(self._emit, "error", phase="preflight", msg=msg)
            result.error_message = msg
            return result

        # ── 2. Cache check ────────────────────────────────────────────────
        from ..core import cache as _cache
        mode = ",".join(req.strategies) if req.strategies else "auto"
        cache_key = (
            _cache.compute_key(req.pdf_path, mode, _cache_options(req))
            if not req.no_cache else None
        )

        cached_entry = _cache.load_or_none(cache_key) if cache_key else None
        if cached_entry is not None:
            md, meta = cached_entry
            cached_md = _mark_cached_markdown(md)
            if req.output_format in ("md", "both"):
                md_out.write_text(cached_md, encoding="utf-8")
            if req.with_images:
                _cache.load_images(cache_key, images_dir)

            result.features_used = meta.get("features_used", [])
            result.quality_score = meta.get("quality_score", 0)
            result.quality_label = meta.get("quality_label", _quality_label(result.quality_score))
            result.warnings = meta.get("warnings", [])
            result.issues = meta.get("issues", [])
            artifacts = _artifact_paths(req.output_format, md_out, json_out, images_dir)

            if req.output_format in ("json", "both"):
                json_result_dict = _json_output_payload(
                    file_name=Path(req.pdf_path).name,
                    output_path=str(primary_out),
                    features_used=result.features_used,
                    quality_score=result.quality_score,
                    quality_label=result.quality_label,
                    pages=meta.get("pages", pf.page_count),
                    warnings=result.warnings,
                    issues=result.issues,
                    from_cache=True,
                    artifacts=artifacts,
                )
                json_out.write_text(
                    json.dumps(json_result_dict, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )

            _emit(self._emit, "cache_hit", key=cache_key, output=str(primary_out))
            result.status = "cached"
            result.output_path = str(primary_out)
            result.artifacts = artifacts
            result.from_cache = True
            result.elapsed_sec = time.monotonic() - t0
            return result

        # ── 3. Profile ────────────────────────────────────────────────────
        from ..core import detector as _det
        profile = _det.run(req.pdf_path, req.page_range)
        _emit(self._emit, "profile",
              scanned=len(profile.scanned_pages),
              text=len(profile.text_native_pages),
              tables=len(profile.table_pages),
              lang=profile.dominant_language,
              has_images=profile.has_images)

        if req.dry_run:
            from ..core import pipeline as _pipe
            from ..core.platform import detect as _plat
            plan = _pipe.dry_run_plan(pf, profile, _plat(), req.strategies)
            _emit(self._emit, "dry_run", plan=plan)
            result.status = "dry_run"
            result.dry_run_plan = plan
            result.elapsed_sec = time.monotonic() - t0
            return result

        # ── 4. Strategy selection ─────────────────────────────────────────
        from ..core.platform import detect as _plat
        from ..core import pipeline as _pipe
        platform = _plat()

        strategies = _pipe.select_features(pf, profile, platform, req.strategies)

        if req.with_structure and "pdf_structure" not in strategies:
            strategies = ["pdf_structure"] + strategies

        _emit(self._emit, "strategy_plan", strategies=strategies)

        # ── 5. Extract ────────────────────────────────────────────────────
        def _pipeline_emit(event: str, **data: Any) -> None:
            _emit(self._emit, event, **data)

        pipeline_result = _pipe.run(
            req.pdf_path, pf, profile, platform,
            page_range=req.page_range,
            forced_features=strategies,
            with_images=req.with_images,
            table_appendix=True,
            on_event=_pipeline_emit,
            output_dir=str(out_dir) if req.with_images else None,
        )
        result.features_used = pipeline_result.features_used
        result.fallbacks = list(pipeline_result.fallbacks)

        # ── 6. Assemble raw Markdown ──────────────────────────────────────
        from ..output import assembler as _asm
        raw_md = _asm.assemble_from_plan(
            pipeline_result.plan,
            frontmatter_str="",
            with_images=req.with_images,
            with_toc=req.with_toc,
            config=_out_cfg,
        )

        # ── 7. Validate ───────────────────────────────────────────────────
        from ..output import validator as _val
        val = _val.run(raw_md, config=_out_cfg)
        result.quality_score = val.quality_score
        result.quality_label = _quality_label(val.quality_score)
        result.issues = [{"code": i.code, "severity": i.severity,
                          "description": i.description} for i in val.issues]
        _emit(self._emit, "validate",
              status=val.status,
              score=val.quality_score,
              issues=len(val.issues),
              issues_detail=result.issues)

        if val.status == "BLOCKED":
            _emit(self._emit, "error", phase="validate",
                  msg="Output is empty or unreadable — no file written")
            result.status = "blocked"
            result.elapsed_sec = time.monotonic() - t0
            return result

        # ── 8. Fix ────────────────────────────────────────────────────────
        from ..output import fixer as _fix
        fix_result = _fix.run(
            raw_md,
            skip_fixes=req.no_fix,
            apply_ocr_correction=(req.apply_spell and pipeline_result.used_ocr),
            ocr_language=profile.dominant_language or "es",
            config=_out_cfg,
        )
        if fix_result.fixes_applied:
            _emit(self._emit, "fix", fixes=fix_result.fixes_applied)
        fixed_md = fix_result.content

        # ── 9. Frontmatter ────────────────────────────────────────────────
        from ..output import frontmatter as _fm
        fm = _fm.build(
            source_file=Path(req.pdf_path).name,
            page_count=pf.page_count,
            file_size_mb=pf.file_size_mb,
            language=profile.dominant_language,
            tables_found=sum(len(v) for v in pipeline_result.plan.table_pages.values()),
            has_images=profile.has_images,
            has_scanned_pages=bool(profile.scanned_pages),
            features_used=pipeline_result.features_used,
            extraction_time_sec=round(time.monotonic() - t0, 2),
            quality_score=val.quality_score,
            is_valid=True,
            from_cache=False,
            warnings=val.warnings + pipeline_result.warnings,
        )
        final_md = fm + fixed_md
        result.warnings = val.warnings + pipeline_result.warnings

        # ── 10. Write output ──────────────────────────────────────────────
        if req.output_format in ("md", "both"):
            md_out.write_text(final_md, encoding="utf-8")

        artifacts = _artifact_paths(req.output_format, md_out, json_out, images_dir)
        json_result_dict = None
        if req.output_format in ("json", "both"):
            json_result_dict = _json_output_payload(
                file_name=Path(req.pdf_path).name,
                output_path=str(primary_out),
                features_used=pipeline_result.features_used,
                quality_score=val.quality_score,
                quality_label=result.quality_label,
                pages=pf.page_count,
                warnings=result.warnings,
                issues=result.issues,
                from_cache=False,
                artifacts=artifacts,
            )
            json_out.write_text(
                json.dumps(json_result_dict, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

        # ── 11. Cache write ───────────────────────────────────────────────
        if cache_key and val.status in ("PASS", "ISSUES_FOUND"):
            _cache.save(
                cache_key,
                final_md,
                {
                    "features_used": pipeline_result.features_used,
                    "quality_score": val.quality_score,
                    "quality_label": result.quality_label,
                    "pages": pf.page_count,
                    "file_size_mb": pf.file_size_mb,
                    "warnings": result.warnings,
                    "issues": result.issues,
                },
                images_dir=images_dir if images_dir.exists() else None,
            )

        result.elapsed_sec = time.monotonic() - t0
        result.output_path = str(primary_out)
        result.artifacts = artifacts
        result.status = "ok"

        # Quality gate
        if req.quality_threshold and val.quality_score < req.quality_threshold:
            _emit(self._emit, "error", phase="quality_gate",
                  msg=f"Quality {val.quality_score:.0f} below threshold {req.quality_threshold:.0f}")
            result.status = "error"
            result.error_message = f"quality_score {val.quality_score:.0f} < threshold {req.quality_threshold:.0f}"

        _emit(self._emit, "done",
          output=str(primary_out),
              quality=val.quality_score,
              status=val.status,
              features=pipeline_result.features_used,
              elapsed_sec=round(result.elapsed_sec, 2))

        return result


# ═══════════════════════════════════════════════════════════════════════════
# InspectUseCase
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class InspectionResult:
    pdf_path: str
    page_count: int
    file_size_mb: float
    is_scanned: bool
    scanned_pages: int
    text_native_pages: int
    table_pages: int
    has_images: bool
    dominant_language: str
    is_encrypted: bool
    suggested_strategies: list[str]
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "pdf_path": self.pdf_path,
            "page_count": self.page_count,
            "file_size_mb": round(self.file_size_mb, 2),
            "is_scanned": self.is_scanned,
            "scanned_pages": self.scanned_pages,
            "text_native_pages": self.text_native_pages,
            "table_pages": self.table_pages,
            "has_images": self.has_images,
            "dominant_language": self.dominant_language,
            "is_encrypted": self.is_encrypted,
            "suggested_strategies": self.suggested_strategies,
            "metadata": self.metadata,
        }


class InspectUseCase:
    """Profile a PDF without extracting content."""

    def __init__(self, on_event: IEventEmitter = noop_emitter) -> None:
        self._emit = on_event

    def execute(self, pdf_path: str,
                page_range: tuple[int, int] | None = None) -> InspectionResult:
        from ..core import preflight as _pf, detector as _det
        from ..core.platform import detect as _plat
        from ..core.pipeline import select_features

        pf = _pf.run(pdf_path)
        if not pf.ok:
            raise ValueError("; ".join(pf.errors))

        profile = _det.run(pdf_path, page_range)
        platform = _plat()
        strategies = select_features(pf, profile, platform)

        # Extract PDF metadata
        meta: dict = {}
        try:
            try:
                import pymupdf as fitz
            except ImportError:
                import fitz  # type: ignore
            doc = fitz.open(pdf_path)
            meta = {k: v for k, v in (doc.metadata or {}).items() if v}
            doc.close()
        except Exception:
            pass

        result = InspectionResult(
            pdf_path=pdf_path,
            page_count=pf.page_count,
            file_size_mb=pf.file_size_mb,
            is_scanned=pf.is_scanned,
            scanned_pages=len(profile.scanned_pages),
            text_native_pages=len(profile.text_native_pages),
            table_pages=len(profile.table_pages),
            has_images=profile.has_images,
            dominant_language=profile.dominant_language,
            is_encrypted=pf.is_encrypted,
            suggested_strategies=strategies,
            metadata=meta,
        )

        _emit(self._emit, "inspect", profile=result.to_dict())
        return result


# ═══════════════════════════════════════════════════════════════════════════
# CapabilitiesUseCase
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class ToolStatus:
    name: str
    available: bool
    version: str | None = None
    note: str | None = None
    category: str = "system"    # "system" | "python"

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "available": self.available,
            "version": self.version,
            "note": self.note,
            "category": self.category,
        }


@dataclass
class CapabilityReport:
    system_tools: list[ToolStatus] = field(default_factory=list)
    python_packages: list[ToolStatus] = field(default_factory=list)
    strategies: list = field(default_factory=list)    # list[StrategyMeta]
    strategy_discovery_failures: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "system_tools": [t.to_dict() for t in self.system_tools],
            "python_packages": [t.to_dict() for t in self.python_packages],
            "strategies": [
                {"name": s.name, "tier": s.tier, "description": s.description,
                 "is_heavy": s.is_heavy, "priority": s.priority}
                for s in self.strategies
            ],
            "strategy_discovery_failures": self.strategy_discovery_failures,
        }


_SYSTEM_TOOLS = [
    ("tesseract",  ["tesseract", "--version"]),
    ("ghostscript",["gs", "--version"]),
    ("unpaper",    ["unpaper", "--version"]),
    ("imagemagick",["convert", "--version"]),
    ("mutool",     ["mutool", "version"]),
    ("pdftk",      ["pdftk", "--version"]),
    ("qpdf",       ["qpdf", "--version"]),
    ("java",       ["java", "-version"]),
    ("exiftool",   ["exiftool", "-ver"]),
    ("pdfinfo",    ["pdfinfo", "-v"]),
    ("pdfimages",  ["pdfimages", "-v"]),
]

_PYTHON_PACKAGES = [
    ("pymupdf",        "fitz",             "PyMuPDF — text, fonts, images"),
    ("pdfplumber",     "pdfplumber",       "tables extraction"),
    ("pymupdf4llm",    "pymupdf4llm",      "LLM-ready Markdown"),
    ("pdfminer.six",   "pdfminer",         "character-level encoding"),
    ("pytesseract",    "pytesseract",      "OCR: Tesseract"),
    ("easyocr",        "easyocr",          "OCR: neural (GPU optional)"),
    ("opencv",         "cv2",              "OCR preprocessing"),
    ("camelot-py",     "camelot",          "table extraction lattice/stream"),
    ("tabula-py",      "tabula",           "Java table extraction"),
    ("docling",        "docling",          "IBM AI layout + tables (heavy)"),
    ("markitdown",     "markitdown",       "Microsoft MarkItDown"),
    ("tika",           "tika",             "Apache Tika (Java)"),
    ("img2table",      "img2table",        "scanned table extraction"),
    ("pyspellchecker", "spellchecker",     "OCR spell correction"),
    ("python-docx",    "docx",             "DOCX output"),
    ("python-pptx",    "pptx",             "PPTX output"),
    ("weasyprint",     "weasyprint",       "HTML→PDF rendering"),
    ("Pillow",         "PIL",              "image processing"),
    ("langdetect",     "langdetect",       "language detection"),
    ("click",          "click",            "CLI framework"),
    ("rich",           "rich",             "terminal formatting"),
]


class CapabilitiesUseCase:
    """Inventory all available system tools and Python packages."""

    def __init__(self, on_event: IEventEmitter = noop_emitter) -> None:
        self._emit = on_event

    def execute(self) -> CapabilityReport:
        from ..core.registry import registry
        report = CapabilityReport()

        for tool_name, cmd in _SYSTEM_TOOLS:
            status = self._check_system(tool_name, cmd)
            report.system_tools.append(status)
            _emit(self._emit, "capability",
                  tool=tool_name, category="system",
                  available=status.available, version=status.version)

        for pkg_label, import_name, note in _PYTHON_PACKAGES:
            status = self._check_python(pkg_label, import_name, note)
            report.python_packages.append(status)
            _emit(self._emit, "capability",
                  tool=pkg_label, category="python",
                  available=status.available, version=status.version, note=note)

        report.strategies = registry.list_all()
        report.strategy_discovery_failures = [
            failure.to_dict() for failure in registry.discovery_failures()
        ]
        return report

    @staticmethod
    def _check_system(name: str, cmd: list[str]) -> ToolStatus:
        if not shutil.which(cmd[0]):
            return ToolStatus(name=name, available=False, category="system")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            out = (result.stdout + result.stderr).strip()
            version = out.splitlines()[0][:60] if out else None
            return ToolStatus(name=name, available=True, version=version, category="system")
        except Exception:
            return ToolStatus(name=name, available=True, category="system")

    @staticmethod
    def _check_python(label: str, import_name: str, note: str) -> ToolStatus:
        if importlib.util.find_spec(import_name) is None:
            return ToolStatus(name=label, available=False, note=note, category="python")
        try:
            mod = importlib.import_module(import_name)
            version = getattr(mod, "__version__", None) or getattr(mod, "VERSION", None)
            return ToolStatus(name=label, available=True,
                              version=str(version) if version else None,
                              note=note, category="python")
        except Exception:
            return ToolStatus(name=label, available=False, note=note, category="python")


# ── Internal helpers ──────────────────────────────────────────────────────────

def _quality_label(score: float) -> str:
    if score >= 90:
        return "excellent"
    if score >= 80:
        return "good"
    if score >= 70:
        return "acceptable"
    return "poor"
