# Estrategia Jerárquica de Conversión PDF → Markdown

**Versión**: 2.0 (Configuración Estratégica Actualizada)  
**Fecha**: 2026-04-21  
**Basada en**: Instrucción de Configuración Estratégica para Procesamiento de PDF

---

## 📊 Jerarquía de Herramientas

### NIVEL 1: SUPERIOR - Extracción Semántica (PRIORITARIO)

#### ✅ Docling
- **Propósito**: Mejor para estructura semántica, tablas complejas, jerarquía de títulos
- **Ventajas**:
  - Preserva jerarquía de encabezados (H1, H2, H3, etc.)
  - Maneja tablas complejas con excelente fidelidad
  - Detección automática de estructura del documento
  - Soporte para bloques de código
- **Cuándo usar**: Primera opción para todos los PDFs

#### ✅ MarkItDown (Microsoft)
- **Propósito**: Excelente para jerarquía de títulos y estructura general
- **Ventajas**:
  - Conversión directa a Markdown de calidad
  - Preserva la estructura del documento
  - Soporte para múltiples formatos
  - Mejor que alternativas genéricas
- **Cuándo usar**: Si Docling no está disponible

---

### NIVEL 2: HÍBRIDO - Extracción Especializada (FALLBACK)

Combinación de herramientas especializadas para máxima fidelidad:

#### ✅ PyMuPDF (fitz)
- **Propósito**: Extracción rápida, bloques de texto, metadatos
- **Casos de uso**:
  - Detección de bloques de contenido
  - Extracción de metadatos
  - Obtención rápida de texto
  - OCR para PDFs escaneados
- **Instalación**: `pip install pymupdf` (importar como `fitz`)

#### ✅ pdfplumber
- **Propósito**: Extracción de tablas superior en alineación visual
- **Casos de uso**:
  - Extracción específica de tablas
  - Método `.extract_table()` para alineación perfecta
  - Detectar y extraer áreas tabulares
- **Ventaja**: Es superior para tablas en comparación con otras librerías

#### ✅ tabulate
- **Propósito**: Formateo de tablas a Markdown estándar
- **Uso**: Convertir datos de tabla a formato `| columna |`
- **Garantía**: Preserva relaciones entre celdas

#### ✅ pymupdf4llm (opcional)
- **Propósito**: Conversión directa PyMuPDF → Markdown
- **Cuándo usar**: Si necesitas Markdown directamente desde PyMuPDF

**Flujo híbrido recomendado:**
```
PDF → PyMuPDF (bloques) → pdfplumber (tablas) → tabulate (Markdown)
```

---

### NIVEL 3: OCR - Imágenes y Escaneos

Para PDFs que son imágenes o no tienen capa de texto:

#### ✅ EasyOCR
- **Propósito**: OCR moderno y preciso
- **Ventajas**:
  - Soporte multiidioma
  - Presición moderna
  - Fácil de usar
- **Instalación**: `pip install easyocr`

#### ⚠️ Tesseract
- **Propósito**: OCR alternativo (requiere instalación de sistema)
- **Nota**: PyMuPDF tiene soporte integrado para Tesseract

---

## 🎯 Reglas de Ejecución

### Regla 1: Nombres Estándar
```
✅ CORRECTO:  pip install pymupdf pdfplumber docling markitdown
❌ INCORRECTO: pip install pdf-to-markdown-pro
```

### Regla 2: Formato de Tablas
Todas las tablas DEBEN salir en formato estándar Markdown:
```markdown
| Columna 1 | Columna 2 | Columna 3 |
|-----------|-----------|-----------|
| Dato 1    | Dato 2    | Dato 3    |
| Dato 4    | Dato 5    | Dato 6    |
```

**Garantías:**
- ✅ Relación entre celdas preservada
- ✅ Alineación visual correcta
- ✅ Estructura table válida en Markdown

### Regla 3: Prioridad de Salida
1. **Estructura semántica** (títulos, jerarquía)
2. **Tablas** (con alineación visual perfecta)
3. **Contenido** (texto, párrafos)
4. **Metadatos** (fecha, autor, etc.)

### Regla 4: Selección de Estrategia

| Tipo de PDF | Estrategia | Herramientas |
|-------------|-----------|--------------|
| **Documento normal** | NIVEL 1 (Docling/MarkItDown) | docling o markitdown |
| **Con tablas complejas** | NIVEL 1 + NIVEL 2 | docling + pdfplumber |
| **Antiguo/Legacy** | NIVEL 2 (Híbrido) | PyMuPDF + pdfplumber |
| **Imagen/Escaneado** | NIVEL 3 (OCR) | EasyOCR o Tesseract |

---

## 💻 Implementación en Código

### Pseudo-código de la jerarquía

```python
def convert_pdf_to_markdown(pdf_path: str) -> str:
    """
    Conversión jerárquica de PDF a Markdown
    Sigue: Docling > MarkItDown > Híbrido > OCR
    """
    
    # NIVEL 1: Intenta Docling primero
    try:
        from docling.document_converter import DocumentConverter
        converter = DocumentConverter()
        result = converter.convert(pdf_path)
        return result.document.export_to_markdown()
    except ImportError:
        pass
    
    # NIVEL 1: Intenta MarkItDown si Docling falla
    try:
        import markitdown
        with open(pdf_path, 'rb') as f:
            return markitdown.markitdown(f)
    except ImportError:
        pass
    
    # NIVEL 2: Estrategia Híbrida
    try:
        import fitz  # PyMuPDF
        import pdfplumber
        from tabulate import tabulate
        
        # Extrae bloques con PyMuPDF
        doc = fitz.open(pdf_path)
        blocks = []
        
        for page in doc:
            # Busca tablas con pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                for pdf_page in pdf.pages:
                    tables = pdf_page.extract_tables()
                    if tables:
                        for table in tables:
                            md_table = tabulate(table, headers='firstrow', 
                                              tablefmt='github')
                            blocks.append(md_table)
        
        return '\n\n'.join(blocks)
    
    except Exception as e:
        # NIVEL 3: OCR como último recurso
        try:
            import easyocr
            reader = easyocr.Reader(['en', 'es'])
            # OCR implementation...
        except:
            raise ValueError(f"No se pudo convertir PDF: {e}")
```

---

## 📋 Instalación Recomendada

### Opción 1: Instalación Básica (Recomendada)
```bash
pip install pymupdf pdfplumber docling markitdown
```

### Opción 2: Instalación Completa (Con OCR)
```bash
pip install pymupdf pdfplumber docling markitdown easyocr
```

### Opción 3: Desde requirements.txt (Skill)
```bash
pip install -r requirements.txt
```

---

## ✅ Puntos de Validación

Después de cada conversión, verificar:

1. **Estructura** ✅
   - ¿Se preservó la jerarquía de títulos?
   - ¿Los headers están en formato Markdown (#, ##, ###)?

2. **Tablas** ✅
   - ¿Están en formato `| | |`?
   - ¿Las celdas están alineadas?
   - ¿No hay relaciones rotas?

3. **Contenido** ✅
   - ¿El texto se legible?
   - ¿Se preservaron párrafos?
   - ¿Los códigos están en bloques ```?

4. **Metadatos** ✅
   - ¿YAML frontmatter incluido?
   - ¿Fecha y autor presentes?

---

## 🚀 Flujo de Procesamiento Completo

```
PDF Input
    ↓
[¿Docling disponible?]
    ├─ SÍ → Usar Docling (NIVEL 1) ✅
    │
    └─ NO ↓
    [¿MarkItDown disponible?]
        ├─ SÍ → Usar MarkItDown (NIVEL 1) ✅
        │
        └─ NO ↓
        [¿PyMuPDF + pdfplumber disponible?]
            ├─ SÍ → Usar Híbrido (NIVEL 2) ✅
            │
            └─ NO ↓
            [¿EasyOCR disponible?]
                ├─ SÍ → Usar OCR (NIVEL 3) ✅
                │
                └─ NO → ERROR (Instalar librerías)

Markdown Output
    ↓
[Validación de Tablas]
    ├─ OK → Éxito ✅
    └─ ERROR → Re-procesar con pdfplumber
```

---

## 📊 Matriz de Decisión

| Escenario | Estrategia | Prioridad | Esperado |
|-----------|-----------|-----------|----------|
| PDF moderno, bien estructurado | Docling | 1 | Excelente |
| PDF legacy, requiere fidelidad | Híbrido (PyMuPDF+pdfplumber) | 2 | Muy bueno |
| PDF escaneado/imagen | OCR (EasyOCR) | 3 | Bueno |
| Tablas complejas | pdfplumber + tabulate | Alta | Perfectas |
| Títulos jerárquicos | Docling o MarkItDown | Alta | Preservados |

---

## 🎯 Objetivo Final

✅ Máxima fidelidad en conversión PDF → Markdown  
✅ Tablas perfectas en formato estándar  
✅ Estructura semántica preservada  
✅ Jerarquía de títulos mantenida  
✅ 100% independencia de implementación  

---

## 📝 Notas Importantes

1. **Importación de PyMuPDF**: 
   ```python
   # CORRECTO:
   import fitz  # Esto es PyMuPDF
   
   # INCORRECTO:
   import pymupdf  # No funciona
   ```

2. **Fallback automático**: 
   La implementación debe intentar NIVEL 1 → NIVEL 2 → NIVEL 3 automáticamente

3. **Validación obligatoria**: 
   Siempre verificar que las tablas salgan en formato `| | |` estándar

4. **Codificación**: 
   Usar UTF-8 para soportar idiomas múltiples

---

**Versión**: 2.0  
**Última actualización**: 2026-04-21  
**Estrategia confirmada**: ✅ Implementada
