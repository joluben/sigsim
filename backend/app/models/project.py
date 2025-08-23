"""
Project Pydantic models for API validation
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, ForwardRef
from datetime import datetime

# Forward reference to avoid circular imports
DeviceResponse = ForwardRef('DeviceResponse')


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Project name")
    description: Optional[str] = Field(None, max_length=500, description="Project description")
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Project name cannot be empty')
        return v.strip()


class ProjectCreate(ProjectBase):
    """Model for creating a new project"""
    pass


class ProjectUpdate(BaseModel):
    """Model for updating an existing project"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Project name")
    description: Optional[str] = Field(None, max_length=500, description="Project description")
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Project name cannot be empty')
        return v.strip() if v else v


class ProjectResponse(ProjectBase):
    """Model for project API responses"""
    id: str = Field(..., description="Project unique identifier")
    created_at: datetime = Field(..., description="Project creation timestamp")
    updated_at: datetime = Field(..., description="Project last update timestamp")
    devices: List[DeviceResponse] = Field(default=[], description="List of devices in this project")
    is_running: bool = Field(default=False, description="Whether the project simulation is running")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ProjectSummary(BaseModel):
    """Lightweight project model for listings"""
    id: str = Field(..., description="Project unique identifier")
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    created_at: datetime = Field(..., description="Project creation timestamp")
    device_count: int = Field(default=0, description="Number of devices in project")
    is_running: bool = Field(default=False, description="Whether the project simulation is running")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Update forward references
from app.models.device import DeviceResponse
ProjectResponse.model_rebuild()