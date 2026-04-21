# PDF Extractor — Agent Contract

Stable, versioned interface for agentic consumers (Claude Skills, Copilot agents,
GitHub Actions, internal bots). Human-facing CLI output is *not* part of this
contract — agents MUST use `--json`.

- **Contract version**: `1.0.0`
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
| `validate`       | `status` ∈ {PASS, ISSUES_FOUND, BLOCKED}, `score` (0–100), `issues` (int)                |
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
