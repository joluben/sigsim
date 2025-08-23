"""
Device repository for data access
"""
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, and_
from app.repositories.base_repository import BaseRepository
from app.schemas.database import Device, Payload, TargetSystem


class DeviceRepository(BaseRepository[Device]):
    def __init__(self, db: Session):
        super().__init__(db, Device)
    
    async def get_by_project_id(self, project_id: str, skip: int = 0, limit: int = 100) -> List[Device]:
        """Get all devices for a project with pagination"""
        try:
            return (
                self.db.query(Device)
                .filter(Device.project_id == project_id)
                .offset(skip)
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting devices for project {project_id}: {e}")
            return []
    
    async def get_enabled_by_project_id(self, project_id: str) -> List[Device]:
        """Get all enabled devices for a project"""
        try:
            return (
                self.db.query(Device)
                .filter(and_(Device.project_id == project_id, Device.is_enabled == True))
                .all()
            )
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting enabled devices for project {project_id}: {e}")
            return []
    
    async def get_with_relations(self, device_id: str) -> Optional[Device]:
        """Get device with payload and target system loaded"""
        try:
            return (
                self.db.query(Device)
                .options(
                    joinedload(Device.payload),
                    joinedload(Device.target_system)
                )
                .filter(Device.id == device_id)
                .first()
            )
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting device with relations {device_id}: {e}")
            return None
    
    async def get_devices_with_relations_by_project(self, project_id: str) -> List[Device]:
        """Get all devices for a project with payload and target system loaded"""
        try:
            return (
                self.db.query(Device)
                .options(
                    joinedload(Device.payload),
                    joinedload(Device.target_system)
                )
                .filter(Device.project_id == project_id)
                .all()
            )
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting devices with relations for project {project_id}: {e}")
            return []
    
    async def count_by_project_id(self, project_id: str) -> int:
        """Count devices in a project"""
        try:
            return (
                self.db.query(Device)
                .filter(Device.project_id == project_id)
                .count()
            )
        except SQLAlchemyError as e:
            self.logger.error(f"Error counting devices for project {project_id}: {e}")
            return 0
    
    async def count_enabled_by_project_id(self, project_id: str) -> int:
        """Count enabled devices in a project"""
        try:
            return (
                self.db.query(Device)
                .filter(and_(Device.project_id == project_id, Device.is_enabled == True))
                .count()
            )
        except SQLAlchemyError as e:
            self.logger.error(f"Error counting enabled devices for project {project_id}: {e}")
            return 0
    
    async def get_by_payload_id(self, payload_id: str) -> List[Device]:
        """Get all devices using a specific payload"""
        try:
            return (
                self.db.query(Device)
                .filter(Device.payload_id == payload_id)
                .all()
            )
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting devices by payload {payload_id}: {e}")
            return []
    
    async def get_by_target_system_id(self, target_system_id: str) -> List[Device]:
        """Get all devices using a specific target system"""
        try:
            return (
                self.db.query(Device)
                .filter(Device.target_system_id == target_system_id)
                .all()
            )
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting devices by target system {target_system_id}: {e}")
            return []
    
    async def search_by_name_in_project(self, project_id: str, search_term: str) -> List[Device]:
        """Search devices by name within a project"""
        try:
            return (
                self.db.query(Device)
                .filter(
                    and_(
                        Device.project_id == project_id,
                        Device.name.ilike(f"%{search_term}%")
                    )
                )
                .all()
            )
        except SQLAlchemyError as e:
            self.logger.error(f"Error searching devices by name in project {project_id}: {e}")
            return []
    
    async def bulk_update_enabled_status(self, device_ids: List[str], is_enabled: bool) -> int:
        """Bulk update enabled status for multiple devices"""
        try:
            updated_count = (
                self.db.query(Device)
                .filter(Device.id.in_(device_ids))
                .update({"is_enabled": is_enabled}, synchronize_session=False)
            )
            self.db.commit()
            self.logger.info(f"Bulk updated {updated_count} devices enabled status to {is_enabled}")
            return updated_count
        except SQLAlchemyError as e:
            self.db.rollback()
            self.logger.error(f"Error bulk updating device enabled status: {e}")
            return 0