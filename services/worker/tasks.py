"""Celery worker tasks for batch color correction processing."""

import io
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import traceback

import cv2
import numpy as np
from celery import Celery, Task
from celery.exceptions import SoftTimeLimitExceeded
from PIL import Image
import rawpy

from color_cv import (
    ArucoDetector,
    WhiteBalancer,
    ColorCorrectionMatrix,
    DeltaECalculator
)
from color_ml import BackgroundRemover

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Celery
app = Celery(
    'color_correction_worker',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/1'
)

# Celery configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour hard limit
    task_soft_time_limit=3300,  # 55 minute soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)


class ColorCorrectionTask(Task):
    """Base task class with error handling and retry logic."""
    
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 3, 'countdown': 5}
    retry_backoff = True
    retry_backoff_max = 600
    retry_jitter = True


@app.task(base=ColorCorrectionTask, bind=True, name='tasks.process_image')
def process_image(
    self,
    image_data: bytes,
    config: Dict[str, Any],
    task_id: Optional[str] = None
) -> Dict[str, Any]:
    """Process a single image with color correction pipeline.
    
    Args:
        image_data: Raw image bytes
        config: Processing configuration dictionary
        task_id: Optional task identifier for tracking
        
    Returns:
        Dictionary containing processed image data and metadata
        
    Raises:
        SoftTimeLimitExceeded: If task exceeds soft time limit
    """
    try:
        logger.info(f"Processing image task {task_id or self.request.id}")
        
        # Update task state
        self.update_state(
            state='PROCESSING',
            meta={'stage': 'loading', 'progress': 10}
        )
        
        # Load image
        image = load_image(image_data, config.get('format', 'auto'))
        
        # Detect ArUco markers
        self.update_state(
            state='PROCESSING',
            meta={'stage': 'aruco_detection', 'progress': 20}
        )
        detector = ArucoDetector()
        markers = detector.detect(image)
        
        if not markers:
            logger.warning("No ArUco markers detected")
            reference_patch = None
        else:
            reference_patch = detector.extract_color_patch(
                image,
                markers[0]  # Use first detected marker
            )
        
        # White balance correction
        self.update_state(
            state='PROCESSING',
            meta={'stage': 'white_balance', 'progress': 40}
        )
        wb = WhiteBalancer(method=config.get('wb_method', 'gray_world'))
        balanced = wb.balance(image, reference_patch)
        
        # Color correction matrix
        self.update_state(
            state='PROCESSING',
            meta={'stage': 'color_correction', 'progress': 60}
        )
        ccm = ColorCorrectionMatrix()
        if reference_patch is not None:
            ccm.calculate_from_reference(reference_patch)
        corrected = ccm.apply(balanced)
        
        # Optional background removal
        if config.get('remove_background', False):
            self.update_state(
                state='PROCESSING',
                meta={'stage': 'background_removal', 'progress': 80}
            )
            bg_remover = BackgroundRemover()
            corrected = bg_remover.remove(corrected)
        
        # Calculate color accuracy metrics
        metrics = {}
        if reference_patch is not None:
            calc = DeltaECalculator()
            metrics['delta_e'] = calc.calculate_average(
                reference_patch,
                corrected
            )
        
        # Encode result
        self.update_state(
            state='PROCESSING',
            meta={'stage': 'encoding', 'progress': 90}
        )
        output_format = config.get('output_format', 'jpeg')
        result_data = encode_image(corrected, output_format)
        
        logger.info(f"Successfully processed image {task_id or self.request.id}")
        
        return {
            'status': 'success',
            'image_data': result_data,
            'markers_detected': len(markers),
            'metrics': metrics,
            'format': output_format
        }
        
    except SoftTimeLimitExceeded:
        logger.error(f"Task {task_id or self.request.id} exceeded time limit")
        raise
    except Exception as e:
        logger.error(
            f"Error processing image {task_id or self.request.id}: {str(e)}\n"
            f"{traceback.format_exc()}"
        )
        return {
            'status': 'error',
            'error': str(e),
            'traceback': traceback.format_exc()
        }


@app.task(base=ColorCorrectionTask, bind=True, name='tasks.batch_process')
def batch_process(
    self,
    image_batch: List[bytes],
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """Process multiple images in batch.
    
    Args:
        image_batch: List of raw image bytes
        config: Processing configuration dictionary
        
    Returns:
        Dictionary containing batch processing results
    """
    try:
        logger.info(f"Starting batch processing of {len(image_batch)} images")
        
        results = []
        total = len(image_batch)
        
        for idx, image_data in enumerate(image_batch):
            self.update_state(
                state='PROCESSING',
                meta={
                    'current': idx + 1,
                    'total': total,
                    'progress': int((idx / total) * 100)
                }
            )
            
            result = process_image.apply(
                args=(image_data, config),
                kwargs={'task_id': f"batch_{self.request.id}_{idx}"}
            ).get()
            
            results.append(result)
        
        successful = sum(1 for r in results if r['status'] == 'success')
        
        logger.info(
            f"Batch processing complete: {successful}/{total} successful"
        )
        
        return {
            'status': 'complete',
            'total': total,
            'successful': successful,
            'failed': total - successful,
            'results': results
        }
        
    except Exception as e:
        logger.error(f"Batch processing error: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'traceback': traceback.format_exc()
        }


def load_image(image_data: bytes, format_hint: str = 'auto') -> np.ndarray:
    """Load image from bytes, supporting RAW and standard formats.
    
    Args:
        image_data: Raw image bytes
        format_hint: Format hint ('auto', 'raw', 'jpeg', 'png', etc.)
        
    Returns:
        Image as numpy array in RGB format
    """
    # Try RAW format first if hint suggests it
    if format_hint in ('raw', 'auto'):
        try:
            with rawpy.imread(io.BytesIO(image_data)) as raw:
                rgb = raw.postprocess(
                    use_camera_wb=False,
                    no_auto_bright=True,
                    output_bps=16
                )
                return rgb
        except Exception:
            if format_hint == 'raw':
                raise
    
    # Fall back to PIL for standard formats
    try:
        image = Image.open(io.BytesIO(image_data))
        return np.array(image.convert('RGB'))
    except Exception as e:
        raise ValueError(f"Failed to load image: {str(e)}")


def encode_image(image: np.ndarray, format: str = 'jpeg') -> bytes:
    """Encode numpy array to image bytes.
    
    Args:
        image: Image as numpy array
        format: Output format ('jpeg', 'png', 'tiff')
        
    Returns:
        Encoded image bytes
    """
    # Convert to 8-bit if necessary
    if image.dtype == np.uint16:
        image = (image / 256).astype(np.uint8)
    
    # Use PIL for encoding
    pil_image = Image.fromarray(image)
    buffer = io.BytesIO()
    
    format_map = {
        'jpeg': 'JPEG',
        'jpg': 'JPEG',
        'png': 'PNG',
        'tiff': 'TIFF',
        'tif': 'TIFF'
    }
    
    pil_format = format_map.get(format.lower(), 'JPEG')
    pil_image.save(buffer, format=pil_format, quality=95)
    
    return buffer.getvalue()


@app.task(name='tasks.health_check')
def health_check() -> Dict[str, str]:
    """Health check endpoint for worker monitoring.
    
    Returns:
        Health status dictionary
    """
    return {
        'status': 'healthy',
        'worker': 'color_correction_worker',
        'version': '1.0.0'
    }
