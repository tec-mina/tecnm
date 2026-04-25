"""
features/ocr_img2table.py — img2table + rapidocr for scanned table extraction.

Specialized for detecting and extracting tables from raster/scanned pages.
Requires img2table and rapidocr-onnxruntime.
"""

from __future__ import annotations

import os
import tempfile

try:
    from img2table.document import PDF as Img2TablePDF
    from img2table.ocr import TesseractOCR, EasyOCR
except ImportError:
    Img2TablePDF = None  # type: ignore
    TesseractOCR = None  # type: ignore
    EasyOCR = None  # type: ignore

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
    name="tables:img2table",
    tier="tables",
    description="img2table + RapidOCR — table extraction from scanned/raster pages",
    module="pdf_extractor.features.ocr_img2table",
    requires_python=["img2table"],
    priority=25,
)


def extract(pdf_path: str, page_range: tuple[int, int] | None = None) -> FeatureResult:
    result = FeatureResult(feature="ocr_img2table", content_category="table")

    if Img2TablePDF is None:
        result.warnings.append("img2table not installed; ocr_img2table skipped")
        return result
    if fitz is None:
        result.warnings.append("pymupdf not installed; ocr_img2table skipped")
        return result

    # Select OCR engine: prefer tesseract, fallback to easyocr
    ocr_engine = _select_ocr()
    if ocr_engine is None:
        result.warnings.append("No OCR engine available for img2table; skipped")
        return result

    tables_found = 0
    md_parts: list[str] = []

    try:
        doc = Img2TablePDF(src=pdf_path, detect_rotation=False)
        extracted = doc.extract_tables(ocr=ocr_engine, implicit_rows=True)

        for page_idx, tables in extracted.items():
            page_1indexed = page_idx + 1
            for table in tables:
                df = table.df
                if df is None or df.empty:
                    continue
                table_md = _df_to_gfm(df, page_1indexed)
                if table_md:
                    md_parts.append(table_md)
                    tables_found += 1
                    result.pages.append(PageResult(
                        page=page_1indexed,
                        content=table_md,
                        content_type="table",
                        backend="img2table",
                    ))

    except Exception as exc:
        result.warnings.append(f"ocr_img2table error: {exc}")
        result.confidence = 0.0
        return result

    result.markdown = "\n\n".join(md_parts)
    result.confidence = 0.77 if tables_found > 0 else 0.0
    result.metadata = {"tables_found": tables_found, "backend": "img2table"}
    return result


def _select_ocr():
    """Return best available OCR engine for img2table."""
    import shutil
    if TesseractOCR is not None and shutil.which("tesseract"):
        try:
            return TesseractOCR(n_threads=4, lang="spa+eng")
        except Exception:
            pass
    if EasyOCR is not None:
        try:
            return EasyOCR(lang=["es", "en"])
        except Exception:
            pass
    return None


def _df_to_gfm(df, page_num: int) -> str:
    cols = [str(c).strip() for c in df.columns]
    rows = [[str(c).replace("\n", "<br>").strip() for c in row]
            for row in df.values.tolist()]
    if not cols:
        return ""
    max_cols = len(cols)
    sep = ["-" * max(len(h), 1) for h in cols]
    lines = [
        "| " + " | ".join(cols) + " |",
        "| " + " | ".join(sep) + " |",
    ]
    for row in rows:
        row = row + [""] * (max_cols - len(row))
        lines.append("| " + " | ".join(row[:max_cols]) + " |")
    return f"### Tabla — página {page_num} (vía img2table)\n\n" + "\n".join(lines)
