# Libraries

## Base recomendada

Estas son las librerias base del skill:

- `pymupdf`
  Apertura de PDF, conteo de paginas e imagenes.

- `pymupdf4llm`
  Extraccion rapida de PDF a Markdown.

- `pdfplumber`
  Backend auxiliar de tablas y estructuras.

- `pdfminer.six`
  Util para contrastes de texto cuando haga falta.

- `pypdf`
  Utilidad general sobre PDFs.

- `pillow`
  Manejo de imagenes.

- `tabulate`
  Renderizado limpio de tablas a Markdown.

- `python-dateutil`
  Fechas y metadata.

- `chardet`
  Apoyo en deteccion de codificacion cuando aparezcan archivos problemáticos.

## Extras opcionales

- `docling`, `docling-core`, `huggingface_hub`
  Mejor precision en tablas dificiles y documentos complejos.

- `camelot-py`, `opencv-python`
  Backend alterno para tablas. Puede requerir dependencias de sistema.

- `img2table`, `rapidocr-onnxruntime`, `pytesseract`, `pdf2image`, `pypdfium2`
  Ruta opcional para OCR o tablas en documentos mas complejos o escaneados.

## Dependencias de sistema

Algunas rutas opcionales pueden requerir:

- Java para `tabula-py` si en el futuro se agrega
- Ghostscript para ciertas instalaciones de Camelot
- Tesseract para `pytesseract`
- Poppler para `pdf2image`

## Criterio de uso

- No toda libreria listada debe activarse en cada corrida.
- La skill debe usar primero la ruta mas confiable y simple.
- Los extras se justifican cuando mejoran un caso real, no por moda.
