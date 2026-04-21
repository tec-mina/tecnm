"""
core/platform.py — OS detection and best available feature set selection.

Determines platform-specific paths and feature preferences.
"""

import platform
import shutil
import sys
from dataclasses import dataclass, field


@dataclass
class PlatformInfo:
    os: str               # "macos" | "linux" | "windows"
    arch: str             # "arm64" | "x86_64" | "amd64"
    tesseract_path: str | None
    preferred_features: list[str] = field(default_factory=list)
    skip_features: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def detect() -> PlatformInfo:
    """Detect OS/arch and return feature preferences."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == "darwin":
        os_name = "macos"
    elif system == "windows":
        os_name = "windows"
    else:
        os_name = "linux"

    arch = "arm64" if "arm" in machine or machine == "aarch64" else "x86_64"

    # Locate Tesseract
    tesseract_path = _find_tesseract(os_name)

    info = PlatformInfo(os=os_name, arch=arch, tesseract_path=tesseract_path)

    if os_name == "macos":
        info.preferred_features = ["markdown_llm", "tables", "text_fast"]
        info.notes.append("macOS: prefer pymupdf4llm + pdfplumber; Tesseract via Homebrew")

    elif os_name == "linux":
        info.preferred_features = ["markdown_llm", "tables", "text_fast",
                                    "tables_camelot", "ocr_tesseract", "ocr_easy", "docling_feat"]
        info.notes.append("Linux: full stack supported; camelot requires ghostscript")

    elif os_name == "windows":
        info.preferred_features = ["markitdown_feat", "tables", "text_fast", "markdown_llm"]
        # EasyOCR on Windows without CUDA is slow; skip by default
        try:
            import torch
            if not torch.cuda.is_available():
                info.skip_features.append("ocr_easy")
                info.notes.append("Windows: EasyOCR skipped (no CUDA detected)")
        except ImportError:
            info.skip_features.append("ocr_easy")
            info.notes.append("Windows: EasyOCR skipped (torch not installed)")
        info.notes.append("Windows: prefer markitdown + pdfplumber; PowerShell launcher for Docker")

    return info


def _find_tesseract(os_name: str) -> str | None:
    """Find tesseract binary according to platform conventions."""
    # Try PATH first
    found = shutil.which("tesseract")
    if found:
        return found

    if os_name == "macos":
        candidates = [
            "/opt/homebrew/bin/tesseract",   # Apple Silicon Homebrew
            "/usr/local/bin/tesseract",       # Intel Homebrew
            "/opt/local/bin/tesseract",       # MacPorts
        ]
    elif os_name == "windows":
        import os
        prog_files = os.environ.get("PROGRAMFILES", "C:\\Program Files")
        candidates = [
            f"{prog_files}\\Tesseract-OCR\\tesseract.exe",
            "C:\\Program Files\\Tesseract-OCR\\tesseract.exe",
            "C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe",
        ]
    else:
        candidates = ["/usr/bin/tesseract", "/usr/local/bin/tesseract"]

    for path in candidates:
        if shutil.which(path) or __import__("pathlib").Path(path).exists():
            return path

    return None


def get_docker_platform_args(info: PlatformInfo) -> list[str]:
    """Return --platform docker args if cross-building needed."""
    if info.os == "macos" and info.arch == "arm64":
        return ["--platform", "linux/arm64"]
    return ["--platform", "linux/amd64"]
