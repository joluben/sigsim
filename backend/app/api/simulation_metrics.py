"""
API endpoints for simulation metrics
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from app.simulation.metrics import metrics_collector

router = APIRouter(prefix="/api/simulation/metrics", tags=["simulation-metrics"])


@router.get("/")
async def get_all_metrics() -> Dict[str, Any]:
    """
    Get all simulation metrics
    
    Returns:
        Dictionary containing all collected metrics
    """
    try:
        return metrics_collector.get_all_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


@router.get("/project/{project_id}")
async def get_project_metrics(project_id: str) -> Dict[str, Any]:
    """
    Get metrics for a specific project
    
    Args:
        project_id: Project identifier
        
    Returns:
        Dictionary containing project metrics
    """
    try:
        return metrics_collector.get_project_summary(project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get project metrics: {str(e)}")


@router.get("/connectors")
async def get_connector_metrics() -> Dict[str, Any]:
    """
    Get metrics for all connectors
    
    Returns:
        Dictionary containing connector metrics
    """
    try:
        all_metrics = metrics_collector.get_all_metrics()
        return all_metrics.get("connectors", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get connector metrics: {str(e)}")


@router.get("/devices")
async def get_device_metrics() -> Dict[str, Any]:
    """
    Get metrics for all devices
    
    Returns:
        Dictionary containing device metrics
    """
    try:
        all_metrics = metrics_collector.get_all_metrics()
        return all_metrics.get("devices", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get device metrics: {str(e)}")


@router.get("/devices/{device_id}")
async def get_device_metrics_by_id(device_id: str) -> Dict[str, Any]:
    """
    Get metrics for a specific device
    
    Args:
        device_id: Device identifier
        
    Returns:
        Dictionary containing device metrics
    """
    try:
        if device_id not in metrics_collector.device_metrics:
            raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
        
        return metrics_collector.device_metrics[device_id].to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get device metrics: {str(e)}")


@router.delete("/reset")
async def reset_all_metrics() -> Dict[str, str]:
    """
    Reset all metrics
    
    Returns:
        Success message
    """
    try:
        metrics_collector.reset_metrics()
        return {"message": "All metrics reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset metrics: {str(e)}")


@router.delete("/reset/project/{project_id}")
async def reset_project_metrics(project_id: str) -> Dict[str, str]:
    """
    Reset metrics for a specific project
    
    Args:
        project_id: Project identifier
        
    Returns:
        Success message
    """
    try:
        metrics_collector.reset_metrics(project_id)
        return {"message": f"Metrics for project {project_id} reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset project metrics: {str(e)}")


@router.get("/health")
async def get_metrics_health() -> Dict[str, Any]:
    """
    Get health status of metrics collection
    
    Returns:
        Health status information
    """
    try:
        all_metrics = metrics_collector.get_all_metrics()
        system_metrics = all_metrics.get("system", {})
        
        return {
            "status": "healthy",
            "uptime_seconds": system_metrics.get("uptime_seconds", 0),
            "total_connectors": system_metrics.get("total_connectors", 0),
            "total_devices": system_metrics.get("total_devices", 0),
            "metrics_collection_active": True
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "metrics_collection_active": False
        }