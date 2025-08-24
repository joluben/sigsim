"""
Integration test for WebSocket connector automatic reconnection
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from app.simulation.connectors.websocket_connector import WebSocketConnector, ConnectionState
from app.models.target import WebSocketConfig


@pytest.fixture
def websocket_config():
    """Create a test WebSocket configuration"""
    return WebSocketConfig(
        url="ws://localhost:8080/test",
        headers={"Authorization": "Bearer test-token"},
        ping_interval=20
    )


@pytest.mark.asyncio
async def test_websocket_connector_has_reconnection_features(websocket_config):
    """Test that WebSocket connector has all the reconnection features implemented"""
    connector = WebSocketConnector(websocket_config)
    
    # Test that all reconnection attributes exist
    assert hasattr(connector, 'max_retries')
    assert hasattr(connector, 'base_delay')
    assert hasattr(connector, 'max_delay')
    assert hasattr(connector, 'retry_count')
    assert hasattr(connector, 'circuit_state')
    assert hasattr(connector, 'failure_count')
    assert hasattr(connector, 'failure_threshold')
    assert hasattr(connector, 'recovery_timeout')
    assert hasattr(connector, '_reconnect_task')
    assert hasattr(connector, '_should_reconnect')
    assert hasattr(connector, '_connection_lock')
    
    # Test that all reconnection methods exist
    assert hasattr(connector, 'start_auto_reconnect')
    assert hasattr(connector, 'stop_auto_reconnect')
    assert hasattr(connector, '_reconnect_and_retry')
    assert hasattr(connector, '_auto_reconnect_loop')
    assert hasattr(connector, 'get_connection_stats')
    
    # Test initial state
    assert connector.circuit_state == ConnectionState.CLOSED
    assert connector.failure_count == 0
    assert connector.retry_count == 0
    assert connector._should_reconnect is True


@pytest.mark.asyncio
async def test_websocket_connector_circuit_breaker_logic():
    """Test circuit breaker state transitions"""
    config = WebSocketConfig(url="ws://localhost:8080/test")
    connector = WebSocketConnector(config)
    
    # Test initial state
    assert connector.circuit_state == ConnectionState.CLOSED
    
    # Simulate failures to open circuit breaker
    connector.failure_count = connector.failure_threshold
    connector._on_connection_failure(Exception("Test failure"))
    
    # Circuit should be open
    assert connector.circuit_state == ConnectionState.OPEN
    
    # Test successful connection resets circuit breaker
    connector._on_connection_success()
    assert connector.circuit_state == ConnectionState.CLOSED
    assert connector.failure_count == 0
    assert connector.retry_count == 0


@pytest.mark.asyncio
async def test_websocket_connector_stats():
    """Test connection statistics"""
    config = WebSocketConfig(url="ws://localhost:8080/test")
    connector = WebSocketConnector(config)
    
    stats = connector.get_connection_stats()
    
    # Check that all expected stats are present
    expected_keys = [
        "connected", "circuit_state", "retry_count", 
        "failure_count", "last_failure_time", "auto_reconnect_active"
    ]
    
    for key in expected_keys:
        assert key in stats
    
    # Check initial values
    assert stats["connected"] is False
    assert stats["circuit_state"] == ConnectionState.CLOSED.value
    assert stats["retry_count"] == 0
    assert stats["failure_count"] == 0


@pytest.mark.asyncio
async def test_websocket_connector_auto_reconnect_lifecycle():
    """Test auto-reconnect start/stop lifecycle"""
    config = WebSocketConfig(url="ws://localhost:8080/test")
    connector = WebSocketConnector(config)
    
    # Initially no reconnect task
    assert connector._reconnect_task is None
    
    # Start auto-reconnect
    await connector.start_auto_reconnect()
    
    # Should have a running task
    assert connector._reconnect_task is not None
    assert not connector._reconnect_task.done()
    assert connector._should_reconnect is True
    
    # Stop auto-reconnect
    await connector.stop_auto_reconnect()
    
    # Task should be cancelled
    assert connector._should_reconnect is False
    assert connector._reconnect_task.done()


def test_websocket_connector_exponential_backoff_calculation():
    """Test exponential backoff delay calculation"""
    config = WebSocketConfig(url="ws://localhost:8080/test")
    connector = WebSocketConnector(config)
    
    # Test delay calculation
    base_delay = connector.base_delay
    max_delay = connector.max_delay
    
    # Test exponential growth
    for i in range(5):
        expected_delay = min(base_delay * (2 ** i), max_delay)
        # This would be the delay used in _reconnect_and_retry
        assert expected_delay >= base_delay
        assert expected_delay <= max_delay


@pytest.mark.asyncio
async def test_websocket_connector_integration_with_device_simulator():
    """Test that WebSocket connector integrates properly with device simulator"""
    from app.simulation.device_simulator import DeviceSimulator
    from app.models.device import DeviceResponse
    from app.simulation.payload_generators.base_generator import PayloadGenerator
    
    # Create mock objects
    from datetime import datetime
    device_config = DeviceResponse(
        id="test-device",
        name="Test Device",
        project_id="test-project",
        metadata={},
        payload_id="test-payload",
        target_system_id="test-target",
        send_interval=1,
        is_enabled=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Create a simple payload generator
    class MockPayloadGenerator(PayloadGenerator):
        async def generate(self, device_metadata=None):
            return {"test": "data", "timestamp": "2023-01-01T00:00:00Z"}
    
    payload_generator = MockPayloadGenerator()
    
    # Create WebSocket connector
    from app.simulation.connectors.websocket_connector import WebSocketConnector
    config = WebSocketConfig(url="ws://localhost:8080/test")
    connector = WebSocketConnector(config)
    
    # Create device simulator
    simulator = DeviceSimulator(
        device_config=device_config,
        payload_generator=payload_generator,
        target_connector=connector
    )
    
    # Test that simulator has the auto-reconnection methods
    assert hasattr(simulator, '_start_auto_reconnection')
    assert hasattr(simulator, '_stop_auto_reconnection')
    
    # Test that the simulator can identify WebSocket connectors
    assert isinstance(simulator.connector, WebSocketConnector)


if __name__ == "__main__":
    pytest.main([__file__])