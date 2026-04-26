import importlib
import pkgutil
import unittest
from unittest.mock import patch

from pdf_extractor.core.registry import _Registry


class RegistryDiscoveryTests(unittest.TestCase):
    def test_discovery_skips_broken_modules_and_reports_them(self) -> None:
        real_import_module = importlib.import_module

        def fake_iter_modules(_path):
            return [
                (None, "broken_feature", False),
                (None, "text_fast", False),
            ]

        def fake_import_module(name: str, package=None):
            if name == "pdf_extractor.features.broken_feature":
                raise SyntaxError("simulated broken feature")
            return real_import_module(name, package)

        with patch.object(pkgutil, "iter_modules", fake_iter_modules), patch.object(
            importlib, "import_module", fake_import_module
        ):
            registry = _Registry()
            strategies = registry.list_all()
            failures = registry.discovery_failures()

        self.assertTrue(any(meta.name == "text:fast" for meta in strategies))
        self.assertEqual(1, len(failures))
        self.assertEqual("pdf_extractor.features.broken_feature", failures[0].module)
        self.assertEqual("SyntaxError", failures[0].error_type)


class RegistryRealDiscoveryTests(unittest.TestCase):
    """Real discovery — guarantees no feature module silently broke its imports.

    This test was added after a regression where a typo in a feature module
    only surfaced on the first /api/v1/strategies hit at runtime. Now any
    broken import shows up in CI / docker build instead of in production.
    """

    def test_no_feature_module_fails_to_import(self) -> None:
        from pdf_extractor.core.registry import registry

        registry.list_all()  # forces discovery
        failures = registry.discovery_failures()
        self.assertEqual(
            [], [f.to_dict() for f in failures],
            f"Feature modules failed to import: {[f.to_dict() for f in failures]}",
        )


if __name__ == "__main__":
    unittest.main()