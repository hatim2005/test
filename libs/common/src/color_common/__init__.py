"""
Color Common Library - Shared types, constants, and utilities.

This package provides shared data structures, type definitions, and constants
used across the Color Correction System monorepo.
"""

from .types import (
    ProcessingMode,
    ColorSpace,
    DetectionResult,
    CorrectionParams,
    CorrectionResult,
    ImageMetadata,
    JobStatus,
    AccuracyLevel
)

from .constants import (
    COLORCHECKER_24_LAB,
    COLORCHECKER_24_SRGB,
    ARUCO_DICT,
    ARUCO_IDS,
    DELTA_E_THRESHOLDS,
    EXTENDED_SKIN_TONES_LAB,
    EXTENDED_TEXTILES_LAB
)

from .errors import (
    ColorCorrectionError,
    DetectionError,
    ProcessingError,
    ValidationError
)

__version__ = "0.1.0"
__all__ = [
    "ProcessingMode",
    "ColorSpace",
    "DetectionResult",
    "CorrectionParams",
    "CorrectionResult",
    "ImageMetadata",
    "JobStatus",
    "AccuracyLevel",
    "COLORCHECKER_24_LAB",
    "COLORCHECKER_24_SRGB",
    "ARUCO_DICT",
    "ARUCO_IDS",
    "DELTA_E_THRESHOLDS",
    "EXTENDED_SKIN_TONES_LAB",
    "EXTENDED_TEXTILES_LAB",
    "ColorCorrectionError",
    "DetectionError",
    "ProcessingError",
    "ValidationError",
]
