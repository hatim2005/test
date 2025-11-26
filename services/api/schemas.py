"""Pydantic schemas for API request/response validation."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum


class WhiteBalanceMethod(str, Enum):
    """Available white balance methods."""
    GRAY_WORLD = "gray_world"
    WHITE_PATCH = "white_patch"
    LEARNING_BASED = "learning_based"


class ProcessingConfig(BaseModel):
    """Configuration for image processing."""
    wb_method: WhiteBalanceMethod = Field(
        default=WhiteBalanceMethod.GRAY_WORLD,
        description="White balance method to use"
    )
    remove_background: bool = Field(
        default=False,
        description="Whether to remove background"
    )
    output_format: str = Field(
        default="jpeg",
        description="Output image format (jpeg, png, tiff)"
    )


class ImageProcessRequest(BaseModel):
    """Request schema for single image processing."""
    config: ProcessingConfig = Field(
        default_factory=ProcessingConfig,
        description="Processing configuration"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "config": {
                    "wb_method": "gray_world",
                    "remove_background": False,
                    "output_format": "jpeg"
                }
            }
        }


class ProcessingMetrics(BaseModel):
    """Metrics from color correction processing."""
    delta_e: Optional[float] = Field(
        default=None,
        description="Average Delta E color difference"
    )
    markers_detected: int = Field(
        description="Number of ArUco markers detected"
    )


class ImageProcessResponse(BaseModel):
    """Response schema for image processing."""
    status: str = Field(description="Processing status")
    task_id: Optional[str] = Field(
        default=None,
        description="Task ID for async processing"
    )
    metrics: Optional[ProcessingMetrics] = Field(
        default=None,
        description="Processing metrics"
    )
    format: Optional[str] = Field(
        default=None,
        description="Output image format"
    )


class BatchProcessRequest(BaseModel):
    """Request schema for batch processing."""
    num_images: int = Field(
        description="Number of images in batch",
        ge=1,
        le=100
    )
    config: ProcessingConfig = Field(
        default_factory=ProcessingConfig
    )


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    worker_available: bool
