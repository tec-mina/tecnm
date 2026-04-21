"""
app/ports.py — Abstract interfaces (Protocols) for all infrastructure dependencies.

High-level use-cases depend ONLY on these protocols — never on concrete
implementations.  This is the Dependency Inversion Principle in practice:
  - ExtractUseCase depends on IEventEmitter, not on core/progress.py
  - InspectUseCase depends on IEventEmitter, not on sys.stdout
  - Any transport (CLI stdout, WebSocket, SSE, gRPC) satisfies IEventEmitter

Usage
-----
    from pdf_extractor.app.ports import IEventEmitter

    class MyLogger:
        def __call__(self, event: dict) -> None:
            print(json.dumps(event))          # CLI
            # OR: ws.send(json.dumps(event))  # WebSocket
            # OR: queue.put(event)            # async
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class IEventEmitter(Protocol):
    """Single-method callback for structured events.

    An event is always a dict with at least ``{"event": str}``.
    The implementation decides how to format and route it.
    """

    def __call__(self, event: dict[str, Any]) -> None: ...


def noop_emitter(event: dict[str, Any]) -> None:
    """Default no-op emitter — use when logging is not needed (tests, batch quiet)."""
