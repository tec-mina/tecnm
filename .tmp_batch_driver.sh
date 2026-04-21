#!/bin/bash
set -u
cd /Users/molina/ClaudeProjects/tecnm
RESULTS=/tmp/pdfx_batch_results.jsonl
LOG=/tmp/pdfx_batch_log.txt
: > "$RESULTS"
: > "$LOG"
PY=./pdf_extractor/.venv/bin/python
i=0
total=$(ls docs/raw/*.pdf | wc -l | tr -d ' ')
for pdf in docs/raw/*.pdf; do
  i=$((i+1))
  name=$(basename "$pdf")
  start=$(date +%s)
  "$PY" -m pdf_extractor extract "$pdf" -o docs/processed --json --no-cache 2>>"$LOG" \
    | grep '"event": "result"' | tail -1 >> "$RESULTS"
  dur=$(( $(date +%s) - start ))
  echo "[$i/$total] ${dur}s  $name" >> "$LOG"
done
echo "DONE" >> "$LOG"
