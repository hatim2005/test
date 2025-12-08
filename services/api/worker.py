"""Celery Worker for Background Task Processing

Handles batch image processing, color detection, and correction jobs.
"""

from celery import Celery, Task
from celery_config import celery_app
import logging
from typing import List, Dict, Optional
import time
import os
import cv2
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Get Celery app instance
app = celery_app

@app.task(name='worker.detect_color_card')
def detect_color_card(image_id: str, image_path: str) -> Dict:
    """Detect color card in image using ArUco markers."""
    start_time = time.time()
    
    try:
        # Import CV library
        from libs.cv.src.color_cv import ArucoDetector
        
        # Load image
        if not os.path.exists(image_path):
            return {
                'success': False,
                'image_id': image_id,
                'error': f'Image not found: {image_path}'
            }
        
        image = cv2.imread(image_path)
        if image is None:
            return {
                'success': False,
                'image_id': image_id,
                'error': 'Failed to load image'
            }
        
        # Detect color card
        detector = ArucoDetector(corner_refinement=True)
        result = detector.detect(image, extract_patches=True)
        
        if result is None:
            return {
                'success': False,
                'image_id': image_id,
                'error': 'No color card detected',
                'processing_time_ms': (time.time() - start_time) * 1000
            }
        
        # Convert patches to serializable format
        patches_data = []
        for patch in result.patches:
            patches_data.append({
                'patch_id': patch.patch_id,
                'center': patch.center,
                'bbox': patch.bbox,
                'mean_rgb': patch.mean_rgb.tolist(),
                'std_dev': float(patch.std_dev),
                'is_specular': patch.is_specular
            })
        
        return {
            'success': True,
            'image_id': image_id,
            'markers_found': 4,
            'card_orientation': result.orientation.name,
            'patches': patches_data,
            'patches_count': len(patches_data),
            'confidence': float(result.confidence),
            'processing_time_ms': (time.time() - start_time) * 1000
        }
        
    except Exception as e:
        logger.error(f"Error detecting color card for {image_id}: {str(e)}")
        return {
            'success': False,
            'image_id': image_id,
            'error': str(e),
            'processing_time_ms': (time.time() - start_time) * 1000
        }

@app.task(name='worker.correct_color')
def correct_color(image_id: str, image_path: str, detection_data: Dict, options: Optional[Dict] = None) -> Dict:
    """Apply color correction using detected color card."""
    start_time = time.time()
    options = options or {}
    
    try:
        from libs.cv.src.color_cv import WhiteBalancer, ColorCorrectionMatrix, DeltaECalculator
        
        image = cv2.imread(image_path)
        if image is None:
            return {'success': False, 'error': 'Failed to load image'}
        
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        wb_method = options.get('white_balance_method', 'gray_world')
        wb = WhiteBalancer(wb_method)
        balanced = wb.balance(image_rgb)
        
        # Extract reference patches
        reference_patches = []
        for patch_data in detection_data.get('patches', []):
            reference_patches.append(np.array(patch_data['mean_rgb']))
        
        if len(reference_patches) < 3:
            return {'success': False, 'error': 'Not enough patches for correction'}
        
        # Compute CCM
        ccm = ColorCorrectionMatrix()
        matrix = ccm.calculate_from_reference(np.array(reference_patches))
        corrected = ccm.apply(balanced)
        
        # Calculate Delta E
        delta_calc = DeltaECalculator('ciede2000')
        delta_e_values = []
        
        for patch_data in detection_data.get('patches', []):
            measured = np.array(patch_data['mean_rgb'])
            delta_e = delta_calc.calculate(measured, measured)
            delta_e_values.append(float(delta_e))
        
        # Save corrected image
        output_dir = 'outputs'
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{image_id}_corrected.png")
        
        corrected_bgr = cv2.cvtColor(corrected, cv2.COLOR_RGB2BGR)
        cv2.imwrite(output_path, corrected_bgr)
        
        return {
            'success': True,
            'image_id': image_id,
            'output_path': output_path,
            'ccm_matrix': matrix.tolist(),
            'processing_time_ms': (time.time() - start_time) * 1000
        }
        
    except Exception as e:
        logger.error(f"Error correcting color: {str(e)}")
        return {'success': False, 'error': str(e)}


if __name__ == '__main__':
    app.start()
