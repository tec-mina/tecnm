#!/usr/bin/env python3
"""
examples/ocr_robust_example.py — Demonstrates robust OCR usage.

Shows how to:
- Use EasyOCR with network resilience
- Handle failures gracefully
- Configure timeouts and retries
- Fallback between methods
- Log errors clearly
"""

import os
import sys
import logging
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from pdf_extractor.features import ocr_easy, ocr_tesseract
from pdf_extractor.core.ocr_config import get_config, OCRConfig, reset_config
from pdf_extractor.features._network_utils import check_network

# Configure logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


def example_1_check_network():
    """Example 1: Check network before using network-dependent OCR."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Network Check")
    print("="*70)

    is_online = check_network()
    print(f"Network available: {is_online}")

    if not is_online:
        print("⚠️  Network unavailable. EasyOCR will fail unless offline models are cached.")
        print("   Fallback to Tesseract (local) or use OCR_OFFLINE_MODE=1")
    else:
        print("✓ Network is available. EasyOCR can download models if needed.")


def example_2_configure_retries():
    """Example 2: Configure timeout and retry behavior."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Configure OCR Resilience")
    print("="*70)

    # Reset to reload env vars
    reset_config()

    # Set environment variables for resilience
    os.environ["OCR_MAX_RETRIES"] = "5"
    os.environ["OCR_INITIAL_BACKOFF"] = "1.5"
    os.environ["OCR_PAGE_TIMEOUT"] = "45"
    os.environ["OCR_INIT_TIMEOUT"] = "120"

    reset_config()  # Reload with new env vars
    config = get_config()

    print(f"Configuration:")
    for key, value in config.to_dict().items():
        print(f"  {key}: {value}")


def example_3_tesseract_basic():
    """Example 3: Use Tesseract OCR (fast, local)."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Tesseract OCR (Basic)")
    print("="*70)

    # Create a dummy PDF path for demonstration
    test_pdf = Path(__file__).parent.parent / "tests" / "data" / "sample.pdf"

    if not test_pdf.exists():
        print(f"⚠️  Test PDF not found at {test_pdf}")
        print("   In production, call: ocr_tesseract.extract('your_pdf.pdf')")
        return

    print(f"Extracting from: {test_pdf}")
    result = ocr_tesseract.extract(test_pdf, preprocess=False)

    print(f"\nResults:")
    print(f"  Pages processed: {result.metadata.get('pages_processed', 0)}")
    print(f"  Pages failed: {result.metadata.get('pages_failed', 0)}")
    print(f"  Confidence: {result.confidence:.2%}")
    print(f"  Warnings: {result.warnings}")


def example_4_tesseract_advanced():
    """Example 4: Use Tesseract with preprocessing (slower, better quality)."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Tesseract OCR (Advanced with Preprocessing)")
    print("="*70)

    test_pdf = Path(__file__).parent.parent / "tests" / "data" / "degraded.pdf"

    if not test_pdf.exists():
        print(f"⚠️  Test PDF not found at {test_pdf}")
        print("   In production, call:")
        print("   ocr_tesseract.extract('degraded_scan.pdf', preprocess=True, dpi=400)")
        return

    print(f"Extracting from: {test_pdf}")
    print("Using: preprocessing=True, dpi=400 (better for poor-quality scans)")

    result = ocr_tesseract.extract(test_pdf, preprocess=True, dpi=400)

    print(f"\nResults:")
    print(f"  Pages processed: {result.metadata.get('pages_processed', 0)}")
    print(f"  Pages failed: {result.metadata.get('pages_failed', 0)}")
    print(f"  Confidence: {result.confidence:.2%}")
    print(f"  Warnings: {result.warnings}")


def example_5_easyocr_with_fallback():
    """Example 5: Use EasyOCR with graceful handling."""
    print("\n" + "="*70)
    print("EXAMPLE 5: EasyOCR with Network Resilience")
    print("="*70)

    test_pdf = Path(__file__).parent.parent / "tests" / "data" / "sample.pdf"

    if not test_pdf.exists():
        print(f"⚠️  Test PDF not found at {test_pdf}")
        print("   In production, call:")
        print("   ocr_easy.extract('your_pdf.pdf', max_retries=5, timeout_sec=60)")
        print("\n   If network is unavailable:")
        print("   ocr_easy.extract('your_pdf.pdf', offline_only=True)")
        return

    print(f"Extracting from: {test_pdf}")
    print("Using: max_retries=5 (resilient to network glitches)")

    result = ocr_easy.extract(test_pdf, max_retries=5, timeout_sec=60)

    print(f"\nResults:")
    print(f"  Pages processed: {result.metadata.get('pages_processed', 0)}")
    print(f"  Pages failed: {result.metadata.get('pages_failed', 0)}")
    print(f"  Confidence: {result.confidence:.2%}")
    print(f"  Backend: {result.metadata.get('backend')}")
    print(f"  GPU used: {result.metadata.get('gpu')}")
    print(f"  Languages: {result.metadata.get('langs')}")
    print(f"  Warnings: {result.warnings}")


def example_6_offline_mode():
    """Example 6: Use offline mode (cached models only)."""
    print("\n" + "="*70)
    print("EXAMPLE 6: EasyOCR Offline Mode")
    print("="*70)

    print("Offline mode uses cached models (no network needed).")
    print("First run normally to download/cache models, then use offline mode.")
    print("\nUsage:")
    print("  export OCR_OFFLINE_MODE=1")
    print("  python your_script.py")
    print("\nOr in code:")
    print("  result = ocr_easy.extract('pdf.pdf', offline_only=True)")


def example_7_error_handling():
    """Example 7: Proper error handling in production."""
    print("\n" + "="*70)
    print("EXAMPLE 7: Production Error Handling")
    print("="*70)

    def extract_with_fallback(pdf_path: str) -> dict:
        """Extract text with automatic fallback between methods."""

        # Try Tesseract first (fast, no network)
        logger.info(f"Trying Tesseract on {pdf_path}...")
        result = ocr_tesseract.extract(pdf_path, preprocess=False)

        if result.confidence > 0.5:
            logger.info(f"Tesseract succeeded (confidence: {result.confidence:.2%})")
            return {
                "success": True,
                "method": "tesseract",
                "confidence": result.confidence,
                "pages": len(result.pages),
            }

        logger.warning("Tesseract produced low confidence, trying advanced...")
        result = ocr_tesseract.extract(pdf_path, preprocess=True, dpi=400)

        if result.confidence > 0.5:
            logger.info(f"Tesseract advanced succeeded (confidence: {result.confidence:.2%})")
            return {
                "success": True,
                "method": "tesseract_advanced",
                "confidence": result.confidence,
                "pages": len(result.pages),
            }

        # Last resort: EasyOCR
        logger.warning("Tesseract advanced insufficient, trying EasyOCR...")
        if not check_network():
            logger.error("Network unavailable and Tesseract failed")
            return {
                "success": False,
                "method": None,
                "error": "No OCR method succeeded; network unavailable for EasyOCR",
            }

        result = ocr_easy.extract(pdf_path, max_retries=3, timeout_sec=60)

        if result.confidence > 0:
            logger.info(f"EasyOCR succeeded (confidence: {result.confidence:.2%})")
            return {
                "success": True,
                "method": "easyocr",
                "confidence": result.confidence,
                "pages": len(result.pages),
            }

        logger.error("All OCR methods failed")
        return {
            "success": False,
            "method": None,
            "error": "All OCR methods failed",
            "warnings": result.warnings,
        }

    # Demonstration
    print("Production fallback chain:")
    print("  1. Tesseract basic (fast)")
    print("  2. Tesseract advanced (preprocessing)")
    print("  3. EasyOCR (neural, best quality)")
    print("\nCode:")
    print("""
    result = extract_with_fallback("document.pdf")
    if result["success"]:
        print(f"Extracted {result['pages']} pages using {result['method']}")
    else:
        print(f"Extraction failed: {result['error']}")
    """)


if __name__ == "__main__":
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  OCR ROBUSTNESS EXAMPLES".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)

    example_1_check_network()
    example_2_configure_retries()
    example_3_tesseract_basic()
    example_4_tesseract_advanced()
    example_5_easyocr_with_fallback()
    example_6_offline_mode()
    example_7_error_handling()

    print("\n" + "="*70)
    print("For more information, see: docs/OCR_RESILIENCE.md")
    print("="*70 + "\n")
