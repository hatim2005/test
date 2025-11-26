"""Color CV Library - Computer Vision Algorithms for Color Correction"""

from .aruco_detector import ArucoDetector, CardDetectionResult, CardOrientation, PatchROI
from .white_balance import WhiteBalancer, WhiteBalanceMethod
from .ccm import ColorCorrectionMatrix
from .delta_e import DeltaECalculator

__version__ = "1.0.0"
__all__ = [
    "ArucoDetector",
    "CardDetectionResult",
    "CardOrientation",
    "PatchROI",
    "WhiteBalancer",
    "WhiteBalanceMethod",
    "ColorCorrectionMatrix",
    "DeltaECalculator",
]
