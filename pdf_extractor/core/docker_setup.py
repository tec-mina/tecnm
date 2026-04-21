"""
core/docker_setup.py — Auto-install Docker when --docker flag is used.

Handles macOS (Homebrew / direct DMG), Windows (winget / choco / installer),
and Linux (informational only).

All flows emit structured JSON progress events.
After successful install, caches the verified Docker version to skip future checks.
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

from . import progress as prog
from .cache import docker_verified_version, set_docker_verified
from .platform import PlatformInfo

_POLL_INTERVAL = 3      # seconds between docker info checks
_TIMEOUT_MAC = 90       # seconds to wait after open
_TIMEOUT_WIN = 120


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def ensure_docker(platform_info: PlatformInfo) -> bool:
    """
    Ensure Docker is installed and running.
    Returns True if Docker is ready, False if manual intervention is needed.
    """
    # Check cache first
    cached = docker_verified_version()
    if cached:
        # Still verify daemon is running
        if _docker_info_ok():
            return True
        # Daemon stopped; try to start it
        _try_start_daemon(platform_info.os)
        if _poll_docker(10, _POLL_INTERVAL):
            return True

    # Check if docker binary exists
    docker_bin = shutil.which("docker")

    if docker_bin:
        # Binary exists; try to start daemon
        if _docker_info_ok():
            _record_version()
            return True
        _try_start_daemon(platform_info.os)
        if _poll_docker(30, _POLL_INTERVAL):
            _record_version()
            return True
        prog.error("", "Docker daemon not responding after start attempt",
                   suggestion="Open Docker Desktop manually and re-run.")
        return False

    # Docker not installed; install it
    return _install_docker(platform_info)


# ---------------------------------------------------------------------------
# Installation flows
# ---------------------------------------------------------------------------

def _install_docker(platform_info: PlatformInfo) -> bool:
    os_name = platform_info.os

    if os_name == "macos":
        return _install_macos(platform_info)
    elif os_name == "windows":
        return _install_windows()
    else:
        _guide_linux()
        return False


def _install_macos(info: PlatformInfo) -> bool:
    """macOS: try Homebrew first, then direct DMG download."""
    if shutil.which("brew"):
        return _macos_homebrew()
    elif shutil.which("port"):
        prog.error("", "MacPorts detected but not supported for Docker install; falling back to direct download")

    return _macos_dmg(info.arch)


def _macos_homebrew() -> bool:
    prog.emit({"event": "install", "tool": "docker", "method": "homebrew", "status": "starting"})
    try:
        subprocess.run(["brew", "install", "--cask", "docker"], check=True)
    except subprocess.CalledProcessError as exc:
        prog.error("", f"brew install docker failed: {exc}")
        return False

    subprocess.run(["open", "-a", "Docker"], check=False)
    prog.emit({"event": "install", "tool": "docker", "method": "homebrew", "status": "waiting"})

    if _poll_docker(_TIMEOUT_MAC, _POLL_INTERVAL):
        prog.emit({"event": "install", "tool": "docker", "method": "homebrew", "status": "done"})
        _record_version()
        return True

    _print_manual_guide("macos")
    return False


def _macos_dmg(arch: str) -> bool:
    urls = {
        "arm64":  "https://desktop.docker.com/mac/main/arm64/Docker.dmg",
        "x86_64": "https://desktop.docker.com/mac/main/amd64/Docker.dmg",
    }
    url = urls.get(arch, urls["x86_64"])

    prog.emit({"event": "install", "tool": "docker", "method": "dmg", "status": "downloading"})

    with tempfile.TemporaryDirectory() as tmpdir:
        dmg_path = Path(tmpdir) / "Docker.dmg"
        try:
            urllib.request.urlretrieve(url, dmg_path)
        except Exception as exc:
            prog.error("", f"Failed to download Docker DMG: {exc}")
            _print_manual_guide("macos")
            return False

        try:
            subprocess.run(["hdiutil", "attach", str(dmg_path)], check=True)
            subprocess.run(["cp", "-R", "/Volumes/Docker/Docker.app", "/Applications/"], check=True)
            subprocess.run(["hdiutil", "detach", "/Volumes/Docker"], check=False)
        except subprocess.CalledProcessError as exc:
            prog.error("", f"Docker DMG install failed: {exc}")
            _print_manual_guide("macos")
            return False

    subprocess.run(["open", "/Applications/Docker.app"], check=False)
    prog.emit({"event": "install", "tool": "docker", "method": "dmg", "status": "waiting"})

    if _poll_docker(_TIMEOUT_MAC, _POLL_INTERVAL):
        prog.emit({"event": "install", "tool": "docker", "method": "dmg", "status": "done"})
        _record_version()
        return True

    _print_manual_guide("macos")
    return False


def _install_windows() -> bool:
    """Windows: try winget → choco → direct installer."""
    if shutil.which("winget"):
        return _windows_winget()
    if shutil.which("choco"):
        return _windows_choco()
    return _windows_direct_installer()


def _windows_winget() -> bool:
    prog.emit({"event": "install", "tool": "docker", "method": "winget", "status": "starting"})
    try:
        subprocess.run(
            ["winget", "install", "-e", "--id", "Docker.DockerDesktop",
             "--accept-package-agreements", "--accept-source-agreements"],
            check=True
        )
    except subprocess.CalledProcessError as exc:
        prog.error("", f"winget install failed: {exc}")
        return _windows_direct_installer()

    if _poll_docker(_TIMEOUT_WIN, _POLL_INTERVAL):
        prog.emit({"event": "install", "tool": "docker", "method": "winget", "status": "done"})
        _record_version()
        return True

    _print_manual_guide("windows")
    return False


def _windows_choco() -> bool:
    prog.emit({"event": "install", "tool": "docker", "method": "chocolatey", "status": "starting"})
    try:
        subprocess.run(["choco", "install", "docker-desktop", "-y"], check=True)
    except subprocess.CalledProcessError as exc:
        prog.error("", f"choco install failed: {exc}")
        return _windows_direct_installer()

    if _poll_docker(_TIMEOUT_WIN, _POLL_INTERVAL):
        prog.emit({"event": "install", "tool": "docker", "method": "chocolatey", "status": "done"})
        _record_version()
        return True

    _print_manual_guide("windows")
    return False


def _windows_direct_installer() -> bool:
    url = "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe"
    prog.emit({"event": "install", "tool": "docker", "method": "installer", "status": "downloading"})

    tmp_dir = Path(os.environ.get("TEMP", tempfile.gettempdir()))
    installer = tmp_dir / "DockerInstaller.exe"

    try:
        urllib.request.urlretrieve(url, installer)
    except Exception as exc:
        prog.error("", f"Failed to download Docker installer: {exc}")
        _print_manual_guide("windows")
        return False

    ps_cmd = (
        f'Start-Process -FilePath "{installer}" '
        '-ArgumentList "install","--quiet","--accept-license" -Wait'
    )
    try:
        subprocess.run(["powershell", "-Command", ps_cmd], check=True)
    except subprocess.CalledProcessError as exc:
        prog.error("", f"Docker installer failed: {exc}")
        _print_manual_guide("windows")
        return False

    if _poll_docker(_TIMEOUT_WIN, _POLL_INTERVAL):
        prog.emit({"event": "install", "tool": "docker", "method": "installer", "status": "done"})
        _record_version()
        return True

    _print_manual_guide("windows")
    return False


def _guide_linux() -> None:
    """Print distro-specific installation guidance for Linux."""
    prog.emit({"event": "install", "tool": "docker", "method": "manual", "status": "guidance"})
    distro = _detect_linux_distro()
    guides = {
        "ubuntu": "sudo apt install docker.io && sudo systemctl start docker",
        "debian": "sudo apt install docker.io && sudo systemctl start docker",
        "fedora": "sudo dnf install docker && sudo systemctl start docker",
        "arch":   "sudo pacman -S docker && sudo systemctl start docker",
    }
    cmd = guides.get(distro, "# See https://docs.docker.com/engine/install/")
    print(f"\nDocker not found. Install it with:\n  {cmd}")
    print("Then add yourself to the docker group:")
    print("  sudo usermod -aG docker $USER")


def _detect_linux_distro() -> str:
    try:
        text = Path("/etc/os-release").read_text().lower()
        for name in ("ubuntu", "debian", "fedora", "arch"):
            if name in text:
                return name
    except OSError:
        pass
    return "unknown"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _docker_info_ok() -> bool:
    try:
        r = subprocess.run(
            ["docker", "info"],
            capture_output=True, timeout=10
        )
        return r.returncode == 0
    except Exception:
        return False


def _try_start_daemon(os_name: str) -> None:
    if os_name == "macos":
        subprocess.run(["open", "-a", "Docker"], check=False)
    elif os_name == "linux":
        subprocess.run(["sudo", "systemctl", "start", "docker"], check=False)


def _poll_docker(timeout: int, interval: int) -> bool:
    elapsed = 0
    while elapsed < timeout:
        if _docker_info_ok():
            return True
        time.sleep(interval)
        elapsed += interval
    return False


def _record_version() -> None:
    try:
        r = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        version = r.stdout.strip()
        set_docker_verified(version)
        prog.emit({"event": "install", "tool": "docker", "version": version, "status": "verified"})
    except Exception:
        pass


def _print_manual_guide(os_name: str) -> None:
    if os_name == "macos":
        msg = (
            "Docker Desktop was installed but did not start in time.\n"
            "Open Docker Desktop from /Applications and re-run this command."
        )
    else:
        msg = (
            "Docker Desktop was installed. Please:\n"
            "  1. Open Docker Desktop from the Start Menu.\n"
            "  2. Complete the first-run setup wizard.\n"
            "  3. Re-run this command once the whale icon appears in the system tray."
        )
    prog.error("", msg, suggestion="Start Docker Desktop manually then re-run.")
    print(msg, file=sys.stderr)


# ---------------------------------------------------------------------------
# Image build
# ---------------------------------------------------------------------------

_IMAGE_NAME = "pdf-extractor:latest"


def build_image(repo_root: Path | None = None) -> bool:
    """Build the pdf-extractor Docker image if it doesn't already exist.

    The build context is the repo root; the Dockerfile lives at
    pdf_extractor/docker/Dockerfile inside it.
    """
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[2]

    # Fast path: image already present
    r = subprocess.run(
        ["docker", "image", "inspect", _IMAGE_NAME],
        capture_output=True,
    )
    if r.returncode == 0:
        return True

    dockerfile = repo_root / "pdf_extractor" / "docker" / "Dockerfile"
    prog.emit({"event": "docker_build", "image": _IMAGE_NAME, "status": "starting"})
    print(f"[pdf-extractor] Building Docker image {_IMAGE_NAME} — first run only, this takes ~2 min...",
          file=sys.stderr, flush=True)

    try:
        proc = subprocess.Popen(
            ["docker", "build", "-t", _IMAGE_NAME,
             "-f", str(dockerfile), str(repo_root)],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1,
        )
        assert proc.stdout is not None
        for line in proc.stdout:
            print(f"  {line}", end="", file=sys.stderr, flush=True)
        proc.wait()
    except Exception as exc:
        prog.error("", f"Docker build error: {exc}")
        return False

    if proc.returncode == 0:
        prog.emit({"event": "docker_build", "image": _IMAGE_NAME, "status": "done"})
        return True

    prog.error("", f"Docker build failed (exit {proc.returncode})",
               suggestion="Run: docker build -t pdf-extractor:latest -f pdf_extractor/docker/Dockerfile .")
    return False


# ---------------------------------------------------------------------------
# Run extraction inside Docker
# ---------------------------------------------------------------------------

def run_in_docker(
    pdf_path: str,
    output_dir: str,
    extra_args: list[str],
    platform_info: PlatformInfo,
) -> int:
    """Build image if needed, then run extraction inside Docker, streaming output."""
    repo_root = Path(__file__).resolve().parents[2]

    if not build_image(repo_root):
        return 1

    cache_root = Path.home() / ".cache" / "pdf-extractor"
    cache_root.mkdir(parents=True, exist_ok=True)

    abs_pdf   = Path(pdf_path).resolve()
    abs_out   = Path(output_dir).resolve()
    abs_out.mkdir(parents=True, exist_ok=True)

    cmd = [
        "docker", "run", "--rm",
        "-v", f"{abs_pdf.parent}:/app/input:ro",
        "-v", f"{abs_out}:/app/output",
        "-v", f"{cache_root}:/root/.cache/pdf-extractor",
        _IMAGE_NAME,
        f"/app/input/{abs_pdf.name}",
        "--output-dir", "/app/output",
        "--no-docker",          # prevent re-entry inside the container
    ] + extra_args

    prog.emit({"event": "docker_run", "file": abs_pdf.name, "image": _IMAGE_NAME})

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            text=True, bufsize=1,
        )
        assert proc.stdout is not None
        for line in proc.stdout:          # stream JSON progress events back to caller
            print(line, end="", flush=True)
        proc.wait()
        return proc.returncode
    except Exception as exc:
        prog.error("", f"Docker run error: {exc}")
        return 1
