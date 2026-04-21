# Libraries

## Jerarquia de backends de extraccion

El skill usa una jerarquia explicita. Activar un nivel no desactiva los otros;
se escogen por flag o por disponibilidad.

### Nivel 1 — Semantico (mejor fidelidad de tablas y estructura)

- `docling`, `docling-core`, `huggingface_hub`
  IBM Docling + TableFormer AI (~93% precision en tablas). Requiere descarga de
  modelos la primera vez (~2-3 min). Flag: `--docling`.
  Instalar: `python scripts/bootstrap_env.py --extras docling`

- `markitdown[pdf]`
  Microsoft MarkItDown. Buena jerarquia de titulos y tablas, sin modelos AI.
  Flag: `--markitdown`.
  Instalar: `python scripts/bootstrap_env.py --extras markitdown`

### Nivel 2 — Hibrido rapido (default)

- `pymupdf`
  Apertura de PDF, conteo de paginas, extraccion de imagenes, validacion.

- `pymupdf4llm`
  Extraccion rapida a Markdown con estrategia de tablas por texto.
  Usa chunks + tqdm para PDFs grandes (> 40 paginas).

- `pdfplumber`
  Backend auxiliar de tablas con alta fidelidad visual.

- `tabula-py`
  Backend auxiliar de tablas usando Java. Alternativa util cuando pdfplumber
  no detecta tablas. Requiere Java en el PATH.
  Instalar: `python scripts/bootstrap_env.py --extras tabula`

- `camelot-py`, `opencv-python`
  Backend alterno de tablas (lattice y stream). Requiere Ghostscript.
  Instalar: `python scripts/bootstrap_env.py --extras camelot`

### Nivel 3 — OCR (PDFs escaneados sin capa de texto)

- `easyocr`
  OCR neural multi-idioma. Flag: `--ocr-easyocr [es en ...]`.
  Instalar: `python scripts/bootstrap_env.py --extras ocr`

- `pytesseract`, `pdf2image`, `pypdfium2`
  Ruta Tesseract clasica. Requiere Tesseract y Poppler en el sistema.

- `img2table`, `rapidocr-onnxruntime`
  Extraccion de tablas en imagenes para documentos escaneados.

## Base siempre instalada

- `pdfminer.six` — contraste de texto
- `pypdf` — utilidades generales sobre PDFs
- `pillow` — manejo de imagenes
- `tabulate` — renderizado de tablas a Markdown
- `tqdm` — barras de progreso en terminal para PDFs grandes
- `python-dateutil` — fechas y metadata
- `chardet` — deteccion de codificacion

## Dependencias de sistema

- Java (JRE) — requerido por `tabula-py`
- Ghostscript — requerido por `camelot-py`
- Tesseract — requerido por `pytesseract`
- Poppler (`pdfinfo`, `pdftoppm`) — requerido por `pdf2image`

  macOS: `brew install poppler tesseract ghostscript`
  Debian/Ubuntu: `apt install poppler-utils tesseract-ocr ghostscript`

## Criterio de uso

- No toda libreria debe activarse en cada corrida.
- La ruta default (PyMuPDF + pymupdf4llm + pdfplumber) cubre la mayoria de casos.
- Los extras se justifican cuando mejoran un caso real documentado.
