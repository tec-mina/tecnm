"""
features/adaptive_intelligent.py — Per-page intelligent adaptive extraction.

For each page: detect content type, try candidate strategies in order, score
each result semantically, and keep the best one.  A structurally valid table
that is 80 % null is useless — semantic scoring catches that.

Semantic rules
--------------
Text
  • word_density  = alphabetic_words / total_tokens   ≥ 0.35
  • min_chars     = stripped content ≥ 40 chars
  • noise ratio   = repeated short sequences — penalises OCR garbage

Tables
  • real_cell_ratio = non-empty cells / total cells   ≥ 0.40
  • needs ≥ 2 columns with at least one non-trivial header
  • header tokens must be mostly alphabetic

Strategy order per page type
-----------------------------
text-native  : text_fast → text_pdfminer → tables (if rect-dense) → ocr_tesseract
scanned      : ocr_tesseract → ocr_easy
table-heavy  : tables → text_fast → tables_camelot
mixed        : text_fast + tables → ocr_tesseract for remaining scanned pages
"""

from __future__ import annotations

import importlib
import re
from dataclasses import dataclass, field

from ._base import FeatureResult, PageResult
from ._protocol import StrategyMeta

STRATEGY = StrategyMeta(
    name="auto:intelligent",
    tier="auto",
    description="Intelligent per-page: tries strategies in order, keeps best semantically valid result",
    module="pdf_extractor.features.adaptive_intelligent",
    requires_python=["fitz"],
    priority=1,
)

# ── Minimum thresholds for accepting a result ──────────────────────────────

_MIN_TEXT_WORD_DENSITY = 0.30     # fraction of tokens that must be real words
_MIN_TEXT_CHARS = 40              # absolute minimum chars (after strip)
_MIN_TABLE_REAL_CELL_RATIO = 0.40 # fraction of cells that must be non-empty
_MIN_TABLE_COLS = 2               # discard single-column "tables"
_OCR_ARTIFACT_RE = re.compile(
    r"(\b[bcdfghjklmnpqrstvwxyz]{5,}\b|[^\w\s]{3,}|\b\d{10,}\b)",
    re.IGNORECASE,
)


# ── Strategy candidate lists (module short-names) ──────────────────────────

_STRATEGIES_TEXT = ["text_fast", "text_pdfminer", "text_tika"]
_STRATEGIES_OCR  = ["ocr_tesseract", "ocr_easy"]
_STRATEGIES_TABLE = ["tables", "tables_camelot", "tables_tabula"]


# ---------------------------------------------------------------------------
# Public entry-point
# ---------------------------------------------------------------------------

def extract(
    pdf_path: str,
    page_range: tuple[int, int] | None = None,
) -> FeatureResult:
    result = FeatureResult(feature="adaptive_intelligent", content_category="text")

    try:
        import pymupdf as fitz
    except ImportError:
        try:
            import fitz
        except ImportError:
            result.warnings.append("pymupdf/fitz not installed; adaptive strategy unavailable")
            return result

    try:
        doc = fitz.open(pdf_path)
    except Exception as exc:
        result.warnings.append(f"Cannot open PDF: {exc}")
        return result

    try:
        total = doc.page_count
        start, end = _resolve_range(page_range, total)
        page_profiles = _profile_pages(doc, start, end)
    finally:
        doc.close()

    md_parts: list[str] = []
    total_score = 0.0
    pages_extracted = 0

    for page_1indexed, profile in page_profiles.items():
        candidates = _candidate_strategies(profile)
        best_content, best_score, best_backend = _best_for_page(
            pdf_path, page_1indexed, candidates, profile
        )

        if best_content:
            md_parts.append(f"<!-- Page {page_1indexed} -->\n\n{best_content}")
            result.pages.append(PageResult(
                page=page_1indexed,
                content=best_content,
                backend=best_backend,
                confidence=best_score,
            ))
            total_score += best_score
            pages_extracted += 1
        else:
            result.warnings.append(f"Page {page_1indexed}: no strategy produced useful content")

    result.markdown = "\n\n".join(md_parts)
    if pages_extracted:
        result.confidence = round(total_score / pages_extracted, 3)
        result.metadata = {
            "pages_extracted": pages_extracted,
            "pages_total": end - start,
            "backend": "adaptive_intelligent",
        }
    else:
        result.confidence = 0.0

    return result


# ---------------------------------------------------------------------------
# Per-page profiling
# ---------------------------------------------------------------------------

@dataclass
class _PageProfile:
    page_num: int
    is_scanned: bool = False
    has_tables: bool = False
    char_count: int = 0
    image_count: int = 0
    rect_count: int = 0


def _profile_pages(doc, start: int, end: int) -> dict[int, _PageProfile]:
    profiles: dict[int, _PageProfile] = {}

    try:
        import pdfplumber
        _has_plumber = True
    except ImportError:
        _has_plumber = False

    for page_num in range(start, end):
        page = doc[page_num]
        page_1indexed = page_num + 1

        text = page.get_text("text")
        char_count = len(text.strip())
        images = page.get_images(full=True)

        p = _PageProfile(page_num=page_1indexed)
        p.char_count = char_count
        p.image_count = len(images)
        p.is_scanned = (char_count < 60 and len(images) > 0)

        if _has_plumber and not p.is_scanned:
            try:
                import pdfplumber as _plumber
                with _plumber.open(doc.name) as pdf:
                    if page_num < len(pdf.pages):
                        rects = pdf.pages[page_num].rects
                        p.rect_count = len(rects) if rects else 0
                        p.has_tables = p.rect_count >= 4
            except Exception:
                pass

        profiles[page_1indexed] = p

    return profiles


# ---------------------------------------------------------------------------
# Strategy selection per page profile
# ---------------------------------------------------------------------------

def _candidate_strategies(profile: _PageProfile) -> list[str]:
    if profile.is_scanned:
        return _STRATEGIES_OCR

    if profile.has_tables and profile.char_count > 60:
        # Mixed: text + tables — try table extractors first, then text
        return _STRATEGIES_TABLE + _STRATEGIES_TEXT

    if profile.has_tables:
        return _STRATEGIES_TABLE + _STRATEGIES_OCR

    return _STRATEGIES_TEXT + _STRATEGIES_TABLE


# ---------------------------------------------------------------------------
# Run strategies until one produces semantically valid content
# ---------------------------------------------------------------------------

def _best_for_page(
    pdf_path: str,
    page_1indexed: int,
    candidates: list[str],
    profile: _PageProfile,
) -> tuple[str, float, str]:
    """Return (content, score, backend) for the best strategy on this page."""
    best_content = ""
    best_score = 0.0
    best_backend = "none"

    page_range = (page_1indexed, page_1indexed)

    for strategy_name in candidates:
        mod = _load_strategy(strategy_name)
        if mod is None:
            continue

        try:
            fr = mod.extract(pdf_path, page_range)
        except Exception:
            continue

        if fr is None or fr.confidence == 0.0:
            continue

        content, content_type = _content_for_page(fr, page_1indexed)
        if not content:
            continue

        score = semantic_score(content, content_type)

        if score > best_score:
            best_score = score
            best_content = content
            best_backend = strategy_name

        # Accept immediately if score is good enough
        if score >= 0.70:
            break

    return best_content, best_score, best_backend


def _content_for_page(fr: FeatureResult, page_1indexed: int) -> tuple[str, str]:
    """Extract content and type for a specific page from a FeatureResult."""
    # Per-page results
    for pr in fr.pages:
        if pr.page == page_1indexed and pr.content.strip():
            return pr.content.strip(), pr.content_type

    # Fallback: try to parse page marker from full markdown
    if fr.markdown:
        page_blocks = re.split(r"<!-- Page (\d+) -->", fr.markdown)
        for i in range(1, len(page_blocks) - 1, 2):
            if int(page_blocks[i]) == page_1indexed:
                block = page_blocks[i + 1].strip()
                if block:
                    content_type = "table" if "|" in block else "text"
                    return block, content_type

    return "", "text"


# ---------------------------------------------------------------------------
# Semantic scoring
# ---------------------------------------------------------------------------

def semantic_score(content: str, content_type: str = "text") -> float:
    """Return a 0.0–1.0 semantic quality score.

    0.0 → useless (empty, all-null table, pure noise)
    1.0 → high-quality content with real information
    """
    if not content or len(content.strip()) < _MIN_TEXT_CHARS:
        return 0.0

    if content_type == "table" or "|" in content:
        return _score_table(content)

    return _score_text(content)


def _score_text(content: str) -> float:
    tokens = content.split()
    if not tokens:
        return 0.0

    word_count = sum(1 for t in tokens if _is_real_word(t))
    word_density = word_count / len(tokens)

    if word_density < _MIN_TEXT_WORD_DENSITY:
        return round(word_density * 0.5, 3)  # partial score, below threshold

    # Penalise OCR artifact patterns
    artifact_hits = len(_OCR_ARTIFACT_RE.findall(content))
    artifact_penalty = min(0.3, artifact_hits * 0.03)

    # Bonus for content richness
    richness = min(0.2, len(content) / 5000)

    score = word_density * 0.70 - artifact_penalty + richness + 0.10
    return round(max(0.0, min(1.0, score)), 3)


def _score_table(content: str) -> float:
    lines = [l for l in content.split("\n") if "|" in l]
    if not lines:
        return _score_text(content)

    # Skip separator rows: cells contain only dashes, colons, spaces (no letters/digits)
    def _is_separator(line: str) -> bool:
        cells = line.strip().strip("|").split("|")
        return all(re.fullmatch(r"[\s\-:]+", c) for c in cells)

    data_rows = [l for l in lines if not _is_separator(l)]
    if not data_rows:
        return 0.0

    # Parse cells
    all_cells: list[str] = []
    for row in data_rows:
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        all_cells.extend(cells)

    if not all_cells:
        return 0.0

    col_count = len(data_rows[0].strip().strip("|").split("|"))
    if col_count < _MIN_TABLE_COLS:
        return 0.05  # single-column "table" — almost never useful

    # Count empty/null cells
    _NULL_VALUES = {"", "-", "—", "n/a", "na", "null", "none", "nan", "nd", "s/d"}
    empty = sum(1 for c in all_cells if c.lower() in _NULL_VALUES)
    real_cell_ratio = 1.0 - (empty / len(all_cells))

    if real_cell_ratio < _MIN_TABLE_REAL_CELL_RATIO:
        return round(real_cell_ratio * 0.4, 3)  # penalise heavily

    # Check header quality (first data row = headers)
    header_cells = [c.strip() for c in data_rows[0].strip().strip("|").split("|")]
    header_words = sum(1 for h in header_cells if _is_real_word(h))
    header_quality = header_words / max(len(header_cells), 1)

    score = real_cell_ratio * 0.60 + header_quality * 0.30 + 0.10
    return round(max(0.0, min(1.0, score)), 3)


def _is_real_word(token: str) -> bool:
    """True if token looks like an actual word (not a number, symbol, or noise)."""
    clean = re.sub(r"[^\w]", "", token)
    if len(clean) < 2:
        return False
    alpha_ratio = sum(1 for c in clean if c.isalpha()) / len(clean)
    return alpha_ratio >= 0.60


# ---------------------------------------------------------------------------
# Strategy loader
# ---------------------------------------------------------------------------

_strategy_cache: dict[str, object | None] = {}


def _load_strategy(name: str):
    if name in _strategy_cache:
        return _strategy_cache[name]
    try:
        mod = importlib.import_module(f"pdf_extractor.features.{name}")
        _strategy_cache[name] = mod
        return mod
    except ImportError:
        _strategy_cache[name] = None
        return None


def _resolve_range(page_range: tuple[int, int] | None, total: int) -> tuple[int, int]:
    if page_range is None:
        return 0, total
    return max(0, page_range[0] - 1), min(total, page_range[1])
