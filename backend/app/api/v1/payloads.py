"""
Payload management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api.dependencies import get_db_session
from app.models.payload import PayloadCreate, PayloadResponse, PayloadUpdate, PayloadSummary, PayloadType
from app.services.payload_service import PayloadService
from app.services.validation_service import ValidationService

router = APIRouter()


@router.get("/", response_model=List[PayloadSummary])
async def get_payloads(
    skip: int = Query(0, ge=0, description="Number of payloads to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of payloads to return"),
    search: Optional[str] = Query(None, description="Search term for payload names"),
    payload_type: Optional[PayloadType] = Query(None, description="Filter by payload type"),
    db: Session = Depends(get_db_session)
):
    """Get all payloads with pagination and optional filters"""
    service = PayloadService(db)
    
    if search:
        payloads = await service.search_payloads(search, skip, limit)
    elif payload_type:
        payloads = await service.get_payloads_by_type(payload_type, skip, limit)
    else:
        payloads = await service.get_all_payloads(skip, limit)
    
    return [
        PayloadSummary(
            id=payload.id,
            name=payload.name,
            type=payload.type,
            created_at=payload.created_at
        )
        for payload in payloads
    ]


@router.post("/", response_model=PayloadResponse, status_code=status.HTTP_201_CREATED)
async def create_payload(
    payload: PayloadCreate,
    db: Session = Depends(get_db_session)
):
    """Create a new payload"""
    service = PayloadService(db)
    validation_service = ValidationService(db)
    
    # Validate payload data
    errors = await validation_service.validate_payload_creation(payload.dict())
    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Validation failed", "errors": errors}
        )
    
    result = await service.create_payload(payload)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create payload"
        )
    
    return result


@router.get("/recent", response_model=List[PayloadSummary])
async def get_recent_payloads(
    limit: int = Query(10, ge=1, le=50, description="Number of recent payloads to return"),
    db: Session = Depends(get_db_session)
):
    """Get most recently created payloads"""
    service = PayloadService(db)
    payloads = await service.get_recent_payloads(limit)
    return [
        PayloadSummary(
            id=payload.id,
            name=payload.name,
            type=payload.type,
            created_at=payload.created_at
        )
        for payload in payloads
    ]


@router.get("/stats")
async def get_payload_stats(db: Session = Depends(get_db_session)):
    """Get payload statistics by type"""
    service = PayloadService(db)
    return await service.get_payload_stats()


@router.get("/{payload_id}", response_model=PayloadResponse)
async def get_payload(
    payload_id: str,
    db: Session = Depends(get_db_session)
):
    """Get a specific payload by ID"""
    service = PayloadService(db)
    payload = await service.get_payload_by_id(payload_id)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payload not found"
        )
    return payload


@router.put("/{payload_id}", response_model=PayloadResponse)
async def update_payload(
    payload_id: str,
    payload_update: PayloadUpdate,
    db: Session = Depends(get_db_session)
):
    """Update a payload"""
    service = PayloadService(db)
    validation_service = ValidationService(db)
    
    # Validate update data
    errors = await validation_service.validate_payload_update(payload_id, payload_update.dict())
    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Validation failed", "errors": errors}
        )
    
    payload = await service.update_payload(payload_id, payload_update)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payload not found or update failed"
        )
    return payload


@router.delete("/{payload_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payload(
    payload_id: str,
    db: Session = Depends(get_db_session)
):
    """Delete a payload"""
    service = PayloadService(db)
    
    # Check if payload is being used by devices
    if await service.is_payload_in_use(payload_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete payload: it is being used by one or more devices"
        )
    
    success = await service.delete_payload(payload_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payload not found"
        )


@router.post("/{payload_id}/test")
async def test_payload_generation(
    payload_id: str,
    test_data: Optional[dict] = None,
    db: Session = Depends(get_db_session)
):
    """Test payload generation with optional device metadata"""
    service = PayloadService(db)
    
    try:
        result = await service.test_payload_generation(payload_id, test_data)
        return {"success": True, "generated_payload": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payload generation failed: {str(e)}"
        )