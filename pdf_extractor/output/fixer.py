"""
output/fixer.py — Safe mechanical fixes ONLY (no semantic changes).

Safe fixes:
  ✅ Expand typographic ligatures (ﬁ→fi, ﬂ→fl, ﬀ→ff, ﬃ→ffi, ﬄ→ffl)
  ✅ Remove ASCII control characters (< 32, except \\t \\n \\r)
  ✅ Normalize multiple spaces → single space (NEVER inside code blocks or tables)
  ✅ Normalize list markers (-, *, +) to consistent style (-)
  ✅ Rejoin broken hyphenation at line-end (high-confidence only)
  ✅ Normalize CRLF → LF
  ✅ OCR artifact correction (pattern + optional dictionary) — applied only to
     pages flagged as OCR-sourced (confidence < 0.85 threshold)
  ✅ OCR table reconstruction — detects implicit two-column tables in OCR text
     (\"label  decimal\" pattern) and reformats them as Markdown tables. Missing
     values (lost due to shaded rows) are replaced with "—". Only active when
     apply_ocr_correction=True.

NEVER:
  ❌ Invent tables, text, or headings
  ❌ Change figures, names, dates, or institutional tone
  ❌ Modify content inside fenced code blocks
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


_LIGATURES = {
    "\uFB00": "ff",
    "\uFB01": "fi",
    "\uFB02": "fl",
    "\uFB03": "ffi",
    "\uFB04": "ffl",
    "\uFB05": "st",
    "\uFB06": "st",
}

# Words that should NOT be rejoined after hyphen (abbreviations, proper nouns heuristic)
_REJOIN_MIN_WORD_LEN = 3

# ---------------------------------------------------------------------------
# OCR table reconstruction constants
# ---------------------------------------------------------------------------
# Matches an OCR data row: [optional row-number]  label-text  [optional decimal]
# Must match:
#   "Nacional 45.1"                 "1 Aguascalientes 48.0"
#   "3 Baja California Sur 35.0"    "6 Colima"    "Chihuahua"
#   "9 Ciudad de México 136.2"
_OCR_ROW_RE = re.compile(
    r"^(\d{1,3}\.?\s+)?"                       # optional leading row number
    r"([A-Za-z\u00C0-\u024F]"                  # label starts with a letter (incl. accented)
    r"[A-Za-z\u00C0-\u024F\s\-',./()]{0,80}?"  # label body
    r"[A-Za-z\u00C0-\u024F.])"                 # label ends with letter or punctuation
    r"(\s+([\d]+[.,][\d]+))?"                  # optional decimal value  e.g. 45.1
    r"\s*$",
    re.UNICODE,
)
# Matches a standalone decimal anywhere on a line (used to count "valued" rows)
_OCR_DECIMAL_RE = re.compile(r"[\d]+[.,][\d]+")
# Minimum matching rows to qualify as a table block
_OCR_MIN_TABLE_ROWS = 4
# Fraction of rows that must carry a numeric value (guards against plain prose false positives)
_OCR_MIN_VALUED_RATIO = 0.30
# Consecutive blank/garbage lines tolerated mid-run (shading may produce noise rows)
_OCR_MAX_GAP = 1


@dataclass
class FixerResult:
    content: str
    fixes_applied: dict[str, int] = field(default_factory=dict)   # fix_name → count

    def total_fixes(self) -> int:
        return sum(self.fixes_applied.values())


def run(
    markdown: str,
    skip_fixes: bool = False,
    apply_ocr_correction: bool = False,
    ocr_language: str = "es",
) -> FixerResult:
    """Apply all safe mechanical fixes and return FixerResult.

    Parameters
    ----------
    apply_ocr_correction : bool
        When True, run the OCR artifact corrector (pattern + spell-check).
        Should be True only when the source is known to be OCR-extracted.
    ocr_language : str
        Language passed to the spell corrector ("es" or "en").
    """
    if skip_fixes:
        return FixerResult(content=markdown)

    result = FixerResult(content=markdown)

    result.content, count = _fix_crlf(result.content)
    if count:
        result.fixes_applied["crlf"] = count

    result.content, count = _fix_control_chars(result.content)
    if count:
        result.fixes_applied["control_chars"] = count

    result.content, count = _fix_ligatures(result.content)
    if count:
        result.fixes_applied["ligatures"] = count

    result.content, count = _fix_spaces(result.content)
    if count:
        result.fixes_applied["spaces"] = count

    result.content, count = _fix_list_markers(result.content)
    if count:
        result.fixes_applied["list_markers"] = count

    result.content, count = _fix_broken_hyphenation(result.content)
    if count:
        result.fixes_applied["hyphenation"] = count

    # OCR-specific correction (optional, only for OCR-sourced text)
    if apply_ocr_correction:
        # Reconstruct implicit two-column tables BEFORE spell correction so the
        # corrector doesn't mangle column-alignment spaces inside table cells.
        result.content, count = _fix_ocr_table_reconstruction(result.content)
        if count:
            result.fixes_applied["ocr_table_reconstruction"] = count

        try:
            from . import spell_corrector
            spell_result = spell_corrector.run(result.content, language=ocr_language)
            result.content = spell_result.content
            total_ocr = spell_result.total()
            if total_ocr:
                result.fixes_applied["ocr_correction"] = total_ocr
        except Exception:
            pass   # spell corrector is best-effort

    return result


# ---------------------------------------------------------------------------
# Individual fixers
# ---------------------------------------------------------------------------

def _fix_ocr_table_reconstruction(text: str) -> tuple[str, int]:
    """Detect implicit two-column tables in OCR text and reformat as Markdown.

    When Tesseract reads a table with shaded/coloured rows it often loses the
    column alignment, producing a flat list like::

        Entidad Federativa  Cobertura
        Nacional  45.1
        1 Aguascalientes  48.0
        6 Colima               ← value lost (dark background confused OCR)
        ...

    This function detects runs of ≥ ``_OCR_MIN_TABLE_ROWS`` consecutive lines
    that match ``[rownum] label [decimal]`` and where at least
    ``_OCR_MIN_VALUED_RATIO`` of them carry a numeric value, then replaces the
    run with a proper Markdown table.  Missing values are shown as "—".

    The line immediately before the run is used as the table header when it:
      - Has ≥ 2 words
      - Does NOT end with a decimal number
      - Does NOT start with a row number
    If no suitable header is found, generic "Descripción / Valor" labels are used.

    This is reformatting of already-extracted data — no new information is added.
    """
    lines = text.split("\n")

    # ── Phase 1: locate candidate regions ──────────────────────────────────
    def _is_data_row(line: str) -> bool:
        s = line.strip()
        return bool(s and not s.startswith(("#", "|", "```", "-", "*", "!"))
                    and _OCR_ROW_RE.match(s))

    regions: list[tuple[int, int]] = []  # (start, end) inclusive indices into `lines`
    i = 0
    while i < len(lines):
        if not _is_data_row(lines[i]):
            i += 1
            continue

        # Walk forward, tolerating up to _OCR_MAX_GAP blank/non-matching lines
        start = i
        j = i + 1
        gap = 0
        matching = 1
        while j < len(lines):
            lj = lines[j].strip()
            if not lj:                         # blank line
                gap += 1
                if gap > _OCR_MAX_GAP:
                    break
                j += 1
                continue
            if _is_data_row(lines[j]):
                gap = 0
                matching += 1
                j += 1
            else:
                break                          # markdown / heading / code block

        end = j - 1
        # Trim trailing blank lines
        while end >= start and not lines[end].strip():
            end -= 1

        i = j  # advance past this run

        if matching < _OCR_MIN_TABLE_ROWS:
            continue

        valued = sum(1 for k in range(start, end + 1)
                     if _OCR_DECIMAL_RE.search(lines[k]))
        if valued / matching < _OCR_MIN_VALUED_RATIO:
            continue

        regions.append((start, end))

    if not regions:
        return text, 0

    # ── Phase 2: build output ───────────────────────────────────────────────
    result: list[str] = []
    consumed_header: set[int] = set()  # line indices consumed as table headers
    converted = 0
    prev = 0

    for start, end in regions:
        result.extend(lines[prev:start])

        # Detect header: look back past at most one blank line
        header_col1, header_col2 = "Descripción", "Valor"
        header_idx: int | None = None
        for back in (1, 2):
            candidate_idx = start - back
            if candidate_idx < 0:
                break
            candidate = lines[candidate_idx].strip()
            if not candidate:
                continue  # blank — keep looking one more line back
            words = candidate.split()
            if (len(words) >= 2
                    and not _OCR_DECIMAL_RE.fullmatch(candidate)
                    and not re.match(r"^\d{1,3}\s", candidate)):
                # Split: last word is col-2 header, everything else is col-1
                header_col1 = " ".join(words[:-1])
                header_col2 = words[-1]
                header_idx = candidate_idx
            break  # only look back 1-2 lines total

        # Remove the consumed header from output if we already added it
        if header_idx is not None and header_idx not in consumed_header:
            # It may be in `result` already if it was part of the lines before `start`
            # Find and pop it (it would be the last non-blank entry we added)
            for ri in range(len(result) - 1, -1, -1):
                if result[ri].strip() == lines[header_idx].strip():
                    result.pop(ri)
                    consumed_header.add(header_idx)
                    break

        # Build data rows
        table_rows: list[tuple[str, str]] = []
        for k in range(start, end + 1):
            raw = lines[k].strip()
            if not raw:
                continue
            m = _OCR_ROW_RE.match(raw)
            if not m:
                continue
            rownum = (m.group(1) or "").strip()
            label  = m.group(2).strip()
            value  = (m.group(4) or "").strip() or "—"
            full_label = f"{rownum} {label}".strip() if rownum else label
            table_rows.append((full_label, value))

        if not table_rows:
            result.extend(lines[start:end + 1])
            prev = end + 1
            continue

        # Format as Markdown table
        col1_w = max(len(header_col1), max(len(r[0]) for r in table_rows))
        col2_w = max(len(header_col2), max(len(r[1]) for r in table_rows))
        md: list[str] = [
            f"| {header_col1:<{col1_w}} | {header_col2:<{col2_w}} |",
            f"| {'-' * col1_w} | {'-' * col2_w} |",
        ]
        for lbl, val in table_rows:
            md.append(f"| {lbl:<{col1_w}} | {val:<{col2_w}} |")

        result.append("\n".join(md))
        converted += 1
        prev = end + 1

    result.extend(lines[prev:])
    return "\n".join(result), converted


def _fix_crlf(text: str) -> tuple[str, int]:
    count = text.count("\r\n")
    return text.replace("\r\n", "\n").replace("\r", "\n"), count


def _fix_control_chars(text: str) -> tuple[str, int]:
    count = 0
    out = []
    for ch in text:
        if ord(ch) < 32 and ch not in ("\t", "\n"):
            count += 1
        else:
            out.append(ch)
    return "".join(out), count


def _fix_ligatures(text: str) -> tuple[str, int]:
    count = 0
    for lig, replacement in _LIGATURES.items():
        occurrences = text.count(lig)
        if occurrences:
            text = text.replace(lig, replacement)
            count += occurrences
    return text, count


def _fix_spaces(text: str) -> tuple[str, int]:
    """Normalize multiple spaces to single, but NOT inside code blocks or table lines."""
    lines = text.split("\n")
    fixed = []
    in_code = False
    count = 0

    for line in lines:
        if line.strip().startswith("```"):
            in_code = not in_code
            fixed.append(line)
            continue
        if in_code or "|" in line:
            fixed.append(line)
            continue
        new_line = re.sub(r" {2,}", " ", line)
        count += line.count("  ") - new_line.count("  ")
        fixed.append(new_line)

    return "\n".join(fixed), count


def _fix_list_markers(text: str) -> tuple[str, int]:
    """Normalize *, + list markers to -."""
    lines = text.split("\n")
    fixed = []
    count = 0
    in_code = False

    for line in lines:
        if line.strip().startswith("```"):
            in_code = not in_code
            fixed.append(line)
            continue
        if in_code:
            fixed.append(line)
            continue
        m = re.match(r"^(\s*)[*+](\s+\S)", line)
        if m:
            line = m.group(1) + "-" + m.group(2) + line[len(m.group(0)):]
            count += 1
        fixed.append(line)

    return "\n".join(fixed), count


def _fix_broken_hyphenation(text: str) -> tuple[str, int]:
    """
    Rejoin words broken across lines with a trailing hyphen.
    Only when both parts look like real words (length >= min, no digits or caps).
    """
    lines = text.split("\n")
    fixed: list[str] = []
    count = 0
    i = 0

    while i < len(lines):
        line = lines[i]
        # Check for trailing hyphen (not a markdown HR)
        if (i + 1 < len(lines) and line.endswith("-")
                and len(line) > 1 and line[-2] != "-"):
            word_end = re.search(r"(\w+)-$", line)
            next_line = lines[i + 1].lstrip()
            word_start = re.match(r"^([a-záéíóúüñ]+)", next_line, re.IGNORECASE)

            if (word_end and word_start
                    and len(word_end.group(1)) >= _REJOIN_MIN_WORD_LEN
                    and len(word_start.group(1)) >= _REJOIN_MIN_WORD_LEN
                    and word_end.group(1)[0].islower()
                    and word_start.group(1)[0].islower()):
                # Rejoin: remove hyphen, merge next line
                rejoined = line[:-1] + next_line
                fixed.append(rejoined)
                i += 2
                count += 1
                continue

        fixed.append(line)
        i += 1

    return "\n".join(fixed), count
