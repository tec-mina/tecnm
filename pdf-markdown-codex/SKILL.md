---
name: pdf-markdown-codex
description: >
  Convierte PDFs a Markdown estructurado con validacion, progreso en tiempo real
  y multiples backends de extraccion (PyMuPDF, Docling AI, MarkItDown, EasyOCR).
  Usa esta skill SIEMPRE que el usuario mencione un archivo PDF o quiera:
  convertir, procesar o extraer contenido de un PDF;
  cargar un PDF al contexto de un LLM;
  preservar tablas, encabezados o imagenes de un PDF;
  extraer texto de un documento escaneado o imagen;
  mejorar o verificar la calidad de un Markdown ya generado desde un PDF;
  manejar PDFs grandes sin que el modelo se cuelgue;
  detectar si un PDF esta encriptado o dañado.
  Aplica tambien cuando el usuario diga "convierte", "extrae", "pasa a markdown",
  "sube este pdf", "necesito el texto de este archivo" o muestre un .pdf.
  NO usar si el archivo claramente no es PDF (Word, Excel, HTML, imagen suelta).
---

# PDF Markdown Codex

Skill unificada para convertir PDF a Markdown de forma mas seria y reusable.

## Objetivo

Entregar un `.md` que sea:
- fiel al PDF;
- util para lectura humana;
- util para LLMs;
- explicito sobre lo no verificado.

## Flujo base

1. Extraer el PDF completo a Markdown.
2. Aplicar quality gate heuristico.
3. Ejecutar safe fixes solo si ayudan sin cambiar significado.
4. Si las tablas importan, usar un backend auxiliar de tablas.
5. Cerrar con `PASS`, `ISSUES_FOUND` o `BLOCKED_MISSING_CONTEXT`.

## Scripts principales

- `scripts/bootstrap_env.py`
  Crea un `.venv` local del skill e instala dependencias base y opcionales.

- `scripts/check_system_deps.py`
  Verifica si existen dependencias de sistema: `tesseract`, `gs`, `java`, `pdftotext`.

- `scripts/pdf_markdown_pipeline.py`
  Punto de entrada recomendado. Orquesta validacion, extraccion, quality gate
  y safe fixes. Progreso visible en tiempo real (no captura stderr).

- `scripts/pdf_to_md.py`
  Extractor directo. Maneja cache, imagenes y appendix auxiliar de tablas.

- `scripts/extractor.py`
  Backends de extraccion:
  - `extract_pdf_fast` — PyMuPDF + pymupdf4llm, tqdm por bloques para PDFs grandes
  - `extract_pdf_docling` — Docling AI, mejor precision en tablas complejas
  - `extract_pdf_markitdown` — Microsoft MarkItDown, buena jerarquia sin AI
  - `extract_pdf_easyocr` — EasyOCR para PDFs escaneados sin capa de texto
  - `validate_pdf` — validacion pre-vuelo: magia bytes, encriptado, paginas, scanned

- `scripts/table_backends.py`
  Backends auxiliares para tablas:
  - `pdfplumber` (default auto)
  - `tabula` (requiere Java)
  - `camelot` (lattice y stream, requiere Ghostscript)

- `scripts/pdf_markdown_compare.py`
  Quality gate heuristico del Markdown.

- `scripts/markdown_fixer.py`
  Limpieza mecanica segura.

## Comandos recomendados

Preparar entorno base:

```bash
python scripts/bootstrap_env.py
python scripts/check_system_deps.py
```

Instalar extras segun necesidad:

```bash
python scripts/bootstrap_env.py --extras docling
python scripts/bootstrap_env.py --extras markitdown
python scripts/bootstrap_env.py --extras tabula
python scripts/bootstrap_env.py --extras camelot
python scripts/bootstrap_env.py --extras ocr
```

Extraccion normal (default: PyMuPDF rapido + tablas pdfplumber/tabula/camelot):

```bash
python scripts/pdf_markdown_pipeline.py documento.pdf
```

Nivel 1 — Docling AI (mejor para tablas dificiles):

```bash
python scripts/pdf_markdown_pipeline.py documento.pdf --docling
```

Nivel 1 — MarkItDown de Microsoft (buena jerarquia, sin modelos):

```bash
python scripts/pdf_markdown_pipeline.py documento.pdf --markitdown
```

Nivel 3 — OCR con EasyOCR (PDFs escaneados):

```bash
python scripts/pdf_markdown_pipeline.py documento.pdf --ocr-easyocr
python scripts/pdf_markdown_pipeline.py documento.pdf --ocr-easyocr es en fr
```

Forzar backend auxiliar de tablas:

```bash
python scripts/pdf_markdown_pipeline.py documento.pdf --table-backend pdfplumber
python scripts/pdf_markdown_pipeline.py documento.pdf --table-backend camelot
python scripts/pdf_markdown_pipeline.py documento.pdf --table-backend tabula
```

Aplicar safe fixes:

```bash
python scripts/pdf_markdown_pipeline.py documento.pdf --fix-safe
```

## Elegir el backend correcto

Elige segun el problema que tienes, no segun preferencia:

| Situacion | Backend recomendado |
|---|---|
| PDF digital normal, texto seleccionable | *(ninguno, default)* |
| Tablas sin bordes visibles o muy densas | `--docling` |
| PDF de Word/PowerPoint exportado | `--markitdown` |
| PDF escaneado, sin capa de texto | `--ocr-easyocr` |
| PDF escaneado en idioma no hispano | `--ocr-easyocr en fr de` |
| Tablas numericas con celdas fusionadas | `--table-backend camelot` |
| Tablas en PDF de reporte financiero | `--table-backend tabula` |

Si no sabes cual usar, corre primero el default. El quality gate te dira si las tablas quedaron mal y puedes escalar entonces.

**PDFs grandes (> 40 paginas):** el progreso se muestra automaticamente con tqdm en bloques de 30 paginas. No hace falta hacer nada adicional.

## Extraccion completa obligatoria

Toda extraccion debe cubrir el 100% de las paginas del PDF:

- Si una pagina o un bloque de paginas falla, se registra como
  `<!-- EXTRACTION_ERROR pages N-M: ... -->` en el `.md` y la extraccion continua.
- Nunca se entrega un `.md` truncado sin advertir explicitamente cuales paginas quedaron incompletas.
- El quality gate siempre informa el numero de paginas procesadas vs. el total declarado en el PDF.
- Si el `.md` resultante tiene menos contenido del esperado, reporta `ISSUES_FOUND` con detalle;
  no cierres como `PASS` silencioso.

## Archivos generados

Por defecto la extraccion produce **un solo archivo**: `documento.md`.

No se crea un directorio `images/` a menos que el usuario pida explicitamente las imagenes:

```bash
python scripts/pdf_markdown_pipeline.py documento.pdf --with-images
```

Para LLMs e ingestion de texto, las imagenes del PDF son ruido — omitirlas es la politica correcta.



- La extraccion principal manda sobre el cuerpo del documento.
- Los backends auxiliares de tablas sirven para rescatar o contrastar tablas, no para inventarlas.
- Si las tablas siguen mal, reportalo; no simules fidelidad.

## PDFs escaneados

- Con `--ocr-easyocr` se activa EasyOCR neural (no requiere Tesseract).
- Si el PDF mezcla texto digital y paginas escaneadas, el quality gate lo detecta y sugiere OCR.
- Si la salida queda vacia, rota o muy pobre incluso con OCR, cierra como `BLOCKED_MISSING_CONTEXT` y explica que el PDF requiere preprocesamiento de imagen (enderezar, aumentar contraste) antes de intentarlo de nuevo.

## Referencias

Lee estas referencias solo cuando hagan falta:

- `references/WORKFLOW.md`
  Flujo operativo y criterios de decision.

- `references/LIBRARIES.md`
  Librerias base, opcionales y dependencias del sistema.

## Criterio de cierre

La tarea solo queda bien cerrada si:
- existe un `.md` legible;
- el quality gate se informo claramente;
- los safe fixes no alteraron el significado;
- lo no verificado quedo marcado como no verificado.
