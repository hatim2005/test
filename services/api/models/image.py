"""Image Model.

Defines Image and ImageMetadata models for storing uploaded images and their processing results.
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from .database import Base


class Image(Base):
    """Image model for uploaded images and processing results."""
    
    __tablename__ = "images"
    
    # Primary key
    id = Column(String, primary_key=True, index=True)
    
    # Foreign keys
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # File information
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)
    thumbnail_url = Column(String, nullable=True)
    
    # Processing status
    status = Column(String, default="uploaded", nullable=False)  # uploaded, processing, completed, failed
    
    # Detection results
    detection_id = Column(String, nullable=True)
    markers_found = Column(Integer, nullable=True)
    card_orientation = Column(String, nullable=True)
    
    # Correction results
    correction_id = Column(String, nullable=True)
    ccm_matrix = Column(JSON, nullable=True)  # 3x3 matrix as JSON
    white_balance_gains = Column(JSON, nullable=True)  # [R, G, B] as JSON
    delta_e_overall = Column(Float, nullable=True)
    delta_e_per_patch = Column(JSON, nullable=True)  # List of ΔE values as JSON
    quality_rating = Column(String, nullable=True)  # Excellent, VeryGood, Good, Fair, Poor
    
    # Output
    output_image_url = Column(String, nullable=True)
    
    # Timestamps
    upload_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_date = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="images")
    metadata = relationship("ImageMetadata", back_populates="image", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Image(id={self.id}, filename={self.filename}, status={self.status})>"


class ImageMetadata(Base):
    """Image metadata model for EXIF and technical details."""
    
    __tablename__ = "image_metadata"
    
    # Primary key
    id = Column(String, primary_key=True, index=True)
    
    # Foreign key
    image_id = Column(String, ForeignKey("images.id"), nullable=False, unique=True)
    
    # Image dimensions
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    
    # Color information
    format = Column(String, nullable=True)
    color_space = Column(String, nullable=True)
    bit_depth = Column(Integer, nullable=True)
    
    # Camera information
    device_make = Column(String, nullable=True)
    device_model = Column(String, nullable=True)
    
    # Camera settings
    iso = Column(Integer, nullable=True)
    exposure_time = Column(String, nullable=True)
    f_number = Column(Float, nullable=True)
    focal_length = Column(Float, nullable=True)
    
    # Additional EXIF
    capture_date = Column(DateTime, nullable=True)
    gps_latitude = Column(Float, nullable=True)
    gps_longitude = Column(Float, nullable=True)
    
    # Relationships
    image = relationship("Image", back_populates="metadata")
    
    def __repr__(self):
        return f"<ImageMetadata(image_id={self.image_id}, {self.width}x{self.height})>"
