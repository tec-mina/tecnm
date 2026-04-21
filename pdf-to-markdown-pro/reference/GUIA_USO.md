# Guía de Uso - PDF to Markdown Profesional

## 📋 Tabla de Contenidos

1. [Instalación Rápida](#instalación-rápida)
2. [Uso Básico](#uso-básico)
3. [Ejemplos](#ejemplos)
4. [Parámetros](#parámetros)
5. [Salida](#salida)
6. [Solución de Problemas](#solución-de-problemas)

## Instalación Rápida

### Paso 1: Instalar dependencias
```bash
pip install -r requirements.txt
```

### Paso 2: Verificar instalación
```bash
python scripts/extractor.py --version
# O simplemente:
python -c "import pdfplumber, fitz, tabulate; print('✓ Todo instalado')"
```

## Uso Básico

### Opción 1: Línea de comandos (más fácil)

```bash
# Conversión simple
python scripts/pdf_to_md.py documento.pdf -o documento.md

# Con validación
python scripts/pdf_to_md.py documento.pdf -o documento.md --verify

# Con auto-corrección
python scripts/pdf_to_md.py documento.pdf -o documento.md --fix

# Completo
python scripts/pdf_to_md.py documento.pdf -o documento.md --verify --fix

# Exportar como JSON también
python scripts/pdf_to_md.py documento.pdf -o documento.md --json
```

### Opción 2: Python (más flexible)

```python
from scripts.pdf_to_md import PDFToMarkdown

# Crear convertidor
converter = PDFToMarkdown(verify=True, fix=True)

# Procesar
result = converter.process('documento.pdf', output='documento.md')

# Acceder a componentes
print(f"Calidad: {result['validation']['quality_score']}%")
print(f"Tablas encontradas: {len(result['tables'])}")
print(f"Imágenes: {len(result['images'])}")
```

## Ejemplos

### Ejemplo 1: Documento simple

```bash
python scripts/pdf_to_md.py reporte.pdf -o reporte.md
```

**Resultado:**
```
---
source: reporte.pdf
pages: 5
extraction_date: 2024-01-15T10:30:00
language: es
tables: 2
has_images: false
quality_score: 95.3%
is_valid: true
---

# Reporte de Ventas

## Resumen
...

## Tablas
...
```

### Ejemplo 2: Documento con muchas tablas

```bash
python scripts/pdf_to_md.py datos.pdf -o datos.md --lang es
```

**Las tablas se extraen con estructura perfecta gracias a pdfplumber:**
```
| Columna 1 | Columna 2 | Columna 3 |
|-----------|-----------|-----------|
| Valor A   | Valor B   | Valor C   |
| Valor D   | Valor E   | Valor F   |
```

### Ejemplo 3: Documento escaneado

```bash
# Detecta automáticamente idioma
python scripts/pdf_to_md.py documento_escaneado.pdf -o documento.md --lang es
```

### Ejemplo 4: Procesamiento por lotes

```python
from pathlib import Path
from scripts.pdf_to_md import PDFToMarkdown

converter = PDFToMarkdown(verify=True, fix=True)
pdf_dir = Path('documentos')

for pdf_file in pdf_dir.glob('*.pdf'):
    output = pdf_file.with_suffix('.md')
    print(f"Procesando {pdf_file.name}...", end='')
    
    result = converter.process(str(pdf_file), output=str(output))
    
    quality = result['validation']['quality_score']
    print(f" ✓ ({quality:.0f}%)")
```

### Ejemplo 5: Acceso detallado a datos

```python
from scripts.extractor import PDFExtractor

extractor = PDFExtractor()
result = extractor.extract('documento.pdf')

# Obtener componentes
print("=== TEXTO ===")
print(result['raw_text'][:200])

print("\n=== TABLAS ===")
for table in result['tables']:
    print(f"Tabla p{table['page']}: {table['rows']}x{table['cols']}")
    print(table['markdown'])

print("\n=== IMÁGENES ===")
for img in result['images']:
    print(img['reference'])

print("\n=== METADATOS ===")
for k, v in result['metadata'].items():
    print(f"{k}: {v}")
```

## Parámetros

### Para pdf_to_md.py (CLI)

```bash
python scripts/pdf_to_md.py <pdf> [opciones]
```

| Parámetro | Descripción | Default |
|-----------|-------------|---------|
| `pdf` | Archivo PDF (requerido) | - |
| `-o, --output` | Archivo de salida .md | stdout |
| `--lang` | Idioma: es, en, auto | auto |
| `--verify` | Validar contenido | true |
| `--fix` | Auto-corregir | true |
| `--json` | Exportar JSON también | false |

### Para PDFToMarkdown (Python)

```python
converter = PDFToMarkdown(
    verify=True,    # ¿Validar?
    fix=True        # ¿Corregir?
)

result = converter.process(
    pdf_path='documento.pdf',  # Ruta del PDF
    lang='auto',               # Idioma
    output='documento.md'      # Salida (opcional)
)
```

## Salida

### Estructura del resultado

```python
result = {
    'markdown': str,           # Contenido final formateado
    'metadata': {
        'source_file': str,
        'total_pages': int,
        'extraction_date': str,
        'language': str,
        'tables_count': int,
        'has_images': bool,
        'quality_score': float,
        'issues_found': int
    },
    'tables': [                # Tablas extraídas
        {
            'page': int,
            'table_num': int,
            'rows': int,
            'cols': int,
            'markdown': str,   # Formato Markdown
            'raw': list        # Datos crudos
        }
    ],
    'images': [                # Imágenes encontradas
        {
            'page': int,
            'image_num': int,
            'reference': str   # Referencia Markdown
        }
    ],
    'validation': {            # Reporte de calidad
        'quality_score': float,
        'is_valid': bool,
        'issues': list,
        'warnings': list,
        'recommendations': list
    }
}
```

### Frontmatter YAML incluido

El archivo Markdown generado incluye metadatos al inicio:

```yaml
---
source: documento.pdf
pages: 42
extraction_date: 2024-01-15T10:30:00
language: es
tables: 5
has_images: true
quality_score: 95.3%
is_valid: true
---

# Contenido...
```

## Solución de Problemas

### "ModuleNotFoundError: No module named 'pdfplumber'"

**Solución:**
```bash
pip install pdfplumber
# O mejor aún:
pip install -r requirements.txt
```

### "Las tablas no se ven bien"

**Posible causa:** PDF con tablas sin bordes claros

**Soluciones:**
1. Verificar que el PDF tiene tablas estructuradas
2. Intentar con `--lang` específico:
   ```bash
   python scripts/pdf_to_md.py documento.pdf -o documento.md --lang es
   ```
3. Revisar manualmente las tablas en el archivo generado

### "Calidad muy baja (< 80%)"

**Soluciones:**
1. Intentar con `--fix`:
   ```bash
   python scripts/pdf_to_md.py documento.pdf --fix
   ```
2. El PDF puede tener problemas - revisar manualmente
3. Consultar el archivo `.json` para detalles de problemas:
   ```bash
   python scripts/pdf_to_md.py documento.pdf --json
   ```

### "Caracteres especiales mal codificados"

**Solución:**
```bash
python scripts/pdf_to_md.py documento.pdf --lang es
```

El parámetro `--lang` ayuda a detectar la codificación correcta.

### "¿Cómo extraigo solo las tablas?"

```python
from scripts.extractor import PDFExtractor
import json

extractor = PDFExtractor()
result = extractor.extract('documento.pdf')

# Guardar solo tablas
for table in result['tables']:
    print(table['markdown'])

# O como JSON
with open('tablas.json', 'w') as f:
    json.dump(result['tables'], f, indent=2)
```

### "¿Cómo proceso múltiples PDFs?"

```bash
#!/bin/bash
for pdf in *.pdf; do
    echo "Procesando $pdf..."
    python scripts/pdf_to_md.py "$pdf" -o "${pdf%.pdf}.md"
done
```

O en Python:
```python
from pathlib import Path
from scripts.pdf_to_md import PDFToMarkdown

converter = PDFToMarkdown()
for pdf in Path('.').glob('*.pdf'):
    output = pdf.with_suffix('.md')
    converter.process(str(pdf), output=str(output))
```

## Tips de Uso

### 💡 Tip 1: Verificación de calidad
```bash
# Genera JSON para análisis detallado
python scripts/pdf_to_md.py documento.pdf --json
# Mira documento.json para ver problemas específicos
```

### 💡 Tip 2: Procesamiento optimizado
```python
# Para lotes grandes, deshabilita validación si no la necesitas
converter = PDFToMarkdown(verify=False, fix=False)
# Mucho más rápido para volúmenes altos
```

### 💡 Tip 3: Exportar componentes
```python
result = converter.process('documento.pdf')

# Guardar solo tablas
import json
with open('tablas.json', 'w') as f:
    json.dump(result['tables'], f, indent=2)

# Guardar metadatos
with open('metadata.json', 'w') as f:
    json.dump(result['metadata'], f, indent=2)
```

### 💡 Tip 4: Integración con otros sistemas

```python
# Procesar y enviar a API
result = converter.process('documento.pdf')

import requests
requests.post('https://mi-api.com/documentos', json={
    'content': result['markdown'],
    'metadata': result['metadata'],
    'quality': result['validation']['quality_score']
})
```

## Flujo de Procesamiento Visual

```
PDF Input
    ↓
[1] EXTRACCIÓN
    ├─ pdfminer.six → Texto preciso
    ├─ pdfplumber → Tablas perfectas
    ├─ PyMuPDF → Imágenes & metadatos
    ↓
[2] FORMATEO
    ├─ tabulate → Tablas a Markdown
    ├─ langdetect → Detectar idioma
    ↓
[3] VALIDACIÓN (si verify=True)
    ├─ Analizar contenido
    ├─ Calcular puntuación 0-100%
    ├─ Identificar problemas
    ↓
[4] CORRECCIÓN (si fix=True y hay problemas)
    ├─ Normalizar espacios
    ├─ Reparar tablas
    ├─ Consistencia headers
    ↓
[5] EXPORTACIÓN
    ├─ Añadir frontmatter YAML
    ├─ Generar Markdown final
    ├─ Compilar JSON (si --json)
    ↓
Markdown + Metadatos (✓ Listo)
```

## Casos de Uso Típicos

### 📚 Digitalizador de documentos
```bash
# Convertir folder completo
for f in *.pdf; do python scripts/pdf_to_md.py "$f" -o "${f%.pdf}.md"; done
```

### 📊 Extractor de tablas
```python
result = extractor.extract('datos.pdf')
for table in result['tables']:
    print(table['markdown'])
```

### 📖 Conversor a documentación
```bash
python scripts/pdf_to_md.py libro.pdf -o libro.md --verify
# Editar libro.md y usar en wiki/documentación
```

### 🔄 Pipeline de automatización
```python
converter = PDFToMarkdown(verify=True, fix=True)
for pdf in get_new_pdfs():
    result = converter.process(pdf)
    if result['validation']['is_valid']:
        save_to_database(result)
    else:
        flag_for_review(result)
```

¡Listo para usar! 🚀
