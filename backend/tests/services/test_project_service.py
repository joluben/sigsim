"""
Test project service
"""
import pytest
from app.services.project_service import ProjectService
from app.models.project import ProjectCreate, ProjectUpdate


@pytest.mark.asyncio
async def test_create_project_success(db_session):
    """Test successful project creation"""
    service = ProjectService(db_session)
    
    project_data = ProjectCreate(name="Test Project", description="A test project")
    
    result = await service.create_project(project_data)
    
    assert result is not None
    assert result.name == "Test Project"
    assert result.description == "A test project"
    assert result.id is not None


@pytest.mark.asyncio
async def test_create_project_duplicate_name(db_session):
    """Test project creation with duplicate name"""
    service = ProjectService(db_session)
    
    # Create first project
    project_data = ProjectCreate(name="Duplicate Name")
    await service.create_project(project_data)
    
    # Try to create second project with same name
    duplicate_project_data = ProjectCreate(name="Duplicate Name")
    result = await service.create_project(duplicate_project_data)
    
    assert result is None


@pytest.mark.asyncio
async def test_get_project_by_id(db_session):
    """Test getting project by ID"""
    service = ProjectService(db_session)
    
    # Create a project first
    project_data = ProjectCreate(name="Test Project")
    created_project = await service.create_project(project_data)
    
    # Get the project by ID
    retrieved_project = await service.get_project_by_id(created_project.id)
    
    assert retrieved_project is not None
    assert retrieved_project.id == created_project.id
    assert retrieved_project.name == "Test Project"


@pytest.mark.asyncio
async def test_get_project_by_id_not_found(db_session):
    """Test getting project by non-existent ID"""
    service = ProjectService(db_session)
    
    result = await service.get_project_by_id("non-existent-id")
    
    assert result is None


@pytest.mark.asyncio
async def test_update_project_success(db_session):
    """Test successful project update"""
    service = ProjectService(db_session)
    
    # Create a project first
    project_data = ProjectCreate(name="Original Name")
    created_project = await service.create_project(project_data)
    
    # Update the project
    update_data = ProjectUpdate(name="Updated Name", description="Updated description")
    updated_project = await service.update_project(created_project.id, update_data)
    
    assert updated_project is not None
    assert updated_project.name == "Updated Name"
    assert updated_project.description == "Updated description"


@pytest.mark.asyncio
async def test_update_project_duplicate_name(db_session):
    """Test project update with duplicate name"""
    service = ProjectService(db_session)
    
    # Create two projects
    project1_data = ProjectCreate(name="Project 1")
    project2_data = ProjectCreate(name="Project 2")
    
    project1 = await service.create_project(project1_data)
    project2 = await service.create_project(project2_data)
    
    # Try to update project2 with project1's name
    update_data = ProjectUpdate(name="Project 1")
    result = await service.update_project(project2.id, update_data)
    
    assert result is None


@pytest.mark.asyncio
async def test_delete_project_success(db_session):
    """Test successful project deletion"""
    service = ProjectService(db_session)
    
    # Create a project first
    project_data = ProjectCreate(name="Project to Delete")
    created_project = await service.create_project(project_data)
    
    # Delete the project
    success = await service.delete_project(created_project.id)
    assert success is True
    
    # Verify it's deleted
    retrieved_project = await service.get_project_by_id(created_project.id)
    assert retrieved_project is None


@pytest.mark.asyncio
async def test_delete_project_not_found(db_session):
    """Test deleting non-existent project"""
    service = ProjectService(db_session)
    
    success = await service.delete_project("non-existent-id")
    assert success is False


@pytest.mark.asyncio
async def test_validate_project_name(db_session):
    """Test project name validation"""
    service = ProjectService(db_session)
    
    # Create a project first
    project_data = ProjectCreate(name="Existing Project")
    created_project = await service.create_project(project_data)
    
    # Test validation
    assert await service.validate_project_name("New Project") is True
    assert await service.validate_project_name("Existing Project") is False
    assert await service.validate_project_name("Existing Project", exclude_id=created_project.id) is True