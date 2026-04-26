#!/bin/sh
# entrypoint.sh — corre warmup completo antes de iniciar el servidor.
#
# Por qué existe:
#   EasyOCR carga ~300 MB de modelos en RAM la primera vez.
#   Tika levanta una JVM que tarda ~15 s en arrancar.
#   Si el servidor arranca sin esperar, el primer request de OCR llega
#   mientras los backends están inicializando → OOM kill o Network error.
#
# Flujo:
#   1. warmup (inicializa todos los backends, muere si hay error fatal)
#   2. exec serve  ← el proceso pasa a ser PID 1 del contenedor
#
# Se pasa cualquier argumento extra directamente a `python -m pdf_extractor`.
# Ejemplo: entrypoint.sh serve --port 5000

set -e

echo "⏳  Iniciando warmup de backends (EasyOCR + Tika + registry)..."
python -m pdf_extractor warmup \
    --languages es,en \
    --skip-on-error \
    --quiet \
    && echo "✅  Warmup completo — todos los backends listos." \
    || echo "⚠️   Warmup terminó con errores en algunos backends (ver /api/v1/readiness)."

echo ""
exec python -m pdf_extractor "$@"
