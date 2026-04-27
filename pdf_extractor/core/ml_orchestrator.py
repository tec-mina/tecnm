"""
core/ml_orchestrator.py — ML-driven PDF analysis + intelligent model selection.

Core Intelligence:
- PDFCharacterizer: Analyzes PDF → features → complexity score
- ModelSelector: complexity score → recommended strategy + fallback chain

Philosophy:
Instead of always using same pipeline (tesseract → easyocr → docling),
this module characterizes each PDF and selects the most cost-effective model(s).

Example:
    characterizer = PDFCharacterizer(pdf_path)
    features = characterizer.analyze()

    selector = ModelSelector()
    strategy = selector.recommend(features)
    # → Strategy(primary="ocr:tesseract-basic", fallbacks=["ocr:easyocr"], ...)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class ComplexityTier(Enum):
    """PDF complexity classification."""
    CLEAN_SCAN = "clean_scan"  # Native text, good quality, simple layout
    NORMAL = "normal"  # Mix of text/scans, reasonable quality
    COMPLEX = "complex"  # Tables, mixed layouts, poor quality
    EXTREME = "extreme"  # Handwriting, multiple languages, degraded


@dataclass
class PDFFeatures:
    """Extracted PDF characteristics."""
    text_percentage: float  # 0-100: % of text native vs scanned
    has_tables: bool
    has_images: bool
    layout_complexity: float  # 0-100: estimated layout complexity
    estimated_quality: float  # 0-100: estimated scan quality
    languages_detected: list[str]  # ["es", "en", ...]
    page_count: int
    avg_pages_with_text: float  # 0-100: % pages with text content
    avg_page_size_kb: float
    metadata: dict = field(default_factory=dict)

    def complexity_tier(self) -> ComplexityTier:
        """Classify into complexity tier based on features."""
        # Scoring logic
        score = 0.0

        # Text-nativeness boost
        if self.text_percentage > 80:
            score -= 20  # Reduce complexity if mostly native text
        elif self.text_percentage < 20:
            score += 15  # Increase if mostly scanned

        # Layout complexity
        score += self.layout_complexity * 0.5

        # Quality penalty
        if self.estimated_quality < 50:
            score += 20  # Poor quality = more complex

        # Tables/Images
        if self.has_tables:
            score += 15
        if self.has_images:
            score += 10

        # Multi-language penalty
        if len(self.languages_detected) > 2:
            score += 10

        # Normalize to 0-100
        score = max(0, min(100, score))

        if score <= 20:
            return ComplexityTier.CLEAN_SCAN
        elif score <= 45:
            return ComplexityTier.NORMAL
        elif score <= 70:
            return ComplexityTier.COMPLEX
        else:
            return ComplexityTier.EXTREME


@dataclass
class OCRStrategy:
    """Recommended OCR strategy with fallbacks."""
    tier: ComplexityTier
    primary: str  # e.g., "ocr:tesseract-basic"
    fallbacks: list[str]  # Fallback chain
    ensemble: bool  # If True, run multiple models in parallel and vote
    quality_scoring_required: bool  # If True, run quality scorer first
    preprocessing_hint: str  # "none" | "light" | "heavy"
    gpu_recommended: bool
    estimated_cost_seconds: float
    confidence_threshold: float = 0.75  # Stop if >= this


class PDFCharacterizer:
    """Analyzes PDF to extract features for intelligent model selection."""

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.logger = logger.getChild("PDFCharacterizer")

    def analyze(self) -> PDFFeatures:
        """Analyze PDF and extract features.

        This is a heuristic implementation. In production, you'd integrate:
        - LayoutLM / Pix2Struct for layout understanding
        - langdetect for language identification
        - perceptual hashing for quality estimation
        """
        features = PDFFeatures(
            text_percentage=self._estimate_text_percentage(),
            has_tables=self._detect_tables(),
            has_images=self._detect_images(),
            layout_complexity=self._estimate_layout_complexity(),
            estimated_quality=self._estimate_quality(),
            languages_detected=self._detect_languages(),
            page_count=self._count_pages(),
            avg_pages_with_text=self._estimate_pages_with_text(),
            avg_page_size_kb=self._estimate_page_size(),
        )

        self.logger.info(
            f"PDF analyzed: tier={features.complexity_tier().value}, "
            f"text={features.text_percentage:.0f}%, quality={features.estimated_quality:.0f}%"
        )

        return features

    def _estimate_text_percentage(self) -> float:
        """Estimate % of text that is native (not scanned)."""
        try:
            import pymupdf as fitz
        except ImportError:
            try:
                import fitz
            except ImportError:
                self.logger.warning("PyMuPDF not available; assuming 50% text")
                return 50.0

        try:
            doc = fitz.open(self.pdf_path)
            text_pages = 0
            for page in doc:
                # If page.get_text() returns content, it's likely native text
                if page.get_text(output="text").strip():
                    text_pages += 1
            doc.close()

            if doc.page_count == 0:
                return 0.0
            return (text_pages / doc.page_count) * 100.0
        except Exception as e:
            self.logger.warning(f"Error estimating text: {e}")
            return 50.0

    def _detect_tables(self) -> bool:
        """Detect if PDF contains tables."""
        try:
            import pymupdf as fitz
        except ImportError:
            try:
                import fitz
            except ImportError:
                return False

        try:
            doc = fitz.open(self.pdf_path)
            # Heuristic: check for table-like block structures
            for page in doc:
                blocks = page.get_text("blocks")
                # Tables often appear as multiple rows of structured blocks
                table_candidates = sum(
                    1 for b in blocks if isinstance(b, tuple) and len(b) > 4
                )
                if table_candidates > 5:
                    doc.close()
                    return True
            doc.close()
            return False
        except Exception as e:
            self.logger.warning(f"Error detecting tables: {e}")
            return False

    def _detect_images(self) -> bool:
        """Detect if PDF contains images."""
        try:
            import pymupdf as fitz
        except ImportError:
            try:
                import fitz
            except ImportError:
                return False

        try:
            doc = fitz.open(self.pdf_path)
            for page in doc:
                if page.get_images():
                    doc.close()
                    return True
            doc.close()
            return False
        except Exception as e:
            self.logger.warning(f"Error detecting images: {e}")
            return False

    def _estimate_layout_complexity(self) -> float:
        """Estimate layout complexity (0-100).

        Simple heuristic: more blocks = more complex.
        In production: use LayoutLM or similar.
        """
        try:
            import pymupdf as fitz
        except ImportError:
            try:
                import fitz
            except ImportError:
                return 50.0

        try:
            doc = fitz.open(self.pdf_path)
            total_blocks = 0
            for page in doc:
                blocks = page.get_text("blocks")
                total_blocks += len(blocks)

            avg_blocks = total_blocks / doc.page_count if doc.page_count > 0 else 0
            # Normalize: 0-5 blocks = low, 20+ = high
            complexity = min(100, (avg_blocks / 20) * 100)
            doc.close()
            return complexity
        except Exception as e:
            self.logger.warning(f"Error estimating layout: {e}")
            return 50.0

    def _estimate_quality(self) -> float:
        """Estimate image quality (0-100).

        Simple heuristic: based on file size and text extractability.
        In production: use perceptual hashing (pHash, dHash).
        """
        try:
            import os
            file_size_mb = os.path.getsize(self.pdf_path) / (1024 * 1024)

            # Larger files often = higher quality images
            quality = min(100, (file_size_mb / 5) * 100)  # 5 MB = "high quality"

            # Boost if text is extractable (native text = good quality)
            text_pct = self._estimate_text_percentage()
            if text_pct > 80:
                quality += 10

            return min(100, quality)
        except Exception as e:
            self.logger.warning(f"Error estimating quality: {e}")
            return 50.0

    def _detect_languages(self) -> list[str]:
        """Detect languages in PDF."""
        try:
            from langdetect import detect_langs
        except ImportError:
            self.logger.debug("langdetect not available; defaulting to [es, en]")
            return ["es", "en"]

        try:
            import pymupdf as fitz
        except ImportError:
            try:
                import fitz
            except ImportError:
                return ["es", "en"]

        try:
            doc = fitz.open(self.pdf_path)
            text_sample = ""
            for i, page in enumerate(doc):
                text_sample += page.get_text(output="text")
                if i >= 2:  # Sample first 3 pages
                    break

            if not text_sample.strip():
                return ["es", "en"]  # Fallback for scanned docs

            detected = detect_langs(text_sample[:500])  # First 500 chars
            doc.close()
            return [d.lang for d in detected][:3]  # Top 3 languages
        except Exception as e:
            self.logger.debug(f"Error detecting languages: {e}")
            return ["es", "en"]

    def _count_pages(self) -> int:
        """Count pages in PDF."""
        try:
            import pymupdf as fitz
        except ImportError:
            try:
                import fitz
            except ImportError:
                return 0

        try:
            doc = fitz.open(self.pdf_path)
            count = doc.page_count
            doc.close()
            return count
        except Exception as e:
            self.logger.warning(f"Error counting pages: {e}")
            return 0

    def _estimate_pages_with_text(self) -> float:
        """Estimate % of pages with text content."""
        try:
            import pymupdf as fitz
        except ImportError:
            try:
                import fitz
            except ImportError:
                return 50.0

        try:
            doc = fitz.open(self.pdf_path)
            pages_with_text = 0
            for page in doc:
                if page.get_text(output="text").strip():
                    pages_with_text += 1

            if doc.page_count == 0:
                return 0.0
            result = (pages_with_text / doc.page_count) * 100
            doc.close()
            return result
        except Exception as e:
            self.logger.warning(f"Error estimating pages with text: {e}")
            return 50.0

    def _estimate_page_size(self) -> float:
        """Average page size in KB."""
        try:
            import os
            total_bytes = os.path.getsize(self.pdf_path)
            page_count = self._count_pages()
            if page_count == 0:
                return 0.0
            return (total_bytes / page_count) / 1024  # KB
        except Exception as e:
            self.logger.warning(f"Error estimating page size: {e}")
            return 100.0


class ModelSelector:
    """Selects optimal OCR strategy based on PDF features."""

    def __init__(self):
        self.logger = logger.getChild("ModelSelector")

    def recommend(self, features: PDFFeatures) -> OCRStrategy:
        """Recommend OCR strategy based on features.

        Returns OCRStrategy with primary model, fallbacks, and configuration.
        """
        tier = features.complexity_tier()
        self.logger.info(f"Recommending strategy for tier: {tier.value}")

        if tier == ComplexityTier.CLEAN_SCAN:
            return self._strategy_clean_scan(features)
        elif tier == ComplexityTier.NORMAL:
            return self._strategy_normal(features)
        elif tier == ComplexityTier.COMPLEX:
            return self._strategy_complex(features)
        else:
            return self._strategy_extreme(features)

    def _strategy_clean_scan(self, features: PDFFeatures) -> OCRStrategy:
        """Clean scan: native text, good quality → Tesseract only."""
        return OCRStrategy(
            tier=ComplexityTier.CLEAN_SCAN,
            primary="ocr:tesseract-basic",
            fallbacks=["ocr:tesseract-advanced"],
            ensemble=False,
            quality_scoring_required=False,
            preprocessing_hint="none",
            gpu_recommended=False,
            estimated_cost_seconds=5.0,
            confidence_threshold=0.80,
        )

    def _strategy_normal(self, features: PDFFeatures) -> OCRStrategy:
        """Normal: mix of text/scans, reasonable quality → EasyOCR."""
        return OCRStrategy(
            tier=ComplexityTier.NORMAL,
            primary="ocr:easyocr",
            fallbacks=["ocr:tesseract-advanced", "text:docling"],
            ensemble=False,
            quality_scoring_required=True,
            preprocessing_hint="light",
            gpu_recommended=True,
            estimated_cost_seconds=30.0,
            confidence_threshold=0.75,
        )

    def _strategy_complex(self, features: PDFFeatures) -> OCRStrategy:
        """Complex: tables, degraded quality → Ensemble (EasyOCR + Tesseract) + Docling."""
        preprocessing = "heavy" if features.estimated_quality < 50 else "light"
        return OCRStrategy(
            tier=ComplexityTier.COMPLEX,
            primary="text:docling",  # Best for layouts
            fallbacks=["ocr:easyocr", "ocr:tesseract-advanced", "tables:img2table"],
            ensemble=True,  # Run EasyOCR + Tesseract in parallel, vote
            quality_scoring_required=True,
            preprocessing_hint=preprocessing,
            gpu_recommended=True,
            estimated_cost_seconds=60.0,
            confidence_threshold=0.70,
        )

    def _strategy_extreme(self, features: PDFFeatures) -> OCRStrategy:
        """Extreme: handwriting, multiple langs, degraded → Full ensemble + heavy prep."""
        return OCRStrategy(
            tier=ComplexityTier.EXTREME,
            primary="text:docling",  # Start with best
            fallbacks=["ocr:easyocr", "tables:img2table"],
            ensemble=True,  # Always vote
            quality_scoring_required=True,
            preprocessing_hint="heavy",
            gpu_recommended=True,
            estimated_cost_seconds=120.0,
            confidence_threshold=0.65,  # Lower threshold for tough cases
        )


# ── API for Pipeline Integration ──────────────────────────────────────────────

def analyze_and_recommend(pdf_path: str) -> tuple[PDFFeatures, OCRStrategy]:
    """One-shot: analyze PDF and get recommended strategy."""
    characterizer = PDFCharacterizer(pdf_path)
    features = characterizer.analyze()

    selector = ModelSelector()
    strategy = selector.recommend(features)

    return features, strategy


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) < 2:
        print("Usage: python -m pdf_extractor.core.ml_orchestrator <pdf_path>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    features, strategy = analyze_and_recommend(pdf_path)

    print("\n" + "=" * 70)
    print("PDF ANALYSIS")
    print("=" * 70)
    print(f"Text percentage: {features.text_percentage:.1f}%")
    print(f"Has tables: {features.has_tables}")
    print(f"Has images: {features.has_images}")
    print(f"Layout complexity: {features.layout_complexity:.1f}/100")
    print(f"Estimated quality: {features.estimated_quality:.1f}/100")
    print(f"Languages: {', '.join(features.languages_detected)}")
    print(f"Pages: {features.page_count}")
    print(f"Complexity tier: {features.complexity_tier().value}")

    print("\n" + "=" * 70)
    print("RECOMMENDATION")
    print("=" * 70)
    print(f"Strategy: {strategy.tier.value}")
    print(f"Primary: {strategy.primary}")
    print(f"Fallbacks: {' → '.join(strategy.fallbacks)}")
    print(f"Ensemble: {strategy.ensemble}")
    print(f"Quality scoring: {strategy.quality_scoring_required}")
    print(f"Preprocessing: {strategy.preprocessing_hint}")
    print(f"GPU recommended: {strategy.gpu_recommended}")
    print(f"Est. time: {strategy.estimated_cost_seconds:.1f}s")
    print("=" * 70 + "\n")
