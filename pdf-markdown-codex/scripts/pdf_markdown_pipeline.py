#!/usr/bin/env python3
"""
pdf_markdown_pipeline.py - Unified PDF to Markdown extraction pipeline.

This wrapper runs:
1. PDF pre-flight validation
2. PDF extraction to Markdown (with real-time progress)
3. Heuristic quality analysis
4. Optional safe mechanical cleanup
5. Final status summary

Usage:
    python scripts/pdf_markdown_pipeline.py input.pdf
    python scripts/pdf_markdown_pipeline.py input.pdf --docling
    python scripts/pdf_markdown_pipeline.py input.pdf --fix-safe --report report.txt
"""

import argparse
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from markdown_fixer import MarkdownFixer
from pdf_markdown_compare import AnalysisReport


def run_extraction(
    pdf_path: Path,
    output_path: Path,
    docling: bool,
    markitdown: bool,
    ocr_easyocr: list | None,
    table_backend: str,
    max_aux_tables: int,
    table_appendix: bool,
    with_images: bool = False,
) -> int:
    """Run pdf_to_md.py as a subprocess with live stderr (progress bars visible)."""
    cmd = [sys.executable, str(SCRIPT_DIR / "pdf_to_md.py"), str(pdf_path), str(output_path)]
    if docling:
        cmd.append("--docling")
    if markitdown:
        cmd.append("--markitdown")
    if ocr_easyocr is not None:
        cmd.append("--ocr-easyocr")
        cmd.extend(ocr_easyocr)
    cmd.extend(["--table-backend", table_backend, "--max-aux-tables", str(max_aux_tables)])
    if not table_appendix:
        cmd.append("--no-table-appendix")
    if with_images:
        cmd.append("--with-images")
    # Do NOT capture stderr so tqdm progress bars and validation messages
    # stream directly to the terminal in real time.
    result = subprocess.run(cmd, check=False)
    return result.returncode


def build_report(markdown_path: Path) -> AnalysisReport:
    report = AnalysisReport(str(markdown_path))
    report.check_structure().check_tables().check_suspicious_numbers()
    return report


def apply_safe_fixes(markdown_path: Path) -> str:
    content = markdown_path.read_text(encoding="utf-8")
    fixer = MarkdownFixer(content)
    fixer.fix_ligatures()
    fixer.fix_control_chars()
    fixer.fix_spaces()
    fixer.fix_paragraphs()
    fixer.fix_double_spaces()
    markdown_path.write_text(fixer.content, encoding="utf-8")
    return fixer.get_changes_summary()


def main() -> None:
    parser = argparse.ArgumentParser(description="Unified PDF to Markdown pipeline")
    parser.add_argument("input", help="Input PDF path")
    parser.add_argument(
        "output",
        nargs="?",
        help="Output Markdown path (default: <input>.md)",
    )
    parser.add_argument("--docling", action="store_true", help="Use Docling for more accurate tables")
    parser.add_argument("--markitdown", action="store_true", help="Use Microsoft MarkItDown backend")
    parser.add_argument(
        "--ocr-easyocr",
        nargs="*",
        metavar="LANG",
        dest="ocr_easyocr",
        help="Use EasyOCR for scanned PDFs (default langs: es en). Example: --ocr-easyocr es en",
    )
    parser.add_argument("--fix-safe", action="store_true", help="Apply safe mechanical markdown cleanup")
    parser.add_argument("--report", help="Write quality report to this file")
    parser.add_argument(
        "--with-images",
        action="store_true",
        help="Extract and copy embedded PDF images next to the Markdown output",
    )
    parser.add_argument(
        "--table-backend",
        choices=["auto", "none", "pdfplumber", "camelot", "tabula"],
        default="auto",
        help="Auxiliary table extraction backend",
    )
    parser.add_argument(
        "--max-aux-tables",
        type=int,
        default=25,
        help="Maximum auxiliary tables to append",
    )
    parser.add_argument(
        "--no-table-appendix",
        action="store_true",
        help="Disable the auxiliary table appendix",
    )
    args = parser.parse_args()

    # Pre-flight validation before launching the subprocess
    from extractor import validate_pdf

    pdf_info = validate_pdf(args.input)
    for w in pdf_info.warnings:
        print(f"AVISO: {w}", file=sys.stderr)
    if not pdf_info.ok:
        for err in pdf_info.errors:
            print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(1)

    pdf_path = Path(args.input).resolve()
    output_path = Path(args.output).resolve() if args.output else pdf_path.with_suffix(".md")

    returncode = run_extraction(
        pdf_path,
        output_path,
        args.docling,
        getattr(args, "markitdown", False),
        getattr(args, "ocr_easyocr", None),
        args.table_backend,
        args.max_aux_tables,
        not args.no_table_appendix,
        getattr(args, "with_images", False),
    )
    if returncode != 0:
        sys.exit(returncode)

    if not output_path.exists():
        print(f"ERROR: El archivo de salida no fue generado: {output_path}", file=sys.stderr)
        sys.exit(1)

    report = build_report(output_path)

    fix_summary = None
    if args.fix_safe:
        fix_summary = apply_safe_fixes(output_path)
        report = build_report(output_path)

    report_text = report.generate_text_report()
    if args.report:
        Path(args.report).write_text(report_text, encoding="utf-8")

    print("")
    print(report_text)

    if fix_summary:
        print("")
        print("Safe fixes aplicados:")
        print(fix_summary)
        print(f"Markdown actualizado: {output_path}")


if __name__ == "__main__":
    main()
