"""
features/images_extract.py — Extract embedded images from PDF pages.

Strategy: images:extract

Uses PyMuPDF to enumerate every embedded XObject image per page,
saves them to an ``images/`` subdirectory, and emits Markdown references.

Rules applied
-------------
- Images smaller than 50×50 px are skipped (decorative / bullets).
- File names follow the pattern: ``p{page:03d}_img{idx:02d}.{ext}``
- When no output_dir is provided the references are emitted as relative paths
  so they work after the caller writes the .md file.
"""

from __future__ import annotations

from pathlib import Path

from ._base import FeatureResult, PageResult
from ._protocol import StrategyMeta


STRATEGY = StrategyMeta(
    name="images:extract",
    tier="images",
    description="Extract embedded images from PDF (PyMuPDF) — saves to images/",
    module="pdf_extractor.features.images_extract",
    requires_python=["fitz"],
    priority=10,
)

_MIN_DIM = 50   # pixels — skip anything smaller (decorative)


def extract(
    pdf_path: str,
    page_range: tuple[int, int] | None = None,
    output_dir: str | None = None,
) -> FeatureResult:
    """Extract embedded images and return image PageResults.

    Parameters
    ----------
    output_dir : str | None
        Directory where to write image files.  Images are placed in a
        sub-folder ``images/`` inside this directory.  When None, image bytes
        are not saved and references use placeholder paths.
    """
    result = FeatureResult(feature="images_extract")

    try:
        try:
            import pymupdf as fitz
        except ImportError:
            import fitz  # type: ignore
    except ImportError:
        result.warnings.append("PyMuPDF not installed; images_extract skipped")
        return result

    out_dir: Path | None = None
    if output_dir:
        out_dir = Path(output_dir) / "images"
        out_dir.mkdir(parents=True, exist_ok=True)

    try:
        doc = fitz.open(pdf_path)
    except Exception as exc:
        result.warnings.append(f"Cannot open PDF: {exc}")
        return result

    total_pages = doc.page_count
    start = (page_range[0] - 1) if page_range else 0
    end = page_range[1] if page_range else total_pages
    total_saved = 0

    try:
        for page_idx in range(start, min(end, total_pages)):
            page = doc[page_idx]
            page_num = page_idx + 1
            img_refs: list[str] = []

            for img_idx, img_info in enumerate(page.get_images(full=True), 1):
                xref = img_info[0]
                try:
                    base_img = doc.extract_image(xref)
                except Exception:
                    continue

                width = base_img.get("width", 0)
                height = base_img.get("height", 0)
                if width < _MIN_DIM or height < _MIN_DIM:
                    continue

                ext = base_img.get("ext", "png")
                img_bytes = base_img["image"]
                filename = f"p{page_num:03d}_img{img_idx:02d}.{ext}"

                if out_dir:
                    (out_dir / filename).write_bytes(img_bytes)
                    ref_path = f"images/{filename}"
                else:
                    ref_path = f"images/{filename}"   # caller will write later

                alt = f"Figura {img_idx} — página {page_num} ({width}×{height}px)"
                img_refs.append(f"![{alt}]({ref_path})")
                total_saved += 1

            if img_refs:
                result.pages.append(PageResult(
                    page=page_num,
                    content="\n".join(img_refs),
                    content_type="image",
                    backend="pymupdf-images",
                    confidence=0.95,
                ))
    finally:
        doc.close()

    result.confidence = 0.95 if total_saved > 0 else 0.0
    result.metadata = {"total_images": total_saved}
    return result
