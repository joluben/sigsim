"""
Project business logic service
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.project_repository import ProjectRepository
from app.models.project import ProjectCreate, ProjectResponse, ProjectUpdate, ProjectSummary
from app.schemas.database import Project
from app.utils.logger import app_logger


class ProjectService:
    def __init__(self, db: Session):
        self.repository = ProjectRepository(db)
        self.logger = app_logger
    
    async def get_all_projects(self, skip: int = 0, limit: int = 100) -> List[ProjectSummary]:
        """Get all projects with pagination"""
        try:
            projects_with_count = await self.repository.get_projects_with_device_count(skip, limit)
            return [
                ProjectSummary(
                    id=item['project'].id,
                    name=item['project'].name,
                    description=item['project'].description,
                    created_at=item['project'].created_at,
                    device_count=item['device_count'],
                    is_running=False  # TODO: Get from simulation engine
                )
                for item in projects_with_count
            ]
        except Exception as e:
            self.logger.error(f"Error getting all projects: {e}")
            return []
    
    async def get_project_by_id(self, project_id: str) -> Optional[ProjectResponse]:
        """Get project by ID"""
        try:
            project = await self.repository.get_by_id(project_id)
            if project:
                return ProjectResponse.from_orm(project)
            return None
        except Exception as e:
            self.logger.error(f"Error getting project {project_id}: {e}")
            return None
    
    async def create_project(self, project_data: ProjectCreate) -> Optional[ProjectResponse]:
        """Create a new project"""
        try:
            # Check if name already exists
            if await self.repository.name_exists(project_data.name):
                self.logger.warning(f"Project name already exists: {project_data.name}")
                return None
            
            project = await self.repository.create(project_data.dict())
            if project:
                self.logger.info(f"Created project: {project.name}")
                return ProjectResponse.from_orm(project)
            return None
        except Exception as e:
            self.logger.error(f"Error creating project: {e}")
            return None
    
    async def update_project(self, project_id: str, project_data: ProjectUpdate) -> Optional[ProjectResponse]:
        """Update a project"""
        try:
            # Filter out None values
            update_data = {k: v for k, v in project_data.dict().items() if v is not None}
            if not update_data:
                return await self.get_project_by_id(project_id)
            
            # Check if new name already exists (if name is being updated)
            if 'name' in update_data:
                if await self.repository.name_exists(update_data['name'], exclude_id=project_id):
                    self.logger.warning(f"Project name already exists: {update_data['name']}")
                    return None
            
            project = await self.repository.update(project_id, update_data)
            if project:
                self.logger.info(f"Updated project: {project_id}")
                return ProjectResponse.from_orm(project)
            return None
        except Exception as e:
            self.logger.error(f"Error updating project {project_id}: {e}")
            return None
    
    async def delete_project(self, project_id: str) -> bool:
        """Delete a project"""
        try:
            # TODO: Check if project is running and stop simulation first
            success = await self.repository.delete(project_id)
            if success:
                self.logger.info(f"Deleted project: {project_id}")
            return success
        except Exception as e:
            self.logger.error(f"Error deleting project {project_id}: {e}")
            return False
    
    async def get_project_with_devices(self, project_id: str) -> Optional[ProjectResponse]:
        """Get project with all its devices"""
        try:
            project = await self.repository.get_with_devices(project_id)
            if project:
                return ProjectResponse.from_orm(project)
            return None
        except Exception as e:
            self.logger.error(f"Error getting project with devices {project_id}: {e}")
            return None
    
    async def search_projects(self, search_term: str, skip: int = 0, limit: int = 100) -> List[ProjectSummary]:
        """Search projects by name"""
        try:
            projects = await self.repository.search_by_name(search_term, skip, limit)
            return [
                ProjectSummary(
                    id=project.id,
                    name=project.name,
                    description=project.description,
                    created_at=project.created_at,
                    device_count=0,  # TODO: Get device count
                    is_running=False  # TODO: Get from simulation engine
                )
                for project in projects
            ]
        except Exception as e:
            self.logger.error(f"Error searching projects: {e}")
            return []
    
    async def get_recent_projects(self, limit: int = 10) -> List[ProjectSummary]:
        """Get most recently created projects"""
        try:
            projects = await self.repository.get_recent_projects(limit)
            return [
                ProjectSummary(
                    id=project.id,
                    name=project.name,
                    description=project.description,
                    created_at=project.created_at,
                    device_count=0,  # TODO: Get device count
                    is_running=False  # TODO: Get from simulation engine
                )
                for project in projects
            ]
        except Exception as e:
            self.logger.error(f"Error getting recent projects: {e}")
            return []
    
    async def validate_project_name(self, name: str, exclude_id: Optional[str] = None) -> bool:
        """Validate if project name is available"""
        try:
            return not await self.repository.name_exists(name, exclude_id)
        except Exception as e:
            self.logger.error(f"Error validating project name {name}: {e}")
            return False