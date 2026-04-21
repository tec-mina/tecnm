#!/usr/bin/env python3
"""Consume /tmp/pdfx_batch_results.jsonl + produce docs/processed/BATCH_SUMMARY.md."""
from __future__ import annotations
import json
import os
from collections import Counter
from pathlib import Path

RESULTS = Path("/tmp/pdfx_batch_results.jsonl")
OUT = Path("docs/processed/BATCH_SUMMARY.md")

rows: list[dict] = []
for line in RESULTS.read_text().splitlines():
    line = line.strip()
    if not line:
        continue
    try:
        rows.append(json.loads(line))
    except json.JSONDecodeError:
        continue

total = len(rows)
status_c = Counter(r.get("status", "unknown") for r in rows)
feat_c: Counter[str] = Counter()
for r in rows:
    for f in r.get("features_used", []):
        feat_c[f] += 1

exit_c = Counter(r.get("exit_code", "?") for r in rows)
quality_vals = [r.get("quality_score", 0) for r in rows if r.get("status") == "ok"]
avg_q = sum(quality_vals) / len(quality_vals) if quality_vals else 0

# Label buckets
excellent = sum(1 for q in quality_vals if q >= 90)
good = sum(1 for q in quality_vals if 80 <= q < 90)
acceptable = sum(1 for q in quality_vals if 70 <= q < 80)
poor = sum(1 for q in quality_vals if q < 70)

lines: list[str] = []
lines.append("# Batch Summary — Conversión PDF → Markdown")
lines.append("")
lines.append(f"- Total PDFs: **{total}**")
lines.append(f"- Tool: `python -m pdf_extractor extract … --json`")
lines.append(f"- Resultados crudos: `/tmp/pdfx_batch_results.jsonl`")
lines.append("")
lines.append("## Status")
lines.append("")
lines.append("| Estado | Cantidad |")
lines.append("|---|---|")
for status, n in status_c.most_common():
    lines.append(f"| `{status}` | {n} |")
lines.append("")
lines.append("## Exit codes")
lines.append("")
lines.append("| Código | Significado | Cantidad |")
lines.append("|---|---|---|")
ec_meaning = {0: "ok", 1: "error", 2: "quality gate", 3: "preflight falló",
              4: "blocked (sin contenido)", 5: "strict violation"}
for code, n in sorted(exit_c.items(), key=lambda kv: (kv[0] is None, kv[0])):
    lines.append(f"| `{code}` | {ec_meaning.get(code, '?')} | {n} |")
lines.append("")
lines.append("## Calidad (sólo `status=ok`)")
lines.append("")
lines.append(f"- Promedio: **{avg_q:.1f}/100**")
lines.append(f"- Excellent (≥90): {excellent}")
lines.append(f"- Good (80-89): {good}")
lines.append(f"- Acceptable (70-79): {acceptable}")
lines.append(f"- Poor (<70): {poor}")
lines.append("")
lines.append("## Capacidades utilizadas (agregado)")
lines.append("")
lines.append("Estrategias que efectivamente contribuyeron contenido (confidence > 0).")
lines.append("")
lines.append("| Estrategia (tier) | PDFs en los que contribuyó |")
lines.append("|---|---|")
for feat, n in feat_c.most_common():
    lines.append(f"| `{feat}` | {n} |")
lines.append("")
lines.append("## Detalle por PDF")
lines.append("")
lines.append("| # | Archivo | Páginas | MB | Calidad | Estado | Exit | Capacidades usadas |")
lines.append("|---:|---|---:|---:|---:|---|---:|---|")

# Sort by original order — rows arrive in directory order.
for i, r in enumerate(rows, 1):
    out_path = r.get("output_path") or ""
    file_name = Path(out_path).stem or "(n/a)"
    pages = r.get("pages", "")
    mb = r.get("file_size_mb", "")
    q = r.get("quality_score", 0)
    st = r.get("status", "?")
    ec = r.get("exit_code", "?")
    feats = ", ".join(r.get("features_used", [])) or "—"
    lines.append(
        f"| {i} | `{file_name}` | {pages} | {mb} | {q:.0f} | {st} | {ec} | {feats} |"
    )

lines.append("")
lines.append("## Advertencias frecuentes")
lines.append("")
warn_c: Counter[str] = Counter()
for r in rows:
    for w in r.get("warnings", []):
        warn_c[w] += 1
for w, n in warn_c.most_common(10):
    lines.append(f"- ({n}×) {w}")

lines.append("")
lines.append("## Issues frecuentes")
lines.append("")
issue_c: Counter[str] = Counter()
for r in rows:
    for it in r.get("issues", []):
        issue_c[it.get("code", "?")] += 1
for code, n in issue_c.most_common():
    lines.append(f"- ({n}×) `{code}`")

OUT.write_text("\n".join(lines), encoding="utf-8")
print(f"wrote {OUT} ({total} rows)")
