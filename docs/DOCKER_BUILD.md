# Docker Build & Deployment

## Clean Docker Build (Fresh Image)

### 1. Remove old containers and images
```bash
# Stop all running containers
docker stop $(docker ps -aq) 2>/dev/null || true

# Remove PDF Extractor containers
docker rm $(docker ps -a | grep pdf-extractor | awk '{print $1}') 2>/dev/null || true

# Remove old images
docker rmi $(docker images | grep pdf-extractor | awk '{print $3}') 2>/dev/null || true

# Optional: Clean dangling images (save space)
docker image prune -f
```

### 2. Build fresh image from current code
```bash
cd pdf_extractor

# Build image with tag
docker build -f docker/Dockerfile -t pdf-extractor:latest ..

# Or with version
docker build -f docker/Dockerfile -t pdf-extractor:v1.0 ..
```

### 3. Run container
```bash
# Development (interactive, with volume mount)
docker run -it --name pdf-extractor \
  -p 8080:8080 \
  -v $(pwd)/docs:/app/docs \
  -v $(pwd)/output:/app/output \
  pdf-extractor:latest

# Production (detached, with health check)
docker run -d \
  --name pdf-extractor \
  -p 8080:8080 \
  --health-cmd="curl -f http://localhost:8080/healthz || exit 1" \
  --health-interval=30s \
  --health-timeout=10s \
  --health-retries=3 \
  pdf-extractor:latest
```

### 4. Verify container is working
```bash
# Check container status
docker ps | grep pdf-extractor

# Check health
docker exec pdf-extractor curl http://localhost:8080/healthz

# View logs
docker logs -f pdf-extractor

# Test API
curl http://localhost:8080/api/v1/readiness | jq .
```

## What Happens During Build

The Dockerfile:
1. **Installs system dependencies** (Tesseract, Ghostscript, Java, fonts, etc.)
2. **Installs Python packages** from `requirements.txt` (including docling)
3. **Runs build-time warmup** - downloads all models and validates backends
4. **Copies application source code**
5. **Sets up runtime directories** for caching

Everything is **cached in the image layer**, so the container starts ready to process PDFs immediately.

## What's Inside

- ✅ All text extraction methods (text:fast, text:pdfminer, text:docling, text:markitdown)
- ✅ All OCR methods (tesseract-basic, tesseract-advanced, easyocr)
- ✅ Table extraction (pdfplumber, camelot, tabula, img2table)
- ✅ Image extraction and structure analysis
- ✅ Font analysis
- ✅ Docling AI with integrated OCR
- ✅ Cross-tier fallback for scanned PDFs
- ✅ Clear error messages

## Environment Variables

```bash
# Available at runtime
PORT=8080                  # API port
EXTRACTOR_WORKERS=4       # Parallel workers
PYTHONUNBUFFERED=1        # Log streaming
PYTHONPATH=/app           # Python path
TIKA_PATH=/opt/tika       # Tika JAR location
```

## Accessing the Service

Once container is running:

- **Web UI:** http://localhost:8080/web
- **REST API:** http://localhost:8080/api/v1
- **API Docs:** http://localhost:8080/docs
- **Health Check:** http://localhost:8080/healthz

## Docker Compose (Optional)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  pdf-extractor:
    build:
      context: .
      dockerfile: pdf_extractor/docker/Dockerfile
    ports:
      - "8080:8080"
    volumes:
      - ./docs:/app/docs
      - ./output:/app/output
    environment:
      - PORT=8080
      - EXTRACTOR_WORKERS=4
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 120s
    restart: unless-stopped
```

Then run:
```bash
docker-compose up -d
docker-compose logs -f pdf-extractor
```
