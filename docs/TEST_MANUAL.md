# Testing Manual — PDF Extractor

## 🚀 Inicio Rápido

```bash
cd /Users/molina/ClaudeProjects/tecnm/.claude/worktrees/quizzical-pare-6b2b10/pdf_extractor

# Start server
python3 -m pdf_extractor serve --host 0.0.0.0 --port 8080
```

Luego abre: **http://localhost:8080/web**

---

## 📊 Escenarios de Test

### Escenario 1: PDF Nativo (con tablas)
**PDF:** `JEFATURA_DE_DEPARTAMENTO_DE_PROGRAMACI_N_Y_PRESUPUESTO_CENTRAL.pdf`

**Steps:**
1. Arrastra el PDF a la interfaz
2. Espera análisis (`analizando...`)
3. En "Auto" debe mostrar: `Auto · text:fast, tables:camelot` (recomendación del servidor)
4. Prueba estos métodos:
   - ✅ `text:fast` (debe funcionar rápido)
   - ✅ `text:pdfminer` (debe extraer con precisión)
   - ✅ `text:docling` (debe usar IA para layout, si está instalado)
   - ✅ `text:fast,tables:pdfplumber` (combo recomendada)
5. Descarga cualquier resultado y verifica que sea Markdown válido

**Esperado:** Todos los métodos text funcionan ✓

---

### Escenario 2: PDF Escaneado (sin texto)
**PDF:** `19012026-MAT.pdf` (o cualquiera que sea escaneado)

**Steps:**
1. Arrastra el PDF escaneado
2. Observa en "Auto": debe mostrar `Auto · ocr:tesseract-basic` (detectó escaneado)
3. Intenta estas estrategias:
   - ✅ `ocr:tesseract-basic` (debe extraer con OCR)
   - ✅ `ocr:tesseract-advanced` (OCR con preprocessing)
   - ✅ `text:fast` → **debe fallar y auto-fallback a OCR**
   - ⚠️ `text:docling` → Si docling NO está instalado, debe estar deshabilitado (❌)

4. Para el caso `text:fast` en escaneado:
   - Verifica que falle silenciosamente
   - Checkea `X-Fallback-Used` header en la descarga (debe mostrar: `text:fast → ocr:tesseract-basic [OCR]`)

**Esperado:** 
- OCR funciona ✓
- text:fast auto-fallback a OCR ✓
- Docling muestra como "no disponible" si no instalado ✓

---

### Escenario 3: Errores Claros
**Para provocar error:**
1. Abre un PDF vacío o muy pequeño
2. Intenta extraer con cualquier método
3. Espera error HTTP 422

**Esperado:**
- ❌ Antes: `HTTP 422 — [object Object]`
- ✅ Después: Mensaje claro multiline:
  ```
  HTTP 422 — ❌ No se extrajo contenido del PDF.
  
  Posibles causas:
  • El PDF está escaneado...
  • Todas las estrategias...
  ```

---

### Escenario 4: Métodos No Instalados
**Para docling (si no está en pip install):**

1. Verifica dropdown "Solo texto" → busca docling
2. Observa: `❌ Docling AI... (no disponible)` en gris, disabled
3. Readiness banner debe mostrar: `⏳ Faltan modelos por descargar`
4. Click en banner → descarga docling + modelos
5. Espera a que termine
6. Dropdown se actualiza automáticamente
7. Ahora puedes seleccionar docling

**Esperado:**
- Métodos no-instalados deshabilitados ✓
- Warmup on-demand funciona ✓
- UI se actualiza sin recargar ✓

---

## 🔍 Validación Técnica

### Via CLI (sin server)
```bash
python3 -m pdf_extractor extract \
  --strategy text:fast \
  --output extracted.md \
  docs/raw_pdf/JEFATURA_DE_DEPARTAMENTO_DE_PROGRAMACI_N_Y_PRESUPUESTO_CENTRAL.pdf
```

### Via API (curl)
```bash
# Inspect un PDF (detecta tipo + sugiere estrategias)
curl -X POST \
  -F file=@docs/raw_pdf/JEFATURA_DE_DEPARTAMENTO_DE_PROGRAMACI_N_Y_PRESUPUESTO_CENTRAL.pdf \
  http://localhost:8080/api/v1/inspect | jq .

# Extract con estrategia específica
curl -X POST \
  -F file=@docs/raw_pdf/JEFATURA_DE_DEPARTAMENTO_DE_PROGRAMACI_N_Y_PRESUPUESTO_CENTRAL.pdf \
  -F strategies=text:fast \
  http://localhost:8080/api/v1/extract \
  -H "Accept: text/markdown" \
  -o output.md
```

### Headers Clave
Después de extraer, revisa estos headers:
- `X-Quality-Score`: 0-100 (qué tan bien se extrajo)
- `X-Pages`: número de páginas procesadas
- `X-Features-Used`: qué métodos se usaron realmente
- `X-Fallback-Used`: si hubo sustitución automática

---

## 📋 Checklist Final

- [ ] PDF nativo: `text:fast` funciona ✓
- [ ] PDF nativo: `text:docling` funciona (o muestra "no disponible") ✓
- [ ] PDF escaneado: `ocr:tesseract` funciona ✓
- [ ] PDF escaneado: `text:fast` auto-fallback a OCR ✓
- [ ] Docling en dropdown: visible + instalación clara ✓
- [ ] Errores: mensajes claros, no "[object Object]" ✓
- [ ] Readiness banner: permite descargar modelos ✓
- [ ] Métodos no-instalados: deshabilitados en dropdown ✓

---

## 🐛 Si Algo Falla

1. **Error de importación:** 
   ```bash
   pip install -r requirements.txt
   ```

2. **Docling no descarga:**
   ```bash
   python3 -c "from docling.document_converter import DocumentConverter; DocumentConverter()"
   ```

3. **OCR falla:**
   ```bash
   tesseract --version
   # Si no existe: brew install tesseract
   ```

4. **Ver logs del servidor:**
   Arranca con flag verbose:
   ```bash
   python3 -m pdf_extractor serve --log-level DEBUG
   ```

---

## 💡 Tips

- Los PDFs en `/docs/raw_pdf/` son reales (documentación institucional)
- Algunos son escaneados, otros nativos — es ideal para probar
- El dropdown muestra estrategias en grupos lógicos + "Otras estrategias disponibles"
- Auto-warmup es on-demand: solo descarga si el usuario lo selecciona
