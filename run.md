docker build \
  --platform linux/arm64 \
  -f pdf_extractor/docker/Dockerfile \
  -t pdf-extractor:latest .


# Detener contenedor que ocupe el puerto 5001 (si hay uno corriendo)
docker ps --filter "publish=5001" -q | xargs -r docker stop


docker run --rm \
  --platform linux/arm64 \
  -p 5001:5000 \
  --memory=6g --memory-swap=6g \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  pdf-extractor:latest serve --port 5000