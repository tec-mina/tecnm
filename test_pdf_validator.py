#!/usr/bin/env python3
"""
test_pdf_validator.py — Test PDFValidator with synthetic cases.
"""

import os
import sys
import logging
import tempfile
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent))

from pdf_extractor.core.pdf_validator import PDFValidator, PDFStatus


def test_nonexistent_file():
    """Test validation of nonexistent file"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST: Nonexistent file")
    logger.info("=" * 80)

    validator = PDFValidator()
    result = validator.validate("/nonexistent/file.pdf")

    assert not result.is_valid, "Should be invalid"
    assert result.status == PDFStatus.UNREADABLE, f"Expected UNREADABLE, got {result.status}"
    assert len(result.errors) > 0, "Should have errors"
    logger.info(f"✅ Result: {result.status.value}")
    logger.info(f"   Errors: {result.errors}")


def test_empty_file():
    """Test validation of empty file"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST: Empty file")
    logger.info("=" * 80)

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        empty_path = f.name

    try:
        validator = PDFValidator()
        result = validator.validate(empty_path)

        assert not result.is_valid, "Should be invalid"
        assert result.status == PDFStatus.EMPTY, f"Expected EMPTY, got {result.status}"
        logger.info(f"✅ Result: {result.status.value}")
        logger.info(f"   File size: {result.file_size_kb:.1f} KB")
    finally:
        os.unlink(empty_path)


def test_wrong_format_file():
    """Test validation of non-PDF file with PDF extension"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST: Wrong format (text file with .pdf extension)")
    logger.info("=" * 80)

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False, mode="w") as f:
        # Write enough content to pass size check but fail header check
        f.write("This is just text, not a PDF. " * 10)
        wrong_path = f.name

    try:
        validator = PDFValidator()
        result = validator.validate(wrong_path)

        assert not result.is_valid, "Should be invalid"
        assert (
            result.status == PDFStatus.WRONG_FORMAT
        ), f"Expected WRONG_FORMAT, got {result.status}"
        logger.info(f"✅ Result: {result.status.value}")
        logger.info(f"   Errors: {result.errors}")
    finally:
        os.unlink(wrong_path)


def test_truncated_pdf():
    """Test validation of truncated PDF (has header but no footer)"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST: Truncated PDF (header but no footer)")
    logger.info("=" * 80)

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False, mode="wb") as f:
        # Write PDF header + substantial content but no footer
        f.write(b"%PDF-1.4\n")
        f.write(b"1 0 obj\n")
        f.write(b"<< /Type /Catalog /Pages 2 0 R >>\n")
        f.write(b"endobj\n")
        # Pad with more content to pass size check
        f.write(b"comment: " * 50)
        # Intentionally missing %%EOF footer
        truncated_path = f.name

    try:
        validator = PDFValidator()
        result = validator.validate(truncated_path)

        # Should detect truncation (missing footer)
        assert result.is_truncated, "Should detect truncation"
        logger.info(f"✅ Result: {result.status.value}")
        logger.info(f"   Is truncated: {result.is_truncated}")
        logger.info(f"   Has footer: {result.has_pdf_footer}")
    finally:
        os.unlink(truncated_path)


def test_valid_minimal_pdf():
    """Test validation of minimal but valid PDF"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST: Minimal but valid PDF")
    logger.info("=" * 80)

    # Create a minimal PDF with proper structure
    pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> >>
endobj
4 0 obj
<< /Length 44 >>
stream
BT
/F1 12 Tf
100 700 Td
(Hello World) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000273 00000 n
trailer
<< /Size 5 /Root 1 0 R >>
startxref
366
%%EOF
"""

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False, mode="wb") as f:
        f.write(pdf_content)
        valid_path = f.name

    try:
        validator = PDFValidator()
        result = validator.validate(valid_path)

        logger.info(f"✅ Result: {result.status.value}")
        logger.info(f"   Is valid: {result.is_valid}")
        logger.info(f"   Page count: {result.page_count}")
        logger.info(f"   File size: {result.file_size_kb:.1f} KB")
        logger.info(f"   Warnings: {result.warnings}")
    finally:
        os.unlink(valid_path)


def test_large_file_warning():
    """Test that large file triggers warning"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST: Large file (warning)")
    logger.info("=" * 80)

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False, mode="wb") as f:
        # Write PDF header + 100 MB of padding (simulate large file)
        f.write(b"%PDF-1.4\n")
        f.seek(100 * 1024 * 1024)
        f.write(b"%%EOF\n")
        large_path = f.name

    try:
        validator = PDFValidator()
        result = validator.validate(large_path)

        logger.info(f"✅ Result: {result.status.value}")
        logger.info(f"   File size: {result.file_size_kb / 1024:.1f} MB")
        logger.info(f"   Warnings: {result.warnings}")
        assert any("very large" in w.lower() for w in result.warnings), "Should warn about size"
    finally:
        os.unlink(large_path)


def test_validator_result_serialization():
    """Test that ValidationResult can be serialized to dict"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST: ValidationResult serialization")
    logger.info("=" * 80)

    validator = PDFValidator()
    result = validator.validate("/nonexistent/file.pdf")
    result_dict = result.to_dict()

    assert isinstance(result_dict, dict), "Should be serializable"
    assert "is_valid" in result_dict, "Should have is_valid"
    assert "status" in result_dict, "Should have status"
    assert isinstance(result_dict["status"], str), "Status should be string in dict"

    logger.info(f"✅ Serialization successful")
    logger.info(f"   Keys: {list(result_dict.keys())}")


if __name__ == "__main__":
    print("\n" + "█" * 80)
    print("█" + " " * 78 + "█")
    print("█" + "  PDF VALIDATOR TESTS".center(78) + "█")
    print("█" + " " * 78 + "█")
    print("█" * 80)

    try:
        test_nonexistent_file()
        test_empty_file()
        test_wrong_format_file()
        test_truncated_pdf()
        test_valid_minimal_pdf()
        test_large_file_warning()
        test_validator_result_serialization()

        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED")
        print("=" * 80 + "\n")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
