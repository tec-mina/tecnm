import tempfile
import unittest
from pathlib import Path

from pdf_extractor.core.cache import compute_key


class CacheKeyTests(unittest.TestCase):
    def test_compute_key_changes_when_cache_sensitive_options_change(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            pdf_path = Path(tmp_dir) / "sample.pdf"
            pdf_path.write_bytes(b"%PDF-1.4\ncache-key-test\n")

            key_without_images = compute_key(
                str(pdf_path),
                "ocr:tesseract-basic",
                {"with_images": False, "with_toc": True},
            )
            key_with_images = compute_key(
                str(pdf_path),
                "ocr:tesseract-basic",
                {"with_images": True, "with_toc": True},
            )

        self.assertNotEqual(key_without_images, key_with_images)
        self.assertNotIn(":", key_without_images)
        self.assertNotIn(":", key_with_images)


if __name__ == "__main__":
    unittest.main()