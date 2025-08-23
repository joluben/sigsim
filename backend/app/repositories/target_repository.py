"""
Target System repository for data access
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.repositories.base_repository import BaseRepository
from app.schemas.database import TargetSystem
from app.models.target import TargetType


class TargetSystemRepository(BaseRepository[TargetSystem]):
    def __init__(self, db: Session):
        super().__init__(db, TargetSystem)
    
    async def get_by_type(self, target_type: TargetType, skip: int = 0, limit: int = 100) -> List[TargetSystem]:
        """Get target systems by type"""
        try:
            return (
                self.db.query(TargetSystem)
                .filter(TargetSystem.type == target_type)
                .offset(skip)
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting target systems by type {target_type}: {e}")
            return []
    
    async def get_by_name(self, name: str) -> Optional[TargetSystem]:
        """Get target system by name"""
        try:
            return self.db.query(TargetSystem).filter(TargetSystem.name == name).first()
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting target system by name {name}: {e}")
            return None
    
    async def search_by_name(self, search_term: str, skip: int = 0, limit: int = 100) -> List[TargetSystem]:
        """Search target systems by name"""
        try:
            return (
                self.db.query(TargetSystem)
                .filter(TargetSystem.name.ilike(f"%{search_term}%"))
                .offset(skip)
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            self.logger.error(f"Error searching target systems by name {search_term}: {e}")
            return []
    
    async def get_recent_target_systems(self, limit: int = 10) -> List[TargetSystem]:
        """Get most recently created target systems"""
        try:
            return (
                self.db.query(TargetSystem)
                .order_by(TargetSystem.created_at.desc())
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting recent target systems: {e}")
            return []
    
    async def count_by_type(self, target_type: TargetType) -> int:
        """Count target systems by type"""
        try:
            return (
                self.db.query(TargetSystem)
                .filter(TargetSystem.type == target_type)
                .count()
            )
        except SQLAlchemyError as e:
            self.logger.error(f"Error counting target systems by type {target_type}: {e}")
            return 0
    
    async def name_exists(self, name: str, exclude_id: Optional[str] = None) -> bool:
        """Check if target system name already exists"""
        try:
            query = self.db.query(TargetSystem).filter(TargetSystem.name == name)
            if exclude_id:
                query = query.filter(TargetSystem.id != exclude_id)
            return query.first() is not None
        except SQLAlchemyError as e:
            self.logger.error(f"Error checking if target system name exists {name}: {e}")
            return False