"""
PDF extraction with multiple backends:
- Fast mode: PyMuPDF with multi-strategy table detection (good for simple tables)
- Accurate mode: IBM Docling with TableFormer AI (better for complex/borderless tables)
"""

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

# Suppress PyMuPDF's "Consider using pymupdf_layout" recommendation
# This prints to stdout and pollutes --stdout output
os.environ.setdefault("PYMUPDF_SUGGEST_LAYOUT_ANALYZER", "0")

# Pages above this threshold use chunked tqdm extraction instead of all-at-once
_LARGE_PDF_PAGES = 40
_CHUNK_SIZE = 30  # pages per chunk for large PDF progress


@dataclass
class PdfInfo:
    """Result of pre-flight PDF validation."""

    path: str
    is_valid: bool = False
    is_encrypted: bool = False
    is_scanned: bool = False          # True = no selectable text layer
    page_count: int = 0
    file_size_mb: float = 0.0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.is_valid and not self.is_encrypted and not self.errors


def validate_pdf(path: str) -> PdfInfo:
    """
    Comprehensive pre-flight check before extraction.

    Checks:
    - File exists and is readable
    - File has PDF magic bytes (%PDF-)
    - File is not encrypted / password-protected
    - File has at least one page
    - Whether the document is scanned (no text layer)

    Returns a PdfInfo dataclass; call .ok to know if extraction can proceed.
    """
    p = Path(path)
    info = PdfInfo(path=str(p))

    # --- Existence / readability ---
    if not p.exists():
        info.errors.append(f"Archivo no encontrado: {p}")
        return info

    if not p.is_file():
        info.errors.append(f"La ruta no es un archivo: {p}")
        return info

    try:
        info.file_size_mb = round(p.stat().st_size / (1024 * 1024), 2)
    except OSError as exc:
        info.errors.append(f"No se pudo leer el archivo: {exc}")
        return info

    # --- Magic bytes: must start with %PDF- ---
    try:
        with open(p, "rb") as f:
            header = f.read(8)
        if not header.startswith(b"%PDF-"):
            info.errors.append(
                f"El archivo no es un PDF valido (magic bytes incorrectos). "
                f"Extension o contenido no reconocido: {p.suffix!r}"
            )
            return info
    except OSError as exc:
        info.errors.append(f"No se pudo leer el encabezado del archivo: {exc}")
        return info

    # --- Open with pymupdf for deeper checks ---
    try:
        import pymupdf
    except ImportError:
        info.errors.append("pymupdf no instalado; ejecuta: python scripts/bootstrap_env.py")
        return info

    try:
        doc = pymupdf.open(str(p))
    except Exception as exc:
        info.errors.append(f"PDF corrupto o ilegible: {exc}")
        return info

    try:
        # Encrypted check
        if doc.is_encrypted:
            info.is_encrypted = True
            info.errors.append(
                "El PDF esta protegido con contrasena. "
                "Desencriptalo primero con: qpdf --decrypt input.pdf output.pdf"
            )
            doc.close()
            return info

        info.page_count = len(doc)
        info.is_valid = True

        if info.page_count == 0:
            info.errors.append("El PDF no tiene paginas.")
            doc.close()
            return info

        # Scanned detection: sample first few pages for extractable text
        sample_pages = min(5, info.page_count)
        total_chars = 0
        for i in range(sample_pages):
            total_chars += len(doc[i].get_text("text").strip())

        chars_per_page = total_chars / sample_pages
        if chars_per_page < 30:
            info.is_scanned = True
            info.warnings.append(
                f"PDF probablemente escaneado (promedio {chars_per_page:.0f} chars/pagina). "
                "La extraccion puede ser deficiente. Usa --extras ocr si instalaste el grupo OCR."
            )

        # Large PDF warning
        if info.page_count > 200:
            info.warnings.append(
                f"PDF grande ({info.page_count} paginas, {info.file_size_mb} MB). "
                "La extraccion se hara por bloques con progreso visible."
            )

    finally:
        doc.close()

    return info

# Version for cache invalidation - increment when extraction logic changes
# Format: major.minor.patch
# 3.1.0: Page separators now use <!-- PAGE_BREAK --> instead of -----
#        Image extraction includes nested XObjects (full=True)
# 3.2.0: Fast mode now includes image references in markdown (write_images=True)
#        Cache keys now include no_images flag to avoid contamination
# 3.3.0: Image paths in cached markdown now use relative 'images/' prefix
#        (fixes broken temp directory references in cached output)
EXTRACTOR_VERSION = "3.4.0"


def check_docling_models():
    """Check if Docling models are downloaded."""
    try:
        from huggingface_hub import scan_cache_dir

        cache_info = scan_cache_dir()
        # Check for docling models in HF cache
        docling_repos = [r for r in cache_info.repos if "docling" in r.repo_id.lower()]
        return len(docling_repos) > 0
    except Exception:
        return False


def extract_pdf_fast(
    pdf_path: str, image_dir: str = None, show_progress: bool = False
) -> str:
    """
    Fast PDF extraction using PyMuPDF with text-based table detection.

    Uses 'text' table strategy which handles borderless/whitespace-based
    tables better than the default 'lines_strict' for mixed document types.

    For large PDFs (> _LARGE_PDF_PAGES pages) the extraction runs in chunks
    with a tqdm progress bar so the user can see real progress instead of a
    frozen terminal.

    Args:
        pdf_path: Path to the PDF file
        image_dir: Directory to save extracted images (None = skip images)
        show_progress: Whether to show progress output

    Returns:
        Markdown string of the PDF content with image references if image_dir provided
    """
    import pymupdf
    import pymupdf4llm

    doc = pymupdf.open(pdf_path)
    total_pages = len(doc)
    doc.close()

    if show_progress:
        print(f"[PDF] {total_pages} paginas detectadas.", file=sys.stderr)

    use_chunks = show_progress and total_pages > _LARGE_PDF_PAGES

    if not use_chunks:
        # Small/medium PDF: single pass with fallback to chunked on failure.
        # Falling back ensures ALL pages are represented in the output even
        # when one corrupted page would abort a full-document extraction.
        if show_progress:
            print("Extrayendo con PyMuPDF (modo rapido)...", file=sys.stderr)
        try:
            markdown = pymupdf4llm.to_markdown(
                pdf_path,
                show_progress=False,
                table_strategy="text",
                write_images=image_dir is not None,
                image_path=image_dir,
            )
            markdown = markdown.replace("\n-----\n", "\n<!-- PAGE_BREAK -->\n")
            return markdown
        except Exception as exc:
            print(
                f"WARNING: Extraccion completa fallo ({exc}); reintentando pagina por pagina...",
                file=sys.stderr,
            )
            use_chunks = True  # fall through to chunk loop below

    # Large PDF: chunk-by-chunk with tqdm
    # Images are NOT extracted per-chunk to avoid filename collisions;
    # the caller handles image extraction via extract_images() separately.
    try:
        from tqdm import tqdm
    except ImportError:
        print(
            "Nota: instala tqdm para barra de progreso: pip install tqdm",
            file=sys.stderr,
        )
        print("Extrayendo con PyMuPDF (modo rapido, PDF grande)...", file=sys.stderr)
        markdown = pymupdf4llm.to_markdown(
            pdf_path,
            show_progress=False,
            table_strategy="text",
            write_images=False,
        )
        return markdown.replace("\n-----\n", "\n<!-- PAGE_BREAK -->\n")

    page_indices = list(range(total_pages))
    chunks: list[str] = []

    with tqdm(
        total=total_pages,
        desc="Extrayendo paginas",
        unit="pag",
        file=sys.stderr,
        dynamic_ncols=True,
    ) as pbar:
        for start in range(0, total_pages, _CHUNK_SIZE):
            chunk_pages = page_indices[start : start + _CHUNK_SIZE]
            try:
                chunk_md = pymupdf4llm.to_markdown(
                    pdf_path,
                    pages=chunk_pages,
                    show_progress=False,
                    table_strategy="text",
                    write_images=False,  # images handled separately
                )
                chunk_md = chunk_md.replace("\n-----\n", "\n<!-- PAGE_BREAK -->\n")
                chunks.append(chunk_md)
            except Exception as exc:
                print(
                    f"\nWARNING: Error en paginas {start+1}-{start+len(chunk_pages)}: {exc}",
                    file=sys.stderr,
                )
                chunks.append(
                    f"\n<!-- EXTRACTION_ERROR pages {start+1}-{start+len(chunk_pages)}: {exc} -->\n"
                )
            pbar.update(len(chunk_pages))

    # If image_dir requested and large PDF, extract images separately
    if image_dir:
        from extractor import extract_images
        extract_images(pdf_path, image_dir, show_progress=False)

    return "\n<!-- PAGE_BREAK -->\n".join(chunks)


def _save_docling_images(result, output_dir: Path) -> list:
    """
    Save images from a Docling conversion result to output directory.

    Images are saved in iteration order, which matches the order of
    <!-- image --> placeholders in the exported markdown.

    Args:
        result: Docling ConversionResult object
        output_dir: Directory to save images to

    Returns:
        List of saved image paths (in iteration order)
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    image_paths = []

    for i, (element, _level) in enumerate(result.document.iterate_items()):
        if hasattr(element, "image") and element.image is not None:
            img_path = output_dir / f"figure_{i:04d}.png"
            element.image.pil_image.save(str(img_path))
            image_paths.append(str(img_path))

    return image_paths


def extract_pdf_docling(
    pdf_path: str,
    output_dir: str = None,
    images_scale: float = 4.0,
    show_progress: bool = False,
) -> tuple:
    """
    Extract PDF using Docling with accurate tables + high-res images.

    Uses IBM's TableFormer AI model for ~93.6% table extraction accuracy.
    Also extracts images at configurable resolution (default 4x for crisp images).

    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save extracted images (None = skip images)
        images_scale: Image resolution multiplier (default: 4.0 for high-res)
        show_progress: Whether to show progress output

    Returns:
        tuple: (markdown: str, image_paths: list[str])
    """
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
    from docling_core.types.doc.base import ImageRefMode

    # Check if this is first run (models need downloading)
    if not check_docling_models():
        print(
            "First run: downloading Docling AI models (one-time setup, ~2-3 minutes)...",
            file=sys.stderr,
        )

    if show_progress:
        print(
            f"Processing PDF with Docling (accurate mode, ~1 sec/page)...",
            file=sys.stderr,
        )

    # Configure pipeline for accurate tables + image extraction
    pipeline_options = PdfPipelineOptions(
        do_table_structure=True,
        generate_picture_images=output_dir is not None,
        images_scale=images_scale,
    )
    pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    # Convert the document
    result = converter.convert(pdf_path)

    # Check for conversion errors
    if hasattr(result, "errors") and result.errors:
        for error in result.errors:
            print(f"WARNING: Docling conversion error: {error}", file=sys.stderr)

    # Check conversion status
    from docling.datamodel.base_models import ConversionStatus

    if hasattr(result, "status") and result.status != ConversionStatus.SUCCESS:
        print(
            f"WARNING: Docling conversion status: {result.status.name}",
            file=sys.stderr,
        )

    # Save images to output directory (order matters for placeholder replacement)
    image_paths = []
    if output_dir:
        image_paths = _save_docling_images(result, Path(output_dir))
        if show_progress and image_paths:
            print(
                f"Extracted {len(image_paths)} images at {images_scale}x resolution",
                file=sys.stderr,
            )

    # Export markdown with placeholders
    md = result.document.export_to_markdown(image_mode=ImageRefMode.PLACEHOLDER)

    # Replace placeholders with actual image references (order must match iteration order)
    for img_path in image_paths:
        md = md.replace("<!-- image -->", f"![Figure](images/{Path(img_path).name})", 1)

    return md, image_paths


def extract_pdf_markitdown(pdf_path: str, show_progress: bool = False) -> str:
    """
    Extract PDF to Markdown using Microsoft MarkItDown.

    MarkItDown uses pdfminer under the hood and produces clean heading/table
    Markdown. It is lighter than Docling (no AI models required) and a good
    intermediate option when PyMuPDF tables look bad but Docling is too heavy.

    Install: python scripts/bootstrap_env.py --extras markitdown

    Returns:
        Markdown string, or raises ImportError / RuntimeError on failure.
    """
    try:
        from markitdown import MarkItDown  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "markitdown no instalado. Ejecuta: python scripts/bootstrap_env.py --extras markitdown"
        ) from exc

    if show_progress:
        print("Extrayendo con MarkItDown (Microsoft)...", file=sys.stderr)

    md_converter = MarkItDown()
    result = md_converter.convert(pdf_path)
    text = result.text_content or ""
    if not text.strip():
        raise RuntimeError(
            "MarkItDown produjo salida vacia. El PDF puede estar escaneado o protegido."
        )
    return text


def extract_pdf_easyocr(
    pdf_path: str,
    lang: list[str] | None = None,
    show_progress: bool = False,
) -> str:
    """
    OCR-based extraction for scanned PDFs using EasyOCR + pdf2image.

    Renders each page as an image and runs EasyOCR on it. Slower than text
    extraction, but the only reliable route when there is no text layer.

    Install: python scripts/bootstrap_env.py --extras ocr
            (includes easyocr, pdf2image, poppler required as system dep)

    Args:
        pdf_path: Path to the scanned PDF.
        lang: EasyOCR language codes (default: ['es', 'en']).
        show_progress: Show tqdm progress bar.

    Returns:
        Markdown string (each page separated by <!-- PAGE_BREAK -->).
    """
    if lang is None:
        lang = ["es", "en"]

    try:
        import easyocr  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "easyocr no instalado. Ejecuta: python scripts/bootstrap_env.py --extras ocr"
        ) from exc

    try:
        from pdf2image import convert_from_path  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "pdf2image no instalado. Ejecuta: python scripts/bootstrap_env.py --extras ocr\n"
            "Tambien necesitas poppler: brew install poppler  (macOS) o apt install poppler-utils"
        ) from exc

    if show_progress:
        print(f"OCR con EasyOCR (idiomas: {lang})...", file=sys.stderr)

    reader = easyocr.Reader(lang, verbose=False)
    pages_img = convert_from_path(pdf_path)

    import numpy as np

    pages_md: list[str] = []

    iter_pages = pages_img
    if show_progress:
        try:
            from tqdm import tqdm
            iter_pages = tqdm(pages_img, desc="OCR paginas", unit="pag", file=sys.stderr, dynamic_ncols=True)
        except ImportError:
            pass

    for page_img in iter_pages:
        img_array = np.array(page_img)
        results = reader.readtext(img_array, detail=0, paragraph=True)
        pages_md.append("\n\n".join(results))

    return "\n\n<!-- PAGE_BREAK -->\n\n".join(pages_md)


def extract_pdf_to_markdown(
    pdf_path: str, accurate: bool = False, show_progress: bool = False
) -> str:
    """
    Extract PDF to markdown with configurable accuracy/speed trade-off.

    Args:
        pdf_path: Path to the PDF file
        accurate: If True, use Docling AI (better for complex tables, slower).
                  If False, use PyMuPDF (fast, good for simple tables).
        show_progress: Whether to show progress output

    Returns:
        Markdown string of the PDF content
    """
    if accurate:
        # Use Docling without image extraction
        md, _ = extract_pdf_docling(
            pdf_path, output_dir=None, show_progress=show_progress
        )
        return md
    else:
        return extract_pdf_fast(pdf_path, show_progress)


def get_page_count(pdf_path: str) -> int:
    """Get the number of pages in a PDF using pymupdf (faster than Docling for this)."""
    import pymupdf

    doc = pymupdf.open(pdf_path)
    count = len(doc)
    doc.close()
    return count


def extract_images(pdf_path: str, output_dir: str, show_progress: bool = False) -> list:
    """
    Extract images from PDF to output directory.

    Uses pymupdf for image extraction since Docling focuses on document structure.
    Deduplicates by xref to avoid extracting the same image multiple times
    (e.g., icons/logos reused across pages).

    Returns:
        List of extracted image paths
    """
    import pymupdf

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    doc = pymupdf.open(pdf_path)
    extracted = []
    image_count = 0
    seen_xrefs = set()  # Track already-extracted images by xref

    for page_num in range(len(doc)):
        page = doc[page_num]
        # full=True includes images nested inside form XObjects (common in
        # documents exported from Word/PowerPoint)
        images = page.get_images(full=True)

        for img_index, img in enumerate(images):
            try:
                xref = img[0]

                # Skip if we've already extracted this image
                if xref in seen_xrefs:
                    continue
                seen_xrefs.add(xref)

                pix = pymupdf.Pixmap(doc, xref)

                # Convert CMYK to RGB if necessary
                if pix.n - pix.alpha > 3:
                    pix = pymupdf.Pixmap(pymupdf.csRGB, pix)

                image_count += 1
                img_filename = f"image_{image_count:04d}.png"
                img_path = output_path / img_filename
                pix.save(str(img_path))
                extracted.append(str(img_path))

                pix = None
            except Exception as e:
                # Log instead of silently swallowing errors
                print(
                    f"WARNING: Failed to extract image {img_index} on page {page_num + 1}: {e}",
                    file=sys.stderr,
                )
                continue

    doc.close()

    if show_progress and extracted:
        print(f"Extracted {len(extracted)} unique images", file=sys.stderr)

    return extracted
