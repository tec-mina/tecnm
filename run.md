# Comandos — PDF Extractor

## 0. Limpiar desde cero (Apple Silicon — linux/arm64)

Usa esto cuando hay errores raros de imagen corrupta. Luego corre §1 con `--no-cache`.

```bash
docker rmi pdf-extractor:latest --force
docker builder prune --force
docker buildx prune --all --force   # limpia build cache (las entradas del historial en Docker Desktop hay que borrarlas manualmente desde la UI)
docker image prune --force
docker volume prune --force
```

> Ninguno de estos toca `./input` ni `./output` — son bind mounts en tu Mac.

---

## 1. Construir imagen

```bash
docker build \
  --platform linux/arm64 \
  -f pdf_extractor/docker/Dockerfile \
  -t pdf-extractor:latest .
```

> Después de un §0, añade `--no-cache` para forzar descarga limpia (~10-15 min).  
> En uso normal omítelo — reutiliza el cache (~1-2 min).

> Durante el build el paso `warmup` descarga y bake en la imagen:
> - Modelos EasyOCR es+en (~64 MB)
> - JAR Apache Tika (~60 MB)

---

## 2. Correr el servidor (interfaz web)

```bash
# Liberar el puerto 5001 si ya está ocupado
docker ps --filter "publish=5001" -q | xargs -r docker stop
```

```bash
  docker run --rm -d --name pdf-extractor-dev \
  --platform linux/arm64 \
  -p 5001:5000 \
  --memory=6g --memory-swap=6g \
  -v "$(pwd)/pdf_extractor:/app/pdf_extractor" \
  -v "$(pwd)/input:/app/input" \
  -v "$(pwd)/output:/app/output" \
  pdf-extractor:latest serve --port 5000 
```

> **Reglas de oro:**
> - NO montes `-v easyocr-models:/root/.EasyOCR` — los modelos ya están en la imagen; montarlo los sobreescribe con un directorio vacío.
> - El `--memory` aquí coincide con el límite de Docker Desktop (ver Settings → Resources → Memory). Si Docker Desktop tiene menos de 4 GB asignados, sube ese límite primero.

### ¿Qué verás en la terminal?

```
⏳  Iniciando warmup de backends (EasyOCR + Tika + registry)...
✅  Warmup completo — todos los backends listos.

🚀 PDF Extractor API started
   Web: http://localhost:5000
   Docs: http://localhost:5000/docs
INFO:     Uvicorn running on http://0.0.0.0:5000
```

> El warmup tarda **60–90 segundos** (carga modelos en RAM + levanta JVM Tika).
> **El servidor solo acepta requests DESPUÉS de ese mensaje.** Si intentas usarlo antes verás "Network error".

Abre en el navegador: **http://localhost:5001**

---

## 3. Verificar que todos los backends están listos

Después de que aparezca el mensaje de startup, en otra terminal:

```bash
curl -s http://localhost:5001/api/v1/readiness | python3 -m json.tool
```

Busca `"ready": true` en cada backend. Si alguno dice `false`, el campo `last_error` explica por qué.

---

## 4. Extraer PDF vía CLI (sin servidor)

```bash
docker run --rm \
  --platform linux/arm64 \
  --memory=4g --memory-swap=4g \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  pdf-extractor:latest extract /app/input/documento.pdf -o /app/output
```

✓ El archivo Markdown aparecerá en `./output/`

### Especificar estrategia manualmente

```bash
# Solo Tesseract (rápido, sin descargas extra)
docker run --rm --platform linux/arm64 \
  -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output \
  pdf-extractor:latest extract /app/input/documento.pdf \
  --strategies ocr:tesseract-basic -o /app/output

# Tesseract + tablas pdfplumber
docker run --rm --platform linux/arm64 \
  -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output \
  pdf-extractor:latest extract /app/input/documento.pdf \
  --strategies ocr:tesseract-basic,tables:pdfplumber -o /app/output

# EasyOCR neuronal (mejor calidad, más lento)
docker run --rm --platform linux/arm64 --memory=4g --memory-swap=4g \
  -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output \
  pdf-extractor:latest extract /app/input/documento.pdf \
  --strategies ocr:easyocr -o /app/output
```

---

## 5. Ver todas las estrategias disponibles

```bash
docker run --rm --platform linux/arm64 \
  pdf-extractor:latest strategies
```

---

## 6. Diagnóstico rápido dentro del contenedor

```bash
# Ver qué backends detectó el contenedor
docker run --rm --platform linux/arm64 \
  pdf-extractor:latest readiness

# Ver herramientas del sistema disponibles
docker run --rm --platform linux/arm64 \
  pdf-extractor:latest capabilities
```