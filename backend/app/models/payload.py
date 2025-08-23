"""
Payload Pydantic models for API validation
"""
from pydantic import BaseModel, Field, validator
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum


class PayloadType(str, Enum):
    VISUAL = "visual"
    PYTHON = "python"


class FieldType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    UUID = "uuid"
    TIMESTAMP = "timestamp"


class PayloadBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Payload name")
    type: PayloadType = Field(..., description="Payload type (visual or python)")
    schema: Optional[Dict[str, Any]] = Field(None, description="JSON schema for visual payloads")
    python_code: Optional[str] = Field(None, description="Python code for python payloads")
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Payload name cannot be empty')
        return v.strip()


class PayloadCreate(PayloadBase):
    """Model for creating a new payload"""
    
    @validator('schema')
    def validate_schema(cls, v, values):
        payload_type = values.get('type')
        if payload_type == PayloadType.VISUAL:
            if not v:
                raise ValueError('Schema is required for visual payloads')
            # Validate schema structure
            if not isinstance(v, dict) or 'fields' not in v:
                raise ValueError('Schema must contain a "fields" array')
            if not isinstance(v['fields'], list):
                raise ValueError('Schema fields must be an array')
        return v
    
    @validator('python_code')
    def validate_python_code(cls, v, values):
        payload_type = values.get('type')
        if payload_type == PayloadType.PYTHON:
            if not v or not v.strip():
                raise ValueError('Python code is required for python payloads')
            # Basic Python syntax validation
            try:
                compile(v, '<string>', 'exec')
            except SyntaxError as e:
                raise ValueError(f'Invalid Python syntax: {e}')
        return v


class PayloadUpdate(BaseModel):
    """Model for updating an existing payload"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Payload name")
    type: Optional[PayloadType] = Field(None, description="Payload type")
    schema: Optional[Dict[str, Any]] = Field(None, description="JSON schema for visual payloads")
    python_code: Optional[str] = Field(None, description="Python code for python payloads")
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Payload name cannot be empty')
        return v.strip() if v else v
    
    @validator('python_code')
    def validate_python_code(cls, v):
        if v is not None and v.strip():
            try:
                compile(v, '<string>', 'exec')
            except SyntaxError as e:
                raise ValueError(f'Invalid Python syntax: {e}')
        return v


class PayloadResponse(PayloadBase):
    """Model for payload API responses"""
    id: str = Field(..., description="Payload unique identifier")
    created_at: datetime = Field(..., description="Payload creation timestamp")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PayloadSummary(BaseModel):
    """Lightweight payload model for listings"""
    id: str = Field(..., description="Payload unique identifier")
    name: str = Field(..., description="Payload name")
    type: PayloadType = Field(..., description="Payload type")
    created_at: datetime = Field(..., description="Payload creation timestamp")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Schema validation models for visual payloads
class FieldGenerator(BaseModel):
    """Field generator configuration"""
    type: str = Field(..., description="Generator type")
    value: Optional[Any] = Field(None, description="Fixed value")
    min: Optional[float] = Field(None, description="Minimum value for random generators")
    max: Optional[float] = Field(None, description="Maximum value for random generators")
    choices: Optional[List[str]] = Field(None, description="Choices for random selection")
    length: Optional[int] = Field(None, description="Length for string generators")
    decimals: Optional[int] = Field(None, description="Decimal places for float generators")


class PayloadField(BaseModel):
    """Payload field definition"""
    name: str = Field(..., description="Field name")
    type: FieldType = Field(..., description="Field type")
    generator: FieldGenerator = Field(..., description="Field generator configuration")


class PayloadSchema(BaseModel):
    """Complete payload schema"""
    fields: List[PayloadField] = Field(..., description="List of payload fields")