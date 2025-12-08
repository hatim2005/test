from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import uuid

from ..schemas import ResultCreateSchema, ResultSchema, ResultUpdateSchema
from ..database.models import Result
from ..database.config import get_db

router = APIRouter(prefix="/results", tags=["results"])


@router.post("/", response_model=ResultSchema, status_code=status.HTTP_201_CREATED)
async def create_result(
    result_data: ResultCreateSchema,
    user_id: str = None,
    db: Session = Depends(get_db)
) -> ResultSchema:
    """
    Store processing result
    
    - **job_id**: Processing job ID (UUID)
    - **result_image_path**: Path to result image
    - **metadata**: Processing metadata (dict)
    - **color_correction_data**: Correction data (optional dict)
    """
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    new_result = Result(
        job_id=result_data.job_id,
        result_image_path=result_data.result_image_path,
        metadata=result_data.metadata,
        color_correction_data=result_data.color_correction_data,
        created_at=datetime.utcnow()
    )
    
    db.add(new_result)
    db.commit()
    db.refresh(new_result)
    
    return new_result


@router.get("/", response_model=List[ResultSchema])
async def list_results(
    user_id: str = None,
    job_id: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
) -> List[ResultSchema]:
    """
    List processing results with optional job filtering
    
    - **job_id**: Filter by job ID (optional)
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum records to return (default: 10, max: 100)
    """
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    query = db.query(Result)
    
    if job_id:
        query = query.filter(Result.job_id == uuid.UUID(job_id))
    
    results = query.offset(skip).limit(limit).all()
    return results


@router.get("/{result_id}", response_model=ResultSchema)
async def get_result(
    result_id: str,
    user_id: str = None,
    db: Session = Depends(get_db)
) -> ResultSchema:
    """
    Get specific result by ID
    
    - **result_id**: Result unique identifier
    """
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    result = db.query(Result).filter(
        Result.id == uuid.UUID(result_id)
    ).first()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Result not found"
        )
    
    return result


@router.patch("/{result_id}", response_model=ResultSchema)
async def update_result(
    result_id: str,
    result_data: ResultUpdateSchema,
    user_id: str = None,
    db: Session = Depends(get_db)
) -> ResultSchema:
    """
    Update result quality score or metadata
    
    - **result_id**: Result unique identifier
    - **quality_score**: Quality score 0-1 (optional)
    - **metadata**: Updated metadata dict (optional)
    """
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    result = db.query(Result).filter(
        Result.id == uuid.UUID(result_id)
    ).first()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Result not found"
        )
    
    if result_data.quality_score is not None:
        result.quality_score = max(0.0, min(1.0, result_data.quality_score))
    
    if result_data.metadata is not None:
        if result.metadata:
            result.metadata.update(result_data.metadata)
        else:
            result.metadata = result_data.metadata
    
    result.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(result)
    
    return result


@router.delete("/{result_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_result(
    result_id: str,
    user_id: str = None,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a result record
    
    - **result_id**: Result unique identifier
    """
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    result = db.query(Result).filter(
        Result.id == uuid.UUID(result_id)
    ).first()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Result not found"
        )
    
    db.delete(result)
    db.commit()
