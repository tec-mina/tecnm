"""
features/tables_camelot.py — camelot-py lattice/stream table extraction.

Fallback when pdfplumber fails. Requires Ghostscript.
Tries lattice mode first, then stream mode.
"""

from __future__ import annotations

from ._protocol import StrategyMeta

STRATEGY = StrategyMeta(
    name="tables:camelot",
    tier="tables",
    description="camelot-py lattice/stream table extraction (requires Ghostscript)",
    module="pdf_extractor.features.tables_camelot",
    requires_python=["camelot"],
    requires_system=["ghostscript"],
    priority=20,
)

try:
    import camelot
except ImportError:
    camelot = None  # type: ignore

from ._base import FeatureResult, PageResult


def extract(pdf_path: str, page_range: tuple[int, int] | None = None) -> FeatureResult:
    result = FeatureResult(feature="tables_camelot")

    if camelot is None:
        result.warnings.append("camelot-py not installed; tables_camelot skipped")
        return result

    pages_spec = _range_to_camelot(page_range)
    tables_found = 0
    md_parts: list[str] = []

    for flavor in ("lattice", "stream"):
        try:
            tables = camelot.read_pdf(pdf_path, pages=pages_spec, flavor=flavor)
            for table in tables:
                page_1indexed = table.page
                df = table.df
                if df.empty:
                    continue
                table_md = _df_to_gfm(df, page_1indexed, flavor)
                if table_md:
                    md_parts.append(table_md)
                    tables_found += 1
                    result.pages.append(PageResult(
                        page=page_1indexed,
                        content=table_md,
                        content_type="table",
                        backend=f"camelot-{flavor}",
                    ))

            if tables_found > 0:
                break  # lattice succeeded; no need for stream

        except Exception as exc:
            result.warnings.append(f"camelot {flavor} error: {exc}")
            continue

    result.markdown = "\n\n".join(md_parts)
    result.confidence = 0.82 if tables_found > 0 else 0.0
    result.metadata = {"tables_found": tables_found, "backend": "camelot"}
    return result


def _range_to_camelot(page_range) -> str:
    if page_range is None:
        return "all"
    start, end = page_range
    return f"{start}-{end}"


def _df_to_gfm(df, page_num: int, flavor: str) -> str:
    rows = df.values.tolist()
    if not rows:
        return ""

    header = [str(c).replace("\n", "<br>").strip() for c in rows[0]]
    body = [[str(c).replace("\n", "<br>").strip() for c in row] for row in rows[1:]]

    max_cols = len(header)
    sep = ["-" * max(len(h), 1) for h in header]

    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(sep) + " |",
    ]
    for row in body:
        row = row + [""] * (max_cols - len(row))
        lines.append("| " + " | ".join(row[:max_cols]) + " |")

    table_md = "\n".join(lines)
    return f"### Tabla — página {page_num} (vía camelot-{flavor})\n\n{table_md}"
