"""
Test device Pydantic models
"""
import pytest
from pydantic import ValidationError
from app.models.device import DeviceCreate, DeviceUpdate


def test_device_create_valid():
    """Test valid device creation"""
    device_data = {
        "project_id": "test-project-id",
        "name": "Test Device",
        "metadata": {"location": "office"},
        "send_interval": 30,
        "is_enabled": True
    }
    device = DeviceCreate(**device_data)
    assert device.name == "Test Device"
    assert device.metadata == {"location": "office"}
    assert device.send_interval == 30
    assert device.is_enabled is True


def test_device_create_minimal():
    """Test device creation with minimal data"""
    device_data = {
        "project_id": "test-project-id",
        "name": "Test Device"
    }
    device = DeviceCreate(**device_data)
    assert device.name == "Test Device"
    assert device.metadata == {}
    assert device.send_interval == 10  # default
    assert device.is_enabled is True  # default


def test_device_create_invalid_interval():
    """Test device creation with invalid send interval"""
    # Too small
    with pytest.raises(ValidationError):
        DeviceCreate(
            project_id="test-project-id",
            name="Test Device",
            send_interval=0
        )
    
    # Too large
    with pytest.raises(ValidationError):
        DeviceCreate(
            project_id="test-project-id",
            name="Test Device",
            send_interval=3601
        )


def test_device_metadata_validation():
    """Test device metadata validation"""
    # Valid JSON serializable metadata
    device = DeviceCreate(
        project_id="test-project-id",
        name="Test Device",
        metadata={"location": "office", "floor": 2, "active": True}
    )
    assert device.metadata == {"location": "office", "floor": 2, "active": True}


def test_device_name_trimming():
    """Test that device names are trimmed"""
    device = DeviceCreate(
        project_id="test-project-id",
        name="  Test Device  "
    )
    assert device.name == "Test Device"


def test_device_empty_name():
    """Test device creation with empty name"""
    with pytest.raises(ValidationError):
        DeviceCreate(
            project_id="test-project-id",
            name=""
        )


def test_device_update_partial():
    """Test partial device update"""
    update_data = {"name": "Updated Device"}
    device_update = DeviceUpdate(**update_data)
    assert device_update.name == "Updated Device"
    assert device_update.send_interval is None