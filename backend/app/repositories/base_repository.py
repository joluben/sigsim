"""
Base repository with common CRUD operations
"""
from typing import Generic, TypeVar, Type, List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, desc, asc
from app.core.database import Base
from app.utils.logger import app_logger

T = TypeVar('T', bound=Base)


class BaseRepository(Generic[T]):
    """Base repository class with common CRUD operations"""
    
    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model
        self.logger = app_logger
    
    async def get_by_id(self, id: str) -> Optional[T]:
        """Get entity by ID"""
        try:
            return self.db.query(self.model).filter(self.model.id == id).first()
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting {self.model.__name__} by ID {id}: {e}")
            return None
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all entities with pagination"""
        try:
            return (
                self.db.query(self.model)
                .offset(skip)
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting all {self.model.__name__}: {e}")
            return []
    
    async def get_count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Get total count of entities"""
        try:
            query = self.db.query(self.model)
            if filters:
                query = self._apply_filters(query, filters)
            return query.count()
        except SQLAlchemyError as e:
            self.logger.error(f"Error counting {self.model.__name__}: {e}")
            return 0
    
    async def get_by_filters(
        self, 
        filters: Dict[str, Any], 
        skip: int = 0, 
        limit: int = 100,
        order_by: Optional[str] = None,
        order_desc: bool = False
    ) -> List[T]:
        """Get entities by filters with pagination and ordering"""
        try:
            query = self.db.query(self.model)
            query = self._apply_filters(query, filters)
            
            if order_by and hasattr(self.model, order_by):
                order_column = getattr(self.model, order_by)
                if order_desc:
                    query = query.order_by(desc(order_column))
                else:
                    query = query.order_by(asc(order_column))
            
            return query.offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting {self.model.__name__} by filters: {e}")
            return []
    
    async def create(self, data: Dict[str, Any]) -> Optional[T]:
        """Create new entity"""
        try:
            # Remove None values
            clean_data = {k: v for k, v in data.items() if v is not None}
            entity = self.model(**clean_data)
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            self.logger.info(f"Created {self.model.__name__} with ID: {entity.id}")
            return entity
        except SQLAlchemyError as e:
            self.db.rollback()
            self.logger.error(f"Error creating {self.model.__name__}: {e}")
            return None
    
    async def update(self, id: str, data: Dict[str, Any]) -> Optional[T]:
        """Update entity by ID"""
        try:
            entity = await self.get_by_id(id)
            if not entity:
                return None
            
            # Remove None values and update only provided fields
            clean_data = {k: v for k, v in data.items() if v is not None}
            for key, value in clean_data.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            
            self.db.commit()
            self.db.refresh(entity)
            self.logger.info(f"Updated {self.model.__name__} with ID: {id}")
            return entity
        except SQLAlchemyError as e:
            self.db.rollback()
            self.logger.error(f"Error updating {self.model.__name__} {id}: {e}")
            return None
    
    async def delete(self, id: str) -> bool:
        """Delete entity by ID"""
        try:
            entity = await self.get_by_id(id)
            if not entity:
                return False
            
            self.db.delete(entity)
            self.db.commit()
            self.logger.info(f"Deleted {self.model.__name__} with ID: {id}")
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            self.logger.error(f"Error deleting {self.model.__name__} {id}: {e}")
            return False
    
    async def exists(self, id: str) -> bool:
        """Check if entity exists by ID"""
        try:
            return self.db.query(self.model).filter(self.model.id == id).first() is not None
        except SQLAlchemyError as e:
            self.logger.error(f"Error checking existence of {self.model.__name__} {id}: {e}")
            return False
    
    async def bulk_create(self, data_list: List[Dict[str, Any]]) -> List[T]:
        """Create multiple entities in bulk"""
        try:
            entities = []
            for data in data_list:
                clean_data = {k: v for k, v in data.items() if v is not None}
                entity = self.model(**clean_data)
                entities.append(entity)
            
            self.db.add_all(entities)
            self.db.commit()
            
            for entity in entities:
                self.db.refresh(entity)
            
            self.logger.info(f"Bulk created {len(entities)} {self.model.__name__} entities")
            return entities
        except SQLAlchemyError as e:
            self.db.rollback()
            self.logger.error(f"Error bulk creating {self.model.__name__}: {e}")
            return []
    
    def _apply_filters(self, query, filters: Dict[str, Any]):
        """Apply filters to query"""
        for key, value in filters.items():
            if hasattr(self.model, key):
                column = getattr(self.model, key)
                if isinstance(value, list):
                    query = query.filter(column.in_(value))
                elif isinstance(value, dict):
                    # Handle range filters like {"gte": 10, "lte": 100}
                    if "gte" in value:
                        query = query.filter(column >= value["gte"])
                    if "lte" in value:
                        query = query.filter(column <= value["lte"])
                    if "gt" in value:
                        query = query.filter(column > value["gt"])
                    if "lt" in value:
                        query = query.filter(column < value["lt"])
                    if "like" in value:
                        query = query.filter(column.like(f"%{value['like']}%"))
                else:
                    query = query.filter(column == value)
        return query