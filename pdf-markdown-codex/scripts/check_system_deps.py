#!/usr/bin/env python3
"""check_system_deps.py - Report common system dependencies for PDF tooling."""

from __future__ import annotations

import shutil


TOOLS = {
    "tesseract": "OCR via pytesseract",
    "gs": "Ghostscript, often useful for Camelot",
    "java": "Needed by some Java-based PDF tools",
    "pdftotext": "Poppler text extraction utility",
    "pdfinfo": "Poppler PDF metadata utility",
}


def main() -> None:
    for tool, purpose in TOOLS.items():
        path = shutil.which(tool)
        status = path if path else "MISSING"
        print(f"{tool}: {status} - {purpose}")


if __name__ == "__main__":
    main()
