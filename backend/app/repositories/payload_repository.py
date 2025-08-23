"""
Payload repository for data access
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.repositories.base_repository import BaseRepository
from app.schemas.database import Payload
from app.models.payload import PayloadType


class PayloadRepository(BaseRepository[Payload]):
    def __init__(self, db: Session):
        super().__init__(db, Payload)
    
    async def get_by_type(self, payload_type: PayloadType, skip: int = 0, limit: int = 100) -> List[Payload]:
        """Get payloads by type"""
        try:
            return (
                self.db.query(Payload)
                .filter(Payload.type == payload_type)
                .offset(skip)
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting payloads by type {payload_type}: {e}")
            return []
    
    async def get_by_name(self, name: str) -> Optional[Payload]:
        """Get payload by name"""
        try:
            return self.db.query(Payload).filter(Payload.name == name).first()
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting payload by name {name}: {e}")
            return None
    
    async def search_by_name(self, search_term: str, skip: int = 0, limit: int = 100) -> List[Payload]:
        """Search payloads by name"""
        try:
            return (
                self.db.query(Payload)
                .filter(Payload.name.ilike(f"%{search_term}%"))
                .offset(skip)
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            self.logger.error(f"Error searching payloads by name {search_term}: {e}")
            return []
    
    async def get_recent_payloads(self, limit: int = 10) -> List[Payload]:
        """Get most recently created payloads"""
        try:
            return (
                self.db.query(Payload)
                .order_by(Payload.created_at.desc())
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting recent payloads: {e}")
            return []
    
    async def count_by_type(self, payload_type: PayloadType) -> int:
        """Count payloads by type"""
        try:
            return (
                self.db.query(Payload)
                .filter(Payload.type == payload_type)
                .count()
            )
        except SQLAlchemyError as e:
            self.logger.error(f"Error counting payloads by type {payload_type}: {e}")
            return 0
    
    async def name_exists(self, name: str, exclude_id: Optional[str] = None) -> bool:
        """Check if payload name already exists"""
        try:
            query = self.db.query(Payload).filter(Payload.name == name)
            if exclude_id:
                query = query.filter(Payload.id != exclude_id)
            return query.first() is not None
        except SQLAlchemyError as e:
            self.logger.error(f"Error checking if payload name exists {name}: {e}")
            return False