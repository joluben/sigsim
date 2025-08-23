"""
Test device API endpoints
"""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def project_id(client: TestClient, sample_project_data):
    """Create a project and return its ID"""
    response = client.post("/api/v1/projects/", json=sample_project_data)
    return response.json()["id"]


def test_create_device_success(client: TestClient, project_id, sample_device_data):
    """Test successful device creation via API"""
    device_data = {**sample_device_data, "project_id": project_id}
    
    response = client.post("/api/v1/devices/", json=device_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["name"] == device_data["name"]
    assert data["project_id"] == project_id
    assert data["send_interval"] == device_data["send_interval"]
    assert "id" in data


def test_create_device_invalid_project(client: TestClient, sample_device_data):
    """Test device creation with invalid project ID"""
    device_data = {**sample_device_data, "project_id": "invalid-project-id"}
    
    response = client.post("/api/v1/devices/", json=device_data)
    assert response.status_code == 400
    
    data = response.json()
    assert "errors" in data


def test_get_devices_by_project(client: TestClient, project_id, sample_device_data):
    """Test getting devices for a project"""
    # Create a device first
    device_data = {**sample_device_data, "project_id": project_id}
    client.post("/api/v1/devices/", json=device_data)
    
    response = client.get(f"/api/v1/devices/project/{project_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "has_payload" in data[0]
    assert "has_target" in data[0]


def test_get_devices_with_pagination(client: TestClient, project_id):
    """Test getting devices with pagination"""
    # Create multiple devices
    for i in range(5):
        device_data = {
            "name": f"Device {i}",
            "project_id": project_id,
            "send_interval": 30
        }
        client.post("/api/v1/devices/", json=device_data)
    
    # Test pagination
    response = client.get(f"/api/v1/devices/project/{project_id}?skip=2&limit=2")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2


def test_get_devices_enabled_only(client: TestClient, project_id):
    """Test getting only enabled devices"""
    # Create enabled and disabled devices
    enabled_device = {
        "name": "Enabled Device",
        "project_id": project_id,
        "is_enabled": True
    }
    disabled_device = {
        "name": "Disabled Device",
        "project_id": project_id,
        "is_enabled": False
    }
    
    client.post("/api/v1/devices/", json=enabled_device)
    client.post("/api/v1/devices/", json=disabled_device)
    
    response = client.get(f"/api/v1/devices/project/{project_id}?enabled_only=true")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Enabled Device"


def test_get_device_by_id(client: TestClient, project_id, sample_device_data):
    """Test getting a specific device by ID"""
    device_data = {**sample_device_data, "project_id": project_id}
    create_response = client.post("/api/v1/devices/", json=device_data)
    device_id = create_response.json()["id"]
    
    response = client.get(f"/api/v1/devices/{device_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == device_id
    assert data["name"] == device_data["name"]


def test_get_device_by_id_not_found(client: TestClient):
    """Test getting a device that doesn't exist"""
    response = client.get("/api/v1/devices/nonexistent-id")
    assert response.status_code == 404


def test_update_device_success(client: TestClient, project_id, sample_device_data):
    """Test successful device update"""
    device_data = {**sample_device_data, "project_id": project_id}
    create_response = client.post("/api/v1/devices/", json=device_data)
    device_id = create_response.json()["id"]
    
    update_data = {"name": "Updated Device Name", "send_interval": 60}
    response = client.put(f"/api/v1/devices/{device_id}", json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["send_interval"] == update_data["send_interval"]


def test_delete_device_success(client: TestClient, project_id, sample_device_data):
    """Test successful device deletion"""
    device_data = {**sample_device_data, "project_id": project_id}
    create_response = client.post("/api/v1/devices/", json=device_data)
    device_id = create_response.json()["id"]
    
    response = client.delete(f"/api/v1/devices/{device_id}")
    assert response.status_code == 204
    
    # Verify device is deleted
    get_response = client.get(f"/api/v1/devices/{device_id}")
    assert get_response.status_code == 404


def test_bulk_update_device_status(client: TestClient, project_id):
    """Test bulk updating device enabled status"""
    # Create multiple devices
    device_ids = []
    for i in range(3):
        device_data = {
            "name": f"Device {i}",
            "project_id": project_id,
            "is_enabled": True
        }
        response = client.post("/api/v1/devices/", json=device_data)
        device_ids.append(response.json()["id"])
    
    # Bulk disable devices
    bulk_data = {
        "device_ids": device_ids,
        "is_enabled": False
    }
    response = client.patch("/api/v1/devices/bulk-enable", json=bulk_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["updated_count"] == 3
    assert data["is_enabled"] is False


def test_get_device_stats_by_project(client: TestClient, project_id):
    """Test getting device statistics for a project"""
    # Create devices with different statuses
    enabled_device = {
        "name": "Enabled Device",
        "project_id": project_id,
        "is_enabled": True
    }
    disabled_device = {
        "name": "Disabled Device",
        "project_id": project_id,
        "is_enabled": False
    }
    
    client.post("/api/v1/devices/", json=enabled_device)
    client.post("/api/v1/devices/", json=disabled_device)
    
    response = client.get(f"/api/v1/devices/project/{project_id}/stats")
    assert response.status_code == 200
    
    data = response.json()
    assert "total" in data
    assert "enabled" in data
    assert "disabled" in data
    assert data["total"] == 2
    assert data["enabled"] == 1
    assert data["disabled"] == 1