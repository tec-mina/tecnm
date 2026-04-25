# PDF Extractor — Agent Contract

Stable, versioned interface for agentic consumers (AI agents, CI pipelines, scripts).

- **Contract version**: `3.0.0`
- **Design**: stateless — no job IDs, no polling, no persistent storage
- **Transports**: HTTP REST (primary) · stdin/stdout NDJSON (CLI)
- **Stability guarantee**: additive changes are minor-version bumps; field
  removals or renames are major-version bumps. Unknown fields MUST be ignored.

---

## Quick start

```bash
# local
python -m pdf_extractor serve --port 8080

# Docker
docker run --rm -p 8080:8080 pdf-extractor:latest

# Cloud Run (PORT env injected automatically)
gcloud run deploy pdf-extractor --image …
```

Interactive docs at `/docs` once the server is running.

---

## HTTP API (v1)

Base path: `/api/v1`

### Authentication (optional)

Set `API_KEY` env var on the server to require:
```
Authorization: Bearer <token>
```

---

### GET /healthz

Liveness probe for Cloud Run / load balancers. No auth required.

```
→ 200  {"status": "ok", "ts": "2026-04-25T12:00:00+00:00"}
```

---

### GET /api/v1/capabilities

Returns availability of every system binary and Python package used by the
pipeline. Call once at session start to know which strategies are usable.

```
→ 200  {system_tools, python_packages, strategies, strategy_discovery_failures}
```

---

### GET /api/v1/strategies[?tier=\<tier\>]

List registered extraction strategies.

```
→ 200  [{name, tier, description, priority, is_heavy,
          requires_python, requires_system}, ...]
```

Tiers: `text` · `ocr` · `tables` · `images` · `fonts` · `layout` · `correct`

---

### POST /api/v1/inspect

Profile a PDF without extracting it. Returns page breakdown and which
strategies the pipeline would select.

```
POST /api/v1/inspect
Content-Type: multipart/form-data
  file: <PDF binary>

→ 200  {pages, scanned_pages, text_native_pages, table_pages,
         lang, suggested_strategies, metadata}
```

---

### POST /api/v1/extract  →  download `.md`

Upload one PDF, receive the extracted Markdown as a file download.
The request blocks until extraction is complete.

```
POST /api/v1/extract
Content-Type: multipart/form-data

  file            required  PDF file (binary)
  strategies      optional  comma-separated, e.g. "text:fast,tables:pdfplumber"
  page_range      optional  "1-10"
  with_images     optional  true|false   (default: false)
  with_structure  optional  true|false   (default: false)
  no_spell        optional  true|false   (default: false)

→ 200
  Content-Type: text/markdown; charset=utf-8
  Content-Disposition: attachment; filename="<original_stem>.md"
  X-Quality-Score: 92.0          # 0–100
  X-Pages: 42
  X-Elapsed-Sec: 3.14
  X-Features-Used: text_fast,tables:pdfplumber
  <body: Markdown content>
```

**Error responses**

| Status | Meaning |
|--------|---------|
| 400 | Bad request (missing file, bad params) |
| 413 | File exceeds `MAX_UPLOAD_MB` limit (default 200 MB) |
| 415 | Not a PDF |
| 500 | Extraction failed — see `{"detail": "…"}` |

---

### POST /api/v1/batch  →  download `.zip`

Upload multiple PDFs, receive a ZIP archive with one `.md` per file plus
a `_summary.json` with metadata. Files that fail are skipped and recorded
in the summary — the request never fails if at least some files succeed.

```
POST /api/v1/batch
Content-Type: multipart/form-data

  files           required  one or more PDF files (field name: "files")
  strategies      optional  applied to all files
  page_range      optional
  with_images     optional
  with_structure  optional
  no_spell        optional

→ 200
  Content-Type: application/zip
  Content-Disposition: attachment; filename="extracted.zip"
  <body: ZIP>
```

**ZIP contents**

```
<stem>.md          one per successfully extracted PDF
_summary.json      per-file metadata array
```

**`_summary.json` schema**

```json
[
  {
    "file":         "ley_adquisiciones.pdf",
    "output":       "ley_adquisiciones.md",
    "status":       "ok",
    "quality_score": 91.5,
    "pages":        38,
    "elapsed_sec":  4.2,
    "features_used": ["text_fast", "tables:pdfplumber"],
    "warnings":     []
  },
  {
    "file":         "corrupt.pdf",
    "status":       "error",
    "error":        "extraction produced no output"
  }
]
```

---

## Quality score interpretation

| Score | Label | Recommendation |
|-------|-------|---------------|
| 90–100 | Excellent | Use as-is |
| 70–89  | Good | Minor review recommended |
| 50–69  | Fair | Check for table/layout issues |
| < 50   | Poor | Re-run with `strategies=ocr:tesseract-advanced` |

If `X-Quality-Score` < 50 and the PDF is scanned, retry with:
```
strategies=ocr:tesseract-advanced
```

---

## CLI reference (NDJSON mode)

```bash
python -m pdf_extractor extract DOC.pdf -o out/ --json
python -m pdf_extractor extract *.pdf   -o out/ --json --strict --quality-threshold 80
python -m pdf_extractor inspect  DOC.pdf --json
python -m pdf_extractor capabilities    --json
python -m pdf_extractor strategies list --json
python -m pdf_extractor serve --port 8080
```

All commands emit NDJSON on stdout. Human diagnostics go to stderr.

### Exit codes (CLI)

| Code | Meaning | Agent action |
|------|---------|--------------|
| 0 | Success | Consume artifacts |
| 1 | Generic error | Report, optionally retry |
| 2 | Quality gate failed (`--quality-threshold`) | Lower threshold or re-run OCR |
| 3 | Preflight failed (corrupt/encrypted/missing) | Human intervention |
| 4 | Blocked — no content extracted | Try different strategy |
| 5 | `--strict`: requested strategy not used | Install missing backend |

---

## Validate issue codes

Issue codes appear in CLI NDJSON `validate` events and in `_summary.json` warnings.

| Code | Severity | Action |
|------|----------|--------|
| `EMPTY_OUTPUT` | critical | Nothing extracted — check the PDF |
| `EMPTY_CONTENT` | critical | Page markers but no text — OCR backend missing |
| `SPARSE_PAGE_CONTENT` | high | OCR ran but yielded almost no text — retry with `ocr:tesseract-advanced` |
| `WRONG_HEADING_HIERARCHY` | high | Heading levels are not sequential |
| `HEADING_LEVEL_JUMPS` | medium | Heading levels skip more than one level |
| `REPEATED_LINES` | medium | Artifact noise — run with `--no-cache` |
| `OVERLONG_LINES` | low | Lines > 500 chars (probable table encoding issue) |
| `TABLE_MISALIGNED` | medium | Column separators not aligned |
| `EMBEDDED_PAGE_NUMBERS` | low | Page numbers interspersed in text |

---

## Versioning

Breaking changes bump the major version. Additive changes are minor bumps.
Pin to a specific image digest for reproducibility.
