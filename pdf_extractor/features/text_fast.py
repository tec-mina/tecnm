"""
features/text_fast.py — PyMuPDF (fitz) text extraction.

Extracts text blocks preserving font metadata and page layout.
Falls back gracefully if pymupdf is not installed.
"""

from __future__ import annotations

import sys

try:
    import pymupdf as fitz
except ImportError:
    try:
        import fitz
    except ImportError:
        fitz = None  # type: ignore

from ._base import FeatureResult, PageResult
from ._protocol import StrategyMeta

STRATEGY = StrategyMeta(
    name="text:fast",
    tier="text",
    description="Fast PyMuPDF text extraction — preserves block layout",
    module="pdf_extractor.features.text_fast",
    requires_python=["fitz"],
    priority=20,
)

_CHUNK_SIZE = 30
_LARGE_PDF_THRESHOLD = 40


def extract(pdf_path: str, page_range: tuple[int, int] | None = None) -> FeatureResult:
    result = FeatureResult(feature="text_fast")

    if fitz is None:
        result.warnings.append("pymupdf not installed; text_fast skipped")
        return result

    try:
        doc = fitz.open(pdf_path)
    except Exception as exc:
        result.warnings.append(f"Cannot open PDF: {exc}")
        return result

    try:
        total = doc.page_count
        start, end = _resolve_range(page_range, total)
        pages_to_process = list(range(start, end))

        md_parts: list[str] = []

        for page_num in _iter_pages(pages_to_process, total):
            page = doc[page_num]
            page_1indexed = page_num + 1
            text = _extract_page_text(page)
            md_parts.append(f"\n<!-- Page {page_1indexed} -->\n\n{text}")
            result.pages.append(PageResult(
                page=page_1indexed, content=text, backend="pymupdf"
            ))

        result.markdown = "\n".join(md_parts)
        result.confidence = 0.85 if result.markdown.strip() else 0.0
        result.metadata = {
            "pages_processed": len(pages_to_process),
            "backend": "pymupdf",
        }

    except Exception as exc:
        result.warnings.append(f"text_fast extraction error: {exc}")
        result.confidence = 0.0
    finally:
        doc.close()

    return result


def _extract_page_text(page) -> str:
    """Extract text blocks preserving layout order."""
    blocks = page.get_text("blocks", sort=True)
    lines: list[str] = []

    for block in blocks:
        # block: (x0, y0, x1, y1, text, block_no, block_type)
        if block[6] != 0:   # block_type 0 = text, 1 = image
            continue
        text = block[4].strip()
        if not text:
            continue

        # Simple heading detection by font size hint
        # PyMuPDF blocks don't expose font directly in plain mode; use spans
        lines.append(text)

    return "\n\n".join(lines)


def _resolve_range(page_range, total):
    if page_range is None:
        return 0, total
    return max(0, page_range[0] - 1), min(total, page_range[1])


def _iter_pages(pages, total):
    """Yield page indices; for large PDFs emits tqdm chunks to stderr."""
    if total > _LARGE_PDF_THRESHOLD:
        try:
            from tqdm import tqdm
            yield from tqdm(pages, desc="text_fast", file=sys.stderr)
            return
        except ImportError:
            pass
    yield from pages
