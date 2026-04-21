---
title: PDF a Markdown Profesional
description: Extrae PDFs a Markdown limpio con tablas perfectas, validación de calidad y corrección automática
triggers:
  - "convert pdf to markdown"
  - "pdf to markdown"
  - "extract pdf"
  - "pdf extraction"
  - "markdown conversion"
tags:
  - pdf
  - markdown
  - extraction
  - conversion
  - tables
  - documentation
version: 1.0
dependencies:
  - pdfplumber>=0.9.0
  - PyMuPDF>=1.23.0
  - pdfminer.six>=20221105
  - tabulate>=0.9.0
  - Pillow>=10.0.0
  - langdetect>=1.0.9
author: TecNM
license: MIT
---

# PDF a Markdown Profesional

Extrae documentos PDF a Markdown limpio, estructurado y definitivo, con soporte avanzado para tablas, preservación de formato y validación de calidad.

**Integración de 3 skills** en una sola solución profesional con librerías especializadas de última generación.

## Descripción

Skill unificada que combina:
- **pdfplumber**: Mejor extracción de tablas y estructuras
- **pymupdf**: Soporte de imágenes y metadatos
- **pdfminer.six**: Extracción de texto precisa
- **tabulate**: Conversión inteligente de tablas

Con validación automática, corrección inteligente y soporte multiidioma.

## Características principales

### Extracción Avanzada
- ✅ Tablas extraídas correctamente preservando estructura
- ✅ Texto con detección automática de espacios y párrafos
- ✅ Imágenes identificadas y referenciadas
- ✅ Metadatos completos (título, autor, fechas)
- ✅ Soporte para PDFs complejos y multicolumna

### Validación de Calidad
- Análisis de cada sección
- Detección de contenido problemático
- Puntuación de calidad 0-100%
- Recomendaciones automáticas

### Corrección Inteligente
- Normalización de espacios
- Reparación de tablas deformadas
- Consistencia de formato
- Limpieza de caracteres especiales

## Cuándo usar

✅ Convertir PDF a Markdown de calidad profesional
✅ Extraer tablas completas manteniendo estructura
✅ Procesar lotes de documentos automáticamente
✅ Verificar integridad de conversiones
✅ Crear documentación desde PDFs

## Casos de uso

- **Documentación técnica**: PDFs → Wiki/Markdown
- **Bases de datos**: Tablas PDF → CSV/Markdown
- **Reportes**: Extraer datos de PDFs
- **Archivos**: Convertir documentos legacy
- **Automatización**: Procesar lotes de PDFs

## Parámetros

### Entrada
- `pdf_path`: Ruta del archivo PDF
- `lang`: Idioma ('es', 'en', 'auto')
- `verify_quality`: Validar contenido (default: true)
- `auto_fix`: Corregir automáticamente (default: true)
- `extract_tables`: Extraer tablas avanzadas (default: true)
- `preserve_images`: Mantener referencias de imágenes (default: true)

### Salida
```python
{
    'markdown': str,           # Contenido markdown
    'metadata': {              # Información del documento
        'source': str,
        'pages': int,
        'language': str,
        'quality_score': float
    },
    'tables': list,            # Tablas extraídas
    'images': list,            # Referencias de imágenes
    'validation': {            # Reporte de validación
        'is_valid': bool,
        'score': float,
        'issues': list
    }
}
```

## Ejemplos

### Uso básico
```python
from pdf_to_markdown_profesional import PDFToMarkdown

converter = PDFToMarkdown()
result = converter.process('documento.pdf')
print(result['markdown'])
```

### Con opciones avanzadas
```python
result = converter.process(
    'documento.pdf',
    lang='es',
    verify_quality=True,
    auto_fix=True,
    extract_tables=True
)
```

### CLI
```bash
python scripts/extractor.py documento.pdf -o documento.md
python scripts/pdf_to_md.py documento.pdf --verify --fix
```

## Librerías usadas

- **pdfplumber** (≥0.9.0): Tablas y estructuras
- **PyMuPDF** (≥1.23.0): Imágenes y metadatos
- **pdfminer.six** (≥20221105): Extracción de texto
- **tabulate** (≥0.9.0): Formateo de tablas
- **Pillow** (≥10.0.0): Procesamiento de imágenes
- **langdetect** (≥1.0.9): Detección de idioma

## Diferencias con versiones anteriores

### vs pdf-processing
- ✅ Extracción de tablas mejorada con pdfplumber
- ✅ Mejor detección de estructura
- ✅ Formateo profesional de tablas

### vs pdf-to-markdown
- ✅ Soporte completo de tablas
- ✅ Validación integrada
- ✅ Auto-corrección

### vs md-verifier
- ✅ Integrado en un solo paso
- ✅ Mejor extracción de origen
- ✅ Librerías especializadas
