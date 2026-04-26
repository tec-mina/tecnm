"""
interfaces/api.py — FastAPI REST interface for PDF Extractor.

Design: stateless, synchronous request-response.
Upload PDF → receive Markdown. No job IDs, no polling, no disk persistence.

Endpoints
---------
GET  /healthz                  — liveness probe (Cloud Run)
GET  /api/v1/capabilities      — system tool & package inventory
GET  /api/v1/strategies        — registered extraction strategies
POST /api/v1/inspect           — profile a PDF (returns JSON)
POST /api/v1/extract           — extract one PDF → download .md
POST /api/v1/batch             — extract multiple PDFs → download .zip

POST /api/v1/extract
  Content-Type: multipart/form-data
  Fields:
    file            required  PDF file (binary)
    strategies      optional  comma-separated strategy names
                              e.g. "text:fast,tables:pdfplumber"
    page_range      optional  "1-10"
    with_images     optional  "true" / "false"  (default false)
    with_structure  optional  "true" / "false"  (default false)
    no_spell        optional  "true" / "false"  (default false)

  Response 200:
    Content-Type: text/markdown; charset=utf-8
    Content-Disposition: attachment; filename="<original_stem>.md"
    X-Quality-Score: float       0–100
    X-Pages: int
    X-Elapsed-Sec: float
    X-Features-Used: str         comma-separated strategy names used

POST /api/v1/batch
  Same form fields but "files" (multiple) instead of "file".

  Response 200:
    Content-Type: application/zip
    Content-Disposition: attachment; filename="extracted.zip"
    ZIP contents:
      <stem>.md          one per input file (errors are skipped)
      _summary.json      per-file quality scores, pages, elapsed, errors

Authentication
--------------
None by default. Set API_KEY env var to require
  Authorization: Bearer <token>  on all /api/* routes.

Error responses
---------------
All errors:
    {"error": str, "detail": str | null}
"""

from __future__ import annotations

import asyncio
import io
import json
import os
import shutil
import uuid
import zipfile
from pathlib import Path
from typing import Any

from fastapi import BackgroundTasks, Depends, FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

_WEB_HTML_PATH = Path(__file__).with_name("web.html")

# ── App factory ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="PDF Extractor API",
    description=(
        "Stateless PDF → Markdown extraction service. "
        "Upload a PDF, receive the extracted Markdown. No accounts, no storage."
    ),
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Config ────────────────────────────────────────────────────────────────────

_TMP_DIR = Path(os.environ.get("TMP_DIR", "/tmp/pdf-extractor"))
_MAX_UPLOAD_MB = int(os.environ.get("MAX_UPLOAD_MB", "200"))
_API_KEY: str | None = os.environ.get("API_KEY")
# Cap a single extraction's wall-clock so a pathological PDF can't tie up an
# instance for the full Cloud Run request timeout.
_EXTRACTION_TIMEOUT_SEC = int(os.environ.get("EXTRACTION_TIMEOUT_SEC", "300"))
# Global cap on concurrent extractions per process. Prevents a thundering herd
# of /extract calls from pegging memory and exhausting the default ThreadPool.
_MAX_CONCURRENT_EXTRACTIONS = int(os.environ.get("EXTRACTOR_WORKERS", "4"))
# Inspect is lighter than extraction but still reads the entire PDF into RAM.
# A separate, smaller semaphore keeps inspect calls from competing with extract.
_MAX_CONCURRENT_INSPECTS = int(os.environ.get("INSPECT_WORKERS", "2"))
_INSPECT_TIMEOUT_SEC = int(os.environ.get("INSPECT_TIMEOUT_SEC", "60"))

_TMP_DIR.mkdir(parents=True, exist_ok=True)

# Created lazily on first use so it binds to the running event loop, not to
# import time (asyncio.Semaphore stores a reference to the current loop).
_extraction_sem: asyncio.Semaphore | None = None
_inspect_sem: asyncio.Semaphore | None = None


def _get_extraction_sem() -> asyncio.Semaphore:
    global _extraction_sem
    if _extraction_sem is None:
        _extraction_sem = asyncio.Semaphore(_MAX_CONCURRENT_EXTRACTIONS)
    return _extraction_sem


def _get_inspect_sem() -> asyncio.Semaphore:
    global _inspect_sem
    if _inspect_sem is None:
        _inspect_sem = asyncio.Semaphore(_MAX_CONCURRENT_INSPECTS)
    return _inspect_sem


def _get_memory_info() -> dict[str, int | None]:
    """Best-effort memory stats from cgroup limits and /proc/meminfo.

    Works inside Docker with both cgroup v1 and v2. Returns MB values or None
    if the file isn't accessible (e.g. macOS dev environment).
    """
    limit_mb: int | None = None
    available_mb: int | None = None

    # cgroup v2 (Docker Desktop >= 4.x on Linux)
    try:
        raw = Path("/sys/fs/cgroup/memory.max").read_text().strip()
        if raw != "max":
            limit_mb = int(raw) // (1024 * 1024)
    except Exception:
        pass

    # cgroup v1 fallback
    if limit_mb is None:
        try:
            raw_v1 = int(Path("/sys/fs/cgroup/memory/memory.limit_in_bytes").read_text().strip())
            if raw_v1 < (1 << 62):  # 0x4000… means "no limit" in cgroupv1
                limit_mb = raw_v1 // (1024 * 1024)
        except Exception:
            pass

    # /proc/meminfo → MemAvailable (Linux inside container)
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemAvailable:"):
                available_mb = int(line.split()[1]) // 1024
                break
    except Exception:
        pass

    # Fallback: sysconf total physical pages (macOS / non-Linux)
    if limit_mb is None:
        try:
            limit_mb = (os.sysconf("SC_PHYS_PAGES") * os.sysconf("SC_PAGE_SIZE")) // (1024 * 1024)
        except Exception:
            pass

    return {"limit_mb": limit_mb, "available_mb": available_mb}


async def _run_extraction_guarded(
    pdf_path: Path, out_dir: Path, options: dict[str, Any]
) -> Any:
    """Run extraction in the threadpool, guarded by the global semaphore and
    a hard wall-clock timeout. Translates timeouts to HTTP 504.

    Note: asyncio.wait_for cancels the *awaitable*, not the OS thread running
    extract(). The thread continues until the underlying library yields. On
    Cloud Run this is acceptable because the instance is recycled on request
    timeout; for long-lived deployments consider switching to a process pool.
    """
    loop = asyncio.get_running_loop()
    sem = _get_extraction_sem()
    async with sem:
        try:
            return await asyncio.wait_for(
                loop.run_in_executor(None, _run_sync_extraction, pdf_path, out_dir, options),
                timeout=_EXTRACTION_TIMEOUT_SEC,
            )
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=504,
                detail={
                    "error": "extraction_timeout",
                    "message": (
                        f"La extracción superó {_EXTRACTION_TIMEOUT_SEC}s y fue abortada. "
                        "Usa `page_range` para procesar el PDF por partes o sube "
                        "EXTRACTION_TIMEOUT_SEC en el contenedor."
                    ),
                    "timeout_sec": _EXTRACTION_TIMEOUT_SEC,
                },
            )

# ── Auth (optional) ───────────────────────────────────────────────────────────

_bearer = HTTPBearer(auto_error=False)


def _check_auth(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> None:
    if not _API_KEY:
        return
    if credentials is None or credentials.credentials != _API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ── Helpers ───────────────────────────────────────────────────────────────────

def _validate_upload(file: UploadFile) -> None:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF files are accepted",
        )


def _content_disposition(filename: str) -> str:
    """Build a Content-Disposition header that is safe for HTTP (latin-1 only).

    HTTP headers must be latin-1 encoded. File names from user PDFs often contain
    accented characters (tildes, eñes) that are not latin-1 encodable and cause
    ``UnicodeEncodeError`` in Starlette's response builder.

    We follow RFC 5987 / RFC 6266: emit a plain ASCII fallback *plus* a
    percent-encoded UTF-8 value in the ``filename*`` parameter so modern browsers
    use the correct name while old ones get the sanitized fallback.
    """
    from urllib.parse import quote
    import unicodedata

    # ASCII fallback: strip combining marks, then drop anything still non-ASCII
    nfkd = unicodedata.normalize("NFKD", filename)
    ascii_name = "".join(c for c in nfkd if ord(c) < 128).strip() or "output"
    # percent-encode the original UTF-8 name for RFC 5987
    utf8_encoded = quote(filename, safe="")
    return (
        f'attachment; filename="{ascii_name}"; '
        f"filename*=UTF-8''{utf8_encoded}"
    )


async def _save_upload_and_check_size(upload: UploadFile, dest: Path) -> None:
    """Stream the upload to *dest* without blocking the asyncio event loop.

    Using ``await upload.read(n)`` instead of ``upload.file.read(n)`` delegates
    the blocking SpooledTemporaryFile read to the default executor, so concurrent
    uploads don't freeze uvicorn and cause 'Failed to fetch' in the browser.
    """
    limit = _MAX_UPLOAD_MB * 1024 * 1024
    written = 0
    with dest.open("wb") as f:
        while True:
            chunk = await upload.read(8 * 1024 * 1024)  # 8 MB async read
            if not chunk:
                break
            written += len(chunk)
            if written > limit:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File exceeds {_MAX_UPLOAD_MB} MB limit",
                )
            f.write(chunk)


def _parse_strategies(s: str | None) -> list[str] | None:
    """Parse the comma-separated `strategies` form field, validating each
    name against the registry. Raises HTTP 400 with the list of valid names
    when an unknown strategy is requested — silent fallthrough used to mask
    typos like `ocr:tesseract` (missing `-basic`)."""
    if not s:
        return None
    raw = [item.strip() for item in s.split(",") if item.strip()]
    if not raw:
        return None
    from ..core.registry import registry
    unknown = [n for n in raw if registry.get(n) is None]
    if unknown:
        valid = sorted({m.name for m in registry.list_all()})
        raise HTTPException(
            status_code=400,
            detail={
                "error": "unknown_strategy",
                "message": f"Unknown strategy name(s): {unknown}",
                "unknown": unknown,
                "valid_strategies": valid,
            },
        )
    return raw


def _parse_range(s: str | None) -> tuple[int, int] | None:
    """Parse "X-Y" or "X" into a (start, end) tuple. Raises HTTP 400 on bad input
    instead of silently returning None — otherwise the user thinks they processed
    a range and actually got the whole PDF."""
    if s is None:
        return None
    s = s.strip()
    if not s:
        return None
    try:
        if "-" in s:
            start_s, end_s = s.split("-", 1)
            start, end = int(start_s.strip()), int(end_s.strip())
        else:
            start = end = int(s)
        if start < 1 or end < start:
            raise ValueError(f"invalid range: {s}")
        return start, end
    except (ValueError, AttributeError) as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_page_range",
                "message": f"page_range must be 'N' or 'N-M' with N≥1 and M≥N. Got: {s!r}",
                "parse_error": str(exc),
            },
        )


def _cleanup(work_dir: Path) -> None:
    """Delete temp working directory after response is sent."""
    shutil.rmtree(work_dir, ignore_errors=True)


def _run_sync_extraction(
    pdf_path: Path,
    out_dir: Path,
    options: dict[str, Any],
) -> Any:
    """Run ExtractUseCase synchronously. Intended for run_in_executor."""
    from ..app.ports import noop_emitter
    from ..app.use_cases import ExtractUseCase, ExtractionRequest

    req = ExtractionRequest(
        pdf_path=str(pdf_path),
        output_dir=str(out_dir),
        strategies=options.get("strategies"),
        page_range=options.get("page_range"),
        with_images=options.get("with_images", False),
        with_structure=options.get("with_structure", False),
        apply_spell=not options.get("no_spell", False),
        output_format="md",
    )
    return ExtractUseCase(on_event=noop_emitter).execute(req)


# ═══════════════════════════════════════════════════════════════════════════
# Routes
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    return RedirectResponse(url="/web", status_code=307)


@app.get("/web", include_in_schema=False, response_class=HTMLResponse)
async def web_ui() -> HTMLResponse:
    """Drag & drop SPA — talks to /api/v1/inspect, /strategies and /extract."""
    try:
        return HTMLResponse(_WEB_HTML_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="web.html missing in image")


@app.get(
    "/api/v1/readiness",
    tags=["ops"],
    summary="Per-backend readiness (installed + initialized)",
    description=(
        "Reports for every supported backend whether its Python deps and system "
        "binaries are present (`installed`) and whether its model files / JARs "
        "have already been downloaded (`initialized`). The UI uses this to grey "
        "out options that are not ready and to show a 'descargando…' banner."
    ),
)
async def readiness() -> dict:
    from ..app.readiness import collect_readiness
    return collect_readiness().to_dict()


@app.post(
    "/api/v1/readiness/download",
    tags=["ops"],
    summary="Trigger on-demand warmup of one or more backends",
    description=(
        "Body: `{\"backends\": [\"easyocr\", \"tika\"]}`. Use \"all\" to warm "
        "every backend that supports it. Returns the post-warmup readiness "
        "report. This is a synchronous call — clients should expect long "
        "responses (model downloads can take minutes)."
    ),
    dependencies=[Depends(_check_auth)],
)
async def readiness_download(payload: dict | None = None) -> dict:
    """Body: ``{"backends": [<name>, …]}``  or  ``{"backends": ["all"]}``.

    Backend names accept either the full strategy name (``ocr:easyocr``) or
    the legacy short alias (``easyocr``, ``tika``). Unknown names return 400.
    """
    from ..app.readiness import WARMUP_BY_NAME, collect_readiness, retry_missing

    payload = payload or {}
    requested_raw = payload.get("backends") or ["all"]
    if not isinstance(requested_raw, list):
        raise HTTPException(status_code=400, detail="`backends` must be a list")

    # Legacy aliases for the original two-button UI.
    aliases = {
        "easyocr": "ocr:easyocr",
        "tika": "text:tika-java",
        "tika-java": "text:tika-java",
        "tesseract": "ocr:tesseract-basic",
        "tesseract-basic": "ocr:tesseract-basic",
        "tesseract-advanced": "ocr:tesseract-advanced",
    }

    if "all" in requested_raw:
        only: list[str] | None = None
    else:
        only = [aliases.get(n, n) for n in requested_raw]
        unknown = [n for n in only if n not in WARMUP_BY_NAME]
        if unknown:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "unknown_backends",
                    "unknown": unknown,
                    "valid": sorted(WARMUP_BY_NAME.keys()),
                },
            )

    loop = asyncio.get_running_loop()
    _, retried = await loop.run_in_executor(
        None, lambda: retry_missing(only=only),
    )
    return {
        "results": {r["name"]: r for r in retried},
        "readiness": collect_readiness().to_dict(),
    }


@app.get("/healthz", tags=["ops"], summary="Liveness probe")
async def healthz() -> dict:
    """Always returns 200 while the process is alive. Used by Cloud Run."""
    from datetime import datetime, timezone
    return {"status": "ok", "ts": datetime.now(timezone.utc).isoformat()}


@app.get(
    "/readyz",
    tags=["ops"],
    summary="Readiness probe — 200 only when all backends are usable",
    description=(
        "Distinct from /healthz. Returns 503 until every probed backend is "
        "installed AND initialized (models/JARs on disk). Use this — not "
        "/healthz — as the readiness probe in Kubernetes / load balancers, "
        "so traffic isn't routed to an instance that is still warming up."
    ),
)
async def readyz() -> dict:
    from datetime import datetime, timezone
    from ..app.readiness import collect_readiness

    rep = collect_readiness()
    payload = {
        "status": "ready" if rep.all_ready else "not_ready",
        "ts": datetime.now(timezone.utc).isoformat(),
        "all_ready": rep.all_ready,
        "not_ready": [b.name for b in rep.backends if not b.ready],
    }
    if not rep.all_ready:
        raise HTTPException(status_code=503, detail=payload)
    return payload


@app.get(
    "/api/v1/capabilities",
    tags=["meta"],
    summary="System tool & package inventory",
    description=(
        "Returns availability of every system binary (tesseract, poppler, …) "
        "and Python package used by the pipeline. Call once to know which "
        "strategies are usable in this environment."
    ),
    # Intentionally NOT behind auth: the web UI calls this before the user has
    # any chance to provide a token. Read-only, no PDFs involved.
)
async def capabilities() -> dict:
    from ..app.ports import noop_emitter
    from ..app.use_cases import CapabilitiesUseCase

    return CapabilitiesUseCase(on_event=noop_emitter).execute().to_dict()


@app.get(
    "/api/v1/strategies",
    tags=["meta"],
    summary="List extraction strategies",
    description=(
        "Returns all registered strategies with tier, priority, and requirements. "
        "Filter with ?tier=ocr. Tiers: text | ocr | tables | images | fonts | layout | correct"
    ),
    # Read-only, used by the web UI before auth — no PDF data exposed.
)
async def strategies(tier: str | None = None) -> list[dict]:
    from ..core.registry import registry
    from ..app.readiness import collect_readiness

    all_meta = registry.list_all()
    if tier:
        all_meta = [m for m in all_meta if m.tier == tier]

    # Collect readiness for installed status
    readiness = collect_readiness()
    readiness_map = {b.name: b for b in readiness.backends}

    return [
        {
            "name": m.name,
            "tier": m.tier,
            "description": m.description,
            "priority": m.priority,
            "is_heavy": m.is_heavy,
            "requires_python": m.requires_python,
            "requires_system": m.requires_system,
            "installed": readiness_map.get(m.name, type('obj', (object,), {'installed': False})()).installed,
        }
        for m in sorted(all_meta, key=lambda x: (x.tier, x.priority))
    ]


@app.get(
    "/api/v1/capacity",
    tags=["ops"],
    summary="Server resource limits and active concurrency load",
    description=(
        "Returns the container’s memory limits, available RAM, CPU count, "
        "current active jobs, and a recommended queue depth for the client. "
        "The UI uses this to warn users before they overwhelm the server."
    ),
)
async def capacity() -> dict:
    ext_sem = _get_extraction_sem()
    insp_sem = _get_inspect_sem()
    mem = _get_memory_info()

    # Semaphore._value decreases with each acquire() — reliable internal field.
    active_extractions = _MAX_CONCURRENT_EXTRACTIONS - ext_sem._value
    active_inspects = _MAX_CONCURRENT_INSPECTS - insp_sem._value

    available_mb = mem["available_mb"] or 0
    limit_mb = mem["limit_mb"]

    # Heuristic: OCR on a scanned PDF peaks at ~350 MB per job.
    # Reserve 600 MB for the OS + JVM/Tika + model-loading headroom.
    MB_PER_EXTRACTION = 350
    RESERVE_MB = 600
    usable_mb = max(0, available_mb - RESERVE_MB)

    # How many more concurrent extractions can safely start right now?
    mem_concurrency = usable_mb // MB_PER_EXTRACTION if usable_mb else _MAX_CONCURRENT_EXTRACTIONS
    recommended_concurrency = max(1, min(
        _MAX_CONCURRENT_EXTRACTIONS - active_extractions,
        mem_concurrency,
    ))

    # Safe queue depth: total files the user can enqueue without risking OOM.
    # Files are processed through the semaphore one-at-a-time, but each inspect
    # also loads the PDF — use 120 MB as the per-inspect estimate.
    MB_PER_INSPECT = 120
    inspect_headroom = (usable_mb // MB_PER_INSPECT) if usable_mb else 20
    # Round down to a clean number; cap at 100 to avoid absurd suggestions.
    recommended_queue_limit = min(max(1, inspect_headroom), 100)

    return {
        "max_concurrent_extractions": _MAX_CONCURRENT_EXTRACTIONS,
        "max_concurrent_inspects": _MAX_CONCURRENT_INSPECTS,
        "active_extractions": active_extractions,
        "active_inspects": active_inspects,
        "cpu_count": os.cpu_count() or 1,
        "memory_limit_mb": limit_mb,
        "memory_available_mb": available_mb or None,
        "recommended_concurrency": recommended_concurrency,
        "recommended_queue_limit": recommended_queue_limit,
    }


@app.post(
    "/api/v1/inspect",
    tags=["extract"],
    summary="Profile a PDF without extracting",
    description=(
        "Analyses the PDF and returns a profile: page count, scanned vs "
        "text-native ratio, detected language, and which strategies would be "
        "selected. No Markdown is produced."
    ),
    dependencies=[Depends(_check_auth)],
)
async def inspect(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
) -> dict:
    _validate_upload(file)

    work_dir = _TMP_DIR / str(uuid.uuid4())
    work_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = work_dir / "input.pdf"

    try:
        await _save_upload_and_check_size(file, pdf_path)
    except Exception:
        _cleanup(work_dir)
        raise

    background_tasks.add_task(_cleanup, work_dir)

    loop = asyncio.get_running_loop()

    def _run() -> Any:
        from ..app.ports import noop_emitter
        from ..app.use_cases import InspectUseCase
        return InspectUseCase(on_event=noop_emitter).execute(str(pdf_path))

    async with _get_inspect_sem():
        try:
            result = await asyncio.wait_for(
                loop.run_in_executor(None, _run),
                timeout=_INSPECT_TIMEOUT_SEC,
            )
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=504,
                detail={
                    "error": "inspect_timeout",
                    "message": (
                        f"El análisis superó {_INSPECT_TIMEOUT_SEC}s. "
                        "El PDF puede estar dañado o ser demasiado complejo."
                    ),
                },
            )
    return result.to_dict()


@app.post(
    "/api/v1/extract",
    tags=["extract"],
    summary="Extract one PDF → download .md",
    description=(
        "Uploads one PDF, extracts it, and returns the Markdown as a file "
        "download (`Content-Type: text/markdown`).\n\n"
        "Extraction metadata is available in response headers:\n"
        "- `X-Quality-Score` — 0–100 quality score\n"
        "- `X-Pages` — total pages processed\n"
        "- `X-Elapsed-Sec` — wall-clock processing time\n"
        "- `X-Features-Used` — comma-separated strategy names used\n\n"
        "For very large PDFs use `page_range` to split the job across calls."
    ),
    dependencies=[Depends(_check_auth)],
)
async def extract(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    strategies: str | None = Form(None, description="Comma-separated strategy names"),
    page_range: str | None = Form(None, description="Page range e.g. 1-10"),
    with_images: bool = Form(False, description="Include extracted images"),
    with_structure: bool = Form(False, description="Include document structure"),
    no_spell: bool = Form(False, description="Skip OCR spell correction"),
) -> StreamingResponse:
    _validate_upload(file)

    work_dir = _TMP_DIR / str(uuid.uuid4())
    out_dir = work_dir / "out"
    work_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = work_dir / "input.pdf"
    
    try:
        await _save_upload_and_check_size(file, pdf_path)
    except Exception:
        _cleanup(work_dir)
        raise

    original_stem = Path(file.filename or "output").stem
    options = {
        "strategies": _parse_strategies(strategies),
        "page_range": _parse_range(page_range),
        "with_images": with_images,
        "with_structure": with_structure,
        "no_spell": no_spell,
    }

    try:
        result = await _run_extraction_guarded(pdf_path, out_dir, options)
    except HTTPException:
        background_tasks.add_task(_cleanup, work_dir)
        raise
    except Exception as exc:
        background_tasks.add_task(_cleanup, work_dir)
        raise HTTPException(status_code=500, detail=str(exc))

    md_files = sorted(out_dir.rglob("*.md"))
    if not md_files:
        background_tasks.add_task(_cleanup, work_dir)
        status_str = getattr(result, "status", "error")
        issues = getattr(result, "issues", []) or []
        warnings = getattr(result, "warnings", []) or []
        features_used = getattr(result, "features_used", []) or []
        # "blocked" means the pipeline finished but produced empty output
        # (typically: PDF needs OCR but no OCR backend is available, or every
        # selected strategy was skipped). Surface the real reason instead of
        # a generic 500.
        if status_str == "blocked":
            fallbacks_info = getattr(result, "fallbacks", []) or []
            fallback_msg = ""
            if fallbacks_info:
                fallback_msg = f"\n\nIntentó usar: {', '.join(fallbacks_info)}"

            reason = (
                f"❌ No se extrajo contenido del PDF.\n\n"
                f"Posibles causas:\n"
                f"• El PDF está escaneado (imágenes) y OCR no está disponible o falló\n"
                f"• Todas las estrategias elegidas fueron omitidas o fallaron\n"
                f"• El PDF está vacío o corrupto\n"
                f"• El contenido está en formato no soportado (solo imágenes, binarios)"
                f"{fallback_msg}"
            )
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "extraction_blocked",
                    "message": reason,
                    "status": status_str,
                    "features_used": features_used,
                    "issues": issues,
                    "warnings": warnings,
                },
            )
        raise HTTPException(
            status_code=500,
            detail={
                "error": "extraction_failed",
                "message": "Extraction produced no output",
                "status": status_str,
                "features_used": features_used,
                "issues": issues,
                "warnings": warnings,
            },
        )

    md_content = md_files[0].read_bytes()
    background_tasks.add_task(_cleanup, work_dir)

    headers = {
        "Content-Disposition": _content_disposition(f"{original_stem}.md"),
        "X-Quality-Score": str(round(getattr(result, "quality_score", 0.0), 1)),
        "X-Pages": str(getattr(result, "pages", 0)),
        "X-Elapsed-Sec": str(round(getattr(result, "elapsed_sec", 0.0), 2)),
        "X-Features-Used": ",".join(getattr(result, "features_used", [])),
    }
    fallbacks = getattr(result, "fallbacks", []) or []
    if fallbacks:
        headers["X-Fallback-Used"] = ";".join(fallbacks)
        headers["Access-Control-Expose-Headers"] = (
            "X-Quality-Score,X-Pages,X-Elapsed-Sec,X-Features-Used,X-Fallback-Used"
        )
    else:
        headers["Access-Control-Expose-Headers"] = (
            "X-Quality-Score,X-Pages,X-Elapsed-Sec,X-Features-Used"
        )

    return StreamingResponse(
        io.BytesIO(md_content),
        media_type="text/markdown; charset=utf-8",
        headers=headers,
    )


@app.post(
    "/api/v1/batch",
    tags=["extract"],
    summary="Extract multiple PDFs → download .zip",
    description=(
        "Uploads multiple PDFs, extracts each one, and returns a ZIP archive "
        "containing one `.md` per PDF plus a `_summary.json` with quality scores "
        "and metadata per file. Files that fail are skipped and recorded in the summary."
    ),
    dependencies=[Depends(_check_auth)],
)
async def batch(
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(..., description="One or more PDF files"),
    strategies: str | None = Form(None, description="Comma-separated strategy names"),
    page_range: str | None = Form(None, description="Page range e.g. 1-10"),
    with_images: bool = Form(False),
    with_structure: bool = Form(False),
    no_spell: bool = Form(False),
) -> StreamingResponse:
    if not files:
        raise HTTPException(status_code=400, detail="At least one file is required")

    work_dir = _TMP_DIR / str(uuid.uuid4())
    work_dir.mkdir(parents=True, exist_ok=True)

    options = {
        "strategies": _parse_strategies(strategies),
        "page_range": _parse_range(page_range),
        "with_images": with_images,
        "with_structure": with_structure,
        "no_spell": no_spell,
    }

    summary: list[dict] = []

    async def _process_upload(upload: UploadFile) -> dict | tuple[str, str, dict]:
        try:
            _validate_upload(upload)
        except Exception as exc:
            return {"file": upload.filename, "status": "error", "error": str(exc)}

        original_stem = Path(upload.filename or "output").stem
        file_dir = work_dir / str(uuid.uuid4())
        out_dir = file_dir / "out"
        file_dir.mkdir(parents=True)
        out_dir.mkdir(parents=True)
        pdf_path = file_dir / "input.pdf"

        try:
            await _save_upload_and_check_size(upload, pdf_path)
            # Use the same global semaphore + per-job timeout as /extract.
            result = await _run_extraction_guarded(pdf_path, out_dir, options)
            md_files = sorted(out_dir.rglob("*.md"))
            if md_files:
                md_content = md_files[0].read_text("utf-8")
                item_summary = {
                    "file": upload.filename,
                    "output": f"{original_stem}.md",
                    "status": getattr(result, "status", "ok"),
                    "quality_score": round(getattr(result, "quality_score", 0.0), 1),
                    "pages": getattr(result, "pages", 0),
                    "elapsed_sec": round(getattr(result, "elapsed_sec", 0.0), 2),
                    "features_used": getattr(result, "features_used", []),
                    "warnings": getattr(result, "warnings", []),
                }
                return (original_stem, md_content, item_summary)
            else:
                return {"file": upload.filename, "status": "error", "error": "extraction produced no output"}
        except HTTPException as exc:
            # Per-file timeout / blocked → record in summary, don't fail the batch.
            detail = exc.detail if isinstance(exc.detail, dict) else {"message": str(exc.detail)}
            return {"file": upload.filename, "status": "error",
                    "error": detail.get("message", str(detail)),
                    "code": detail.get("error", f"http_{exc.status_code}")}
        except Exception as exc:
            return {"file": upload.filename, "status": "error", "error": str(exc)}

    results = await asyncio.gather(*[_process_upload(upload) for upload in files])
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for res in results:
            if isinstance(res, tuple):
                stem, html, summ = res
                zf.writestr(f"{stem}.md", html)
                summary.append(summ)
            else:
                summary.append(res)
        
        zf.writestr("_summary.json", json.dumps(summary, ensure_ascii=False, indent=2))

    background_tasks.add_task(_cleanup, work_dir)
    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="extracted.zip"'},
    )


# ── Dev server entry point (used by CLI 'serve' command) ──────────────────────

def run_server(host: str = "0.0.0.0", port: int = 8080, reload: bool = False) -> None:
    """Start uvicorn programmatically — called by CLI 'serve' command."""
    import uvicorn

    uvicorn.run(
        "pdf_extractor.interfaces.api:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )
