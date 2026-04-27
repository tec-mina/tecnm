# OCR Resilience Guide

This document explains how the OCR backends are configured for robustness and how to diagnose/resolve common issues.

## Overview

All OCR backends (EasyOCR, Tesseract) now implement:

- ✅ **Per-page error recovery** — one page failure doesn't stop the entire batch
- ✅ **Network resilience** — automatic retries with exponential backoff
- ✅ **Clear error messages** — exactly what failed and suggestions for fixes
- ✅ **Configurable timeouts** — environment variables control behavior
- ✅ **Graceful degradation** — fallback to simpler methods when advanced features fail
- ✅ **Offline mode** — use cached models without network access

## Configuration

### Environment Variables

All OCR timeouts and retry behavior is controlled via environment variables:

```bash
# Maximum number of retries on network/timeout errors (default: 3)
export OCR_MAX_RETRIES=3

# Initial backoff duration in seconds, then doubles each retry (default: 2.0)
export OCR_INITIAL_BACKOFF=2.0

# Timeout per page in seconds (default: 30.0)
export OCR_PAGE_TIMEOUT=30.0

# Timeout for initialization/model download in seconds (default: 60.0)
export OCR_INIT_TIMEOUT=60.0

# Force offline mode: use cached models only, no network (default: 0)
export OCR_OFFLINE_MODE=1
```

### Python API

```python
from pdf_extractor.core.ocr_config import get_config

config = get_config()
print(config.to_dict())
# {
#     'max_retries': 3,
#     'initial_backoff': 2.0,
#     'page_timeout': 30.0,
#     'init_timeout': 60.0,
#     'offline_mode': False
# }
```

## EasyOCR Specifics

### Common Issues

#### 1. **Network error on initialization**

**Error:** `✕ Network error` when calling `easyocr.Reader()`

**Root Cause:** EasyOCR downloads neural models from the internet on first use. Network connectivity is required.

**Solutions:**

a) **Check internet connection:**
```bash
ping 8.8.8.8
curl -I https://github.com
```

b) **Increase timeouts:**
```bash
export OCR_INIT_TIMEOUT=120  # 2 minutes
export OCR_MAX_RETRIES=5      # More retries
python your_script.py
```

c) **Use offline mode (with cached models):**
```bash
# First run on a machine with internet to download/cache models
python your_script.py

# Then on offline machine:
export OCR_OFFLINE_MODE=1
python your_script.py
```

d) **Pre-download models manually:**
```python
import easyocr
import os

# This downloads and caches models for Spanish + English
reader = easyocr.Reader(['es', 'en'], gpu=False)
print("Models cached successfully")
```

#### 2. **Memory pressure with large PDFs**

**Error:** `CUDA out of memory` or process killed

**Solution:**
```bash
# Use CPU instead of GPU
CUDA_VISIBLE_DEVICES="" python your_script.py

# Or explicitly disable GPU in code
export OCR_GPU=0  # (if your code checks this)
```

#### 3. **Page-specific failures**

**Error:** One page fails but others succeed

**Expected behavior:** This is now handled gracefully. The page is skipped with a warning logged.

**Check logs:**
```bash
python your_script.py 2>&1 | grep "Page.*failed"
```

## Tesseract Specifics

### Common Issues

#### 1. **Tesseract not found**

**Error:** `Tesseract not found in PATH`

**Solutions:**

a) **Linux/Ubuntu:**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-spa tesseract-ocr-eng
```

b) **macOS:**
```bash
brew install tesseract
brew install tesseract-lang  # for Spanish language pack
```

c) **Windows:**
- Download installer from [GitHub Tesseract Releases](https://github.com/UB-Mannheim/tesseract/wiki)
- Add to PATH or configure in code

#### 2. **Language data missing**

**Error:** Warnings about Spanish or English language data

**Solution:**
```bash
# Linux
sudo apt-get install tesseract-ocr-spa tesseract-ocr-eng

# macOS (already included with tesseract-lang)

# Or download manually to ~/.tesseract/tessdata/
```

#### 3. **Slow or poor accuracy**

**Use preprocessing (advanced strategy):**
```python
from pdf_extractor.features import ocr_tesseract

result = ocr_tesseract.extract(
    pdf_path="scan.pdf",
    preprocess=True,  # Enable denoise, deskew, binarize
    dpi=400  # Higher resolution helps
)
```

## Debugging

### Enable Detailed Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("pdf_extractor")
logger.setLevel(logging.DEBUG)

# Now run your extraction
```

### Check Configuration

```python
from pdf_extractor.core.ocr_config import get_config
import json

config = get_config()
print(json.dumps(config.to_dict(), indent=2))
```

### Test Network Connectivity

```python
from pdf_extractor.features._network_utils import check_network

is_online = check_network()
print(f"Network available: {is_online}")
```

### Test Individual Backends

**EasyOCR:**
```python
from pdf_extractor.features import ocr_easy

result = ocr_easy.extract("test.pdf", offline_only=False)
print(f"Success: {result.confidence > 0}")
print(f"Warnings: {result.warnings}")
print(f"Metadata: {result.metadata}")
```

**Tesseract:**
```python
from pdf_extractor.features import ocr_tesseract

result = ocr_tesseract.extract("test.pdf", preprocess=False)
print(f"Success: {result.confidence > 0}")
print(f"Warnings: {result.warnings}")
print(f"Metadata: {result.metadata}")
```

## Pipeline Behavior

### Feature Selection

The pipeline automatically selects OCR strategies based on:

1. **Text-native PDF?** → Use `text:fast` (no OCR needed)
2. **Scanned PDF?** → Try `ocr:tesseract-basic` → fallback to `ocr:easyocr`
3. **Mixed?** → Use text extraction on text pages, OCR on scanned pages

### Fallback Chain

```
ocr:tesseract-basic (fast, no preprocessing)
    ↓ (if fails or produces nothing)
ocr:tesseract-advanced (with preprocessing)
    ↓ (if fails or produces nothing)
ocr:easyocr (neural OCR, good for degraded scans)
    ↓ (if fails or produces nothing)
    warning: "All OCR methods failed"
```

### Force a Specific Strategy

```python
from pdf_extractor.app.use_cases import extract_pdf

result = extract_pdf(
    pdf_path="scan.pdf",
    forced_features=["ocr:easyocr"]  # Only use EasyOCR
)
```

## Best Practices

### 1. **Start with Tesseract**

Tesseract is:
- Fast ✓
- Local/no network ✓
- Good for clean scans ✓
- Limited for poor-quality or multi-language documents ✗

### 2. **Use Advanced Preprocessing**

For degraded scans, enable preprocessing:

```python
result = ocr_tesseract.extract(
    pdf_path="degraded_scan.pdf",
    preprocess=True,  # OpenCV denoise + deskew
    dpi=400  # Higher resolution
)
```

### 3. **Fallback to EasyOCR for Complex Cases**

EasyOCR handles:
- Handwriting ✓
- Multiple languages ✓
- Rotated text ✓
- Degraded quality ✓

### 4. **Monitor Performance**

Check metadata to understand what worked:

```python
result = ocr_tesseract.extract("document.pdf")
print(result.metadata)
# {
#     'pages_processed': 5,
#     'pages_failed': 0,
#     'backend': 'tesseract',
#     'preprocessed': False,
#     'dpi': 300,
#     'config': {...}
# }
```

### 5. **Handle Partial Failures Gracefully**

Even if some pages fail, you get output for successful pages:

```python
result = extract_pdf("problematic.pdf")
if result.confidence > 0:
    print(f"Got {len(result.pages)} pages of {total} total")
    # Save what we have
    save_markdown(result.markdown)
```

## Troubleshooting Flowchart

```
Does extraction work?
├─ NO
│  ├─ Check logs for "not found" errors
│  │  ├─ Tesseract? → Install tesseract-ocr
│  │  └─ EasyOCR? → Check network or use OCR_OFFLINE_MODE=1
│  │
│  ├─ Check logs for "Network error"
│  │  ├─ Increase OCR_INIT_TIMEOUT
│  │  ├─ Increase OCR_MAX_RETRIES
│  │  └─ Use OCR_OFFLINE_MODE=1 if models are cached
│  │
│  └─ Check logs for "timeout" or "resource"
│     ├─ Increase OCR_PAGE_TIMEOUT
│     ├─ Reduce resolution (dpi=200 instead of 300)
│     └─ Use CPU instead of GPU (CUDA_VISIBLE_DEVICES="")
│
└─ YES
   ├─ Is confidence low?
   │  ├─ Try preprocessing: preprocess=True
   │  ├─ Try higher DPI: dpi=400
   │  └─ Try EasyOCR for degraded quality
   │
   └─ Are some pages blank?
      ├─ Check page_range parameter
      ├─ Check if original PDF is corrupt
      └─ Use both Tesseract and EasyOCR together
```

## Further Reading

- [EasyOCR Documentation](https://github.com/JaidedAI/EasyOCR)
- [Tesseract GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
- [PDF Extractor Core Documentation](../pdf_extractor/core/README.md)
