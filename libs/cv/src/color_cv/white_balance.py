"""White balance algorithms for color correction."""

import numpy as np
import cv2
from typing import Optional, Tuple
from enum import Enum


class WhiteBalanceMethod(Enum):
    """Available white balance methods."""
    GRAY_WORLD = 'gray_world'
    WHITE_PATCH = 'white_patch'
    LEARNING_BASED = 'learning_based'


class WhiteBalancer:
    """White balance correction using multiple algorithms.
    
    Attributes:
        method: Selected white balance method
    """
    
    def __init__(self, method: str = 'gray_world'):
        """Initialize white balancer.
        
        Args:
            method: White balance method ('gray_world', 'white_patch', 'learning_based')
        """
        self.method = WhiteBalanceMethod(method)
    
    def balance(self, image: np.ndarray, reference: Optional[np.ndarray] = None) -> np.ndarray:
        """Apply white balance to image.
        
        Args:
            image: Input image (RGB format)
            reference: Optional reference patch for color calibration
            
        Returns:
            White balanced image
        """
        if self.method == WhiteBalanceMethod.GRAY_WORLD:
            return self._gray_world(image)
        elif self.method == WhiteBalanceMethod.WHITE_PATCH:
            return self._white_patch(image)
        elif self.method == WhiteBalanceMethod.LEARNING_BASED:
            return self._learning_based(image, reference)
        else:
            raise ValueError(f"Unknown method: {self.method}")
    
    def _gray_world(self, image: np.ndarray) -> np.ndarray:
        """Gray world white balance assumption.
        
        Assumes average color in image should be gray.
        
        Args:
            image: Input RGB image
            
        Returns:
            Balanced image
        """
        # Convert to float
        img_float = image.astype(np.float32)
        
        # Calculate average for each channel
        avg_r = np.mean(img_float[:, :, 0])
        avg_g = np.mean(img_float[:, :, 1])
        avg_b = np.mean(img_float[:, :, 2])
        
        # Calculate gray (average of all channels)
        gray = (avg_r + avg_g + avg_b) / 3.0
        
        # Calculate scaling factors
        scale_r = gray / avg_r if avg_r > 0 else 1.0
        scale_g = gray / avg_g if avg_g > 0 else 1.0
        scale_b = gray / avg_b if avg_b > 0 else 1.0
        
        # Apply scaling
        balanced = img_float.copy()
        balanced[:, :, 0] *= scale_r
        balanced[:, :, 1] *= scale_g
        balanced[:, :, 2] *= scale_b
        
        # Clip and convert back
        balanced = np.clip(balanced, 0, 255).astype(np.uint8)
        
        return balanced
    
    def _white_patch(self, image: np.ndarray) -> np.ndarray:
        """White patch (max RGB) white balance.
        
        Assumes brightest point in image should be white.
        
        Args:
            image: Input RGB image
            
        Returns:
            Balanced image
        """
        img_float = image.astype(np.float32)
        
        # Find maximum values for each channel
        max_r = np.percentile(img_float[:, :, 0], 99)  # Use 99th percentile to avoid outliers
        max_g = np.percentile(img_float[:, :, 1], 99)
        max_b = np.percentile(img_float[:, :, 2], 99)
        
        # Calculate scaling factors
        scale_r = 255.0 / max_r if max_r > 0 else 1.0
        scale_g = 255.0 / max_g if max_g > 0 else 1.0
        scale_b = 255.0 / max_b if max_b > 0 else 1.0
        
        # Apply scaling
        balanced = img_float.copy()
        balanced[:, :, 0] *= scale_r
        balanced[:, :, 1] *= scale_g
        balanced[:, :, 2] *= scale_b
        
        # Clip and convert
        balanced = np.clip(balanced, 0, 255).astype(np.uint8)
        
        return balanced
    
    def _learning_based(self, image: np.ndarray, reference: Optional[np.ndarray] = None) -> np.ndarray:
        """Learning-based white balance using reference patch.
        
        Uses color constancy with reference gray card.
        
        Args:
            image: Input RGB image
            reference: Reference color patch (should be neutral gray)
            
        Returns:
            Balanced image
        """
        if reference is None:
            # Fall back to gray world if no reference
            return self._gray_world(image)
        
        # Calculate average color of reference patch
        ref_avg = np.mean(reference, axis=(0, 1))
        
        # Expected gray value (mid-gray = 128)
        target_gray = 128.0
        
        # Calculate gains
        gain_r = target_gray / ref_avg[0] if ref_avg[0] > 0 else 1.0
        gain_g = target_gray / ref_avg[1] if ref_avg[1] > 0 else 1.0
        gain_b = target_gray / ref_avg[2] if ref_avg[2] > 0 else 1.0
        
        # Apply gains
        img_float = image.astype(np.float32)
        balanced = img_float.copy()
        balanced[:, :, 0] *= gain_r
        balanced[:, :, 1] *= gain_g
        balanced[:, :, 2] *= gain_b
        
        # Clip and convert
        balanced = np.clip(balanced, 0, 255).astype(np.uint8)
        
        return balanced
    
    def estimate_illuminant(self, image: np.ndarray) -> Tuple[float, float, float]:
        """Estimate scene illuminant color.
        
        Args:
            image: Input RGB image
            
        Returns:
            Tuple of (R, G, B) illuminant estimates
        """
        img_float = image.astype(np.float32)
        
        if self.method == WhiteBalanceMethod.GRAY_WORLD:
            # Illuminant is average color
            return tuple(np.mean(img_float, axis=(0, 1)))
        
        elif self.method == WhiteBalanceMethod.WHITE_PATCH:
            # Illuminant is brightest color
            return tuple(np.percentile(img_float, 99, axis=(0, 1)))
        
        else:
            # Default to gray world
            return tuple(np.mean(img_float, axis=(0, 1)))
