#!/usr/bin/env python3
"""
test_phase2_integration.py — Test PDFValidator integration into preflight pipeline.

Verifies that corrupt PDFs are caught early and prevent cascading failures.
"""

import os
import sys
import tempfile
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent))

from pdf_extractor.core.preflight import run as preflight_run
from pdf_extractor.core.pdf_validator import PDFStatus


def test_preflight_with_nonexistent_file():
    """Test that preflight rejects nonexistent file"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 1: Preflight with nonexistent file")
    logger.info("=" * 80)

    result = preflight_run("/nonexistent/file.pdf")

    assert not result.ok, "Should fail"
    assert len(result.errors) > 0, "Should have errors"
    logger.info(f"✅ PASSED: {result.errors[0]}")


def test_preflight_with_corrupt_file():
    """Test that preflight rejects corrupt file"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 2: Preflight with corrupt file (wrong format)")
    logger.info("=" * 80)

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False, mode="w") as f:
        f.write("This is not a PDF " * 10)
        corrupt_path = f.name

    try:
        result = preflight_run(corrupt_path)

        assert not result.ok, "Should fail"
        assert len(result.errors) > 0, "Should have errors"
        logger.info(f"✅ PASSED: {result.errors[0]}")
    finally:
        os.unlink(corrupt_path)


def test_preflight_with_truncated_file():
    """Test that preflight detects truncated PDF"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 3: Preflight with truncated PDF")
    logger.info("=" * 80)

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False, mode="wb") as f:
        f.write(b"%PDF-1.4\n")
        f.write(b"1 0 obj\n")
        f.write(b"<< /Type /Catalog /Pages 2 0 R >>\n")
        f.write(b"endobj\n")
        f.write(b"comment: " * 50)
        # No footer
        truncated_path = f.name

    try:
        result = preflight_run(truncated_path)

        # Should warn about truncation
        assert any("truncat" in w.lower() for w in result.warnings), "Should warn about truncation"
        logger.info(f"✅ PASSED: Warnings: {result.warnings}")
    finally:
        os.unlink(truncated_path)


def test_preflight_with_valid_pdf():
    """Test that preflight passes valid PDF"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 4: Preflight with valid minimal PDF")
    logger.info("=" * 80)

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
        result = preflight_run(valid_path)

        assert result.ok, f"Should pass. Errors: {result.errors}"
        assert result.page_count > 0, "Should detect page count"
        logger.info(f"✅ PASSED: {result.page_count} pages detected")
    finally:
        os.unlink(valid_path)


if __name__ == "__main__":
    print("\n" + "█" * 80)
    print("█" + " " * 78 + "█")
    print("█" + "  PHASE 2.1 INTEGRATION TESTS".center(78) + "█")
    print("█" + " " * 78 + "█")
    print("█" * 80)

    try:
        test_preflight_with_nonexistent_file()
        test_preflight_with_corrupt_file()
        test_preflight_with_truncated_file()
        test_preflight_with_valid_pdf()

        print("\n" + "=" * 80)
        print("✅ ALL INTEGRATION TESTS PASSED")
        print("=" * 80 + "\n")
        print("Phase 2.1 Status: ✅ PDFValidator integrated into preflight pipeline")
        print("Next: Phase 2.2 - Error classification and fallback routing")
        print("=" * 80 + "\n")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback

        traceback.print_exc()
        sys.exit(1)
