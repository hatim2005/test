"""SQLAlchemy ORM Models for Color Correction System

Database models for user management, image processing, job tracking, and results storage.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Boolean, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class User(Base):
    """User account model for authentication and profile management"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    images = relationship("Image", back_populates="owner", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="owner", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class Image(Base):
    """Image model for uploaded images and metadata"""
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    storage_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    mime_type = Column(String(50), default="image/jpeg")
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    is_raw = Column(Boolean, default=False)
    metadata = Column(JSON, nullable=True)  # Camera info, color profile, etc.
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="images")
    jobs = relationship("Job", back_populates="image", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Image(id={self.id}, filename='{self.filename}')>"


class JobStatus(str, enum.Enum):
    """Enum for job status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobType(str, enum.Enum):
    """Enum for job type"""
    DETECTION = "detection"
    CORRECTION = "correction"
    BATCH = "batch"
    ANALYSIS = "analysis"


class Job(Base):
    """Job model for tracking processing tasks"""
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=True, index=True)
    job_type = Column(Enum(JobType), default=JobType.DETECTION, nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, nullable=False, index=True)
    description = Column(Text, nullable=True)
    parameters = Column(JSON, nullable=True)  # Job-specific parameters
    progress = Column(Float, default=0.0)  # 0-100 percentage
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    owner = relationship("User", back_populates="jobs")
    image = relationship("Image", back_populates="jobs")
    results = relationship("Result", back_populates="job", cascade="all, delete-orphan", uselist=False)
    
    def __repr__(self):
        return f"<Job(id={self.id}, type='{self.job_type.value}', status='{self.status.value}')>"


class Result(Base):
    """Result model for storing processing results and corrections"""
    __tablename__ = "results"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, unique=True, index=True)
    
    # Corrected/processed image paths
    corrected_image_path = Column(String(500), nullable=True)
    thumbnail_path = Column(String(500), nullable=True)
    
    # Color accuracy metrics
    delta_e_average = Column(Float, nullable=True)  # Average color difference
    delta_e_max = Column(Float, nullable=True)  # Maximum color difference
    delta_e_std = Column(Float, nullable=True)  # Standard deviation
    accuracy_rating = Column(String(50), nullable=True)  # Excellent, Good, Fair, Poor
    
    # Processing details
    processing_time_ms = Column(Integer, nullable=True)  # Processing time in milliseconds
    color_space = Column(String(50), nullable=True)  # sRGB, Adobe RGB, etc.
    whitepoint = Column(JSON, nullable=True)  # {"x": ..., "y": ...}
    
    # Detection results (if applicable)
    markers_detected = Column(Integer, nullable=True)  # Number of markers/patches found
    detection_confidence = Column(Float, nullable=True)  # 0-1 confidence score
    marker_positions = Column(JSON, nullable=True)  # List of detected marker positions
    
    # Comprehensive metadata
    metadata = Column(JSON, nullable=True)  # Additional processing information
    notes = Column(Text, nullable=True)  # User or system notes
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    job = relationship("Job", back_populates="results")
    
    def __repr__(self):
        return f"<Result(id={self.id}, job_id={self.job_id}, delta_e={self.delta_e_average})>"


class ProcessingPreset(Base):
    """Processing presets for different image types and scenarios"""
    __tablename__ = "processing_presets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    job_type = Column(Enum(JobType), nullable=False)
    
    # Processing parameters
    parameters = Column(JSON, nullable=False)  # Configuration for processing
    
    is_default = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<ProcessingPreset(id={self.id}, name='{self.name}')>"


class ProcessingLog(Base):
    """Processing logs for debugging and monitoring"""
    __tablename__ = "processing_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    
    log_level = Column(String(20), default="INFO")  # DEBUG, INFO, WARNING, ERROR
    message = Column(Text, nullable=False)
    stage = Column(String(100), nullable=True)  # detection, correction, validation, etc.
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<ProcessingLog(id={self.id}, level='{self.log_level}')>"


# Export all models
__all__ = [
    'Base',
    'User',
    'Image',
    'Job',
    'JobStatus',
    'JobType',
    'Result',
    'ProcessingPreset',
    'ProcessingLog',
]
