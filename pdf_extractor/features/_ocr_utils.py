"""
features/_ocr_utils.py — Image preprocessing utilities shared by OCR backends.

Available preprocessing methods (tried in order, first available wins):

  opencv   — Denoise + adaptive threshold + deskew (best quality, needs opencv)
  unpaper  — Full scanned-page cleanup via system ``unpaper`` binary
  pil      — Basic contrast + sharpness enhancement via Pillow (always available)

Usage
-----
    from pdf_extractor.features._ocr_utils import preprocess_image, auto_rotate

    better_bytes = preprocess_image(raw_png_bytes, method="auto")
    rotated = auto_rotate(pix, pytesseract)   # returns corrected fitz.Pixmap

All functions are safe to call even when optional deps are absent — they
degrade gracefully and return the original bytes unmodified.
"""

from __future__ import annotations

import io
import shutil
import subprocess
import tempfile
from pathlib import Path


# ── Public API ────────────────────────────────────────────────────────────────

def preprocess_image(img_bytes: bytes, method: str = "auto") -> bytes:
    """Preprocess a raster image for better OCR accuracy.

    Parameters
    ----------
    img_bytes : bytes
        Raw image bytes (PNG preferred).
    method : str
        "auto"    — try opencv → unpaper → pil (first available)
        "opencv"  — force OpenCV pipeline
        "unpaper" — force system unpaper binary
        "pil"     — force Pillow-only pipeline
    """
    if method == "opencv":
        return _preprocess_opencv(img_bytes)
    if method == "unpaper":
        return _preprocess_unpaper(img_bytes)
    if method == "pil":
        return _preprocess_pil(img_bytes)

    # auto: try best → fallback
    result = _preprocess_opencv(img_bytes)
    if result is not img_bytes:
        return result
    result = _preprocess_unpaper(img_bytes)
    if result is not img_bytes:
        return result
    return _preprocess_pil(img_bytes)


def auto_rotate(pix, pytesseract_mod) -> object:
    """Detect page orientation via Tesseract OSD and return a corrected Pixmap.

    Parameters
    ----------
    pix             fitz.Pixmap rendered at OCR resolution.
    pytesseract_mod pytesseract module (already imported by the caller).

    Returns the original *pix* if OSD fails or angle is 0.
    """
    try:
        import pymupdf as fitz
    except ImportError:
        try:
            import fitz  # type: ignore
        except ImportError:
            return pix

    try:
        from PIL import Image
    except ImportError:
        return pix

    try:
        img_bytes = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_bytes))
        osd = pytesseract_mod.image_to_osd(
            img,
            config="--psm 0 -c min_characters_to_try=5",
            output_type=pytesseract_mod.Output.DICT,
        )
        angle = int(osd.get("rotate", 0))
        if angle in (0, 360):
            return pix
        rotated = img.rotate(-angle, expand=True)
        buf = io.BytesIO()
        rotated.save(buf, format="PNG")
        new_pix = fitz.Pixmap(buf.getvalue())
        return new_pix
    except Exception:
        return pix


# ── OpenCV pipeline ───────────────────────────────────────────────────────────

def _preprocess_opencv(img_bytes: bytes) -> bytes:
    try:
        import numpy as np
        import cv2
    except ImportError:
        return img_bytes

    try:
        arr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return img_bytes

        # 1. Denoise
        img = cv2.fastNlMeansDenoising(img, h=10, templateWindowSize=7, searchWindowSize=21)

        # 2. Deskew (basic: find dominant angle via Hough lines)
        img = _deskew_opencv(img)

        # 3. Adaptive binarization
        img = cv2.adaptiveThreshold(
            img, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            blockSize=31,
            C=2,
        )

        _, buf = cv2.imencode(".png", img)
        return buf.tobytes()
    except Exception:
        return img_bytes


def _deskew_opencv(gray) -> object:
    """Minimal deskew: detect angle from text lines and rotate."""
    try:
        import numpy as np
        import cv2

        coords = np.column_stack(np.where(gray < 128))
        if len(coords) < 10:
            return gray
        angle = cv2.minAreaRect(coords.astype(np.float32))[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        if abs(angle) < 0.5:
            return gray
        (h, w) = gray.shape
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC,
                              borderMode=cv2.BORDER_REPLICATE)
    except Exception:
        return gray


# ── unpaper pipeline ──────────────────────────────────────────────────────────

def _preprocess_unpaper(img_bytes: bytes) -> bytes:
    """Run system ``unpaper`` for scanned-page cleanup (deskew + border remove)."""
    if not shutil.which("unpaper"):
        return img_bytes

    try:
        with tempfile.TemporaryDirectory() as tmp:
            in_path = Path(tmp) / "in.pnm"
            out_path = Path(tmp) / "out.pnm"

            # Convert PNG → PNM (unpaper expects PNM/PBM/PGM/PPM)
            in_path.write_bytes(_png_to_pnm(img_bytes))

            proc = subprocess.run(
                ["unpaper", "--overwrite", str(in_path), str(out_path)],
                capture_output=True,
                timeout=30,
            )
            if proc.returncode == 0 and out_path.exists():
                return _pnm_to_png(out_path.read_bytes())
    except Exception:
        pass
    return img_bytes


def _png_to_pnm(img_bytes: bytes) -> bytes:
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        buf = io.BytesIO()
        img.save(buf, format="PPM")
        return buf.getvalue()
    except Exception:
        return img_bytes


def _pnm_to_png(pnm_bytes: bytes) -> bytes:
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(pnm_bytes))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except Exception:
        return pnm_bytes


# ── Pillow-only pipeline ──────────────────────────────────────────────────────

def _preprocess_pil(img_bytes: bytes) -> bytes:
    """Basic contrast + sharpness enhancement with Pillow (always available)."""
    try:
        from PIL import Image, ImageEnhance, ImageFilter
        img = Image.open(io.BytesIO(img_bytes)).convert("L")   # grayscale
        img = ImageEnhance.Contrast(img).enhance(2.0)
        img = ImageEnhance.Sharpness(img).enhance(2.0)
        img = img.filter(ImageFilter.MedianFilter(size=3))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except Exception:
        return img_bytes
