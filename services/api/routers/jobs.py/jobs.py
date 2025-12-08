from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import uuid

from ..schemas import JobCreateSchema, JobSchema, JobUpdateSchema, JobStatusEnum
from ..database.models import Job
from ..database.config import get_db

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/", response_model=JobSchema, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: JobCreateSchema,
    user_id: str = None,
    db: Session = Depends(get_db)
) -> JobSchema:
    """
    Create a new processing job
    
    - **image_id**: Image to process (UUID)
    - **job_name**: Job name (1-255 characters)
    - **description**: Optional job description
    - **color_space**: Color space (default: RGB)
    - **reference_image_id**: Optional reference image UUID
    """
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    new_job = Job(
        user_id=uuid.UUID(user_id),
        image_id=job_data.image_id,
        job_name=job_data.job_name,
        description=job_data.description,
        status=JobStatusEnum.PENDING,
        color_space=job_data.color_space,
        reference_image_id=job_data.reference_image_id,
        progress=0.0,
        created_at=datetime.utcnow()
    )
    
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    
    return new_job


@router.get("/", response_model=List[JobSchema])
async def list_jobs(
    user_id: str = None,
    status: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
) -> List[JobSchema]:
    """
    List user's processing jobs with optional filtering
    
    - **status**: Filter by job status (pending, running, completed, failed, cancelled)
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records (default: 10, max: 100)
    """
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    query = db.query(Job).filter(Job.user_id == uuid.UUID(user_id))
    
    if status:
        query = query.filter(Job.status == status)
    
    jobs = query.offset(skip).limit(limit).all()
    return jobs


@router.get("/{job_id}", response_model=JobSchema)
async def get_job(
    job_id: str,
    user_id: str = None,
    db: Session = Depends(get_db)
) -> JobSchema:
    """
    Get specific job details by ID
    
    - **job_id**: Job unique identifier
    """
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    job = db.query(Job).filter(
        Job.id == uuid.UUID(job_id),
        Job.user_id == uuid.UUID(user_id)
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return job


@router.patch("/{job_id}", response_model=JobSchema)
async def update_job(
    job_id: str,
    job_data: JobUpdateSchema,
    user_id: str = None,
    db: Session = Depends(get_db)
) -> JobSchema:
    """
    Update job status, progress, or metadata
    
    - **job_id**: Job unique identifier
    - **job_name**: New job name (optional)
    - **status**: New status (optional)
    - **progress**: Progress percentage 0-100 (optional)
    - **description**: Updated description (optional)
    """
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    job = db.query(Job).filter(
        Job.id == uuid.UUID(job_id),
        Job.user_id == uuid.UUID(user_id)
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if job_data.job_name is not None:
        job.job_name = job_data.job_name
    
    if job_data.status is not None:
        job.status = job_data.status
        if job_data.status == JobStatusEnum.COMPLETED:
            job.completed_at = datetime.utcnow()
    
    if job_data.progress is not None:
        job.progress = min(100.0, max(0.0, job_data.progress))
    
    if job_data.description is not None:
        job.description = job_data.description
    
    job.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(job)
    
    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: str,
    user_id: str = None,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete or cancel a job
    
    - **job_id**: Job unique identifier
    """
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    job = db.query(Job).filter(
        Job.id == uuid.UUID(job_id),
        Job.user_id == uuid.UUID(user_id)
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    job.status = JobStatusEnum.CANCELLED
    job.updated_at = datetime.utcnow()
    
    db.commit()
