#!/usr/bin/env python3
"""Auxiliary table extraction backends for pdf-markdown-codex."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple


@dataclass
class TableResult:
    page: int | None
    index: int
    backend: str
    rows: int
    cols: int
    markdown: str


def _clean_cell(cell) -> str:
    if cell is None:
        return ""
    return " ".join(str(cell).replace("\r", "\n").split())


def _normalize_matrix(matrix: Iterable[Iterable[object]]) -> List[List[str]]:
    rows = [[_clean_cell(cell) for cell in row] for row in matrix if row]
    rows = [row for row in rows if any(cell for cell in row)]
    if not rows:
        return []

    width = max(len(row) for row in rows)
    return [row + [""] * (width - len(row)) for row in rows]


def _render_markdown(matrix: List[List[str]]) -> str:
    if not matrix:
        return ""

    header = matrix[0]
    body = matrix[1:] or [[""] * len(header)]
    separator = ["---"] * len(header)

    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(separator) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in body)
    return "\n".join(lines)


def _score(results: List[TableResult]) -> Tuple[int, int]:
    total_cells = sum(result.rows * result.cols for result in results)
    return (len(results), total_cells)


def extract_pdfplumber(pdf_path: str, max_tables: int = 25) -> tuple[List[TableResult], List[str]]:
    warnings: List[str] = []
    try:
        import pdfplumber
    except ImportError:
        return [], ["pdfplumber no esta instalado"]

    results: List[TableResult] = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                for index, table in enumerate(page.extract_tables(), start=1):
                    matrix = _normalize_matrix(table)
                    if not matrix:
                        continue
                    results.append(
                        TableResult(
                            page=page_number,
                            index=index,
                            backend="pdfplumber",
                            rows=len(matrix),
                            cols=len(matrix[0]),
                            markdown=_render_markdown(matrix),
                        )
                    )
                    if len(results) >= max_tables:
                        warnings.append(f"pdfplumber truncado a {max_tables} tablas")
                        return results, warnings
    except Exception as exc:
        warnings.append(f"pdfplumber fallo: {exc}")

    return results, warnings


def _extract_camelot_flavor(pdf_path: str, flavor: str, max_tables: int) -> tuple[List[TableResult], List[str]]:
    warnings: List[str] = []
    try:
        import camelot
    except ImportError:
        return [], ["camelot no esta instalado"]

    results: List[TableResult] = []
    try:
        tables = camelot.read_pdf(pdf_path, pages="all", flavor=flavor)
        for index, table in enumerate(tables, start=1):
            matrix = _normalize_matrix(table.df.values.tolist())
            if not matrix:
                continue
            results.append(
                TableResult(
                    page=getattr(table, "page", None),
                    index=index,
                    backend=f"camelot:{flavor}",
                    rows=len(matrix),
                    cols=len(matrix[0]),
                    markdown=_render_markdown(matrix),
                )
            )
            if len(results) >= max_tables:
                warnings.append(f"camelot {flavor} truncado a {max_tables} tablas")
                return results, warnings
    except Exception as exc:
        warnings.append(f"camelot {flavor} fallo: {exc}")

    return results, warnings


def extract_camelot(pdf_path: str, max_tables: int = 25) -> tuple[List[TableResult], List[str]]:
    lattice_results, lattice_warnings = _extract_camelot_flavor(pdf_path, "lattice", max_tables)
    stream_results, stream_warnings = _extract_camelot_flavor(pdf_path, "stream", max_tables)

    if _score(stream_results) > _score(lattice_results):
        return stream_results, lattice_warnings + stream_warnings
    return lattice_results, lattice_warnings + stream_warnings


def extract_tabula(pdf_path: str, max_tables: int = 25) -> tuple[List[TableResult], List[str]]:
    warnings: List[str] = []
    try:
        import tabula  # type: ignore
    except ImportError:
        return [], ["tabula-py no esta instalado (requiere Java en el PATH)"]

    results: List[TableResult] = []
    try:
        dfs = tabula.read_pdf(
            pdf_path,
            pages="all",
            multiple_tables=True,
            silent=True,
            pandas_options={"dtype": str},
        )
        for index, df in enumerate(dfs, start=1):
            if df is None or df.empty:
                continue
            # Use column names as first row for clean header
            header = [str(c) for c in df.columns]
            body = df.fillna("").values.tolist()
            matrix = _normalize_matrix([header] + body)
            if not matrix:
                continue
            results.append(
                TableResult(
                    page=None,
                    index=index,
                    backend="tabula",
                    rows=len(matrix),
                    cols=len(matrix[0]),
                    markdown=_render_markdown(matrix),
                )
            )
            if len(results) >= max_tables:
                warnings.append(f"tabula truncado a {max_tables} tablas")
                return results, warnings
    except Exception as exc:
        warnings.append(f"tabula fallo: {exc}")

    return results, warnings


def extract_tables(pdf_path: str, backend: str = "auto", max_tables: int = 25) -> tuple[List[TableResult], List[str], str | None]:
    if backend == "none":
        return [], [], None

    if backend == "pdfplumber":
        results, warnings = extract_pdfplumber(pdf_path, max_tables=max_tables)
        return results, warnings, "pdfplumber" if results else None

    if backend == "camelot":
        results, warnings = extract_camelot(pdf_path, max_tables=max_tables)
        chosen = results[0].backend if results else None
        return results, warnings, chosen

    if backend == "tabula":
        results, warnings = extract_tabula(pdf_path, max_tables=max_tables)
        return results, warnings, "tabula" if results else None

    # auto: try all backends, pick the one with the best coverage
    candidates = []
    warnings: List[str] = []

    for name, extractor in (
        ("pdfplumber", extract_pdfplumber),
        ("tabula", extract_tabula),
        ("camelot", extract_camelot),
    ):
        results, result_warnings = extractor(pdf_path, max_tables=max_tables)
        warnings.extend(result_warnings)
        if results:
            candidates.append((name, results))

    if not candidates:
        return [], warnings, None

    chosen_name, chosen_results = max(candidates, key=lambda item: _score(item[1]))
    chosen_backend = chosen_results[0].backend if chosen_results else chosen_name
    return chosen_results, warnings, chosen_backend


def render_table_appendix(results: List[TableResult], chosen_backend: str | None, warnings: List[str]) -> str:
    if not results and not warnings:
        return ""

    lines = ["", "---", "", "## Auxiliary Table Extraction", ""]

    if chosen_backend:
        lines.append(f"- Backend: `{chosen_backend}`")
    if results:
        lines.append(f"- Tables extracted: {len(results)}")
    if warnings:
        lines.append(f"- Warnings: {'; '.join(warnings)}")

    for result in results:
        lines.extend(
            [
                "",
                f"### Table {result.index}" + (f" (page {result.page})" if result.page else ""),
                "",
                f"- Backend: `{result.backend}`",
                f"- Shape: {result.rows} x {result.cols}",
                "",
                result.markdown,
            ]
        )

    return "\n".join(lines) + "\n"
