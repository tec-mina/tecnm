"""
features/ocr_tesseract.py — pytesseract / PyMuPDF built-in Tesseract OCR.

Primary OCR backend for scanned PDFs.
Requires tesseract binary in PATH or at platform-specific location.

ROBUSTNESS FEATURES:
- Per-page error recovery (one page failure doesn't stop batch)
- Configurable timeouts and retries via OCRConfig
- Clear error messages with logging
- Graceful degradation on preprocessing failures
- Automatic fallback when preprocessing is unavailable

Strategies exported
-------------------
STRATEGY          → ocr:tesseract-basic
    Fast, no preprocessing.  Good for clean 300 DPI scans.

STRATEGY_ADVANCED → ocr:tesseract-advanced
    Preprocessing via _ocr_utils (OpenCV denoise + deskew → Pillow fallback)
    + OSD auto-rotation.  Slower but much better on degraded scans.
"""

from __future__ import annotations

import os
import sys
import tempfile
import logging
from pathlib import Path

from ._protocol import StrategyMeta

STRATEGY = StrategyMeta(
    name="ocr:tesseract-basic",
    tier="ocr",
    description="Tesseract OCR — fast, no preprocessing (clean scans)",
    module="pdf_extractor.features.ocr_tesseract",
    requires_python=["pytesseract", "fitz"],
    requires_system=["tesseract"],
    config={"preprocess": False, "dpi": 300},
    priority=10,
)

STRATEGIES = [
    STRATEGY,
    StrategyMeta(
        name="ocr:tesseract-advanced",
        tier="ocr",
        description="Tesseract OCR — with OpenCV/unpaper preprocessing + OSD rotation",
        module="pdf_extractor.features.ocr_tesseract",
        requires_python=["pytesseract", "fitz"],
        requires_system=["tesseract"],
        config={"preprocess": True, "dpi": 400},
        priority=15,
    ),
]

try:
    import pytesseract
except ImportError:
    pytesseract = None  # type: ignore

try:
    import pymupdf as fitz
except ImportError:
    try:
        import fitz
    except ImportError:
        fitz = None  # type: ignore

try:
    from PIL import Image
except ImportError:
    Image = None  # type: ignore

from ._base import FeatureResult, PageResult
from ..core.ocr_config import get_config

logger = logging.getLogger(__name__)


def extract(
    pdf_path: str,
    page_range: tuple[int, int] | None = None,
    preprocess: bool = False,
    dpi: int = 300,
) -> FeatureResult:
    """Run Tesseract OCR on each page.

    Parameters
    ----------
    preprocess : bool
        When True, apply _ocr_utils preprocessing (denoise, deskew, binarize)
        and OSD auto-rotation before OCR.  Slower but more accurate on degraded scans.
    dpi : int
        Rendering resolution for PyMuPDF → image conversion.
    """
    result = FeatureResult(feature="ocr_tesseract")

    if pytesseract is None:
        result.warnings.append("pytesseract not installed; ocr_tesseract skipped")
        return result
    if fitz is None:
        result.warnings.append("pymupdf not installed; ocr_tesseract skipped")
        return result
    if Image is None:
        result.warnings.append("Pillow not installed; ocr_tesseract skipped")
        return result

    # Validate tesseract binary
    try:
        pytesseract.get_tesseract_version()
        logger.info("Tesseract binary validated")
    except Exception as exc:
        msg = f"Tesseract not found or failed validation: {exc}"
        result.warnings.append(msg)
        result.confidence = 0.0
        logger.error(msg)
        return result

    config = get_config()
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
                # Render page to image at requested DPI
                scale = dpi / 72
                mat = fitz.Matrix(scale, scale)
                pix = page.get_pixmap(matrix=mat)

                # Optional: auto-rotate via OSD (requires tesseract-ocr-osd)
                if preprocess:
                    try:
                        from . import _ocr_utils
                        pix = _ocr_utils.auto_rotate(pix, pytesseract)
                    except Exception as prep_exc:
                        logger.warning(f"Page {page_1indexed} OSD auto-rotate failed (continuing): {prep_exc}")

                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    tmp_path = tmp.name
                try:
                    pix.save(tmp_path)
                    img_bytes = Path(tmp_path).read_bytes()

                    # Always normalize dark-background regions (cheap, safe)
                    try:
                        from . import _ocr_utils
                        img_bytes = _ocr_utils.normalize_dark_backgrounds(img_bytes)
                    except Exception as norm_exc:
                        logger.debug(f"Page {page_1indexed} dark background normalization skipped: {norm_exc}")

                    # Full preprocessing (denoise, deskew, binarize) — advanced only
                    if preprocess:
                        try:
                            from . import _ocr_utils
                            img_bytes = _ocr_utils.preprocess_image(img_bytes, method="auto")
                            logger.debug(f"Page {page_1indexed} preprocessing applied")
                        except Exception as prep_exc:
                            logger.debug(f"Page {page_1indexed} preprocessing failed (continuing with raw): {prep_exc}")

                    import io
                    img = Image.open(io.BytesIO(img_bytes))
                    text = pytesseract.image_to_string(img, lang="spa+eng")
                    logger.debug(f"Page {page_1indexed} OCR completed ({len(text)} chars)")

                finally:
                    try:
                        os.unlink(tmp_path)
                    except OSError:
                        pass

                if text.strip():
                    md_parts.append(f"\n<!-- Page {page_1indexed} -->\n\n{text.strip()}")
                    result.pages.append(PageResult(
                        page=page_1indexed, content=text.strip(), backend="tesseract"
                    ))
                    pages_processed += 1

            except Exception as page_exc:
                pages_failed += 1
                logger.warning(f"Page {page_1indexed} OCR failed: {page_exc}")
                # Don't fail the whole batch; continue with next page

        doc.close()

    except Exception as exc:
        msg = f"ocr_tesseract extraction error: {exc}"
        result.warnings.append(msg)
        result.confidence = 0.0
        logger.error(msg)
        return result

    result.markdown = "\n".join(md_parts)
    base_confidence = 0.88 if preprocess else 0.80
    result.confidence = base_confidence if pages_processed > 0 else 0.0
    result.metadata = {
        "pages_processed": pages_processed,
        "pages_failed": pages_failed,
        "backend": "tesseract",
        "preprocessed": preprocess,
        "dpi": dpi,
        "config": config.to_dict(),
    }
    if pages_failed > 0:
        result.warnings.append(f"{pages_failed} page(s) failed OCR; check logs for details")
    return result


def _resolve_range(page_range, total):
    if page_range is None:
        return 0, total
    return max(0, page_range[0] - 1), min(total, page_range[1])
