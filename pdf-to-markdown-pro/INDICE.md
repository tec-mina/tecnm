# 📑 Índice de Documentación

## 🚀 Inicio Rápido (Elige tu camino)

### ⚡ 2 Minutos: "Quiero empezar YA"
1. Lee: [`START.md`](./START.md) (este archivo)
2. Instala: `pip install -r requirements.txt`
3. Prueba: `python scripts/pdf_to_md.py documento.pdf -o documento.md`

### 📖 5 Minutos: "Quiero entender qué es esto"
1. Lee: [`SKILL.md`](./SKILL.md) - Especificación oficial

### 📚 15 Minutos: "Quiero aprender a fondo"
1. Lee: [`README.md`](./README.md) - Guía completa
2. Lee: [`reference/LIBRERIAS.md`](./reference/LIBRERIAS.md) - Por qué cada librería
3. Lee: [`reference/GUIA_USO.md`](./reference/GUIA_USO.md) - Casos avanzados

### ✅ 5 Minutos: "Quiero verificar el estado"
- Lee: [`VERIFICACION.md`](./VERIFICACION.md) - Checklist de implementación

---

## 📋 Documentos por Tipo

### 📌 PUNTO DE ENTRADA
| Documento | Tiempo | Para Quién |
|-----------|--------|-----------|
| **START.md** | 2 min | Todos - Comienza aquí |
| **INDICE.md** | 1 min | Este archivo - Navegación |

### 🎯 ESPECIFICACIÓN OFICIAL
| Documento | Tiempo | Contenido |
|-----------|--------|----------|
| **SKILL.md** | 5 min | Qué es, para qué, características, parámetros |

### 📖 GUÍAS DE USO
| Documento | Tiempo | Contenido |
|-----------|--------|----------|
| **README.md** | 10 min | Instalación, ejemplos básicos, FAQ |
| **reference/GUIA_USO.md** | 15 min | Casos avanzados, ejemplos complejos |

### 🔬 DOCUMENTACIÓN TÉCNICA
| Documento | Tiempo | Contenido |
|-----------|--------|----------|
| **reference/LIBRERIAS.md** | 10 min | Por qué cada librería, análisis técnico |

### ✅ ESTADO Y VERIFICACIÓN
| Documento | Tiempo | Contenido |
|-----------|--------|----------|
| **VERIFICACION.md** | 5 min | Checklist, características implementadas |
| **RESUMEN_FINAL.md** | 5 min | Resumen ejecutivo, cambios realizados |

### 💻 CÓDIGO
| Archivo | Líneas | Propósito |
|---------|--------|----------|
| **scripts/extractor.py** | 393 | Extractor robusto con progress bar |
| **scripts/pdf_to_md.py** | 380+ | Conversor con validación y corrección |

### 📦 CONFIGURACIÓN
| Archivo | Contenido |
|---------|----------|
| **requirements.txt** | Dependencias pip |
| **LICENSE** | Licencia MIT |

---

## 🎯 Búsqueda Temática

### "¿Cómo instalo?"
→ Ve a: [`START.md`](./START.md) - Paso 1: Instalación

### "¿Cómo uso desde línea de comandos?"
→ Ve a: [`START.md`](./START.md) - Paso 2: Primer Uso

### "¿Cómo uso desde Python?"
→ Ve a: [`START.md`](./START.md) - Paso 4: Uso desde Python  
→ O: [`reference/GUIA_USO.md`](./reference/GUIA_USO.md) - Scripts avanzados

### "¿Qué librerías se usan y por qué?"
→ Ve a: [`reference/LIBRERIAS.md`](./reference/LIBRERIAS.md) - Análisis de cada una

### "¿Cuáles son todas las opciones CLI?"
→ Ve a: [`README.md`](./README.md) - Sección Parámetros

### "¿Cómo extraigo solo las tablas?"
→ Ve a: [`reference/GUIA_USO.md`](./reference/GUIA_USO.md) - Acceso a Tablas

### "¿Cómo proceso múltiples PDFs?"
→ Ve a: [`reference/GUIA_USO.md`](./reference/GUIA_USO.md) - Procesamiento por Lotes

### "¿Qué significa la puntuación de calidad?"
→ Ve a: [`README.md`](./README.md) - Sección Puntuación de Calidad

### "¿Qué problema tengo?"
→ Ve a: [`README.md`](./README.md) - Sección Solución de Problemas

### "¿Qué mejoras tiene vs. las versiones anteriores?"
→ Ve a: [`RESUMEN_FINAL.md`](./RESUMEN_FINAL.md) - Mejoras vs. Versiones Anteriores

---

## 🔍 Flujo Recomendado de Lectura

```
INDICE.md (tú estás aquí)
    ↓
START.md (¡Comienza aquí! 2 minutos)
    ↓
¿Quieres más detalles?
    ├→ Sí: SKILL.md (5 min)
    │     ↓
    │   README.md (10 min)
    │     ↓
    │   reference/GUIA_USO.md (15 min)
    │
    └→ No: ¡Ya estás listo para usar!
           python scripts/pdf_to_md.py documento.pdf -o documento.md
```

---

## 📊 Resumen de Contenidos

### Documentación de Usuario
- **START.md** - Guía de inicio rápido (2 min)
- **README.md** - Guía completa (10 min)
- **reference/GUIA_USO.md** - Ejemplos avanzados (15 min)

### Documentación Técnica
- **SKILL.md** - Especificación oficial (5 min)
- **reference/LIBRERIAS.md** - Análisis técnico (10 min)

### Verificación y Resumen
- **VERIFICACION.md** - Checklist de implementación (5 min)
- **RESUMEN_FINAL.md** - Resumen ejecutivo (5 min)

### Código
- **scripts/extractor.py** - Extractor robusto
- **scripts/pdf_to_md.py** - Conversor completo

---

## 🎯 Guía Rápida de Referencia

### Instalación
```bash
pip install -r requirements.txt
```

### Uso básico
```bash
python scripts/pdf_to_md.py documento.pdf -o documento.md
```

### Uso avanzado
```bash
python scripts/pdf_to_md.py documento.pdf -o documento.md --lang es --verify --fix --json
```

### Desde Python
```python
from scripts.pdf_to_md import PDFToMarkdown
converter = PDFToMarkdown()
result = converter.process('documento.pdf', output='documento.md')
```

---

## ✅ Checklist de Setup

- [ ] Leíste START.md
- [ ] Instalaste: `pip install -r requirements.txt`
- [ ] Probaste: `python scripts/pdf_to_md.py documento.pdf -o documento.md`
- [ ] Leíste SKILL.md (opcional pero recomendado)
- [ ] ¡Listo para producción!

---

## 📞 Necesitas Ayuda?

1. **¿Estoy en el sitio correcto?** → START.md
2. **¿Cómo instalo?** → START.md, Paso 1
3. **¿Cómo uso?** → START.md, Paso 2
4. **¿Qué problema tengo?** → README.md, Solución de Problemas
5. **¿Cómo hago algo avanzado?** → reference/GUIA_USO.md

---

## 🎓 Propósito de Cada Documento

| Documento | Propósito |
|-----------|----------|
| INDICE.md | Navigación (tú estás aquí) |
| START.md | Inicio rápido (comienza aquí) |
| SKILL.md | Especificación oficial |
| README.md | Guía completa de usuario |
| reference/LIBRERIAS.md | Análisis técnico |
| reference/GUIA_USO.md | Ejemplos y casos avanzados |
| VERIFICACION.md | Checklist de implementación |
| RESUMEN_FINAL.md | Resumen ejecutivo |

---

**¿Listo? → Comienza con [`START.md`](./START.md)** 🚀
