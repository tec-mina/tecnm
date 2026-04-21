"""
features/markdown_llm.py — pymupdf4llm direct LLM-ready Markdown extraction.

Produces cleaner, heading-aware Markdown suitable for LLM consumption.
Falls back to text_fast if pymupdf4llm is not available.
"""

from __future__ import annotations

try:
    import pymupdf4llm
except ImportError:
    pymupdf4llm = None  # type: ignore

from ._base import FeatureResult, PageResult
from ._protocol import StrategyMeta

STRATEGY = StrategyMeta(
    name="text:llm",
    tier="text",
    description="pymupdf4llm — heading-aware Markdown optimised for LLM consumption",
    module="pdf_extractor.features.markdown_llm",
    requires_python=["pymupdf4llm"],
    priority=10,
)


def extract(pdf_path: str, page_range: tuple[int, int] | None = None) -> FeatureResult:
    result = FeatureResult(feature="markdown_llm")

    if pymupdf4llm is None:
        result.warnings.append("pymupdf4llm not installed; markdown_llm skipped")
        return result

    try:
        kwargs: dict = {}
        if page_range is not None:
            # Convert 1-indexed inclusive range → 0-indexed list
            kwargs["pages"] = list(range(page_range[0] - 1, page_range[1]))

        # page_chunks=True returns list[{"metadata": {"page": N, ...}, "text": "..."}]
        # This avoids building one giant string for large documents.
        raw = pymupdf4llm.to_markdown(pdf_path, page_chunks=True, **kwargs)

        if isinstance(raw, list):
            # Per-page mode — process chunk by chunk, never hold full doc in memory
            parts: list[str] = []
            for chunk in raw:
                meta = chunk.get("metadata", {}) if isinstance(chunk, dict) else {}
                text = (chunk.get("text", "") if isinstance(chunk, dict) else str(chunk)).strip()
                # page is 0-indexed in pymupdf4llm metadata
                page_num = meta.get("page", meta.get("page_number", 0))
                page_1 = page_num + 1
                if text:
                    result.pages.append(
                        PageResult(page=page_1, content=text, backend="pymupdf4llm")
                    )
                    parts.append(f"<!-- Page {page_1} -->\n\n{text}")
            result.markdown = "\n\n".join(parts)
        else:
            # Older pymupdf4llm returned a single string
            md_text: str = raw or ""
            result.markdown = md_text
            result.pages = _split_pages(md_text)

        result.confidence = 0.90 if result.markdown.strip() else 0.0
        result.metadata = {"backend": "pymupdf4llm", "page_chunks": isinstance(raw, list)}

    except Exception as exc:
        result.warnings.append(f"markdown_llm extraction error: {exc}")
        result.confidence = 0.0

    return result


def _split_pages(md: str) -> list[PageResult]:
    """Split markdown into per-page results by <!-- Page N --> markers."""
    import re
    parts = re.split(r"<!-- Page (\d+) -->", md)
    pages: list[PageResult] = []
    i = 1
    while i < len(parts) - 1:
        try:
            page_num = int(parts[i])
            content = parts[i + 1].strip()
            pages.append(PageResult(page=page_num, content=content, backend="pymupdf4llm"))
        except (ValueError, IndexError):
            pass
        i += 2
    if not pages and md.strip():
        pages.append(PageResult(page=1, content=md, backend="pymupdf4llm"))
    return pages
