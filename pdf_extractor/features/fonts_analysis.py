"""
features/fonts_analysis.py — Extract font metadata and produce structure-aware text.

Strategy: fonts:analyze

Uses PyMuPDF span-level font data to:
  - Detect body font size (median of all spans)
  - Mark bold/italic spans
  - Promote visually-prominent spans (large or bold) to Markdown headings
    when they appear alone on a line

Confidence is set lower (0.72) than text_fast so it only wins on pages
where text extraction completely fails — its real value is the metadata
it provides to callers that want to understand document structure.
"""

from __future__ import annotations

from ._base import FeatureResult, PageResult
from ._protocol import StrategyMeta


STRATEGY = StrategyMeta(
    name="fonts:analyze",
    tier="fonts",
    description="Extract font metadata (name, size, bold/italic) and structure hints",
    module="pdf_extractor.features.fonts_analysis",
    requires_python=["fitz"],
    priority=10,
)

# PyMuPDF span flag bitmask values
_F_SUPERSCRIPT = 1
_F_ITALIC = 2
_F_SERIFED = 4
_F_MONOSPACED = 8
_F_BOLD = 16

# A span is "heading-like" if its size exceeds body size by this factor
_HEADING_SIZE_FACTOR = 1.20


def extract(pdf_path: str, page_range: tuple[int, int] | None = None) -> FeatureResult:
    result = FeatureResult(feature="fonts_analysis")

    try:
        try:
            import pymupdf as fitz
        except ImportError:
            import fitz  # type: ignore
    except ImportError:
        result.warnings.append("PyMuPDF not installed; fonts_analysis skipped")
        return result

    try:
        doc = fitz.open(pdf_path)
    except Exception as exc:
        result.warnings.append(f"Cannot open PDF: {exc}")
        return result

    total_pages = doc.page_count
    start = (page_range[0] - 1) if page_range else 0
    end = page_range[1] if page_range else total_pages

    # ── Pass 1: collect size samples to estimate body font size ──────────
    size_samples: list[float] = []
    for page_idx in range(start, min(end, total_pages)):
        page = doc[page_idx]
        for block in _iter_text_blocks(page):
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    if span.get("text", "").strip():
                        size_samples.append(span["size"])

    body_size = _median(size_samples) if size_samples else 11.0
    heading_min = body_size * _HEADING_SIZE_FACTOR

    # ── Pass 2: produce annotated text ───────────────────────────────────
    font_info: dict[str, set[str]] = {}   # page_num → unique font names

    try:
        for page_idx in range(start, min(end, total_pages)):
            page = doc[page_idx]
            page_num = page_idx + 1
            lines_out: list[str] = []
            page_fonts: set[str] = set()

            for block in _iter_text_blocks(page):
                for line in block.get("lines", []):
                    spans_text: list[str] = []
                    max_size_in_line = 0.0
                    is_line_bold = False

                    for span in line.get("spans", []):
                        raw = span.get("text", "")
                        if not raw.strip():
                            continue
                        size = span["size"]
                        flags = span.get("flags", 0)
                        is_bold = bool(flags & _F_BOLD)
                        is_italic = bool(flags & _F_ITALIC)
                        font_name = span.get("font", "")
                        if font_name:
                            page_fonts.add(font_name)

                        if size > max_size_in_line:
                            max_size_in_line = size
                        if is_bold:
                            is_line_bold = True

                        # Inline styling
                        if is_bold and is_italic:
                            spans_text.append(f"***{raw.strip()}***")
                        elif is_bold:
                            spans_text.append(f"**{raw.strip()}**")
                        elif is_italic:
                            spans_text.append(f"*{raw.strip()}*")
                        else:
                            spans_text.append(raw.strip())

                    if not spans_text:
                        continue

                    joined = " ".join(spans_text).strip()

                    # Promote visually-prominent single-line spans to headings
                    if max_size_in_line >= heading_min or (is_line_bold and len(joined) < 120):
                        # Estimate heading level from size ratio
                        ratio = max_size_in_line / body_size if body_size else 1.0
                        level = max(1, min(4, int(5 - ratio)))
                        lines_out.append(f"{'#' * level} {joined.strip('*').strip()}")
                    else:
                        lines_out.append(joined)

            if lines_out:
                result.pages.append(PageResult(
                    page=page_num,
                    content="\n\n".join(lines_out),
                    content_type="text",
                    backend="pymupdf-fonts",
                    confidence=0.72,
                ))
                font_info[str(page_num)] = page_fonts
    finally:
        doc.close()

    result.confidence = 0.72 if result.pages else 0.0
    result.metadata = {
        "body_size_estimate": round(body_size, 1),
        "heading_threshold": round(heading_min, 1),
        "unique_fonts": list({f for fonts in font_info.values() for f in fonts}),
    }
    return result


# ── Helpers ──────────────────────────────────────────────────────────────────

def _iter_text_blocks(page):
    try:
        import pymupdf as fitz
    except ImportError:
        import fitz  # type: ignore
    data = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
    for block in data.get("blocks", []):
        if block.get("type") == 0:   # 0 = text
            yield block


def _median(values: list[float]) -> float:
    if not values:
        return 11.0
    s = sorted(values)
    return s[len(s) // 2]
