import io
import tempfile
import unittest
from pathlib import Path

import pdf_extractor.interfaces.web.app as webapp


class WebJobPersistenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp_dir = tempfile.TemporaryDirectory(prefix="pdfx-web-tests-")
        self.base_dir = Path(self._tmp_dir.name)

        self._old_upload_dir = webapp._UPLOAD_DIR
        self._old_output_dir = webapp._OUTPUT_DIR
        self._old_job_state_dir = webapp._JOB_STATE_DIR

        webapp._UPLOAD_DIR = self.base_dir / "uploads"
        webapp._OUTPUT_DIR = self.base_dir / "output"
        webapp._JOB_STATE_DIR = self.base_dir / "job-state"

        webapp._UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        webapp._OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        webapp._JOB_STATE_DIR.mkdir(parents=True, exist_ok=True)
        webapp._LIVE_EVENTS.clear()

        self.client = webapp.app.test_client()

    def tearDown(self) -> None:
        webapp._LIVE_EVENTS.clear()
        webapp._UPLOAD_DIR = self._old_upload_dir
        webapp._OUTPUT_DIR = self._old_output_dir
        webapp._JOB_STATE_DIR = self._old_job_state_dir
        self._tmp_dir.cleanup()

    def test_uploaded_job_is_available_after_memory_is_cleared(self) -> None:
        response = self.client.post(
            "/api/upload",
            data={"file": (io.BytesIO(b"%PDF-1.4\n%stub\n"), "demo.pdf")},
            content_type="multipart/form-data",
        )
        self.assertEqual(200, response.status_code)
        job_id = response.get_json()["job_id"]

        webapp._LIVE_EVENTS.clear()

        job_response = self.client.get(f"/api/jobs/{job_id}")
        self.assertEqual(200, job_response.status_code)
        self.assertEqual("uploaded", job_response.get_json()["status"])
        self.assertTrue((webapp._JOB_STATE_DIR / f"{job_id}.json").exists())

    def test_stream_returns_persisted_terminal_payload_without_live_queue(self) -> None:
        job_id = "job-terminal"
        webapp._upsert_job(
            job_id,
            status="ok",
            pdf_path=str(self.base_dir / "uploads" / "job-terminal.pdf"),
            original_name="demo.pdf",
            result={"status": "ok", "output_path": "/tmp/out.md"},
        )
        webapp._LIVE_EVENTS.clear()

        response = self.client.get(f"/api/stream/{job_id}")
        body = response.get_data(as_text=True)

        self.assertEqual(200, response.status_code)
        self.assertIn("event: end", body)
        self.assertIn("output_path", body)


if __name__ == "__main__":
    unittest.main()