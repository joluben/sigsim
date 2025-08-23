"""
Test project API endpoints
"""
import pytest
from fastapi.testclient import TestClient


def test_create_project_success(client: TestClient, sample_project_data):
    """Test successful project creation via API"""
    response = client.post("/api/v1/projects/", json=sample_project_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["name"] == sample_project_data["name"]
    assert data["description"] == sample_project_data["description"]
    assert "id" in data
    assert "created_at" in data


def test_create_project_validation_error(client: TestClient):
    """Test project creation with validation error"""
    # Missing required name field
    response = client.post("/api/v1/projects/", json={"description": "Test"})
    assert response.status_code == 422


def test_create_project_duplicate_name(client: TestClient, sample_project_data):
    """Test project creation with duplicate name"""
    # Create first project
    client.post("/api/v1/projects/", json=sample_project_data)
    
    # Try to create second project with same name
    response = client.post("/api/v1/projects/", json=sample_project_data)
    assert response.status_code == 400
    
    data = response.json()
    assert "errors" in data
    assert "Project name already exists" in data["errors"]


def test_get_projects(client: TestClient, sample_project_data):
    """Test getting all projects"""
    # Create a project first
    client.post("/api/v1/projects/", json=sample_project_data)
    
    response = client.get("/api/v1/projects/")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "device_count" in data[0]


def test_get_projects_with_pagination(client: TestClient):
    """Test getting projects with pagination"""
    # Create multiple projects
    for i in range(5):
        project_data = {"name": f"Project {i}", "description": f"Description {i}"}
        client.post("/api/v1/projects/", json=project_data)
    
    # Test pagination
    response = client.get("/api/v1/projects/?skip=2&limit=2")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2


def test_get_projects_with_search(client: TestClient):
    """Test searching projects"""
    # Create projects with different names
    client.post("/api/v1/projects/", json={"name": "Alpha Project"})
    client.post("/api/v1/projects/", json={"name": "Beta Project"})
    client.post("/api/v1/projects/", json={"name": "Gamma Test"})
    
    # Search for projects containing "Project"
    response = client.get("/api/v1/projects/?search=Project")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    assert all("Project" in project["name"] for project in data)


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


def test_get_project_by_id_not_found(client: TestClient):
    """Test getting a project that doesn't exist"""
    response = client.get("/api/v1/projects/nonexistent-id")
    assert response.status_code == 404


def test_update_project_success(client: TestClient, sample_project_data):
    """Test successful project update"""
    # Create a project first
    create_response = client.post("/api/v1/projects/", json=sample_project_data)
    project_id = create_response.json()["id"]
    
    update_data = {"name": "Updated Project Name"}
    response = client.put(f"/api/v1/projects/{project_id}", json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == sample_project_data["description"]  # Should remain unchanged


def test_update_project_duplicate_name(client: TestClient):
    """Test project update with duplicate name"""
    # Create two projects
    project1_data = {"name": "Project 1"}
    project2_data = {"name": "Project 2"}
    
    create_response1 = client.post("/api/v1/projects/", json=project1_data)
    create_response2 = client.post("/api/v1/projects/", json=project2_data)
    
    project2_id = create_response2.json()["id"]
    
    # Try to update project2 with project1's name
    update_data = {"name": "Project 1"}
    response = client.put(f"/api/v1/projects/{project2_id}", json=update_data)
    assert response.status_code == 400


def test_delete_project_success(client: TestClient, sample_project_data):
    """Test successful project deletion"""
    # Create a project first
    create_response = client.post("/api/v1/projects/", json=sample_project_data)
    project_id = create_response.json()["id"]
    
    response = client.delete(f"/api/v1/projects/{project_id}")
    assert response.status_code == 204
    
    # Verify project is deleted
    get_response = client.get(f"/api/v1/projects/{project_id}")
    assert get_response.status_code == 404


def test_delete_project_not_found(client: TestClient):
    """Test deleting a project that doesn't exist"""
    response = client.delete("/api/v1/projects/nonexistent-id")
    assert response.status_code == 404


def test_get_recent_projects(client: TestClient):
    """Test getting recent projects"""
    # Create multiple projects
    for i in range(3):
        project_data = {"name": f"Recent Project {i}"}
        client.post("/api/v1/projects/", json=project_data)
    
    response = client.get("/api/v1/projects/recent?limit=2")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    assert all("device_count" in project for project in data)