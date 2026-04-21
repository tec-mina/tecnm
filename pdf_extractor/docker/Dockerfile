FROM python:3.11-slim

# ── System dependencies ──────────────────────────────────────────────────────
# Each group is annotated so the Dockerfile serves as the authoritative
# inventory of available extraction capabilities.
RUN apt-get update && apt-get install -y --no-install-recommends \
    \
    # ── PDF rendering & manipulation ────────────────────────────────────── \
    # poppler-utils : pdftotext, pdfimages, pdfinfo, pdffonts, pdftoppm      \
    # qpdf          : split, merge, decrypt, inspect PDFs                    \
    # pdftk-java    : form-field extraction, bookmarks, page labels          \
    # mupdf-tools   : mutool — font inspect, text with coords, image extract \
    poppler-utils \
    ghostscript \
    qpdf \
    pdftk-java \
    mupdf-tools \
    \
    # ── OCR — Tesseract + language + orientation data ─────────────────── \
    tesseract-ocr \
    tesseract-ocr-spa \
    tesseract-ocr-eng \
    tesseract-ocr-osd \
    \
    # ── Scanned-page preprocessing ───────────────────────────────────────  \
    # unpaper     : deskew, border removal, noise reduction for scanned pages \
    # imagemagick : general-purpose image conversion & manipulation           \
    unpaper \
    imagemagick \
    \
    # ── Java runtime (tabula-py + Apache Tika) ───────────────────────── \
    default-jre-headless \
    \
    # ── Image codec C libraries — needed by Pillow, PyMuPDF, OpenCV ──────  \
    # libopenjp2-7  : JPEG2000 — common in PDFs with compressed images       \
    # libwebp7      : WebP codec                                             \
    # liblcms2-2    : ICC color management (color-accurate image handling)   \
    # libjpeg62-turbo : fast JPEG codec                                      \
    # libtiff6      : TIFF support                                           \
    # libleptonica6 : image analysis library used internally by Tesseract    \
    libopenjp2-7 \
    libwebp7 \
    liblcms2-2 \
    libjpeg62-turbo \
    libtiff6 \
    libleptonica6 \
    \
    # ── Font rendering C libraries ────────────────────────────────────────  \
    # libfreetype6  : FreeType font renderer (PyMuPDF, Pillow, Cairo)        \
    # libfontconfig1: font discovery and substitution                        \
    libfreetype6 \
    libfontconfig1 \
    \
    # ── Image / rendering shared libraries ───────────────────────────────  \
    libgl1 \
    libglib2.0-0 \
    libmagic1 \
    \
    # ── Text layout & vector rendering (WeasyPrint / Pango / Cairo) ─────  \
    # Enables high-fidelity HTML→PDF and font-metric extraction              \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libharfbuzz0b \
    \
    # ── XML / XSLT C libraries ────────────────────────────────────────────  \
    libxml2 \
    libxslt1.1 \
    \
    # ── Metadata extraction ───────────────────────────────────────────────  \
    # exiftool : reads EXIF/XMP/ICC/PDF metadata from any file               \
    libimage-exiftool-perl \
    \
    # ── Fonts — required for proper PDF text rendering ───────────────────  \
    fonts-liberation \
    fonts-open-sans \
    \
    # ── Utilities ────────────────────────────────────────────────────────  \
    curl \
    \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ── Python dependencies (cached layer — rebuilt only when requirements change) ─
COPY pdf_extractor/requirements/base.txt     requirements/base.txt
COPY pdf_extractor/requirements/ocr.txt      requirements/ocr.txt
COPY pdf_extractor/requirements/advanced.txt requirements/advanced.txt
COPY pdf_extractor/requirements/all.txt      requirements/all.txt
RUN pip install --no-cache-dir -r requirements/all.txt

# ── Application source ────────────────────────────────────────────────────────
COPY pdf_extractor/ pdf_extractor/

# ── Runtime dirs ──────────────────────────────────────────────────────────────
RUN mkdir -p /app/input /app/output /root/.cache/pdf-extractor

ENV EXTRACTOR_WORKERS=4
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# ── Healthcheck ───────────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=2 \
    CMD python -m pdf_extractor --help > /dev/null 2>&1 || exit 1

ENTRYPOINT ["python", "-m", "pdf_extractor"]
CMD ["--help"]
