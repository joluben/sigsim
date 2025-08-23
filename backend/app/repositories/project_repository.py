"""
Project repository for data access
"""
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from app.repositories.base_repository import BaseRepository
from app.schemas.database import Project, Device


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db: Session):
        super().__init__(db, Project)
    
    async def get_with_devices(self, project_id: str) -> Optional[Project]:
        """Get project with all its devices loaded"""
        try:
            return (
                self.db.query(Project)
                .options(joinedload(Project.devices))
                .filter(Project.id == project_id)
                .first()
            )
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting project with devices {project_id}: {e}")
            return None
    
    async def get_by_name(self, name: str) -> Optional[Project]:
        """Get project by name"""
        try:
            return self.db.query(Project).filter(Project.name == name).first()
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting project by name {name}: {e}")
            return None
    
    async def get_projects_with_device_count(self, skip: int = 0, limit: int = 100) -> List[dict]:
        """Get projects with device count"""
        try:
            result = (
                self.db.query(
                    Project,
                    func.count(Device.id).label('device_count')
                )
                .outerjoin(Device)
                .group_by(Project.id)
                .offset(skip)
                .limit(limit)
                .all()
            )
            
            return [
                {
                    'project': project,
                    'device_count': device_count
                }
                for project, device_count in result
            ]
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting projects with device count: {e}")
            return []
    
    async def search_by_name(self, search_term: str, skip: int = 0, limit: int = 100) -> List[Project]:
        """Search projects by name"""
        try:
            return (
                self.db.query(Project)
                .filter(Project.name.ilike(f"%{search_term}%"))
                .offset(skip)
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            self.logger.error(f"Error searching projects by name {search_term}: {e}")
            return []
    
    async def get_recent_projects(self, limit: int = 10) -> List[Project]:
        """Get most recently created projects"""
        try:
            return (
                self.db.query(Project)
                .order_by(Project.created_at.desc())
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting recent projects: {e}")
            return []
    
    async def name_exists(self, name: str, exclude_id: Optional[str] = None) -> bool:
        """Check if project name already exists"""
        try:
            query = self.db.query(Project).filter(Project.name == name)
            if exclude_id:
                query = query.filter(Project.id != exclude_id)
            return query.first() is not None
        except SQLAlchemyError as e:
            self.logger.error(f"Error checking if project name exists {name}: {e}")
            return False