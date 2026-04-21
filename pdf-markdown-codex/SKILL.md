---
name: pdf-markdown-codex
description: Convierte PDFs completos a Markdown estructurado con un flujo profesional de extraccion, verificacion y limpieza. Usala cuando el usuario quiera cargar todo un PDF al contexto, preservar encabezados, tablas e imagenes, mejorar la calidad del Markdown resultante o dejar un archivo final mas confiable para analisis posterior. Usa PyMuPDF y Docling para la extraccion principal, mas backends auxiliares de tablas como pdfplumber y Camelot cuando ayudan a rescatar mejor la estructura tabular.
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
  Verifica si existen dependencias de sistema comunes como `tesseract`, `gs`, `java` o `pdftotext`.

- `scripts/pdf_markdown_pipeline.py`
  Orquesta extraccion, quality gate y safe fixes.

- `scripts/pdf_to_md.py`
  Extrae el PDF completo, maneja cache, imagenes y apendice auxiliar de tablas.

- `scripts/extractor.py`
  Backends principales:
  - PyMuPDF + pymupdf4llm para rapidez
  - Docling para tablas complejas y documentos dificiles

- `scripts/table_backends.py`
  Backends auxiliares para tablas:
  - `pdfplumber`
  - `camelot`

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

Instalar extras utiles:

```bash
python scripts/bootstrap_env.py --extras docling camelot ocr
```

Extraccion normal:

```bash
python scripts/pdf_markdown_pipeline.py documento.pdf
```

Extraccion mas precisa para tablas dificiles:

```bash
python scripts/pdf_markdown_pipeline.py documento.pdf --docling
```

Forzar backend auxiliar de tablas:

```bash
python scripts/pdf_markdown_pipeline.py documento.pdf --table-backend pdfplumber
python scripts/pdf_markdown_pipeline.py documento.pdf --table-backend camelot
```

Aplicar safe fixes:

```bash
python scripts/pdf_markdown_pipeline.py documento.pdf --fix-safe
```

## Politica de tablas

- La extraccion principal manda sobre el cuerpo del documento.
- Los backends auxiliares de tablas sirven para rescatar o contrastar tablas, no para inventarlas.
- Si las tablas siguen mal, reportalo; no simules fidelidad.

## PDFs escaneados

- Esta skill puede apoyarse en extras OCR, pero no promete OCR perfecto por defecto.
- Si la salida queda vacia, rota o muy pobre, cierra como `BLOCKED_MISSING_CONTEXT` y marca que se requiere OCR mejor.

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
