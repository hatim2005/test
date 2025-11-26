"""Job Model.

Defines Job model for batch processing and JobStatus enum.
"""

import enum
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship

from .database import Base


class JobStatus(enum.Enum):
    """Enum for job status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Job(Base):
    """Job model for batch processing operations."""
    
    __tablename__ = "jobs"
    
    # Primary key
    id = Column(String, primary_key=True, index=True)
    
    # Foreign key
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Job configuration
    operation = Column(String, nullable=False)  # detect, correct, detect_and_correct, remove_background
    image_ids = Column(JSON, nullable=False)  # List of image IDs to process
    options = Column(JSON, nullable=True)  # Processing options as JSON
    
    # Progress tracking
    total_images = Column(Integer, nullable=False, default=0)
    processed = Column(Integer, nullable=False, default=0)
    failed = Column(Integer, nullable=False, default=0)
    status = Column(Enum(JobStatus), nullable=False, default=JobStatus.PENDING)
    
    # Results
    results_url = Column(String, nullable=True)
    error_messages = Column(JSON, nullable=True)  # List of error messages
    
    # Webhook
    webhook_url = Column(String, nullable=True)
    webhook_sent = Column(String, nullable=False, default="pending")  # pending, sent, failed
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="jobs")
    
    def __repr__(self):
        return f"<Job(id={self.id}, operation={self.operation}, status={self.status.value})>"
