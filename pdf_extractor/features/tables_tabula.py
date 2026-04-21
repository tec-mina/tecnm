"""
features/tables_tabula.py — tabula-py (Java-based) table extraction fallback.

Used when both pdfplumber and camelot fail.
Requires Java JRE in PATH.
"""

from __future__ import annotations

from ._protocol import StrategyMeta

STRATEGY = StrategyMeta(
    name="tables:tabula",
    tier="tables",
    description="tabula-py Java-based table extraction (fallback, requires JRE)",
    module="pdf_extractor.features.tables_tabula",
    requires_python=["tabula"],
    requires_system=["java"],
    priority=30,
)

try:
    import tabula
except ImportError:
    tabula = None  # type: ignore

from ._base import FeatureResult, PageResult


def extract(pdf_path: str, page_range: tuple[int, int] | None = None) -> FeatureResult:
    result = FeatureResult(feature="tables_tabula")

    if tabula is None:
        result.warnings.append("tabula-py not installed; tables_tabula skipped")
        return result

    pages_spec = "all" if page_range is None else f"{page_range[0]}-{page_range[1]}"
    tables_found = 0
    md_parts: list[str] = []

    try:
        dfs = tabula.read_pdf(pdf_path, pages=pages_spec, multiple_tables=True,
                              silent=True)
        for df in dfs:
            if df is None or df.empty:
                continue
            table_md = _df_to_gfm(df)
            if table_md:
                md_parts.append(table_md)
                tables_found += 1
                result.pages.append(PageResult(
                    page=0,  # tabula doesn't always expose page number
                    content=table_md,
                    content_type="table",
                    backend="tabula",
                ))

    except Exception as exc:
        result.warnings.append(f"tabula error: {exc}")
        result.confidence = 0.0
        return result

    result.markdown = "\n\n".join(md_parts)
    result.confidence = 0.75 if tables_found > 0 else 0.0
    result.metadata = {"tables_found": tables_found, "backend": "tabula"}
    return result


def _df_to_gfm(df) -> str:
    rows = df.values.tolist()
    cols = [str(c).replace("\n", "<br>").strip() for c in df.columns]
    if not rows and not cols:
        return ""

    max_cols = len(cols)
    sep = ["-" * max(len(h), 1) for h in cols]
    lines = [
        "| " + " | ".join(cols) + " |",
        "| " + " | ".join(sep) + " |",
    ]
    for row in rows:
        cells = [str(c).replace("\n", "<br>").strip() for c in row]
        cells = cells + [""] * (max_cols - len(cells))
        lines.append("| " + " | ".join(cells[:max_cols]) + " |")

    return "### Tabla (vía tabula)\n\n" + "\n".join(lines)
