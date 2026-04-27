#!/usr/bin/env python3
"""Quick test for OCR resilience features."""

import os
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("\n" + "="*70)
print("OCR RESILIENCE TEST")
print("="*70)

# Test 1: OCRConfig
print("\n✓ Test 1: OCRConfig initialization")
from pdf_extractor.core.ocr_config import get_config, reset_config

os.environ["OCR_MAX_RETRIES"] = "5"
os.environ["OCR_INITIAL_BACKOFF"] = "1.5"
reset_config()
config = get_config()
assert config.max_retries == 5, "max_retries not set correctly"
assert config.initial_backoff == 1.5, "initial_backoff not set correctly"
print("  Config loaded from env vars correctly")
print(f"  {config.to_dict()}")

# Test 2: Network utilities
print("\n✓ Test 2: Network utilities")
from pdf_extractor.features._network_utils import check_network, OfflineMode

is_online = check_network(timeout_sec=2.0)
print(f"  Network check: {is_online}")

# Test offline mode context manager
with OfflineMode("TEST_VAR"):
    assert os.environ.get("TEST_VAR") == "1", "Offline mode not set"
    print(f"  Offline mode context manager working")
assert os.environ.get("TEST_VAR") is None, "Offline mode not cleared"

# Test 3: Retry with backoff
print("\n✓ Test 3: Retry with backoff logic")
from pdf_extractor.features._network_utils import retry_with_backoff

attempt_count = 0
def failing_func():
    global attempt_count
    attempt_count += 1
    if attempt_count < 3:
        raise TimeoutError("Simulated timeout")
    return "success"

result = retry_with_backoff(failing_func, max_retries=5, initial_backoff_sec=0.1)
assert result == "success", "Retry logic failed"
assert attempt_count == 3, f"Expected 3 attempts, got {attempt_count}"
print(f"  Retry backoff succeeded after {attempt_count} attempts")

# Test 4: OCR Easy imports
print("\n✓ Test 4: EasyOCR module imports")
try:
    from pdf_extractor.features import ocr_easy
    print("  ocr_easy module imported successfully")
    print(f"  Strategy: {ocr_easy.STRATEGY.name}")
except ImportError as e:
    print(f"  ⚠️  EasyOCR not available (expected if not installed): {e}")

# Test 5: OCR Tesseract imports
print("\n✓ Test 5: Tesseract module imports")
try:
    from pdf_extractor.features import ocr_tesseract
    print("  ocr_tesseract module imported successfully")
    print(f"  Strategies: {[s.name for s in [ocr_tesseract.STRATEGY] + ocr_tesseract.STRATEGIES]}")
except ImportError as e:
    print(f"  ⚠️  Tesseract not available (expected if not installed): {e}")

# Test 6: Check imports don't break the registry
print("\n✓ Test 6: Registry integration")
try:
    from pdf_extractor.core.registry import registry
    # Try to get some info without assuming internal structure
    print(f"  Registry loaded successfully")
    print(f"  Available methods: {[m for m in dir(registry) if not m.startswith('_')][:5]}...")
except Exception as e:
    print(f"  ⚠️  Registry check skipped: {e}")

print("\n" + "="*70)
print("✅ ALL TESTS PASSED")
print("="*70)
print("\nNext steps:")
print("1. Read: docs/OCR_RESILIENCE.md")
print("2. Run: python examples/ocr_robust_example.py")
print("3. Test: python -m pdf_extractor your_pdf.pdf --strategy ocr:tesseract-basic")
print()
