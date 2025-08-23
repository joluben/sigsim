"""
Device business logic service
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.device_repository import DeviceRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.payload_repository import PayloadRepository
from app.repositories.target_repository import TargetSystemRepository
from app.models.device import DeviceCreate, DeviceResponse, DeviceUpdate, DeviceSummary
from app.utils.logger import app_logger


class DeviceService:
    def __init__(self, db: Session):
        self.repository = DeviceRepository(db)
        self.project_repository = ProjectRepository(db)
        self.payload_repository = PayloadRepository(db)
        self.target_repository = TargetSystemRepository(db)
        self.logger = app_logger
    
    async def get_devices_by_project(self, project_id: str, skip: int = 0, limit: int = 100) -> List[DeviceSummary]:
        """Get all devices for a project with pagination"""
        try:
            devices = await self.repository.get_by_project_id(project_id, skip, limit)
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
        except Exception as e:
            self.logger.error(f"Error getting devices for project {project_id}: {e}")
            return []
    
    async def get_device_by_id(self, device_id: str) -> Optional[DeviceResponse]:
        """Get device by ID"""
        try:
            device = await self.repository.get_by_id(device_id)
            if device:
                return DeviceResponse.from_orm(device)
            return None
        except Exception as e:
            self.logger.error(f"Error getting device {device_id}: {e}")
            return None
    
    async def create_device(self, device_data: DeviceCreate) -> Optional[DeviceResponse]:
        """Create a new device"""
        try:
            # Validate project exists
            if not await self.project_repository.exists(device_data.project_id):
                self.logger.warning(f"Project not found: {device_data.project_id}")
                return None
            
            # Validate payload exists (if provided)
            if device_data.payload_id and not await self.payload_repository.exists(device_data.payload_id):
                self.logger.warning(f"Payload not found: {device_data.payload_id}")
                return None
            
            # Validate target system exists (if provided)
            if device_data.target_system_id and not await self.target_repository.exists(device_data.target_system_id):
                self.logger.warning(f"Target system not found: {device_data.target_system_id}")
                return None
            
            device = await self.repository.create(device_data.dict())
            if device:
                self.logger.info(f"Created device: {device.name} in project {device_data.project_id}")
                return DeviceResponse.from_orm(device)
            return None
        except Exception as e:
            self.logger.error(f"Error creating device: {e}")
            return None
    
    async def update_device(self, device_id: str, device_data: DeviceUpdate) -> Optional[DeviceResponse]:
        """Update a device"""
        try:
            # Filter out None values
            update_data = {k: v for k, v in device_data.dict().items() if v is not None}
            if not update_data:
                return await self.get_device_by_id(device_id)
            
            # Validate payload exists (if being updated)
            if 'payload_id' in update_data and update_data['payload_id']:
                if not await self.payload_repository.exists(update_data['payload_id']):
                    self.logger.warning(f"Payload not found: {update_data['payload_id']}")
                    return None
            
            # Validate target system exists (if being updated)
            if 'target_system_id' in update_data and update_data['target_system_id']:
                if not await self.target_repository.exists(update_data['target_system_id']):
                    self.logger.warning(f"Target system not found: {update_data['target_system_id']}")
                    return None
            
            device = await self.repository.update(device_id, update_data)
            if device:
                self.logger.info(f"Updated device: {device_id}")
                return DeviceResponse.from_orm(device)
            return None
        except Exception as e:
            self.logger.error(f"Error updating device {device_id}: {e}")
            return None
    
    async def delete_device(self, device_id: str) -> bool:
        """Delete a device"""
        try:
            # TODO: Check if device is part of running simulation and handle appropriately
            success = await self.repository.delete(device_id)
            if success:
                self.logger.info(f"Deleted device: {device_id}")
            return success
        except Exception as e:
            self.logger.error(f"Error deleting device {device_id}: {e}")
            return False
    
    async def get_enabled_devices_by_project(self, project_id: str) -> List[DeviceResponse]:
        """Get all enabled devices for a project"""
        try:
            devices = await self.repository.get_enabled_by_project_id(project_id)
            return [DeviceResponse.from_orm(device) for device in devices]
        except Exception as e:
            self.logger.error(f"Error getting enabled devices for project {project_id}: {e}")
            return []
    
    async def get_devices_with_relations_by_project(self, project_id: str) -> List[DeviceResponse]:
        """Get all devices for a project with payload and target system loaded"""
        try:
            devices = await self.repository.get_devices_with_relations_by_project(project_id)
            return [DeviceResponse.from_orm(device) for device in devices]
        except Exception as e:
            self.logger.error(f"Error getting devices with relations for project {project_id}: {e}")
            return []
    
    async def search_devices_in_project(self, project_id: str, search_term: str) -> List[DeviceSummary]:
        """Search devices by name within a project"""
        try:
            devices = await self.repository.search_by_name_in_project(project_id, search_term)
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
        except Exception as e:
            self.logger.error(f"Error searching devices in project {project_id}: {e}")
            return []
    
    async def bulk_update_enabled_status(self, device_ids: List[str], is_enabled: bool) -> int:
        """Bulk update enabled status for multiple devices"""
        try:
            updated_count = await self.repository.bulk_update_enabled_status(device_ids, is_enabled)
            self.logger.info(f"Bulk updated {updated_count} devices enabled status to {is_enabled}")
            return updated_count
        except Exception as e:
            self.logger.error(f"Error bulk updating device enabled status: {e}")
            return 0
    
    async def get_device_count_by_project(self, project_id: str) -> dict:
        """Get device count statistics for a project"""
        try:
            total_count = await self.repository.count_by_project_id(project_id)
            enabled_count = await self.repository.count_enabled_by_project_id(project_id)
            
            return {
                'total': total_count,
                'enabled': enabled_count,
                'disabled': total_count - enabled_count
            }
        except Exception as e:
            self.logger.error(f"Error getting device count for project {project_id}: {e}")
            return {'total': 0, 'enabled': 0, 'disabled': 0}