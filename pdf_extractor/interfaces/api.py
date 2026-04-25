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
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

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

_TMP_DIR.mkdir(parents=True, exist_ok=True)

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


def _save_upload_and_check_size(upload: UploadFile, dest: Path) -> None:
    limit = _MAX_UPLOAD_MB * 1024 * 1024
    written = 0
    with dest.open("wb") as f:
        while chunk := upload.file.read(8192 * 1024):  # 8MB chunks
            written += len(chunk)
            if written > limit:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File exceeds {_MAX_UPLOAD_MB} MB limit",
                )
            f.write(chunk)


def _parse_range(s: str | None) -> tuple[int, int] | None:
    if not s:
        return None
    try:
        start, end = s.split("-")
        return int(start), int(end)
    except (ValueError, AttributeError):
        return None


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

@app.get("/healthz", tags=["ops"], summary="Liveness probe")
async def healthz() -> dict:
    """Always returns 200 while the process is alive. Used by Cloud Run."""
    from datetime import datetime, timezone
    return {"status": "ok", "ts": datetime.now(timezone.utc).isoformat()}


@app.get(
    "/api/v1/capabilities",
    tags=["meta"],
    summary="System tool & package inventory",
    description=(
        "Returns availability of every system binary (tesseract, poppler, …) "
        "and Python package used by the pipeline. Call once to know which "
        "strategies are usable in this environment."
    ),
    dependencies=[Depends(_check_auth)],
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
        _save_upload_and_check_size(file, pdf_path)
    except Exception:
        _cleanup(work_dir)
        raise

    background_tasks.add_task(_cleanup, work_dir)

    loop = asyncio.get_running_loop()

    def _run() -> Any:
        from ..app.ports import noop_emitter
        from ..app.use_cases import InspectUseCase
        return InspectUseCase(on_event=noop_emitter).execute(str(pdf_path))

    result = await loop.run_in_executor(None, _run)
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
        _save_upload_and_check_size(file, pdf_path)
    except Exception:
        _cleanup(work_dir)
        raise

    original_stem = Path(file.filename or "output").stem
    options = {
        "strategies": [s.strip() for s in strategies.split(",")] if strategies else None,
        "page_range": _parse_range(page_range),
        "with_images": with_images,
        "with_structure": with_structure,
        "no_spell": no_spell,
    }

    loop = asyncio.get_running_loop()
    try:
        result = await loop.run_in_executor(
            None, _run_sync_extraction, pdf_path, out_dir, options
        )
    except Exception as exc:
        background_tasks.add_task(_cleanup, work_dir)
        raise HTTPException(status_code=500, detail=str(exc))

    md_files = sorted(out_dir.rglob("*.md"))
    if not md_files:
        background_tasks.add_task(_cleanup, work_dir)
        raise HTTPException(status_code=500, detail="Extraction produced no output")

    md_content = md_files[0].read_bytes()
    background_tasks.add_task(_cleanup, work_dir)

    return StreamingResponse(
        io.BytesIO(md_content),
        media_type="text/markdown; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{original_stem}.md"',
            "X-Quality-Score": str(round(getattr(result, "quality_score", 0.0), 1)),
            "X-Pages": str(getattr(result, "pages", 0)),
            "X-Elapsed-Sec": str(round(getattr(result, "elapsed_sec", 0.0), 2)),
            "X-Features-Used": ",".join(getattr(result, "features_used", [])),
        },
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
        "strategies": [s.strip() for s in strategies.split(",")] if strategies else None,
        "page_range": _parse_range(page_range),
        "with_images": with_images,
        "with_structure": with_structure,
        "no_spell": no_spell,
    }

    loop = asyncio.get_running_loop()
    summary: list[dict] = []
    
    sem = asyncio.Semaphore(int(os.environ.get("EXTRACTOR_WORKERS", "4")))
    
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
            _save_upload_and_check_size(upload, pdf_path)
            async with sem:
                result = await loop.run_in_executor(
                    None, _run_sync_extraction, pdf_path, out_dir, options
                )
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
