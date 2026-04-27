# 📚 Documentación del Proyecto TecNM - Extracción de PDFs

> Organización centralizada de toda la documentación del proyecto

---

## 🎯 Índice Principal

### 📖 Guías de Inicio Rápido
- **[START_HERE.md](../START_HERE.md)** - Punto de entrada (2 min)
- **[README_PDF_EXTRACTOR.md](../README_PDF_EXTRACTOR.md)** - Guía de uso (5 min)

### 📚 Documentación Técnica
- **[MARKDOWN_STRUCTURE_GUIDE.md](../MARKDOWN_STRUCTURE_GUIDE.md)** - Cómo estructurar Markdown
- **[MULTI_METHOD_EXTRACTION_STRATEGY.md](../MULTI_METHOD_EXTRACTION_STRATEGY.md)** - Estrategia técnica
- **[QUICK_START_IMPLEMENTATION.md](../QUICK_START_IMPLEMENTATION.md)** - 4 opciones de implementación

### 📊 Reportes y Resultados
- **[EXTRACTION_REPORT.md](../EXTRACTION_REPORT.md)** - Resultados de tests (4/5 exitosos)
- **[IMPLEMENTATION_ROADMAP.md](../IMPLEMENTATION_ROADMAP.md)** - Próximos pasos y mejoras

### 📦 Información del Proyecto
- **[DELIVERABLES.md](../DELIVERABLES.md)** - Inventario completo de entregables
- **[CONTEXT.md](../CONTEXT.md)** - Memoria canónica del proyecto

---

## 🔧 Estructura de Carpetas

```
proyecto/
├── docs/                           # ← Documentación centralizada
│   └── README.md                   # Este archivo (índice)
│
├── [Guías principales]
│   ├── START_HERE.md
│   ├── README_PDF_EXTRACTOR.md
│   ├── MARKDOWN_STRUCTURE_GUIDE.md
│   └── ... (más guías)
│
├── [Código]
│   ├── pdf_extractor_complete.py   # Script principal
│   ├── analyze_pdfs.py             # Análisis previo
│   └── requirements.txt
│
├── [Aplicación Web]
│   └── pdf-extractor-web/          # NUEVA: App web integrada
│       ├── app.py                  # Flask/FastAPI backend
│       ├── templates/
│       ├── static/
│       └── requirements.txt
│
└── [Datos]
    ├── docs/raw_pdf/               # PDFs a procesar
    ├── output/                     # Markdown generados
    └── pdf_analysis_report.json
```

---

## 🚀 Quick Navigation

### "Quiero..."

| Quiero... | Ir a... | Tiempo |
|-----------|---------|--------|
| Empezar AHORA | [START_HERE.md](../START_HERE.md) | 2 min |
| Usar el script | [README_PDF_EXTRACTOR.md](../README_PDF_EXTRACTOR.md) | 5 min |
| Entender la estrategia | [MULTI_METHOD_EXTRACTION_STRATEGY.md](../MULTI_METHOD_EXTRACTION_STRATEGY.md) | 15 min |
| Ver resultados reales | [EXTRACTION_REPORT.md](../EXTRACTION_REPORT.md) | 10 min |
| Próximos pasos | [IMPLEMENTATION_ROADMAP.md](../IMPLEMENTATION_ROADMAP.md) | 20 min |
| Usar la web app | [Web App README](./web-app/README.md) | 3 min |

---

## 📋 Documentos por Categoría

### Fase 1: Análisis y Diseño
- `MARKDOWN_STRUCTURE_GUIDE.md` - Arquitectura de Markdown
- `BEFORE_AFTER_COMPARISON.md` - Mejoras visuales
- `MULTI_METHOD_EXTRACTION_STRATEGY.md` - Estrategia técnica

### Fase 2: Implementación
- `pdf_extractor_complete.py` - Código principal
- `analyze_pdfs.py` - Análisis previo
- `requirements.txt` - Dependencias

### Fase 3: Validación
- `EXTRACTION_REPORT.md` - Resultados de tests
- `pdf_analysis_report.json` - Análisis en JSON
- `docs/raw_pdf/*_extracted.md` - Ejemplos generados

### Fase 4: Producción
- `IMPLEMENTATION_ROADMAP.md` - Mejoras y roadmap
- `pdf-extractor-web/` - App web integrada
- `DELIVERABLES.md` - Inventario completo

---

## 🆕 App Web Integrada

**NUEVA**: Interfaz web para extraer PDFs sin terminal.

```bash
# Instalar
pip install flask

# Ejecutar
python3 pdf-extractor-web/app.py

# Visitar
http://localhost:5000
```

**Características**:
- ✅ Upload de PDFs
- ✅ Extracción automática
- ✅ Preview de Markdown
- ✅ Descarga de resultados
- ✅ Historial de extracciones

Ver: [Web App README](./web-app/README.md)

---

## 📚 Documentos Heredados (Archivados)

Estos archivos son del proyecto original. Consúltalos solo si necesitas contexto histórico:

- `CONTEXT.md` - Memoria canónica (LEER PRIMERO)
- `PHASE2.1_GETTING_STARTED.md` - Fase anterior
- `PHASE2.2_GETTING_STARTED.md` - Fase anterior
- `SESSION_SUMMARY_*.md` - Resúmenes de sesiones
- `ML_AI_AUDIT.md` - Auditoría previa
- `COMPREHENSIVE_AUDIT_ALL_METHODS.md` - Auditoría completa
- `CHANGES_OCR_RESILIENCE.md` - Cambios previos
- `CAMBIOS_REALIZADOS.md` - Cambios previos
- `DOCKER_BUILD.md` - Configuración Docker
- `AGENTS.md` - Configuración de agentes
- `CODEX.md` - Codex del proyecto
- `TEST_MANUAL.md` - Tests manuales previos
- `run.md` - Instrucciones de ejecución previas

---

## ✨ Convención de Este Proyecto

Seguimos las reglas de `CONTEXT.md`:

1. **Verdad sobre fluidez** - Si no sabemos, lo decimos
2. **Desacuerdo útil** - Cuestionamos supuestos débiles
3. **Evidencia antes de conclusión** - Todo debe estar verificado
4. **Separar hechos de inferencias** - Claro y explícito
5. **Alta señal en memoria** - Solo lo reutilizable

---

## 📞 Dónde Encontrar Qué

| Pregunta | Consulta... |
|----------|-------------|
| ¿Cómo empiezo? | [START_HERE.md](../START_HERE.md) |
| ¿Cómo uso el script? | [README_PDF_EXTRACTOR.md](../README_PDF_EXTRACTOR.md) |
| ¿Cómo es un Markdown bueno? | [MARKDOWN_STRUCTURE_GUIDE.md](../MARKDOWN_STRUCTURE_GUIDE.md) |
| ¿Qué métodos hay? | [MULTI_METHOD_EXTRACTION_STRATEGY.md](../MULTI_METHOD_EXTRACTION_STRATEGY.md) |
| ¿Qué resultados obtuviste? | [EXTRACTION_REPORT.md](../EXTRACTION_REPORT.md) |
| ¿Qué sigue? | [IMPLEMENTATION_ROADMAP.md](../IMPLEMENTATION_ROADMAP.md) |
| ¿Qué entregaste? | [DELIVERABLES.md](../DELIVERABLES.md) |
| ¿Contexto del proyecto? | [CONTEXT.md](../CONTEXT.md) |
| ¿Usar la app web? | [Web App](../pdf-extractor-web/README.md) |

---

## 🎯 Estado del Proyecto

| Componente | Status | Notas |
|-----------|--------|-------|
| Extracción Script | ✅ Completado | 683 líneas, 3 métodos |
| Documentación | ✅ Completado | 17,458 líneas, 9 guías |
| Tests | ✅ Completado | 5 PDFs, 80% éxito |
| App Web | 🆕 NUEVA | Interfaz integrada |
| OCR (opcional) | ⏳ Pendiente | `pip install paddleocr` |
| Claude Vision | 🔮 Futuro | Fallback opcional |

---

## 🚀 Próximos Pasos

1. **Hoy** - Instala y prueba: `pip install pdfplumber && python3 pdf_extractor_complete.py "tu_pdf.pdf"`
2. **Mañana** - Prueba la app web: `python3 pdf-extractor-web/app.py`
3. **Esta semana** - Instala OCR: `pip install paddleocr`
4. **Próximas semanas** - Mejoras opcionales (Ver roadmap)

---

**Última actualización**: 2026-04-26  
**Documentos**: 9 guías + app web  
**Estado**: ✅ Operativo
