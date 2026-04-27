"""
features/ocr_easy.py — EasyOCR neural OCR backend (GPU optional, multi-language).

Fallback when Tesseract is not available or for better multi-language support.
Uses easyocr library with GPU acceleration if CUDA is available.

ROBUSTNESS FEATURES:
- Automatic retries with exponential backoff for network errors
- Configurable timeouts and retry limits
- Offline mode: uses cached models if available
- Network validation before initialization
- Per-page error recovery (one page failure doesn't stop the whole batch)
- Clear error messages (what failed and why)
"""

from __future__ import annotations

import os
import sys
import tempfile
import logging

from ._protocol import StrategyMeta
from ._network_utils import check_network, retry_with_backoff, OfflineMode, report_failure

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
_MAX_RETRIES = 3
_INITIAL_BACKOFF_SEC = 2.0
_TIMEOUT_SEC = 30.0

logger = logging.getLogger(__name__)


def extract(pdf_path: str, page_range: tuple[int, int] | None = None,
            langs: list[str] | None = None,
            max_retries: int = _MAX_RETRIES,
            timeout_sec: float = _TIMEOUT_SEC,
            offline_only: bool = False) -> FeatureResult:
    """Extract text from PDF using EasyOCR with network resilience.

    Args:
        pdf_path: Path to PDF file
        page_range: (start, end) page numbers (1-indexed)
        langs: Languages for OCR (default: ["es", "en"])
        max_retries: Number of retries on network failure
        timeout_sec: Timeout per operation (seconds)
        offline_only: If True, only use cached models (no network)
    """
    result = FeatureResult(feature="ocr_easy")

    if easyocr is None:
        result.warnings.append("easyocr not installed; ocr_easy skipped")
        return result
    if fitz is None:
        result.warnings.append("pymupdf not installed; ocr_easy skipped")
        return result

    langs = langs or _DEFAULT_LANGS

    # Validate network if not offline_only
    if not offline_only and not _check_network():
        msg = "Network unavailable; EasyOCR needs to download models. Use offline_only=True to skip, or check internet connection."
        result.warnings.append(msg)
        logger.warning(msg)
        return result

    # Initialize reader with retries
    reader = _init_reader_with_retries(
        langs, max_retries=max_retries, timeout_sec=timeout_sec, offline_only=offline_only
    )
    if reader is None:
        msg = f"EasyOCR initialization failed after {max_retries} retries; check network and model cache"
        result.warnings.append(msg)
        result.confidence = 0.0
        logger.error(msg)
        return result

    md_parts: list[str] = []
    pages_processed = 0
    pages_failed = 0

    try:
        doc = fitz.open(pdf_path)
        total = doc.page_count
        start, end = _resolve_range(page_range, total)

        for page_num in range(start, end):
            page = doc[page_num]
            page_1indexed = page_num + 1

            try:
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

            except Exception as page_exc:
                pages_failed += 1
                logger.warning(f"Page {page_1indexed} OCR failed: {page_exc}")
                # Don't fail the whole batch; continue with next page

        doc.close()

    except Exception as exc:
        msg = f"ocr_easy extraction error: {exc}"
        result.warnings.append(msg)
        logger.error(msg)
        result.confidence = 0.0
        return result

    result.markdown = "\n".join(md_parts)
    result.confidence = 0.78 if pages_processed > 0 else 0.0
    result.metadata = {
        "pages_processed": pages_processed,
        "pages_failed": pages_failed,
        "backend": "easyocr",
        "gpu": _has_gpu(),
        "langs": langs,
    }
    if pages_failed > 0:
        result.warnings.append(f"{pages_failed} page(s) failed OCR; check logs for details")
    return result


def _init_reader_with_retries(
    langs: list[str],
    max_retries: int = _MAX_RETRIES,
    timeout_sec: float = _TIMEOUT_SEC,
    offline_only: bool = False,
) -> easyocr.Reader | None:
    """Initialize EasyOCR Reader with exponential backoff retries.

    Returns:
        Reader instance or None if all retries failed.
    """
    gpu = _has_gpu()

    def init_func():
        logger.info(f"EasyOCR Reader init (gpu={gpu}, offline={offline_only})...")
        with OfflineMode() if offline_only else _NoOpContextManager():
            reader = easyocr.Reader(langs, gpu=gpu, verbose=False)
            logger.info("EasyOCR Reader initialized successfully")
            return reader

    return retry_with_backoff(
        init_func,
        max_retries=max_retries,
        initial_backoff_sec=_INITIAL_BACKOFF_SEC,
        name="EasyOCR Reader init",
    )


class _NoOpContextManager:
    """No-op context manager for conditional context manager usage."""
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass


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
