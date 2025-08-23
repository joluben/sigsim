"""
Pytest configuration and fixtures
"""
import pytest
import asyncio
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db, Base
from app.core.config import settings


# Test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session) -> Generator:
    """Create a test client with database override"""
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_project_data():
    """Sample project data for testing"""
    return {
        "name": "Test Project",
        "description": "A test project for unit testing"
    }


@pytest.fixture
def sample_device_data():
    """Sample device data for testing"""
    return {
        "name": "Test Device",
        "metadata": {"location": "test_lab", "type": "sensor"},
        "send_interval": 30,
        "is_enabled": True
    }


@pytest.fixture
def sample_payload_data():
    """Sample payload data for testing"""
    return {
        "name": "Test Payload",
        "type": "visual",
        "schema": {
            "fields": [
                {
                    "name": "temperature",
                    "type": "number",
                    "generator": {
                        "type": "random_float",
                        "min": 18.0,
                        "max": 25.0
                    }
                }
            ]
        }
    }


@pytest.fixture
def sample_target_data():
    """Sample target system data for testing"""
    return {
        "name": "Test HTTP Target",
        "type": "http",
        "config": {
            "url": "https://httpbin.org/post",
            "method": "POST",
            "headers": {"Content-Type": "application/json"}
        }
    }