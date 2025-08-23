"""
Device management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api.dependencies import get_db_session
from app.models.device import DeviceCreate, DeviceResponse, DeviceUpdate, DeviceSummary
from app.services.device_service import DeviceService
from app.services.validation_service import ValidationService

router = APIRouter()


@router.get("/project/{project_id}", response_model=List[DeviceSummary])
async def get_devices_by_project(
    project_id: str,
    skip: int = Query(0, ge=0, description="Number of devices to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of devices to return"),
    search: Optional[str] = Query(None, description="Search term for device names"),
    enabled_only: bool = Query(False, description="Return only enabled devices"),
    db: Session = Depends(get_db_session)
):
    """Get devices for a specific project with pagination and filters"""
    service = DeviceService(db)
    
    if search:
        return await service.search_devices_in_project(project_id, search)
    elif enabled_only:
        devices = await service.get_enabled_devices_by_project(project_id)
        return [
            DeviceSummary(
                id=device.id,
                name=device.name,
                is_enabled=device.is_enabled,
                send_interval=device.send_interval,
                has_payload=device.payload_id is not None,
                has_target=device.target_system_id is not None
            )
            for device in devices
        ]
    else:
        return await service.get_devices_by_project(project_id, skip, limit)


@router.get("/project/{project_id}/with-relations", response_model=List[DeviceResponse])
async def get_devices_with_relations_by_project(
    project_id: str,
    db: Session = Depends(get_db_session)
):
    """Get all devices for a project with payload and target system loaded"""
    service = DeviceService(db)
    return await service.get_devices_with_relations_by_project(project_id)


@router.get("/project/{project_id}/stats")
async def get_device_stats_by_project(
    project_id: str,
    db: Session = Depends(get_db_session)
):
    """Get device statistics for a project"""
    service = DeviceService(db)
    return await service.get_device_count_by_project(project_id)


@router.post("/", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def create_device(
    device: DeviceCreate,
    db: Session = Depends(get_db_session)
):
    """Create a new device"""
    service = DeviceService(db)
    validation_service = ValidationService(db)
    
    # Validate device data
    errors = await validation_service.validate_device_creation(device.dict())
    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Validation failed", "errors": errors}
        )
    
    result = await service.create_device(device)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create device"
        )
    
    return result


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: str,
    db: Session = Depends(get_db_session)
):
    """Get a specific device by ID"""
    service = DeviceService(db)
    device = await service.get_device_by_id(device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    return device


@router.put("/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: str,
    device_update: DeviceUpdate,
    db: Session = Depends(get_db_session)
):
    """Update a device"""
    service = DeviceService(db)
    validation_service = ValidationService(db)
    
    # Validate update data
    errors = await validation_service.validate_device_update(device_id, device_update.dict())
    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Validation failed", "errors": errors}
        )
    
    device = await service.update_device(device_id, device_update)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found or update failed"
        )
    return device


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_id: str,
    db: Session = Depends(get_db_session)
):
    """Delete a device"""
    service = DeviceService(db)
    success = await service.delete_device(device_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )


@router.patch("/bulk-enable", status_code=status.HTTP_200_OK)
async def bulk_update_device_status(
    request_data: dict,
    db: Session = Depends(get_db_session)
):
    """Bulk update enabled status for multiple devices"""
    service = DeviceService(db)
    
    device_ids = request_data.get("device_ids", [])
    is_enabled = request_data.get("is_enabled", True)
    
    if not device_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="device_ids is required"
        )
    
    updated_count = await service.bulk_update_enabled_status(device_ids, is_enabled)
    return {
        "message": f"Updated {updated_count} devices",
        "updated_count": updated_count,
        "is_enabled": is_enabled
    }