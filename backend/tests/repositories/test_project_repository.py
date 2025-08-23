"""
Test project repository
"""
import pytest
from app.repositories.project_repository import ProjectRepository
from app.schemas.database import Project


@pytest.mark.asyncio
async def test_create_project(db_session):
    """Test creating a project"""
    repository = ProjectRepository(db_session)
    
    project_data = {
        "name": "Test Project",
        "description": "A test project"
    }
    
    project = await repository.create(project_data)
    
    assert project is not None
    assert project.name == "Test Project"
    assert project.description == "A test project"
    assert project.id is not None


@pytest.mark.asyncio
async def test_get_project_by_id(db_session):
    """Test getting a project by ID"""
    repository = ProjectRepository(db_session)
    
    # Create a project first
    project_data = {"name": "Test Project"}
    created_project = await repository.create(project_data)
    
    # Get the project by ID
    retrieved_project = await repository.get_by_id(created_project.id)
    
    assert retrieved_project is not None
    assert retrieved_project.id == created_project.id
    assert retrieved_project.name == "Test Project"


@pytest.mark.asyncio
async def test_get_project_by_name(db_session):
    """Test getting a project by name"""
    repository = ProjectRepository(db_session)
    
    # Create a project first
    project_data = {"name": "Unique Project Name"}
    await repository.create(project_data)
    
    # Get the project by name
    retrieved_project = await repository.get_by_name("Unique Project Name")
    
    assert retrieved_project is not None
    assert retrieved_project.name == "Unique Project Name"


@pytest.mark.asyncio
async def test_name_exists(db_session):
    """Test checking if project name exists"""
    repository = ProjectRepository(db_session)
    
    # Create a project first
    project_data = {"name": "Existing Project"}
    created_project = await repository.create(project_data)
    
    # Check if name exists
    assert await repository.name_exists("Existing Project") is True
    assert await repository.name_exists("Non-existing Project") is False
    
    # Check with exclude_id
    assert await repository.name_exists("Existing Project", exclude_id=created_project.id) is False


@pytest.mark.asyncio
async def test_update_project(db_session):
    """Test updating a project"""
    repository = ProjectRepository(db_session)
    
    # Create a project first
    project_data = {"name": "Original Name"}
    created_project = await repository.create(project_data)
    
    # Update the project
    update_data = {"name": "Updated Name", "description": "Updated description"}
    updated_project = await repository.update(created_project.id, update_data)
    
    assert updated_project is not None
    assert updated_project.name == "Updated Name"
    assert updated_project.description == "Updated description"


@pytest.mark.asyncio
async def test_delete_project(db_session):
    """Test deleting a project"""
    repository = ProjectRepository(db_session)
    
    # Create a project first
    project_data = {"name": "Project to Delete"}
    created_project = await repository.create(project_data)
    
    # Delete the project
    success = await repository.delete(created_project.id)
    assert success is True
    
    # Verify it's deleted
    retrieved_project = await repository.get_by_id(created_project.id)
    assert retrieved_project is None


@pytest.mark.asyncio
async def test_get_all_projects(db_session):
    """Test getting all projects"""
    repository = ProjectRepository(db_session)
    
    # Create multiple projects
    for i in range(3):
        project_data = {"name": f"Project {i}"}
        await repository.create(project_data)
    
    # Get all projects
    projects = await repository.get_all()
    
    assert len(projects) == 3
    assert all(isinstance(project, Project) for project in projects)