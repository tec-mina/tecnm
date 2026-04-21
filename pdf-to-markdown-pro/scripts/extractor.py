#!/usr/bin/env python3
"""
Extractor robusto - PDF a Markdown con jerarquía inteligente de librerías
NIVEL 1: Docling > MarkItDown
NIVEL 2: PyMuPDF + pdfplumber (fallback)
"""

import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Logger minimalista
import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


@dataclass
class ExtractionMetadata:
    """Metadatos de extracción"""
    source_file: str
    total_pages: int
    file_size_mb: float
    extraction_date: str
    extraction_time_sec: float
    language: str = "unknown"
    tables_count: int = 0
    images_count: int = 0
    errors: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class PDFExtractor:
    """Extrae PDF con jerarquía: Docling → MarkItDown → Híbrido (PyMuPDF+pdfplumber)"""

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.logger = logger if verbose else logging.getLogger('null')

    def extract(self, pdf_path: str, lang: str = 'auto') -> Dict[str, Any]:
        """Extrae PDF usando jerarquía inteligente"""
        start_time = time.time()

        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF no encontrado: {pdf_path}")

        file_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
        self._log(f"\n📄 Procesando: {Path(pdf_path).name} ({file_size_mb:.1f} MB)")

        # NIVEL 1: Intenta Docling
        try:
            self._log("🔍 [1/3] Intentando Docling...")
            from docling.document_converter import DocumentConverter
            from docling.datamodel.base_models import ConversionStatus

            converter = DocumentConverter()
            result = converter.convert(pdf_path)

            if result.status == ConversionStatus.SUCCESS:
                markdown = result.document.export_to_markdown()
                self._log("✅ Extracción con Docling exitosa")

                metadata = ExtractionMetadata(
                    source_file=Path(pdf_path).name,
                    total_pages=len(result.document.pages) if hasattr(result.document, 'pages') else 1,
                    file_size_mb=file_size_mb,
                    extraction_date=datetime.now().isoformat(),
                    extraction_time_sec=time.time() - start_time,
                    language=lang
                )

                return {
                    'markdown': markdown,
                    'metadata': metadata.__dict__,
                    'tables': [],
                    'images': [],
                    'raw_text': markdown
                }
        except Exception as e:
            self._log(f"⚠ Docling no disponible: {str(e)[:50]}")

        # NIVEL 1: Intenta MarkItDown
        try:
            self._log("🔍 [2/3] Intentando MarkItDown...")
            import markitdown

            with open(pdf_path, 'rb') as f:
                markdown = markitdown.markitdown(f)

            if markdown and len(markdown) > 100:
                self._log("✅ Extracción con MarkItDown exitosa")

                metadata = ExtractionMetadata(
                    source_file=Path(pdf_path).name,
                    total_pages=1,
                    file_size_mb=file_size_mb,
                    extraction_date=datetime.now().isoformat(),
                    extraction_time_sec=time.time() - start_time,
                    language=lang
                )

                return {
                    'markdown': markdown,
                    'metadata': metadata.__dict__,
                    'tables': [],
                    'images': [],
                    'raw_text': markdown
                }
        except Exception as e:
            self._log(f"⚠ MarkItDown no disponible: {str(e)[:50]}")

        # NIVEL 2: Estrategia Híbrida (PyMuPDF + pdfplumber)
        self._log("🔍 [3/3] Usando estrategia híbrida (PyMuPDF + pdfplumber)...")
        try:
            import fitz
            import pdfplumber
            from tabulate import tabulate

            # Abre con PyMuPDF
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            self._log(f"📖 Total de páginas: {total_pages}")

            all_text = []
            all_tables = []

            # Extrae con pdfplumber (mejor para tablas)
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        # Extrae texto
                        page_text = page.extract_text()
                        if page_text:
                            all_text.append(page_text)

                        # Extrae tablas
                        tables = page.extract_tables()
                        if tables:
                            for table in tables:
                                md_table = tabulate(table, headers='firstrow', tablefmt='github')
                                all_tables.append({
                                    'page': page_num,
                                    'markdown': md_table
                                })
                    except Exception as e:
                        self._log(f"⚠ Error en página {page_num}: {str(e)[:50]}")

            # Combina contenido
            markdown_parts = all_text.copy()
            if all_tables:
                markdown_parts.append("\n## Tablas\n")
                for table in all_tables:
                    markdown_parts.append(f"### Tabla (página {table['page']})\n{table['markdown']}\n")

            markdown = '\n\n'.join(markdown_parts)
            self._log(f"✅ Extracción híbrida completada ({len(markdown)} caracteres)")

            metadata = ExtractionMetadata(
                source_file=Path(pdf_path).name,
                total_pages=total_pages,
                file_size_mb=file_size_mb,
                extraction_date=datetime.now().isoformat(),
                extraction_time_sec=time.time() - start_time,
                language=lang,
                tables_count=len(all_tables)
            )

            return {
                'markdown': markdown,
                'metadata': metadata.__dict__,
                'tables': all_tables,
                'images': [],
                'raw_text': markdown
            }

        except Exception as e:
            self._log(f"❌ Error en extracción híbrida: {e}")
            # Fallback: retorna metadatos vacíos pero válidos
            metadata = ExtractionMetadata(
                source_file=Path(pdf_path).name,
                total_pages=1,
                file_size_mb=file_size_mb,
                extraction_date=datetime.now().isoformat(),
                extraction_time_sec=time.time() - start_time,
                language=lang,
                errors=[str(e)]
            )
            return {
                'markdown': f"# {Path(pdf_path).stem}\n\n*Contenido no extraído - revisar dependencias*\n\n**Error**: {str(e)[:100]}",
                'metadata': metadata.__dict__,
                'tables': [],
                'images': [],
                'raw_text': ""
            }

    def _log(self, msg: str):
        """Log controlado"""
        if self.verbose:
            self.logger.info(msg)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Extrae PDF a Markdown')
    parser.add_argument('pdf', help='Archivo PDF')
    parser.add_argument('-o', '--output', help='Archivo de salida')
    parser.add_argument('--lang', default='auto', help='Idioma')
    parser.add_argument('--quiet', action='store_true', help='Sin progreso')

    args = parser.parse_args()

    try:
        extractor = PDFExtractor(verbose=not args.quiet)
        result = extractor.extract(args.pdf, args.lang)

        if args.output:
            Path(args.output).write_text(result['markdown'], encoding='utf-8')
            print(f"✅ Guardado: {args.output}")
        else:
            print(result['markdown'])

        meta = result['metadata']
        print(f"\n📊 Resumen:")
        print(f"  Páginas: {meta['total_pages']}")
        print(f"  Tiempo: {meta['extraction_time_sec']:.1f}s")
        print(f"  Tablas: {meta['tables_count']}")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
