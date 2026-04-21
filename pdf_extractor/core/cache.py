"""
core/cache.py — SHA256-based extraction cache.

Cache key = SHA256(file_content) + file_size + extraction_options_digest
Location:   ~/.cache/pdf-extractor/<cache_key>/
"""

import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import Any


_CACHE_ROOT = Path.home() / ".cache" / "pdf-extractor"
_DOCKER_FLAG = _CACHE_ROOT / "docker_verified"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compute_key(
    pdf_path: str,
    mode: str,
    options: dict[str, Any] | None = None,
) -> str:
    """Compute a cross-platform cache key for the PDF content and request options."""
    p = Path(pdf_path)
    size = p.stat().st_size
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    options_sig = json.dumps(
        {"mode": mode, "options": options or {}},
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    )
    options_hash = hashlib.sha256(options_sig.encode("utf-8")).hexdigest()[:16]
    return f"{h.hexdigest()}_{size}_{options_hash}"


def hit(key: str) -> bool:
    """Return True if a valid cached result exists for this key.

    Note: this is a best-effort signal only. A concurrent process can evict
    the entry between hit() and load(). Callers must handle the race by
    using ``load_or_none()`` or wrapping ``load()`` in try/except.
    """
    entry = _entry_dir(key)
    return (entry / "full_output.md").exists() and (entry / "metadata.json").exists()


def load(key: str) -> tuple[str, dict[str, Any]]:
    """Load cached markdown and metadata. Raises if not found."""
    entry = _entry_dir(key)
    markdown = (entry / "full_output.md").read_text(encoding="utf-8")
    metadata = json.loads((entry / "metadata.json").read_text(encoding="utf-8"))
    return markdown, metadata


def load_or_none(key: str) -> tuple[str, dict[str, Any]] | None:
    """Atomic cache read. Returns None on any read error (missing, partial,
    corrupt JSON) so the caller can fall back to a fresh extraction instead
    of crashing on a concurrent cache eviction.
    """
    entry = _entry_dir(key)
    try:
        markdown = (entry / "full_output.md").read_text(encoding="utf-8")
        metadata = json.loads((entry / "metadata.json").read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None
    return markdown, metadata


def save(key: str, markdown: str, metadata: dict[str, Any],
         images_dir: Path | None = None) -> None:
    """Write extraction results to cache. Only called after validation PASS."""
    entry = _entry_dir(key)
    entry.mkdir(parents=True, exist_ok=True)
    (entry / "full_output.md").write_text(markdown, encoding="utf-8")
    (entry / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if images_dir and images_dir.exists():
        dest_images = entry / "images"
        if dest_images.exists():
            shutil.rmtree(dest_images)
        shutil.copytree(images_dir, dest_images)


def load_images(key: str, dest_dir: Path) -> None:
    """Copy cached images to dest_dir if present."""
    src = _entry_dir(key) / "images"
    if src.exists():
        dest_dir.mkdir(parents=True, exist_ok=True)
        for img in src.iterdir():
            shutil.copy2(img, dest_dir / img.name)


def invalidate(key: str) -> None:
    """Delete a specific cache entry."""
    entry = _entry_dir(key)
    if entry.exists():
        shutil.rmtree(entry)


# ---------------------------------------------------------------------------
# Docker install flag
# ---------------------------------------------------------------------------

def docker_verified_version() -> str | None:
    if _DOCKER_FLAG.exists():
        return _DOCKER_FLAG.read_text(encoding="utf-8").strip()
    return None


def set_docker_verified(version: str) -> None:
    _CACHE_ROOT.mkdir(parents=True, exist_ok=True)
    _DOCKER_FLAG.write_text(version, encoding="utf-8")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _entry_dir(key: str) -> Path:
    return _CACHE_ROOT / key
