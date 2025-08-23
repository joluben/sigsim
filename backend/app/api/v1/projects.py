"""
Project management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api.dependencies import get_db_session
from app.models.project import ProjectCreate, ProjectResponse, ProjectUpdate, ProjectSummary
from app.services.project_service import ProjectService
from app.services.validation_service import ValidationService

router = APIRouter()


@router.get("/", response_model=List[ProjectSummary])
async def get_projects(
    skip: int = Query(0, ge=0, description="Number of projects to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of projects to return"),
    search: Optional[str] = Query(None, description="Search term for project names"),
    db: Session = Depends(get_db_session)
):
    """Get all projects with pagination and optional search"""
    service = ProjectService(db)
    
    if search:
        return await service.search_projects(search, skip, limit)
    else:
        return await service.get_all_projects(skip, limit)


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db_session)
):
    """Create a new project"""
    service = ProjectService(db)
    validation_service = ValidationService(db)
    
    # Validate project data
    errors = await validation_service.validate_project_creation(project.dict())
    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Validation failed", "errors": errors}
        )
    
    result = await service.create_project(project)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create project"
        )
    
    return result


@router.get("/recent", response_model=List[ProjectSummary])
async def get_recent_projects(
    limit: int = Query(10, ge=1, le=50, description="Number of recent projects to return"),
    db: Session = Depends(get_db_session)
):
    """Get most recently created projects"""
    service = ProjectService(db)
    return await service.get_recent_projects(limit)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: Session = Depends(get_db_session)
):
    """Get a specific project by ID"""
    service = ProjectService(db)
    project = await service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return project


@router.get("/{project_id}/with-devices", response_model=ProjectResponse)
async def get_project_with_devices(
    project_id: str,
    db: Session = Depends(get_db_session)
):
    """Get a project with all its devices loaded"""
    service = ProjectService(db)
    project = await service.get_project_with_devices(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db_session)
):
    """Update a project"""
    service = ProjectService(db)
    validation_service = ValidationService(db)
    
    # Validate update data
    errors = await validation_service.validate_project_update(project_id, project_update.dict())
    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Validation failed", "errors": errors}
        )
    
    project = await service.update_project(project_id, project_update)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or update failed"
        )
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    db: Session = Depends(get_db_session)
):
    """Delete a project"""
    service = ProjectService(db)
    success = await service.delete_project(project_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )


@router.post("/{project_id}/validate-name")
async def validate_project_name(
    project_id: str,
    name_data: dict,
    db: Session = Depends(get_db_session)
):
    """Validate if a project name is available"""
    service = ProjectService(db)
    name = name_data.get("name")
    
    if not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name is required"
        )
    
    is_valid = await service.validate_project_name(name, exclude_id=project_id)
    return {"valid": is_valid, "message": "Name is available" if is_valid else "Name already exists"}