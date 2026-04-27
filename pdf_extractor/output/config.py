"""
output/config.py — Central configuration for all output assembly behaviour.

Load once at startup via OutputConfig.load(path); pass the instance to
assembler, fixer, validator, and frontmatter.  Missing YAML sections fall
back to safe defaults so the system works without any config file present.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Sub-sections
# ---------------------------------------------------------------------------

@dataclass
class StructureConfig:
    heading_normalize: bool = True
    heading_placeholder: str = "—"
    min_headings_for_toc: int = 3
    toc_label: str = "Contenido"
    toc_heading_level: int = 2
    page_markers: bool = True
    page_marker_format: str = "<!-- Page {n} -->"


@dataclass
class TablesConfig:
    null_replacement: str = "—"
    min_columns: int = 2
    min_rows: int = 2
    trim_whitespace: bool = True
    appendix: bool = True
    appendix_label: str = "Tablas Auxiliares"


@dataclass
class ImagesConfig:
    enabled: bool = False
    dir: str = "images"
    alt_text_fallback: str = "Imagen extraída"


@dataclass
class FrontmatterConfig:
    enabled: bool = True
    fields: list[str] = field(default_factory=lambda: [
        "source", "pages", "file_size_mb", "extraction_date", "language",
        "tables_found", "has_images", "has_scanned_pages", "features_used",
        "extraction_time_sec", "quality_score", "quality_label",
        "is_valid", "from_cache", "warnings",
    ])
    custom_fields: dict[str, Any] = field(default_factory=dict)


@dataclass
class OcrPattern:
    pattern: str
    replacement: str

    def compiled(self) -> re.Pattern:
        return re.compile(self.pattern)


@dataclass
class SymbolsConfig:
    ligatures: dict[str, str] = field(default_factory=lambda: {
        "ﬀ": "ff",
        "ﬁ": "fi",
        "ﬂ": "fl",
        "ﬃ": "ffi",
        "ﬄ": "ffl",
        "ﬅ": "st",
        "ﬆ": "st",
    })
    replacements: dict[str, str] = field(default_factory=lambda: {
        " ": " ",   # non-breaking space
    })
    ocr_patterns: list[OcrPattern] = field(default_factory=list)


@dataclass
class SpellConfig:
    enabled: bool = False
    language: str = "es"
    min_word_length: int = 4
    skip_headings: bool = True
    skip_tables: bool = True
    skip_code_blocks: bool = True
    custom_dictionary: list[str] = field(default_factory=list)


@dataclass
class OutputFormatConfig:
    line_endings: str = "lf"          # "lf" | "crlf"
    normalize_spaces: bool = True
    normalize_lists: bool = True
    rejoin_hyphenated_words: bool = True
    min_word_length_for_rejoin: int = 3


@dataclass
class ValidatorConfig:
    overlong_line_chars: int = 180
    repeated_line_min: int = 3
    empty_threshold: int = 50
    sparse_page_chars: int = 30
    sparse_page_ratio: float = 0.6


# ---------------------------------------------------------------------------
# Root config
# ---------------------------------------------------------------------------

@dataclass
class OutputConfig:
    structure: StructureConfig = field(default_factory=StructureConfig)
    tables: TablesConfig = field(default_factory=TablesConfig)
    images: ImagesConfig = field(default_factory=ImagesConfig)
    frontmatter: FrontmatterConfig = field(default_factory=FrontmatterConfig)
    symbols: SymbolsConfig = field(default_factory=SymbolsConfig)
    spell: SpellConfig = field(default_factory=SpellConfig)
    output: OutputFormatConfig = field(default_factory=OutputFormatConfig)
    validator: ValidatorConfig = field(default_factory=ValidatorConfig)

    # ------------------------------------------------------------------
    @classmethod
    def load(cls, path: str | Path | None = None) -> "OutputConfig":
        """Load from a YAML file.  Missing file → safe defaults.  Missing
        YAML keys → per-field defaults.  Never raises for missing config."""
        cfg = cls()
        if path is None:
            return cfg

        p = Path(path)
        if not p.exists():
            return cfg

        try:
            import yaml  # PyYAML — optional dependency
        except ImportError:
            return cfg

        try:
            raw: dict = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        except Exception:
            return cfg

        _apply(cfg.structure, raw.get("structure", {}))
        _apply(cfg.tables, raw.get("tables", {}))
        _apply(cfg.images, raw.get("images", {}))
        _apply(cfg.output, raw.get("output", {}))
        _apply(cfg.validator, raw.get("validator", {}))
        _apply_spell(cfg.spell, raw.get("spell", {}))
        _apply_frontmatter(cfg.frontmatter, raw.get("frontmatter", {}))
        _apply_symbols(cfg.symbols, raw.get("symbols", {}))

        return cfg

    @classmethod
    def default(cls) -> "OutputConfig":
        return cls()


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _apply(obj: Any, data: dict) -> None:
    """Overwrite dataclass fields from dict, ignoring unknown keys."""
    if not isinstance(data, dict):
        return
    for key, val in data.items():
        if hasattr(obj, key):
            setattr(obj, key, val)


def _apply_spell(cfg: SpellConfig, data: dict) -> None:
    _apply(cfg, data)
    if "custom_dictionary" in data and isinstance(data["custom_dictionary"], list):
        cfg.custom_dictionary = [str(w) for w in data["custom_dictionary"]]


def _apply_frontmatter(cfg: FrontmatterConfig, data: dict) -> None:
    _apply(cfg, data)
    if "fields" in data and isinstance(data["fields"], list):
        cfg.fields = [str(f) for f in data["fields"]]
    if "custom_fields" in data and isinstance(data["custom_fields"], dict):
        cfg.custom_fields = dict(data["custom_fields"])


def _apply_symbols(cfg: SymbolsConfig, data: dict) -> None:
    if not isinstance(data, dict):
        return
    if "ligatures" in data and isinstance(data["ligatures"], dict):
        cfg.ligatures = dict(data["ligatures"])
    if "replacements" in data and isinstance(data["replacements"], dict):
        cfg.replacements = dict(data["replacements"])
    if "ocr_patterns" in data and isinstance(data["ocr_patterns"], list):
        cfg.ocr_patterns = []
        for entry in data["ocr_patterns"]:
            if isinstance(entry, dict) and "pattern" in entry and "replacement" in entry:
                cfg.ocr_patterns.append(
                    OcrPattern(pattern=entry["pattern"], replacement=entry["replacement"])
                )
