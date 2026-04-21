"""
features/_protocol.py — Strategy Protocol and metadata for all extraction backends.

Each feature module SHOULD export a STRATEGY (and optionally STRATEGIES for variants)
constant of type StrategyMeta.  The registry uses these for named-strategy lookup.

Naming convention:  <tier>:<name>
  Tiers   : text | ocr | tables | images | fonts | layout | correct
  Examples: ocr:tesseract-basic, ocr:tesseract-advanced, tables:pdfplumber,
            text:llm, images:extract, fonts:analyze, correct:spell

Pipeline backward-compat: short module names ("ocr_tesseract", "tables", …)
still work — the registry also registers them under their module short-name.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class StrategyMeta:
    """Metadata for a named extraction strategy.

    Attributes
    ----------
    name            Unique strategy ID used on the CLI: ``ocr:tesseract-basic``
    tier            Category: text | ocr | tables | images | fonts | layout | correct
    description     Human-readable description shown by --list-strategies
    module          Full Python module path: ``pdf_extractor.features.ocr_tesseract``
    requires_system System-level executables needed (checked at runtime)
    requires_python  Python packages needed (informational; import errors are caught)
    config          Extra keyword arguments forwarded to the module's extract() call
    priority        Auto-selection preference: lower = tried first within the same tier
    is_heavy        True for backends that download large ML models (> 500 MB)
    is_gpu_optional True for backends that benefit from a GPU but don't require one
    """

    name: str
    tier: str
    description: str
    module: str
    requires_system: list[str] = field(default_factory=list)
    requires_python: list[str] = field(default_factory=list)
    config: dict = field(default_factory=dict)
    priority: int = 50
    is_heavy: bool = False
    is_gpu_optional: bool = False

    # ------------------------------------------------------------------ #
    # Convenience helpers
    # ------------------------------------------------------------------ #

    @property
    def short_name(self) -> str:
        """Module short-name derived from the module path (last segment)."""
        return self.module.rsplit(".", 1)[-1]

    def __str__(self) -> str:
        heavy = " [heavy]" if self.is_heavy else ""
        gpu = " [gpu-optional]" if self.is_gpu_optional else ""
        return f"{self.name}{heavy}{gpu} — {self.description}"
