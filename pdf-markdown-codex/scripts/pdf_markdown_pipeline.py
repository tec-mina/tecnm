#!/usr/bin/env python3
"""
pdf_markdown_pipeline.py - Unified PDF to Markdown extraction pipeline.

This wrapper runs:
1. PDF extraction to Markdown
2. Heuristic quality analysis
3. Optional safe mechanical cleanup
4. Final status summary

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
    table_backend: str,
    max_aux_tables: int,
    table_appendix: bool,
) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(SCRIPT_DIR / "pdf_to_md.py"), str(pdf_path), str(output_path)]
    if docling:
        cmd.append("--docling")
    cmd.extend(["--table-backend", table_backend, "--max-aux-tables", str(max_aux_tables)])
    if not table_appendix:
        cmd.append("--no-table-appendix")
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


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
    parser.add_argument("--fix-safe", action="store_true", help="Apply safe mechanical markdown cleanup")
    parser.add_argument("--report", help="Write quality report to this file")
    parser.add_argument(
        "--table-backend",
        choices=["auto", "none", "pdfplumber", "camelot"],
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

    pdf_path = Path(args.input).resolve()
    if not pdf_path.exists():
        print(f"Error: PDF file '{pdf_path}' not found", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output).resolve() if args.output else pdf_path.with_suffix(".md")

    extraction = run_extraction(
        pdf_path,
        output_path,
        args.docling,
        args.table_backend,
        args.max_aux_tables,
        not args.no_table_appendix,
    )
    report = build_report(output_path)

    fix_summary = None
    if args.fix_safe:
        fix_summary = apply_safe_fixes(output_path)
        report = build_report(output_path)

    report_text = report.generate_text_report()
    if args.report:
        Path(args.report).write_text(report_text, encoding="utf-8")

    print(extraction.stdout.strip())
    if extraction.stderr.strip():
        print("")
        print("Extractor notes:")
        print(extraction.stderr.strip())
    print("")
    print(report_text)

    if fix_summary:
        print("")
        print("Safe fixes applied:")
        print(fix_summary)
        print(f"Updated markdown: {output_path}")


if __name__ == "__main__":
    main()
