#!/usr/bin/env python3
"""
core/error_classifier.py — Error classification and intelligent fallback routing.

Analyzes exceptions from extraction methods and classifies them into actionable
categories: timeout, dependency missing, memory, network, corruption, etc.
Recommends fallback chains based on error type.

Phase 2.2: Universal Error Handling + Automatic Fallback Routing
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

logger = logging.getLogger(__name__)


class ErrorCategory(Enum):
    """Error classification for intelligent routing"""
    CORRUPT_INPUT = "corrupt_input"           # PDF is corrupted
    TIMEOUT = "timeout"                       # Method took too long
    DEPENDENCY_MISSING = "dependency_missing" # Library not installed
    MEMORY_ERROR = "memory_error"            # Out of memory
    NETWORK_ERROR = "network_error"          # Network unavailable (for cloud methods)
    ENCODING_ERROR = "encoding_error"        # Text encoding issue
    PERMISSION_ERROR = "permission_error"    # File permission denied
    RESOURCE_EXHAUSTED = "resource_exhausted" # GPU/CPU exhausted
    INVALID_OUTPUT = "invalid_output"        # Output quality check failed
    NOT_IMPLEMENTED = "not_implemented"      # Feature not available
    UNKNOWN = "unknown"                       # Unclassified


@dataclass
class ErrorAnalysis:
    """Detailed error analysis"""
    category: ErrorCategory
    message: str
    original_exception: Optional[Exception]
    is_recoverable: bool  # Can retry/fallback?
    is_critical: bool     # Fail entire batch?
    suggested_action: str  # What to do next
    fallback_priority: int  # 0=try immediately, higher=try later


class ErrorClassifier:
    """Classify extraction errors and suggest recovery strategies"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Pattern matching for common errors
        self.patterns = {
            ErrorCategory.TIMEOUT: [
                r"timeout",
                r"timed out",
                r"exceeded.*timeout",
                r"deadline exceeded",
            ],
            ErrorCategory.DEPENDENCY_MISSING: [
                r"ModuleNotFoundError",
                r"ImportError",
                r"cannot import",
                r"not installed",
                r"No module named",
            ],
            ErrorCategory.MEMORY_ERROR: [
                r"MemoryError",
                r"out of memory",
                r"cannot allocate memory",
                r"memory limit",
                r"RAM exhausted",
            ],
            ErrorCategory.NETWORK_ERROR: [
                r"network",
                r"connection",
                r"socket",
                r"unreachable",
                r"failed to resolve",
                r"no internet",
                r"offline",
            ],
            ErrorCategory.ENCODING_ERROR: [
                r"UnicodeDecodeError",
                r"encoding",
                r"decode",
                r"codec",
                r"invalid utf",
            ],
            ErrorCategory.PERMISSION_ERROR: [
                r"PermissionError",
                r"permission denied",
                r"access denied",
                r"not readable",
            ],
            ErrorCategory.CORRUPT_INPUT: [
                r"corrupt",
                r"invalid pdf",
                r"malformed",
                r"truncated",
                r"unreadable",
                r"broken stream",
            ],
            ErrorCategory.RESOURCE_EXHAUSTED: [
                r"CUDA out of memory",
                r"gpu memory",
                r"resource exhausted",
                r"no available device",
            ],
            ErrorCategory.INVALID_OUTPUT: [
                r"empty result",
                r"no pages",
                r"zero length",
                r"content validation failed",
            ],
        }

    def classify(
        self, exception: Exception, method_name: str, context: Optional[dict] = None
    ) -> ErrorAnalysis:
        """
        Classify an exception and return recovery strategy.

        Args:
            exception: The caught exception
            method_name: Name of the extraction method that failed
            context: Optional context (page number, etc)

        Returns:
            ErrorAnalysis with category, recovery action, fallback priority
        """
        exc_message = str(exception)
        exc_type = type(exception).__name__

        category = self._match_category(exc_message, exc_type)

        analysis = ErrorAnalysis(
            category=category,
            message=exc_message,
            original_exception=exception,
            is_recoverable=self._is_recoverable(category),
            is_critical=self._is_critical(category),
            suggested_action=self._suggest_action(category, method_name, context),
            fallback_priority=self._fallback_priority(category),
        )

        self.logger.warning(
            f"Error in {method_name}: {category.value} — {analysis.suggested_action}"
        )

        return analysis

    def _match_category(self, message: str, exc_type: str) -> ErrorCategory:
        """Find matching error category from patterns"""
        message_lower = message.lower()

        for category, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    return category

        return ErrorCategory.UNKNOWN

    def _is_recoverable(self, category: ErrorCategory) -> bool:
        """Can we recover from this error?"""
        NOT_RECOVERABLE = {
            ErrorCategory.PERMISSION_ERROR,  # File permission won't change
            ErrorCategory.DEPENDENCY_MISSING,  # Can't install during extraction
            ErrorCategory.NOT_IMPLEMENTED,  # Feature doesn't exist
        }
        return category not in NOT_RECOVERABLE

    def _is_critical(self, category: ErrorCategory) -> bool:
        """Should this error stop the entire batch?"""
        CRITICAL_ERRORS = {
            ErrorCategory.PERMISSION_ERROR,  # Can't read file
            # Others are recoverable via fallback
        }
        return category in CRITICAL_ERRORS

    def _suggest_action(
        self, category: ErrorCategory, method_name: str, context: Optional[dict] = None
    ) -> str:
        """Suggest recovery action based on error type"""
        page_info = f" (page {context.get('page_number')})" if context else ""

        suggestions = {
            ErrorCategory.TIMEOUT: f"Method {method_name} timed out{page_info}. Try fallback with longer timeout.",
            ErrorCategory.DEPENDENCY_MISSING: f"Required library missing for {method_name}. Install dependencies or use fallback.",
            ErrorCategory.MEMORY_ERROR: f"Memory exhausted in {method_name}{page_info}. Try chunked processing or skip large PDFs.",
            ErrorCategory.NETWORK_ERROR: f"Network unavailable for {method_name}. Use offline mode or try local fallback.",
            ErrorCategory.ENCODING_ERROR: f"Text encoding issue in {method_name}{page_info}. Try alternative text extraction.",
            ErrorCategory.PERMISSION_ERROR: f"File permission denied for {method_name}. Check file access.",
            ErrorCategory.CORRUPT_INPUT: f"Corrupt PDF detected in {method_name}{page_info}. Use more robust fallback.",
            ErrorCategory.RESOURCE_EXHAUSTED: f"GPU/CPU exhausted in {method_name}. Try CPU-only fallback or reduce batch size.",
            ErrorCategory.INVALID_OUTPUT: f"Output validation failed in {method_name}{page_info}. Retry with different method.",
            ErrorCategory.NOT_IMPLEMENTED: f"Feature not available in {method_name}. Use alternative method.",
            ErrorCategory.UNKNOWN: f"Unknown error in {method_name}. Check logs and try fallback.",
        }

        return suggestions.get(category, f"Error in {method_name}. Try fallback method.")

    def _fallback_priority(self, category: ErrorCategory) -> int:
        """Priority for trying fallback (0=highest, 10=lowest)"""
        priorities = {
            ErrorCategory.TIMEOUT: 0,            # Try immediately (just slower)
            ErrorCategory.INVALID_OUTPUT: 0,     # Might work with different params
            ErrorCategory.CORRUPT_INPUT: 1,      # Fallback might handle better
            ErrorCategory.ENCODING_ERROR: 1,     # Switch text extractor
            ErrorCategory.DEPENDENCY_MISSING: 5, # Can't fix, skip this tier
            ErrorCategory.PERMISSION_ERROR: 10,  # Fatal, don't retry
            ErrorCategory.MEMORY_ERROR: 3,       # Skip large pages
            ErrorCategory.NETWORK_ERROR: 2,      # Try offline/local
            ErrorCategory.RESOURCE_EXHAUSTED: 4, # Reduce batch size
            ErrorCategory.NOT_IMPLEMENTED: 6,    # Not available
            ErrorCategory.UNKNOWN: 7,            # Unclear, be cautious
        }

        return priorities.get(category, 5)

    def should_retry(self, analysis: ErrorAnalysis) -> bool:
        """Should we retry this method with different params?"""
        return (
            analysis.is_recoverable
            and not analysis.is_critical
            and analysis.fallback_priority < 5
        )

    def should_try_fallback(self, analysis: ErrorAnalysis) -> bool:
        """Should we try a fallback method?"""
        return analysis.is_recoverable and analysis.fallback_priority < 10


class FallbackRouter:
    """Route extraction attempts through fallback chains"""

    def __init__(self, registry):
        """
        Initialize router with strategy registry.

        Args:
            registry: Strategy registry for looking up fallback chains
        """
        self.registry = registry
        self.logger = logging.getLogger(__name__)

        # Define fallback chains by tier
        # If a method in tier X fails, try the next method in same tier
        self.tier_fallbacks = {
            "text": ["text:fast", "text:pdfminer", "text:tika", "text:docling"],
            "ocr": ["ocr:tesseract-basic", "ocr:tesseract-advanced", "ocr:easyocr", "ocr:img2table"],
            "tables": ["tables:pdfplumber", "tables:camelot", "tables:tabula", "tables:img2table"],
            "layout": ["pdf:structure", "text:docling"],
        }

    def get_fallback_chain(self, failed_method: str) -> List[str]:
        """
        Get fallback chain for a failed method.

        Examples:
            failed: "text:fast" → ["text:pdfminer", "text:tika", "text:docling"]
            failed: "ocr:tesseract-basic" → ["ocr:tesseract-advanced", "ocr:easyocr"]

        Args:
            failed_method: Name of method that failed

        Returns:
            List of fallback methods to try, in order
        """
        # Determine tier from method name
        tier = failed_method.split(":")[0] if ":" in failed_method else failed_method

        if tier not in self.tier_fallbacks:
            self.logger.warning(f"No fallback chain defined for tier: {tier}")
            return []

        # Get chain and remove the failed method
        chain = self.tier_fallbacks[tier]
        try:
            idx = chain.index(failed_method)
            # Return methods after the failed one
            return chain[idx + 1 :]
        except ValueError:
            # Method not in chain, return full chain minus first (whatever it is)
            return chain[1:]

    def should_cross_tier(
        self, failed_method: str, analysis: ErrorAnalysis
    ) -> bool:
        """
        Should we try a different tier after same-tier fallback fails?

        Generally only for severe errors (corruption, dependency).
        """
        severe_errors = {
            ErrorCategory.CORRUPT_INPUT,
            ErrorCategory.DEPENDENCY_MISSING,
            ErrorCategory.INVALID_OUTPUT,
        }

        return analysis.category in severe_errors

    def get_cross_tier_fallback(self, failed_method: str) -> List[str]:
        """
        Get fallbacks from adjacent tiers.

        Example:
            failed: "text:fast" (text tier)
            → try: ocr:tesseract-basic, tables:pdfplumber (adjacent tiers)
        """
        tier = failed_method.split(":")[0] if ":" in failed_method else failed_method

        # Define cross-tier fallbacks
        cross_tier = {
            "text": ["ocr", "layout"],
            "ocr": ["text", "layout"],
            "tables": ["layout", "text"],
            "layout": ["text", "ocr", "tables"],
        }

        adjacent_tiers = cross_tier.get(tier, [])
        fallbacks = []

        for adjacent_tier in adjacent_tiers:
            if adjacent_tier in self.tier_fallbacks:
                # Add first method from adjacent tier
                fallbacks.append(self.tier_fallbacks[adjacent_tier][0])

        return fallbacks


def classify_error(
    exception: Exception, method_name: str, context: Optional[dict] = None
) -> ErrorAnalysis:
    """Convenience function to classify a single error"""
    classifier = ErrorClassifier()
    return classifier.classify(exception, method_name, context)
