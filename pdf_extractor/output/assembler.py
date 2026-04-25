"""
output/assembler.py — Merge FeatureResults into a single clean Markdown document.

Assembly order:
  1. YAML frontmatter (always)
  2. Auto-generated Table of Contents (when headings present)
  3. Main text content (preserving heading hierarchy H1→H6)
  4. Tables inline at their original page position (<!-- Page N --> markers)
  5. Image references as ![description](images/page_N_img_M.png)
  6. Auxiliary tables appendix (if table_appendix=True)

Page markers always emitted:
  <!-- Page 1 -->
  ... content ...
  <!-- Page 2 -->

Heading hierarchy rules:
  - First heading must be H1
  - No heading level jumps > 1 (insert placeholder H2 if needed)

Feature routing:
  text features   → text_pages (best-wins per page by confidence)
  table features  → table_pages (additive, all tables kept)
  image features  → image_pages (additive)
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..features._base import FeatureResult, PageResult


_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)")
_TABLE_HEADING_RE = re.compile(r"^### Tabla")



@dataclass
class AssemblyPlan:
    """Tracks which content goes on which page.
    Built incrementally — one FeatureResult at a time via merge_feature().
    """
    text_pages: dict[int, str]           # page → best text content so far
    text_confidence: dict[int, float]    # page → confidence of stored text
    table_pages: dict[int, list[str]]    # page → table markdown blocks (additive)
    image_pages: dict[int, list[str]]    # page → image refs
    total_pages: int


# ---------------------------------------------------------------------------
# Incremental streaming API
# ---------------------------------------------------------------------------

def make_plan(total_pages: int) -> AssemblyPlan:
    """Return an empty AssemblyPlan ready to receive features."""
    return AssemblyPlan(
        text_pages={},
        text_confidence={},
        table_pages={},
        image_pages={},
        total_pages=total_pages,
    )


def merge_feature(plan: AssemblyPlan, fr: FeatureResult) -> None:
    """Absorb one FeatureResult into *plan*.

    Call immediately after each feature runs, then ``del fr`` to free memory.
    Text pages are kept only when the new feature has higher confidence than
    what is already stored (per-page best-wins).  Table and image pages are
    additive.
    """
    if fr.confidence == 0.0:
        return

    if fr.content_category == "table":
        _merge_tables(plan, fr)
    elif fr.content_category == "image":
        _merge_images(plan, fr)
    else:
        # Default: "text" — best-wins per page by confidence
        _merge_text(plan, fr)


def _merge_text(plan: AssemblyPlan, fr: FeatureResult) -> None:
    per_page = [p for p in fr.pages if p.content.strip()]
    if per_page:
        for pr in per_page:
            if fr.confidence > plan.text_confidence.get(pr.page, -1.0):
                plan.text_pages[pr.page] = pr.content
                plan.text_confidence[pr.page] = fr.confidence
    elif fr.markdown.strip():
        # No per-page breakdown: split full markdown by page markers
        for page_num, content in _split_by_markers(fr.markdown).items():
            if fr.confidence > plan.text_confidence.get(page_num, -1.0):
                plan.text_pages[page_num] = content
                plan.text_confidence[page_num] = fr.confidence


def _merge_tables(plan: AssemblyPlan, fr: FeatureResult) -> None:
    for pr in fr.pages:
        if pr.content_type == "table" and pr.content.strip():
            plan.table_pages.setdefault(pr.page, []).append(pr.content)


def _merge_images(plan: AssemblyPlan, fr: FeatureResult) -> None:
    for pr in fr.pages:
        if pr.content.strip():
            plan.image_pages.setdefault(pr.page, []).append(pr.content)


# ---------------------------------------------------------------------------
# Render plan → Markdown string
# ---------------------------------------------------------------------------

def assemble_from_plan(
    plan: AssemblyPlan,
    frontmatter_str: str = "",
    table_appendix: bool = True,
    with_images: bool = False,
    images_dir: Path | None = None,
    with_toc: bool = True,
) -> str:
    """Render an already-built AssemblyPlan into a single Markdown string."""
    parts: list[str] = [frontmatter_str]
    all_tables: list[str] = []
    body_parts: list[str] = []

    for page_num in range(1, plan.total_pages + 1):
        # Determine if the page has any actual content
        page_text = plan.text_pages.get(page_num, "").strip()
        page_tables = plan.table_pages.get(page_num, [])
        page_images = plan.image_pages.get(page_num, []) if with_images else []

        if not page_text and not page_tables and not page_images:
            continue   # skip empty pages — no marker emitted

        body_parts.append(f"<!-- Page {page_num} -->")

        if page_text:
            body_parts.append(_fix_heading_hierarchy(page_text))

        for table_md in page_tables:
            body_parts.append(table_md)
            all_tables.append(table_md)

        if with_images:
            for img_ref in page_images:
                body_parts.append(img_ref)

    body = "\n\n".join(p for p in body_parts if p.strip())

    # Table of Contents — inserted after frontmatter, before body
    if with_toc:
        toc = _generate_toc(body)
        if toc:
            parts.append(toc)

    parts.append(body)

    if table_appendix and all_tables:
        parts.append("\n## Tablas Auxiliares\n")
        parts.extend(all_tables)

    return "\n\n".join(p for p in parts if p.strip())


def assemble(
    feature_results: list[FeatureResult],
    frontmatter_str: str,
    total_pages: int,
    table_appendix: bool = True,
    with_images: bool = False,
    images_dir: Path | None = None,
    with_toc: bool = True,
) -> str:
    """Backward-compatible wrapper: build plan from a list, then render.

    Prefer the incremental pipeline (make_plan / merge_feature / assemble_from_plan)
    when processing large documents.
    """
    plan = make_plan(total_pages)
    for fr in feature_results:
        merge_feature(plan, fr)
    return assemble_from_plan(
        plan, frontmatter_str, table_appendix, with_images, images_dir, with_toc
    )


def _split_by_markers(markdown: str) -> dict[int, str]:
    """Split assembled markdown into per-page dict using <!-- Page N --> markers."""
    result: dict[int, str] = {}
    parts = re.split(r"<!-- Page (\d+) -->", markdown)
    i = 1
    while i < len(parts) - 1:
        try:
            page_num = int(parts[i])
            content = parts[i + 1].strip()
            result[page_num] = content
        except (ValueError, IndexError):
            pass
        i += 2
    if not result and markdown.strip():
        result[1] = markdown.strip()
    return result


# ---------------------------------------------------------------------------
# Heading hierarchy fixer
# ---------------------------------------------------------------------------

def _fix_heading_hierarchy(text: str) -> str:
    """
    Ensure first heading is H1 and no level jumps > 1.
    Inserts placeholder headings where needed.
    """
    lines = text.split("\n")
    out: list[str] = []
    prev_level: int | None = None

    for line in lines:
        m = _HEADING_RE.match(line)
        if not m:
            out.append(line)
            continue

        level = len(m.group(1))
        heading_text = m.group(2)

        # First heading must be H1
        if prev_level is None and level != 1:
            out.append(f"# {heading_text}")
            prev_level = 1
            continue

        # Insert missing intermediate headings
        if prev_level is not None and level - prev_level > 1:
            for mid_level in range(prev_level + 1, level):
                out.append(f"{'#' * mid_level} —")

        out.append(line)
        prev_level = level

    return "\n".join(out)


# ---------------------------------------------------------------------------
# Table of Contents generator
# ---------------------------------------------------------------------------

def _generate_toc(body: str) -> str:
    """Build a Markdown Table of Contents from headings in *body*.

    Returns an empty string when fewer than 3 headings are found
    (not worth having a ToC for very short docs).
    """
    entries: list[str] = []
    in_code = False

    for line in body.split("\n"):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue

        m = _HEADING_RE.match(line)
        if not m:
            continue

        level = len(m.group(1))
        title = m.group(2).strip().strip("*")   # remove bold markers if any

        # Build GitHub-compatible anchor
        anchor = re.sub(r"[^\w\s\-]", "", title.lower())
        anchor = re.sub(r"\s+", "-", anchor.strip())
        anchor = re.sub(r"-{2,}", "-", anchor)

        indent = "  " * (level - 1)
        entries.append(f"{indent}- [{title}](#{anchor})")

    if len(entries) < 3:
        return ""

    return "## Contenido\n\n" + "\n".join(entries)
