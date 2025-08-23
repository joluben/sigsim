"""
Enhanced simulation service using connector factory
"""
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.project_repository import ProjectRepository
from app.repositories.device_repository import DeviceRepository
from app.repositories.payload_repository import PayloadRepository
from app.repositories.target_repository import TargetRepository
from app.services.connector_service import ConnectorService
from app.simulation.engine import SimulationEngine, SimulationProject
from app.simulation.device_simulator import DeviceSimulator
from app.simulation.payload_generators import PayloadGeneratorFactory
from app.models.simulation import SimulationStatus, SimulationLogEntry


class EnhancedSimulationService:
    """Enhanced simulation service with connector factory integration"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.project_repository = ProjectRepository(db)
        self.device_repository = DeviceRepository(db)
        self.payload_repository = PayloadRepository(db)
        self.target_repository = TargetRepository(db)
        self.connector_service = ConnectorService(self.target_repository)
        self.engine = SimulationEngine.get_instance()
    
    async def start_project_simulation(self, project_id: str) -> bool:
        """
        Start simulation for a project with all its devices
        
        Args:
            project_id: ID of the project to simulate
            
        Returns:
            True if simulation started successfully, False otherwise
        """
        try:
            # Check if already running
            if project_id in self.engine.running_projects:
                return False
            
            # Get project and its devices
            project = await self.project_repository.get_by_id(project_id)
            if not project:
                raise ValueError(f"Project not found: {project_id}")
            
            devices = await self.device_repository.get_by_project_id(project_id)
            if not devices:
                raise ValueError(f"No devices found for project: {project_id}")
            
            # Create simulation project
            sim_project = SimulationProject(project_id)
            sim_project.started_at = datetime.utcnow()
            
            # Create device simulators
            for device in devices:
                if not device.is_enabled:
                    continue
                
                try:
                    # Create payload generator
                    payload = await self.payload_repository.get_by_id(device.payload_id)
                    if not payload:
                        print(f"Payload not found for device {device.id}, skipping")
                        continue
                    
                    payload_generator = PayloadGeneratorFactory.create_generator(
                        payload.type, payload.config
                    )
                    
                    # Create target connector using connector service
                    connector = await self.connector_service.create_connector(device.target_system_id)
                    
                    # Create device simulator
                    device_simulator = DeviceSimulator(
                        device_config=device,
                        payload_generator=payload_generator,
                        target_connector=connector,
                        log_callback=lambda log_entry: sim_project.notify_observers(log_entry)
                    )
                    
                    sim_project.device_simulators.append(device_simulator)
                    
                except Exception as e:
                    print(f"Error creating simulator for device {device.id}: {e}")
                    continue
            
            if not sim_project.device_simulators:
                raise ValueError("No valid device simulators could be created")
            
            # Start simulation
            await sim_project.start_all_devices()
            self.engine.running_projects[project_id] = sim_project
            
            # Update project status in database
            await self.project_repository.update(project_id, {"is_running": True})
            
            return True
            
        except Exception as e:
            print(f"Error starting simulation for project {project_id}: {e}")
            return False
    
    async def stop_project_simulation(self, project_id: str) -> bool:
        """
        Stop simulation for a project
        
        Args:
            project_id: ID of the project to stop
            
        Returns:
            True if simulation stopped successfully, False otherwise
        """
        try:
            if project_id not in self.engine.running_projects:
                return False
            
            sim_project = self.engine.running_projects[project_id]
            await sim_project.stop_all_devices()
            
            # Disconnect all connectors for this project
            for simulator in sim_project.device_simulators:
                try:
                    await simulator.connector.disconnect()
                except:
                    pass  # Ignore disconnect errors
            
            del self.engine.running_projects[project_id]
            
            # Update project status in database
            await self.project_repository.update(project_id, {"is_running": False})
            
            return True
            
        except Exception as e:
            print(f"Error stopping simulation for project {project_id}: {e}")
            return False
    
    async def get_project_simulation_status(self, project_id: str) -> SimulationStatus:
        """
        Get detailed simulation status for a project
        
        Args:
            project_id: ID of the project
            
        Returns:
            SimulationStatus object with current status
        """
        if project_id not in self.engine.running_projects:
            # Get project info from database
            project = await self.project_repository.get_by_id(project_id)
            devices = await self.device_repository.get_by_project_id(project_id)
            
            return SimulationStatus(
                project_id=project_id,
                is_running=False,
                active_devices=0,
                total_devices=len([d for d in devices if d.is_enabled]) if devices else 0,
                messages_sent=0,
                devices=[],
                errors=[]
            )
        
        sim_project = self.engine.running_projects[project_id]
        
        # Collect device statuses
        device_statuses = []
        total_messages = 0
        errors = []
        
        for simulator in sim_project.device_simulators:
            status = simulator.get_status()
            device_statuses.append(status)
            total_messages += status.get('messages_sent', 0)
            
            if status.get('error'):
                errors.append({
                    'device_id': status['device_id'],
                    'device_name': status['device_name'],
                    'error': status['error']
                })
        
        return SimulationStatus(
            project_id=project_id,
            is_running=sim_project.is_running,
            active_devices=len([s for s in sim_project.device_simulators if s.is_running]),
            total_devices=len(sim_project.device_simulators),
            messages_sent=total_messages,
            started_at=sim_project.started_at,
            devices=device_statuses,
            errors=errors
        )
    
    async def get_all_simulations_status(self) -> List[SimulationStatus]:
        """
        Get status of all running simulations
        
        Returns:
            List of SimulationStatus objects
        """
        statuses = []
        
        for project_id in self.engine.running_projects.keys():
            status = await self.get_project_simulation_status(project_id)
            statuses.append(status)
        
        return statuses
    
    async def emergency_stop_all(self) -> List[str]:
        """
        Emergency stop all running simulations
        
        Returns:
            List of project IDs that were stopped
        """
        stopped_projects = []
        
        # Get list of running projects to avoid modifying dict during iteration
        running_project_ids = list(self.engine.running_projects.keys())
        
        for project_id in running_project_ids:
            try:
                success = await self.stop_project_simulation(project_id)
                if success:
                    stopped_projects.append(project_id)
            except Exception as e:
                print(f"Error stopping project {project_id} during emergency stop: {e}")
                # Continue with other projects even if one fails
                continue
        
        return stopped_projects
    
    async def validate_project_for_simulation(self, project_id: str) -> Dict[str, any]:
        """
        Validate if a project is ready for simulation
        
        Args:
            project_id: ID of the project to validate
            
        Returns:
            Dictionary with validation results
        """
        try:
            project = await self.project_repository.get_by_id(project_id)
            if not project:
                return {
                    'valid': False,
                    'errors': ['Project not found'],
                    'warnings': []
                }
            
            devices = await self.device_repository.get_by_project_id(project_id)
            if not devices:
                return {
                    'valid': False,
                    'errors': ['No devices found in project'],
                    'warnings': []
                }
            
            errors = []
            warnings = []
            valid_devices = 0
            
            for device in devices:
                if not device.is_enabled:
                    continue
                
                # Check payload
                if not device.payload_id:
                    errors.append(f"Device '{device.name}' has no payload generator assigned")
                    continue
                
                payload = await self.payload_repository.get_by_id(device.payload_id)
                if not payload:
                    errors.append(f"Device '{device.name}' has invalid payload generator")
                    continue
                
                # Check target system
                if not device.target_system_id:
                    errors.append(f"Device '{device.name}' has no target system assigned")
                    continue
                
                target = await self.target_repository.get_by_id(device.target_system_id)
                if not target:
                    errors.append(f"Device '{device.name}' has invalid target system")
                    continue
                
                # Check send interval
                if device.send_interval <= 0:
                    errors.append(f"Device '{device.name}' has invalid send interval")
                    continue
                
                if device.send_interval < 5:
                    warnings.append(f"Device '{device.name}' has very short send interval ({device.send_interval}s)")
                
                valid_devices += 1
            
            if valid_devices == 0:
                errors.append('No valid devices found for simulation')
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings,
                'valid_devices': valid_devices,
                'total_devices': len([d for d in devices if d.is_enabled])
            }
            
        except Exception as e:
            return {
                'valid': False,
                'errors': [f'Validation error: {str(e)}'],
                'warnings': []
            }
    
    async def test_device_configuration(self, device_id: str) -> Dict[str, any]:
        """
        Test configuration for a specific device
        
        Args:
            device_id: ID of the device to test
            
        Returns:
            Dictionary with test results
        """
        try:
            device = await self.device_repository.get_by_id(device_id)
            if not device:
                return {
                    'success': False,
                    'error': 'Device not found'
                }
            
            # Test payload generation
            if not device.payload_id:
                return {
                    'success': False,
                    'error': 'No payload generator assigned'
                }
            
            payload = await self.payload_repository.get_by_id(device.payload_id)
            if not payload:
                return {
                    'success': False,
                    'error': 'Payload generator not found'
                }
            
            try:
                payload_generator = PayloadGeneratorFactory.create_generator(
                    payload.type, payload.config
                )
                test_payload = await payload_generator.generate(device_metadata=device.metadata)
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Payload generation failed: {str(e)}'
                }
            
            # Test target connection
            if not device.target_system_id:
                return {
                    'success': False,
                    'error': 'No target system assigned'
                }
            
            connection_test = await self.connector_service.test_connection(device.target_system_id)
            
            if connection_test['success']:
                return {
                    'success': True,
                    'message': 'Device configuration test successful',
                    'payload': test_payload,
                    'target_info': connection_test
                }
            else:
                return {
                    'success': False,
                    'error': f"Target connection failed: {connection_test.get('error', 'Unknown error')}",
                    'payload': test_payload,
                    'details': connection_test
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Configuration test failed: {str(e)}'
            }