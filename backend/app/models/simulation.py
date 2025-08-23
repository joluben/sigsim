"""
Simulation Pydantic models for API validation
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class SimulationError(BaseModel):
    device_id: str
    error_message: str
    timestamp: datetime


class DeviceStatus(BaseModel):
    device_id: str
    device_name: str
    is_running: bool
    messages_sent: int
    last_message_at: Optional[datetime] = None
    error: Optional[str] = None


class SimulationStatus(BaseModel):
    project_id: str
    is_running: bool
    active_devices: int
    total_devices: int
    messages_sent: int
    started_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    devices: List[DeviceStatus] = []
    errors: List[SimulationError] = []


class SimulationLogEntry(BaseModel):
    timestamp: datetime
    device_id: str
    device_name: str
    event_type: str  # "message_sent", "error", "started", "stopped"
    message: str
    payload: Optional[dict] = None