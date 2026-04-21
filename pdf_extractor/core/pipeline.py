"""
core/pipeline.py — Orchestrator: auto-selects strategies, runs them, merges output.

Decision tree:
  text_native, no tables   → markdown_llm (if available), else text_fast
  text_native, has_tables  → text_fast + tables (pdfplumber → camelot → tabula fallback)
  scanned                  → ocr_tesseract → ocr_easy → ocr_img2table
  mixed                    → text_fast on text pages + ocr_tesseract on scanned pages
  complex layout           → docling_feat OR markitdown_feat

Override with --features / --strategy flag.

Strategy names (new) and module short-names (legacy) are both accepted.
The registry resolves strategy names → module paths automatically.
"""

from __future__ import annotations

import importlib
import sys
import time
from dataclasses import dataclass, field
from typing import Any

from . import progress as prog
from .detector import PDFProfile
from .preflight import PreflightResult
from .platform import PlatformInfo
from .registry import registry
from ..output import assembler as asm


# Ordered fallback chains (module short-names — backward compat)
_TABLE_CHAIN = ["tables", "tables_camelot", "tables_tabula"]
_OCR_CHAIN = ["ocr_tesseract", "ocr_easy"]


@dataclass
class PipelineResult:
    features_used: list[str] = field(default_factory=list)
    plan: Any = None                    # asm.AssemblyPlan — built incrementally
    warnings: list[str] = field(default_factory=list)
    extraction_time_sec: float = 0.0
    used_ocr: bool = False              # True when any OCR feature ran successfully


def run(
    pdf_path: str,
    preflight: PreflightResult,
    profile: PDFProfile,
    platform: PlatformInfo,
    page_range: tuple[int, int] | None = None,
    forced_features: list[str] | None = None,
    with_images: bool = False,
    table_appendix: bool = True,
) -> PipelineResult:
    """Select features/strategies, run them one by one, stream results into AssemblyPlan.

    Each FeatureResult is merged into the plan immediately after extraction
    and then discarded — only the assembled page dicts are kept in memory.
    """
    t0 = time.monotonic()
    result = PipelineResult()
    result.plan = asm.make_plan(preflight.page_count)

    feature_names = (
        forced_features if forced_features
        else _select_features(preflight, profile, platform)
    )

    # Append image extraction when requested
    if with_images and "images_extract" not in feature_names:
        feature_names = list(feature_names) + ["images_extract"]

    for name in feature_names:
        fr = _run_feature(pdf_path, name, page_range, pdf_path)
        if fr is None:
            continue
        asm.merge_feature(result.plan, fr)   # absorb into plan
        result.features_used.append(name)
        result.warnings.extend(fr.warnings)
        if name in ("ocr_tesseract", "ocr_easy", "ocr:tesseract-basic",
                    "ocr:tesseract-advanced", "ocr:easyocr") and fr.confidence > 0:
            result.used_ocr = True
        del fr                               # free FeatureResult immediately

    result.extraction_time_sec = time.monotonic() - t0
    return result


# ---------------------------------------------------------------------------
# Auto-selection
# ---------------------------------------------------------------------------

def select_features(
    preflight: PreflightResult,
    profile: PDFProfile,
    platform: PlatformInfo,
    forced: list[str] | None = None,
) -> list[str]:
    """Public wrapper — returns the list of features the pipeline would choose."""
    return forced if forced else _select_features(preflight, profile, platform)


def _select_features(
    preflight: PreflightResult,
    profile: PDFProfile,
    platform: PlatformInfo,
) -> list[str]:
    """Apply decision tree from spec."""

    all_scanned = bool(profile.scanned_pages) and not profile.text_native_pages
    all_text = bool(profile.text_native_pages) and not profile.scanned_pages
    mixed = bool(profile.text_native_pages) and bool(profile.scanned_pages)
    has_tables = bool(profile.table_pages)

    features: list[str] = []

    if all_scanned:
        features = ["ocr_tesseract", "ocr_easy"]
        if has_tables:
            features.append("ocr_img2table")

    elif mixed:
        features = ["text_fast", "ocr_tesseract"]
        if has_tables:
            features.extend(_TABLE_CHAIN)

    elif all_text:
        if has_tables:
            features = ["text_fast"] + _TABLE_CHAIN
        else:
            features = ["markdown_llm", "text_fast"]  # markdown_llm attempted first; text_fast fallback
    else:
        # Unknown / default
        features = ["text_fast"] + _TABLE_CHAIN

    # Platform overrides
    if platform.os == "macos":
        # Prefer pymupdf4llm + pdfplumber on macOS; no camelot issues
        pass
    elif platform.os == "windows":
        # markitdown preferred; swap in if not already present
        if "markitdown_feat" not in features:
            features = ["markitdown_feat"] + features
        # Remove heavy OCR backends if not on GPU
        if "ocr_easy" in features and "ocr_easy" in platform.skip_features:
            features.remove("ocr_easy")

    return features


# ---------------------------------------------------------------------------
# Feature runner — resolves both strategy names and module short-names
# ---------------------------------------------------------------------------

def _run_feature(pdf_path: str, name: str, page_range, file_label: str):
    """Import and run a single feature module. Returns FeatureResult or None.

    Accepts:
      - Strategy names:    "ocr:tesseract-basic", "tables:pdfplumber", …
      - Module short-names: "ocr_tesseract", "tables", …  (legacy / backward compat)
    """
    # Resolve via registry first
    meta = registry.get(name)
    if meta:
        module_path = meta.module
        extra_kwargs = meta.config   # e.g. {"preprocess": True, "dpi": 400}
    else:
        # Fallback: treat name as module short-name
        module_path = f"pdf_extractor.features.{name}"
        extra_kwargs = {}

    try:
        mod = importlib.import_module(module_path)
    except ImportError as exc:
        prog.feature_skipped(file_label, name, f"module import failed: {exc}")
        return None

    prog.feature_running(file_label, name)

    try:
        fr = mod.extract(pdf_path, page_range, **extra_kwargs)
    except TypeError:
        # Module's extract() doesn't accept extra kwargs — call without them
        try:
            fr = mod.extract(pdf_path, page_range)
        except Exception as exc:
            prog.error(file_label, str(exc), feature=name)
            return None
    except Exception as exc:
        prog.error(file_label, str(exc), feature=name)
        return None

    prog.feature_done(file_label, name, fr.confidence)
    return fr


# ---------------------------------------------------------------------------
# Dry-run plan
# ---------------------------------------------------------------------------

def dry_run_plan(
    preflight: PreflightResult,
    profile: PDFProfile,
    platform: PlatformInfo,
    forced_features: list[str] | None = None,
) -> dict[str, Any]:
    features = forced_features or _select_features(preflight, profile, platform)
    return {
        "file": preflight.path,
        "page_count": preflight.page_count,
        "is_scanned": preflight.is_scanned,
        "profile": profile.to_dict(),
        "planned_features": features,
        "platform": platform.os,
    }
