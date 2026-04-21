"""
core/preflight.py — Pre-flight PDF validation before extraction.

Checks (in order):
  1. File exists and is readable
  2. Magic bytes start with %PDF-
  3. Not encrypted / password-protected
  4. Page count > 0
  5. is_scanned: sample 5 pages → selectable text chars < 50 → scanned
  6. File size warning (> 200 MB)

Returns PreflightResult used by pipeline.py to gate which features run.
If encryption is detected the pipeline should emit an error event and exit.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path


_SAMPLE_PAGES = 5          # pages to sample for scanned detection
_SCANNED_CHAR_THRESHOLD = 50   # chars per page below this → scanned
_LARGE_FILE_MB = 200


@dataclass
class PreflightResult:
    path: str
    ok: bool = False
    is_encrypted: bool = False
    is_scanned: bool = False
    page_count: int = 0
    file_size_mb: float = 0.0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def run(pdf_path: str) -> PreflightResult:
    """Run all pre-flight checks and return a PreflightResult."""
    result = PreflightResult(path=pdf_path)
    p = Path(pdf_path)

    # 1. File exists and readable
    if not p.exists():
        result.errors.append(f"File not found: {pdf_path}")
        return result
    if not p.is_file():
        result.errors.append(f"Path is not a file: {pdf_path}")
        return result
    try:
        result.file_size_mb = round(p.stat().st_size / (1024 * 1024), 2)
    except OSError as exc:
        result.errors.append(f"Cannot stat file: {exc}")
        return result

    if result.file_size_mb > _LARGE_FILE_MB:
        result.warnings.append(
            f"Large file ({result.file_size_mb:.1f} MB). "
            "Consider --workers and chunked mode for best performance."
        )

    # 2. Magic bytes
    try:
        with open(p, "rb") as f:
            header = f.read(8)
        if not header.startswith(b"%PDF-"):
            result.errors.append(
                f"Not a valid PDF (bad magic bytes). Got: {header[:8]!r}"
            )
            return result
    except OSError as exc:
        result.errors.append(f"Cannot read file header: {exc}")
        return result

    # 3-5. Open with PyMuPDF for deep checks
    try:
        import pymupdf as fitz
    except ImportError:
        try:
            import fitz
        except ImportError:
            result.errors.append("pymupdf not installed; run: pip install pymupdf")
            return result

    try:
        doc = fitz.open(str(p))
    except Exception as exc:
        result.errors.append(f"Corrupt or unreadable PDF: {exc}")
        return result

    try:
        # 3. Encryption
        if doc.is_encrypted:
            result.is_encrypted = True
            result.errors.append("PDF is encrypted/password-protected.")
            return result

        # 4. Page count
        result.page_count = doc.page_count
        if result.page_count == 0:
            result.errors.append("PDF has zero pages.")
            return result

        # 5. Scanned detection — sample up to _SAMPLE_PAGES pages
        total = result.page_count
        step = max(1, total // _SAMPLE_PAGES)
        sample_indices = list(range(0, total, step))[:_SAMPLE_PAGES]
        total_chars = 0
        for idx in sample_indices:
            page = doc[idx]
            text = page.get_text("text")
            total_chars += len(text.strip())

        avg_chars = total_chars / len(sample_indices) if sample_indices else 0
        result.is_scanned = avg_chars < _SCANNED_CHAR_THRESHOLD

    finally:
        doc.close()

    result.ok = True
    return result
