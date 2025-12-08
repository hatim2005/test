from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
import uuid


# Authentication Schemas
class UserRegisterSchema(BaseModel):
    """User registration schema"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "password": "securepassword123"
            }
        }


class UserLoginSchema(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123"
            }
        }


class TokenSchema(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600
            }
        }


class UserSchema(BaseModel):
    """User schema for responses"""
    id: uuid.UUID
    email: EmailStr
    username: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "username": "johndoe",
                "created_at": "2024-01-01T12:00:00",
                "updated_at": "2024-01-02T12:00:00"
            }
        }


# Image Schemas
class ImageCreateSchema(BaseModel):
    """Image creation schema"""
    filename: str
    file_size: int
    file_type: str
    description: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "filename": "image.jpg",
                "file_size": 1024000,
                "file_type": "image/jpeg",
                "description": "Sample image for color correction"
            }
        }


class ImageSchema(BaseModel):
    """Image schema for responses"""
    id: uuid.UUID
    user_id: uuid.UUID
    filename: str
    file_path: str
    file_size: int
    file_type: str
    description: Optional[str] = None
    upload_date: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440001",
                "filename": "image.jpg",
                "file_path": "/uploads/images/550e8400-e29b-41d4-a716-446655440000.jpg",
                "file_size": 1024000,
                "file_type": "image/jpeg",
                "description": "Sample image",
                "upload_date": "2024-01-01T12:00:00",
                "created_at": "2024-01-01T12:00:00",
                "updated_at": "2024-01-02T12:00:00"
            }
        }


class ImageUpdateSchema(BaseModel):
    """Image update schema"""
    description: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "description": "Updated description"
            }
        }


# Job Schemas
class JobCreateSchema(BaseModel):
    """Job creation schema"""
    image_id: uuid.UUID
    job_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    color_space: str = "RGB"
    reference_image_id: Optional[uuid.UUID] = None

    class Config:
        json_schema_extra = {
            "example": {
                "image_id": "550e8400-e29b-41d4-a716-446655440000",
                "job_name": "Color Correction Job 1",
                "description": "Correcting white balance",
                "color_space": "RGB",
                "reference_image_id": None
            }
        }


class JobStatusEnum(str):
    """Job status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobSchema(BaseModel):
    """Job schema for responses"""
    id: uuid.UUID
    user_id: uuid.UUID
    image_id: uuid.UUID
    job_name: str
    description: Optional[str] = None
    status: str
    color_space: str
    reference_image_id: Optional[uuid.UUID] = None
    progress: float = 0.0
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440001",
                "image_id": "550e8400-e29b-41d4-a716-446655440002",
                "job_name": "Color Correction Job 1",
                "description": "Correcting white balance",
                "status": "completed",
                "color_space": "RGB",
                "reference_image_id": None,
                "progress": 100.0,
                "created_at": "2024-01-01T12:00:00",
                "updated_at": "2024-01-02T12:00:00",
                "completed_at": "2024-01-02T12:30:00"
            }
        }


class JobUpdateSchema(BaseModel):
    """Job update schema"""
    job_name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    progress: Optional[float] = None

    class Config:
        json_schema_extra = {
            "example": {
                "job_name": "Updated Job Name",
                "description": "Updated description",
                "status": "running",
                "progress": 50.0
            }
        }


# Result Schemas
class ResultCreateSchema(BaseModel):
    """Result creation schema"""
    job_id: uuid.UUID
    result_image_path: str
    metadata: dict = {}
    color_correction_data: Optional[dict] = None

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "550e8400-e29b-41d4-a716-446655440000",
                "result_image_path": "/results/550e8400-e29b-41d4-a716-446655440000.jpg",
                "metadata": {"processing_time": 45.3, "algorithm": "ArUco"},
                "color_correction_data": {"color_matrix": [[1.0, 0.0], [0.0, 1.0]]}
            }
        }


class ResultSchema(BaseModel):
    """Result schema for responses"""
    id: uuid.UUID
    job_id: uuid.UUID
    result_image_path: str
    metadata: dict
    color_correction_data: Optional[dict] = None
    processing_time: Optional[float] = None
    quality_score: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "job_id": "550e8400-e29b-41d4-a716-446655440001",
                "result_image_path": "/results/550e8400-e29b-41d4-a716-446655440000.jpg",
                "metadata": {"processing_time": 45.3, "algorithm": "ArUco"},
                "color_correction_data": {"color_matrix": [[1.0, 0.0], [0.0, 1.0]]},
                "processing_time": 45.3,
                "quality_score": 0.95,
                "created_at": "2024-01-01T12:00:00",
                "updated_at": "2024-01-02T12:00:00"
            }
        }


class ResultUpdateSchema(BaseModel):
    """Result update schema"""
    quality_score: Optional[float] = None
    metadata: Optional[dict] = None

    class Config:
        json_schema_extra = {
            "example": {
                "quality_score": 0.98,
                "metadata": {"reviewed": True}
            }
        }
