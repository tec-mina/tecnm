"""
features/text_pdfminer.py — pdfminer.six character-level text extraction.

Strategy: text:pdfminer

Key advantage over text_fast (PyMuPDF):
  pdfminer explicitly resolves ToUnicode and Encoding tables per glyph,
  which makes it significantly better for PDFs that use custom fonts,
  Type1/CFF fonts with non-standard encodings, or documents with
  mathematical/technical symbols that PyMuPDF sometimes maps incorrectly.

It also preserves reading order through LAParams analysis and exposes
font-size info per character — useful for heading detection.

When to prefer over text:fast
------------------------------
  - PDFs with custom glyph→Unicode mappings (legal, government, academic)
  - Documents where PyMuPDF produces garbage characters for some words
  - PDFs using symbolic fonts (Wingdings, Symbol, ZapfDingbats)
"""

from __future__ import annotations

import io

from ._base import FeatureResult, PageResult
from ._protocol import StrategyMeta


STRATEGY = StrategyMeta(
    name="text:pdfminer",
    tier="text",
    description="pdfminer.six — character-level extraction, best for custom font encodings",
    module="pdf_extractor.features.text_pdfminer",
    requires_python=["pdfminer"],
    priority=25,
)


def extract(pdf_path: str, page_range: tuple[int, int] | None = None) -> FeatureResult:
    result = FeatureResult(feature="text_pdfminer")

    try:
        from pdfminer.high_level import extract_pages
        from pdfminer.layout import (
            LAParams, LTPage, LTTextBox, LTTextLine, LTChar, LTFigure,
        )
    except ImportError:
        result.warnings.append("pdfminer.six not installed; text_pdfminer skipped")
        return result

    try:
        laparams = LAParams(
            line_margin=0.5,        # vertical distance for same line
            char_margin=2.0,        # horizontal distance for same word
            word_margin=0.1,
            detect_vertical=False,
        )

        start = (page_range[0] - 1) if page_range else None
        end = page_range[1] if page_range else None

        pages_processed = 0

        for page_layout in extract_pages(pdf_path, laparams=laparams,
                                         page_numbers=_page_numbers(start, end, pdf_path)):
            page_num = page_layout.pageid
            lines_out: list[str] = []

            for element in page_layout:
                if isinstance(element, LTTextBox):
                    box_lines: list[str] = []
                    for line in element:
                        if isinstance(line, LTTextLine):
                            text = line.get_text().rstrip("\n")
                            if text.strip():
                                box_lines.append(text)
                    if box_lines:
                        lines_out.append("\n".join(box_lines))

            if lines_out:
                content = "\n\n".join(lines_out)
                result.pages.append(PageResult(
                    page=page_num,
                    content=content,
                    backend="pdfminer",
                    confidence=0.83,
                ))
                pages_processed += 1

        result.confidence = 0.83 if pages_processed > 0 else 0.0
        result.metadata = {"pages_processed": pages_processed, "backend": "pdfminer.six"}

    except Exception as exc:
        result.warnings.append(f"text_pdfminer error: {exc}")

    return result


def _page_numbers(start, end, pdf_path):
    """Return a list of 0-indexed page numbers for pdfminer, or None for all."""
    if start is None and end is None:
        return None
    try:
        from pdfminer.high_level import extract_pages
        import pdfminer.pdfpage as _pp
        with open(pdf_path, "rb") as f:
            total = sum(1 for _ in _pp.PDFPage.get_pages(f))
        s = start or 0
        e = min(end, total) if end else total
        return list(range(s, e))
    except Exception:
        return None
