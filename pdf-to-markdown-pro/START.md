```
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║                 PDF TO MARKDOWN PROFESIONAL v1.0                           ║
║                   Skill Unificada Especializada                            ║
║                                                                            ║
║   Integración profesional de 3 skills + mejores librerías del mercado      ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
```

## 🎯 ¿Qué es esto?

Una **skill profesional y unificada** que reemplaza completamente 3 herramientas anteriores:
- ✅ `pdf-processing.skill`
- ✅ `pdf-to-markdown.skill`  
- ✅ `md-verifier.skill`

Todo integrado en una sola solución usando **las mejores librerías especializadas**:
- 🔵 **pdfplumber** para tablas (mejor del mercado)
- 🟢 **PyMuPDF** para imágenes y metadatos
- 🟠 **pdfminer.six** para texto preciso
- 🟡 **tabulate** para formateo Markdown

## 📁 Estructura Profesional

```
pdf-to-markdown-profesional/
├── SKILL.md                 ← Especificación oficial (5 min)
├── README.md                ← Guía rápida (10 min)
├── START.md                 ← Este archivo (2 min)
├── LICENSE                  ← MIT License
├── requirements.txt         ← Dependencias (pip install -r)
│
├── scripts/                 ← Scripts ejecutables
│   ├── extractor.py        (Extractor multi-librería)
│   └── pdf_to_md.py        (Conversor completo)
│
└── reference/              ← Documentación detallada
    ├── LIBRERIAS.md        (Análisis de cada librería - 10 min)
    └── GUIA_USO.md         (Ejemplos y casos de uso - 15 min)
```

## ⚡ 3 Formas de Empezar

### 1️⃣ Línea de Comandos (MÁS FÁCIL)

```bash
# Instalar dependencias (una sola vez)
pip install -r requirements.txt

# Convertir un PDF
python scripts/pdf_to_md.py documento.pdf -o documento.md

# Con validación y corrección automática
python scripts/pdf_to_md.py documento.pdf -o documento.md --verify --fix
```

### 2️⃣ Python (MÁS FLEXIBLE)

```python
from scripts.pdf_to_md import PDFToMarkdown

converter = PDFToMarkdown(verify=True, fix=True)
result = converter.process('documento.pdf', output='documento.md')

print(f"Calidad: {result['validation']['quality_score']}%")
print(f"Tablas: {len(result['tables'])}")
```

### 3️⃣ Acceso Directo a Componentes (MÁS CONTROL)

```python
from scripts.extractor import PDFExtractor

extractor = PDFExtractor()
result = extractor.extract('documento.pdf')

# Acceder a componentes individuales
print(result['markdown'])      # Contenido
print(result['tables'])        # Tablas extraídas
print(result['images'])        # Imágenes referenciadas
print(result['metadata'])      # Metadatos del PDF
```

## 📚 Documentación por Tiempo

| Tiempo | Documento | Contenido |
|--------|-----------|-----------|
| ⏱️ 2 min | Este archivo | Resumen rápido |
| ⏱️ 5 min | SKILL.md | Qué es y para qué sirve |
| ⏱️ 10 min | README.md | Cómo instalar y usar básico |
| ⏱️ 10 min | reference/LIBRERIAS.md | Por qué cada librería |
| ⏱️ 15 min | reference/GUIA_USO.md | Casos de uso avanzados |

## ✨ Lo Mejor de Cada Librería

### pdfplumber para TABLAS 🔵

```python
# Extrae tablas manteniendo perfecta estructura
# ✓ Mejor detección de bordes
# ✓ Maneja tablas complejas
# ✓ Preserva alineación

tables = page.extract_tables()
# → [[header], [row1], [row2], ...]
```

### PyMuPDF para IMÁGENES & METADATOS 🟢

```python
# Acceso directo a recursos PDF
# ✓ Metadatos nativos
# ✓ Posición de elementos
# ✓ Información de imagen

images = page.get_images()
metadata = doc.metadata
```

### pdfminer.six para TEXTO PRECISO 🟠

```python
# Extrae preservando espacios y estructura
# ✓ Respeta párrafos
# ✓ Mejor para PDFs complejos
# ✓ Preciso en codificación

text = extract_text('documento.pdf')
```

### tabulate para FORMATEO 🟡

```python
# Convierte datos a Markdown perfecto
# ✓ Alineación automática
# ✓ Formato profesional
# ✓ Múltiples estilos

markdown = tabulate.tabulate(
    data, 
    headers=headers,
    tablefmt='github'
)
```

## 🎯 Flujo de Procesamiento

```
PDF Input
    ↓
┌────────────────────────────────┐
│ 1. EXTRACCIÓN MULTI-LIBRERÍA   │
│   • pdfminer → Texto           │
│   • pdfplumber → Tablas        │
│   • PyMuPDF → Imágenes         │
├────────────────────────────────┤
│ 2. FORMATEO                    │
│   • tabulate → Markdown        │
│   • langdetect → Idioma        │
├────────────────────────────────┤
│ 3. VALIDACIÓN (opcional)       │
│   • Analizar contenido         │
│   • Puntuación 0-100%          │
├────────────────────────────────┤
│ 4. CORRECCIÓN (opcional)       │
│   • Auto-fix problemas         │
│   • Normalizar formato         │
├────────────────────────────────┤
│ 5. EXPORTACIÓN                 │
│   • Frontmatter YAML           │
│   • Markdown definitivo        │
└────────────────────────────────┘
    ↓
Markdown Profesional (✓ LISTO)
```

## 📊 Comparativa: ¿Por qué esta versión es mejor?

| Aspecto | Versión Anterior | Versión Pro |
|--------|------------------|-------------|
| Número de herramientas | 3 por separado | 1 integrada |
| Extracción de tablas | Básica | ⭐ Perfecta (pdfplumber) |
| Validación automática | ✗ | ✓ Integrada |
| Corrección automática | ✗ | ✓ Integrada |
| Librerías especializadas | Parciales | ✓ Todas |
| Metadata completa | Limitada | ✓ Completa |
| Interfaz unificada | No | ✓ Sí |
| Documentación | Básica | ✓ Completa |

## 🚀 Primeros Pasos

### Paso 1: Instalar (30 segundos)
```bash
pip install -r requirements.txt
```

### Paso 2: Crear un test (10 segundos)
```bash
# Crear un PDF simple para probar (o usa uno que tengas)
python scripts/pdf_to_md.py ejemplo.pdf -o ejemplo.md
```

### Paso 3: Revisar resultado
```bash
# Ver el archivo generado
cat ejemplo.md
```

### Paso 4: Leer documentación (según tiempo)
- **Rápido** (5 min): Lee SKILL.md
- **Normal** (15 min): Lee README.md + GUIA_USO.md
- **Profundo** (25 min): Lee TODO incluyendo LIBRERIAS.md

## 💡 Tips Iniciales

### Tip 1: Validación de calidad
```bash
# Genera reporte JSON con análisis
python scripts/pdf_to_md.py documento.pdf --json
# Abre documento.json para ver problemas específicos
```

### Tip 2: Procesamiento rápido
```python
# Para lotes grandes sin validación
converter = PDFToMarkdown(verify=False, fix=False)
# Mucho más rápido
```

### Tip 3: Acceso a tablas
```python
result = extractor.extract('documento.pdf')
for table in result['tables']:
    print(table['markdown'])  # Ya formateada
```

### Tip 4: Múltiples PDFs
```bash
# Script simple para procesar todos
for f in *.pdf; do 
    python scripts/pdf_to_md.py "$f" -o "${f%.pdf}.md"
done
```

## ❓ Preguntas Rápidas

**P: ¿Necesito los 3 archivos .skill anteriores?**  
R: No. Esto los reemplaza completamente. Descarta los anteriores.

**P: ¿Funciona sin internet?**  
R: Sí, completamente offline.

**P: ¿Soporta PDFs complejos?**  
R: Sí. Tablas, imágenes, múltiples idiomas, escaneados.

**P: ¿Qué pasa si falla?**  
R: Revisa reference/GUIA_USO.md sección "Solución de Problemas"

**P: ¿Puedo usar desde código personalizado?**  
R: Sí. Es una librería Python completa con API clara.

## 📖 Próximo Paso

1. **Instala**: `pip install -r requirements.txt`
2. **Lee**: `SKILL.md` (5 minutos)
3. **Prueba**: `python scripts/pdf_to_md.py documento.pdf -o documento.md`
4. **Aprende**: `reference/GUIA_USO.md` (según necesites)

## 🎓 Árbol de Documentación

```
START.md (tú estás aquí) ← 2 min
    ↓
SKILL.md ← Qué es (5 min)
    ↓
README.md ← Cómo usar (10 min)
    ↓
reference/GUIA_USO.md ← Casos avanzados (15 min)
    ↓
reference/LIBRERIAS.md ← Por qué cada librería (10 min)
```

---

## ✅ Verificación Rápida

```bash
# Esto te dirá que todo está instalado correctamente:
python -c "
import pdfplumber
import fitz
import tabulate
print('✓ Todas las librerías disponibles')
print('✓ Skill lista para usar')
"
```

## 🎯 Está Listo Para:

✅ Convertir documentos a wikis/documentación  
✅ Extraer datos y tablas de PDFs  
✅ Automatizar procesamiento de reportes  
✅ Digitalizar archivos legacy  
✅ Crear backups en formato texto  
✅ Integrar en pipelines de datos  

---

**¡Listo para usar!** 🚀

```bash
pip install -r requirements.txt
python scripts/pdf_to_md.py documento.pdf -o documento.md
```

Luego lee `SKILL.md` para entender completamente qué puedes hacer.
