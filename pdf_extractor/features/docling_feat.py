"""
features/docling_feat.py — IBM Docling + TableFormer AI extraction.

~93% table accuracy. Best fidelity for complex layouts.
Requires docling library (heavy dependency, GPU optional).
"""

from __future__ import annotations

try:
    from docling.document_converter import DocumentConverter
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
except ImportError:
    DocumentConverter = None  # type: ignore
    InputFormat = None  # type: ignore
    PdfPipelineOptions = None  # type: ignore

from ._base import FeatureResult, PageResult


def extract(pdf_path: str, page_range: tuple[int, int] | None = None) -> FeatureResult:
    result = FeatureResult(feature="docling_feat")

    if DocumentConverter is None:
        result.warnings.append("docling not installed; docling_feat skipped")
        return result

    try:
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = False       # Only for scanned; text PDFs use native
        pipeline_options.do_table_structure = True

        converter = DocumentConverter()
        conv_result = converter.convert(pdf_path)
        doc = conv_result.document

        md_text = doc.export_to_markdown()
        result.markdown = md_text
        result.confidence = 0.93 if md_text.strip() else 0.0
        result.pages = _extract_pages(md_text)
        result.metadata = {"backend": "docling", "tableformer": True}

    except Exception as exc:
        result.warnings.append(f"docling_feat error: {exc}")
        result.confidence = 0.0

    return result


def _extract_pages(md: str) -> list[PageResult]:
    import re
    parts = re.split(r"<!-- Page (\d+) -->", md)
    pages: list[PageResult] = []
    i = 1
    while i < len(parts) - 1:
        try:
            page_num = int(parts[i])
            content = parts[i + 1].strip()
            pages.append(PageResult(page=page_num, content=content, backend="docling"))
        except (ValueError, IndexError):
            pass
        i += 2
    if not pages and md.strip():
        pages.append(PageResult(page=1, content=md, backend="docling"))
    return pages
