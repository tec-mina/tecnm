"""
features/ocr_easy.py — EasyOCR neural OCR backend (GPU optional, multi-language).

Fallback when Tesseract is not available or for better multi-language support.
Uses easyocr library with GPU acceleration if CUDA is available.
"""

from __future__ import annotations

import os
import sys
import tempfile

from ._protocol import StrategyMeta

STRATEGY = StrategyMeta(
    name="ocr:easyocr",
    tier="ocr",
    description="EasyOCR neural OCR — GPU optional, good multi-language support",
    module="pdf_extractor.features.ocr_easy",
    requires_python=["easyocr"],
    priority=20,
    is_gpu_optional=True,
)

try:
    import easyocr
except ImportError:
    easyocr = None  # type: ignore

try:
    import pymupdf as fitz
except ImportError:
    try:
        import fitz
    except ImportError:
        fitz = None  # type: ignore

from ._base import FeatureResult, PageResult

_DEFAULT_LANGS = ["es", "en"]


def extract(pdf_path: str, page_range: tuple[int, int] | None = None,
            langs: list[str] | None = None) -> FeatureResult:
    result = FeatureResult(feature="ocr_easy")

    if easyocr is None:
        result.warnings.append("easyocr not installed; ocr_easy skipped")
        return result
    if fitz is None:
        result.warnings.append("pymupdf not installed; ocr_easy skipped")
        return result

    langs = langs or _DEFAULT_LANGS

    try:
        gpu = _has_gpu()
        reader = easyocr.Reader(langs, gpu=gpu, verbose=False)
    except Exception as exc:
        result.warnings.append(f"EasyOCR init failed: {exc}")
        result.confidence = 0.0
        return result

    md_parts: list[str] = []
    pages_processed = 0

    try:
        doc = fitz.open(pdf_path)
        total = doc.page_count
        start, end = _resolve_range(page_range, total)

        for page_num in range(start, end):
            page = doc[page_num]
            page_1indexed = page_num + 1

            mat = fitz.Matrix(300 / 72, 300 / 72)
            pix = page.get_pixmap(matrix=mat)

            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp_path = tmp.name
            try:
                pix.save(tmp_path)
                detections = reader.readtext(tmp_path, detail=0, paragraph=True)
                text = "\n".join(detections)
            finally:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass

            if text.strip():
                md_parts.append(f"\n<!-- Page {page_1indexed} -->\n\n{text.strip()}")
                result.pages.append(PageResult(
                    page=page_1indexed, content=text.strip(), backend="easyocr"
                ))
                pages_processed += 1

        doc.close()

    except Exception as exc:
        result.warnings.append(f"ocr_easy error: {exc}")
        result.confidence = 0.0
        return result

    result.markdown = "\n".join(md_parts)
    result.confidence = 0.78 if pages_processed > 0 else 0.0
    result.metadata = {
        "pages_processed": pages_processed,
        "backend": "easyocr",
        "gpu": _has_gpu(),
        "langs": langs,
    }
    return result


def _has_gpu() -> bool:
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


def _resolve_range(page_range, total):
    if page_range is None:
        return 0, total
    return max(0, page_range[0] - 1), min(total, page_range[1])
