"""
features/_quality_scorer.py — Image quality analysis for adaptive preprocessing.

Metrics (multi-dimensional quality assessment):
- Contrast ratio (Weber)
- Edge definition (Laplacian variance)
- Noise level (entropy)
- Sharpness (Tenengrad)
- Brightness/exposure
- Skew angle (Hough transform)

Decision: Should we preprocess this image before OCR?
- quality >= 85: No preprocessing needed
- 50-85: Light preprocessing (Pillow)
- 30-50: Medium preprocessing (OpenCV)
- < 30: Heavy preprocessing (OpenCV + Unpaper)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class PreprocessingRecommendation(Enum):
    """Preprocessing recommendation."""
    NONE = "none"  # Quality too good to touch
    LIGHT = "light"  # PIL enhancement sufficient
    MEDIUM = "medium"  # OpenCV denoise+deskew
    HEAVY = "heavy"  # Full OpenCV + Unpaper


@dataclass
class QualityMetrics:
    """Detailed quality metrics for an image."""
    contrast_ratio: float  # 0-100, higher = better (Weber contrast)
    edge_definition: float  # 0-100, higher = sharper (Laplacian variance)
    noise_level: float  # 0-100, LOWER = better (entropy, inverted)
    sharpness: float  # 0-100, higher = sharper (Tenengrad)
    brightness: float  # 0-100, target is 50 (optimal exposure)
    skew_angle: float  # degrees, 0 = not skewed
    overall_score: float  # 0-100, weighted composite

    @property
    def is_high_quality(self) -> bool:
        """True if overall score >= 85."""
        return self.overall_score >= 85

    @property
    def is_low_quality(self) -> bool:
        """True if overall score < 30."""
        return self.overall_score < 30

    @property
    def recommendation(self) -> PreprocessingRecommendation:
        """Suggest preprocessing based on quality."""
        if self.overall_score >= 85:
            return PreprocessingRecommendation.NONE
        elif self.overall_score >= 50:
            return PreprocessingRecommendation.LIGHT
        elif self.overall_score >= 30:
            return PreprocessingRecommendation.MEDIUM
        else:
            return PreprocessingRecommendation.HEAVY


class ImageQualityScorer:
    """Analyze image quality and recommend preprocessing."""

    def __init__(self):
        self.logger = logger.getChild("ImageQualityScorer")

    def score(self, img_bytes: bytes) -> QualityMetrics:
        """Score image quality from raw bytes.

        Gracefully falls back if dependencies missing.
        """
        try:
            from PIL import Image
            import io

            img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        except Exception as e:
            self.logger.warning(f"Could not load image: {e}. Returning neutral metrics.")
            return self._neutral_metrics()

        metrics = QualityMetrics(
            contrast_ratio=self._measure_contrast(img),
            edge_definition=self._measure_edge_definition(img),
            noise_level=self._measure_noise(img),
            sharpness=self._measure_sharpness(img),
            brightness=self._measure_brightness(img),
            skew_angle=self._measure_skew(img_bytes),
            overall_score=0.0,  # Computed below
        )

        # Weighted composite score
        metrics.overall_score = (
            metrics.contrast_ratio * 0.20
            + metrics.edge_definition * 0.20
            + (100 - metrics.noise_level) * 0.15  # Inverted: low noise = good
            + metrics.sharpness * 0.20
            + (100 - abs(metrics.brightness - 50) * 2) * 0.10  # Bonus if brightness ~50
            + (100 - min(metrics.skew_angle, 45) / 45 * 100) * 0.15  # Bonus if not skewed
        )
        metrics.overall_score = max(0, min(100, metrics.overall_score))

        return metrics

    def _measure_contrast(self, img) -> float:
        """Measure contrast ratio (Weber contrast).

        Higher = better contrast between text and background.
        Formula: Michelson contrast = (Lmax - Lmin) / (Lmax + Lmin)
        """
        try:
            import numpy as np

            arr = np.array(img.convert("L"), dtype=np.float32)
            lmax = arr.max()
            lmin = arr.min()

            if lmax + lmin == 0:
                return 50.0

            contrast = (lmax - lmin) / (lmax + lmin)
            # Normalize to 0-100
            return min(100, contrast * 100)
        except Exception as e:
            self.logger.debug(f"Contrast measurement failed: {e}")
            return 50.0

    def _measure_edge_definition(self, img) -> float:
        """Measure edge sharpness via Laplacian variance.

        Higher = sharper, better-defined text edges.
        """
        try:
            import cv2
            import numpy as np

            # Convert to grayscale, then to OpenCV format
            gray = np.array(img.convert("L"), dtype=np.uint8)

            # Apply Laplacian (edge detection)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            variance = laplacian.var()

            # Normalize (empirically, good scans ~100-500, poor <50)
            score = min(100, (variance / 5))  # Scale factor
            return max(0, score)
        except Exception as e:
            self.logger.debug(f"Edge definition measurement failed: {e}")
            return 50.0

    def _measure_noise(self, img) -> float:
        """Measure noise level via entropy.

        Lower entropy = less noise. Returns inverted (0=noisy, 100=clean).
        """
        try:
            import numpy as np
            from PIL import ImageFilter

            # Laplacian-of-Gaussian to detect high-frequency noise
            gray = np.array(img.convert("L"), dtype=np.uint8)

            # Standard deviation of pixel differences (proxy for noise)
            diffs = np.diff(gray.flatten())
            noise_estimate = np.std(diffs)

            # Empirically, good scans have low noise (~1-5)
            # Normalize and invert
            score = 100 - min(100, (noise_estimate / 10) * 100)
            return max(0, score)
        except Exception as e:
            self.logger.debug(f"Noise measurement failed: {e}")
            return 50.0

    def _measure_sharpness(self, img) -> float:
        """Measure sharpness via Tenengrad metric.

        Higher = sharper image.
        """
        try:
            import cv2
            import numpy as np

            gray = np.array(img.convert("L"), dtype=np.uint8)

            # Compute Sobel derivatives
            gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)

            # Tenengrad = sum(gx^2 + gy^2)
            g = (gx**2 + gy**2) ** 0.5
            sharpness = np.mean(g)

            # Normalize (empirically, good scans ~50-100)
            score = min(100, (sharpness / 2))
            return max(0, score)
        except Exception as e:
            self.logger.debug(f"Sharpness measurement failed: {e}")
            return 50.0

    def _measure_brightness(self, img) -> float:
        """Measure brightness (0=too dark, 50=optimal, 100=too bright).

        Optimal brightness is ~128 (mid-gray). Penalize extremes.
        """
        try:
            import numpy as np

            gray = np.array(img.convert("L"), dtype=np.float32)
            mean_brightness = gray.mean()

            # Normalize to 0-100 scale
            return mean_brightness / 255 * 100
        except Exception as e:
            self.logger.debug(f"Brightness measurement failed: {e}")
            return 50.0

    def _measure_skew(self, img_bytes: bytes) -> float:
        """Estimate skew angle in degrees.

        Uses Hough transform to detect dominant text lines.
        Returns angle in degrees (0 = not skewed).
        """
        try:
            import cv2
            import numpy as np
            from PIL import Image
            import io

            img = Image.open(io.BytesIO(img_bytes)).convert("L")
            gray = np.array(img, dtype=np.uint8)

            # Edge detection
            edges = cv2.Canny(gray, 50, 150)

            # Hough line transform to find dominant angle
            lines = cv2.HoughLines(edges, 1, np.pi / 180, 100)

            if lines is None or len(lines) == 0:
                return 0.0

            # Extract angles from lines
            angles = [line[0][1] for line in lines]

            # Find dominant angle (mode)
            if angles:
                # Quantize to bins and find most common
                angle_bins = np.histogram(
                    [a * 180 / np.pi for a in angles], bins=36, range=(0, 180)
                )
                dominant_bin = np.argmax(angle_bins[0])
                dominant_angle = dominant_bin * 5  # 5 degrees per bin

                # Normalize to -45 to 45 (text can be rotated either way)
                if dominant_angle > 90:
                    dominant_angle = 180 - dominant_angle

                return abs(dominant_angle)
            return 0.0

        except Exception as e:
            self.logger.debug(f"Skew measurement failed: {e}")
            return 0.0

    def _neutral_metrics(self) -> QualityMetrics:
        """Return neutral metrics (assume medium quality)."""
        return QualityMetrics(
            contrast_ratio=50.0,
            edge_definition=50.0,
            noise_level=50.0,
            sharpness=50.0,
            brightness=50.0,
            skew_angle=0.0,
            overall_score=50.0,
        )


def adaptive_preprocessing_recommendation(
    img_bytes: bytes, force_method: str = "auto"
) -> PreprocessingRecommendation:
    """Quick API: score image and get preprocessing recommendation."""
    scorer = ImageQualityScorer()
    metrics = scorer.score(img_bytes)
    return metrics.recommendation


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print("Usage: python -m pdf_extractor.features._quality_scorer <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]

    try:
        with open(image_path, "rb") as f:
            img_bytes = f.read()
    except Exception as e:
        print(f"Error reading image: {e}")
        sys.exit(1)

    scorer = ImageQualityScorer()
    metrics = scorer.score(img_bytes)

    print("\n" + "=" * 70)
    print("IMAGE QUALITY ANALYSIS")
    print("=" * 70)
    print(f"Contrast ratio: {metrics.contrast_ratio:.1f}/100")
    print(f"Edge definition: {metrics.edge_definition:.1f}/100")
    print(f"Noise level: {metrics.noise_level:.1f}/100 (lower = better)")
    print(f"Sharpness: {metrics.sharpness:.1f}/100")
    print(f"Brightness: {metrics.brightness:.1f}/100 (optimal = 50)")
    print(f"Skew angle: {metrics.skew_angle:.1f}°")
    print(f"\nOverall quality: {metrics.overall_score:.1f}/100")
    print(f"Quality tier: {'HIGH' if metrics.is_high_quality else 'LOW' if metrics.is_low_quality else 'MEDIUM'}")
    print(f"Recommendation: {metrics.recommendation.value}")
    print("=" * 70 + "\n")
