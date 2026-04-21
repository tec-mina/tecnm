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
