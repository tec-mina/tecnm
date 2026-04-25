# PDF Extractor — Agent Contract

Stable, versioned interface for agentic consumers (Claude Skills, Copilot agents,
GitHub Actions, internal bots).

- **Contract version**: `2.0.0`
- **Transports**: HTTP REST + SSE (primary) · stdin/stdout NDJSON (CLI, legacy)
- **Stability guarantee**: additive changes are minor-version bumps; field
  removals or renames are major-version bumps. Unknown fields MUST be ignored
  by consumers.

---

## Transports at a glance

| Mode | When to use | Entry point |
|------|-------------|-------------|
| **API (HTTP)** | Cloud Run, any network client, AI agents over HTTP | `python -m pdf_extractor serve` |
| **CLI (stdout NDJSON)** | Local scripts, CI pipelines, shell agents | `python -m pdf_extractor extract … --json` |

---

## Quick start

### API server
```bash
# local
python -m pdf_extractor serve --port 8080

# Docker
docker run --rm -p 8080:8080 pdf-extractor:latest

# Cloud Run (PORT env injected automatically)
gcloud run deploy pdf-extractor --image …
```

Interactive docs at `/docs` once the server is running.

### CLI
```bash
python -m pdf_extractor <command> [args] --json
```

All commands emit NDJSON on stdout. Human diagnostics go to stderr.

---

## HTTP API (v1)

Base path: `/api/v1`

### Authentication (optional)

Set `API_KEY` env var on the server to require:
```
Authorization: Bearer <token>
```

### Liveness probe
```
GET /healthz
→ 200  {"status": "ok", "ts": "..."}
```

### Capabilities
```
GET /api/v1/capabilities
→ 200  {system_tools, python_packages, strategies, strategy_discovery_failures}
```

Agents SHOULD call this once at session start.

### Strategies
```
GET /api/v1/strategies[?tier=<tier>]
→ 200  [{name, tier, description, priority, is_heavy, requires_python, requires_system}, ...]
```

Tiers: `text` · `ocr` · `tables` · `images` · `fonts` · `layout` · `correct`

### Inspect (profile without extracting)
```
POST /api/v1/inspect
Content-Type: multipart/form-data
  file: <PDF binary>

→ 200  {pages, scanned_pages, text_native_pages, table_pages, lang,
         suggested_strategies, metadata}
```

### Extract (single PDF)
```
POST /api/v1/extract
Content-Type: multipart/form-data
  file:           <PDF binary>          required
  strategies:     "text:fast,tables:…"  optional  (default: auto)
  page_range:     "1-10"               optional
  with_images:    true|false           optional  (default: false)
  with_structure: true|false           optional  (default: false)
  no_spell:       true|false           optional  (default: false)

→ 202  {"job_id": "…", "filename": "…", "status": "queued"}
```

### Stream extraction events (SSE)
```
GET /api/v1/extract/{job_id}/stream
→ 200  text/event-stream

Each line:  data: <JSON>\n\n
Last line:  data: {"event":"stream_end","ts":"…"}\n\n
```

Reconnect if the connection drops before `stream_end`.

### Get extraction result
```
GET /api/v1/extract/{job_id}
→ 202  {"job_id":"…", "status":"running"}   (still in progress)
→ 200  {
          "job_id":       "…",
          "status":       "ok"|"error"|"blocked"|"cached",
          "filename":     "…",
          "quality":      92.0,
          "elapsed_sec":  2.3,
          "output_files": ["…/doc.md"],
          "markdown":     "…",        // inline if single file < 1 MB, else null
          "events":       [{…}, …],   // full event log
          "error":        null
       }
→ 404  {"error":"job not found"}
```

### Batch (multiple PDFs)
```
POST /api/v1/batch
Content-Type: multipart/form-data
  files[]:    <PDF binary> …  required (one or more)
  strategies, page_range, with_images, with_structure, no_spell — same as /extract

→ 202  {"batch_id":"…", "jobs":[{"job_id":"…","filename":"…"}, …]}

GET /api/v1/batch/{batch_id}
→ 200  {"batch_id","total","done","failed","running",
         "jobs":[{"job_id","filename","status"}, …]}
```

### Error responses
All errors:
```json
{"error": "…", "detail": "…"|null}
```

---

## Event stream contract

Every event has at minimum `{"event": str, "ts": ISO-8601-UTC}`.
The stream is identical over SSE (`/stream`) and CLI (`--json`).

### Lifecycle of one extraction

```
preflight → profile → [cache_hit | strategy_plan → (feature_start → feature_done|feature_skip)* → validate → fix]
         → done
```

`error` may appear at any point and terminates the run.

### Event reference

| Event            | Key payload fields |
|------------------|--------------------|
| `preflight`      | `file`, `ok`, `pages`, `size_mb`, `is_scanned`, `warnings[]` |
| `profile`        | `scanned`, `text`, `tables`, `lang`, `has_images` |
| `cache_hit`      | `key`, `output` |
| `strategy_plan`  | `strategies[]` |
| `feature_start`  | `name`, `tier` |
| `feature_done`   | `name`, `tier`, `confidence` (0.0–1.0, always > 0) |
| `feature_skip`   | `name`, `tier`, `reason` |
| `validate`       | `status` ∈ {PASS, ISSUES_FOUND, BLOCKED}, `score` (0–100), `issues` (int), `issues_detail[]` |
| `fix`            | `fixes` (object: fix_name → count) |
| `done`           | `output`, `quality`, `status`, `features[]`, `elapsed_sec` |
| `error`          | `phase`, `msg` |
| `stream_end`     | — (always last, SSE only) |

`validate.issues_detail` items:
```json
{"code": "SPARSE_PAGE_CONTENT", "severity": "high",
 "description": "18/22 pages have <30 chars — try ocr:tesseract-advanced"}
```

Known `validate` issue codes:
- `EMPTY_OUTPUT` — critical — nothing extracted
- `EMPTY_CONTENT` — critical — page markers but no text (OCR missing)
- `SPARSE_PAGE_CONTENT` — high — OCR ran but yielded almost nothing per page
- `WRONG_HEADING_HIERARCHY` — high
- `HEADING_LEVEL_JUMPS` — medium
- `REPEATED_LINES` — medium — artifact noise
- `OVERLONG_LINES` — low
- `TABLE_MISALIGNED` — medium
- `EMBEDDED_PAGE_NUMBERS` — low

### Final `done` event
```json
{
  "event":         "done",
  "ts":            "…",
  "output":        "/abs/path/doc.md",
  "quality":       92.0,
  "status":        "ok",
  "features":      ["text_fast", "tables:pdfplumber"],
  "elapsed_sec":   2.0
}
```

`features` contains only strategies that produced content (`confidence > 0`).

---

## CLI reference (NDJSON mode)

```bash
python -m pdf_extractor extract DOC.pdf -o out/ --json
python -m pdf_extractor extract *.pdf   -o out/ --json --strict --quality-threshold 80
python -m pdf_extractor inspect  DOC.pdf --json
python -m pdf_extractor capabilities    --json
python -m pdf_extractor strategies list --json
python -m pdf_extractor strategies info ocr:tesseract-advanced --json
```

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

## Determinism & caching

- Cache key = SHA-256(PDF bytes) + strategy list + options.
- `from_cache: true` in `done` means no features ran.
- Pass `--no-cache` (CLI) or omit `strategies` (API) to force re-extraction.

---

## Error handling best practices

1. **API**: poll `/extract/{job_id}` or stream `/extract/{job_id}/stream`. Never assume synchronous completion.
2. **CLI**: parse stdout line-by-line (NDJSON); never assume a single JSON blob.
3. On `validate.issues_detail` containing `SPARSE_PAGE_CONTENT` → retry with `strategies=ocr:tesseract-advanced`.
4. On `EMPTY_CONTENT` or exit code 4 → OCR backend unavailable; check `/capabilities`.
5. On exit code 5 → run `capabilities --json` and install missing backend.

---

## Versioning

Breaking changes bump the major version. Additive changes are minor bumps.
Agents should pin to a specific image digest for reproducibility.

- **Scope**: `extract`, `inspect`, `capabilities`, `strategies list`, `strategies info`
- **Transport**: stdin/stdout; line-delimited JSON (NDJSON), UTF-8
- **Stability guarantee**: additive changes are minor-version bumps; field
  removals or renames are major-version bumps. Unknown fields MUST be ignored
  by consumers.

---

## Invocation

```bash
python -m pdf_extractor <command> [args] --json
```

All commands emit NDJSON on stdout. Human diagnostics go to stderr.
Exit code is the agent's primary success signal — see table below.

### Claude Skills
```yaml
command: python -m pdf_extractor extract "{{pdf_path}}" -o "{{out_dir}}" --json
```

### Copilot / GitHub Actions
```yaml
- run: python -m pdf_extractor extract "$PDF" -o out/ --json --strict \
        --quality-threshold 80 > events.ndjson
```

---

## Exit codes

| Code | Meaning                                       | Action for agent                 |
|------|-----------------------------------------------|----------------------------------|
| 0    | Success                                       | Consume artifacts                |
| 1    | Generic error (see `error` event)             | Report, optionally retry         |
| 2    | Quality gate failed (`--quality-threshold`)   | Lower threshold or re-run OCR    |
| 3    | Preflight failed (corrupt/encrypted/missing)  | Do not retry — human intervention|
| 4    | Blocked — no content could be extracted       | Try different strategy           |
| 5    | `--strict`: requested strategy not used       | Install missing backend          |

---

## Event stream (NDJSON)

Every line is a JSON object with at least `event` (string) and `ts` (ISO-8601 UTC).
The same stream is emitted over Server-Sent Events on the web interface.

### Lifecycle of one `extract` call

```
preflight → profile → [cache_hit | strategy_plan → (feature_start → feature_done|feature_skip)* → validate → fix]
         → done → result
```

`error` may appear at any point. On error, `result` is still emitted with
`status != "ok"`.

### Event reference

| Event            | Always-present fields                                                                    |
|------------------|------------------------------------------------------------------------------------------|
| `preflight`      | `file`, `ok`, `pages`, `size_mb`, `is_scanned`, `warnings[]`                             |
| `profile`        | `scanned`, `text`, `tables`, `lang`, `has_images`                                        |
| `cache_hit`      | `key`, `output`                                                                          |
| `strategy_plan`  | `strategies[]`                                                                           |
| `feature_start`  | `name`, `tier`                                                                           |
| `feature_done`   | `name`, `tier`, `confidence` (0.0–1.0, always > 0)                                       |
| `feature_skip`   | `name`, `tier`, `reason`                                                                 |
| `validate`       | `status` ∈ {PASS, ISSUES_FOUND, BLOCKED}, `score` (0–100), `issues` (int), `issues_detail` (array of `{code, severity, description}`) |
| `fix`            | `fixes` (object: fix_name → count)                                                       |
| `done`           | `output`, `quality`, `status`, `features[]`, `elapsed_sec`                               |
| `error`          | `phase` ∈ {preflight, feature, validate, quality_gate}, `msg`                            |
| `dry_run`        | `plan` (nested object)                                                                   |
| `inspect`        | `profile` (see `InspectionResult` schema)                                                |
| `capability`     | `tool`, `category` ∈ {system, python}, `available`, `version?`                           |

### Final `result` event (extract)

Emitted once, last. This is the agent's contract for the final state:

```json
{
  "event": "result",
  "exit_code": 0,
  "status": "ok",          // ok | cached | dry_run | blocked | error
  "output_path": "/.../doc.md",
  "artifacts": ["/.../doc.md", "/.../images"],
  "features_used": ["text_fast", "tables:pdfplumber"],
  "quality_score": 92.0,
  "quality_label": "excellent",   // excellent | good | acceptable | poor
  "pages": 9,
  "file_size_mb": 0.18,
  "warnings": [],
  "issues": [{"code": "REPEATED_LINES", "severity": "medium", "description": "..."}],
  "from_cache": false,
  "elapsed_sec": 2.0
}
```

**Invariant**: `features_used` contains only strategies that produced content
(`confidence > 0`). Agents can trust this list to decide post-processing.

---

## Inspect output

```bash
python -m pdf_extractor inspect DOC.pdf --json
```

Emits one `inspect` event and one `result` event with the same payload. Use
`suggested_strategies` to decide what to pass to `extract --strategy`.

---

## Capabilities output

```bash
python -m pdf_extractor capabilities --json
```

One-shot emission:

```json
{
  "system_tools":     [{"name":"tesseract", "available":true, "version":"..."}],
  "python_packages":  [{"name":"pymupdf",   "available":true, "version":"..."}],
  "strategies":       [{"name":"text:fast", "tier":"text", "is_heavy":false, "priority":10}],
  "strategy_discovery_failures": []
}
```

Agents SHOULD call this once at session start to plan which strategies are
viable on the host.

---

## Strategies

`strategies list --json` returns an array of strategy metadata. Each entry:

```json
{
  "name":            "ocr:tesseract-advanced",
  "tier":            "ocr",
  "description":     "...",
  "priority":        20,
  "is_heavy":        true,
  "requires_python": ["pytesseract", "opencv-python"],
  "requires_system": ["tesseract", "unpaper"]
}
```

`priority` orders within a tier (lower runs first). `is_heavy=true` signals a
slow / GPU-preferred strategy — avoid for latency-sensitive calls.

---

## Determinism & caching

- Cache key = SHA-256(PDF bytes) + strategy list + options. Stable across runs.
- `from_cache: true` in the result means no features ran. Artifacts are
  reproduced from the last successful extraction.
- Pass `--no-cache` to force re-extraction. Pass `--quality-threshold` to
  reject cached results that would now fail the threshold.

---

## Error handling best practices

1. Always parse stdout line-by-line; never assume a single JSON blob.
2. Treat any `error` event as advisory — the `result` event is authoritative.
3. On `exit_code == 2`, lower `--quality-threshold` or add `--strategy ocr:tesseract-advanced`.
4. On `exit_code == 4`, the PDF likely needs OCR but none was configured —
   retry with `--strategy ocr:tesseract-basic`.
5. On `exit_code == 5`, run `capabilities --json` and install the missing backend.

---

## Versioning

This file tracks the contract version. Breaking changes bump the major number
and are announced in the top-level `CHANGELOG` (when it exists). Until then,
agents should pin to a specific commit SHA.
