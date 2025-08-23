"""
API endpoints for target system connectors
"""
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.services.connector_service import ConnectorService
from app.repositories.target_repository import TargetRepository
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(prefix="/connectors", tags=["connectors"])


class ConnectionTestRequest(BaseModel):
    """Request model for connection testing"""
    target_system_id: str


class ConnectionTestResponse(BaseModel):
    """Response model for connection testing"""
    success: bool
    message: str = None
    error: str = None
    details: str = None
    test_payload: Dict[str, Any] = None


class ConfigValidationRequest(BaseModel):
    """Request model for configuration validation"""
    target_type: str
    config: Dict[str, Any]


class ConfigValidationResponse(BaseModel):
    """Response model for configuration validation"""
    valid: bool
    validated_config: Dict[str, Any] = None
    errors: List[str] = None


class SupportedTypesResponse(BaseModel):
    """Response model for supported types"""
    supported_types: List[str]
    schemas: Dict[str, Dict[str, Any]] = None


class HealthCheckResponse(BaseModel):
    """Response model for health check"""
    total_connections: int
    healthy_connections: int
    unhealthy_connections: int
    connection_details: Dict[str, Dict[str, Any]]


def get_connector_service(db: AsyncSession = Depends(get_db)) -> ConnectorService:
    """Dependency to get connector service"""
    target_repository = TargetRepository(db)
    return ConnectorService(target_repository)


@router.get("/types", response_model=SupportedTypesResponse)
async def get_supported_types(
    include_schemas: bool = False,
    connector_service: ConnectorService = Depends(get_connector_service)
):
    """
    Get list of supported connector types
    
    Args:
        include_schemas: Whether to include configuration schemas
        connector_service: Connector service dependency
        
    Returns:
        List of supported types and optionally their schemas
    """
    supported_types = connector_service.get_supported_types()
    
    response = SupportedTypesResponse(supported_types=supported_types)
    
    if include_schemas:
        schemas = {}
        for target_type in supported_types:
            schema = connector_service.get_config_schema(target_type)
            if schema:
                schemas[target_type] = schema
        response.schemas = schemas
    
    return response


@router.post("/test", response_model=ConnectionTestResponse)
async def test_connection(
    request: ConnectionTestRequest,
    connector_service: ConnectorService = Depends(get_connector_service)
):
    """
    Test connection to a target system
    
    Args:
        request: Connection test request
        connector_service: Connector service dependency
        
    Returns:
        Connection test results
    """
    try:
        result = await connector_service.test_connection(request.target_system_id)
        
        return ConnectionTestResponse(
            success=result['success'],
            message=result.get('message'),
            error=result.get('error'),
            details=result.get('details'),
            test_payload=result.get('test_payload')
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Connection test failed: {str(e)}"
        )


@router.post("/validate", response_model=ConfigValidationResponse)
async def validate_config(
    request: ConfigValidationRequest,
    connector_service: ConnectorService = Depends(get_connector_service)
):
    """
    Validate configuration for a target type
    
    Args:
        request: Configuration validation request
        connector_service: Connector service dependency
        
    Returns:
        Validation results
    """
    try:
        validated_config = connector_service.validate_config(
            request.target_type, 
            request.config
        )
        
        return ConfigValidationResponse(
            valid=True,
            validated_config=validated_config
        )
        
    except ValueError as e:
        return ConfigValidationResponse(
            valid=False,
            errors=[str(e)]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Configuration validation failed: {str(e)}"
        )


@router.get("/health", response_model=HealthCheckResponse)
async def health_check(
    connector_service: ConnectorService = Depends(get_connector_service)
):
    """
    Perform health check on all active connections
    
    Args:
        connector_service: Connector service dependency
        
    Returns:
        Health check results
    """
    try:
        result = await connector_service.health_check()
        
        return HealthCheckResponse(
            total_connections=result['total_connections'],
            healthy_connections=result['healthy_connections'],
            unhealthy_connections=result['unhealthy_connections'],
            connection_details=result['connection_details']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )


@router.get("/active")
async def get_active_connections(
    connector_service: ConnectorService = Depends(get_connector_service)
):
    """
    Get list of active connections
    
    Args:
        connector_service: Connector service dependency
        
    Returns:
        List of active connection IDs
    """
    try:
        active_connections = connector_service.get_active_connections()
        
        return {
            "active_connections": active_connections,
            "count": len(active_connections)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get active connections: {str(e)}"
        )


@router.post("/disconnect/{target_system_id}")
async def disconnect_target(
    target_system_id: str,
    connector_service: ConnectorService = Depends(get_connector_service)
):
    """
    Disconnect from a specific target system
    
    Args:
        target_system_id: ID of the target system to disconnect
        connector_service: Connector service dependency
        
    Returns:
        Disconnection result
    """
    try:
        await connector_service.disconnect_target(target_system_id)
        
        return {
            "message": f"Disconnected from target system {target_system_id}",
            "target_system_id": target_system_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disconnect from target: {str(e)}"
        )


@router.post("/disconnect-all")
async def disconnect_all_targets(
    connector_service: ConnectorService = Depends(get_connector_service)
):
    """
    Disconnect from all active target systems
    
    Args:
        connector_service: Connector service dependency
        
    Returns:
        Disconnection result
    """
    try:
        active_connections = connector_service.get_active_connections()
        await connector_service.disconnect_all()
        
        return {
            "message": "Disconnected from all target systems",
            "disconnected_count": len(active_connections),
            "disconnected_targets": active_connections
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disconnect from all targets: {str(e)}"
        )