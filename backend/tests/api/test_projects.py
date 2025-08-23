"""
Test project API endpoints
"""
import pytest
from fastapi.testclient import TestClient


def test_create_project(client: TestClient, sample_project_data):
    """Test creating a new project"""
    response = client.post("/api/v1/projects/", json=sample_project_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["name"] == sample_project_data["name"]
    assert data["description"] == sample_project_data["description"]
    assert "id" in data
    assert "created_at" in data


def test_get_projects(client: TestClient, sample_project_data):
    """Test getting all projects"""
    # Create a project first
    client.post("/api/v1/projects/", json=sample_project_data)
    
    response = client.get("/api/v1/projects/")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_project_by_id(client: TestClient, sample_project_data):
    """Test getting a specific project by ID"""
    # Create a project first
    create_response = client.post("/api/v1/projects/", json=sample_project_data)
    project_id = create_response.json()["id"]
    
    response = client.get(f"/api/v1/projects/{project_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == project_id
    assert data["name"] == sample_project_data["name"]


def test_get_nonexistent_project(client: TestClient):
    """Test getting a project that doesn't exist"""
    response = client.get("/api/v1/projects/nonexistent-id")
    assert response.status_code == 404


def test_update_project(client: TestClient, sample_project_data):
    """Test updating a project"""
    # Create a project first
    create_response = client.post("/api/v1/projects/", json=sample_project_data)
    project_id = create_response.json()["id"]
    
    update_data = {"name": "Updated Project Name"}
    response = client.put(f"/api/v1/projects/{project_id}", json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == sample_project_data["description"]  # Should remain unchanged


def test_delete_project(client: TestClient, sample_project_data):
    """Test deleting a project"""
    # Create a project first
    create_response = client.post("/api/v1/projects/", json=sample_project_data)
    project_id = create_response.json()["id"]
    
    response = client.delete(f"/api/v1/projects/{project_id}")
    assert response.status_code == 204
    
    # Verify project is deleted
    get_response = client.get(f"/api/v1/projects/{project_id}")
    assert get_response.status_code == 404


def test_create_project_validation(client: TestClient):
    """Test project creation validation"""
    # Test missing name
    response = client.post("/api/v1/projects/", json={"description": "Test"})
    assert response.status_code == 422
    
    # Test empty name
    response = client.post("/api/v1/projects/", json={"name": ""})
    assert response.status_code == 422