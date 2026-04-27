#!/usr/bin/env python3
"""
core/pdf_validator.py — Universal PDF input validation framework.

Validates PDFs before processing to prevent corrupt files from cascading
failures across the entire extraction system. Detects: corruption, encryption,
truncation, wrong format, and provides early feedback.

Phase 2.1: Input Validation Wrapper
"""

import os
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class PDFStatus(Enum):
    """PDF validation status"""
    VALID = "valid"
    CORRUPT = "corrupt"
    ENCRYPTED = "encrypted"
    TRUNCATED = "truncated"
    WRONG_FORMAT = "wrong_format"
    EMPTY = "empty"
    UNREADABLE = "unreadable"


@dataclass
class ValidationResult:
    """Result of PDF validation"""
    path: str
    is_valid: bool
    status: PDFStatus
    page_count: int = 0
    file_size_kb: float = 0.0
    is_encrypted: bool = False
    is_corrupted: bool = False
    is_truncated: bool = False
    has_pdf_header: bool = False
    has_pdf_footer: bool = False
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    can_fallback: bool = True
    estimated_recovery_difficulty: str = "easy"

    def to_dict(self):
        """Convert to dictionary for logging/serialization"""
        return {
            "path": self.path,
            "is_valid": self.is_valid,
            "status": self.status.value,
            "page_count": self.page_count,
            "file_size_kb": self.file_size_kb,
            "is_encrypted": self.is_encrypted,
            "is_corrupted": self.is_corrupted,
            "is_truncated": self.is_truncated,
            "has_pdf_header": self.has_pdf_header,
            "has_pdf_footer": self.has_pdf_footer,
            "warnings": self.warnings,
            "errors": self.errors,
            "can_fallback": self.can_fallback,
            "estimated_recovery_difficulty": self.estimated_recovery_difficulty,
        }


class PDFValidator:
    """Universal PDF validation (apply before any extraction)"""

    MIN_PDF_SIZE_BYTES = 100
    MAX_PDF_SIZE_MB = 1000
    PDF_HEADER = b"%PDF"
    PDF_FOOTER_PATTERN = b"%%EOF"

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def validate(self, pdf_path: str) -> ValidationResult:
        """
        Comprehensive PDF validation.

        Returns ValidationResult with:
        - is_valid: True if safe to process
        - status: Detailed status (valid, corrupt, encrypted, etc)
        - page_count: Number of pages (if readable)
        - warnings/errors: Detailed feedback
        - can_fallback: Whether fallback methods might work
        """
        result = ValidationResult(
            path=pdf_path,
            is_valid=False,
            status=PDFStatus.UNREADABLE,
        )

        # Step 1: File existence and readability
        if not self._check_file_exists(pdf_path, result):
            return result

        # Step 2: File size validation
        if not self._check_file_size(pdf_path, result):
            return result

        # Step 3: Binary content validation (PDF header/footer)
        if not self._check_binary_structure(pdf_path, result):
            return result

        # Step 4: Multi-library validation (try fitz, pdfplumber, pypdf)
        self._validate_with_libraries(pdf_path, result)

        # Step 5: Final verdict
        self._finalize_verdict(result)

        return result

    def _check_file_exists(self, pdf_path: str, result: ValidationResult) -> bool:
        """Check file exists and is readable"""
        try:
            path = Path(pdf_path)
            if not path.exists():
                result.errors.append(f"File not found: {pdf_path}")
                result.status = PDFStatus.UNREADABLE
                result.can_fallback = False
                self.logger.error(f"PDF validation: {pdf_path} not found")
                return False

            if not os.access(pdf_path, os.R_OK):
                result.errors.append(f"File not readable: {pdf_path}")
                result.status = PDFStatus.UNREADABLE
                result.can_fallback = False
                self.logger.error(f"PDF validation: {pdf_path} not readable")
                return False

            return True
        except Exception as e:
            result.errors.append(f"Error checking file: {str(e)}")
            result.status = PDFStatus.UNREADABLE
            result.can_fallback = False
            return False

    def _check_file_size(self, pdf_path: str, result: ValidationResult) -> bool:
        """Check file size is within acceptable range"""
        try:
            file_size = os.path.getsize(pdf_path)
            result.file_size_kb = file_size / 1024.0

            if file_size < self.MIN_PDF_SIZE_BYTES:
                result.errors.append(f"File too small ({file_size} bytes)")
                result.status = PDFStatus.EMPTY
                self.logger.warning(f"PDF validation: {pdf_path} too small")
                return False

            if file_size > self.MAX_PDF_SIZE_MB * 1024 * 1024:
                result.warnings.append(
                    f"File very large ({result.file_size_kb:.0f} KB). "
                    "Processing may be slow or cause memory issues."
                )
                result.estimated_recovery_difficulty = "medium"

            return True
        except Exception as e:
            result.errors.append(f"Error checking file size: {str(e)}")
            result.status = PDFStatus.UNREADABLE
            return False

    def _check_binary_structure(
        self, pdf_path: str, result: ValidationResult
    ) -> bool:
        """Check PDF header and footer structure"""
        try:
            with open(pdf_path, "rb") as f:
                # Check PDF header
                header = f.read(4)
                if header != self.PDF_HEADER:
                    result.errors.append(
                        f"Missing PDF header (expected {self.PDF_HEADER}, got {header})"
                    )
                    result.status = PDFStatus.WRONG_FORMAT
                    result.has_pdf_header = False
                    self.logger.warning(f"PDF validation: {pdf_path} missing PDF header")
                    return False

                result.has_pdf_header = True

                # Check PDF footer (approximate)
                try:
                    f.seek(-1024, 2)  # Seek to last 1KB
                except OSError:
                    # File smaller than 1KB, just read from beginning
                    f.seek(0)

                tail = f.read()
                if self.PDF_FOOTER_PATTERN in tail:
                    result.has_pdf_footer = True
                else:
                    result.warnings.append(
                        "PDF missing proper footer (may be truncated or streaming)"
                    )
                    result.is_truncated = True

            return True
        except Exception as e:
            result.errors.append(f"Error checking binary structure: {str(e)}")
            result.status = PDFStatus.UNREADABLE
            return False

    def _validate_with_libraries(
        self, pdf_path: str, result: ValidationResult
    ) -> None:
        """Try opening with multiple libraries to detect issues"""
        libraries_to_try = [
            ("fitz (PyMuPDF)", self._try_fitz),
            ("pdfplumber", self._try_pdfplumber),
            ("pypdf", self._try_pypdf),
        ]

        lib_results = []
        for lib_name, try_func in libraries_to_try:
            try:
                page_count = try_func(pdf_path)
                if page_count is not None:
                    lib_results.append((lib_name, page_count, None))
                    self.logger.debug(f"PDF validated with {lib_name}: {page_count} pages")
                    continue
            except Exception as e:
                lib_results.append((lib_name, None, str(e)))
                continue

        # Analyze results
        successful_libs = [(name, count) for name, count, err in lib_results if err is None]
        failed_libs = [(name, err) for name, count, err in lib_results if err is not None]

        if successful_libs:
            # At least one library succeeded
            result.page_count = successful_libs[0][1]
            result.is_valid = result.page_count > 0
            result.is_corrupted = False
            result.status = PDFStatus.VALID if result.page_count > 0 else PDFStatus.EMPTY

            if len(successful_libs) < len(libraries_to_try):
                result.warnings.append(
                    f"Opened with {successful_libs[0][0]}, "
                    f"but {len(failed_libs)} other libs failed. May have corruption."
                )
                result.is_corrupted = True

        else:
            # All libraries failed
            result.is_valid = False
            result.is_corrupted = True
            result.status = PDFStatus.CORRUPT

            # Analyze failures to determine if encrypted
            for lib_name, err_msg in failed_libs:
                result.errors.append(f"{lib_name}: {err_msg}")
                if (
                    "encrypt" in err_msg.lower()
                    or "password" in err_msg.lower()
                    or "security" in err_msg.lower()
                ):
                    result.is_encrypted = True
                    result.status = PDFStatus.ENCRYPTED
                    result.can_fallback = False

    def _try_fitz(self, pdf_path: str) -> Optional[int]:
        """Try opening PDF with PyMuPDF (fitz)"""
        try:
            import fitz

            doc = fitz.open(pdf_path)
            page_count = doc.page_count
            doc.close()
            return page_count
        except ImportError:
            return None
        except Exception as e:
            raise e

    def _try_pdfplumber(self, pdf_path: str) -> Optional[int]:
        """Try opening PDF with pdfplumber"""
        try:
            import pdfplumber

            with pdfplumber.open(pdf_path) as pdf:
                return len(pdf.pages)
        except ImportError:
            return None
        except Exception as e:
            raise e

    def _try_pypdf(self, pdf_path: str) -> Optional[int]:
        """Try opening PDF with pypdf"""
        try:
            from pypdf import PdfReader

            reader = PdfReader(pdf_path)
            return len(reader.pages)
        except ImportError:
            return None
        except Exception as e:
            raise e

    def _finalize_verdict(self, result: ValidationResult) -> None:
        """Finalize validation verdict"""
        if result.is_valid:
            self.logger.info(
                f"✅ PDF valid: {result.path} ({result.page_count} pages, "
                f"{result.file_size_kb:.0f} KB)"
            )
        else:
            self.logger.error(
                f"❌ PDF invalid: {result.path} "
                f"(status={result.status.value}, errors={len(result.errors)})"
            )


def validate_pdf(pdf_path: str) -> ValidationResult:
    """Convenience function to validate a single PDF"""
    validator = PDFValidator()
    return validator.validate(pdf_path)
