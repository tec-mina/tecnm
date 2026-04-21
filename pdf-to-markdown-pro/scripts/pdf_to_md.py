#!/usr/bin/env python3
"""
Conversor completo: PDF → Markdown (Extracción + Validación + Corrección)
Flujo profesional con validación integrada y corrección automática

Features:
  ✓ Integración con extractor independiente
  ✓ Validación de calidad automática
  ✓ Corrección inteligente de contenido
  ✓ Frontmatter YAML incluido
  ✓ Reportes de validación detallados
  ✓ Export a JSON opcional
  ✓ Logging configurable
  ✓ Manejo de errores robusto
"""

import os
import sys
import json
import logging
import re
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

# Import del extractor (mismo directorio)
try:
    from extractor import PDFExtractor
except ImportError:
    print("ERROR: extractor.py no encontrado. Debe estar en el mismo directorio.")
    sys.exit(1)

# Logger minimalista
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


@dataclass
class ValidationReport:
    """Reporte de validación con detalles completos"""
    is_valid: bool
    quality_score: float
    issues: List[Dict[str, Any]]
    warnings: List[str]
    recommendations: List[str]
    validation_time_sec: float = 0.0


class PDFToMarkdown:
    """
    Conversor completo PDF → Markdown con validación integrada
    - Extracción robusta de PDFs grandes
    - Validación de calidad automática
    - Corrección inteligente
    - Reportes detallados
    """

    def __init__(self, verify: bool = True, fix: bool = True, verbose: bool = True):
        """
        Args:
            verify: Validar calidad del contenido
            fix: Auto-corregir problemas detectados
            verbose: Mostrar progreso y logs
        """
        self.extractor = PDFExtractor(verbose=verbose)
        self.verify = verify
        self.fix = fix
        self.verbose = verbose
        self.logger = logger if verbose else logging.getLogger('null')

    def process(self, pdf_path: str, lang: str = 'auto', output: Optional[str] = None) -> Dict[str, Any]:
        """
        Procesa PDF completo: extracción → validación → corrección

        Args:
            pdf_path: Ruta del PDF
            lang: Idioma ('es', 'en', 'auto')
            output: Ruta de salida .md (opcional)

        Returns:
            Diccionario con markdown, metadata, validación, tablas e imágenes
        """
        start_time = time.time()

        self._log(f"\n{'='*70}")
        self._log("🔄 PDF TO MARKDOWN - Procesamiento Completo")
        self._log(f"{'='*70}\n")

        try:
            # Paso 1: Extrae PDF
            self._log("📥 [1/4] Extrayendo PDF...")
            extraction = self.extractor.extract(pdf_path, lang)
            self._log(f"✓ Extracción completada ({extraction['metadata']['extraction_time_sec']:.1f}s)")

            # Paso 2: Valida
            validation = None
            if self.verify:
                self._log("\n🔍 [2/4] Validando contenido...")
                validation = self._validate(extraction['markdown'])
                self._log(f"✓ Puntuación de calidad: {validation.quality_score:.1f}%")

            # Paso 3: Corrige
            markdown = extraction['markdown']
            if self.fix and validation and not validation.is_valid:
                self._log("\n🔧 [3/4] Aplicando correcciones automáticas...")
                markdown = self._fix_content(markdown)
                extraction['markdown'] = markdown
                self._log("✓ Correcciones aplicadas")

            # Paso 4: Genera salida
            self._log("\n📄 [4/4] Generando salida final...")
            result = self._generate_output(extraction, validation)

            # Guarda archivo si se especifica
            if output:
                try:
                    output_path = Path(output)
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_text(result['markdown'], encoding='utf-8')
                    self._log(f"✓ Guardado: {output_path.name}")
                except Exception as e:
                    self._log(f"⚠ Error guardando archivo: {e}")

            # Resumen
            total_time = time.time() - start_time
            self._print_summary(extraction, validation, total_time)

            return result

        except Exception as e:
            self._log(f"\n❌ Error fatal: {e}")
            raise

    def _log(self, msg: str):
        """Log controlado"""
        if self.verbose:
            self.logger.info(msg)

    def _validate(self, content: str) -> ValidationReport:
        """
        Valida el contenido extraído con análisis de estructura y calidad
        Detecta problemas comunes en conversiones PDF → Markdown
        """
        start_time = time.time()
        issues = []
        warnings = []

        if not content or len(content) < 10:
            return ValidationReport(
                is_valid=False,
                quality_score=0,
                issues=[{'type': 'empty_content', 'description': 'Contenido vacío'}],
                warnings=[],
                recommendations=['El PDF no contiene texto extraíble'],
                validation_time_sec=time.time() - start_time
            )

        lines = content.split('\n')
        non_empty_lines = [l for l in lines if l.strip()]

        # Problema 1: Líneas muy largas sin espacios (texto sin procesar)
        long_lines = [i for i, line in enumerate(lines, 1)
                     if len(line) > 150 and line.count(' ') < len(line) / 20]
        if len(long_lines) > len(non_empty_lines) * 0.3:
            issues.append({
                'type': 'long_lines',
                'count': len(long_lines),
                'severity': 'high',
                'description': f'{len(long_lines)} líneas muy largas sin espacios (posible texto pegado)'
            })

        # Problema 2: Tablas mal formadas
        table_lines = [line for line in lines if '|' in line and len(line) > 5]
        if len(table_lines) > 0:
            try:
                col_counts = [line.count('|') for line in table_lines if '|' in line]
                if col_counts and len(set(col_counts)) > 1:
                    inconsistent = len(set(col_counts))
                    issues.append({
                        'type': 'malformed_table',
                        'severity': 'medium',
                        'description': f'Tabla con {inconsistent} variaciones en número de columnas'
                    })
            except Exception:
                pass

        # Problema 3: Caracteres especiales problemáticos
        problematic_chars = ['\x00', '\x01', '\x02', '\x03', '\x04', '\x05']
        char_issues = sum(1 for char in problematic_chars if char in content)
        if char_issues > 0:
            issues.append({
                'type': 'special_chars',
                'count': char_issues,
                'severity': 'medium',
                'description': f'{char_issues} caracteres de control detectados'
            })

        # Advertencia 1: Headers inconsistentes
        headers = [line for line in lines if line.startswith('#')]
        if len(headers) > 0:
            try:
                header_levels = [len(re.match(r'^#+', h).group()) for h in headers]
                if len(header_levels) > 1 and max(header_levels) - min(header_levels) > 2:
                    warnings.append(f'Headers con {max(header_levels) - min(header_levels)} niveles de diferencia')
            except Exception:
                pass

        # Advertencia 2: Muchas líneas vacías
        empty_lines = len([l for l in lines if not l.strip()])
        if empty_lines > len(non_empty_lines) * 0.2:
            warnings.append(f'{empty_lines} líneas vacías ({empty_lines*100//len(lines)}% del contenido)')

        # Advertencia 3: Poco contenido
        if len(content) < 500:
            warnings.append('Contenido muy corto (< 500 caracteres)')

        # Calcula puntuación
        quality_score = 100.0
        quality_score -= len([i for i in issues if i.get('severity') == 'high']) * 20
        quality_score -= len([i for i in issues if i.get('severity') == 'medium']) * 10
        quality_score -= len([i for i in issues if i.get('severity') != 'high' and i.get('severity') != 'medium']) * 5
        quality_score -= len(warnings) * 3
        quality_score = max(0, min(100, quality_score))

        # Recomendaciones
        recommendations = []
        if quality_score < 70:
            recommendations.append("⚠ Calidad baja: Revisar manualmente")
        if any(i['type'] == 'long_lines' for i in issues):
            recommendations.append("💡 Usar --fix para normalizar líneas largas")
        if any(i['type'] == 'malformed_table' for i in issues):
            recommendations.append("💡 Revisar tablas manualmente o usar corrección automática")
        if any(i['type'] == 'special_chars' for i in issues):
            recommendations.append("💡 Caracteres especiales detectados, revisar manualmente")

        return ValidationReport(
            is_valid=quality_score >= 80,
            quality_score=quality_score,
            issues=issues,
            warnings=warnings,
            recommendations=recommendations,
            validation_time_sec=time.time() - start_time
        )

    def _fix_content(self, content: str) -> str:
        """
        Aplica correcciones inteligentes al contenido
        Normaliza espacios, tablas, headers y caracteres especiales
        """
        lines = content.split('\n')
        fixed_lines = []
        in_code_block = False

        for line in lines:
            # Detecta bloques de código (no modificar contenido dentro)
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                fixed_lines.append(line)
                continue

            if in_code_block:
                fixed_lines.append(line)
                continue

            # Limpia caracteres especiales
            line = ''.join(c for c in line if ord(c) >= 32 or c in '\t\n')

            # Normaliza espacios múltiples (excepto en tablas)
            if '|' not in line:
                line = re.sub(r' {2,}', ' ', line)

            # Normaliza tablas
            if '|' in line:
                # Normaliza espacios alrededor de pipes
                line = re.sub(r'\s*\|\s*', ' | ', line)
                # Limpia espacios múltiples dentro de celdas
                parts = line.split('|')
                parts = [p.strip() for p in parts]
                line = ' | '.join(parts)

            # Normaliza headers
            if re.match(r'^#+', line):
                match = re.match(r'^(#+)\s*(.*)', line)
                if match:
                    hashes = match.group(1)
                    text = match.group(2).strip()
                    if text:
                        line = f"{hashes} {text}"

            # Normaliza listas
            if re.match(r'^[\s]*[-*+]\s+', line):
                match = re.match(r'^([\s]*)[-*+]\s+(.*)', line)
                if match:
                    indent = match.group(1)
                    text = match.group(2).strip()
                    line = f"{indent}- {text}"

            fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def _generate_output(self, extraction: Dict[str, Any], validation: Optional[ValidationReport] = None) -> Dict[str, Any]:
        """
        Genera salida final con frontmatter YAML y metadata completa
        Incluye información de validación y procesamiento
        """
        meta = extraction['metadata']

        # Frontmatter YAML
        frontmatter = {
            'source': meta['source_file'],
            'pages': meta['total_pages'],
            'file_size_mb': meta['file_size_mb'],
            'extraction_date': meta['extraction_date'],
            'language': meta['language'],
            'tables': meta['tables_count'],
            'images': meta['images_count'],
            'has_images': meta['has_images'],
            'extraction_time_sec': meta['extraction_time_sec']
        }

        if validation:
            frontmatter['quality_score'] = f"{validation.quality_score:.1f}%"
            frontmatter['is_valid'] = validation.is_valid
            frontmatter['validation_time_sec'] = validation.validation_time_sec

        # Construye YAML
        meta_str = "---\n"
        for key, value in frontmatter.items():
            if isinstance(value, str):
                meta_str += f"{key}: {value}\n"
            elif isinstance(value, bool):
                meta_str += f"{key}: {str(value).lower()}\n"
            else:
                meta_str += f"{key}: {value}\n"
        meta_str += "---\n\n"

        # Construye resultado
        return {
            'markdown': meta_str + extraction['markdown'],
            'metadata': extraction['metadata'],
            'validation': {
                'quality_score': validation.quality_score if validation else 0,
                'is_valid': validation.is_valid if validation else True,
                'issues': validation.issues if validation else [],
                'warnings': validation.warnings if validation else [],
                'recommendations': validation.recommendations if validation else [],
                'validation_time_sec': validation.validation_time_sec if validation else 0
            } if validation else None,
            'tables': extraction['tables'],
            'images': extraction['images']
        }

    def _print_summary(self, extraction: Dict[str, Any], validation: Optional[ValidationReport] = None, total_time: float = 0):
        """Imprime resumen profesional de ejecución"""
        self._log(f"\n{'='*70}")
        self._log("✅ RESUMEN DE PROCESAMIENTO")
        self._log(f"{'='*70}\n")

        meta = extraction['metadata']

        # Información del documento
        self._log("📄 Documento:")
        self._log(f"  Archivo: {meta['source_file']}")
        self._log(f"  Páginas: {meta['total_pages']}")
        self._log(f"  Tamaño: {meta['file_size_mb']:.1f} MB")
        self._log(f"  Idioma: {meta['language']}")

        # Contenido extraído
        self._log(f"\n📊 Contenido Extraído:")
        self._log(f"  Tablas: {meta['tables_count']}")
        self._log(f"  Imágenes: {meta['images_count']}")
        self._log(f"  Caracteres: {len(extraction['markdown']):,}")

        # Tiempos
        self._log(f"\n⏱️ Tiempos:")
        self._log(f"  Extracción: {meta['extraction_time_sec']:.1f}s")
        if validation:
            self._log(f"  Validación: {validation.validation_time_sec:.1f}s")
        self._log(f"  Total: {total_time:.1f}s")

        # Validación
        if validation:
            self._log(f"\n✓ Validación:")
            self._log(f"  Calidad: {validation.quality_score:.1f}%")
            status = "✓ VÁLIDO (listo)" if validation.is_valid else "⚠ PROBLEMAS DETECTADOS"
            self._log(f"  Estado: {status}")

            if validation.issues:
                self._log(f"  Problemas: {len(validation.issues)}")
                for issue in validation.issues[:5]:
                    severity = issue.get('severity', 'info').upper()
                    desc = issue.get('description', 'Sin descripción')
                    self._log(f"    [{severity}] {desc}")
                if len(validation.issues) > 5:
                    self._log(f"    ... y {len(validation.issues) - 5} más")

            if validation.warnings:
                self._log(f"  Advertencias: {len(validation.warnings)}")
                for warn in validation.warnings[:3]:
                    self._log(f"    ⚠ {warn}")
                if len(validation.warnings) > 3:
                    self._log(f"    ... y {len(validation.warnings) - 3} más")

            if validation.recommendations:
                self._log(f"\n💡 Recomendaciones:")
                for rec in validation.recommendations:
                    self._log(f"  {rec}")

        self._log(f"\n{'='*70}\n")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Conversor robusto PDF → Markdown con validación integrada',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python pdf_to_md.py documento.pdf -o documento.md
  python pdf_to_md.py documento.pdf --verify --fix -o output.md
  python pdf_to_md.py documento.pdf -o documento.md --json
  python pdf_to_md.py documento.pdf --lang es --quiet
        """
    )

    parser.add_argument('pdf', help='Ruta del archivo PDF')
    parser.add_argument('-o', '--output', help='Archivo de salida .md (opcional)')
    parser.add_argument('--lang', default='auto', choices=['es', 'en', 'auto'],
                       help='Idioma para detección (default: auto)')
    parser.add_argument('--verify', action='store_true', default=True,
                       help='Validar contenido (default: activado)')
    parser.add_argument('--no-verify', dest='verify', action='store_false',
                       help='Desactivar validación')
    parser.add_argument('--fix', action='store_true', default=True,
                       help='Auto-corregir problemas (default: activado)')
    parser.add_argument('--no-fix', dest='fix', action='store_false',
                       help='Desactivar correcciones automáticas')
    parser.add_argument('--json', action='store_true',
                       help='Exportar información adicional como JSON')
    parser.add_argument('--quiet', action='store_true',
                       help='Suprimir logs y progreso')

    args = parser.parse_args()

    try:
        # Validar que el PDF existe
        pdf_path = Path(args.pdf)
        if not pdf_path.exists():
            print(f"❌ Error: Archivo no encontrado: {args.pdf}")
            sys.exit(1)

        # Crear conversor
        converter = PDFToMarkdown(verify=args.verify, fix=args.fix, verbose=not args.quiet)

        # Procesar
        result = converter.process(args.pdf, args.lang, args.output)

        # Exportar JSON si se solicita
        if args.json:
            json_output = str(Path(args.output).with_suffix('.json')) if args.output else 'resultado.json'
            try:
                # Serializar resultado (tabla raw no es JSON-serializable)
                json_data = {
                    'metadata': result.get('metadata', {}),
                    'validation': result.get('validation', {}),
                    'tables_count': len(result.get('tables', [])),
                    'images_count': len(result.get('images', []))
                }
                Path(json_output).write_text(
                    json.dumps(json_data, ensure_ascii=False, indent=2),
                    encoding='utf-8'
                )
                if not args.quiet:
                    print(f"✓ JSON guardado: {json_output}")
            except Exception as e:
                print(f"⚠ No se pudo guardar JSON: {e}")

        if not args.quiet:
            print("\n✅ Procesamiento completado exitosamente")

    except FileNotFoundError as e:
        print(f"❌ Error de archivo: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error fatal: {e}", file=sys.stderr)
        sys.exit(1)
