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
COPY pdf_extractor/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ── Application source ────────────────────────────────────────────────────────
COPY pdf_extractor/ pdf_extractor/

# ── Runtime dirs ──────────────────────────────────────────────────────────────
RUN mkdir -p /app/input /app/output /root/.cache/pdf-extractor /root/.EasyOCR

# Keep the Tika JAR in /opt so it survives /tmp wipes between Cloud Run revisions
# (and survives `docker run --tmpfs /tmp` setups).
ENV TIKA_PATH=/opt/tika
RUN mkdir -p ${TIKA_PATH}

ENV EXTRACTOR_WORKERS=4
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
# Cloud Run injects $PORT at runtime (default 8080).
# Pass it through so 'serve' picks it up via --port / $PORT.
ENV PORT=8080

# ── Build-time warmup ─────────────────────────────────────────────────────────
# Runs the full warmup suite — every backend is imported, binaries verified,
# and model files downloaded and baked into the image layer:
#   - EasyOCR: downloads craft_mlt_25k.pth (detection) + latin_g2.pth (recognition)
#     and runs a readtext() inference pass to confirm both models work.
#   - Tika: downloads the JAR into $TIKA_PATH
#   - Tesseract: verifies spa+eng tessdata loads correctly
#   - All other backends: import check + binary availability
# `--skip-on-error` keeps the build green if egress is blocked; the runtime
# `/api/v1/readiness` endpoint will then report what is missing.
RUN python -m pdf_extractor warmup --languages es,en --skip-on-error --quiet

# ── Entrypoint — warmup then serve ───────────────────────────────────────────
# entrypoint.sh runs `warmup` to fully initialize EasyOCR and Tika before
# uvicorn starts accepting requests.  Without this, the first OCR request
# arrives while the backends are still initializing → OOM kill / Network error.
COPY pdf_extractor/docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# ── Healthcheck (Cloud Run / Docker) ─────────────────────────────────────────
# /healthz is a lightweight liveness probe — no PDF processing involved.
# start-period is raised to 120s to cover the runtime warmup (EasyOCR + Tika).
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -sf http://localhost:${PORT}/healthz || exit 1

# ── Default: run the REST API (Cloud Run target) ──────────────────────────────
# Override with `docker run ... python -m pdf_extractor extract ...` for CLI use.
ENTRYPOINT ["/entrypoint.sh"]
CMD ["serve", "--host", "0.0.0.0"]
