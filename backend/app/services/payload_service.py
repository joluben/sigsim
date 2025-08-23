"""
Payload business logic service
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.payload_repository import PayloadRepository
from app.repositories.device_repository import DeviceRepository
from app.models.payload import PayloadCreate, PayloadResponse, PayloadUpdate, PayloadType
from app.utils.logger import app_logger


class PayloadService:
    def __init__(self, db: Session):
        self.repository = PayloadRepository(db)
        self.device_repository = DeviceRepository(db)
        self.logger = app_logger
    
    async def get_all_payloads(self, skip: int = 0, limit: int = 100) -> List[PayloadResponse]:
        """Get all payloads with pagination"""
        try:
            payloads = await self.repository.get_all(skip, limit)
            return [PayloadResponse.from_orm(payload) for payload in payloads]
        except Exception as e:
            self.logger.error(f"Error getting all payloads: {e}")
            return []
    
    async def get_payload_by_id(self, payload_id: str) -> Optional[PayloadResponse]:
        """Get payload by ID"""
        try:
            payload = await self.repository.get_by_id(payload_id)
            if payload:
                return PayloadResponse.from_orm(payload)
            return None
        except Exception as e:
            self.logger.error(f"Error getting payload {payload_id}: {e}")
            return None
    
    async def create_payload(self, payload_data: PayloadCreate) -> Optional[PayloadResponse]:
        """Create a new payload"""
        try:
            # Check if name already exists
            if await self.repository.name_exists(payload_data.name):
                self.logger.warning(f"Payload name already exists: {payload_data.name}")
                return None
            
            payload = await self.repository.create(payload_data.dict())
            if payload:
                self.logger.info(f"Created payload: {payload.name}")
                return PayloadResponse.from_orm(payload)
            return None
        except Exception as e:
            self.logger.error(f"Error creating payload: {e}")
            return None
    
    async def update_payload(self, payload_id: str, payload_data: PayloadUpdate) -> Optional[PayloadResponse]:
        """Update a payload"""
        try:
            # Filter out None values
            update_data = {k: v for k, v in payload_data.dict().items() if v is not None}
            if not update_data:
                return await self.get_payload_by_id(payload_id)
            
            # Check if new name already exists (if name is being updated)
            if 'name' in update_data:
                if await self.repository.name_exists(update_data['name'], exclude_id=payload_id):
                    self.logger.warning(f"Payload name already exists: {update_data['name']}")
                    return None
            
            payload = await self.repository.update(payload_id, update_data)
            if payload:
                self.logger.info(f"Updated payload: {payload_id}")
                return PayloadResponse.from_orm(payload)
            return None
        except Exception as e:
            self.logger.error(f"Error updating payload {payload_id}: {e}")
            return None
    
    async def delete_payload(self, payload_id: str) -> bool:
        """Delete a payload"""
        try:
            success = await self.repository.delete(payload_id)
            if success:
                self.logger.info(f"Deleted payload: {payload_id}")
            return success
        except Exception as e:
            self.logger.error(f"Error deleting payload {payload_id}: {e}")
            return False
    
    async def get_payloads_by_type(self, payload_type: PayloadType, skip: int = 0, limit: int = 100) -> List[PayloadResponse]:
        """Get payloads by type"""
        try:
            payloads = await self.repository.get_by_type(payload_type, skip, limit)
            return [PayloadResponse.from_orm(payload) for payload in payloads]
        except Exception as e:
            self.logger.error(f"Error getting payloads by type {payload_type}: {e}")
            return []
    
    async def search_payloads(self, search_term: str, skip: int = 0, limit: int = 100) -> List[PayloadResponse]:
        """Search payloads by name"""
        try:
            payloads = await self.repository.search_by_name(search_term, skip, limit)
            return [PayloadResponse.from_orm(payload) for payload in payloads]
        except Exception as e:
            self.logger.error(f"Error searching payloads: {e}")
            return []
    
    async def get_recent_payloads(self, limit: int = 10) -> List[PayloadResponse]:
        """Get most recently created payloads"""
        try:
            payloads = await self.repository.get_recent_payloads(limit)
            return [PayloadResponse.from_orm(payload) for payload in payloads]
        except Exception as e:
            self.logger.error(f"Error getting recent payloads: {e}")
            return []
    
    async def get_payload_stats(self) -> Dict[str, int]:
        """Get payload statistics by type"""
        try:
            stats = {}
            for payload_type in PayloadType:
                count = await self.repository.count_by_type(payload_type)
                stats[payload_type.value] = count
            
            total = await self.repository.get_count()
            stats['total'] = total
            
            return stats
        except Exception as e:
            self.logger.error(f"Error getting payload stats: {e}")
            return {}
    
    async def is_payload_in_use(self, payload_id: str) -> bool:
        """Check if payload is being used by any devices"""
        try:
            devices = await self.device_repository.get_by_payload_id(payload_id)
            return len(devices) > 0
        except Exception as e:
            self.logger.error(f"Error checking if payload is in use {payload_id}: {e}")
            return False
    
    async def test_payload_generation(self, payload_id: str, test_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Test payload generation"""
        try:
            payload = await self.repository.get_by_id(payload_id)
            if not payload:
                raise ValueError("Payload not found")
            
            # Import payload generators
            from app.simulation.payload_generators.json_builder import JsonBuilderGenerator
            from app.simulation.payload_generators.python_runner import PythonCodeGenerator
            
            if payload.type == PayloadType.VISUAL:
                if not payload.schema:
                    raise ValueError("Visual payload missing schema")
                generator = JsonBuilderGenerator(payload.schema)
            elif payload.type == PayloadType.PYTHON:
                if not payload.python_code:
                    raise ValueError("Python payload missing code")
                generator = PythonCodeGenerator(payload.python_code)
            else:
                raise ValueError(f"Unsupported payload type: {payload.type}")
            
            # Generate test payload
            result = await generator.generate(test_metadata)
            return result
            
        except Exception as e:
            self.logger.error(f"Error testing payload generation {payload_id}: {e}")
            raise