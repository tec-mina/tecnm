"""Entry point for python -m pdf_extractor"""
from .interfaces.cli import main
import sys

sys.exit(main())
