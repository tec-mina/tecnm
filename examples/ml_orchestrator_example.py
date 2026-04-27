#!/usr/bin/env python3
"""
examples/ml_orchestrator_example.py — Demonstrate intelligent OCR strategy selection.

Shows how the ML orchestrator characterizes a PDF and recommends the best
OCR strategy based on its characteristics.
"""

import os
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pdf_extractor.core.ml_orchestrator import (
    PDFCharacterizer,
    ModelSelector,
    analyze_and_recommend,
)
from pdf_extractor.features._quality_scorer import (
    ImageQualityScorer,
    adaptive_preprocessing_recommendation,
)


def example_1_basic_analysis():
    """Example 1: Analyze a PDF and see what strategy is recommended."""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Basic PDF Analysis → Strategy Recommendation")
    print("=" * 80)

    # Create a dummy PDF path for demo
    test_pdf = Path(__file__).parent.parent / "tests" / "data" / "sample.pdf"

    if not test_pdf.exists():
        print(f"ℹ️  Test PDF not found at {test_pdf}")
        print("   In production, you would call:")
        print()
        print("   features, strategy = analyze_and_recommend('your_document.pdf')")
        print()
        print("   features will contain:")
        print("     - text_percentage: % native text vs scanned")
        print("     - has_tables, has_images: Boolean flags")
        print("     - layout_complexity: 0-100 score")
        print("     - estimated_quality: 0-100 score")
        print("     - languages_detected: ['es', 'en', ...]")
        print()
        print("   strategy will recommend:")
        print("     - primary: best model for this PDF type")
        print("     - fallbacks: chain of alternatives")
        print("     - ensemble: whether to run multiple models in parallel")
        print("     - preprocessing_hint: 'none' | 'light' | 'medium' | 'heavy'")
        return

    print(f"Analyzing: {test_pdf}")
    features, strategy = analyze_and_recommend(str(test_pdf))

    print("\nPDF Features:")
    print(f"  Text percentage: {features.text_percentage:.1f}% (native text)")
    print(f"  Has tables: {features.has_tables}")
    print(f"  Has images: {features.has_images}")
    print(f"  Layout complexity: {features.layout_complexity:.1f}/100")
    print(f"  Estimated quality: {features.estimated_quality:.1f}/100")
    print(f"  Languages: {', '.join(features.languages_detected)}")
    print(f"  Page count: {features.page_count}")
    print(f"  Complexity tier: {features.complexity_tier().value}")

    print("\nRecommended Strategy:")
    print(f"  Tier: {strategy.tier.value}")
    print(f"  Primary model: {strategy.primary}")
    print(f"  Fallbacks: {' → '.join(strategy.fallbacks)}")
    print(f"  Use ensemble (parallel models): {strategy.ensemble}")
    print(f"  Preprocessing hint: {strategy.preprocessing_hint}")
    print(f"  GPU recommended: {strategy.gpu_recommended}")
    print(f"  Estimated time: {strategy.estimated_cost_seconds:.1f}s")
    print(f"  Confidence threshold: {strategy.confidence_threshold}")


def example_2_manual_characterization():
    """Example 2: Use characterizer directly to understand a PDF."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Direct PDF Characterization")
    print("=" * 80)

    test_pdf = Path(__file__).parent.parent / "tests" / "data" / "sample.pdf"

    if not test_pdf.exists():
        print(f"ℹ️  Test PDF not found. Skipping this example.")
        return

    characterizer = PDFCharacterizer(str(test_pdf))
    features = characterizer.analyze()

    print(f"\nCharacterized: {test_pdf}")
    print(f"  Complexity tier: {features.complexity_tier().value}")
    print(f"  Text: {features.text_percentage:.0f}%")
    print(f"  Quality: {features.estimated_quality:.0f}%")


def example_3_model_selection():
    """Example 3: Given features, see what different selectors would recommend."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Strategy Selector (Decision Logic)")
    print("=" * 80)

    from pdf_extractor.core.ml_orchestrator import PDFFeatures, ComplexityTier

    selector = ModelSelector()

    # Simulate different PDF types
    scenarios = [
        {
            "name": "Clean native text PDF",
            "features": PDFFeatures(
                text_percentage=95,
                has_tables=False,
                has_images=False,
                layout_complexity=10,
                estimated_quality=95,
                languages_detected=["es"],
                page_count=5,
                avg_pages_with_text=100,
                avg_page_size_kb=50,
            ),
        },
        {
            "name": "Scanned + tables (medium quality)",
            "features": PDFFeatures(
                text_percentage=30,
                has_tables=True,
                has_images=False,
                layout_complexity=45,
                estimated_quality=60,
                languages_detected=["es", "en"],
                page_count=20,
                avg_pages_with_text=80,
                avg_page_size_kb=150,
            ),
        },
        {
            "name": "Degraded scan with handwriting",
            "features": PDFFeatures(
                text_percentage=5,
                has_tables=True,
                has_images=True,
                layout_complexity=80,
                estimated_quality=25,
                languages_detected=["es"],
                page_count=10,
                avg_pages_with_text=60,
                avg_page_size_kb=200,
            ),
        },
    ]

    for scenario in scenarios:
        features = scenario["features"]
        strategy = selector.recommend(features)

        print(f"\n📄 Scenario: {scenario['name']}")
        print(f"   Tier: {strategy.tier.value}")
        print(f"   → Primary: {strategy.primary}")
        print(f"   → Fallbacks: {strategy.fallbacks}")
        print(f"   → Ensemble: {'Yes' if strategy.ensemble else 'No'}")
        print(f"   → Est. time: {strategy.estimated_cost_seconds:.1f}s")


def example_4_quality_scoring():
    """Example 4: Score image quality and get preprocessing recommendations."""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Image Quality Scoring")
    print("=" * 80)

    print("ℹ️  Image Quality Scorer analyzes:")
    print("   - Contrast ratio (Weber)")
    print("   - Edge definition (Laplacian variance)")
    print("   - Noise level (entropy)")
    print("   - Sharpness (Tenengrad)")
    print("   - Brightness/exposure")
    print("   - Skew angle (Hough transform)")
    print()
    print("Output: Preprocessing recommendation")
    print("   - NONE: Quality >= 85 (don't touch)")
    print("   - LIGHT: 50-85 (Pillow enhancement)")
    print("   - MEDIUM: 30-50 (OpenCV denoise/deskew)")
    print("   - HEAVY: < 30 (Full preprocessing)")
    print()

    # Find a test image
    test_images_dir = Path(__file__).parent.parent / "tests" / "data" / "images"
    if test_images_dir.exists():
        test_images = list(test_images_dir.glob("*.png")) + list(
            test_images_dir.glob("*.jpg")
        )

        if test_images:
            print(f"Found {len(test_images)} test image(s):")
            scorer = ImageQualityScorer()

            for img_path in test_images[:3]:  # Show first 3
                try:
                    with open(img_path, "rb") as f:
                        img_bytes = f.read()

                    metrics = scorer.score(img_bytes)
                    print(f"\n  📷 {img_path.name}")
                    print(f"     Overall quality: {metrics.overall_score:.1f}/100")
                    print(f"     Recommendation: {metrics.recommendation.value}")

                except Exception as e:
                    print(f"     Error: {e}")
        else:
            print("No test images found.")
    else:
        print("Test images directory not found.")
    print()


def example_5_practical_workflow():
    """Example 5: Practical workflow - analyze, recommend, execute."""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Complete Workflow (Analyze → Recommend → Execute)")
    print("=" * 80)

    print("""
Typical workflow:

1. analyze_and_recommend(pdf_path)
   → Characterizes PDF
   → Returns (features, strategy)

2. Check strategy.tier
   - CLEAN_SCAN: Fast path (Tesseract only)
   - NORMAL: Medium complexity (EasyOCR)
   - COMPLEX: Use ensemble or Docling
   - EXTREME: Full resources, heavy preprocessing

3. Decide execution based on strategy.ensemble
   if strategy.ensemble:
       result = ensemble_extract(pdf_path, models=[...])
       # Run multiple models in parallel, vote
   else:
       result = extract(pdf_path, strategy=strategy.primary)
       # Use single best model

4. Optional: Check strategy.quality_scoring_required
   if strategy.quality_scoring_required:
       quality = score_image_quality(page_image)
       adapt_preprocessing_based_on_quality(quality)

5. Expected latency vs quality tradeoff:
   - CLEAN_SCAN: 5-10s, confidence ~0.90
   - NORMAL: 30-45s, confidence ~0.85
   - COMPLEX: 60-90s, confidence ~0.88 (ensemble)
   - EXTREME: 120-180s, confidence ~0.82 (multiple retries)
    """)


if __name__ == "__main__":
    print("\n" + "█" * 80)
    print("█" + " " * 78 + "█")
    print("█" + "  ML ORCHESTRATOR EXAMPLES".center(78) + "█")
    print("█" + " " * 78 + "█")
    print("█" * 80)

    example_1_basic_analysis()
    example_2_manual_characterization()
    example_3_model_selection()
    example_4_quality_scoring()
    example_5_practical_workflow()

    print("\n" + "=" * 80)
    print("For more details, see: ML_AI_AUDIT.md")
    print("=" * 80 + "\n")
