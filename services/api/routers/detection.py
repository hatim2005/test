"""Color Card Detection Router - Full Implementation

Handles ArUco marker detection using the CV library.
"""

from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import JSONResponse
from .auth import TokenData, get_current_user
import cv2
import numpy as np
import uuid
from datetime import datetime
import io
import logging

logger = logging.getLogger(__name__)

# Import CV library
try:
    from libs.cv.src.color_cv import ArucoDetector
except ImportError:
    logger.warning("CV library not available - detection will be disabled")
    ArucoDetector = None

router = APIRouter(prefix="/detect", tags=["detection"])

# Pydantic Models
class PatchData(BaseModel):
    patch_id: int
    center: tuple
    bbox: tuple
    mean_rgb: List[float]
    std_dev: float
    is_specular: bool

class DetectionResult(BaseModel):
    detection_id: str
    image_id: str
    success: bool
    markers_found: int
    card_orientation: Optional[str]
    patches: List[PatchData]
    patches_count: int
    confidence: float
    processing_time_ms: float
    timestamp: str
    errors: Optional[List[str]] = None

# Global storage (in production, use database)
detection_storage = {}

@router.post("/card", response_model=DetectionResult)
async def detect_color_card(
    file: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Detect color card in uploaded image using ArUco markers.
    
    Detects 4 ArUco markers (ID 0-3) at corners, determines orientation,
    applies perspective correction, and extracts 24-patch grid.
    
    Args:
        file: Uploaded image file (JPEG, PNG, TIFF)
        current_user: Authenticated user
        
    Returns:
        DetectionResult with patches and metadata
    """
    
    if ArucoDetector is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="CV library not available"
        )
    
    start_time = datetime.utcnow()
    detection_id = str(uuid.uuid4())
    image_id = f"{current_user.sub}_{start_time.timestamp()}"
    
    try:
        # Read image file
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return DetectionResult(
                detection_id=detection_id,
                image_id=image_id,
                success=False,
                markers_found=0,
                card_orientation=None,
                patches=[],
                patches_count=0,
                confidence=0.0,
                processing_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                timestamp=start_time.isoformat(),
                errors=["Failed to decode image"]
            )
        
        # Detect color card
        detector = ArucoDetector(corner_refinement=True)
        result = detector.detect(image, extract_patches=True)
        
        if result is None:
            return DetectionResult(
                detection_id=detection_id,
                image_id=image_id,
                success=False,
                markers_found=0,
                card_orientation=None,
                patches=[],
                patches_count=0,
                confidence=0.0,
                processing_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                timestamp=start_time.isoformat(),
                errors=["No color card detected in image"]
            )
        
        # Convert patches to response format
        patches_data = []
        for patch in result.patches:
            patch_data = PatchData(
                patch_id=patch.patch_id,
                center=patch.center,
                bbox=patch.bbox,
                mean_rgb=patch.mean_rgb.tolist(),
                std_dev=float(patch.std_dev),
                is_specular=patch.is_specular
            )
            patches_data.append(patch_data)
        
        detection_result = DetectionResult(
            detection_id=detection_id,
            image_id=image_id,
            success=True,
            markers_found=4,
            card_orientation=result.orientation.name,
            patches=patches_data,
            patches_count=len(patches_data),
            confidence=float(result.confidence),
            processing_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
            timestamp=start_time.isoformat()
        )
        
        # Store detection result
        detection_storage[detection_id] = detection_result
        
        logger.info(f"Detection successful: {detection_id} by user {current_user.sub}")
        return detection_result
        
    except Exception as e:
        logger.error(f"Error in color card detection: {str(e)}")
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        return DetectionResult(
            detection_id=detection_id,
            image_id=image_id,
            success=False,
            markers_found=0,
            card_orientation=None,
            patches=[],
            patches_count=0,
            confidence=0.0,
            processing_time_ms=processing_time,
            timestamp=start_time.isoformat(),
            errors=[str(e)]
        )

@router.get("/card/{detection_id}", response_model=DetectionResult)
async def get_detection_result(
    detection_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Retrieve a stored detection result by ID.
    
    Args:
        detection_id: Detection result ID
        current_user: Authenticated user
        
    Returns:
        DetectionResult if found
    """
    if detection_id not in detection_storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Detection result {detection_id} not found"
        )
    
    return detection_storage[detection_id]

@router.get("/health")
async def detection_health():
    """
    Health check endpoint for detection service.
    """
    return {
        "status": "healthy" if ArucoDetector is not None else "unavailable",
        "cv_library_available": ArucoDetector is not None,
        "timestamp": datetime.utcnow().isoformat()
    }
