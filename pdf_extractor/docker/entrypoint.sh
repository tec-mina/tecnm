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
    || echo "⚠️   Warmup terminó con errores en algunos backends."

# Self-heal — re-warm anything that is installed but not initialized.
# Catches the case where the build ran with --skip-on-error because the
# build host had no egress; on first boot the container can talk to the
# network and download the missing JAR / models without manual intervention.
echo "🩺  Verificando backends y reintentando los que falten..."
python -m pdf_extractor warmup \
    --languages es,en \
    --retry-missing \
    --skip-on-error \
    --quiet || true

echo ""
exec python -m pdf_extractor "$@"
