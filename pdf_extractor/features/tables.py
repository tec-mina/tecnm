"""
features/tables.py — pdfplumber table extraction → GFM Markdown.

Primary table backend. Falls back to camelot then tabula on failure.
Tables are emitted under: ### Tabla — página X (vía pdfplumber)

Rules:
  - Never split a logical row across lines
  - Merge multi-line cells with <br>
  - Every row must have same column count as header
  - Validate GFM pipe table format
"""

from __future__ import annotations

from ._protocol import StrategyMeta

STRATEGY = StrategyMeta(
    name="tables:pdfplumber",
    tier="tables",
    description="pdfplumber table extraction → GFM Markdown (best pure-Python option)",
    module="pdf_extractor.features.tables",
    requires_python=["pdfplumber"],
    priority=10,
)

try:
    import pdfplumber
except ImportError:
    pdfplumber = None  # type: ignore

try:
    from tabulate import tabulate as _tabulate
except ImportError:
    _tabulate = None  # type: ignore

from ._base import FeatureResult, PageResult


def extract(pdf_path: str, page_range: tuple[int, int] | None = None) -> FeatureResult:
    result = FeatureResult(feature="tables")

    if pdfplumber is None:
        result.warnings.append("pdfplumber not installed; tables skipped")
        return result

    tables_found = 0
    md_parts: list[str] = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            total = len(pdf.pages)
            start, end = _resolve_range(page_range, total)

            for idx in range(start, end):
                page = pdf.pages[idx]
                page_1indexed = idx + 1
                tables = page.extract_tables()

                if not tables:
                    continue

                for table in tables:
                    table_md = _render_table(table, page_1indexed)
                    if table_md:
                        md_parts.append(table_md)
                        tables_found += 1
                        result.pages.append(PageResult(
                            page=page_1indexed,
                            content=table_md,
                            content_type="table",
                            backend="pdfplumber",
                        ))

        result.markdown = "\n\n".join(md_parts)
        result.confidence = 0.88 if tables_found > 0 else 0.0
        result.metadata = {
            "tables_found": tables_found,
            "backend": "pdfplumber",
        }

    except Exception as exc:
        result.warnings.append(f"tables (pdfplumber) error: {exc}")
        result.confidence = 0.0

    return result


def _render_table(rows: list[list], page_num: int) -> str:
    """Render a table as GFM Markdown with heading."""
    if not rows:
        return ""

    # Normalize cells: replace None with "", flatten multi-line
    cleaned = []
    for row in rows:
        cleaned_row = []
        for cell in (row or []):
            if cell is None:
                cell = ""
            cell = str(cell).replace("\n", "<br>").strip()
            cleaned_row.append(cell)
        if any(c.strip() for c in cleaned_row):
            cleaned.append(cleaned_row)

    if not cleaned:
        return ""

    # Ensure uniform column count
    max_cols = max(len(r) for r in cleaned)
    normalized = [r + [""] * (max_cols - len(r)) for r in cleaned]

    header = normalized[0]
    body = normalized[1:]

    # Build GFM table
    sep = ["-" * max(len(h), 1) for h in header]

    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(sep) + " |",
    ]
    for row in body:
        lines.append("| " + " | ".join(row) + " |")

    table_md = "\n".join(lines)
    return f"### Tabla — página {page_num} (vía pdfplumber)\n\n{table_md}"


def _resolve_range(page_range, total):
    if page_range is None:
        return 0, total
    return max(0, page_range[0] - 1), min(total, page_range[1])
