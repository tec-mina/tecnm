# PDF to Markdown Profesional

**Skill unificada para extraer PDFs a Markdown limpio y estructurado**

Integra 3 skills en 1 solución profesional usando las mejores librerías especializadas del mercado.

## ✨ Características

- 🔵 **Tablas perfectas** con pdfplumber (mejor del mercado)
- 🟢 **Imágenes y metadatos** con PyMuPDF
- 🟠 **Texto preciso** con pdfminer.six
- 🟡 **Formateo profesional** con tabulate
- ✅ **Validación automática** de calidad 0-100%
- 🔧 **Corrección inteligente** de problemas
- 📊 **Múltiples formatos de salida** (Markdown + JSON)

## 🚀 Inicio Rápido

### 1. Instalar
```bash
pip install -r requirements.txt
```

### 2. Usar (CLI)
```bash
python scripts/pdf_to_md.py documento.pdf -o documento.md
```

### 3. Usar (Python)
```python
from scripts.pdf_to_md import PDFToMarkdown

converter = PDFToMarkdown()
result = converter.process('documento.pdf', output='documento.md')
```

## 📁 Estructura Profesional

```
pdf-to-markdown-profesional/
├── SKILL.md                    # Documentación oficial
├── README.md                   # Este archivo
├── requirements.txt            # Dependencias
├── scripts/
│   ├── extractor.py           # Extractor multi-librería
│   └── pdf_to_md.py           # Conversor completo
└── reference/
    ├── LIBRERIAS.md           # Análisis de librerías
    └── GUIA_USO.md            # Guía completa
```

## 🎯 Librerías Usadas

| Librería | Uso | Razón |
|----------|-----|-------|
| **pdfplumber** | Tablas | Mejor del mercado para detectar estructura |
| **PyMuPDF** | Imágenes & Metadatos | Acceso completo a recursos PDF |
| **pdfminer.six** | Texto preciso | Preserva estructura y espacios |
| **tabulate** | Formateo | Convierte tablas a Markdown perfecto |
| **langdetect** | Detectar idioma | Identifica automáticamente idioma |
| **Pillow** | Procesamiento imagen | Conversión de formatos |

## 📊 Comparativa con Versiones Anteriores

| Feature | pdf-processing | pdf-to-markdown | md-verifier | **Pro** |
|---------|---|---|---|---|
| Extrae PDF | ✓ | ✓ | ✗ | ✓ |
| Tablas | Básicas | Básicas | ✗ | **⭐ Perfectas** |
| Valida | ✗ | ✗ | ✓ | **✓ Integrado** |
| Corrige | ✗ | ✗ | ✓ | **✓ Integrado** |
| Una sola herramienta | ✗ | ✗ | ✗ | **✓** |
| Librerías especializadas | Parcial | Parcial | - | **✓ Todas** |

## 💻 Ejemplos de Uso

### Conversión Simple
```bash
python scripts/pdf_to_md.py reporte.pdf -o reporte.md
```

### Con Validación
```bash
python scripts/pdf_to_md.py documento.pdf -o documento.md --verify
```

### Con Auto-Corrección
```bash
python scripts/pdf_to_md.py documento.pdf -o documento.md --verify --fix
```

### Procesamiento por Lotes (Python)
```python
from pathlib import Path
from scripts.pdf_to_md import PDFToMarkdown

converter = PDFToMarkdown(verify=True, fix=True)

for pdf in Path('.').glob('*.pdf'):
    output = pdf.with_suffix('.md')
    converter.process(str(pdf), output=str(output))
    print(f"✓ {pdf.name}")
```

### Acceso a Tablas
```python
from scripts.extractor import PDFExtractor

extractor = PDFExtractor()
result = extractor.extract('datos.pdf')

for table in result['tables']:
    print(f"Tabla p{table['page']}: {table['rows']}x{table['cols']}")
    print(table['markdown'])  # Ya formateada para Markdown
```

## 📋 Parámetros

### CLI: pdf_to_md.py

```bash
python scripts/pdf_to_md.py <pdf> [opciones]
```

```
Opciones:
  -o, --output   Archivo de salida .md
  --lang         Idioma: es, en, auto (default: auto)
  --verify       Validar contenido (default: true)
  --fix          Auto-corregir (default: true)
  --json         Exportar JSON también (default: false)
```

### Python: PDFToMarkdown

```python
converter = PDFToMarkdown(
    verify=True,    # Validar contenido
    fix=True        # Auto-corregir problemas
)

result = converter.process(
    pdf_path='documento.pdf',
    lang='auto',
    output='documento.md'  # Opcional
)
```

## 📤 Salida

### Estructura del Resultado

```python
{
    'markdown': str,        # Contenido Markdown con frontmatter
    'metadata': dict,       # Información del documento
    'tables': list,         # Tablas extraídas con formato
    'images': list,         # Referencias a imágenes
    'validation': dict      # Reporte de calidad
}
```

### Frontmatter YAML Incluido

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

# Contenido Markdown aquí...
```

### Puntuación de Calidad

- **90-100%** ✓ Excelente, listo inmediatamente
- **80-89%** ✓ Bueno, con correcciones menores
- **70-79%** ⚠️ Aceptable, requiere revisión
- **<70%** ❌ Pobre, requiere edición manual

## 🔧 Instalación Detallada

### Requisitos
- Python 3.8+
- pip

### Paso 1: Clonar/Descargar
```bash
cd pdf-to-markdown-profesional
```

### Paso 2: Crear entorno virtual (recomendado)
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### Paso 3: Instalar dependencias
```bash
pip install -r requirements.txt
```

### Paso 4: Verificar instalación
```bash
python -c "import pdfplumber, fitz, tabulate; print('✓ Todo instalado')"
```

## 📖 Documentación

- **SKILL.md**: Descripción oficial de la skill (5 min)
- **reference/LIBRERIAS.md**: Análisis técnico de cada librería (15 min)
- **reference/GUIA_USO.md**: Guía completa con ejemplos (20 min)
- **README.md**: Este archivo (10 min)

## ❓ Preguntas Frecuentes

### ¿Necesito los 3 archivos .skill anteriores?
No, esto los reemplaza completamente. Descarta los anteriores.

### ¿Funciona sin internet?
Sí, completamente offline una vez instaladas las librerías.

### ¿Soporta PDFs escaneados?
Sí, detecta automáticamente y usa OCR si está disponible.

### ¿Qué pasa si una tabla no se extrae bien?
Las tablas mal estructuradas pueden no detectarse. Revisa manualmente o consulta la validación.

### ¿Puedo procesar múltiples PDFs?
Sí, mira ejemplos en reference/GUIA_USO.md

### ¿Preserva las imágenes?
Las preserva como referencias. Para incrustadas, requiere modificación del código.

### ¿Compatible con Windows/Mac/Linux?
Sí, Python puro, funciona en todos.

## 🐛 Solución de Problemas

### Error: "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Las tablas no se ven bien
1. Verificar que el PDF tiene tablas estructuradas
2. Intentar con idioma específico: `--lang es`
3. Revisar manualmente en el archivo generado

### Baja calidad (< 80%)
1. Usar `--fix` para auto-corregir
2. Revisar el reporte de validación
3. Editar manualmente si es necesario

### Caracteres especiales mal codificados
```bash
python scripts/pdf_to_md.py documento.pdf --lang es
```

## 📊 Casos de Uso

✅ Convertir documentos a wikis/documentación  
✅ Extraer datos de PDFs para procesamiento  
✅ Digitalizar archivos legacy  
✅ Automatizar procesamiento de reportes  
✅ Crear backups en formato texto  

## 🚀 Próximas Mejoras

- [ ] GUI interactiva para preview
- [ ] Soporte para PDF con capas
- [ ] Detección mejorada de columnas múltiples
- [ ] Export a ReStructuredText y Asciidoc
- [ ] Caché de OCR para documentos grandes

## 📄 Licencia

MIT - Libre para uso comercial y personal

## 👤 Información

**Skill Unificada**: PDF to Markdown Profesional  
**Versión**: 1.0  
**Basada en**: pdf-processing + pdf-to-markdown + md-verifier  
**Mejorada con**: Librerías especializadas y validación integrada  

## 🎓 Aprendizaje Recomendado

1. **5 min**: Lee SKILL.md
2. **5 min**: Ejecuta `python scripts/pdf_to_md.py ejemplo.pdf -o ejemplo.md`
3. **10 min**: Revisa reference/LIBRERIAS.md para entender por qué cada librería
4. **15 min**: Lee reference/GUIA_USO.md para casos avanzados
5. **Práctica**: Usa con tus propios PDFs

## ✅ Verificación

```bash
# Probar instalación
python -c "
from scripts.extractor import PDFExtractor
from scripts.pdf_to_md import PDFToMarkdown
print('✓ Skill lista para usar')
"
```

---

¿Listo para convertir PDFs a Markdown profesional? 🚀

Comienza con:
```bash
python scripts/pdf_to_md.py documento.pdf -o documento.md
```
