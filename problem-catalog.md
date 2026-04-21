# Catálogo de problemas en .md extraídos de PDFs

Guía de referencia con ejemplos concretos de cada tipo de problema, cómo detectarlo y cómo corregirlo. Consulta este archivo cuando necesites más detalle del que hay en el SKILL.md principal.

---

## 1. Problemas de separación de páginas

### 1.1 Números de página incrustados en el texto

El patrón más común y más dañino porque rompe oraciones.

**Ejemplo dañado:**
```
...el presupuesto asignado al capítulo 1000 servicios personales 12
corresponde a un 65% del total anual para el ejercicio fiscal 2026...
```

El "12" en medio era el número de página 12. El texto real debería ser:
```
...el presupuesto asignado al capítulo 1000 servicios personales corresponde a un 65% del total anual para el ejercicio fiscal 2026...
```

**Cómo detectarlo:**
- Números de 1-3 dígitos aislados en medio de texto, sin contexto que los justifique
- Secuencia creciente a lo largo del documento (4, 5, 6...) que coincide con paginación
- Si tienes el PDF, compara: el número huérfano coincide con el número de página real

**Cómo corregirlo:**
- Elimina el número del flujo de texto
- Inserta el marcador de página antes del siguiente bloque significativo:
  ```
  
  ---
  
  <!-- Página 12 -->
  
  ```

### 1.2 Ausencia total de marcadores de página

El `.md` es un muro continuo. El PDF tenía 80 páginas pero el `.md` no tiene ninguna indicación.

**Cómo detectarlo:**
- El PDF está disponible, tiene N páginas, y en el `.md` no aparece ni una sola referencia a páginas
- Impacto: buscar "esto estaba en la página 15" es imposible

**Cómo corregirlo (solo con PDF):**
- Reconstruye los límites de página comparando bloques de texto del PDF con el `.md`
- Inserta marcadores cada vez que cruzas un límite real
- Si no tienes PDF, no inventes límites arbitrarios — reporta el problema y ya

### 1.3 Encabezados y pies de página repetidos

Extractores ingenuos copian el encabezado/pie en cada página. Si cada página tenía "Manual de Procedimientos TecNM — 2026" arriba, acabas con esa frase 80 veces en el `.md`.

**Cómo detectarlo:**
- Buscar frases idénticas que se repiten 5+ veces en el documento
- Típicamente incluyen: nombre del documento, fecha, número de página, "SEP - TecNM", logos textualizados

**Cómo corregirlo:**
- Elimina todas las repeticiones del cuerpo
- Opcional: menciónalo una vez al inicio del `.md` como metadato:
  ```
  <!-- Encabezado original: "Manual de Procedimientos TecNM — Edición 2026" -->
  <!-- Pie original: "Subdirección de Planeación — Página N" -->
  ```

### 1.4 Salto de página en medio de oración

Cuando la oración del PDF cruza dos páginas físicas, algunos extractores insertan dobles saltos de línea donde no corresponden.

**Ejemplo dañado:**
```
...la asignación presupuestal corresponde al ejercicio fiscal

2026 y deberá ser comprobada dentro de los primeros 30 días...
```

**Cómo corregirlo:**
- Si la línea anterior no termina en puntuación final (`.`, `:`, `?`, `!`) y la siguiente no empieza con mayúscula de inicio de sección, únelas.

---

## 2. Problemas de formato legible

### 2.1 Muros de texto sin saltos

Todo el documento es un solo párrafo gigante. Imposible de leer, peor aún de usar como contexto.

**Cómo corregirlo:**
- Inserta salto de párrafo cuando detectes:
  - Cambio de tema (nuevo concepto, nueva cláusula)
  - Inicio con conector fuerte ("Asimismo,", "Por lo anterior,", "En virtud de,")
  - Números de artículo, fracción o inciso
  - Encabezados que quedaron planos

### 2.2 Saltos duros en medio de oraciones

El opuesto del anterior: PDFs de dos columnas extraídos mal, o con anchos fijos, rompen cada línea del PDF en una línea del `.md`.

**Ejemplo dañado:**
```
El jefe de planeación, programación
y presupuestación del instituto
tecnológico deberá presentar ante
la subdirección académica un
informe trimestral de avance.
```

**Cómo corregirlo:**
- Une líneas consecutivas salvo que la línea anterior termine en puntuación final o sea claramente un item de lista/encabezado
- Resultado:
  ```
  El jefe de planeación, programación y presupuestación del instituto tecnológico deberá presentar ante la subdirección académica un informe trimestral de avance.
  ```

### 2.3 Jerarquía de títulos perdida

Todos los "títulos" quedaron como texto normal o todos como `#`. No se distingue un capítulo de una sección.

**Cómo corregirlo:**
- Usa pistas del documento original:
  - Texto todo en MAYÚSCULAS y corto (< 80 caracteres) → probablemente H1 o H2
  - Texto con numeración tipo "1.", "1.1", "1.1.1" → niveles H2, H3, H4 respectivamente
  - "ARTÍCULO PRIMERO", "CAPÍTULO I", etc. → H2 o H3 según contexto
  - Usa el PDF si está: los tamaños de fuente y estilos te dan pistas directas

- Solo debe haber un `#` H1 — el título del documento.

### 2.4 Listas aplanadas

Lo que era una lista con viñetas en el PDF quedó como texto corrido con guiones o bullets raros mezclados.

**Ejemplo dañado:**
```
Los requisitos son:  servicios personales vigentes,  materiales de oficina,  equipo de cómputo funcional,  mobiliario adecuado.
```

**Cómo corregirlo:**
```
Los requisitos son:

- Servicios personales vigentes
- Materiales de oficina
- Equipo de cómputo funcional
- Mobiliario adecuado
```

### 2.5 Ligaduras y caracteres de control

Los PDFs usan ligaduras tipográficas que muchos extractores no desarman.

| Ligadura | Corregido |
|----------|-----------|
| `ﬁ` | `fi` |
| `ﬂ` | `fl` |
| `ﬀ` | `ff` |
| `ﬃ` | `ffi` |
| `ﬄ` | `ffl` |
| `ﬆ` | `st` |

Además elimina:
- `\x0c` (form feed, salto de página interno)
- `\x00`-`\x08` y otros caracteres de control no imprimibles
- Espacios no-break `\xa0` (conviértelos a espacio normal)

---

## 3. Problemas de tablas

### 3.1 Tabla aplanada en líneas sueltas

**Ejemplo dañado:**
```
Concepto
Monto
Porcentaje
Servicios personales
12,450,000
65%
Materiales
1,200,000
6%
```

**Corregido:**
```markdown
| Concepto | Monto | Porcentaje |
|----------|------:|-----------:|
| Servicios personales | 12,450,000 | 65% |
| Materiales | 1,200,000 | 6% |
```

Para reconstruir necesitas saber cuántas columnas eran. Si tienes el PDF, véla directamente. Si no, cuenta el patrón: si los valores se repiten en grupos de N, son N columnas.

### 3.2 Tabla con espacios fijos (PDF de ancho fijo)

```
Concepto                    Monto           Porcentaje
Servicios personales        12,450,000      65%
Materiales                  1,200,000       6%
```

**Corregido:** Igual que arriba, convertir a markdown estándar.

### 3.3 Tabla markdown con columnas desalineadas

A veces el extractor intenta hacer markdown pero sale mal:

```
| Concepto | Monto | Porcentaje
|----------|
| Servicios personales | 12,450,000 | 65%
```

**Cómo corregirlo:**
- Verifica que todas las filas tengan el mismo número de `|`
- El separador (`|---|`) debe tener tantas columnas como el encabezado
- Alinea números: `---:` a la derecha, texto: `---` izquierda

### 3.4 Tabla demasiado dañada

Si la tabla se extrajo tan mal que no puedes reconstruirla con seguridad, marca la sección:

```markdown
<!-- TABLA REQUIERE REVISIÓN MANUAL — ver PDF página N -->

[Texto crudo extraído aquí tal cual, sin tocar]
```

Mejor preservar el texto original y marcar el problema que inventar datos.

---

## 4. Problemas de imágenes faltantes

Este bloque SOLO aplica cuando tienes el PDF disponible para comparar.

### 4.1 Cómo detectar imágenes faltantes

Dos estrategias complementarias:

1. **Visual:** Abre el PDF con una herramienta de rendering (pdfplumber, pdf2image) y revisa cada página. Si ves un elemento visual (logo, diagrama, gráfica, firma) que no tiene equivalente en el `.md`, es faltante.

2. **Estructural:** Busca huecos en el flujo del `.md`. Si una página del PDF tiene poco texto porque estaba ocupada por una gráfica, el `.md` va a "saltar" entre conceptos en esa zona.

### 4.2 Tipos de elementos visuales comunes en documentos TecNM

- **Logotipos institucionales:** TecNM, escudo nacional, logo del instituto tecnológico específico
- **Organigramas:** estructura de la institución, dependencias jerárquicas
- **Diagramas de flujo:** procesos administrativos, flujos de autorización de presupuesto
- **Gráficas:** distribución presupuestal por capítulo, comparativos anuales, indicadores
- **Firmas y sellos:** al final de oficios, actas, convenios
- **Membretes:** encabezados institucionales formales
- **Fotografías:** en informes de evaluación, reportes de obra

### 4.3 Placeholder estándar

```markdown
> **[IMAGEN FALTANTE]**
> **Título:** [lo que dice el pie de imagen, si tiene]
> **Concepto:** [descripción de qué hay en la imagen]
> **Ubicación original:** Página N del PDF
```

El campo **Concepto** es el más importante. Si la imagen es un organigrama, describe la estructura: "Jerarquía de 4 niveles: Dirección > 3 subdirecciones > 8 jefaturas de departamento > áreas operativas". Si es una gráfica: "Gráfica de barras mostrando distribución del presupuesto 2026: servicios personales 65%, materiales 6%, servicios generales 18%, inversión 11%".

Esto hace que aunque la imagen no esté, el LLM que consuma el contexto entienda qué información contenía.

### 4.4 Firmas y sellos en oficios/actas

Estos casos merecen mención explícita porque son evidencia de oficialidad del documento:

```markdown
> **[FIRMA/SELLO FALTANTE]**
> **Ubicación:** Final del oficio, página N
> **Contenido:** Firma del Ing. [nombre], Director del Instituto Tecnológico de Minatitlán. Sello oficial del TecNM.
```

Si no puedes leer el nombre con claridad del PDF, usa `[nombre ilegible]` en lugar de inventar.
