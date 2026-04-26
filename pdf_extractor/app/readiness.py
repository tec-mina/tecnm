"""
app/readiness.py — per-backend readiness checks and on-demand warmup.

A backend is considered:
  - "installed"     : its Python package(s) import cleanly AND its system
                      binary (if any) is on $PATH.
  - "initialized"   : its model files / runtime artifacts are already on disk
                      (so the first real request doesn't pay a download tax).
  - "ready"         : both of the above. This is what the UI cares about.

Used by:
  - CLI command  `python -m pdf_extractor warmup`   — build-time pre-download
  - CLI command  `python -m pdf_extractor readiness` — diagnostic table
  - REST endpoint /api/v1/readiness                  — UI status banner
  - REST endpoint /api/v1/readiness/download         — on-demand warmup
"""

from __future__ import annotations

import importlib
import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable


# ─────────────────────────────────────────────────────────────────────────────
# Data model
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class BackendStatus:
    name: str                              # e.g. "ocr:tesseract-basic" or "tika"
    label: str                             # human-readable
    installed: bool                        # python deps + system bins present
    initialized: bool                      # models/runtime artifacts on disk
    install_hint: str | None = None        # what to install if not installed
    init_hint: str | None = None           # what gets downloaded if not initialized
    last_error: str | None = None          # last failure encountered
    can_warmup: bool = True                # whether `download()` is supported

    @property
    def ready(self) -> bool:
        return self.installed and self.initialized

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "label": self.label,
            "installed": self.installed,
            "initialized": self.initialized,
            "ready": self.ready,
            "install_hint": self.install_hint,
            "init_hint": self.init_hint,
            "last_error": self.last_error,
            "can_warmup": self.can_warmup,
        }


@dataclass
class ReadinessReport:
    backends: list[BackendStatus] = field(default_factory=list)

    @property
    def all_ready(self) -> bool:
        """True only when every probed backend is fully ready.

        A backend that isn't installed counts as NOT ready — otherwise the UI
        would show a green check on a half-configured environment where most
        OCR / Tika options are silently going to fail.
        """
        return bool(self.backends) and all(b.ready for b in self.backends)

    def to_dict(self) -> dict:
        return {
            "all_ready": self.all_ready,
            "backends": [b.to_dict() for b in self.backends],
        }


# ─────────────────────────────────────────────────────────────────────────────
# Low-level checks
# ─────────────────────────────────────────────────────────────────────────────


def _python_available(package: str) -> tuple[bool, str | None]:
    try:
        importlib.import_module(package)
        return True, None
    except Exception as exc:  # ImportError, ModuleNotFoundError, …
        return False, f"{type(exc).__name__}: {exc}"


def _binary_available(name: str) -> bool:
    return shutil.which(name) is not None


# ─────────────────────────────────────────────────────────────────────────────
# Per-backend probes
#
# Each probe returns a BackendStatus. They never raise — failures are recorded
# in `last_error` so the UI can show a useful message.
# ─────────────────────────────────────────────────────────────────────────────


def _probe_pymupdf() -> BackendStatus:
    ok, err = _python_available("fitz")
    return BackendStatus(
        name="text:fast",
        label="Texto rápido (PyMuPDF)",
        installed=ok,
        initialized=ok,        # no model download required
        install_hint="pip install pymupdf",
        last_error=err,
        can_warmup=False,
    )


def _probe_pdfplumber() -> BackendStatus:
    ok, err = _python_available("pdfplumber")
    return BackendStatus(
        name="tables:pdfplumber",
        label="Tablas (pdfplumber)",
        installed=ok,
        initialized=ok,
        install_hint="pip install pdfplumber",
        last_error=err,
        can_warmup=False,
    )


def _probe_pdfminer() -> BackendStatus:
    ok, err = _python_available("pdfminer.high_level")
    return BackendStatus(
        name="text:pdfminer",
        label="Texto preciso (pdfminer.six)",
        installed=ok,
        initialized=ok,
        install_hint="pip install pdfminer.six",
        last_error=err,
        can_warmup=False,
    )


def _probe_tesseract() -> BackendStatus:
    py_ok, py_err = _python_available("pytesseract")
    bin_ok = _binary_available("tesseract")
    return BackendStatus(
        name="ocr:tesseract-basic",
        label="OCR Tesseract",
        installed=py_ok and bin_ok,
        initialized=py_ok and bin_ok,    # uses system tessdata, no per-user download
        install_hint=(
            "pip install pytesseract  +  apt-get install tesseract-ocr "
            "tesseract-ocr-spa tesseract-ocr-eng"
        ),
        last_error=py_err if not py_ok else (None if bin_ok else "tesseract binary not found on $PATH"),
        can_warmup=False,
    )


def _easyocr_model_dir() -> Path:
    return Path(os.environ.get("EASYOCR_MODULE_PATH", str(Path.home() / ".EasyOCR")))


def _probe_easyocr() -> BackendStatus:
    ok, err = _python_available("easyocr")
    if not ok:
        return BackendStatus(
            name="ocr:easyocr",
            label="OCR neuronal (EasyOCR)",
            installed=False,
            initialized=False,
            install_hint="pip install easyocr",
            init_hint="Descarga modelos ~64 MB en la primera ejecución",
            last_error=err,
        )
    model_dir = _easyocr_model_dir() / "model"
    has_models = model_dir.exists() and any(model_dir.iterdir())
    return BackendStatus(
        name="ocr:easyocr",
        label="OCR neuronal (EasyOCR)",
        installed=True,
        initialized=has_models,
        install_hint="pip install easyocr",
        init_hint="Descarga modelos (~64 MB) la primera vez",
    )


def _tika_jar_path() -> Path:
    # tika-python downloads to /tmp/tika-server-<hash>.jar by default.
    custom = os.environ.get("TIKA_PATH")
    return Path(custom) if custom else Path("/tmp")


def _probe_tika() -> BackendStatus:
    ok, err = _python_available("tika")
    if not ok:
        return BackendStatus(
            name="text:tika-java",
            label="Apache Tika (Java)",
            installed=False,
            initialized=False,
            install_hint="pip install tika  +  apt-get install default-jre-headless",
            init_hint="Descarga el JAR (~60 MB) la primera vez",
            last_error=err,
        )
    if not _binary_available("java"):
        return BackendStatus(
            name="text:tika-java",
            label="Apache Tika (Java)",
            installed=False,
            initialized=False,
            install_hint="apt-get install default-jre-headless",
            last_error="java binary not found on $PATH",
        )
    jar_dir = _tika_jar_path()
    has_jar = any(jar_dir.glob("tika-server*.jar"))
    return BackendStatus(
        name="text:tika-java",
        label="Apache Tika (Java)",
        installed=True,
        initialized=has_jar,
        init_hint="Descarga el JAR (~60 MB) la primera vez",
    )


def _probe_camelot() -> BackendStatus:
    ok, err = _python_available("camelot")
    bin_ok = _binary_available("gs") or _binary_available("ghostscript")
    return BackendStatus(
        name="tables:camelot",
        label="Tablas alta precisión (Camelot)",
        installed=ok and bin_ok,
        initialized=ok and bin_ok,
        install_hint="pip install camelot-py[cv]  +  apt-get install ghostscript",
        last_error=err if not ok else (None if bin_ok else "ghostscript not found on $PATH"),
        can_warmup=False,
    )


def _probe_tabula() -> BackendStatus:
    ok, err = _python_available("tabula")
    bin_ok = _binary_available("java")
    return BackendStatus(
        name="tables:tabula",
        label="Tablas Java (Tabula)",
        installed=ok and bin_ok,
        initialized=ok and bin_ok,
        install_hint="pip install tabula-py  +  apt-get install default-jre-headless",
        last_error=err if not ok else (None if bin_ok else "java binary not found on $PATH"),
        can_warmup=False,
    )


def _probe_markitdown() -> BackendStatus:
    ok, err = _python_available("markitdown")
    return BackendStatus(
        name="text:markitdown",
        label="MarkItDown (Microsoft)",
        installed=ok,
        initialized=ok,
        install_hint="pip install markitdown",
        last_error=err,
        can_warmup=False,
    )


def _probe_img2table() -> BackendStatus:
    ok, err = _python_available("img2table")
    return BackendStatus(
        name="tables:img2table",
        label="Tablas escaneadas (img2table)",
        installed=ok,
        initialized=ok,
        install_hint="pip install img2table",
        last_error=err,
        can_warmup=False,
    )


_PROBES: list[Callable[[], BackendStatus]] = [
    _probe_pymupdf,
    _probe_pdfminer,
    _probe_pdfplumber,
    _probe_markitdown,
    _probe_tesseract,
    _probe_easyocr,
    _probe_tika,
    _probe_camelot,
    _probe_tabula,
    _probe_img2table,
]


def collect_readiness() -> ReadinessReport:
    """Run every probe and return a ReadinessReport. Never raises."""
    report = ReadinessReport()
    for probe in _PROBES:
        try:
            report.backends.append(probe())
        except Exception as exc:  # defensive: a probe must not break the report
            report.backends.append(BackendStatus(
                name=getattr(probe, "__name__", "unknown"),
                label="probe failed",
                installed=False,
                initialized=False,
                last_error=f"{type(exc).__name__}: {exc}",
                can_warmup=False,
            ))
    return report


# ─────────────────────────────────────────────────────────────────────────────
# Warmup — actually downloads / initializes things
# ─────────────────────────────────────────────────────────────────────────────


def warmup_easyocr(languages: tuple[str, ...] = ("es", "en")) -> tuple[bool, str | None]:
    try:
        import easyocr  # type: ignore
    except ImportError as exc:
        return False, f"easyocr not installed: {exc}"
    try:
        # Constructing a Reader downloads model files to ~/.EasyOCR/model/.
        # gpu=False is intentional: build-time should not assume CUDA.
        easyocr.Reader(list(languages), gpu=False, download_enabled=True, verbose=False)
        return True, None
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def warmup_tika() -> tuple[bool, str | None]:
    try:
        from tika import parser as _tika_parser  # type: ignore
    except ImportError as exc:
        return False, f"tika not installed: {exc}"
    try:
        # First call downloads the JAR. Empty PDF is enough to trigger it.
        _tika_parser.from_buffer(b"%PDF-1.4\n%%EOF\n")
        return True, None
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def warmup_registry() -> tuple[bool, list[dict]]:
    """Force feature discovery; return (ok, failures)."""
    from ..core.registry import registry
    registry.list_all()
    failures = [f.to_dict() for f in registry.discovery_failures()]
    return (len(failures) == 0), failures


def run_full_warmup(
    *,
    languages: tuple[str, ...] = ("es", "en"),
    skip_on_error: bool = False,
    on_step: Callable[[str, bool, str | None], None] | None = None,
) -> bool:
    """Run every warmup step. Returns True if all succeeded.

    `on_step(label, ok, error)` is invoked after each step for progress reporting.
    `skip_on_error=True` is the build-time default — a failed download (e.g. no
    egress) shouldn't break the image build, the runtime probes will report it.
    """
    def _step(label: str, fn: Callable[[], tuple[bool, object]]) -> bool:
        ok, err = fn()
        if on_step:
            on_step(label, ok, err if isinstance(err, str) else (None if ok else str(err)))
        return ok

    overall = True
    overall &= _step("registry", lambda: warmup_registry())
    overall &= _step("easyocr", lambda: warmup_easyocr(languages))
    overall &= _step("tika", lambda: warmup_tika())

    if not overall and not skip_on_error:
        return False
    return overall or skip_on_error
