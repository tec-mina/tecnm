#!/usr/bin/env python3
"""
bootstrap_env.py - Create a local virtual environment for this skill.

Usage:
    python scripts/bootstrap_env.py
    python scripts/bootstrap_env.py --extras docling camelot ocr
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import venv
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
VENV_DIR = SKILL_ROOT / ".venv"
BASE_REQUIREMENTS = SKILL_ROOT / "requirements.txt"

EXTRA_GROUPS = {
    "docling": ["docling", "docling-core", "huggingface_hub"],
    "camelot": ["camelot-py", "opencv-python"],
    "ocr": ["img2table", "rapidocr-onnxruntime", "pytesseract", "pdf2image", "pypdfium2"],
}


def python_bin() -> Path:
    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def create_venv() -> None:
    if VENV_DIR.exists():
        return
    venv.create(VENV_DIR, with_pip=True)


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Bootstrap a virtual environment for pdf-markdown-codex")
    parser.add_argument(
        "--extras",
        nargs="*",
        choices=sorted(EXTRA_GROUPS.keys()),
        default=[],
        help="Optional dependency groups to install",
    )
    args = parser.parse_args()

    create_venv()
    py = python_bin()

    run([str(py), "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])
    run([str(py), "-m", "pip", "install", "-r", str(BASE_REQUIREMENTS)])

    for group in args.extras:
        packages = EXTRA_GROUPS[group]
        run([str(py), "-m", "pip", "install", *packages])

    print(f"Virtual environment ready: {VENV_DIR}")
    print(f"Python: {py}")


if __name__ == "__main__":
    main()
