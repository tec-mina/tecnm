"""
core/ocr_config.py — Centralized OCR resilience configuration.

All OCR backends (EasyOCR, Tesseract, etc.) should use these settings
for consistent timeout, retry, and error handling behavior.

Environment variables override defaults:
- OCR_MAX_RETRIES: max retry attempts
- OCR_INITIAL_BACKOFF: initial backoff in seconds
- OCR_PAGE_TIMEOUT: timeout per page in seconds
- OCR_INIT_TIMEOUT: timeout for initialization in seconds
- OCR_OFFLINE_MODE: "1" to force offline (cached models only)
"""

from __future__ import annotations

import os
import logging

logger = logging.getLogger(__name__)

# Defaults
DEFAULT_MAX_RETRIES = 3
DEFAULT_INITIAL_BACKOFF = 2.0
DEFAULT_PAGE_TIMEOUT = 30.0
DEFAULT_INIT_TIMEOUT = 60.0


class OCRConfig:
    """Centralized OCR configuration from env vars or defaults."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._load_from_env()

    def _load_from_env(self):
        """Load configuration from environment variables."""
        self.max_retries = int(os.getenv("OCR_MAX_RETRIES", DEFAULT_MAX_RETRIES))
        self.initial_backoff = float(
            os.getenv("OCR_INITIAL_BACKOFF", DEFAULT_INITIAL_BACKOFF)
        )
        self.page_timeout = float(
            os.getenv("OCR_PAGE_TIMEOUT", DEFAULT_PAGE_TIMEOUT)
        )
        self.init_timeout = float(
            os.getenv("OCR_INIT_TIMEOUT", DEFAULT_INIT_TIMEOUT)
        )
        self.offline_mode = os.getenv("OCR_OFFLINE_MODE", "0") == "1"

        logger.info(
            f"OCR config: max_retries={self.max_retries}, "
            f"backoff={self.initial_backoff}s, "
            f"page_timeout={self.page_timeout}s, "
            f"init_timeout={self.init_timeout}s, "
            f"offline={self.offline_mode}"
        )

    def to_dict(self) -> dict:
        """Export as dictionary for logging/debugging."""
        return {
            "max_retries": self.max_retries,
            "initial_backoff": self.initial_backoff,
            "page_timeout": self.page_timeout,
            "init_timeout": self.init_timeout,
            "offline_mode": self.offline_mode,
        }


def get_config() -> OCRConfig:
    """Get singleton OCR configuration."""
    return OCRConfig()


def reset_config():
    """Reset singleton (useful for testing)."""
    OCRConfig._instance = None
