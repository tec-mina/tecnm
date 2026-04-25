"""
interfaces/api.py — FastAPI REST + SSE interface for PDF Extractor.

Design
------
All business logic lives in app/use_cases.py (hexagonal core).
This module is the *transport layer* only: it receives HTTP requests,
translates them into use-case calls, and serialises results back to JSON
or Server-Sent Events (SSE).

AI / agent consumers should read the full event contract documented in
app/use_cases.py; every event has at minimum:
    {"event": str, "ts": ISO-8601, ...payload fields...}

Endpoints
---------
GET  /healthz                     — liveness probe (Cloud Run / K8s)
GET  /api/v1/capabilities         — system tool + package inventory
GET  /api/v1/strategies           — registered extraction strategies
POST /api/v1/inspect              — profile a PDF (multipart upload)
POST /api/v1/extract              — extract one PDF → returns job_id
GET  /api/v1/extract/{job_id}/stream
                                  — SSE stream of extraction events
GET  /api/v1/extract/{job_id}     — final result once job completes
POST /api/v1/batch                — submit multiple PDFs at once
GET  /api/v1/batch/{batch_id}     — batch status + per-file results

Request / Response schemas
--------------------------
POST /api/v1/extract
  Content-Type: multipart/form-data
  Fields:
    file            required  PDF file (binary)
    strategies      optional  comma-separated strategy names
                              e.g. "text:fast,tables:pdfplumber"
    page_range      optional  "1-10"
    with_images     optional  "true" / "false"  (default false)
    with_structure  optional  "true" / "false"  (default false)

  Response 202:
    {"job_id": str, "filename": str, "status": "queued"}

GET /api/v1/extract/{job_id}/stream
  Returns text/event-stream; each event is:
    data: <JSON>\\n\\n
  where JSON matches the event contract in app/use_cases.py.
  The stream terminates after the "done" or "error" event.

GET /api/v1/extract/{job_id}
  Response 200 (completed):
    {
      "job_id":       str,
      "status":       "ok" | "error" | "blocked" | "cached",
      "filename":     str,
      "quality":      float,          # 0–100
      "elapsed_sec":  float,
      "output_files": [str, ...],     # relative paths inside job output dir
      "markdown":     str | null,     # inline if single file < 1 MB
      "events":       [{...}, ...],   # full event log for the job
      "error":        str | null
    }
  Response 202 (still running):
    {"job_id": str, "status": "running"}
  Response 404: job not found

POST /api/v1/batch
  Content-Type: multipart/form-data
  Fields:
    files[]         required  one or more PDF files
    strategies      optional  (applied to all files)
    page_range      optional
    with_images     optional

  Response 202:
    {"batch_id": str, "jobs": [{"job_id": str, "filename": str}, ...]}

GET /api/v1/batch/{batch_id}
  Response 200:
    {
      "batch_id":  str,
      "total":     int,
      "done":      int,
      "failed":    int,
      "running":   int,
      "jobs":      [{"job_id": str, "filename": str, "status": str}, ...]
    }

Error responses
---------------
All errors follow:
    {"error": str, "detail": str | null}

Pagination
----------
/api/v1/strategies accepts ?tier=<tier> query param.

Authentication
--------------
None by default.  Set API_KEY env var to require
  Authorization: Bearer <token>  on all /api/* routes.
"""

from __future__ import annotations

import asyncio
import json
import os
import queue
import shutil
import threading
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, AsyncIterator

from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# ── App factory ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="PDF Extractor API",
    description=(
        "Production-grade PDF → Markdown extraction pipeline. "
        "Accepts one or multiple PDF files and returns structured Markdown "
        "with quality scores and extraction metadata."
    ),
    version="2.0.0",
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

_UPLOAD_DIR = Path(os.environ.get("UPLOAD_DIR", "/tmp/pdf-extractor/uploads"))
_OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", "/tmp/pdf-extractor/output"))
_JOB_STATE_DIR = Path(os.environ.get("JOB_STATE_DIR", str(_OUTPUT_DIR / ".jobs")))
_JOB_TTL_SEC = max(3600, int(os.environ.get("JOB_TTL_SEC", str(24 * 3600))))
_MAX_UPLOAD_MB = int(os.environ.get("MAX_UPLOAD_MB", "200"))
_API_KEY: str | None = os.environ.get("API_KEY")

for _d in (_UPLOAD_DIR, _OUTPUT_DIR, _JOB_STATE_DIR):
    _d.mkdir(parents=True, exist_ok=True)

_LIVE_EVENTS: dict[str, queue.Queue] = {}
_JOBS_LOCK = threading.Lock()
_RERUNNABLE_STATUSES = {"uploaded", "ok", "error", "blocked", "cached"}

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


# ── SSE emitter ───────────────────────────────────────────────────────────────

class _QueueEmitter:
    """Puts each event dict into a thread-safe Queue for SSE streaming."""

    def __init__(self, q: queue.Queue) -> None:
        self._q = q

    def __call__(self, event: dict[str, Any]) -> None:
        self._q.put(event)


# ── Job store ─────────────────────────────────────────────────────────────────

def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _utc_iso(dt: datetime | None = None) -> str:
    return (dt or _utc_now()).isoformat()


def _job_state_path(job_id: str) -> Path:
    return _JOB_STATE_DIR / f"{job_id}.json"


def _load_job(job_id: str) -> dict[str, Any] | None:
    p = _job_state_path(job_id)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text("utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _write_job(record: dict[str, Any]) -> dict[str, Any]:
    now = _utc_now()
    record = dict(record)
    record.setdefault("created_at", _utc_iso(now))
    record["updated_at"] = _utc_iso(now)
    record["expires_at"] = _utc_iso(now + timedelta(seconds=_JOB_TTL_SEC))
    p = _job_state_path(record["job_id"])
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(record, ensure_ascii=False, indent=2), "utf-8")
    tmp.replace(p)
    return record


def _upsert_job(job_id: str, **updates: Any) -> dict[str, Any]:
    with _JOBS_LOCK:
        record = _load_job(job_id) or {"job_id": job_id}
        record.update(updates)
        return _write_job(record)


def _delete_job(job_id: str, record: dict[str, Any] | None = None) -> None:
    _LIVE_EVENTS.pop(job_id, None)
    _job_state_path(job_id).unlink(missing_ok=True)
    out = _OUTPUT_DIR / job_id
    if out.exists():
        shutil.rmtree(out, ignore_errors=True)
    if record and record.get("pdf_path"):
        Path(record["pdf_path"]).unlink(missing_ok=True)


def _cleanup_expired() -> None:
    with _JOBS_LOCK:
        for p in _JOB_STATE_DIR.glob("*.json"):
            try:
                rec = json.loads(p.read_text("utf-8"))
            except (OSError, json.JSONDecodeError):
                p.unlink(missing_ok=True)
                continue
            exp = rec.get("expires_at")
            if exp:
                try:
                    if datetime.fromisoformat(exp) <= _utc_now():
                        _delete_job(rec.get("job_id", p.stem), rec)
                except ValueError:
                    pass


def _get_job(job_id: str) -> dict[str, Any] | None:
    _cleanup_expired()
    with _JOBS_LOCK:
        return _load_job(job_id)


# ── Page-range parser ─────────────────────────────────────────────────────────

def _parse_range(s: str | None) -> tuple[int, int] | None:
    if not s:
        return None
    try:
        start, end = s.split("-")
        return int(start), int(end)
    except (ValueError, AttributeError):
        return None


# ── Extraction worker ─────────────────────────────────────────────────────────

def _run_extraction(job_id: str, options: dict[str, Any]) -> None:
    """Runs in a background thread. Writes all events into the live queue
    and updates the job record when done."""
    from ..app.use_cases import ExtractUseCase, ExtractionRequest

    q: queue.Queue = _LIVE_EVENTS[job_id]
    job = _get_job(job_id)
    if not job:
        return

    out_dir = _OUTPUT_DIR / job_id
    out_dir.mkdir(parents=True, exist_ok=True)

    emitter = _QueueEmitter(q)
    event_log: list[dict] = []

    def _logging_emitter(event: dict[str, Any]) -> None:
        event_log.append(event)
        emitter(event)

    req = ExtractionRequest(
        pdf_path=job["pdf_path"],
        output_dir=str(out_dir),
        strategies=options.get("strategies"),
        page_range=options.get("page_range"),
        with_images=options.get("with_images", False),
        with_structure=options.get("with_structure", False),
        apply_spell=not options.get("no_spell", False),
        output_format="md",
    )

    try:
        uc = ExtractUseCase(on_event=_logging_emitter)
        result = uc.execute(req)

        # Collect output files
        output_files = sorted(str(f.relative_to(_OUTPUT_DIR)) for f in out_dir.rglob("*.md"))

        # Inline markdown if single file < 1 MB
        markdown_inline: str | None = None
        if len(output_files) == 1:
            full_path = _OUTPUT_DIR / output_files[0]
            if full_path.stat().st_size < 1024 * 1024:
                markdown_inline = full_path.read_text("utf-8")

        _upsert_job(
            job_id,
            status=result.status if hasattr(result, "status") else "ok",
            quality=getattr(result, "quality_score", None),
            elapsed_sec=getattr(result, "elapsed_sec", None),
            output_files=output_files,
            markdown=markdown_inline,
            events=event_log,
            error=None,
        )
    except Exception as exc:
        _upsert_job(
            job_id,
            status="error",
            error=str(exc),
            events=event_log,
        )
        emitter({"event": "error", "ts": _utc_iso(), "msg": str(exc), "phase": "extraction"})
    finally:
        # Signal stream end
        q.put(None)


# ── SSE async generator ───────────────────────────────────────────────────────

async def _sse_stream(job_id: str) -> AsyncIterator[str]:
    """Async generator that yields SSE-formatted strings from the job queue."""
    loop = asyncio.get_event_loop()

    with _JOBS_LOCK:
        q = _LIVE_EVENTS.get(job_id)

    if q is None:
        # Job already finished — replay stored events
        job = _get_job(job_id)
        if job and job.get("events"):
            for ev in job["events"]:
                yield f"data: {json.dumps(ev, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'event': 'stream_end', 'ts': _utc_iso()})}\n\n"
        return

    while True:
        try:
            event = await loop.run_in_executor(None, lambda: q.get(timeout=30))
        except Exception:
            # timeout — send keepalive comment
            yield ": keepalive\n\n"
            continue

        if event is None:
            # Sentinel — extraction thread finished
            yield f"data: {json.dumps({'event': 'stream_end', 'ts': _utc_iso()})}\n\n"
            with _JOBS_LOCK:
                _LIVE_EVENTS.pop(job_id, None)
            break

        yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

        # Auto-terminate after terminal events
        if event.get("event") in ("done", "error"):
            yield f"data: {json.dumps({'event': 'stream_end', 'ts': _utc_iso()})}\n\n"
            with _JOBS_LOCK:
                _LIVE_EVENTS.pop(job_id, None)
            break


# ═══════════════════════════════════════════════════════════════════════════
# Routes
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/healthz", tags=["ops"])
async def healthz() -> dict:
    """Liveness probe — always returns 200 if the process is alive."""
    return {"status": "ok", "ts": _utc_iso()}


@app.get(
    "/api/v1/capabilities",
    tags=["meta"],
    summary="System tool & package inventory",
    description=(
        "Returns availability of every system binary (tesseract, poppler, …) "
        "and Python package used by the extraction pipeline. "
        "Agents should call this once on startup to know which strategies are usable."
    ),
    dependencies=[Depends(_check_auth)],
)
async def capabilities() -> dict:
    from ..app.use_cases import CapabilitiesUseCase
    from ..app.ports import noop_emitter

    report = CapabilitiesUseCase(on_event=noop_emitter).execute()
    return report.to_dict()


@app.get(
    "/api/v1/strategies",
    tags=["meta"],
    summary="List extraction strategies",
    description=(
        "Returns all registered extraction strategies with their tier, priority, "
        "and requirements. Use ?tier=ocr to filter by tier. "
        "Tiers: text | ocr | tables | images | fonts | layout | correct"
    ),
    dependencies=[Depends(_check_auth)],
)
async def strategies(tier: str | None = None) -> list[dict]:
    from ..core.registry import registry

    all_meta = registry.list_all()
    if tier:
        all_meta = [m for m in all_meta if m.tier == tier]
    return [
        {
            "name": m.name,
            "tier": m.tier,
            "description": m.description,
            "priority": m.priority,
            "is_heavy": m.is_heavy,
            "is_gpu_optional": m.is_gpu_optional,
            "requires_python": m.requires_python,
            "requires_system": m.requires_system,
        }
        for m in sorted(all_meta, key=lambda x: (x.tier, x.priority))
    ]


@app.post(
    "/api/v1/inspect",
    tags=["extract"],
    summary="Profile a PDF without extracting",
    description=(
        "Analyses the PDF and returns a profile: page count, "
        "proportion of scanned vs. text-native pages, detected language, "
        "and the strategies the pipeline would choose. "
        "No Markdown is produced. Useful for pre-flight checks by agents."
    ),
    dependencies=[Depends(_check_auth)],
)
async def inspect(file: UploadFile = File(...)) -> dict:
    _cleanup_expired()
    _validate_upload(file)

    tmp_id = str(uuid.uuid4())
    tmp_path = _UPLOAD_DIR / f"{tmp_id}.pdf"
    try:
        content = await file.read()
        tmp_path.write_bytes(content)

        from ..app.use_cases import InspectUseCase
        from ..app.ports import noop_emitter

        result = InspectUseCase(on_event=noop_emitter).execute(str(tmp_path))
        return result.to_dict()
    finally:
        tmp_path.unlink(missing_ok=True)


@app.post(
    "/api/v1/extract",
    status_code=status.HTTP_202_ACCEPTED,
    tags=["extract"],
    summary="Submit a PDF for extraction",
    description=(
        "Uploads one PDF and queues an async extraction job. "
        "Returns a job_id immediately. "
        "Poll GET /api/v1/extract/{job_id} for results, "
        "or stream events via GET /api/v1/extract/{job_id}/stream."
    ),
    dependencies=[Depends(_check_auth)],
)
async def extract(
    file: UploadFile = File(...),
    strategies: str | None = Form(None, description="Comma-separated strategy names"),
    page_range: str | None = Form(None, description="Page range e.g. 1-10"),
    with_images: bool = Form(False),
    with_structure: bool = Form(False),
    no_spell: bool = Form(False),
) -> dict:
    _cleanup_expired()
    _validate_upload(file)

    job_id = str(uuid.uuid4())
    pdf_path = _UPLOAD_DIR / f"{job_id}.pdf"
    content = await file.read()
    _check_size(content)
    pdf_path.write_bytes(content)

    parsed_strategies = [s.strip() for s in strategies.split(",")] if strategies else None
    options = {
        "strategies": parsed_strategies,
        "page_range": _parse_range(page_range),
        "with_images": with_images,
        "with_structure": with_structure,
        "no_spell": no_spell,
    }

    _upsert_job(
        job_id,
        status="running",
        pdf_path=str(pdf_path),
        original_name=file.filename,
        options=options,
    )

    q: queue.Queue = queue.Queue()
    with _JOBS_LOCK:
        _LIVE_EVENTS[job_id] = q

    thread = threading.Thread(target=_run_extraction, args=(job_id, options), daemon=True)
    thread.start()

    return {"job_id": job_id, "filename": file.filename, "status": "queued"}


@app.get(
    "/api/v1/extract/{job_id}/stream",
    tags=["extract"],
    summary="Stream extraction events (SSE)",
    description=(
        "Server-Sent Events stream. Each event line is:\n\n"
        "    data: <JSON>\\n\\n\n\n"
        "Event types (from app/use_cases.py contract):\n"
        "- preflight  — file validation result\n"
        "- profile    — page breakdown (text/scanned/tables)\n"
        "- cache_hit  — result served from cache\n"
        "- strategy_plan — chosen strategies\n"
        "- feature_start / feature_done / feature_skip — per-strategy progress\n"
        "- validate   — quality score\n"
        "- fix        — post-processing fixes applied\n"
        "- done       — extraction complete, quality score & output path\n"
        "- error      — extraction failed\n"
        "- stream_end — always the last event\n\n"
        "Callers should reconnect if the connection drops before stream_end."
    ),
    dependencies=[Depends(_check_auth)],
)
async def extract_stream(job_id: str) -> StreamingResponse:
    job = _get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")

    return StreamingResponse(
        _sse_stream(job_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.get(
    "/api/v1/extract/{job_id}",
    tags=["extract"],
    summary="Get extraction result",
    description=(
        "Returns the final extraction result once the job is complete. "
        "Returns 202 while the job is still running. "
        "The 'markdown' field is populated (inline) only when the output is a "
        "single file under 1 MB; otherwise use output_files paths."
    ),
    dependencies=[Depends(_check_auth)],
)
async def extract_result(job_id: str) -> JSONResponse:
    job = _get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")

    if job.get("status") == "running":
        return JSONResponse(
            content={"job_id": job_id, "status": "running"},
            status_code=202,
        )

    return JSONResponse(content={
        "job_id":       job_id,
        "status":       job.get("status"),
        "filename":     job.get("original_name"),
        "quality":      job.get("quality"),
        "elapsed_sec":  job.get("elapsed_sec"),
        "output_files": job.get("output_files", []),
        "markdown":     job.get("markdown"),
        "events":       job.get("events", []),
        "error":        job.get("error"),
    })


@app.post(
    "/api/v1/batch",
    status_code=status.HTTP_202_ACCEPTED,
    tags=["batch"],
    summary="Submit multiple PDFs",
    description=(
        "Accepts one or more PDF files (files[] field) and queues them "
        "as individual jobs under a shared batch_id. "
        "All files share the same extraction options."
    ),
    dependencies=[Depends(_check_auth)],
)
async def batch_extract(
    files: list[UploadFile] = File(...),
    strategies: str | None = Form(None),
    page_range: str | None = Form(None),
    with_images: bool = Form(False),
    with_structure: bool = Form(False),
    no_spell: bool = Form(False),
) -> dict:
    if not files:
        raise HTTPException(status_code=400, detail="At least one file is required")

    batch_id = str(uuid.uuid4())
    parsed_strategies = [s.strip() for s in strategies.split(",")] if strategies else None
    options = {
        "strategies": parsed_strategies,
        "page_range": _parse_range(page_range),
        "with_images": with_images,
        "with_structure": with_structure,
        "no_spell": no_spell,
    }

    jobs: list[dict] = []
    for upload in files:
        _validate_upload(upload)
        content = await upload.read()
        _check_size(content)

        job_id = str(uuid.uuid4())
        pdf_path = _UPLOAD_DIR / f"{job_id}.pdf"
        pdf_path.write_bytes(content)

        _upsert_job(
            job_id,
            status="running",
            pdf_path=str(pdf_path),
            original_name=upload.filename,
            batch_id=batch_id,
            options=options,
        )

        q: queue.Queue = queue.Queue()
        with _JOBS_LOCK:
            _LIVE_EVENTS[job_id] = q

        thread = threading.Thread(
            target=_run_extraction, args=(job_id, options), daemon=True
        )
        thread.start()
        jobs.append({"job_id": job_id, "filename": upload.filename})

    # Store batch manifest
    _upsert_job(
        batch_id,
        status="batch",
        job_ids=[j["job_id"] for j in jobs],
    )

    return {"batch_id": batch_id, "jobs": jobs}


@app.get(
    "/api/v1/batch/{batch_id}",
    tags=["batch"],
    summary="Get batch status",
    description="Returns aggregate status for all jobs in the batch.",
    dependencies=[Depends(_check_auth)],
)
async def batch_status(batch_id: str) -> dict:
    batch = _get_job(batch_id)
    if not batch or batch.get("status") != "batch":
        raise HTTPException(status_code=404, detail="batch not found")

    job_ids: list[str] = batch.get("job_ids", [])
    job_records = [_get_job(jid) for jid in job_ids]

    def _st(r: dict | None) -> str:
        return r.get("status", "unknown") if r else "unknown"

    statuses = [_st(r) for r in job_records]
    return {
        "batch_id": batch_id,
        "total":   len(job_ids),
        "done":    sum(1 for s in statuses if s in ("ok", "cached", "blocked")),
        "failed":  sum(1 for s in statuses if s == "error"),
        "running": sum(1 for s in statuses if s == "running"),
        "jobs": [
            {"job_id": jid, "filename": (r or {}).get("original_name"), "status": s}
            for jid, r, s in zip(job_ids, job_records, statuses)
        ],
    }


# ── Validation helpers ────────────────────────────────────────────────────────

def _validate_upload(file: UploadFile) -> None:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF files are accepted",
        )


def _check_size(content: bytes) -> None:
    limit = _MAX_UPLOAD_MB * 1024 * 1024
    if len(content) > limit:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds {_MAX_UPLOAD_MB} MB limit",
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
