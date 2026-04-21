# Procesamiento PDF → Markdown

## Estado: ✅ COMPLETADO

**Fecha:** 2026-04-21  
**Usuario:** Kevin Molina (TecNM - Jefe de Planeación, Programación y Presupuestación)

---

## 📊 Resumen

| Métrica | Valor |
|---------|-------|
| **PDFs Originales** | 80 |
| **Markdown Generados** | 80 |
| **Tamaño Original** | 172.3 MB |
| **Tamaño Procesado** | 3.0 MB |
| **Tasa Compresión** | 98.3% |
| **Estrategia** | pdf-to-markdown-pro (batch mode) |

---

## 📁 Estructura de Directorios

```
/docs
├── raw/                      # PDFs originales sin procesar
│   ├── 10-reglamento_*.pdf
│   ├── 11-ly_iva.pdf
│   ├── ... (80 archivos)
│   └── REGLAMENTO_NO_DOCENTE.pdf
│
└── processed/                # Markdown procesados
    ├── README.md             # Este archivo
    ├── INDEX.md              # Índice completo
    ├── STATS.json            # Estadísticas del procesamiento
    ├── 10-reglamento_*.md
    ├── 11-ly_iva.md
    └── ... (80 archivos markdown)
```

---

## 📋 Archivos Documentales Procesados

### Legislación Fiscal
- `10-reglamento_codigo_fiscal_federacion.pdf` → Regulaciones del código fiscal
- `11-ly_iva.pdf` → Ley de IVA
- `12-reglamento_impuesto_valor_agregado.pdf` → Reglamento IVA
- `13-ley_impuesto_sobre_la_renta.pdf` → Ley de ISR
- `14-reglamento_impuesto_sobre_renta.pdf` → Reglamento ISR

### Marco Institucional TecNM
- `15-DC-TecNM.pdf` → Decreto de Creación
- `22-MO-TecNM.pdf` → Manual de Organización
- `64-decreto_tecnologico_nacional_mexico.pdf` → Decreto del Tecnológico Nacional

### Normativa Laboral
- `20-ley_federal_trabajo.pdf` → Ley Federal del Trabajo
- `27-Reglamento_de_las_Condiciones_*.pdf` → Condiciones de Trabajo SEP
- `REGLAMENTO_INT_DE_TRABAJO_DEL_PERSONAL_DOCENTE-1.pdf` → Reglamento Docente
- `REGLAMENTO_NO_DOCENTE.pdf` → Reglamento Personal No Docente

### Manuales de Usuarios IT
- `37-Manual-de-Usuario_IT_Centros_PTA_2023.pdf`
- `39-Manual de Usuario_IT_Centros_Viáticos.pdf`
- `44-Manual de Usuario_IT_Centros_Elaboración_de_Requisiciones.pdf`
- `47-Manual_de_Usuario_IT_Centros_POA.pdf` (12.2 MB)
- `55-Manual de Usuario_IT_Centros_Capítulo_1000.pdf`
- `56-Manual de Usuario_IT_Centros_Procedimiento_Partidas_de_Mantenimiento.pdf`
- `70-Manual de Usuario_IT_Centros_Proveedores.pdf`

### Presupuesto y Financiero
- `PEF_2026.pdf` → Presupuesto de Egresos de la Federación 2026
- `FAM_2024_ASIGNACIÓN.pdf` → Asignaciones 2024
- `FAM_2025_ASIGNACIÓN.pdf` → Asignaciones 2025
- `61-Formato_Adecuación_al_Presupuesto_de_Ingresos_Propios.pdf`

### Clasificadores
- `48-Clasificador_por_Objeto_del_Gasto_*.pdf` (duplicados)
- `81-77-Guía_Módulo_Otros_Ingresos_SISAD_V3.pdf`

### Consideraciones POA (Planes Operativos Anuales)
- `54-Consideraciones_POA_2022.pdf`
- `73-Consideraciones_Adecuación_POA_2023.pdf`
- `75-Consideraciones_Adecuación_POA_2024_*.pdf`
- `78-Consideraciones_al_POA_2025_*.pdf`
- `82-Consideraciones_al_POA_2026.pdf`

### Normativa Estatal
- `2-CPEUM_100715.pdf` → Constitución Política
- `3-ley_planeacion.pdf` → Ley de Planeación
- `4-ley_adquisiciones_*.pdf` → Leyes de Adquisiciones
- `21-ly_gral_edu.pdf` → Ley General de Educación

### Integridad Pública
- `16-codigo_etica_servidores_publicos_apf.pdf`
- `17-ley_federal_responsabilidades_*.pdf`
- `18-ley_federal_responsabilidades_servidores_publicos.pdf`
- `2_Guia_Autoevaluacion_Integridad_Sector_Publico.pdf`

### Otros Documentos
- `19012026-MAT.pdf` → MAT (Matriz de Asignación de Transferencias)
- `2026_01_19_MAT_presrep.pdf` → MAT Presupuestal
- `2026_01_19_MAT_shcp.pdf` → MAT SHCP
- `Manual_de_Procedimientos_del_Tecnológico_Nacional_de_México_2.pdf` (32.2 MB)
- `Manual_de_Usuario_SICOP_2025.pdf`
- `CABM_Enero_2024_pdf.pdf`
- `DOF - Diario Oficial de la Federación.pdf` (x2)
- Circulares varias

---

## 🔧 Procesamiento Utilizado

### Skill: `pdf-to-markdown-pro`
- **Extracción Semántica:** Docling + MarkItDown
- **Fallback Híbrido:** PyMuPDF + pdfplumber + tabulate
- **OCR (Escaneos):** EasyOCR
- **Validación:** Inteligencia automática de calidad

### Características
✅ Extracción de texto preservando estructura  
✅ Tablas con formato Markdown  
✅ Referencias de imágenes  
✅ Metadatos completos  
✅ Normalización de espacios  
✅ Detección de idioma: Español

---

## 📖 Cómo Usar los Archivos

### Lectura Individual
```bash
# Abrir un markdown específico
cat processed/47-Manual_de_Usuario_IT_Centros_POA.md
```

### Búsqueda por Contenido
```bash
# Buscar término en todos los markdown
grep -r "presupuesto" processed/
grep -r "POA" processed/
```

### Indexación
```bash
# Ver el índice completo
cat processed/INDEX.md
```

### Estadísticas
```bash
# Ver estadísticas de procesamiento
cat processed/STATS.json | python3 -m json.tool
```

---

## ⚠️ Notas Importantes

1. **Archivos Grandes:** Los documentos > 5 MB pueden requerir especial atención
   - `Manual_de_Procedimientos_del_Tecnológico_Nacional_de_México_2.pdf` (32.2 MB)
   - `REGLAMENTO_INT_DE_TRABAJO_DEL_PERSONAL_DOCENTE-1.pdf` (28.4 MB)
   - `47-Manual_de_Usuario_IT_Centros_POA.pdf` (12.2 MB)

2. **Duplicados Detectados:**
   - `Clasificador_por_Objeto_del_Gasto_*.pdf` (aparece 3 veces)
   - `DOF - Diario Oficial de la Federación.pdf` (x2)

3. **Documentos Legales:** Todos los documentos legislativos han sido procesados preservando su estructura original

4. **Validación:** Cada archivo markdown contiene:
   - Encabezado con nombre del documento
   - Metadatos del origen (PDF)
   - Contenido estructurado por página/sección
   - Referencias de tablas si las hay

---

## 🎯 Próximos Pasos

1. **Revisión Manual:** Verificar integridad de archivos críticos
2. **Actualización de CONTEXT.md:** Agregar referencias a estos documentos
3. **Indexación en Base de Datos:** Si se requiere búsqueda avanzada
4. **Control de Versiones:** Considerar versionar estos archivos

---

**Generado:** 2026-04-21 01:30:16  
**Sistema:** pdf-to-markdown-pro (batch processing)  
**Responsable:** Kevin Molina - Jefe de Planeación, Programación y Presupuestación  
**Institución:** Tecnológico Nacional de México (TecNM)

