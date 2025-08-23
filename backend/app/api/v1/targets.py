"""
Target system management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api.dependencies import get_db_session
from app.models.target import TargetSystemCreate, TargetSystemResponse, TargetSystemUpdate, TargetSystemSummary, TargetType
from app.services.target_service import TargetSystemService
from app.services.validation_service import ValidationService

router = APIRouter()


@router.get("/", response_model=List[TargetSystemSummary])
async def get_target_systems(
    skip: int = Query(0, ge=0, description="Number of target systems to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of target systems to return"),
    search: Optional[str] = Query(None, description="Search term for target system names"),
    target_type: Optional[TargetType] = Query(None, description="Filter by target type"),
    db: Session = Depends(get_db_session)
):
    """Get all target systems with pagination and optional filters"""
    service = TargetSystemService(db)
    
    if search:
        targets = await service.search_target_systems(search, skip, limit)
    elif target_type:
        targets = await service.get_target_systems_by_type(target_type, skip, limit)
    else:
        targets = await service.get_all_target_systems(skip, limit)
    
    return [
        TargetSystemSummary(
            id=target.id,
            name=target.name,
            type=target.type,
            created_at=target.created_at
        )
        for target in targets
    ]


@router.post("/", response_model=TargetSystemResponse, status_code=status.HTTP_201_CREATED)
async def create_target_system(
    target: TargetSystemCreate,
    db: Session = Depends(get_db_session)
):
    """Create a new target system"""
    service = TargetSystemService(db)
    validation_service = ValidationService(db)
    
    # Validate target system data
    errors = await validation_service.validate_target_system_creation(target.dict())
    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Validation failed", "errors": errors}
        )
    
    result = await service.create_target_system(target)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create target system"
        )
    
    return result


@router.get("/recent", response_model=List[TargetSystemSummary])
async def get_recent_target_systems(
    limit: int = Query(10, ge=1, le=50, description="Number of recent target systems to return"),
    db: Session = Depends(get_db_session)
):
    """Get most recently created target systems"""
    service = TargetSystemService(db)
    targets = await service.get_recent_target_systems(limit)
    return [
        TargetSystemSummary(
            id=target.id,
            name=target.name,
            type=target.type,
            created_at=target.created_at
        )
        for target in targets
    ]


@router.get("/stats")
async def get_target_system_stats(db: Session = Depends(get_db_session)):
    """Get target system statistics by type"""
    service = TargetSystemService(db)
    return await service.get_target_system_stats()


@router.get("/{target_id}", response_model=TargetSystemResponse)
async def get_target_system(
    target_id: str,
    db: Session = Depends(get_db_session)
):
    """Get a specific target system by ID"""
    service = TargetSystemService(db)
    target = await service.get_target_system_by_id(target_id)
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target system not found"
        )
    return target


@router.put("/{target_id}", response_model=TargetSystemResponse)
async def update_target_system(
    target_id: str,
    target_update: TargetSystemUpdate,
    db: Session = Depends(get_db_session)
):
    """Update a target system"""
    service = TargetSystemService(db)
    validation_service = ValidationService(db)
    
    # Validate update data
    errors = await validation_service.validate_target_system_update(target_id, target_update.dict())
    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Validation failed", "errors": errors}
        )
    
    target = await service.update_target_system(target_id, target_update)
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target system not found or update failed"
        )
    return target


@router.delete("/{target_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_target_system(
    target_id: str,
    db: Session = Depends(get_db_session)
):
    """Delete a target system"""
    service = TargetSystemService(db)
    
    # Check if target system is being used by devices
    if await service.is_target_system_in_use(target_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete target system: it is being used by one or more devices"
        )
    
    success = await service.delete_target_system(target_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target system not found"
        )


@router.post("/{target_id}/test-connection")
async def test_target_system_connection(
    target_id: str,
    db: Session = Depends(get_db_session)
):
    """Test connection to a target system"""
    service = TargetSystemService(db)
    
    try:
        result = await service.test_connection(target_id)
        return {"success": result["success"], "message": result["message"]}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Connection test failed: {str(e)}"
        )