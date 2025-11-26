"""Color Correction Matrix (CCM) calculation and application."""

import numpy as np
from typing import Optional, Tuple
import cv2


class ColorCorrectionMatrix:
    """Color correction matrix for chromatic adaptation.
    
    Attributes:
        matrix: 3x3 color correction matrix
    """
    
    def __init__(self):
        """Initialize with identity matrix."""
        self.matrix = np.eye(3, dtype=np.float32)
    
    def calculate_from_reference(
        self,
        reference_patch: np.ndarray,
        target_colors: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """Calculate CCM from reference color patch.
        
        Args:
            reference_patch: Measured colors from reference chart (Nx3 array)
            target_colors: Known/ideal colors for reference chart (Nx3 array)
                          If None, uses standard ColorChecker values
        
        Returns:
            3x3 color correction matrix
        """
        if target_colors is None:
            # Use standard Macbeth ColorChecker values (first 24 patches)
            target_colors = self._get_colorchecker_values()
        
        # Reshape if needed
        if reference_patch.ndim == 3:
            # Average colors in patch
            reference_patch = np.mean(reference_patch, axis=(0, 1))
        
        # Ensure we have enough samples
        if reference_patch.shape[0] < 3:
            raise ValueError("Need at least 3 color samples for CCM calculation")
        
        # Solve least squares: target = matrix @ reference
        # matrix = target @ reference.T @ (reference @ reference.T)^-1
        ref_colors = reference_patch.T  # 3xN
        tgt_colors = target_colors[:reference_patch.shape[0]].T  # 3xN
        
        # Compute pseudo-inverse solution
        self.matrix = tgt_colors @ np.linalg.pinv(ref_colors)
        
        return self.matrix
    
    def calculate_from_illuminants(
        self,
        source_illuminant: Tuple[float, float, float],
        target_illuminant: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    ) -> np.ndarray:
        """Calculate CCM for chromatic adaptation between illuminants.
        
        Uses Bradford chromatic adaptation transform.
        
        Args:
            source_illuminant: Source illuminant RGB values
            target_illuminant: Target illuminant RGB values (default: D65)
        
        Returns:
            3x3 color correction matrix
        """
        # Bradford cone response matrix
        bradford = np.array([
            [ 0.8951,  0.2664, -0.1614],
            [-0.7502,  1.7135,  0.0367],
            [ 0.0389, -0.0685,  1.0296]
        ], dtype=np.float32)
        
        bradford_inv = np.linalg.inv(bradford)
        
        # Convert illuminants to cone response domain
        source_cone = bradford @ np.array(source_illuminant, dtype=np.float32)
        target_cone = bradford @ np.array(target_illuminant, dtype=np.float32)
        
        # Diagonal scaling matrix
        scale = np.diag(target_cone / source_cone)
        
        # Complete transform
        self.matrix = bradford_inv @ scale @ bradford
        
        return self.matrix
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        """Apply color correction matrix to image.
        
        Args:
            image: Input RGB image
        
        Returns:
            Color corrected image
        """
        # Convert to float
        img_float = image.astype(np.float32)
        
        # Reshape for matrix multiplication
        h, w, c = img_float.shape
        pixels = img_float.reshape(-1, 3).T  # 3xN
        
        # Apply matrix
        corrected = self.matrix @ pixels
        
        # Reshape back
        corrected = corrected.T.reshape(h, w, c)
        
        # Clip and convert
        corrected = np.clip(corrected, 0, 255).astype(np.uint8)
        
        return corrected
    
    def set_matrix(self, matrix: np.ndarray):
        """Set custom CCM matrix.
        
        Args:
            matrix: 3x3 color correction matrix
        """
        if matrix.shape != (3, 3):
            raise ValueError("Matrix must be 3x3")
        self.matrix = matrix.astype(np.float32)
    
    def get_matrix(self) -> np.ndarray:
        """Get current CCM matrix.
        
        Returns:
            Current 3x3 matrix
        """
        return self.matrix.copy()
    
    @staticmethod
    def _get_colorchecker_values() -> np.ndarray:
        """Get standard Macbeth ColorChecker RGB values under D65.
        
        Returns:
            24x3 array of reference RGB values
        """
        # Standard ColorChecker patch values (sRGB under D65 illuminant)
        # Values from X-Rite ColorChecker specification
        colorchecker = np.array([
            [115,  82,  68],  # Dark skin
            [194, 150, 130],  # Light skin
            [ 98, 122, 157],  # Blue sky
            [ 87, 108,  67],  # Foliage
            [133, 128, 177],  # Blue flower
            [103, 189, 170],  # Bluish green
            [214, 126,  44],  # Orange
            [ 80,  91, 166],  # Purplish blue
            [193,  90,  99],  # Moderate red
            [ 94,  60, 108],  # Purple
            [157, 188,  64],  # Yellow green
            [224, 163,  46],  # Orange yellow
            [ 56,  61, 150],  # Blue
            [ 70, 148,  73],  # Green
            [175,  54,  60],  # Red
            [231, 199,  31],  # Yellow
            [187,  86, 149],  # Magenta
            [  8, 133, 161],  # Cyan
            [243, 243, 242],  # White
            [200, 200, 200],  # Neutral 8
            [160, 160, 160],  # Neutral 6.5
            [122, 122, 121],  # Neutral 5
            [ 85,  85,  85],  # Neutral 3.5
            [ 52,  52,  52],  # Black
        ], dtype=np.float32)
        
        return colorchecker
    
    def calculate_accuracy(
        self,
        measured: np.ndarray,
        reference: Optional[np.ndarray] = None
    ) -> dict:
        """Calculate color accuracy metrics after correction.
        
        Args:
            measured: Measured colors after correction
            reference: Reference/target colors
        
        Returns:
            Dictionary with accuracy metrics
        """
        if reference is None:
            reference = self._get_colorchecker_values()
        
        # Calculate color differences
        delta_rgb = measured - reference[:measured.shape[0]]
        
        # Mean absolute error per channel
        mae_r = np.mean(np.abs(delta_rgb[:, 0]))
        mae_g = np.mean(np.abs(delta_rgb[:, 1]))
        mae_b = np.mean(np.abs(delta_rgb[:, 2]))
        
        # Root mean squared error
        rmse = np.sqrt(np.mean(delta_rgb ** 2))
        
        # Maximum error
        max_error = np.max(np.abs(delta_rgb))
        
        return {
            'mae_r': float(mae_r),
            'mae_g': float(mae_g),
            'mae_b': float(mae_b),
            'rmse': float(rmse),
            'max_error': float(max_error)
        }
