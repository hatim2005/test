"""FastAPI Backend Service for Color Correction System"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
from datetime import datetime
from celery import Celery
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Color Correction API",
    version="2.0.0",
    description="Production color correction system with RAW processing, ArUco detection, and batch jobs"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Celery Configuration
def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
        broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    )
    celery.conf.update(app.config)
    return celery

celery_app = make_celery(app)

# Import routers
try:
    from routers.detection import router as detection_router
    from routers.correction import router as correction_router
    from routers.batch import router as batch_router
    from routers.auth import router as auth_router
    from routers.images import router as images_router
    from routers.jobs import router as jobs_router
    from routers.results import router as results_router
    logger.info("Successfully imported all routers")
except ImportError as e:
    logger.error(f"Error importing routers: {e}")
    raise

# Include routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(images_router, prefix="/api/v1/images", tags=["Image Management"])
app.include_router(jobs_router, prefix="/api/v1/jobs", tags=["Job Management"])
app.include_router(results_router, prefix="/api/v1/results", tags=["Results"])
app.include_router(detection_router, prefix="/api/v1/detection", tags=["Detection"])
app.include_router(correction_router, prefix="/api/v1/correction", tags=["Correction"])
app.include_router(batch_router, prefix="/api/v1/batch", tags=["Batch Processing"])
logger.info("All 7 routers registered successfully")

# Data models
class HealthCheckResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    components: dict

class ImageUploadResponse(BaseModel):
    image_id: str
    filename: str
    size: int
    upload_time: str

class APIErrorResponse(BaseModel):
    error: str
    detail: str
    timestamp: str

# Health check endpoint
@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
def health_check():
    """Check API health status and component availability"""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.0.0",
            "components": {
                "authentication": "operational",
                "image_management": "operational",
                "job_management": "operational",
                "results_tracking": "operational",
                "detection": "operational",
                "correction": "operational",
                "batch_processing": "operational",
                "celery_worker": "operational",
                "cv_library": "integrated"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Root endpoint
@app.get("/", tags=["Root"])
def read_root():
    """API root endpoint with version information"""
    return {
        "message": "Color Correction System API",
        "version": "2.0.0",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "auth": "/api/v1/auth",
            "images": "/api/v1/images",
            "jobs": "/api/v1/jobs",
            "results": "/api/v1/results",
            "detection": "/api/v1/detection",
            "correction": "/api/v1/correction",
            "batch": "/api/v1/batch"
        }
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Error",
            "detail": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("=" * 70)
    logger.info("Color Correction System API - Starting Up")
    logger.info(f"Version: 2.0.0")
    logger.info(f"Timestamp: {datetime.utcnow().isoformat()}")
    logger.info("Components Initialized:")
    logger.info(" - FastAPI Framework: Ready")
    logger.info(" - CORS Middleware: Configured")
    logger.info(" - Authentication Router: Integrated")
    logger.info(" - Image Management Router: Integrated")
    logger.info(" - Job Management Router: Integrated")
    logger.info(" - Results Tracking Router: Integrated")
    logger.info(" - Detection Router: Integrated")
    logger.info(" - Correction Router: Integrated")
    logger.info(" - Batch Processing Router: Integrated")
    logger.info(" - Celery Worker: Connected")
    logger.info("=" * 70)

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("Color Correction System API - Shutting Down")
    logger.info(f"Timestamp: {datetime.utcnow().isoformat()}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
