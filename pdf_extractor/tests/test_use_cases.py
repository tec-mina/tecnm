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

            with patch(
                "pdf_extractor.core.cache.load_or_none",
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


class PipelineTelemetryTruthfulnessTests(unittest.TestCase):
    """features_used must reflect only strategies that produced content.

    Regression guard: prior behavior appended every attempted strategy,
    including ones whose backend was missing (confidence 0.0). That lied
    to downstream agents about what actually ran.
    """

    def test_features_used_excludes_zero_confidence_backends(self) -> None:
        from pdf_extractor.core import pipeline as pipe
        from pdf_extractor.features._base import FeatureResult
        from pdf_extractor.core.preflight import PreflightResult
        from pdf_extractor.core.detector import PDFProfile
        from pdf_extractor.core.platform import PlatformInfo

        emitted: list[dict] = []

        def emit(event: str, **data):
            emitted.append({"event": event, **data})

        def fake_run_feature(pdf_path, name, page_range, file_label,
                             on_event=None, output_dir=None):
            # "text_fast" succeeds with content; "tables_camelot" is unavailable.
            if name == "text_fast":
                fr = FeatureResult(feature="text_fast",
                                   markdown="# Doc\n\ntext",
                                   confidence=0.9)
                if on_event:
                    on_event("feature_done", name=name, tier="text",
                             confidence=fr.confidence)
                return fr
            fr = FeatureResult(feature=name,
                               warnings=[f"{name} backend missing"],
                               confidence=0.0)
            if on_event:
                on_event("feature_skip", name=name, tier="tables",
                         reason=fr.warnings[0])
            return fr

        pf = PreflightResult(path="x.pdf", ok=True, page_count=1,
                             file_size_mb=0.1, is_scanned=False)
        profile = PDFProfile(text_native_pages=[1], scanned_pages=[],
                             table_pages=[1])
        platform = PlatformInfo(os="macos", arch="arm64", tesseract_path=None)

        with patch.object(pipe, "_run_feature", side_effect=fake_run_feature):
            result = pipe.run(
                "x.pdf", pf, profile, platform,
                forced_features=["text_fast", "tables_camelot"],
                on_event=emit,
            )

        self.assertEqual(result.features_used, ["text_fast"])
        # Warning from the failed backend must still propagate.
        self.assertTrue(any("tables_camelot" in w for w in result.warnings))


if __name__ == "__main__":
    unittest.main()