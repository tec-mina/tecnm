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
    # Both detection (craft_mlt_25k.pth) AND recognition (latin_g2.pth) must be present.
    # Checking only `any(iterdir())` was returning True when only craft was downloaded.
    detection_ok = (model_dir / "craft_mlt_25k.pth").exists()
    recognition_ok = (model_dir / "latin_g2.pth").exists()
    has_models = detection_ok and recognition_ok
    return BackendStatus(
        name="ocr:easyocr",
        label="OCR neuronal (EasyOCR)",
        installed=True,
        initialized=has_models,
        install_hint="pip install easyocr",
        init_hint="Requiere craft_mlt_25k.pth + latin_g2.pth en ~/.EasyOCR/model/",
        last_error=(
            None if has_models
            else "Faltan modelos: " + (
                "craft_mlt_25k.pth" if not detection_ok else "latin_g2.pth"
            )
        ),
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


def _probe_tesseract_advanced() -> BackendStatus:
    """ocr:tesseract-advanced — same binary deps as basic, but also uses numpy/cv2."""
    py_ok, py_err = _python_available("pytesseract")
    bin_ok = _binary_available("tesseract")
    installed = py_ok and bin_ok
    return BackendStatus(
        name="ocr:tesseract-advanced",
        label="OCR Tesseract avanzado (preprocesado + rotación automática)",
        installed=installed,
        initialized=installed,
        install_hint=(
            "pip install pytesseract  +  apt-get install tesseract-ocr "
            "tesseract-ocr-spa tesseract-ocr-eng"
        ),
        last_error=py_err if not py_ok else (None if bin_ok else "tesseract binary not found on $PATH"),
        can_warmup=False,
    )


def _probe_images_extract() -> BackendStatus:
    """images:extract — depends only on PyMuPDF (fitz), always available."""
    ok, err = _python_available("fitz")
    return BackendStatus(
        name="images:extract",
        label="Extraer imágenes embebidas (PyMuPDF)",
        installed=ok,
        initialized=ok,
        install_hint="pip install pymupdf",
        last_error=err,
        can_warmup=False,
    )


def _probe_layout_structure() -> BackendStatus:
    """layout:structure — depends only on PyMuPDF (fitz), always available."""
    ok, err = _python_available("fitz")
    return BackendStatus(
        name="layout:structure",
        label="Estructura: marcadores, índice, formularios, vínculos (PyMuPDF)",
        installed=ok,
        initialized=ok,
        install_hint="pip install pymupdf",
        last_error=err,
        can_warmup=False,
    )


def _probe_fonts_analyze() -> BackendStatus:
    """fonts:analyze — depends only on PyMuPDF (fitz), always available."""
    ok, err = _python_available("fitz")
    return BackendStatus(
        name="fonts:analyze",
        label="Análisis de fuentes y detección de encabezados (PyMuPDF)",
        installed=ok,
        initialized=ok,
        install_hint="pip install pymupdf",
        last_error=err,
        can_warmup=False,
    )


_PROBES: list[Callable[[], BackendStatus]] = [
    _probe_pymupdf,
    _probe_pdfminer,
    _probe_pdfplumber,
    _probe_markitdown,
    _probe_tesseract,
    _probe_tesseract_advanced,
    _probe_easyocr,
    _probe_tika,
    _probe_camelot,
    _probe_tabula,
    _probe_img2table,
    _probe_images_extract,
    _probe_layout_structure,
    _probe_fonts_analyze,
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


def warmup_pymupdf() -> tuple[bool, str | None]:
    try:
        import fitz  # type: ignore  # noqa: F401
    except ImportError as exc:
        return False, f"pymupdf not installed: {exc}"
    try:
        doc = fitz.Document()
        doc.new_page(width=100, height=100)
        buf = doc.tobytes()
        doc2 = fitz.open(stream=buf, filetype="pdf")
        _ = doc2[0].get_text()
        _ = doc2[0].get_pixmap(dpi=72)
        doc2.close()
        return True, None
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def warmup_pdfminer() -> tuple[bool, str | None]:
    try:
        import io
        import fitz  # type: ignore
        from pdfminer.high_level import extract_text  # type: ignore
    except ImportError as exc:
        return False, f"dependency not installed: {exc}"
    try:
        doc = fitz.Document()
        doc.new_page(width=100, height=100)
        buf = io.BytesIO(doc.tobytes())
        _ = extract_text(buf)
        return True, None
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def warmup_pdfplumber() -> tuple[bool, str | None]:
    try:
        import io
        import fitz  # type: ignore
        import pdfplumber  # type: ignore
    except ImportError as exc:
        return False, f"dependency not installed: {exc}"
    try:
        doc = fitz.Document()
        doc.new_page(width=100, height=100)
        buf = io.BytesIO(doc.tobytes())
        with pdfplumber.open(buf) as pdf:
            _ = pdf.pages[0].extract_text()
        return True, None
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def warmup_markitdown() -> tuple[bool, str | None]:
    try:
        from markitdown import MarkItDown  # type: ignore
    except ImportError as exc:
        return False, f"markitdown not installed: {exc}"
    try:
        _ = MarkItDown()
        return True, None
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def warmup_tesseract() -> tuple[bool, str | None]:
    try:
        import numpy as np
        import pytesseract  # type: ignore
    except ImportError as exc:
        return False, f"dependency not installed: {exc}"
    try:
        # Blank white image — verifies tessdata (spa+eng) loads correctly.
        img = np.ones((50, 200, 3), dtype=np.uint8) * 255
        pytesseract.image_to_string(img, lang="spa+eng")
        return True, None
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def warmup_camelot() -> tuple[bool, str | None]:
    try:
        import camelot  # type: ignore  # noqa: F401
    except ImportError as exc:
        return False, f"camelot not installed: {exc}"
    if not _binary_available("gs") and not _binary_available("ghostscript"):
        return False, "ghostscript not found on $PATH"
    return True, None


def warmup_tabula() -> tuple[bool, str | None]:
    try:
        import tabula  # type: ignore  # noqa: F401
    except ImportError as exc:
        return False, f"tabula not installed: {exc}"
    if not _binary_available("java"):
        return False, "java not found on $PATH"
    return True, None


def warmup_img2table() -> tuple[bool, str | None]:
    try:
        import img2table  # type: ignore  # noqa: F401
    except ImportError as exc:
        return False, f"img2table not installed: {exc}"
    return True, None


def warmup_tesseract_advanced() -> tuple[bool, str | None]:
    """Same binary as basic; additionally verify numpy is available for preprocessing."""
    ok, err = warmup_tesseract()
    if not ok:
        return ok, err
    try:
        import numpy as np  # type: ignore  # noqa: F401
    except ImportError as exc:
        return False, f"numpy not installed (required for preprocessing): {exc}"
    return True, None


def warmup_images_extract() -> tuple[bool, str | None]:
    try:
        import fitz  # type: ignore  # noqa: F401
    except ImportError as exc:
        return False, f"pymupdf not installed: {exc}"
    return True, None


def warmup_layout_structure() -> tuple[bool, str | None]:
    try:
        import fitz  # type: ignore  # noqa: F401
    except ImportError as exc:
        return False, f"pymupdf not installed: {exc}"
    return True, None


def warmup_fonts_analyze() -> tuple[bool, str | None]:
    try:
        import fitz  # type: ignore  # noqa: F401
    except ImportError as exc:
        return False, f"pymupdf not installed: {exc}"
    return True, None


def warmup_easyocr(languages: tuple[str, ...] = ("es", "en")) -> tuple[bool, str | None]:
    try:
        import numpy as np  # type: ignore
        import easyocr  # type: ignore
    except ImportError as exc:
        return False, f"easyocr not installed: {exc}"
    try:
        # Constructing a Reader downloads the detection model (craft_mlt_25k.pth).
        # Calling readtext() triggers the recognition model download (latin_g2.pth).
        # Both must succeed for easyocr to actually work on real PDFs.
        reader = easyocr.Reader(list(languages), gpu=False, download_enabled=True, verbose=False)
        reader.readtext(np.zeros((32, 200, 3), dtype=np.uint8))
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


# Map of backend.name → warmup function. Used by:
#   - retry_missing()                 — runtime self-heal
#   - /api/v1/readiness/download      — on-demand UI button
# Add an entry here for every backend that supports warmup.
WARMUP_BY_NAME: dict[str, Callable[[], tuple[bool, str | None]]] = {
    "text:fast":               warmup_pymupdf,
    "text:pdfminer":           warmup_pdfminer,
    "tables:pdfplumber":       warmup_pdfplumber,
    "text:markitdown":         warmup_markitdown,
    "ocr:tesseract-basic":     warmup_tesseract,
    "ocr:tesseract-advanced":  warmup_tesseract_advanced,
    "ocr:easyocr":             lambda: warmup_easyocr(),
    "text:tika-java":          warmup_tika,
    "tables:camelot":          warmup_camelot,
    "tables:tabula":           warmup_tabula,
    "tables:img2table":        warmup_img2table,
    "images:extract":          warmup_images_extract,
    "layout:structure":        warmup_layout_structure,
    "fonts:analyze":           warmup_fonts_analyze,
}


def retry_missing(
    only: list[str] | None = None,
    on_step: Callable[[str, bool, str | None], None] | None = None,
) -> tuple[bool, list[dict]]:
    """Re-warm only backends that report installed && !initialized.

    Used at container startup so a build that ran with --skip-on-error (typical
    when the build host had no egress) still self-heals on first boot.

    Parameters
    ----------
    only :  optional list of backend names; restricts the retry to those.
    on_step : per-backend progress callback (label, ok, error).

    Returns (all_ready_after_retry, results) where each result is
        {"name": str, "attempted": bool, "ok": bool, "error": str|None}.
    """
    report = collect_readiness()
    pending = [
        b for b in report.backends
        if not b.ready and b.can_warmup and (only is None or b.name in only)
    ]
    results: list[dict] = []
    for b in pending:
        fn = WARMUP_BY_NAME.get(b.name)
        if fn is None:
            results.append({
                "name": b.name, "attempted": False, "ok": False,
                "error": "no warmup function registered",
            })
            if on_step:
                on_step(b.name, False, "no warmup function registered")
            continue
        try:
            ok, err = fn()
        except Exception as exc:  # pragma: no cover — defensive
            ok, err = False, f"{type(exc).__name__}: {exc}"
        results.append({"name": b.name, "attempted": True, "ok": ok, "error": err})
        if on_step:
            on_step(b.name, ok, err)
    final = collect_readiness()
    return final.all_ready, results


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
    overall &= _step("registry",                lambda: warmup_registry())
    overall &= _step("text:fast",               lambda: warmup_pymupdf())
    overall &= _step("text:pdfminer",           lambda: warmup_pdfminer())
    overall &= _step("tables:pdfplumber",       lambda: warmup_pdfplumber())
    overall &= _step("text:markitdown",         lambda: warmup_markitdown())
    overall &= _step("ocr:tesseract-basic",     lambda: warmup_tesseract())
    overall &= _step("ocr:tesseract-advanced",  lambda: warmup_tesseract_advanced())
    overall &= _step("ocr:easyocr",             lambda: warmup_easyocr(languages))
    overall &= _step("text:tika",               lambda: warmup_tika())
    overall &= _step("tables:camelot",          lambda: warmup_camelot())
    overall &= _step("tables:tabula",           lambda: warmup_tabula())
    overall &= _step("tables:img2table",        lambda: warmup_img2table())
    overall &= _step("images:extract",          lambda: warmup_images_extract())
    overall &= _step("layout:structure",        lambda: warmup_layout_structure())
    overall &= _step("fonts:analyze",           lambda: warmup_fonts_analyze())

    if not overall and not skip_on_error:
        return False
    return overall or skip_on_error
