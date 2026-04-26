# Comandos — PDF Extractor

## 1. Construir imagen
```bash
docker build -f pdf_extractor/docker/Dockerfile -t pdf-extractor:latest .
```
✓ Espera a que termine (dirá `DONE`)

## 2. Interfaz web — Paso a paso

**Paso 1:** Corre este comando:
```bash
docker run --rm -p 5001:5000 \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  pdf-extractor:latest serve --port 5000
```

**Paso 2:** Espera a ver este mensaje en la terminal (verás algo así):
```
🚀 PDF Extractor API started
   Web: http://localhost:5001
   Docs: http://localhost:5001/docs
```

**Paso 3:** Copia-pega en tu navegador: **http://localhost:5001**

(NO intentes `0.0.0.0` — ese es dirección interna. Usa siempre `localhost:5001`)

## 3. Extraer PDF (CLI)
```bash
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  pdf-extractor:latest extract /app/input/documento.pdf -o /app/output
```
✓ El archivo Markdown aparecerá en `./output/`