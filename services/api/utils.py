"""Utility Functions Module.

This module provides common utility functions for the Color Correction System API.
Includes file handling, validation, and helper functions.
"""

import os
import uuid
from pathlib import Path
from typing import Optional, List, Tuple
from datetime import datetime
import hashlib
from fastapi import UploadFile, HTTPException, status
from config import settings
import logging

logger = logging.getLogger(__name__)


def validate_file_extension(filename: str) -> bool:
    """Validate file extension against allowed types.
    
    Args:
        filename: The filename to validate
        
    Returns:
        True if extension is allowed, False otherwise
        
    Example:
        >>> validate_file_extension("photo.jpg")
        True
        >>> validate_file_extension("document.txt")
        False
    """
    if not filename:
        return False
    
    ext = filename.rsplit(".", 1)[-1].lower()
    return ext in settings.ALLOWED_EXTENSIONS


def validate_file_size(size_bytes: int) -> bool:
    """Validate file size against maximum allowed.
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        True if size is within limits, False otherwise
    """
    return 0 < size_bytes <= settings.MAX_UPLOAD_SIZE


def generate_unique_filename(original_filename: str) -> str:
    """Generate a unique filename for uploaded file.
    
    Preserves original extension but creates unique name to avoid conflicts.
    
    Args:
        original_filename: Original filename from upload
        
    Returns:
        Unique filename with preserved extension
        
    Example:
        >>> gen = generate_unique_filename("photo.jpg")
        >>> print(gen)  # "550e8400-e29b-41d4-a716-446655440000.jpg"
    """
    if "." not in original_filename:
        return str(uuid.uuid4())
    
    name, ext = original_filename.rsplit(".", 1)
    return f"{uuid.uuid4()}.{ext}"


async def save_upload_file(upload_file: UploadFile) -> Tuple[str, int]:
    """Save uploaded file to disk.
    
    Validates file before saving. Creates upload directory if needed.
    
    Args:
        upload_file: FastAPI UploadFile object
        
    Returns:
        Tuple of (filename, file_size_bytes)
        
    Raises:
        HTTPException: If file validation fails
    """
    # Validate extension
    if not validate_file_extension(upload_file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Create upload directory
    upload_dir = Path(settings.UPLOAD_DIRECTORY)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Read file content
    content = await upload_file.read()
    file_size = len(content)
    
    # Validate size
    if not validate_file_size(file_size):
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
        )
    
    # Generate unique filename
    unique_filename = generate_unique_filename(upload_file.filename)
    file_path = upload_dir / unique_filename
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(content)
    
    logger.info(f"File saved: {unique_filename} ({file_size} bytes)")
    
    return unique_filename, file_size


def get_file_path(filename: str) -> Path:
    """Get full path to uploaded file.
    
    Args:
        filename: Filename to locate
        
    Returns:
        Full Path object to file
        
    Raises:
        ValueError: If file not found
    """
    file_path = Path(settings.UPLOAD_DIRECTORY) / filename
    
    if not file_path.exists():
        raise ValueError(f"File not found: {filename}")
    
    return file_path


def delete_file(filename: str) -> bool:
    """Delete uploaded file.
    
    Args:
        filename: Filename to delete
        
    Returns:
        True if deleted successfully, False if file not found
    """
    try:
        file_path = get_file_path(filename)
        file_path.unlink()  # Delete file
        logger.info(f"File deleted: {filename}")
        return True
    except ValueError:
        logger.warning(f"File not found for deletion: {filename}")
        return False


def calculate_file_hash(file_path: Path, algorithm: str = "sha256") -> str:
    """Calculate hash of file for integrity verification.
    
    Args:
        file_path: Path to file
        algorithm: Hash algorithm (sha256, md5, etc.)
        
    Returns:
        Hex digest of file hash
    """
    hash_obj = hashlib.new(algorithm)
    
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_obj.update(chunk)
    
    return hash_obj.hexdigest()


def format_file_size(size_bytes: int) -> str:
    """Format file size for human-readable display.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., "2.5 MB")
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    
    return f"{size_bytes:.1f} TB"


def get_timestamp() -> datetime:
    """Get current UTC timestamp.
    
    Returns:
        Current datetime in UTC
    """
    return datetime.utcnow()


def validate_pagination(skip: int, limit: int) -> Tuple[int, int]:
    """Validate pagination parameters.
    
    Args:
        skip: Number of items to skip
        limit: Number of items to return
        
    Returns:
        Validated (skip, limit) tuple
        
    Raises:
        HTTPException: If parameters are invalid
    """
    if skip < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="skip must be >= 0"
        )
    
    if limit < 1 or limit > settings.MAX_PAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"limit must be between 1 and {settings.MAX_PAGE_SIZE}"
        )
    
    return skip, limit
