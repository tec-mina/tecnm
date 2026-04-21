"""
core/detector.py — PDF type classifier.

Classifies each page independently using PyMuPDF + pdfplumber heuristics.
Returns a PDFProfile dataclass consumed by pipeline.py.

Types:
  text_native  — selectable text layer present
  scanned      — raster image only (no text layer)
  mixed        — both (partially digitized)
  has_tables   — line-density + pdfplumber bbox analysis
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence


_TEXT_CHAR_THRESHOLD = 50     # chars per page below this → scanned
_TABLE_RECT_MIN = 4           # minimum pdfplumber rects to flag has_tables


@dataclass
class PDFProfile:
    text_native_pages: list[int] = field(default_factory=list)
    scanned_pages: list[int] = field(default_factory=list)
    mixed_pages: list[int] = field(default_factory=list)
    table_pages: list[int] = field(default_factory=list)
    dominant_language: str = "unknown"
    has_images: bool = False
    page_count: int = 0

    def to_dict(self) -> dict:
        return {
            "text_native_pages": self.text_native_pages,
            "scanned_pages": self.scanned_pages,
            "mixed_pages": self.mixed_pages,
            "table_pages": self.table_pages,
            "dominant_language": self.dominant_language,
            "has_images": self.has_images,
            "page_count": self.page_count,
        }


def run(pdf_path: str, page_range: tuple[int, int] | None = None) -> PDFProfile:
    """
    Classify every page and build a PDFProfile.
    page_range is (start, end) 1-indexed inclusive.
    """
    profile = PDFProfile()

    try:
        import pymupdf as fitz
    except ImportError:
        try:
            import fitz
        except ImportError:
            return profile

    doc = fitz.open(pdf_path)
    try:
        total = doc.page_count
        profile.page_count = total

        start_idx, end_idx = _resolve_range(page_range, total)

        for page_num in range(start_idx, end_idx):
            page = doc[page_num]
            page_1indexed = page_num + 1

            text = page.get_text("text")
            char_count = len(text.strip())

            # Detect images on page
            imgs = page.get_images(full=True)
            if imgs:
                profile.has_images = True

            has_text = char_count >= _TEXT_CHAR_THRESHOLD
            has_raster = bool(imgs)

            if has_text and has_raster:
                profile.mixed_pages.append(page_1indexed)
                profile.text_native_pages.append(page_1indexed)
            elif has_text:
                profile.text_native_pages.append(page_1indexed)
            else:
                profile.scanned_pages.append(page_1indexed)

        # Table detection with pdfplumber (best available)
        _detect_tables(pdf_path, start_idx, end_idx, profile)

        # Language detection on first 3 pages of text
        _detect_language(doc, profile)

    finally:
        doc.close()

    return profile


def _resolve_range(page_range: tuple[int, int] | None, total: int) -> tuple[int, int]:
    if page_range is None:
        return 0, total
    start = max(0, page_range[0] - 1)
    end = min(total, page_range[1])
    return start, end


def _detect_tables(pdf_path: str, start_idx: int, end_idx: int, profile: PDFProfile) -> None:
    try:
        import pdfplumber
    except ImportError:
        return

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for idx in range(start_idx, min(end_idx, len(pdf.pages))):
                page = pdf.pages[idx]
                page_1indexed = idx + 1
                # pdfplumber rect heuristic: count horizontal/vertical lines
                h_lines = [o for o in page.objects.get("line", [])
                           if abs(o.get("height", 1)) < 2]
                v_lines = [o for o in page.objects.get("line", [])
                           if abs(o.get("width", 1)) < 2]
                rects = page.objects.get("rect", [])
                score = len(h_lines) + len(v_lines) + len(rects)
                if score >= _TABLE_RECT_MIN:
                    if page_1indexed not in profile.table_pages:
                        profile.table_pages.append(page_1indexed)
    except Exception:
        pass


def _detect_language(doc, profile: PDFProfile) -> None:
    try:
        from langdetect import detect, LangDetectException
    except ImportError:
        return

    sample_text = ""
    for idx in range(min(3, doc.page_count)):
        sample_text += doc[idx].get_text("text")[:1000]

    if len(sample_text.strip()) < 50:
        return

    try:
        profile.dominant_language = detect(sample_text)
    except Exception:
        pass
