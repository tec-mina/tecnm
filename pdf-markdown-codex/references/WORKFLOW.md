# Workflow

## Flujo operativo

1. Confirmar objetivo:
- solo extraer;
- extraer y verificar;
- extraer, verificar y aplicar safe fixes.

2. Elegir backend principal:
- rapido: PyMuPDF + pymupdf4llm
- preciso: Docling

3. Elegir backend auxiliar de tablas si hace falta:
- `pdfplumber`: buena opcion general
- `camelot`: util en tablas estructuradas, especialmente tipo lattice/stream

4. Ejecutar quality gate:
- `PASS`
- `ISSUES_FOUND`
- `BLOCKED_MISSING_CONTEXT`

5. Aplicar safe fixes solo si:
- no cambian significado;
- no inventan contenido;
- corrigen problemas mecanicos claros.

## Reglas de decision

- Si importa velocidad y el PDF es normal: usa modo rapido.
- Si importan tablas complejas: usa `--docling`.
- Si aun hay dudas con tablas: agrega backend auxiliar de tablas.
- Si el PDF es escaneado y la salida sale pobre: no fuerces un resultado; reporta necesidad de OCR.

## Lo que no se debe hacer

- No inventar tablas o texto.
- No cambiar cifras, nombres o tono institucional.
- No asumir que un backend secundario siempre mejora al principal.
- No cerrar como `PASS` si el Markdown sale vacio o materialmente incompleto.
