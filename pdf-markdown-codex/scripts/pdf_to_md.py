#!/usr/bin/env python3
"""
PDF to Markdown Converter for LLM Context

Extracts an entire PDF as structured markdown, keeps a persistent cache,
copies extracted images next to the output, and can append auxiliary table
extraction using optional table backends.
"""

import argparse
import sys
import os
import re
import json
import hashlib
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime


# =============================================================================
# DATACLASSES
# =============================================================================


@dataclass
class ExtractionConfig:
    """Configuration for PDF extraction."""

    pdf_path: str
    docling: bool = False
    images_scale: float = 4.0


@dataclass
class ExtractionResult:
    """Result of PDF extraction or cache load."""

    markdown: str
    image_dir: Path | None
    total_pages: int
    from_cache: bool = False


# Suppress PyMuPDF's "Consider using pymupdf_layout" recommendation
os.environ.setdefault("PYMUPDF_SUGGEST_LAYOUT_ANALYZER", "0")

# Default cache directory
DEFAULT_CACHE_DIR = Path.home() / ".cache" / "pdf-to-markdown"


# =============================================================================
# CACHE MANAGER
# =============================================================================


class CacheManager:
    """Manages PDF extraction cache."""

    def __init__(self, cache_dir: Path = None):
        self.cache_dir = cache_dir or DEFAULT_CACHE_DIR

    def get_key(self, config: ExtractionConfig) -> str:
        """Generate cache key from file content + size + mode."""
        p = Path(config.pdf_path).resolve()
        stat = p.stat()
        file_size = stat.st_size

        chunk_size = 65536  # 64KB
        hasher = hashlib.sha256()

        with open(p, "rb") as f:
            if file_size <= chunk_size * 2:
                hasher.update(f.read())
            else:
                hasher.update(f.read(chunk_size))
                f.seek(-chunk_size, 2)
                hasher.update(f.read(chunk_size))

        mode = f"docling_{config.images_scale}" if config.docling else "fast"
        raw = f"{file_size}|{hasher.hexdigest()}|{mode}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def _get_dir(self, cache_key: str) -> Path:
        """Get cache directory for a given cache key."""
        return self.cache_dir / cache_key

    def is_valid(self, config: ExtractionConfig) -> tuple[bool, str]:
        """Check if valid cache exists for this PDF."""
        from extractor import EXTRACTOR_VERSION

        try:
            cache_key = self.get_key(config)
        except (FileNotFoundError, OSError):
            return False, ""

        cache_dir = self._get_dir(cache_key)
        metadata_file = cache_dir / "metadata.json"
        output_file = cache_dir / "full_output.md"

        if not metadata_file.exists() or not output_file.exists():
            return False, cache_key

        try:
            with open(metadata_file) as f:
                metadata = json.load(f)

            p = Path(config.pdf_path).resolve()
            stat = p.stat()

            if (
                metadata.get("source_size") != stat.st_size
                or metadata.get("source_mtime") != stat.st_mtime
            ):
                return False, cache_key

            if metadata.get("extractor_version") != EXTRACTOR_VERSION:
                return False, cache_key

            return True, cache_key
        except (json.JSONDecodeError, KeyError, OSError):
            return False, cache_key

    def load(self, cache_key: str) -> ExtractionResult | None:
        """Load markdown from cache."""
        cache_dir = self._get_dir(cache_key)

        try:
            full_md = (cache_dir / "full_output.md").read_text(encoding="utf-8")
            with open(cache_dir / "metadata.json") as f:
                metadata = json.load(f)
            total_pages = metadata.get("total_pages", 0)
        except (FileNotFoundError, IOError, json.JSONDecodeError, OSError) as e:
            print(
                f"WARNING: Cache corrupted ({e.__class__.__name__}), regenerating...",
                file=sys.stderr,
            )
            try:
                if cache_dir.exists():
                    shutil.rmtree(cache_dir)
            except OSError:
                pass
            return None

        # Check if markdown references images
        has_image_refs = bool(re.search(r"!\[[^\]]*\]\([^)]+\)", full_md))

        # Get cached images directory
        cached_image_dir = cache_dir / "images"
        has_images = cached_image_dir.exists() and any(cached_image_dir.iterdir())

        # If markdown expects images but they're missing, invalidate cache
        if has_image_refs and not has_images:
            print(
                "WARNING: Cache missing images, regenerating...",
                file=sys.stderr,
            )
            try:
                shutil.rmtree(cache_dir)
            except OSError:
                pass
            return None

        image_dir = cached_image_dir if has_images else None

        return ExtractionResult(
            markdown=full_md,
            image_dir=image_dir,
            total_pages=total_pages,
            from_cache=True,
        )

    def _normalize_image_paths(self, markdown: str, source_image_dir: Path) -> str:
        """Normalize image paths in markdown to use relative 'images/' prefix."""
        if not source_image_dir:
            return markdown

        source_image_dir = Path(source_image_dir)

        def normalize_ref(match):
            alt_text = match.group(1)
            filename_raw = match.group(2)
            filename = Path(filename_raw).name
            if (source_image_dir / filename).exists():
                return f"![{alt_text}](images/{filename})"
            return match.group(0)

        pattern = r"!\[([^\]]*)\]\(([^)]+)\)"
        return re.sub(pattern, normalize_ref, markdown)

    def save(self, cache_key: str, result: ExtractionResult, config: ExtractionConfig):
        """Save full extraction to cache using atomic writes."""
        from extractor import EXTRACTOR_VERSION

        cache_dir = self._get_dir(cache_key)
        cache_dir.mkdir(parents=True, exist_ok=True)

        markdown = result.markdown
        if result.image_dir:
            markdown = self._normalize_image_paths(markdown, result.image_dir)

        p = Path(config.pdf_path).resolve()
        stat = p.stat()
        mode = f"docling_{config.images_scale}" if config.docling else "fast"

        metadata = {
            "source_path": str(p),
            "source_mtime": stat.st_mtime,
            "source_size": stat.st_size,
            "cache_key": cache_key,
            "cached_at": datetime.now().isoformat(),
            "total_pages": result.total_pages,
            "extractor_version": EXTRACTOR_VERSION,
            "mode": mode,
            "images_scale": config.images_scale if config.docling else None,
        }

        temp_md = None
        temp_json = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                dir=cache_dir,
                suffix=".md.tmp",
                delete=False,
                encoding="utf-8",
            ) as f:
                f.write(markdown)
                temp_md = f.name

            with tempfile.NamedTemporaryFile(
                mode="w", dir=cache_dir, suffix=".json.tmp", delete=False
            ) as f:
                json.dump(metadata, f, indent=2)
                temp_json = f.name

            os.replace(temp_md, cache_dir / "full_output.md")
            temp_md = None
            os.replace(temp_json, cache_dir / "metadata.json")
            temp_json = None

            if result.image_dir and Path(result.image_dir).exists():
                temp_images = cache_dir / "images.tmp"
                final_images = cache_dir / "images"

                if temp_images.exists():
                    shutil.rmtree(temp_images)

                shutil.copytree(result.image_dir, temp_images)

                if final_images.exists():
                    shutil.rmtree(final_images)
                os.rename(temp_images, final_images)

        finally:
            if temp_md and os.path.exists(temp_md):
                os.unlink(temp_md)
            if temp_json and os.path.exists(temp_json):
                os.unlink(temp_json)

    def clear(self, pdf_path: str = None) -> bool:
        """Clear cache for specific PDF (both fast and docling modes) or entire cache."""
        if pdf_path:
            # Clear BOTH fast and docling caches for this PDF
            cleared = False
            for docling_mode in [False, True]:
                try:
                    config = ExtractionConfig(pdf_path=pdf_path, docling=docling_mode)
                    cache_key = self.get_key(config)
                    cache_dir = self._get_dir(cache_key)
                    if cache_dir.exists():
                        shutil.rmtree(cache_dir)
                        cleared = True
                except (FileNotFoundError, OSError):
                    pass
            return cleared
        else:
            if self.cache_dir.exists():
                shutil.rmtree(self.cache_dir)
                return True
            return False

    def get_stats(self) -> dict:
        """Get statistics about the cache."""
        if not self.cache_dir.exists():
            return {"entries": 0, "total_size_mb": 0, "cache_dir": str(self.cache_dir)}

        entries = 0
        total_size = 0

        for entry in self.cache_dir.iterdir():
            if entry.is_dir():
                entries += 1
                for f in entry.rglob("*"):
                    if f.is_file():
                        total_size += f.stat().st_size

        return {
            "entries": entries,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "cache_dir": str(self.cache_dir),
        }


# =============================================================================
# IMAGE MANAGER
# =============================================================================


class ImageManager:
    """Manages image extraction and cleanup."""

    def __init__(self):
        self._temp_dirs: list[Path] = []

    def create_temp_dir(self, pdf_path: str) -> Path:
        """Create tracked temp directory for image extraction."""
        pdf_name = Path(pdf_path).stem
        safe_name = re.sub(r"[^\w\-_]", "_", pdf_name)
        temp_dir = Path(tempfile.mkdtemp(prefix=f"pdf_images_{safe_name}_"))
        self._temp_dirs.append(temp_dir)
        return temp_dir

    def cleanup(self):
        """Clean up all tracked temp directories."""
        for temp_dir in self._temp_dirs:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
        self._temp_dirs.clear()

    def extract_references(self, markdown: str) -> set:
        """Extract the set of image filenames referenced in markdown."""
        pattern = r"!\[[^\]]*\]\(([^)]+)\)"
        matches = re.findall(pattern, markdown)
        return {Path(m).name for m in matches}

    def get_info(self, image_dir: Path, referenced_only: set = None) -> list:
        """Get information about extracted images."""
        if not image_dir or not Path(image_dir).exists():
            return []

        image_dir = Path(image_dir)
        images = []

        for img_path in sorted(image_dir.glob("*")):
            if img_path.suffix.lower() in (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"):
                if referenced_only is not None and img_path.name not in referenced_only:
                    continue

                try:
                    size_bytes = img_path.stat().st_size
                    size_kb = size_bytes / 1024

                    try:
                        import pymupdf
                        pix = pymupdf.Pixmap(str(img_path))
                        dimensions = f"{pix.width}x{pix.height}"
                        pix = None
                    except Exception:
                        dimensions = "unknown"

                    images.append({
                        "filename": img_path.name,
                        "path": str(img_path),
                        "size_kb": round(size_kb, 1),
                        "dimensions": dimensions,
                    })
                except Exception:
                    pass

        return images

    def enhance_markdown(self, markdown: str, image_dir: Path) -> str:
        """Rewrite image references to use relative paths (portable, Windows-safe)."""
        if not image_dir:
            return markdown

        image_dir = Path(image_dir)

        def replace_image_ref(match):
            alt_text = match.group(1)
            filename_raw = match.group(2)
            filename = Path(filename_raw).name
            full_path = image_dir / filename

            # Use relative path for portability (POSIX format for Windows compatibility)
            relative_path = Path("images") / filename

            if full_path.exists():
                try:
                    size_kb = round(full_path.stat().st_size / 1024, 1)
                    try:
                        import pymupdf
                        pix = pymupdf.Pixmap(str(full_path))
                        dims = f"{pix.width}x{pix.height}"
                        pix = None
                    except Exception:
                        dims = "?"

                    return f"![{alt_text}]({relative_path.as_posix()})\n\n**[Image: {filename} ({dims}, {size_kb}KB)]**"
                except Exception:
                    return f"![{alt_text}]({relative_path.as_posix()})\n\n**[Image: {filename}]**"

            return match.group(0)

        pattern = r"!\[([^\]]*)\]\(([^)]+)\)"
        return re.sub(pattern, replace_image_ref, markdown)

    def create_summary(self, images: list) -> str:
        """Create a summary section listing all extracted images."""
        if not images:
            return ""

        lines = [
            "",
            "---",
            "",
            "## Extracted Images",
            "",
            "| # | File | Dimensions | Size |",
            "|---|------|------------|------|",
        ]

        for i, img in enumerate(images, 1):
            lines.append(
                f"| {i} | {img['filename']} | {img['dimensions']} | {img['size_kb']}KB |"
            )

        lines.append("")
        return "\n".join(lines)

    def finalize_images(
        self, temp_dir: Path, cache_dir: Path, output_path: Path, show_progress: bool = False
    ) -> Path | None:
        """Finalize image directory after extraction.

        Copies images from cache to output location (next to the markdown file).
        Cleans up temp directories.

        Returns the final image directory (next to output) for reference.
        """
        if not temp_dir:
            return None

        temp_dir = Path(temp_dir)

        # Clean up empty temp directories
        if not temp_dir.exists() or not any(temp_dir.iterdir()):
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            if temp_dir in self._temp_dirs:
                self._temp_dirs.remove(temp_dir)
            return None

        # Clean up temp directory (images are saved to cache)
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            if temp_dir in self._temp_dirs:
                self._temp_dirs.remove(temp_dir)

        # Copy images from cache to output location
        if cache_dir:
            cached_image_dir = cache_dir / "images"
            if cached_image_dir.exists() and any(cached_image_dir.iterdir()):
                return self._copy_images_to_output(cached_image_dir, output_path, show_progress)

        return None

    def _copy_images_to_output(
        self, source_dir: Path, output_path: Path, show_progress: bool = False
    ) -> Path | None:
        """Copy images from cache to output location (next to markdown file)."""
        output_path = Path(output_path)

        # Determine output images directory (sibling to markdown file)
        if output_path.suffix:  # It's a file path like "output.md"
            output_images_dir = output_path.parent / "images"
        else:  # It's a directory
            output_images_dir = output_path / "images"

        # Don't copy if already at output location
        if output_images_dir.resolve() == Path(source_dir).resolve():
            return output_images_dir

        # Copy images to output location
        output_images_dir.mkdir(parents=True, exist_ok=True)
        copied_count = 0
        for img in source_dir.iterdir():
            if img.is_file():
                shutil.copy2(img, output_images_dir / img.name)
                copied_count += 1

        if show_progress and copied_count > 0:
            print(f"Copied {copied_count} images to: {output_images_dir}", file=sys.stderr)

        return output_images_dir


# =============================================================================
# PDF PROCESSING
# =============================================================================


def check_dependencies(docling_mode: bool = False):
    """Check if required packages are installed."""
    missing = []

    try:
        import pymupdf
    except ImportError:
        missing.append("pymupdf")

    if docling_mode:
        try:
            import docling
        except ImportError:
            missing.append("docling")

        try:
            import docling_core
        except ImportError:
            missing.append("docling-core")

        install_cmd = "python scripts/bootstrap_env.py --extras docling"
    else:
        try:
            import pymupdf4llm
        except ImportError:
            missing.append("pymupdf4llm")

        install_cmd = "python scripts/bootstrap_env.py"

    if missing:
        print(f"ERROR: Missing dependencies: {', '.join(missing)}", file=sys.stderr)
        print(f"Install with: {install_cmd}", file=sys.stderr)
        return False

    return True


def convert_pdf(
    pdf_path,
    image_dir,
    show_progress=False,
    docling=False,
    images_scale=4.0,
    markitdown=False,
    easyocr_langs=None,
):
    """Convert PDF to markdown.

    Backend priority:
      --docling      -> Docling AI (best tables, slow)
      --markitdown   -> Microsoft MarkItDown (good headings/tables, fast)
      --ocr-easyocr  -> EasyOCR page-by-page (scanned PDFs only)
      default        -> PyMuPDF + pymupdf4llm (fast, tqdm for large PDFs)
    """
    if docling:
        from extractor import extract_pdf_docling

        markdown, _image_paths = extract_pdf_docling(
            pdf_path,
            output_dir=image_dir,
            images_scale=images_scale,
            show_progress=show_progress,
        )
        return markdown

    if markitdown:
        from extractor import extract_pdf_markitdown

        return extract_pdf_markitdown(pdf_path, show_progress=show_progress)

    if easyocr_langs is not None:
        from extractor import extract_pdf_easyocr

        return extract_pdf_easyocr(pdf_path, lang=easyocr_langs, show_progress=show_progress)

    from extractor import extract_pdf_fast

    return extract_pdf_fast(pdf_path, image_dir=image_dir, show_progress=show_progress)


def add_metadata_header(markdown, pdf_path, total_pages, image_dir=None, cached=False):
    """Add metadata header to markdown output."""
    filename = os.path.basename(pdf_path)

    header_lines = [
        "---",
        f"source: {filename}",
        f"total_pages: {total_pages}",
        f"extracted_at: {datetime.now().isoformat()}",
    ]

    if cached:
        header_lines.append("from_cache: true")

    if image_dir:
        # Use relative path for portability
        header_lines.append("images_dir: images")

    header_lines.extend(["---", "", ""])

    return "\n".join(header_lines) + markdown


def extract_auxiliary_tables(pdf_path: str, backend: str, max_tables: int):
    """Extract tables using optional specialist backends."""
    if backend == "none":
        return [], [], None

    from table_backends import extract_tables

    return extract_tables(pdf_path, backend=backend, max_tables=max_tables)


# =============================================================================
# MAIN
# =============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="Convert PDF to Markdown for LLM context (with persistent caching)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pdf_to_md.py document.pdf                    # Output to document.md (cached)
  python pdf_to_md.py document.pdf output.md         # Custom output path
  python pdf_to_md.py document.pdf --docling         # Accurate tables (slower)
  python pdf_to_md.py document.pdf --table-backend pdfplumber
  python pdf_to_md.py document.pdf --table-backend camelot
  python pdf_to_md.py document.pdf --clear-cache     # Clear cache and re-extract
  python pdf_to_md.py --clear-all-cache              # Clear entire cache

Caching:
  PDFs are cached in ~/.cache/pdf-to-markdown/
  Cache is keyed by file content hash + extraction mode.
  Cache persists until explicitly cleared or source PDF changes.
        """,
    )

    parser.add_argument("input", nargs="?", help="Input PDF file path")
    parser.add_argument("output", nargs="?", help="Output markdown file path (default: <input>.md)")
    parser.add_argument(
        "--docling",
        "--accurate",
        action="store_true",
        dest="docling",
        help="Use Docling AI for complex/borderless tables (slower, ~1 sec/page)",
    )
    parser.add_argument(
        "--markitdown",
        action="store_true",
        help="Use Microsoft MarkItDown for extraction (install: bootstrap_env.py --extras markitdown)",
    )
    parser.add_argument(
        "--ocr-easyocr",
        nargs="*",
        metavar="LANG",
        dest="ocr_easyocr",
        help=(
            "Use EasyOCR for scanned PDFs. Optionally pass language codes "
            "(default: es en). Example: --ocr-easyocr es en fr. "
            "Install: bootstrap_env.py --extras ocr"
        ),
    )
    parser.add_argument("--no-progress", action="store_true", help="Disable progress indicator")
    parser.add_argument(
        "--table-backend",
        choices=["auto", "none", "pdfplumber", "camelot", "tabula"],
        default="auto",
        help="Auxiliary table extraction backend used after main conversion",
    )
    parser.add_argument(
        "--max-aux-tables",
        type=int,
        default=25,
        help="Maximum auxiliary tables to append",
    )
    parser.add_argument(
        "--no-table-appendix",
        action="store_true",
        help="Do not append the auxiliary table extraction section",
    )

    # Cache options
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear cache for this PDF before processing",
    )
    parser.add_argument(
        "--clear-all-cache",
        action="store_true",
        help="Clear entire cache directory and exit",
    )
    parser.add_argument("--cache-stats", action="store_true", help="Show cache statistics and exit")
    parser.add_argument(
        "--with-images",
        action="store_true",
        help="Extract and copy embedded images next to the Markdown output. Off by default to avoid cluttering the output directory.",
    )

    args = parser.parse_args()

    cache_mgr = CacheManager()

    # Handle cache management commands
    if args.clear_all_cache:
        if cache_mgr.clear():
            print(f"Cache cleared: {cache_mgr.cache_dir}", file=sys.stderr)
        else:
            print("Cache was already empty.", file=sys.stderr)
        sys.exit(0)

    if args.cache_stats:
        stats = cache_mgr.get_stats()
        print(f"Cache directory: {stats['cache_dir']}", file=sys.stderr)
        print(f"Cached PDFs: {stats['entries']}", file=sys.stderr)
        print(f"Total size: {stats['total_size_mb']} MB", file=sys.stderr)
        sys.exit(0)

    # Require input for all other operations
    if not args.input:
        parser.error("the following arguments are required: input")

    # Handle --clear-cache
    if args.clear_cache:
        if cache_mgr.clear(args.input):
            print(f"Cache cleared for: {args.input}", file=sys.stderr)
        else:
            print(f"No cache found for: {args.input}", file=sys.stderr)

    # --- Pre-flight PDF validation (hard checks) ---
    from extractor import validate_pdf

    pdf_info = validate_pdf(args.input)

    # Print any warnings even on cache hit
    for w in pdf_info.warnings:
        print(f"AVISO: {w}", file=sys.stderr)

    if not pdf_info.is_valid:
        for err in pdf_info.errors:
            print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(1)

    if pdf_info.errors:
        # Errors block processing (e.g. encrypted)
        for err in pdf_info.errors:
            print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(1)

    show_progress = sys.stderr.isatty() and not args.no_progress

    # Check cache
    config = ExtractionConfig(pdf_path=args.input, docling=args.docling)
    valid, cache_key = cache_mgr.is_valid(config)

    result = None
    image_dir = None
    cache_hit = False

    if valid:
        if show_progress:
            mode = "docling" if args.docling else "fast"
            print(f"Cargando desde cache (modo {mode})...", file=sys.stderr)

        cache_result = cache_mgr.load(cache_key)
        if cache_result:
            result = cache_result.markdown
            total_pages = cache_result.total_pages
            cache_hit = True

            # Copy images from cache to output location only if explicitly requested
            if cache_result.image_dir and getattr(args, "with_images", False):
                output_path = args.output or os.path.splitext(args.input)[0] + ".md"
                img_mgr = ImageManager()
                image_dir = img_mgr._copy_images_to_output(
                    cache_result.image_dir, output_path, show_progress
                )

    # Extract if no cache hit
    if not cache_hit:
        if not check_dependencies(docling_mode=args.docling):
            sys.exit(1)

        # Use page_count from pre-flight validation (avoid double open)
        total_pages = pdf_info.page_count

        if not cache_key:
            cache_key = cache_mgr.get_key(config)

        img_mgr = ImageManager()
        # Only allocate an image directory if the user explicitly asked for images.
        # This prevents an `images/` directory from being created next to every .md output.
        temp_image_dir = img_mgr.create_temp_dir(args.input) if getattr(args, "with_images", False) else None

        try:
            if show_progress:
                if args.docling:
                    print(
                        f"Extrayendo {total_pages} paginas con Docling AI (~1 seg/pagina)...",
                        file=sys.stderr,
                    )
                elif getattr(args, "markitdown", False):
                    print("Extrayendo con MarkItDown (Microsoft)...", file=sys.stderr)
                elif getattr(args, "ocr_easyocr", None) is not None:
                    langs = args.ocr_easyocr or ["es", "en"]
                    print(f"OCR con EasyOCR ({langs})...", file=sys.stderr)
                # Fast mode shows its own tqdm bar via extract_pdf_fast

            easyocr_langs = None
            if getattr(args, "ocr_easyocr", None) is not None:
                easyocr_langs = args.ocr_easyocr if args.ocr_easyocr else ["es", "en"]

            result = convert_pdf(
                args.input,
                image_dir=temp_image_dir,
                show_progress=show_progress,
                docling=args.docling,
                markitdown=getattr(args, "markitdown", False),
                easyocr_langs=easyocr_langs,
            )
        except Exception as e:
            img_mgr.cleanup()
            print(f"ERROR: La conversion fallo: {e}", file=sys.stderr)
            sys.exit(1)

        # Save to cache
        extraction_result = ExtractionResult(
            markdown=result,
            image_dir=temp_image_dir,
            total_pages=total_pages,
        )
        cache_mgr.save(cache_key, extraction_result, config)
        if show_progress:
            print(f"Guardado en cache: {cache_mgr._get_dir(cache_key)}", file=sys.stderr)

        # Finalize images
        output_path = args.output or os.path.splitext(args.input)[0] + ".md"
        image_dir = img_mgr.finalize_images(
            temp_dir=temp_image_dir,
            cache_dir=cache_mgr._get_dir(cache_key),
            output_path=output_path,
            show_progress=show_progress,
        )

    # Format output
    output = result
    img_mgr_for_output = ImageManager()  # Fresh instance for output processing

    referenced_images = img_mgr_for_output.extract_references(result) if result else set()

    if image_dir:
        output = img_mgr_for_output.enhance_markdown(output, image_dir)
        images = img_mgr_for_output.get_info(image_dir, referenced_only=referenced_images)
        if images:
            output += img_mgr_for_output.create_summary(images)

    table_results = []
    table_warnings = []
    chosen_table_backend = None
    if args.table_backend != "none":
        if show_progress:
            print("Extrayendo tablas con backend auxiliar...", file=sys.stderr)
        table_results, table_warnings, chosen_table_backend = extract_auxiliary_tables(
            args.input,
            backend=args.table_backend,
            max_tables=args.max_aux_tables,
        )
        if not args.no_table_appendix and (table_results or table_warnings):
            from table_backends import render_table_appendix

            output += render_table_appendix(
                table_results,
                chosen_table_backend,
                table_warnings,
            )

    output = add_metadata_header(output, args.input, total_pages, image_dir, cached=cache_hit)

    # Write output
    output_path = args.output or os.path.splitext(args.input)[0] + ".md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output)

    msg = f"Converted {total_pages} pages to: {output_path}"
    if cache_hit:
        msg += " (from cache)"
    if image_dir:
        images = img_mgr_for_output.get_info(image_dir, referenced_only=referenced_images)
        if images:
            msg += f" ({len(images)} images)"
    if chosen_table_backend and table_results:
        msg += f" ({len(table_results)} aux tables via {chosen_table_backend})"
    elif table_warnings:
        msg += " (aux table extraction produced warnings)"
    print(msg, file=sys.stderr)


if __name__ == "__main__":
    main()
