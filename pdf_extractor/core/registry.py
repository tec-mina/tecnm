"""
core/registry.py — Auto-discovery registry for extraction strategies.

The registry scans ``pdf_extractor.features`` at first access and collects every
module that exports a ``STRATEGY`` (StrategyMeta) or ``STRATEGIES`` (list of
StrategyMeta) constant.  Each entry is indexed by its ``name`` AND by its
module short-name for backward compatibility with the ``--features`` CLI flag.

Usage
-----
    from pdf_extractor.core.registry import registry

    # List everything
    for meta in registry.list_all():
        print(meta)

    # Retrieve by strategy name  →  "ocr:tesseract-basic"
    # or by module short-name  →  "ocr_tesseract"
    meta = registry.get("ocr:tesseract-basic")
    meta = registry.get("ocr_tesseract")          # same object

    # All OCR strategies sorted by priority
    ocr = registry.list_tier("ocr")

    # Module path for dynamic import
    module_path = registry.module_for("ocr:tesseract-advanced")
    # → "pdf_extractor.features.ocr_tesseract"
"""

from __future__ import annotations

import importlib
import pkgutil
from dataclasses import dataclass

from ..features._protocol import StrategyMeta


@dataclass(frozen=True)
class RegistryFailure:
    module: str
    error_type: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {
            "module": self.module,
            "error_type": self.error_type,
            "message": self.message,
        }


class _Registry:
    """Thread-safe (GIL-protected) lazy registry."""

    def __init__(self) -> None:
        self._by_key: dict[str, StrategyMeta] = {}
        self._failures: list[RegistryFailure] = []
        self._discovered = False

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def register(self, meta: StrategyMeta) -> None:
        """Manually register a strategy (e.g. for tests)."""
        self._by_key[meta.name] = meta
        self._by_key.setdefault(meta.short_name, meta)

    def get(self, name: str) -> StrategyMeta | None:
        """Return strategy by name or module short-name, or None."""
        self._ensure_discovered()
        return self._by_key.get(name)

    def list_all(self) -> list[StrategyMeta]:
        """All strategies sorted by (tier, priority, name)."""
        self._ensure_discovered()
        seen: set[str] = set()
        unique: list[StrategyMeta] = []
        for meta in self._by_key.values():
            if meta.name not in seen:
                seen.add(meta.name)
                unique.append(meta)
        return sorted(unique, key=lambda m: (m.tier, m.priority, m.name))

    def list_tier(self, tier: str) -> list[StrategyMeta]:
        """Strategies for a single tier, sorted by priority."""
        return [m for m in self.list_all() if m.tier == tier]

    def module_for(self, name: str) -> str | None:
        """Return the importable module path for a strategy name, or None."""
        meta = self.get(name)
        return meta.module if meta else None

    def config_for(self, name: str) -> dict:
        """Return extra kwargs for extract() for a strategy, or {}."""
        meta = self.get(name)
        return meta.config if meta else {}

    def format_table(self) -> str:
        """Return a human-readable table of all strategies for --list-strategies."""
        lines = [
            f"{'NAME':<35} {'TIER':<10} {'PRI':>3}  {'DESCRIPTION'}",
            "-" * 80,
        ]
        for meta in self.list_all():
            flags = ""
            if meta.is_heavy:
                flags += " [heavy]"
            if meta.is_gpu_optional:
                flags += " [gpu?]"
            lines.append(
                f"{meta.name:<35} {meta.tier:<10} {meta.priority:>3}  "
                f"{meta.description}{flags}"
            )
        return "\n".join(lines)

    def discovery_failures(self) -> list[RegistryFailure]:
        """Return modules that failed during strategy discovery."""
        self._ensure_discovered()
        return list(self._failures)

    # ------------------------------------------------------------------ #
    # Auto-discovery
    # ------------------------------------------------------------------ #

    def _ensure_discovered(self) -> None:
        if not self._discovered:
            self._discover()
            self._discovered = True

    def _discover(self) -> None:
        """Scan pdf_extractor.features for modules with STRATEGY / STRATEGIES."""
        try:
            import pdf_extractor.features as features_pkg
        except ImportError:
            return

        self._failures.clear()

        for _finder, mod_name, _is_pkg in pkgutil.iter_modules(features_pkg.__path__):
            if mod_name.startswith("_"):
                continue
            full_module = f"pdf_extractor.features.{mod_name}"
            try:
                mod = importlib.import_module(full_module)
            except Exception as exc:
                self._record_failure(full_module, exc)
                continue

            self._collect_module_strategies(full_module, mod)

    def _collect_module_strategies(self, module_name: str, mod) -> None:
        try:
            # Single strategy
            if hasattr(mod, "STRATEGY"):
                meta = mod.STRATEGY
                if isinstance(meta, StrategyMeta):
                    self._index(meta)

            # Multiple strategies from the same module (e.g. basic + advanced)
            if hasattr(mod, "STRATEGIES"):
                for meta in mod.STRATEGIES:
                    if isinstance(meta, StrategyMeta):
                        self._index(meta)
        except Exception as exc:
            self._record_failure(module_name, exc)

    def _index(self, meta: StrategyMeta) -> None:
        self._by_key[meta.name] = meta
        # Backward-compat alias: "ocr_tesseract" → ocr:tesseract-basic, etc.
        self._by_key.setdefault(meta.short_name, meta)

    def _record_failure(self, module_name: str, exc: Exception) -> None:
        self._failures.append(
            RegistryFailure(
                module=module_name,
                error_type=type(exc).__name__,
                message=str(exc) or repr(exc),
            )
        )


# Module-level singleton
registry = _Registry()
