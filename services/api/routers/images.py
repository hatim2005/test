"""Image Upload and Management Router.

Handles image uploads, storage, metadata management, and retrieval.
"""

import os
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel

from .auth import TokenData, get_current_user

router = APIRouter()

# Configuration
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".tiff", ".tif", ".dng", ".raw"]


# Schemas
class ImageMetadata(BaseModel):
    """Image metadata model."""
    width: Optional[int] = None
    height: Optional[int] = None
    format: Optional[str] = None
    color_space: Optional[str] = None
    bit_depth: Optional[int] = None
    device_model: Optional[str] = None
    device_make: Optional[str] = None


class ImageResponse(BaseModel):
    """Image response model."""
    id: str
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    upload_date: datetime
    user_id: str
    metadata: Optional[ImageMetadata] = None
    storage_path: str
    thumbnail_url: Optional[str] = None
    status: str = "uploaded"


class ImageListResponse(BaseModel):
    """Image list response model."""
    images: List[ImageResponse]
    total: int
    page: int
    page_size: int


class ImageUpdate(BaseModel):
    """Image update model."""
    filename: Optional[str] = None
    metadata: Optional[ImageMetadata] = None


# Utility functions
def validate_file(file: UploadFile) -> bool:
    """Validate uploaded file."""
    # Check file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_ext} not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    return True


async def save_upload_file(file: UploadFile, user_id: str) -> tuple:
    """Save uploaded file to storage."""
    # Generate unique filename
    file_id = str(uuid.uuid4())
    file_ext = os.path.splitext(file.filename)[1].lower()
    stored_filename = f"{file_id}{file_ext}"
    
    # Create user directory if not exists
    user_dir = os.path.join(UPLOAD_DIR, user_id)
    os.makedirs(user_dir, exist_ok=True)
    
    # Save file
    file_path = os.path.join(user_dir, stored_filename)
    
    # Read and save file
    content = await file.read()
    file_size = len(content)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE / (1024*1024)} MB"
        )
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    return file_id, file_path, file_size


# Routes
@router.post("/", response_model=ImageResponse, status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Upload a new image.
    
    Args:
        file: Image file to upload (RAW, DNG, JPEG, PNG, TIFF)
        current_user: Current authenticated user
    
    Returns:
        ImageResponse: Uploaded image metadata
    
    Raises:
        HTTPException: If file validation fails or upload error occurs
    """
    # Validate file
    validate_file(file)
    
    try:
        # Save file
        file_id, file_path, file_size = await save_upload_file(file, current_user.user_id)
        
        # TODO: Extract EXIF metadata
        # TODO: Generate thumbnail
        # TODO: Save to database
        
        # Mock response for now
        return ImageResponse(
            id=file_id,
            filename=file_id + os.path.splitext(file.filename)[1],
            original_filename=file.filename,
            file_size=file_size,
            mime_type=file.content_type or "application/octet-stream",
            upload_date=datetime.utcnow(),
            user_id=current_user.user_id,
            storage_path=file_path,
            status="uploaded"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {str(e)}"
        )


@router.post("/batch", response_model=List[ImageResponse], status_code=status.HTTP_201_CREATED)
async def upload_images_batch(
    files: List[UploadFile] = File(...),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Upload multiple images in batch.
    
    Args:
        files: List of image files to upload
        current_user: Current authenticated user
    
    Returns:
        List[ImageResponse]: List of uploaded image metadata
    
    Raises:
        HTTPException: If validation or upload fails
    """
    if len(files) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 100 files allowed per batch upload"
        )
    
    uploaded_images = []
    failed_uploads = []
    
    for file in files:
        try:
            validate_file(file)
            file_id, file_path, file_size = await save_upload_file(file, current_user.user_id)
            
            uploaded_images.append(ImageResponse(
                id=file_id,
                filename=file_id + os.path.splitext(file.filename)[1],
                original_filename=file.filename,
                file_size=file_size,
                mime_type=file.content_type or "application/octet-stream",
                upload_date=datetime.utcnow(),
                user_id=current_user.user_id,
                storage_path=file_path,
                status="uploaded"
            ))
        except Exception as e:
            failed_uploads.append({"filename": file.filename, "error": str(e)})
    
    if failed_uploads:
        # Return partial success with error details
        return uploaded_images
    
    return uploaded_images


@router.get("/", response_model=ImageListResponse)
async def list_images(
    page: int = 1,
    page_size: int = 20,
    current_user: TokenData = Depends(get_current_user)
):
    """
    List user's uploaded images with pagination.
    
    Args:
        page: Page number (default: 1)
        page_size: Items per page (default: 20, max: 100)
        current_user: Current authenticated user
    
    Returns:
        ImageListResponse: Paginated list of images
    """
    if page_size > 100:
        page_size = 100
    
    # TODO: Fetch from database with pagination
    
    # Mock response
    return ImageListResponse(
        images=[],
        total=0,
        page=page,
        page_size=page_size
    )


@router.get("/{image_id}", response_model=ImageResponse)
async def get_image(
    image_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get image details by ID.
    
    Args:
        image_id: Image ID
        current_user: Current authenticated user
    
    Returns:
        ImageResponse: Image metadata
    
    Raises:
        HTTPException: If image not found or access denied
    """
    # TODO: Fetch from database
    # TODO: Check ownership
    
    # Mock response
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Image not found"
    )


@router.patch("/{image_id}", response_model=ImageResponse)
async def update_image(
    image_id: str,
    update_data: ImageUpdate,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Update image metadata.
    
    Args:
        image_id: Image ID
        update_data: Fields to update
        current_user: Current authenticated user
    
    Returns:
        ImageResponse: Updated image metadata
    
    Raises:
        HTTPException: If image not found or access denied
    """
    # TODO: Update in database
    # TODO: Check ownership
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Image not found"
    )


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    image_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Delete an image.
    
    Args:
        image_id: Image ID
        current_user: Current authenticated user
    
    Raises:
        HTTPException: If image not found or access denied
    """
    # TODO: Delete from storage
    # TODO: Delete from database
    # TODO: Check ownership
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Image not found"
    )
