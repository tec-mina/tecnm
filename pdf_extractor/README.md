# PDF Extractor

Pipeline de extracción PDF → Markdown de grado productivo para el **TecNM / DPPP**.  
Convierte cualquier PDF (texto nativo, escaneado, tablas, imágenes) a Markdown limpio y LLM-ready.  
Incluye interfaz web con arrastrar-y-soltar, log en tiempo real y comparación de estrategias.

---

## Características

| Capacidad | Descripción |
|---|---|
| Texto nativo | PyMuPDF, pdfminer.six, pymupdf4llm, Apache Tika |
| OCR | Tesseract básico y avanzado (OpenCV + deskew), EasyOCR |
| Tablas | pdfplumber, Camelot (lattice/stream), Tabula (Java) |
| Imágenes | Extracción con referencias Markdown |
| Fuentes | Análisis de estilos: negrita, cursiva, encabezados por tamaño |
| Estructura | Bookmarks, anotaciones, campos de formulario, adjuntos |
| Corrección OCR | Patrones regex + diccionario (pyspellchecker) |
| Interfaz web | Drag & drop, log SSE en tiempo real, comparación de estrategias |
| Salida | Markdown con frontmatter YAML, ToC automático, calidad 0–100 |

---

## Inicio rápido — Docker (recomendado)

```bash
# 1. Clonar
git clone https://github.com/tec-mina/tecnm.git
cd tecnm

# 2. Construir imagen
docker build -f pdf_extractor/docker/Dockerfile -t pdf-extractor:latest .

# 3. Interfaz web
docker run --rm -p 5000:5000 \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  pdf-extractor:latest web
# Abre http://localhost:5000

# 4. CLI
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  pdf-extractor:latest extract /app/input/documento.pdf -o /app/output

# 5. Ver herramientas
docker run --rm pdf-extractor:latest capabilities
```

---

## Instalación local

### macOS
```bash
# desde la raíz del repositorio
chmod +x install-mac.sh
./install-mac.sh            # instala deps del sistema + venv Python + construye Docker
./install-mac.sh --local    # solo entorno Python local
./install-mac.sh --docker   # solo construye imagen Docker
```

### Windows (PowerShell como Administrador)
```powershell
# desde la raíz del repositorio
Set-ExecutionPolicy Bypass -Scope Process -Force
.\install-windows.ps1               # todo
.\install-windows.ps1 -Mode local   # solo entorno Python local
.\install-windows.ps1 -Mode docker  # solo construye imagen Docker
```

Después de instalar localmente:
```bash
source pdf_extractor/.venv/bin/activate   # macOS/Linux
# o en Windows:
pdf_extractor\.venv\Scripts\Activate.ps1
```

---

## Interfaz web

```bash
# Local
python -m pdf_extractor web

# Docker
docker run --rm -p 5000:5000 \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  pdf-extractor:latest web

# Opciones
python -m pdf_extractor web --port 8080 --host 127.0.0.1
```

Abre `http://localhost:5000` y podrás:

- **Arrastrar** un PDF → se perfila automáticamente (páginas, idioma, si está escaneado)
- Ver las **estrategias recomendadas** resaltadas en verde y activar/desactivar cualquiera
- **Extraer** y ver el log de eventos en tiempo real (SSE)
- Ver el **score de calidad** (0–100), estrategias usadas y advertencias
- **Descargar** el Markdown resultante
- Tab **Herramientas**: inventario con verde/rojo de todo lo instalado
- Tab **Estrategias**: tabla completa de estrategias registradas con sus requisitos

---

## CLI

```bash
# Extraer (auto-selección de estrategia)
python -m pdf_extractor extract documento.pdf -o salida/

# Estrategia específica
python -m pdf_extractor extract documento.pdf -s text:fast -o salida/
python -m pdf_extractor extract escaneado.pdf -s ocr:tesseract-advanced -o salida/

# Combinar estrategias
python -m pdf_extractor extract doc.pdf -s tables:pdfplumber -s text:fast -o salida/

# Con imágenes / estructura del PDF
python -m pdf_extractor extract doc.pdf --with-images --with-structure -o salida/

# Rango de páginas
python -m pdf_extractor extract grande.pdf --pages 1-50 -o salida/

# Ver plan sin extraer
python -m pdf_extractor extract documento.pdf --dry-run

# Perfilar sin extraer
python -m pdf_extractor inspect documento.pdf

# Listar estrategias
python -m pdf_extractor strategies list
python -m pdf_extractor strategies list --tier ocr
python -m pdf_extractor strategies info ocr:tesseract-advanced

# Inventario de herramientas
python -m pdf_extractor capabilities

# Salida JSON para agentes / CI
python -m pdf_extractor extract documento.pdf --json | jq .
python -m pdf_extractor capabilities --json

# Cache
python -m pdf_extractor cache info
python -m pdf_extractor cache clear

# Interfaz web
python -m pdf_extractor web
python -m pdf_extractor web --port 8080
```

---

## Estrategias disponibles

| Tier | Nombre | Descripción |
|---|---|---|
| `text` | `text:fast` | PyMuPDF — extracción rápida de texto nativo |
| `text` | `text:pdfminer` | pdfminer.six — encodings de fuentes custom |
| `text` | `text:llm` | pymupdf4llm — Markdown LLM-optimizado |
| `text` | `text:tika-java` | Apache Tika (Java/PDFBox) |
| `ocr` | `ocr:tesseract-basic` | Tesseract 300 DPI, sin preprocesado |
| `ocr` | `ocr:tesseract-advanced` | Tesseract 400 DPI + OpenCV deskew/denoise |
| `ocr` | `ocr:easyocr` | EasyOCR neural (GPU opcional) |
| `tables` | `tables:pdfplumber` | pdfplumber — tablas en PDFs de texto |
| `tables` | `tables:camelot` | Camelot lattice/stream |
| `tables` | `tables:tabula` | Tabula-py (Java) |
| `images` | `images:extract` | Extracción de imágenes embebidas |
| `fonts` | `fonts:analyze` | Análisis de fuentes: negrita, cursiva, tamaño |
| `layout` | `layout:structure` | Bookmarks, anotaciones, formularios |

---

## Arquitectura

```
tecnm/
├── install-mac.sh              ← instalador macOS (raíz del repo)
├── install-windows.ps1         ← instalador Windows (raíz del repo)
└── pdf_extractor/
    ├── app/                    # Capa de aplicación (SOLID)
    │   ├── ports.py            # Protocolo IEventEmitter (DIP)
    │   └── use_cases.py        # Lógica de negocio pura
    ├── interfaces/
    │   ├── cli.py              # CLI Click + Rich
    │   └── web/
    │       ├── app.py          # Flask + SSE
    │       └── templates/
    │           └── index.html  # UI drag & drop
    ├── core/                   # Infraestructura
    │   ├── pipeline.py         # Orquestación de features
    │   ├── registry.py         # Auto-discovery de estrategias
    │   ├── detector.py         # Perfil del PDF
    │   ├── preflight.py        # Validación previa
    │   ├── cache.py            # Caché SHA256
    │   └── platform.py         # Detección del sistema
    ├── features/               # Adaptadores de extracción
    │   ├── _protocol.py        # StrategyMeta dataclass
    │   ├── text_fast.py        # text:fast
    │   ├── text_pdfminer.py    # text:pdfminer
    │   ├── ocr_tesseract.py    # ocr:tesseract-*
    │   ├── tables.py           # tables:pdfplumber
    │   └── ...
    ├── output/                 # Post-procesamiento
    │   ├── assembler.py        # Merge → Markdown
    │   ├── fixer.py            # Correcciones mecánicas
    │   ├── validator.py        # Calidad 0–100
    │   ├── frontmatter.py      # YAML frontmatter
    │   └── spell_corrector.py  # Corrección de OCR
    ├── docker/
    │   ├── Dockerfile
    │   └── compose.yml
    └── requirements/
        ├── base.txt            # Mínimo (click, rich, flask, pymupdf…)
        ├── ocr.txt             # Tesseract, EasyOCR, OpenCV
        ├── advanced.txt        # Camelot, Tabula, Tika, Docling
        └── ml.txt              # Surya OCR, Marker-PDF (GPU, pesado)
```

### Flujo de eventos

Cada extracción emite un stream estructurado — el mismo en CLI (`--json`) y en la web (SSE):

```
preflight → profile → strategy_plan → feature_start/done × N
         → validate → fix → done
```

---

## Variables de entorno

| Variable | Default | Descripción |
|---|---|---|
| `EXTRACTOR_WORKERS` | `4` | Workers paralelos (Docker) |
| `PYTHONUNBUFFERED` | `1` | Logs en tiempo real |
| `TESSDATA_PREFIX` | auto | Ruta a tessdata de Tesseract |
| `UPLOAD_DIR` | `/tmp/pdf-extractor/uploads` | Uploads temporales (web) |
| `OUTPUT_DIR` | `/tmp/pdf-extractor/output` | Salida temporal (web) |

---

## Requisitos del sistema (instalación local)

| Herramienta | Necesaria para |
|---|---|
| Python 3.10+ | — |
| Tesseract 5+ | OCR |
| Ghostscript | Camelot, preprocesado |
| Poppler (`pdfinfo`, `pdfimages`) | Inspección |
| Java 11+ | Tabula, Apache Tika |
| `unpaper` | OCR avanzado (deskew) |
| ImageMagick | Conversión de imágenes |

En Docker **todo esto ya está incluido** en la imagen.
