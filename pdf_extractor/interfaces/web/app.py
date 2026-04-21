"""
interfaces/web/app.py — Flask web interface for PDF Extractor.

Architecture:
  Same use-cases as the CLI (ExtractUseCase, InspectUseCase, CapabilitiesUseCase).
  Events are streamed to the browser via Server-Sent Events (SSE) — the same
  IEventEmitter protocol, wired to a queue instead of stdout.

Routes:
  GET  /                    — main UI
  GET  /api/capabilities    — tool + package inventory (JSON)
  GET  /api/strategies      — all registered strategies (JSON)
  POST /api/inspect         — profile a PDF (JSON)
  POST /api/extract         — upload PDF, start extraction job (returns job_id)
  GET  /api/stream/<job_id> — SSE stream of events for a running job
  GET  /api/jobs/<job_id>   — final result of a completed job
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
import os
import queue
import shutil
import threading
import time
import uuid
from pathlib import Path
from typing import Any

from flask import Flask, Response, jsonify, render_template, request, stream_with_context

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024   # 200 MB upload limit

# Temporary upload/output directories
_UPLOAD_DIR = Path(os.environ.get("UPLOAD_DIR", "/tmp/pdf-extractor/uploads"))
_OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", "/tmp/pdf-extractor/output"))
_JOB_STATE_DIR = Path(os.environ.get("JOB_STATE_DIR", str(_OUTPUT_DIR / ".jobs")))
_JOB_TTL_SEC = max(3600, int(os.environ.get("JOB_TTL_SEC", str(24 * 3600))))
_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
_JOB_STATE_DIR.mkdir(parents=True, exist_ok=True)

# In-memory live event queues only; job metadata is persisted on disk.
_LIVE_EVENTS: dict[str, queue.Queue] = {}
_JOBS_LOCK = threading.Lock()
_RERUNNABLE_STATUSES = {"uploaded", "ok", "error", "blocked", "cached"}


# ── SSE emitter ───────────────────────────────────────────────────────────────

class _QueueEmitter:
    """IEventEmitter that puts events into a thread-safe queue for SSE streaming."""

    def __init__(self, q: queue.Queue) -> None:
        self._q = q

    def __call__(self, event: dict[str, Any]) -> None:
        self._q.put(event)


# ── Job store helpers ────────────────────────────────────────────────────────

def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _utc_iso(dt: datetime | None = None) -> str:
    return (dt or _utc_now()).isoformat()


def _job_state_path(job_id: str) -> Path:
    return _JOB_STATE_DIR / f"{job_id}.json"


def _job_output_dir(job_id: str) -> Path:
    return _OUTPUT_DIR / job_id


def _load_job_record(job_id: str) -> dict[str, Any] | None:
    path = _job_state_path(job_id)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _write_job_record(record: dict[str, Any]) -> dict[str, Any]:
    now = _utc_now()
    path = _job_state_path(record["job_id"])
    path.parent.mkdir(parents=True, exist_ok=True)

    record = dict(record)
    record.setdefault("created_at", _utc_iso(now))
    record["updated_at"] = _utc_iso(now)
    record["expires_at"] = _utc_iso(now + timedelta(seconds=_JOB_TTL_SEC))

    tmp_path = path.with_suffix(".tmp")
    tmp_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp_path.replace(path)
    return record


def _delete_job_artifacts(job_id: str, record: dict[str, Any] | None = None) -> None:
    _LIVE_EVENTS.pop(job_id, None)

    state_path = _job_state_path(job_id)
    if state_path.exists():
        state_path.unlink(missing_ok=True)

    out_dir = _job_output_dir(job_id)
    if out_dir.exists():
        shutil.rmtree(out_dir, ignore_errors=True)

    if record and record.get("pdf_path"):
        Path(record["pdf_path"]).unlink(missing_ok=True)


def _job_is_expired(record: dict[str, Any]) -> bool:
    expires_at = record.get("expires_at")
    if not expires_at:
        return False
    try:
        return datetime.fromisoformat(expires_at) <= _utc_now()
    except ValueError:
        return False


def _cleanup_expired_jobs() -> None:
    with _JOBS_LOCK:
        for state_path in _JOB_STATE_DIR.glob("*.json"):
            try:
                record = json.loads(state_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                state_path.unlink(missing_ok=True)
                continue

            if _job_is_expired(record):
                _delete_job_artifacts(record.get("job_id", state_path.stem), record)


def _get_job(job_id: str) -> dict[str, Any] | None:
    _cleanup_expired_jobs()
    with _JOBS_LOCK:
        return _load_job_record(job_id)


def _upsert_job(job_id: str, **updates: Any) -> dict[str, Any]:
    with _JOBS_LOCK:
        record = _load_job_record(job_id) or {"job_id": job_id}
        record.update(updates)
        return _write_job_record(record)


def _set_live_queue(job_id: str, event_queue: queue.Queue) -> None:
    with _JOBS_LOCK:
        _LIVE_EVENTS[job_id] = event_queue


def _get_live_queue(job_id: str) -> queue.Queue | None:
    with _JOBS_LOCK:
        return _LIVE_EVENTS.get(job_id)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/capabilities")
def capabilities():
    from ...app.use_cases import CapabilitiesUseCase
    from ...app.ports import noop_emitter
    report = CapabilitiesUseCase(on_event=noop_emitter).execute()
    return jsonify(report.to_dict())


@app.route("/api/strategies")
def strategies():
    from ...core.registry import registry
    tier = request.args.get("tier")
    all_meta = registry.list_all()
    if tier:
        all_meta = [m for m in all_meta if m.tier == tier]
    return jsonify([
        {
            "name": m.name, "tier": m.tier,
            "description": m.description,
            "priority": m.priority,
            "is_heavy": m.is_heavy,
            "is_gpu_optional": m.is_gpu_optional,
            "requires_python": m.requires_python,
            "requires_system": m.requires_system,
        }
        for m in sorted(all_meta, key=lambda x: (x.tier, x.priority))
    ])


@app.route("/api/inspect", methods=["POST"])
def inspect():
    """Inspect an already-uploaded PDF by job_id or file path."""
    data = request.get_json(force=True)
    job_id = data.get("job_id")
    if not job_id:
        return jsonify({"error": "job_id required"}), 400

    job = _get_job(job_id)
    if not job:
        return jsonify({"error": "job not found"}), 404

    pdf_path = job.get("pdf_path")
    if not pdf_path or not Path(pdf_path).exists():
        return jsonify({"error": "PDF file not found"}), 404

    try:
        from ...app.use_cases import InspectUseCase
        from ...app.ports import noop_emitter
        result = InspectUseCase(on_event=noop_emitter).execute(pdf_path)
        return jsonify(result.to_dict())
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/upload", methods=["POST"])
def upload():
    """Upload a PDF and return a job_id. Does NOT start extraction yet."""
    _cleanup_expired_jobs()

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    f = request.files["file"]
    if not f.filename or not f.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are accepted"}), 400

    job_id = str(uuid.uuid4())
    pdf_path = _UPLOAD_DIR / f"{job_id}.pdf"
    f.save(str(pdf_path))

    _upsert_job(
        job_id,
        status="uploaded",
        pdf_path=str(pdf_path),
        original_name=f.filename,
        output_dir=str(_job_output_dir(job_id)),
        result=None,
    )

    return jsonify({"job_id": job_id, "filename": f.filename})


@app.route("/api/extract", methods=["POST"])
def extract():
    """Start extraction for an uploaded PDF. Returns job_id immediately."""
    data = request.get_json(force=True)
    job_id = data.get("job_id")
    if not job_id:
        return jsonify({"error": "job_id required"}), 400

    job = _get_job(job_id)
    if not job:
        return jsonify({"error": "job not found"}), 404
    if job["status"] not in _RERUNNABLE_STATUSES:
        return jsonify({"error": f"job is already {job['status']}"}), 409

    event_queue: queue.Queue = queue.Queue()
    _set_live_queue(job_id, event_queue)

    strategies = data.get("strategies") or None       # None = auto
    page_range_str = data.get("page_range")           # "1-10" or null
    with_images = bool(data.get("with_images", False))
    with_structure = bool(data.get("with_structure", False))
    no_spell = bool(data.get("no_spell", False))

    page_range = _parse_range(page_range_str)
    out_dir = _OUTPUT_DIR / job_id
    out_dir.mkdir(parents=True, exist_ok=True)
    job = _upsert_job(job_id, status="running", result=None, output_dir=str(out_dir))

    def _run():
        from ...app.use_cases import ExtractUseCase, ExtractionRequest
        emitter = _QueueEmitter(event_queue)
        uc = ExtractUseCase(on_event=emitter)
        req = ExtractionRequest(
            pdf_path=job["pdf_path"],
            output_dir=str(out_dir),
            strategies=strategies,
            page_range=page_range,
            with_images=with_images,
            with_structure=with_structure,
            apply_spell=not no_spell,
            output_format="md",
        )
        try:
            result = uc.execute(req)
            _upsert_job(job_id, status=result.status, result=result.to_dict())
        except Exception as exc:
            _upsert_job(job_id, status="error", result={"error": str(exc)})
        finally:
            event_queue.put(None)   # sentinel — stream ends

    threading.Thread(target=_run, daemon=True).start()
    return jsonify({"job_id": job_id, "status": "running"})


@app.route("/api/stream/<job_id>")
def stream(job_id: str):
    """SSE endpoint — streams events until the job finishes."""
    job = _get_job(job_id)
    if not job:
        return jsonify({"error": "job not found"}), 404

    live_queue = _get_live_queue(job_id)

    def _generate():
        if live_queue is None:
            latest = _get_job(job_id) or job
            payload = latest.get("result") or {"status": latest.get("status")}
            yield f"event: end\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"
            return

        q: queue.Queue = live_queue
        while True:
            try:
                event = q.get(timeout=30)
            except queue.Empty:
                yield "event: heartbeat\ndata: {}\n\n"
                continue
            if event is None:
                latest = _get_job(job_id) or job
                yield f"event: end\ndata: {json.dumps(latest.get('result') or {}, ensure_ascii=False)}\n\n"
                break
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

    return Response(
        stream_with_context(_generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.route("/api/jobs/<job_id>")
def job_result(job_id: str):
    job = _get_job(job_id)
    if not job:
        return jsonify({"error": "job not found"}), 404
    return jsonify({
        "job_id": job_id,
        "status": job["status"],
        "original_name": job.get("original_name"),
        "result": job.get("result"),
    })


@app.route("/api/jobs/<job_id>/download")
def job_download(job_id: str):
    from flask import send_file

    job = _get_job(job_id)
    if not job:
        return jsonify({"error": "job not found"}), 404

    out_dir = _OUTPUT_DIR / job_id
    md_files = list(out_dir.glob("*.md"))
    if not md_files:
        return jsonify({"error": "No output file found"}), 404
    return send_file(str(md_files[0]), as_attachment=True,
                     download_name=md_files[0].name)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_range(s: str | None) -> tuple[int, int] | None:
    if not s:
        return None
    try:
        parts = s.split("-")
        if len(parts) == 2:
            return (int(parts[0]), int(parts[1]))
        return (int(parts[0]), int(parts[0]))
    except ValueError:
        return None


def run_dev(host: str = "0.0.0.0", port: int = 5000, debug: bool = True) -> None:
    """Start the Flask development server."""
    app.run(host=host, port=port, debug=debug, threaded=True)
