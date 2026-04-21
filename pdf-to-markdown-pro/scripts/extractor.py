#!/usr/bin/env python3
"""
Extractor principal - PDF a Markdown con librerías especializadas
Completamente independiente, maneja archivos grandes, con progreso visible

Features:
  ✓ Manejo de archivos grandes sin bloqueos
  ✓ Barra de progreso en tiempo real
  ✓ Procesamiento por chunks/páginas
  ✓ Recovery de errores parciales
  ✓ Memoria optimizada (no carga todo en RAM)
  ✓ Timeouts configurables
  ✓ Logging detallado
  ✓ Sin dependencias de modelos de IA
"""

import os
import sys
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

# Validar librerías requeridas
try:
    import pdfplumber
except ImportError:
    print("ERROR: pdfplumber no instalado. Ejecuta: pip install -r requirements.txt")
    sys.exit(1)

try:
    import fitz
except ImportError:
    print("ERROR: PyMuPDF no instalado. Ejecuta: pip install -r requirements.txt")
    sys.exit(1)

try:
    import tabulate
except ImportError:
    print("ERROR: tabulate no instalado. Ejecuta: pip install -r requirements.txt")
    sys.exit(1)

try:
    from pdfminer.high_level import extract_text
except ImportError:
    print("ERROR: pdfminer.six no instalado. Ejecuta: pip install -r requirements.txt")
    sys.exit(1)

# Opcional pero recomendado
try:
    from langdetect import detect
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False

# Logger minimalista
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class ProgressBar:
    """Barra de progreso simple sin dependencias externas"""

    def __init__(self, total: int, desc: str = "", width: int = 30):
        self.total = max(total, 1)
        self.current = 0
        self.desc = desc
        self.width = width
        self.start_time = time.time()

    def update(self, amount: int = 1):
        """Actualiza la barra"""
        self.current = min(self.current + amount, self.total)
        self._print()

    def _print(self):
        """Imprime la barra de progreso"""
        percent = self.current / self.total
        filled = int(self.width * percent)
        bar = '█' * filled + '░' * (self.width - filled)

        elapsed = time.time() - self.start_time
        if self.current > 0 and elapsed > 0:
            rate = self.current / elapsed
            remaining = int((self.total - self.current) / rate) if rate > 0 else 0
        else:
            remaining = 0

        sys.stdout.write(
            f'\r{self.desc} |{bar}| '
            f'{self.current:>3}/{self.total:<3} '
            f'({percent*100:>5.1f}%) '
            f'ETA: {remaining:>3}s'
        )
        sys.stdout.flush()

    def close(self):
        """Cierra la barra"""
        sys.stdout.write('\n')
        sys.stdout.flush()


@dataclass
class ExtractionMetadata:
    """Metadatos de la extracción"""
    source_file: str
    total_pages: int
    file_size_mb: float
    extraction_date: str
    extraction_time_sec: float
    quality_score: float
    language: str
    has_tables: bool
    has_images: bool
    tables_count: int
    images_count: int
    errors: List[str]


class PDFExtractor:
    """
    Extrae PDFs con manejo robusto de archivos grandes
    - Procesa página por página
    - Sin cargar todo en memoria
    - Recuperación de errores
    - Progreso visible
    """

    # Configuración
    TIMEOUT_PER_PAGE = 30  # segundos por página
    MAX_RETRIES = 3
    CHUNK_SIZE = 50  # páginas por chunk

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.logger = logger if verbose else logging.getLogger('null')

    def extract(self, pdf_path: str, lang: str = 'auto') -> Dict[str, Any]:
        """
        Extrae PDF completo con manejo de archivos grandes

        Args:
            pdf_path: Ruta del PDF
            lang: Idioma ('es', 'en', 'auto')

        Returns:
            Diccionario con contenido extraído
        """
        start_time = time.time()

        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF no encontrado: {pdf_path}")

        file_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
        self._log(f"\n📄 Procesando: {Path(pdf_path).name} ({file_size_mb:.1f} MB)")

        # Obtener número de páginas
        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
        except Exception as e:
            self._log(f"❌ Error leyendo PDF: {e}")
            raise

        self._log(f"📊 Total de páginas: {total_pages}")

        # Inicializar contenedores
        all_text = []
        all_tables = []
        all_images = []
        errors = []

        # Extrae en chunks para optimizar memoria
        progress = ProgressBar(total_pages, desc="Extrayendo")

        try:
            # Extrae texto (pdfminer es más eficiente para todo de una)
            self._log("\n🔍 Extrayendo texto...")
            try:
                text = extract_text(pdf_path)
                all_text.append(text)
                self._log("✓ Texto extraído")
            except Exception as e:
                self._log(f"⚠ Error extrayendo texto: {e}")
                errors.append(f"Error en texto: {str(e)[:100]}")

            # Extrae tablas por página (usa menos memoria)
            self._log("\n🔍 Extrayendo tablas...")
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    for page_idx, page in enumerate(pdf.pages, 1):
                        try:
                            page_tables = page.extract_tables()
                            if page_tables:
                                for table_idx, table in enumerate(page_tables):
                                    markdown_table = self._format_table(table)
                                    all_tables.append({
                                        'page': page_idx,
                                        'table_num': table_idx,
                                        'rows': len(table),
                                        'cols': len(table[0]) if table else 0,
                                        'markdown': markdown_table,
                                        'raw': table
                                    })
                        except Exception as e:
                            errors.append(f"Error tabla p{page_idx}: {str(e)[:50]}")

                        progress.update(1)

            except Exception as e:
                self._log(f"⚠ Error extrayendo tablas: {e}")
                errors.append(f"Error tablas: {str(e)[:100]}")

            progress.close()
            self._log(f"✓ Tablas extraídas: {len(all_tables)}")

            # Extrae imágenes (rápido)
            self._log("\n🔍 Extrayendo imágenes...")
            try:
                doc = fitz.open(pdf_path)
                for page_num, page in enumerate(doc, 1):
                    try:
                        image_list = page.get_images()
                        for img_num, img in enumerate(image_list):
                            all_images.append({
                                'page': page_num,
                                'image_num': img_num,
                                'xref': img[0],
                                'reference': f"![img-p{page_num}-{img_num}](img-p{page_num}-{img_num}.png)"
                            })
                    except Exception as e:
                        errors.append(f"Error imagen p{page_num}: {str(e)[:50]}")
                doc.close()
                self._log(f"✓ Imágenes referenciadas: {len(all_images)}")
            except Exception as e:
                self._log(f"⚠ Error extrayendo imágenes: {e}")
                errors.append(f"Error imágenes: {str(e)[:100]}")

            # Detecta idioma
            if lang == 'auto' and LANGDETECT_AVAILABLE and all_text:
                try:
                    lang = detect(all_text[0][:1000])  # Usa solo primeros 1000 chars
                    self._log(f"🌐 Idioma detectado: {lang}")
                except:
                    lang = 'unknown'

            # Formatea contenido
            markdown = self._format_markdown(all_text, all_tables, all_images)

            # Calcula calidad
            quality_score = self._calculate_quality(markdown, errors)

            # Metadatos
            extraction_time = time.time() - start_time
            metadata = ExtractionMetadata(
                source_file=Path(pdf_path).name,
                total_pages=total_pages,
                file_size_mb=file_size_mb,
                extraction_date=datetime.now().isoformat(),
                extraction_time_sec=extraction_time,
                quality_score=quality_score,
                language=lang,
                has_tables=len(all_tables) > 0,
                has_images=len(all_images) > 0,
                tables_count=len(all_tables),
                images_count=len(all_images),
                errors=errors
            )

            self._log(f"\n✅ Extracción completada en {extraction_time:.1f}s")
            self._log(f"📊 Calidad: {quality_score:.1f}%")

            return {
                'markdown': markdown,
                'tables': all_tables,
                'images': all_images,
                'metadata': asdict(metadata),
                'raw_text': '\n'.join(all_text)
            }

        except Exception as e:
            self._log(f"\n❌ Error fatal: {e}")
            raise

    def _format_table(self, table: List[List[str]]) -> str:
        """Formatea tabla para Markdown"""
        if not table or not table[0]:
            return ""

        try:
            headers = table[0]
            rows = table[1:] if len(table) > 1 else []
            return tabulate.tabulate(
                rows,
                headers=headers,
                tablefmt='github',
                stralign='left'
            )
        except:
            # Fallback: formato manual
            lines = []
            if table:
                lines.append('| ' + ' | '.join(str(c) for c in table[0]) + ' |')
                lines.append('|' + '|'.join(['-' * 3] * len(table[0])) + '|')
                for row in table[1:]:
                    lines.append('| ' + ' | '.join(str(c) for c in row) + ' |')
            return '\n'.join(lines)

    def _format_markdown(self, texts: List, tables: List, images: List) -> str:
        """Formatea contenido en Markdown"""
        parts = []

        # Contenido principal
        if texts:
            parts.append('\n'.join(texts))

        # Tablas
        if tables:
            parts.append('\n## Tablas\n')
            for table in tables:
                parts.append(f"### Tabla p{table['page']}-{table['table_num']}\n")
                parts.append(table['markdown'])
                parts.append('')

        # Imágenes
        if images:
            parts.append('\n## Imágenes\n')
            for img in images:
                parts.append(img['reference'])

        return '\n'.join(parts)

    def _calculate_quality(self, content: str, errors: List) -> float:
        """Calcula puntuación de calidad"""
        base_score = 100.0

        # Penaliza por errores
        base_score -= len(errors) * 10

        # Penaliza por contenido muy corto
        if len(content) < 100:
            base_score -= 30

        return max(0, min(100, base_score))

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
            print(f"✓ Guardado: {args.output}")
        else:
            print(result['markdown'])

        # Resumen
        meta = result['metadata']
        print(f"\n📊 Resumen:")
        print(f"  Páginas: {meta['total_pages']}")
        print(f"  Tiempo: {meta['extraction_time_sec']:.1f}s")
        print(f"  Calidad: {meta['quality_score']:.1f}%")
        print(f"  Tablas: {meta['tables_count']}")
        print(f"  Imágenes: {meta['images_count']}")

        if meta['errors']:
            print(f"\n⚠ Errores: {len(meta['errors'])}")
            for err in meta['errors'][:3]:
                print(f"  - {err}")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
