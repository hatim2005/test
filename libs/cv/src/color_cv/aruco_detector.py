"""ArUco Marker-Based Color Card Detector

Detects color calibration cards using 4 corner ArUco markers (IDs 0-3).
Provides perspective correction and color patch extraction.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple
from enum import Enum
import numpy as np
import cv2


class CardOrientation(Enum):
    """Card rotation state"""
    NORMAL = 0
    ROTATED_90 = 1
    ROTATED_180 = 2
    ROTATED_270 = 3


@dataclass
class PatchROI:
    """Single color patch region of interest"""
    patch_id: int
    center: Tuple[int, int]
    bbox: Tuple[int, int, int, int]  # x, y, w, h
    mean_rgb: np.ndarray
    std_dev: float
    is_specular: bool


@dataclass
class CardDetectionResult:
    """Complete card detection output"""
    corners: np.ndarray
    orientation: CardOrientation
    patches: List[PatchROI]
    homography: np.ndarray
    confidence: float
    image_warped: np.ndarray


class ArucoDetector:
    """
    Detects color calibration cards using ArUco markers.
    Supports ColorChecker 24-patch grid with 4 corner markers.
    """
    
    ARUCO_DICT = cv2.aruco.DICT_5X5_50
    MARKER_IDS = [0, 1, 2, 3]  # TL, TR, BR, BL
    PATCH_GRID = (6, 4)  # 6 columns × 4 rows
    CARD_ASPECT_RATIO = 1.5
    
    def __init__(
        self,
        corner_refinement: bool = True,
        min_marker_size: int = 20,
        specular_threshold: float = 0.95
    ):
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(self.ARUCO_DICT)
        self.aruco_params = cv2.aruco.DetectorParameters()
        if corner_refinement:
            self.aruco_params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
        self.aruco_params.minMarkerPerimeterRate = min_marker_size / 1000.0
        self.specular_threshold = specular_threshold
    
    def detect(self, image: np.ndarray, extract_patches: bool = True) -> Optional[CardDetectionResult]:
        """Detect color card in image"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect ArUco markers
        corners_list, ids, _ = cv2.aruco.detectMarkers(
            gray, self.aruco_dict, parameters=self.aruco_params
        )
        
        if ids is None or len(ids) < 4:
            return None
        
        # Map marker IDs to corners
        marker_corners = {}
        for corner, marker_id in zip(corners_list, ids.flatten()):
            if marker_id in self.MARKER_IDS:
                marker_corners[marker_id] = corner[0]
        
        if len(marker_corners) < 4:
            return None
        
        # Order corners: TL, TR, BR, BL
        try:
            card_corners = np.float32([
                marker_corners[0].mean(axis=0),
                marker_corners[1].mean(axis=0),
                marker_corners[2].mean(axis=0),
                marker_corners[3].mean(axis=0),
            ])
        except KeyError:
            return None
        
        # Compute homography
        canonical_width = 600
        canonical_height = int(canonical_width / self.CARD_ASPECT_RATIO)
        dst_corners = np.float32([
            [0, 0],
            [canonical_width, 0],
            [canonical_width, canonical_height],
            [0, canonical_height]
        ])
        
        homography, _ = cv2.findHomography(card_corners, dst_corners, cv2.RANSAC)
        warped = cv2.warpPerspective(image, homography, (canonical_width, canonical_height))
        
        # Determine orientation
        orientation = self._infer_orientation(card_corners)
        
        # Extract patches
        patches = []
        if extract_patches:
            patches = self._extract_patches(warped)
        
        confidence = self._compute_confidence(marker_corners, image.shape)
        
        return CardDetectionResult(
            corners=card_corners,
            orientation=orientation,
            patches=patches,
            homography=homography,
            confidence=confidence,
            image_warped=warped
        )
    
    def _infer_orientation(self, corners: np.ndarray) -> CardOrientation:
        """Infer card rotation from corner positions"""
        center = corners.mean(axis=0)
        tl_to_center = corners[0] - center
        angle = np.arctan2(tl_to_center[1], tl_to_center[0])
        angle_deg = np.degrees(angle)
        
        if -45 <= angle_deg < 45:
            return CardOrientation.NORMAL
        elif 45 <= angle_deg < 135:
            return CardOrientation.ROTATED_90
        elif angle_deg >= 135 or angle_deg < -135:
            return CardOrientation.ROTATED_180
        else:
            return CardOrientation.ROTATED_270
    
    def _extract_patches(self, warped: np.ndarray) -> List[PatchROI]:
        """Extract color patches from warped card image"""
        patches = []
        h, w = warped.shape[:2]
        cols, rows = self.PATCH_GRID
        
        # Calculate patch grid with margins
        margin_x = w * 0.1
        margin_y = h * 0.15
        grid_w = w - 2 * margin_x
        grid_h = h - 2 * margin_y
        
        patch_w = grid_w / cols
        patch_h = grid_h / rows
        
        patch_id = 0
        for row in range(rows):
            for col in range(cols):
                x = int(margin_x + col * patch_w + patch_w * 0.2)
                y = int(margin_y + row * patch_h + patch_h * 0.2)
                w_patch = int(patch_w * 0.6)
                h_patch = int(patch_h * 0.6)
                
                roi = warped[y:y+h_patch, x:x+w_patch]
                mean_rgb = roi.mean(axis=(0, 1))
                std_dev = roi.std()
                
                # Check for specular highlights
                max_val = roi.max()
                is_specular = (max_val / 255.0) > self.specular_threshold
                
                patches.append(PatchROI(
                    patch_id=patch_id,
                    center=(x + w_patch//2, y + h_patch//2),
                    bbox=(x, y, w_patch, h_patch),
                    mean_rgb=mean_rgb,
                    std_dev=std_dev,
                    is_specular=is_specular
                ))
                patch_id += 1
        
        return patches
    
    def _compute_confidence(self, marker_corners: dict, image_shape: tuple) -> float:
        """Compute detection confidence score"""
        if len(marker_corners) < 4:
            return 0.0
        
        # Base confidence on number of markers and their size
        marker_count_score = len(marker_corners) / 4.0
        
        # Calculate average marker size
        marker_sizes = []
        for corners in marker_corners.values():
            w = np.linalg.norm(corners[0] - corners[1])
            h = np.linalg.norm(corners[1] - corners[2])
            marker_sizes.append((w + h) / 2)
        
        avg_size = np.mean(marker_sizes)
        image_size = min(image_shape[:2])
        size_ratio = avg_size / image_size
        
        # Ideal size ratio is 0.05-0.15
        if 0.05 <= size_ratio <= 0.15:
            size_score = 1.0
        else:
            size_score = max(0.5, 1.0 - abs(size_ratio - 0.1) * 5)
        
        return marker_count_score * size_score
