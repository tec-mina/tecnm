"""
features/_network_utils.py — Network resilience utilities for OCR backends.

Shared by EasyOCR, Tesseract, and other methods that may need network
access for model downloads or external services.

Provides:
- Network connectivity check
- Configurable retry logic with exponential backoff
- Timeout handling
- Offline mode support
- Clear error reporting
"""

from __future__ import annotations

import socket
import time
import logging
from typing import Callable, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")

NETWORK_TEST_HOST = "8.8.8.8"  # Google DNS
NETWORK_TEST_PORT = 53
DEFAULT_NETWORK_TIMEOUT = 3.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_INITIAL_BACKOFF = 2.0


def check_network(
    host: str = NETWORK_TEST_HOST,
    port: int = NETWORK_TEST_PORT,
    timeout_sec: float = DEFAULT_NETWORK_TIMEOUT,
) -> bool:
    """Check if network is available via DNS query.

    Args:
        host: Host to test (default: Google DNS)
        port: Port to test (default: 53)
        timeout_sec: Timeout in seconds

    Returns:
        True if network is reachable, False otherwise.
    """
    try:
        socket.create_connection((host, port), timeout=timeout_sec)
        logger.debug("Network connectivity verified")
        return True
    except (socket.timeout, socket.gaierror, ConnectionRefusedError, OSError) as e:
        logger.warning(f"Network check failed: {e}")
        return False


def retry_with_backoff(
    func: Callable[[], T],
    max_retries: int = DEFAULT_MAX_RETRIES,
    initial_backoff_sec: float = DEFAULT_INITIAL_BACKOFF,
    name: str = "operation",
    on_retry: Callable[[int, Exception], None] | None = None,
) -> T | None:
    """Execute function with exponential backoff retries on network/timeout errors.

    Args:
        func: Callable to execute
        max_retries: Number of retries
        initial_backoff_sec: Initial backoff duration
        name: Operation name for logging
        on_retry: Optional callback on retry: on_retry(attempt_number, exception)

    Returns:
        Result from func or None if all retries failed.
    """
    backoff = initial_backoff_sec
    last_exc = None

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"{name} attempt {attempt}/{max_retries}...")
            return func()
        except Exception as exc:
            last_exc = exc
            is_network_error = _is_network_or_timeout_error(exc)

            if attempt < max_retries and is_network_error:
                if on_retry:
                    on_retry(attempt, exc)
                logger.warning(
                    f"{name} attempt {attempt} failed (network/timeout): {exc}. "
                    f"Retrying in {backoff:.1f}s..."
                )
                time.sleep(backoff)
                backoff *= 2.0  # exponential backoff
            else:
                logger.error(f"{name} attempt {attempt} failed: {exc}")
                break

    logger.error(f"{name} failed after {max_retries} attempts. Last error: {last_exc}")
    return None


def _is_network_or_timeout_error(exc: Exception) -> bool:
    """Detect if an exception is a network or timeout error."""
    exc_str = str(exc).lower()
    timeout_keywords = ["timeout", "timed out"]
    network_keywords = [
        "network",
        "connection",
        "refused",
        "unreachable",
        "url",
        "http",
        "socket",
        "dns",
        "nameresolution",
    ]

    is_timeout = any(kw in exc_str for kw in timeout_keywords)
    is_network = any(kw in exc_str for kw in network_keywords)

    return is_timeout or is_network or isinstance(
        exc,
        (
            socket.error,
            socket.timeout,
            ConnectionError,
            ConnectionRefusedError,
            TimeoutError,
        ),
    )


class OfflineMode:
    """Context manager for offline mode."""

    def __init__(self, env_var_name: str = "EASYOCR_OFFLINEMODE"):
        self.env_var = env_var_name
        self.old_value = None

    def __enter__(self):
        import os

        self.old_value = os.environ.get(self.env_var)
        os.environ[self.env_var] = "1"
        logger.info(f"Offline mode enabled ({self.env_var}=1)")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        import os

        if self.old_value is None:
            os.environ.pop(self.env_var, None)
        else:
            os.environ[self.env_var] = self.old_value
        logger.info(f"Offline mode disabled")


def report_failure(
    component: str,
    reason: str,
    suggestion: str = "",
    logs: list[str] | None = None,
) -> str:
    """Format a clear failure report for user-facing messages.

    Args:
        component: Name of the component that failed
        reason: Why it failed
        suggestion: What to try next
        logs: Optional list of log lines

    Returns:
        Formatted message suitable for warnings list.
    """
    msg = f"{component} failed: {reason}"
    if suggestion:
        msg += f". {suggestion}"
    if logs:
        msg += f" ({len(logs)} error(s) logged)"
    return msg
