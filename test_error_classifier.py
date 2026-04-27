#!/usr/bin/env python3
"""
test_error_classifier.py — Test ErrorClassifier and FallbackRouter.
"""

import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent))

from pdf_extractor.core.error_classifier import (
    ErrorClassifier,
    FallbackRouter,
    ErrorCategory,
    classify_error,
)


def test_timeout_error_classification():
    """Test that timeout errors are classified correctly"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 1: Timeout error classification")
    logger.info("=" * 80)

    exc = TimeoutError("Operation timed out after 30 seconds")
    classifier = ErrorClassifier()
    analysis = classifier.classify(exc, "ocr:tesseract-basic")

    assert analysis.category == ErrorCategory.TIMEOUT, f"Expected TIMEOUT, got {analysis.category}"
    assert analysis.is_recoverable, "Timeout should be recoverable"
    assert not analysis.is_critical, "Timeout should not be critical"
    assert analysis.fallback_priority == 0, "Timeout should have highest priority"
    logger.info(f"✅ Category: {analysis.category.value}")
    logger.info(f"   Recoverable: {analysis.is_recoverable}")
    logger.info(f"   Action: {analysis.suggested_action}")


def test_dependency_missing_error():
    """Test that missing dependency errors are classified correctly"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 2: Dependency missing error classification")
    logger.info("=" * 80)

    exc = ModuleNotFoundError("No module named 'easyocr'")
    classifier = ErrorClassifier()
    analysis = classifier.classify(exc, "ocr:easyocr")

    assert analysis.category == ErrorCategory.DEPENDENCY_MISSING
    assert not analysis.is_recoverable, "Missing dependency is not recoverable"
    assert analysis.fallback_priority > 4, "Missing dependency has low priority"
    logger.info(f"✅ Category: {analysis.category.value}")
    logger.info(f"   Recoverable: {analysis.is_recoverable}")
    logger.info(f"   Action: {analysis.suggested_action}")


def test_memory_error_classification():
    """Test that memory errors are classified correctly"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 3: Memory error classification")
    logger.info("=" * 80)

    exc = MemoryError("Out of memory")
    classifier = ErrorClassifier()
    analysis = classifier.classify(exc, "text:fast", context={"page_number": 42})

    assert analysis.category == ErrorCategory.MEMORY_ERROR
    assert analysis.is_recoverable, "Memory error should be recoverable"
    logger.info(f"✅ Category: {analysis.category.value}")
    logger.info(f"   Action: {analysis.suggested_action}")
    assert "page 42" in analysis.suggested_action


def test_corrupt_input_error():
    """Test that corruption errors are classified correctly"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 4: Corrupt input error classification")
    logger.info("=" * 80)

    exc = ValueError("Corrupt or unreadable PDF")
    classifier = ErrorClassifier()
    analysis = classifier.classify(exc, "ocr:tesseract-advanced")

    assert analysis.category == ErrorCategory.CORRUPT_INPUT
    assert analysis.is_recoverable, "Corruption should be recoverable via fallback"
    logger.info(f"✅ Category: {analysis.category.value}")
    logger.info(f"   Action: {analysis.suggested_action}")


def test_permission_error_classification():
    """Test that permission errors are classified correctly"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 5: Permission error classification")
    logger.info("=" * 80)

    exc = PermissionError("Permission denied: /restricted/file.pdf")
    classifier = ErrorClassifier()
    analysis = classifier.classify(exc, "text:pdfminer")

    assert analysis.category == ErrorCategory.PERMISSION_ERROR
    assert not analysis.is_recoverable, "Permission error is not recoverable"
    assert analysis.is_critical, "Permission error should be critical"
    logger.info(f"✅ Category: {analysis.category.value}")
    logger.info(f"   Is critical: {analysis.is_critical}")


def test_encoding_error_classification():
    """Test that encoding errors are classified correctly"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 6: Encoding error classification")
    logger.info("=" * 80)

    exc = UnicodeDecodeError("utf-8", b"bad", 0, 1, "invalid start byte")
    classifier = ErrorClassifier()
    analysis = classifier.classify(exc, "text:tika")

    assert analysis.category == ErrorCategory.ENCODING_ERROR
    assert analysis.is_recoverable, "Encoding error should be recoverable"
    logger.info(f"✅ Category: {analysis.category.value}")
    logger.info(f"   Action: {analysis.suggested_action}")


def test_network_error_classification():
    """Test that network errors are classified correctly"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 7: Network error classification")
    logger.info("=" * 80)

    exc = ConnectionError("Network is unreachable")
    classifier = ErrorClassifier()
    analysis = classifier.classify(exc, "text:docling")

    assert analysis.category == ErrorCategory.NETWORK_ERROR
    assert analysis.is_recoverable, "Network error should be recoverable"
    logger.info(f"✅ Category: {analysis.category.value}")
    logger.info(f"   Action: {analysis.suggested_action}")


def test_fallback_router_same_tier():
    """Test that fallback router provides same-tier fallbacks"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 8: Fallback router - same tier fallbacks")
    logger.info("=" * 80)

    router = FallbackRouter(registry=None)

    # Text tier fallback
    fallback = router.get_fallback_chain("text:fast")
    assert "text:pdfminer" in fallback, "Should include text:pdfminer"
    assert "text:fast" not in fallback, "Should not include original method"
    logger.info(f"✅ text:fast fallbacks: {fallback}")

    # OCR tier fallback
    fallback = router.get_fallback_chain("ocr:tesseract-basic")
    assert "ocr:tesseract-advanced" in fallback, "Should include ocr:tesseract-advanced"
    assert "ocr:easyocr" in fallback, "Should include ocr:easyocr"
    logger.info(f"✅ ocr:tesseract-basic fallbacks: {fallback}")


def test_fallback_router_cross_tier():
    """Test that fallback router provides cross-tier fallbacks"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 9: Fallback router - cross-tier fallbacks")
    logger.info("=" * 80)

    router = FallbackRouter(registry=None)

    # Should only cross tier for severe errors
    from pdf_extractor.core.error_classifier import ErrorAnalysis, ErrorCategory

    analysis = ErrorAnalysis(
        category=ErrorCategory.CORRUPT_INPUT,
        message="PDF is corrupt",
        original_exception=None,
        is_recoverable=True,
        is_critical=False,
        suggested_action="Try fallback",
        fallback_priority=1,
    )

    should_cross = router.should_cross_tier("text:fast", analysis)
    assert should_cross, "Should cross tier for corrupt input"
    logger.info(f"✅ Should cross tier for CORRUPT_INPUT: {should_cross}")

    # Should not cross tier for mild errors
    analysis.category = ErrorCategory.TIMEOUT
    should_cross = router.should_cross_tier("text:fast", analysis)
    assert not should_cross, "Should not cross tier for timeout"
    logger.info(f"✅ Should not cross tier for TIMEOUT: {not should_cross}")


def test_should_retry_and_fallback():
    """Test retry/fallback decision logic"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 10: Retry and fallback decision logic")
    logger.info("=" * 80)

    classifier = ErrorClassifier()

    # Timeout: should retry
    timeout_exc = TimeoutError("Operation timed out")
    timeout_analysis = classifier.classify(timeout_exc, "ocr:tesseract")
    assert classifier.should_retry(timeout_analysis), "Should retry on timeout"
    assert classifier.should_try_fallback(
        timeout_analysis
    ), "Should try fallback on timeout"
    logger.info(f"✅ Timeout: retry={classifier.should_retry(timeout_analysis)}, fallback={classifier.should_try_fallback(timeout_analysis)}")

    # Permission: should not retry
    perm_exc = PermissionError("Access denied")
    perm_analysis = classifier.classify(perm_exc, "text:fast")
    assert not classifier.should_retry(
        perm_analysis
    ), "Should not retry on permission error"
    assert not classifier.should_try_fallback(
        perm_analysis
    ), "Should not try fallback on permission error"
    logger.info(f"✅ Permission: retry={classifier.should_retry(perm_analysis)}, fallback={classifier.should_try_fallback(perm_analysis)}")


def test_convenience_function():
    """Test classify_error convenience function"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 11: Convenience function classify_error()")
    logger.info("=" * 80)

    exc = RuntimeError("Timed out after 60 seconds")
    analysis = classify_error(exc, "tables:pdfplumber", context={"page_number": 10})

    assert analysis.category == ErrorCategory.TIMEOUT
    assert "page 10" in analysis.suggested_action
    logger.info(f"✅ Classified as {analysis.category.value}")
    logger.info(f"   Action: {analysis.suggested_action}")


if __name__ == "__main__":
    print("\n" + "█" * 80)
    print("█" + " " * 78 + "█")
    print("█" + "  ERROR CLASSIFIER TESTS".center(78) + "█")
    print("█" + " " * 78 + "█")
    print("█" * 80)

    try:
        test_timeout_error_classification()
        test_dependency_missing_error()
        test_memory_error_classification()
        test_corrupt_input_error()
        test_permission_error_classification()
        test_encoding_error_classification()
        test_network_error_classification()
        test_fallback_router_same_tier()
        test_fallback_router_cross_tier()
        test_should_retry_and_fallback()
        test_convenience_function()

        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED")
        print("=" * 80 + "\n")
        print("Phase 2.2 Status: ✅ ErrorClassifier and FallbackRouter operational")
        print("=" * 80 + "\n")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        import traceback

        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback

        traceback.print_exc()
        sys.exit(1)
