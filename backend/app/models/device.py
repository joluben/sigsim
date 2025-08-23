"""
Device Pydantic models for API validation
"""
from pydantic import BaseModel, Field, validator
from typing import Dict, Any, Optional
from datetime import datetime


class DeviceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Device name")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Device metadata")
    payload_id: Optional[str] = Field(None, description="Associated payload ID")
    target_system_id: Optional[str] = Field(None, description="Associated target system ID")
    send_interval: int = Field(default=10, ge=1, le=3600, description="Send interval in seconds")
    is_enabled: bool = Field(default=True, description="Whether the device is enabled")
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Device name cannot be empty')
        return v.strip()
    
    @validator('metadata')
    def validate_metadata(cls, v):
        if v is None:
            return {}
        # Ensure metadata values are JSON serializable
        try:
            import json
            json.dumps(v)
        except (TypeError, ValueError):
            raise ValueError('Metadata must be JSON serializable')
        return v
    
    @validator('send_interval')
    def validate_send_interval(cls, v):
        if v < 1:
            raise ValueError('Send interval must be at least 1 second')
        if v > 3600:
            raise ValueError('Send interval cannot exceed 1 hour (3600 seconds)')
        return v


class DeviceCreate(DeviceBase):
    """Model for creating a new device"""
    project_id: str = Field(..., description="Project ID this device belongs to")


class DeviceUpdate(BaseModel):
    """Model for updating an existing device"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Device name")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Device metadata")
    payload_id: Optional[str] = Field(None, description="Associated payload ID")
    target_system_id: Optional[str] = Field(None, description="Associated target system ID")
    send_interval: Optional[int] = Field(None, ge=1, le=3600, description="Send interval in seconds")
    is_enabled: Optional[bool] = Field(None, description="Whether the device is enabled")
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Device name cannot be empty')
        return v.strip() if v else v
    
    @validator('metadata')
    def validate_metadata(cls, v):
        if v is None:
            return v
        # Ensure metadata values are JSON serializable
        try:
            import json
            json.dumps(v)
        except (TypeError, ValueError):
            raise ValueError('Metadata must be JSON serializable')
        return v


class DeviceResponse(DeviceBase):
    """Model for device API responses"""
    id: str = Field(..., description="Device unique identifier")
    project_id: str = Field(..., description="Project ID this device belongs to")
    created_at: datetime = Field(..., description="Device creation timestamp")
    updated_at: datetime = Field(..., description="Device last update timestamp")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DeviceSummary(BaseModel):
    """Lightweight device model for listings"""
    id: str = Field(..., description="Device unique identifier")
    name: str = Field(..., description="Device name")
    is_enabled: bool = Field(..., description="Whether the device is enabled")
    send_interval: int = Field(..., description="Send interval in seconds")
    has_payload: bool = Field(default=False, description="Whether device has a payload assigned")
    has_target: bool = Field(default=False, description="Whether device has a target system assigned")

    class Config:
        from_attributes = True