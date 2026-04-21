"""
features/pdf_structure.py — Extract document structure metadata from PDFs.

Strategy: layout:structure

Extracts the document skeleton that text-extraction backends miss:
  - Table of Contents / Outline (bookmarks hierarchy)
  - Page labels (Roman numerals, custom schemes)
  - Named destinations
  - Annotations (comments, highlights, notes, links)
  - Form fields (interactive AcroForms)
  - Document metadata (author, title, subject, keywords, dates)
  - Embedded file attachments

Output: Emits a structured Markdown section with all metadata, placed on
virtual page 0 (before page 1) so it appears at the top of the document.
This gives LLMs the document skeleton without polluting the page text.

Depends on PyMuPDF (always available as base dep).
"""

from __future__ import annotations

from ._base import FeatureResult, PageResult
from ._protocol import StrategyMeta


STRATEGY = StrategyMeta(
    name="layout:structure",
    tier="layout",
    description="Extract PDF structure: bookmarks, annotations, forms, links (PyMuPDF)",
    module="pdf_extractor.features.pdf_structure",
    requires_python=["fitz"],
    priority=5,
)


def extract(pdf_path: str, page_range: tuple[int, int] | None = None) -> FeatureResult:
    result = FeatureResult(feature="pdf_structure")

    try:
        try:
            import pymupdf as fitz
        except ImportError:
            import fitz  # type: ignore
    except ImportError:
        result.warnings.append("PyMuPDF not installed; pdf_structure skipped")
        return result

    try:
        doc = fitz.open(pdf_path)
    except Exception as exc:
        result.warnings.append(f"Cannot open PDF: {exc}")
        return result

    sections: list[str] = []

    try:
        # ── Document metadata ────────────────────────────────────────────
        meta = doc.metadata or {}
        meta_lines: list[str] = []
        field_map = {
            "title": "Título",
            "author": "Autor",
            "subject": "Tema",
            "keywords": "Palabras clave",
            "creator": "Creador",
            "producer": "Productor",
            "creationDate": "Fecha de creación",
            "modDate": "Última modificación",
        }
        for key, label in field_map.items():
            val = meta.get(key, "").strip()
            if val:
                meta_lines.append(f"- **{label}:** {val}")
        if meta_lines:
            sections.append("### Metadatos del documento\n\n" + "\n".join(meta_lines))

        # ── Table of Contents / Bookmarks ────────────────────────────────
        toc = doc.get_toc(simple=False)
        if toc:
            toc_lines: list[str] = []
            for level, title, page, *_ in toc:
                indent = "  " * (level - 1)
                toc_lines.append(f"{indent}- {title} *(p. {page})*")
            if toc_lines:
                sections.append("### Tabla de contenido (marcadores)\n\n" + "\n".join(toc_lines))

        # ── Page labels ──────────────────────────────────────────────────
        try:
            labels = {i + 1: doc[i].get_label() for i in range(len(doc))
                      if doc[i].get_label()}
            if labels:
                sample = list(labels.items())[:10]
                lbl_lines = [f"- Página {k}: `{v}`" for k, v in sample]
                if len(labels) > 10:
                    lbl_lines.append(f"- … ({len(labels) - 10} páginas más)")
                sections.append("### Etiquetas de página\n\n" + "\n".join(lbl_lines))
        except Exception:
            pass

        # ── Annotations ──────────────────────────────────────────────────
        annot_lines: list[str] = []
        for page in doc:
            page_num = page.number + 1
            if page_range:
                if page_num < page_range[0] or page_num > page_range[1]:
                    continue
            for annot in page.annots():
                atype = annot.type[1]
                info = annot.info
                content = info.get("content", "").strip()
                subject = info.get("subject", "").strip()
                author = info.get("title", "").strip()
                parts = [f"[p.{page_num}] **{atype}**"]
                if subject:
                    parts.append(f"— {subject}")
                if content:
                    parts.append(f": "{content[:120]}{"…" if len(content) > 120 else ""}"")
                if author:
                    parts.append(f"*(autor: {author})*")
                annot_lines.append("- " + " ".join(parts))
        if annot_lines:
            sections.append("### Anotaciones\n\n" + "\n".join(annot_lines[:50]))
            if len(annot_lines) > 50:
                sections[-1] += f"\n- … ({len(annot_lines) - 50} anotaciones más)"

        # ── Form fields (AcroForm) ───────────────────────────────────────
        form_lines: list[str] = []
        for page in doc:
            for widget in page.widgets() or []:
                field_name = widget.field_name or "(sin nombre)"
                field_type = widget.field_type_string
                field_value = str(widget.field_value or "").strip()
                form_lines.append(
                    f"- `{field_name}` [{field_type}]"
                    + (f" = `{field_value}`" if field_value else "")
                )
        if form_lines:
            sections.append("### Campos de formulario (AcroForm)\n\n" + "\n".join(form_lines))

        # ── Embedded attachments ─────────────────────────────────────────
        attach_lines: list[str] = []
        for i in range(doc.embfile_count()):
            try:
                info = doc.embfile_info(i)
                attach_lines.append(
                    f"- `{info.get('filename', 'archivo')}` "
                    f"({info.get('size', 0):,} bytes)"
                )
            except Exception:
                pass
        if attach_lines:
            sections.append("### Archivos adjuntos embebidos\n\n" + "\n".join(attach_lines))

    finally:
        doc.close()

    if not sections:
        return result

    structure_md = "## Estructura del documento\n\n" + "\n\n".join(sections)

    # Emit on virtual page 0 (before page 1) via page=1 with high priority override
    result.pages.append(PageResult(
        page=1,
        content=structure_md,
        content_type="text",
        backend="pymupdf-structure",
        confidence=0.60,   # Lower — won't override better text extraction
    ))
    result.markdown = structure_md
    result.confidence = 0.60
    result.metadata = {
        "has_toc": bool(doc.get_toc() if not doc.is_closed else []),
        "annotation_count": len(annot_lines) if 'annot_lines' in dir() else 0,
        "form_field_count": len(form_lines) if 'form_lines' in dir() else 0,
    }
    return result
