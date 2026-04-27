"""
core/preflight.py — Pre-flight PDF validation before extraction.

Checks (in order):
  1. Input validation (PDFValidator) — file exists, not corrupt, readable
  2. Magic bytes start with %PDF-
  3. Not encrypted / password-protected
  4. Page count > 0
  5. is_scanned: sample 5 pages → selectable text chars < 50 → scanned
  6. File size warning (> 200 MB)

Returns PreflightResult used by pipeline.py to gate which features run.
If encryption is detected the pipeline should emit an error event and exit.

Phase 2.1: Integrated PDFValidator for comprehensive input validation.
"""

from __future__ import annotations

import sys
import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


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

    # Phase 2.1: Input validation with PDFValidator
    from .pdf_validator import PDFValidator

    validator = PDFValidator()
    validation = validator.validate(pdf_path)

    if not validation.is_valid:
        # Detailed error handling based on validation status
        result.errors.extend(validation.errors)
        result.warnings.extend(validation.warnings)

        # Specific handling for encryption
        if validation.is_encrypted:
            result.is_encrypted = True

        logger.error(
            f"PDF validation failed: {pdf_path} "
            f"(status={validation.status.value}, errors={len(validation.errors)})"
        )
        return result

    result.file_size_mb = validation.file_size_kb / 1024.0

    if result.file_size_mb > _LARGE_FILE_MB:
        result.warnings.append(
            f"Large file ({result.file_size_mb:.1f} MB). "
            "Consider --workers and chunked mode for best performance."
        )

    # Early exit if validation caught corruption or truncation issues
    if validation.is_corrupted and validation.is_truncated:
        result.errors.append(
            "PDF is corrupt and truncated. Cannot safely process."
        )
        return result

    if validation.is_truncated:
        result.warnings.append(
            "PDF appears truncated (missing proper footer). "
            "Extraction may be incomplete."
        )

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
