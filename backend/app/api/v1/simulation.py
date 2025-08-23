"""
Simulation control API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.simulation_service import EnhancedSimulationService
from app.models.simulation import SimulationStatus

router = APIRouter()


@router.post("/{project_id}/start")
async def start_simulation(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Start simulation for a project"""
    service = EnhancedSimulationService(db)
    success = await service.start_project_simulation(project_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to start simulation"
        )
    return {"message": "Simulation started successfully", "project_id": project_id}


@router.post("/{project_id}/stop")
async def stop_simulation(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Stop simulation for a project"""
    service = EnhancedSimulationService(db)
    success = await service.stop_project_simulation(project_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to stop simulation"
        )
    return {"message": "Simulation stopped successfully", "project_id": project_id}


@router.get("/{project_id}/status", response_model=SimulationStatus)
async def get_simulation_status(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get simulation status for a project"""
    service = EnhancedSimulationService(db)
    status = await service.get_project_simulation_status(project_id)
    return status


@router.get("/status", response_model=List[SimulationStatus])
async def get_all_simulations_status(
    db: AsyncSession = Depends(get_db)
):
    """Get status of all running simulations"""
    service = EnhancedSimulationService(db)
    statuses = await service.get_all_simulations_status()
    return statuses


@router.get("/{project_id}/validate")
async def validate_project_for_simulation(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Validate if a project is ready for simulation"""
    service = EnhancedSimulationService(db)
    validation = await service.validate_project_for_simulation(project_id)
    return validation


@router.post("/devices/{device_id}/test")
async def test_device_configuration(
    device_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Test configuration for a specific device"""
    service = EnhancedSimulationService(db)
    result = await service.test_device_configuration(device_id)
    return result


@router.post("/connectors/test")
async def test_connector_configuration(
    target_type: str,
    config: dict,
    db: AsyncSession = Depends(get_db)
):
    """Test a connector configuration using the factory"""
    try:
        from app.simulation.connectors import ConnectorFactory, TargetType
        
        # Validate target type
        try:
            target_enum = TargetType(target_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported target type: {target_type}"
            )
        
        # Create connector using factory
        connector = ConnectorFactory.create_connector(target_enum, config)
        
        # Test connection
        connect_success = await connector.connect()
        if not connect_success:
            return {
                'success': False,
                'error': 'Failed to connect to target system',
                'details': 'Connection attempt failed'
            }
        
        # Test sending a sample payload
        test_payload = {
            'test': True,
            'timestamp': '2024-01-01T00:00:00Z',
            'message': 'Connection test from IoT Simulator'
        }
        
        send_success = await connector.send(test_payload)
        await connector.disconnect()
        
        if send_success:
            return {
                'success': True,
                'message': 'Connection test successful',
                'test_payload': test_payload
            }
        else:
            return {
                'success': False,
                'error': 'Failed to send test payload',
                'details': 'Send operation failed'
            }
            
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        return {
            'success': False,
            'error': f'Connection test failed: {str(e)}',
            'details': str(e)
        }


@router.get("/connectors/types")
async def get_supported_connector_types():
    """Get list of supported connector types"""
    from app.simulation.connectors import get_supported_connector_types
    return {
        'supported_types': get_supported_connector_types(),
        'message': 'List of supported target connector types'
    }


@router.get("/connectors/{target_type}/schema")
async def get_connector_config_schema(target_type: str):
    """Get configuration schema for a connector type"""
    try:
        from app.simulation.connectors import ConnectorFactory, TargetType
        
        target_enum = TargetType(target_type.lower())
        schema = ConnectorFactory.get_config_schema(target_enum)
        
        return {
            'target_type': target_type,
            'schema': schema,
            'message': f'Configuration schema for {target_type} connector'
        }
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported target type: {target_type}"
        )


@router.post("/emergency-stop")
async def emergency_stop_all_simulations(
    db: AsyncSession = Depends(get_db)
):
    """Emergency stop all running simulations"""
    service = EnhancedSimulationService(db)
    stopped_projects = await service.emergency_stop_all()
    return {
        "message": "Emergency stop completed",
        "stopped_projects": stopped_projects,
        "count": len(stopped_projects)
    }


@router.websocket("/{project_id}/logs")
async def simulation_logs_websocket(websocket: WebSocket, project_id: str):
    """WebSocket endpoint for real-time simulation logs"""
    await websocket.accept()
    
    try:
        from app.simulation.engine import SimulationEngine
        engine = SimulationEngine.get_instance()
        await engine.stream_logs(project_id, websocket)
    except Exception as e:
        await websocket.close(code=1000)