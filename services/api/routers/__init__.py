"""Routers package for Color Correction API.

This package contains all API route handlers organized by domain:
- auth: Authentication and authorization
- images: Image upload and management
- detection: Color card detection
- correction: Color correction operations
- batch: Batch processing
- reports: Analytics and reporting
"""

from fastapi import APIRouter

# Import all routers
from .auth import router as auth_router
from .images import router as images_router
from .detection import router as detection_router
from .correction import router as correction_router
from .batch import router as batch_router
from .reports import router as reports_router

# Create main API router
api_router = APIRouter()

# Include all sub-routers with prefixes
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(images_router, prefix="/images", tags=["images"])
api_router.include_router(detection_router, prefix="/detect", tags=["detection"])
api_router.include_router(correction_router, prefix="/correct", tags=["correction"])
api_router.include_router(batch_router, prefix="/batch", tags=["batch"])
api_router.include_router(reports_router, prefix="/reports", tags=["reports"])

__all__ = [
    "api_router",
    "auth_router",
    "images_router",
    "detection_router",
    "correction_router",
    "batch_router",
    "reports_router",
]
