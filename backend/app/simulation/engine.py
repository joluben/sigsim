"""
Main simulation engine - orchestrates all simulations
"""
import asyncio
from datetime import datetime
from typing import Dict, Optional, List
from fastapi import WebSocket
from app.models.simulation import SimulationStatus, SimulationLogEntry
from app.simulation.device_simulator import DeviceSimulator
from app.simulation.connectors import ConnectorFactory
from app.models.target import TargetType
from app.repositories.project_repository import ProjectRepository
from app.repositories.device_repository import DeviceRepository
from app.repositories.target_repository import TargetRepository
from app.repositories.payload_repository import PayloadRepository
from app.simulation.payload_generators.visual_generator import VisualPayloadGenerator
from app.simulation.payload_generators.python_runner import PythonCodeGenerator
from app.models.payload import PayloadType


class SimulationProject:
    """Represents a running simulation project"""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.device_simulators: List[DeviceSimulator] = []
        self.tasks: List[asyncio.Task] = []
        self.is_running = False
        self.started_at = None
        self.observers: List[WebSocket] = []
    
    async def start_all_devices(self):
        """Start all device simulators"""
        self.is_running = True
        for simulator in self.device_simulators:
            task = asyncio.create_task(simulator.run())
            self.tasks.append(task)
    
    async def stop_all_devices(self):
        """Stop all device simulators"""
        self.is_running = False
        for task in self.tasks:
            task.cancel()
        
        # Wait for all tasks to complete
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
        
        self.tasks.clear()
    
    def add_observer(self, websocket: WebSocket):
        """Add WebSocket observer for logs"""
        self.observers.append(websocket)
    
    def remove_observer(self, websocket: WebSocket):
        """Remove WebSocket observer"""
        if websocket in self.observers:
            self.observers.remove(websocket)
    
    async def notify_observers(self, log_entry: SimulationLogEntry):
        """Notify all observers of a new log entry"""
        disconnected = []
        for websocket in self.observers:
            try:
                await websocket.send_json(log_entry.dict())
            except:
                disconnected.append(websocket)
        
        # Remove disconnected observers
        for ws in disconnected:
            self.remove_observer(ws)


class SimulationEngine:
    """Main simulation engine - singleton pattern"""
    
    _instance = None
    
    def __init__(self):
        self.running_projects: Dict[str, SimulationProject] = {}
    
    @classmethod
    def get_instance(cls):
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    async def start_project(
        self, 
        project_id: str,
        project_repository: ProjectRepository,
        device_repository: DeviceRepository,
        target_repository: TargetRepository,
        payload_repository: PayloadRepository
    ) -> bool:
        """Start simulation for a project"""
        if project_id in self.running_projects:
            return False  # Already running
        
        try:
            # Create simulation project
            sim_project = SimulationProject(project_id)
            
            # Load devices from database
            devices = await device_repository.get_by_project_id(project_id)
            
            for device in devices:
                # Create payload generator based on type
                if device.payload_id:
                    payload_config = await payload_repository.get_by_id(device.payload_id)
                    if payload_config:
                        if payload_config.type == PayloadType.VISUAL:
                            payload_generator = VisualPayloadGenerator(payload_config.schema)
                        elif payload_config.type == PayloadType.PYTHON:
                            try:
                                payload_generator = PythonCodeGenerator(payload_config.python_code)
                            except ValueError as e:
                                print(f"Error creating Python payload generator for device {device.id}: {e}")
                                continue  # Skip device with invalid Python code
                        else:
                            print(f"Unknown payload type for device {device.id}: {payload_config.type}")
                            continue
                    else:
                        continue  # Skip device without valid payload
                else:
                    continue  # Skip device without payload
                
                # Create target connector using factory
                if device.target_id:
                    target_system = await target_repository.get_by_id(device.target_id)
                    if target_system:
                        target_type = TargetType(target_system.type)
                        connector = ConnectorFactory.create_connector(target_type, target_system.config)
                    else:
                        continue  # Skip device without valid target
                else:
                    continue  # Skip device without target
                
                # Create device simulator with enhanced configuration
                device_simulator = DeviceSimulator(
                    device_config=device,
                    payload_generator=payload_generator,
                    target_connector=connector,
                    log_callback=lambda log_entry: asyncio.create_task(sim_project.notify_observers(log_entry)),
                    max_retries=3,
                    retry_delay=1.0,
                    max_consecutive_errors=10
                )
                
                sim_project.device_simulators.append(device_simulator)
            
            # Start simulation
            sim_project.started_at = datetime.utcnow()
            await sim_project.start_all_devices()
            
            self.running_projects[project_id] = sim_project
            return True
            
        except Exception as e:
            print(f"Error starting simulation for project {project_id}: {e}")
            return False
    
    async def stop_project(self, project_id: str) -> bool:
        """Stop simulation for a project"""
        if project_id not in self.running_projects:
            return False  # Not running
        
        try:
            sim_project = self.running_projects[project_id]
            await sim_project.stop_all_devices()
            del self.running_projects[project_id]
            return True
            
        except Exception as e:
            print(f"Error stopping simulation for project {project_id}: {e}")
            return False
    
    async def get_project_status(self, project_id: str) -> Optional[SimulationStatus]:
        """Get simulation status for a project"""
        if project_id not in self.running_projects:
            return SimulationStatus(
                project_id=project_id,
                is_running=False,
                active_devices=0,
                total_devices=0,
                messages_sent=0,
                devices=[],
                errors=[]
            )
        
        sim_project = self.running_projects[project_id]
        
        # Calculate statistics from device simulators
        total_messages = sum(simulator.stats.messages_sent for simulator in sim_project.device_simulators)
        active_devices = sum(1 for simulator in sim_project.device_simulators if simulator.is_running)
        
        # Get device statuses
        device_statuses = [simulator.get_status() for simulator in sim_project.device_simulators]
        
        # Collect errors from devices
        errors = []
        for simulator in sim_project.device_simulators:
            if simulator.stats.last_error:
                errors.append({
                    "device_id": simulator.config.id,
                    "device_name": simulator.config.name,
                    "error": simulator.stats.last_error,
                    "error_count": simulator.stats.errors
                })
        
        return SimulationStatus(
            project_id=project_id,
            is_running=sim_project.is_running,
            active_devices=active_devices,
            total_devices=len(sim_project.device_simulators),
            messages_sent=total_messages,
            started_at=sim_project.started_at,
            devices=device_statuses,
            errors=errors
        )
    
    async def stream_logs(self, project_id: str, websocket: WebSocket):
        """Stream simulation logs to WebSocket"""
        if project_id not in self.running_projects:
            await websocket.send_json({"error": "Project not running"})
            return
        
        sim_project = self.running_projects[project_id]
        sim_project.add_observer(websocket)
        
        try:
            # Keep connection alive
            while True:
                await asyncio.sleep(1)
        except:
            sim_project.remove_observer(websocket)