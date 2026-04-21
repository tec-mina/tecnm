import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import fitz

from pdf_extractor.app.use_cases import ExtractUseCase, ExtractionRequest


class ExtractUseCaseCacheHitTests(unittest.TestCase):
    def test_cache_hit_materializes_markdown_json_and_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            pdf_path = base_dir / "sample.pdf"
            out_dir = base_dir / "out"

            doc = fitz.open()
            page = doc.new_page()
            page.insert_textbox(
                (72, 72, 500, 500),
                (
                    "Documento suficientemente largo para pasar por el preflight y "
                    "probar la rematerializacion de artifacts desde cache."
                ),
            )
            doc.save(pdf_path)
            doc.close()

            cached_markdown = (
                "---\n"
                "from_cache: false\n"
                "quality_score: 88\n"
                "---\n\n"
                "# Titulo\n\n"
                "Contenido recuperado desde cache con suficiente longitud para el test."
            )
            cached_metadata = {
                "features_used": ["text_fast"],
                "quality_score": 88,
                "quality_label": "good",
                "pages": 1,
                "warnings": ["cache-hit"],
                "issues": [{"code": "MISSING_PAGE_MARKERS", "severity": "medium"}],
            }

            with patch("pdf_extractor.core.cache.hit", return_value=True), patch(
                "pdf_extractor.core.cache.load",
                return_value=(cached_markdown, cached_metadata),
            ):
                result = ExtractUseCase().execute(
                    ExtractionRequest(
                        pdf_path=str(pdf_path),
                        output_dir=str(out_dir),
                        output_format="both",
                    )
                )

            md_path = out_dir / "sample.md"
            json_path = out_dir / "sample.json"
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual("cached", result.status)
            self.assertTrue(md_path.exists())
            self.assertTrue(json_path.exists())
            self.assertIn(str(md_path), result.artifacts)
            self.assertIn(str(json_path), result.artifacts)
            self.assertIn("from_cache: true", md_path.read_text(encoding="utf-8"))
            self.assertTrue(payload["from_cache"])
            self.assertEqual(result.artifacts, payload["artifacts"])


if __name__ == "__main__":
    unittest.main()