"""
features/_base.py — Shared dataclasses for all feature modules.

Every feature exposes:
    def extract(pdf_path: str, page_range: tuple | None = None) -> FeatureResult
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PageResult:
    page: int
    content: str
    content_type: str = "text"   # "text" | "table" | "image"
    backend: str = ""
    confidence: float = 1.0


@dataclass
class FeatureResult:
    feature: str
    pages: list[PageResult] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    markdown: str = ""
    confidence: float = 0.0
    warnings: list[str] = field(default_factory=list)
