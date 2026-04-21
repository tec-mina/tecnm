"""
output/frontmatter.py — Build YAML frontmatter block for output Markdown.

Always prepended to the assembled output.
Quality labels: excellent (90-100) / good (80-89) / acceptable (70-79) / poor (<70)
"""

from __future__ import annotations

from datetime import datetime, timezone


_QUALITY_LABELS = [
    (90, "excellent"),
    (80, "good"),
    (70, "acceptable"),
    (0,  "poor"),
]


def quality_label(score: float) -> str:
    for threshold, label in _QUALITY_LABELS:
        if score >= threshold:
            return label
    return "poor"


def build(
    source_file: str,
    page_count: int,
    file_size_mb: float,
    language: str,
    tables_found: int,
    has_images: bool,
    has_scanned_pages: bool,
    features_used: list[str],
    extraction_time_sec: float,
    quality_score: float,
    is_valid: bool,
    from_cache: bool,
    warnings: list[str],
    extraction_date: str | None = None,
) -> str:
    """Return a YAML frontmatter block (including --- delimiters)."""

    if extraction_date is None:
        extraction_date = datetime.now(timezone.utc).isoformat()

    label = quality_label(quality_score)

    fields: list[tuple[str, object]] = [
        ("source", source_file),
        ("pages", page_count),
        ("file_size_mb", round(file_size_mb, 2)),
        ("extraction_date", f'"{extraction_date}"'),
        ("language", language),
        ("tables_found", tables_found),
        ("has_images", _bool(has_images)),
        ("has_scanned_pages", _bool(has_scanned_pages)),
        ("features_used", _list(features_used)),
        ("extraction_time_sec", round(extraction_time_sec, 2)),
        ("quality_score", round(quality_score, 1)),
        ("quality_label", f'"{label}"'),
        ("is_valid", _bool(is_valid)),
        ("from_cache", _bool(from_cache)),
        ("warnings", _list(warnings)),
    ]

    lines = ["---"]
    for key, value in fields:
        lines.append(f"{key}: {value}")
    lines.append("---")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _bool(v: bool) -> str:
    return "true" if v else "false"


def _list(items: list) -> str:
    if not items:
        return "[]"
    quoted = [f'"{i}"' for i in items]
    return "[" + ", ".join(quoted) + "]"
