"""
core/progress.py — Structured JSON progress events emitted to stdout.

All progress communication happens through this module.
Errors go to stderr; events go to stdout.
tqdm bars are activated only when stdout is a TTY and --format != json.
"""

import json
import sys
import time
from datetime import datetime, timezone
from typing import Any


_tty_mode: bool = sys.stdout.isatty()
_json_mode: bool = False  # set by CLI when --format json


def configure(json_mode: bool) -> None:
    """Called once by CLI to configure output mode."""
    global _json_mode
    _json_mode = json_mode


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def emit(event: dict[str, Any]) -> None:
    """Emit a newline-delimited JSON event to stdout."""
    event.setdefault("ts", _ts())
    print(json.dumps(event, ensure_ascii=False), flush=True)


def start(file: str, pages: int) -> None:
    emit({"event": "start", "file": file, "pages": pages})


def preflight(file: str, status: str, is_scanned: bool = False, **kwargs: Any) -> None:
    emit({"event": "preflight", "file": file, "status": status,
          "is_scanned": is_scanned, **kwargs})


def cache_hit(file: str, key: str) -> None:
    emit({"event": "cache_hit", "file": file, "key": key})


def detect(file: str, profile: dict[str, Any]) -> None:
    emit({"event": "detect", "file": file, "profile": profile})


def feature_running(file: str, feature: str, page: int | None = None) -> None:
    d: dict[str, Any] = {"event": "feature", "file": file, "feature": feature, "status": "running"}
    if page is not None:
        d["page"] = page
    emit(d)


def feature_done(file: str, feature: str, confidence: float) -> None:
    emit({"event": "feature", "file": file, "feature": feature,
          "status": "done", "confidence": confidence})


def feature_skipped(file: str, feature: str, reason: str) -> None:
    emit({"event": "feature", "file": file, "feature": feature,
          "status": "skipped", "reason": reason})


def page_done(file: str, page: int, total: int) -> None:
    pct = round(page / total * 100, 1) if total else 0.0
    emit({"event": "page_done", "file": file, "page": page, "pct": pct})


def fix_applied(file: str, fix: str, count: int) -> None:
    emit({"event": "fix_applied", "file": file, "fix": fix, "count": count})


def validate(file: str, status: str, quality_score: float) -> None:
    emit({"event": "validate", "file": file, "status": status,
          "quality_score": quality_score})


def done(file: str, output: str, features_used: list[str]) -> None:
    emit({"event": "done", "file": file, "output": output,
          "features_used": features_used})


def error(file: str, msg: str, feature: str | None = None, **kwargs: Any) -> None:
    d: dict[str, Any] = {"event": "error", "file": file, "msg": msg}
    if feature:
        d["feature"] = feature
    d.update(kwargs)
    print(json.dumps(d, ensure_ascii=False), file=sys.stderr, flush=True)


# ---------------------------------------------------------------------------
# Optional tqdm helper (only when TTY and not json mode)
# ---------------------------------------------------------------------------

def make_tqdm(iterable, total: int, desc: str = ""):
    """Return a tqdm-wrapped iterable if available and in TTY mode, else plain."""
    if _tty_mode and not _json_mode:
        try:
            from tqdm import tqdm
            return tqdm(iterable, total=total, desc=desc, file=sys.stderr)
        except ImportError:
            pass
    return iterable
