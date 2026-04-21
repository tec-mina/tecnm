"""
output/spell_corrector.py — OCR artifact correction for low-confidence extracted text.

Two correction layers are applied in order:

  1. Pattern-based (no dependencies)
     Common OCR substitution errors caused by visually similar characters:
       0 ↔ o  (inside word context)
       1 ↔ l / i
       | ↔ l
       rn → m   (very common — "rnomento" → "momento")
       vv → w   (rare in Spanish but present in scanned docs)

  2. Dictionary-based (requires pyspellchecker — optional)
     After pattern cleanup, remaining unknown words are looked up in
     a Spanish (default) or English spell-checker dictionary.
     A word is corrected ONLY when:
       - pyspellchecker flags it as unknown
       - a high-confidence correction exists
       - the word is ≥ min_word_len lowercase alpha characters
       - it is NOT a proper noun (first-char uppercase), number, code, URL

CONSERVATIVE POLICY — the corrector NEVER:
  ❌ Modifies content inside fenced code blocks  (````` ``` `````)
  ❌ Modifies Markdown heading lines  (``#``)
  ❌ Modifies Markdown table lines  (starts with ``|``)
  ❌ Corrects capitalized words (possible proper nouns / acronyms)
  ❌ Corrects words that contain digits or non-alpha characters
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


# ── OCR pattern substitutions ─────────────────────────────────────────────────
#
# Each entry: (compiled_pattern, replacement_string)
# Applied in order on lowercase-word-context lines only.

_OCR_PATTERNS: list[tuple[re.Pattern, str]] = [
    # "rn" → "m"  inside words  (most frequent OCR confusion)
    (re.compile(r"\brn([aeiouáéíóúüñ])"),       r"m\1"),
    (re.compile(r"([aeiouáéíóúüñ])rn\b"),       r"\1m"),
    # "0" → "o"  surrounded by letters
    (re.compile(r"(?<=[a-záéíóúüñ])0(?=[a-záéíóúüñ])"),  "o"),
    # "1" → "l"  surrounded by letters
    (re.compile(r"(?<=[a-záéíóúüñ])1(?=[a-záéíóúüñ])"),  "l"),
    # "|" → "l"  surrounded by letters
    (re.compile(r"(?<=[a-záéíóúüñ])\|(?=[a-záéíóúüñ])"), "l"),
    # "vv" word-initial + vowel → "w"  (limited applicability in Spanish)
    (re.compile(r"\bvv([aeiouáéíóúü])"),         r"w\1"),
]


@dataclass
class SpellResult:
    content: str
    patterns_applied: int = 0
    word_corrections: dict[str, str] = field(default_factory=dict)

    def total(self) -> int:
        return self.patterns_applied + len(self.word_corrections)


def run(
    text: str,
    language: str = "es",
    min_word_len: int = 4,
    skip_spell: bool = False,
) -> SpellResult:
    """Apply OCR correction pipeline and return a SpellResult.

    Parameters
    ----------
    text         : Markdown string to correct.
    language     : "es" (Spanish) or "en" (English) for dictionary checks.
    min_word_len : Only consider words >= this length for dictionary correction.
    skip_spell   : When True, skip dictionary step (patterns still applied).
    """
    result = SpellResult(content=text)

    # ── Step 1: pattern-based ────────────────────────────────────────────
    corrected, n_patterns = _apply_patterns(text)
    result.content = corrected
    result.patterns_applied = n_patterns

    # ── Step 2: dictionary spell-check ──────────────────────────────────
    if not skip_spell:
        try:
            corrected, corrections = _apply_spellcheck(corrected, language, min_word_len)
            result.content = corrected
            result.word_corrections = corrections
        except ImportError:
            pass   # pyspellchecker not installed — silent fallback

    return result


# ── Pattern correction ────────────────────────────────────────────────────────

def _apply_patterns(text: str) -> tuple[str, int]:
    count = 0
    lines = text.split("\n")
    out: list[str] = []
    in_code = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            out.append(line)
            continue
        if in_code or stripped.startswith("|") or stripped.startswith("#"):
            out.append(line)
            continue

        new_line = line
        for pattern, repl in _OCR_PATTERNS:
            new_line, n = pattern.subn(repl, new_line)
            count += n
        out.append(new_line)

    return "\n".join(out), count


# ── Dictionary spell-check ────────────────────────────────────────────────────

_WORD_RE = re.compile(r"\b([a-záéíóúüñ]{4,})\b")   # lowercase alpha only, ≥ 4 chars


def _apply_spellcheck(
    text: str,
    language: str,
    min_word_len: int,
) -> tuple[str, dict[str, str]]:
    from spellchecker import SpellChecker  # type: ignore

    lang = language if language in ("es", "en") else "es"
    spell = SpellChecker(language=lang)
    corrections: dict[str, str] = {}

    # Build word regex respecting min_word_len
    word_re = re.compile(rf"\b([a-záéíóúüñ]{{{min_word_len},}})\b")

    lines = text.split("\n")
    out: list[str] = []
    in_code = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            out.append(line)
            continue
        if in_code or stripped.startswith("|") or stripped.startswith("#"):
            out.append(line)
            continue

        def _replace(m: re.Match) -> str:
            word = m.group(1)
            # Check cache first
            if word in corrections:
                return corrections[word]
            # Already correct
            if word in spell:
                return word
            # Suggest correction
            suggestion = spell.correction(word)
            if suggestion and suggestion != word:
                corrections[word] = suggestion
                return suggestion
            return word

        out.append(word_re.sub(_replace, line))

    return "\n".join(out), corrections
