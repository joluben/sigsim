"""
Target System business logic service
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.target_repository import TargetSystemRepository
from app.repositories.device_repository import DeviceRepository
from app.models.target import TargetSystemCreate, TargetSystemResponse, TargetSystemUpdate, TargetType
from app.utils.logger import app_logger


class TargetSystemService:
    def __init__(self, db: Session):
        self.repository = TargetSystemRepository(db)
        self.device_repository = DeviceRepository(db)
        self.logger = app_logger
    
    async def get_all_target_systems(self, skip: int = 0, limit: int = 100) -> List[TargetSystemResponse]:
        """Get all target systems with pagination"""
        try:
            targets = await self.repository.get_all(skip, limit)
            return [TargetSystemResponse.from_orm(target) for target in targets]
        except Exception as e:
            self.logger.error(f"Error getting all target systems: {e}")
            return []
    
    async def get_target_system_by_id(self, target_id: str) -> Optional[TargetSystemResponse]:
        """Get target system by ID"""
        try:
            target = await self.repository.get_by_id(target_id)
            if target:
                return TargetSystemResponse.from_orm(target)
            return None
        except Exception as e:
            self.logger.error(f"Error getting target system {target_id}: {e}")
            return None
    
    async def create_target_system(self, target_data: TargetSystemCreate) -> Optional[TargetSystemResponse]:
        """Create a new target system"""
        try:
            # Check if name already exists
            if await self.repository.name_exists(target_data.name):
                self.logger.warning(f"Target system name already exists: {target_data.name}")
                return None
            
            target = await self.repository.create(target_data.dict())
            if target:
                self.logger.info(f"Created target system: {target.name}")
                return TargetSystemResponse.from_orm(target)
            return None
        except Exception as e:
            self.logger.error(f"Error creating target system: {e}")
            return None
    
    async def update_target_system(self, target_id: str, target_data: TargetSystemUpdate) -> Optional[TargetSystemResponse]:
        """Update a target system"""
        try:
            # Filter out None values
            update_data = {k: v for k, v in target_data.dict().items() if v is not None}
            if not update_data:
                return await self.get_target_system_by_id(target_id)
            
            # Check if new name already exists (if name is being updated)
            if 'name' in update_data:
                if await self.repository.name_exists(update_data['name'], exclude_id=target_id):
                    self.logger.warning(f"Target system name already exists: {update_data['name']}")
                    return None
            
            target = await self.repository.update(target_id, update_data)
            if target:
                self.logger.info(f"Updated target system: {target_id}")
                return TargetSystemResponse.from_orm(target)
            return None
        except Exception as e:
            self.logger.error(f"Error updating target system {target_id}: {e}")
            return None
    
    async def delete_target_system(self, target_id: str) -> bool:
        """Delete a target system"""
        try:
            success = await self.repository.delete(target_id)
            if success:
                self.logger.info(f"Deleted target system: {target_id}")
            return success
        except Exception as e:
            self.logger.error(f"Error deleting target system {target_id}: {e}")
            return False
    
    async def get_target_systems_by_type(self, target_type: TargetType, skip: int = 0, limit: int = 100) -> List[TargetSystemResponse]:
        """Get target systems by type"""
        try:
            targets = await self.repository.get_by_type(target_type, skip, limit)
            return [TargetSystemResponse.from_orm(target) for target in targets]
        except Exception as e:
            self.logger.error(f"Error getting target systems by type {target_type}: {e}")
            return []
    
    async def search_target_systems(self, search_term: str, skip: int = 0, limit: int = 100) -> List[TargetSystemResponse]:
        """Search target systems by name"""
        try:
            targets = await self.repository.search_by_name(search_term, skip, limit)
            return [TargetSystemResponse.from_orm(target) for target in targets]
        except Exception as e:
            self.logger.error(f"Error searching target systems: {e}")
            return []
    
    async def get_recent_target_systems(self, limit: int = 10) -> List[TargetSystemResponse]:
        """Get most recently created target systems"""
        try:
            targets = await self.repository.get_recent_target_systems(limit)
            return [TargetSystemResponse.from_orm(target) for target in targets]
        except Exception as e:
            self.logger.error(f"Error getting recent target systems: {e}")
            return []
    
    async def get_target_system_stats(self) -> Dict[str, int]:
        """Get target system statistics by type"""
        try:
            stats = {}
            for target_type in TargetType:
                count = await self.repository.count_by_type(target_type)
                stats[target_type.value] = count
            
            total = await self.repository.get_count()
            stats['total'] = total
            
            return stats
        except Exception as e:
            self.logger.error(f"Error getting target system stats: {e}")
            return {}
    
    async def is_target_system_in_use(self, target_id: str) -> bool:
        """Check if target system is being used by any devices"""
        try:
            devices = await self.device_repository.get_by_target_system_id(target_id)
            return len(devices) > 0
        except Exception as e:
            self.logger.error(f"Error checking if target system is in use {target_id}: {e}")
            return False
    
    async def test_connection(self, target_id: str) -> Dict[str, Any]:
        """Test connection to a target system"""
        try:
            target = await self.repository.get_by_id(target_id)
            if not target:
                return {"success": False, "message": "Target system not found"}
            
            # Import connectors
            from app.simulation.connectors.http_connector import HTTPConnector
            from app.simulation.connectors.mqtt_connector import MQTTConnector
            from app.simulation.connectors.kafka_connector import KafkaConnector
            from app.simulation.connectors.websocket_connector import WebSocketConnector
            
            connector = None
            
            if target.type == TargetType.HTTP:
                from app.models.target import HTTPConfig
                config = HTTPConfig(**target.config)
                connector = HTTPConnector(config)
            elif target.type == TargetType.MQTT:
                from app.models.target import MQTTConfig
                config = MQTTConfig(**target.config)
                connector = MQTTConnector(config)
            elif target.type == TargetType.KAFKA:
                from app.models.target import KafkaConfig
                config = KafkaConfig(**target.config)
                connector = KafkaConnector(config)
            elif target.type == TargetType.WEBSOCKET:
                from app.models.target import WebSocketConfig
                config = WebSocketConfig(**target.config)
                connector = WebSocketConnector(config)
            else:
                return {"success": False, "message": f"Connection test not supported for {target.type}"}
            
            # Test connection
            if connector:
                success = await connector.connect()
                if success:
                    await connector.disconnect()
                    return {"success": True, "message": "Connection successful"}
                else:
                    return {"success": False, "message": "Connection failed"}
            
            return {"success": False, "message": "Could not create connector"}
            
        except Exception as e:
            self.logger.error(f"Error testing connection for target system {target_id}: {e}")
            return {"success": False, "message": f"Connection test failed: {str(e)}"}