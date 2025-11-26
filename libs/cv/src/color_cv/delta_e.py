"""Delta E (ΔE) color difference calculations."""

import numpy as np
from typing import Union, Tuple
import cv2


class DeltaECalculator:
    """Calculate color differences using various Delta E formulas.
    
    Implements CIE76, CIE94, and CIEDE2000 color difference calculations.
    """
    
    def __init__(self, method: str = 'ciede2000'):
        """Initialize calculator.
        
        Args:
            method: Calculation method ('cie76', 'cie94', 'ciede2000')
        """
        self.method = method.lower()
    
    def calculate(self, color1: np.ndarray, color2: np.ndarray) -> float:
        """Calculate Delta E between two colors.
        
        Args:
            color1: First color in RGB format (0-255)
            color2: Second color in RGB format (0-255)
        
        Returns:
            Delta E value (perceptual color difference)
        """
        # Convert RGB to LAB
        lab1 = self._rgb_to_lab(color1)
        lab2 = self._rgb_to_lab(color2)
        
        if self.method == 'cie76':
            return self._delta_e_76(lab1, lab2)
        elif self.method == 'cie94':
            return self._delta_e_94(lab1, lab2)
        elif self.method == 'ciede2000':
            return self._delta_e_2000(lab1, lab2)
        else:
            raise ValueError(f"Unknown method: {self.method}")
    
    def calculate_average(
        self,
        image1: np.ndarray,
        image2: np.ndarray
    ) -> float:
        """Calculate average Delta E across two images.
        
        Args:
            image1: First image
            image2: Second image
        
        Returns:
            Average Delta E value
        """
        if image1.shape != image2.shape:
            raise ValueError("Images must have same dimensions")
        
        # Calculate per-pixel Delta E
        h, w = image1.shape[:2]
        delta_e_sum = 0.0
        
        # Sample every 10th pixel for efficiency
        sample_step = max(1, min(h, w) // 100)
        count = 0
        
        for i in range(0, h, sample_step):
            for j in range(0, w, sample_step):
                de = self.calculate(image1[i, j], image2[i, j])
                delta_e_sum += de
                count += 1
        
        return delta_e_sum / count if count > 0 else 0.0
    
    def _rgb_to_lab(self, rgb: np.ndarray) -> np.ndarray:
        """Convert RGB to CIELAB color space.
        
        Args:
            rgb: RGB color (0-255)
        
        Returns:
            LAB color (L: 0-100, a/b: -128 to 127)
        """
        # Normalize RGB
        rgb_norm = rgb.astype(np.float32) / 255.0
        
        # sRGB to linear RGB
        def srgb_to_linear(c):
            return np.where(
                c <= 0.04045,
                c / 12.92,
                ((c + 0.055) / 1.055) ** 2.4
            )
        
        r, g, b = srgb_to_linear(rgb_norm[0]), srgb_to_linear(rgb_norm[1]), srgb_to_linear(rgb_norm[2])
        
        # RGB to XYZ (D65 illuminant)
        x = r * 0.4124564 + g * 0.3575761 + b * 0.1804375
        y = r * 0.2126729 + g * 0.7151522 + b * 0.0721750
        z = r * 0.0193339 + g * 0.1191920 + b * 0.9503041
        
        # Normalize by D65 white point
        x = x / 0.95047
        y = y / 1.00000
        z = z / 1.08883
        
        # XYZ to LAB
        def f(t):
            delta = 6.0 / 29.0
            return np.where(
                t > delta ** 3,
                t ** (1.0 / 3.0),
                t / (3 * delta ** 2) + (4.0 / 29.0)
            )
        
        fx = f(x)
        fy = f(y)
        fz = f(z)
        
        L = 116.0 * fy - 16.0
        a = 500.0 * (fx - fy)
        b_val = 200.0 * (fy - fz)
        
        return np.array([L, a, b_val], dtype=np.float32)
    
    def _delta_e_76(self, lab1: np.ndarray, lab2: np.ndarray) -> float:
        """Calculate CIE76 Delta E (simple Euclidean distance).
        
        Args:
            lab1: First LAB color
            lab2: Second LAB color
        
        Returns:
            Delta E value
        """
        diff = lab1 - lab2
        return float(np.sqrt(np.sum(diff ** 2)))
    
    def _delta_e_94(self, lab1: np.ndarray, lab2: np.ndarray) -> float:
        """Calculate CIE94 Delta E.
        
        Args:
            lab1: First LAB color
            lab2: Second LAB color
        
        Returns:
            Delta E value
        """
        L1, a1, b1 = lab1
        L2, a2, b2 = lab2
        
        dL = L1 - L2
        C1 = np.sqrt(a1**2 + b1**2)
        C2 = np.sqrt(a2**2 + b2**2)
        dC = C1 - C2
        da = a1 - a2
        db = b1 - b2
        dH = np.sqrt(max(0, da**2 + db**2 - dC**2))
        
        # Weighting factors for graphic arts
        kL = 1.0
        K1 = 0.045
        K2 = 0.015
        
        SL = 1.0
        SC = 1.0 + K1 * C1
        SH = 1.0 + K2 * C1
        
        dE94 = np.sqrt(
            (dL / (kL * SL))**2 +
            (dC / SC)**2 +
            (dH / SH)**2
        )
        
        return float(dE94)
    
    def _delta_e_2000(self, lab1: np.ndarray, lab2: np.ndarray) -> float:
        """Calculate CIEDE2000 Delta E (most perceptually uniform).
        
        Args:
            lab1: First LAB color
            lab2: Second LAB color
        
        Returns:
            Delta E 2000 value
        """
        L1, a1, b1 = lab1
        L2, a2, b2 = lab2
        
        # Calculate C and h
        C1 = np.sqrt(a1**2 + b1**2)
        C2 = np.sqrt(a2**2 + b2**2)
        
        C_bar = (C1 + C2) / 2.0
        
        # Calculate G
        G = 0.5 * (1 - np.sqrt(C_bar**7 / (C_bar**7 + 25**7)))
        
        # Calculate a'
        a1_prime = (1 + G) * a1
        a2_prime = (1 + G) * a2
        
        # Calculate C'
        C1_prime = np.sqrt(a1_prime**2 + b1**2)
        C2_prime = np.sqrt(a2_prime**2 + b2**2)
        
        # Calculate h'
        h1_prime = np.arctan2(b1, a1_prime) % (2 * np.pi)
        h2_prime = np.arctan2(b2, a2_prime) % (2 * np.pi)
        
        # Convert to degrees
        h1_prime = np.degrees(h1_prime)
        h2_prime = np.degrees(h2_prime)
        
        # Calculate differences
        dL_prime = L2 - L1
        dC_prime = C2_prime - C1_prime
        
        # Calculate dh'
        if C1_prime * C2_prime == 0:
            dh_prime = 0
        elif np.abs(h2_prime - h1_prime) <= 180:
            dh_prime = h2_prime - h1_prime
        elif h2_prime - h1_prime > 180:
            dh_prime = h2_prime - h1_prime - 360
        else:
            dh_prime = h2_prime - h1_prime + 360
        
        # Calculate dH'
        dH_prime = 2 * np.sqrt(C1_prime * C2_prime) * np.sin(np.radians(dh_prime / 2))
        
        # Calculate averages
        L_bar_prime = (L1 + L2) / 2.0
        C_bar_prime = (C1_prime + C2_prime) / 2.0
        
        # Calculate h_bar'
        if C1_prime * C2_prime == 0:
            h_bar_prime = h1_prime + h2_prime
        elif np.abs(h1_prime - h2_prime) <= 180:
            h_bar_prime = (h1_prime + h2_prime) / 2.0
        elif h1_prime + h2_prime < 360:
            h_bar_prime = (h1_prime + h2_prime + 360) / 2.0
        else:
            h_bar_prime = (h1_prime + h2_prime - 360) / 2.0
        
        # Calculate T
        T = (1 - 0.17 * np.cos(np.radians(h_bar_prime - 30)) +
             0.24 * np.cos(np.radians(2 * h_bar_prime)) +
             0.32 * np.cos(np.radians(3 * h_bar_prime + 6)) -
             0.20 * np.cos(np.radians(4 * h_bar_prime - 63)))
        
        # Calculate SL, SC, SH
        SL = 1 + (0.015 * (L_bar_prime - 50)**2) / np.sqrt(20 + (L_bar_prime - 50)**2)
        SC = 1 + 0.045 * C_bar_prime
        SH = 1 + 0.015 * C_bar_prime * T
        
        # Calculate RT
        dTheta = 30 * np.exp(-((h_bar_prime - 275) / 25)**2)
        RC = 2 * np.sqrt(C_bar_prime**7 / (C_bar_prime**7 + 25**7))
        RT = -np.sin(np.radians(2 * dTheta)) * RC
        
        # Calculate final Delta E
        kL = kC = kH = 1.0
        
        dE00 = np.sqrt(
            (dL_prime / (kL * SL))**2 +
            (dC_prime / (kC * SC))**2 +
            (dH_prime / (kH * SH))**2 +
            RT * (dC_prime / (kC * SC)) * (dH_prime / (kH * SH))
        )
        
        return float(dE00)
