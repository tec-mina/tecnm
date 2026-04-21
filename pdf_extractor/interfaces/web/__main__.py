"""
interfaces/web/__main__.py — Entry point for the Flask web server.

Usage:
    python -m pdf_extractor.interfaces.web            # default: 0.0.0.0:5000
    python -m pdf_extractor.interfaces.web --port 8080
    python -m pdf_extractor.interfaces.web --no-debug

Docker:
    docker run --rm -p 5000:5000 \\
      -v $(pwd):/app/input \\
      pdf-extractor:latest web
"""

from __future__ import annotations

import argparse

from .app import run_dev


def main() -> None:
    parser = argparse.ArgumentParser(description="PDF Extractor — web interface")
    parser.add_argument("--host",  default="0.0.0.0")
    parser.add_argument("--port",  default=5000, type=int)
    parser.add_argument("--no-debug", dest="debug", action="store_false", default=True)
    args = parser.parse_args()
    print(f"Starting PDF Extractor web UI → http://{args.host}:{args.port}")
    run_dev(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
