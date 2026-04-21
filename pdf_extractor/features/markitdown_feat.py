"""
features/markitdown_feat.py — Microsoft MarkItDown broad format support.

No AI model required. Good fallback for complex layouts on Windows.
Requires markitdown library.
"""

from __future__ import annotations

try:
    from markitdown import MarkItDown
except ImportError:
    MarkItDown = None  # type: ignore

from ._base import FeatureResult, PageResult
from ._protocol import StrategyMeta


STRATEGY = StrategyMeta(
    name="text:markitdown",
    tier="text",
    description="Microsoft MarkItDown — broad format support, good Windows fallback",
    module="pdf_extractor.features.markitdown_feat",
    requires_python=["markitdown"],
    priority=45,
)


def extract(pdf_path: str, page_range: tuple[int, int] | None = None) -> FeatureResult:
    result = FeatureResult(feature="markitdown_feat")

    if MarkItDown is None:
        result.warnings.append("markitdown not installed; markitdown_feat skipped")
        return result

    try:
        md_instance = MarkItDown()
        conv = md_instance.convert(pdf_path)
        md_text = conv.text_content or ""

        result.markdown = md_text
        result.confidence = 0.82 if md_text.strip() else 0.0
        result.pages = _split_pages(md_text)
        result.metadata = {"backend": "markitdown"}

    except Exception as exc:
        result.warnings.append(f"markitdown_feat error: {exc}")
        result.confidence = 0.0

    return result


def _split_pages(md: str) -> list[PageResult]:
    import re
    parts = re.split(r"<!-- Page (\d+) -->", md)
    pages: list[PageResult] = []
    i = 1
    while i < len(parts) - 1:
        try:
            page_num = int(parts[i])
            content = parts[i + 1].strip()
            pages.append(PageResult(page=page_num, content=content, backend="markitdown"))
        except (ValueError, IndexError):
            pass
        i += 2
    if not pages and md.strip():
        pages.append(PageResult(page=1, content=md, backend="markitdown"))
    return pages
