"""
Test project Pydantic models
"""
import pytest
from pydantic import ValidationError
from app.models.project import ProjectCreate, ProjectUpdate, ProjectResponse


def test_project_create_valid():
    """Test valid project creation"""
    project_data = {
        "name": "Test Project",
        "description": "A test project"
    }
    project = ProjectCreate(**project_data)
    assert project.name == "Test Project"
    assert project.description == "A test project"


def test_project_create_minimal():
    """Test project creation with minimal data"""
    project_data = {"name": "Test Project"}
    project = ProjectCreate(**project_data)
    assert project.name == "Test Project"
    assert project.description is None


def test_project_create_empty_name():
    """Test project creation with empty name"""
    with pytest.raises(ValidationError) as exc_info:
        ProjectCreate(name="")
    
    errors = exc_info.value.errors()
    assert any(error["type"] == "value_error" for error in errors)


def test_project_create_whitespace_name():
    """Test project creation with whitespace name"""
    with pytest.raises(ValidationError) as exc_info:
        ProjectCreate(name="   ")
    
    errors = exc_info.value.errors()
    assert any(error["type"] == "value_error" for error in errors)


def test_project_create_long_name():
    """Test project creation with name too long"""
    long_name = "x" * 101  # Exceeds 100 character limit
    with pytest.raises(ValidationError) as exc_info:
        ProjectCreate(name=long_name)
    
    errors = exc_info.value.errors()
    assert any(error["type"] == "value_error.any_str.max_length" for error in errors)


def test_project_create_long_description():
    """Test project creation with description too long"""
    long_description = "x" * 501  # Exceeds 500 character limit
    with pytest.raises(ValidationError) as exc_info:
        ProjectCreate(name="Test", description=long_description)
    
    errors = exc_info.value.errors()
    assert any(error["type"] == "value_error.any_str.max_length" for error in errors)


def test_project_update_partial():
    """Test partial project update"""
    update_data = {"name": "Updated Name"}
    project_update = ProjectUpdate(**update_data)
    assert project_update.name == "Updated Name"
    assert project_update.description is None


def test_project_update_empty():
    """Test empty project update"""
    project_update = ProjectUpdate()
    assert project_update.name is None
    assert project_update.description is None


def test_project_name_trimming():
    """Test that project names are trimmed"""
    project = ProjectCreate(name="  Test Project  ")
    assert project.name == "Test Project"