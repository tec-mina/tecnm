"""
test_api.py — covers regressions in the FastAPI interface.

Bugs covered here:
  1. /api/v1/extract returned a generic 500 when the pipeline produced empty
     output (typically: scanned PDF + no OCR backend installed). The expected
     behaviour now is HTTP 422 with a structured `detail` dict explaining the
     reason (status="blocked", features_used, issues).

  2. /api/v1/batch wrote `_summary.json` twice into the ZIP because
     `zf.writestr("_summary.json", ...)` was duplicated. The ZIP must contain
     `_summary.json` exactly once.
"""

from __future__ import annotations

import io
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

try:
    import fitz  # noqa: F401
    from fastapi.testclient import TestClient
    from pdf_extractor.app.use_cases import ExtractionResult
    from pdf_extractor.interfaces.api import app
    _DEPS_OK = True
except ImportError as _exc:  # pragma: no cover
    _DEPS_OK = False
    _IMPORT_ERR = str(_exc)


def _make_text_pdf(path: Path, text: str = "Texto de prueba suficientemente largo para pasar el preflight.") -> None:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_textbox((72, 72, 500, 500), text)
    doc.save(str(path))
    doc.close()


@unittest.skipUnless(_DEPS_OK, "fastapi/pymupdf not installed in this environment")
class ExtractBlockedReturnsStructuredErrorTests(unittest.TestCase):
    """When the pipeline returns status='blocked', /extract must return 422
    with a useful detail payload — NOT a generic 500."""

    def test_blocked_status_returns_422_with_reason(self) -> None:
        client = TestClient(app)

        # Simulate the use case finishing with status="blocked" and no .md output.
        blocked_result = ExtractionResult(
            status="blocked",
            features_used=[],
            warnings=[],
            issues=[{
                "code": "EMPTY_OUTPUT",
                "severity": "critical",
                "description": "Markdown is empty or under 50 characters",
            }],
        )

        with patch(
            "pdf_extractor.interfaces.api._run_sync_extraction",
            return_value=blocked_result,
        ):
            resp = client.post(
                "/api/v1/extract",
                files={"file": ("scan.pdf", b"%PDF-1.3\n%%EOF\n", "application/pdf")},
            )

        self.assertEqual(resp.status_code, 422, resp.text)
        body = resp.json()
        detail = body.get("detail")
        self.assertIsInstance(detail, dict, f"detail must be a dict, got: {detail!r}")
        self.assertEqual(detail.get("error"), "extraction_blocked")
        self.assertEqual(detail.get("status"), "blocked")
        # Reason mentions OCR / motor (so the user knows what to do).
        self.assertIn("OCR", detail.get("message", ""))
        # Issues are surfaced verbatim.
        self.assertEqual(detail.get("issues"), blocked_result.issues)


@unittest.skipUnless(_DEPS_OK, "fastapi/pymupdf not installed in this environment")
class BatchZipDoesNotDuplicateSummaryTests(unittest.TestCase):
    """The ZIP returned by /batch must contain _summary.json exactly once."""

    def test_summary_json_appears_exactly_once(self) -> None:
        client = TestClient(app)

        with patch(
            "pdf_extractor.interfaces.api._run_sync_extraction",
            return_value=None,  # forces the "extraction produced no output" branch
        ):
            resp = client.post(
                "/api/v1/batch",
                files=[
                    ("files", ("a.pdf", b"%PDF-1.3\n%%EOF\n", "application/pdf")),
                    ("files", ("b.pdf", b"%PDF-1.3\n%%EOF\n", "application/pdf")),
                ],
            )

        self.assertEqual(resp.status_code, 200, resp.text)
        zf = zipfile.ZipFile(io.BytesIO(resp.content))
        names = zf.namelist()
        self.assertEqual(
            names.count("_summary.json"), 1,
            f"_summary.json must appear exactly once in the zip, got names={names!r}",
        )


@unittest.skipUnless(_DEPS_OK, "fastapi/pymupdf not installed in this environment")
class PageRangeValidationTests(unittest.TestCase):
    """Bad page_range used to silently process the whole PDF. Now must 400."""

    def test_garbage_page_range_returns_400(self) -> None:
        client = TestClient(app)
        resp = client.post(
            "/api/v1/extract",
            files={"file": ("a.pdf", b"%PDF-1.3\n%%EOF\n", "application/pdf")},
            data={"page_range": "abc"},
        )
        self.assertEqual(resp.status_code, 400, resp.text)
        detail = resp.json().get("detail")
        self.assertIsInstance(detail, dict)
        self.assertEqual(detail.get("error"), "invalid_page_range")

    def test_inverted_range_returns_400(self) -> None:
        client = TestClient(app)
        resp = client.post(
            "/api/v1/extract",
            files={"file": ("a.pdf", b"%PDF-1.3\n%%EOF\n", "application/pdf")},
            data={"page_range": "10-5"},
        )
        self.assertEqual(resp.status_code, 400, resp.text)


@unittest.skipUnless(_DEPS_OK, "fastapi/pymupdf not installed in this environment")
class ExtractionTimeoutTests(unittest.TestCase):
    """If extraction exceeds the timeout, /extract must return 504, not 500
    or hang the request."""

    def test_long_running_extraction_returns_504(self) -> None:
        import time as _time
        from pdf_extractor.interfaces import api as _api

        client = TestClient(app)

        def _slow(*_args, **_kwargs):
            _time.sleep(2.0)
            return None

        with patch.object(_api, "_EXTRACTION_TIMEOUT_SEC", 1), \
             patch("pdf_extractor.interfaces.api._run_sync_extraction", side_effect=_slow):
            resp = client.post(
                "/api/v1/extract",
                files={"file": ("slow.pdf", b"%PDF-1.3\n%%EOF\n", "application/pdf")},
            )

        self.assertEqual(resp.status_code, 504, resp.text)
        detail = resp.json().get("detail")
        self.assertIsInstance(detail, dict)
        self.assertEqual(detail.get("error"), "extraction_timeout")


@unittest.skipUnless(_DEPS_OK, "fastapi/pymupdf not installed in this environment")
class MetaEndpointsAreUnauthenticatedTests(unittest.TestCase):
    """When API_KEY is set, the UI still needs /capabilities, /strategies and
    /readiness without a token — otherwise the SPA can't render."""

    def test_meta_endpoints_open_when_api_key_is_set(self) -> None:
        from pdf_extractor.interfaces import api as _api

        client = TestClient(app)
        with patch.object(_api, "_API_KEY", "secret-token-for-test"):
            for path in ("/api/v1/capabilities", "/api/v1/strategies", "/api/v1/readiness"):
                resp = client.get(path)
                self.assertNotEqual(
                    resp.status_code, 401,
                    f"{path} returned 401 even though it should be open. body={resp.text}",
                )

    def test_extract_still_requires_token_when_api_key_is_set(self) -> None:
        from pdf_extractor.interfaces import api as _api

        client = TestClient(app)
        with patch.object(_api, "_API_KEY", "secret-token-for-test"):
            resp = client.post(
                "/api/v1/extract",
                files={"file": ("a.pdf", b"%PDF-1.3\n%%EOF\n", "application/pdf")},
            )
        self.assertEqual(resp.status_code, 401, resp.text)


if __name__ == "__main__":
    unittest.main()
