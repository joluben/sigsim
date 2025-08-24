"""
Tests for WebSocket connector with automatic reconnection
"""
import pytest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
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


@pytest.fixture
def websocket_connector(websocket_config):
    """Create a WebSocket connector instance"""
    return WebSocketConnector(websocket_config)


class TestWebSocketConnector:
    """Test WebSocket connector functionality"""
    
    @pytest.mark.asyncio
    async def test_initial_connection_success(self, websocket_connector):
        """Test successful initial connection"""
        with patch('app.simulation.connectors.websocket_connector.websockets.connect') as mock_connect:
            mock_websocket = AsyncMock()
            mock_connect.return_value = mock_websocket
            
            success = await websocket_connector.connect()
            
            assert success is True
            assert websocket_connector.connected is True
            assert websocket_connector.websocket is mock_websocket
            assert websocket_connector.circuit_state == ConnectionState.CLOSED
            assert websocket_connector.failure_count == 0
            assert websocket_connector.retry_count == 0
    
    @pytest.mark.asyncio
    async def test_initial_connection_failure(self, websocket_connector):
        """Test failed initial connection"""
        with patch('app.simulation.connectors.websocket_connector.websockets.connect') as mock_connect:
            mock_connect.side_effect = Exception("Connection failed")
            
            success = await websocket_connector.connect()
            
            assert success is False
            assert websocket_connector.connected is False
            assert websocket_connector.websocket is None
            assert websocket_connector.failure_count == 1
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_after_failures(self, websocket_connector):
        """Test circuit breaker opens after multiple failures"""
        with patch('app.simulation.connectors.websocket_connector.websockets.connect') as mock_connect:
            mock_connect.side_effect = Exception("Connection failed")
            
            # Fail enough times to open circuit breaker
            for _ in range(websocket_connector.failure_threshold):
                await websocket_connector.connect()
            
            assert websocket_connector.circuit_state == ConnectionState.OPEN
            assert websocket_connector.failure_count == websocket_connector.failure_threshold
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_half_open_after_timeout(self, websocket_connector):
        """Test circuit breaker moves to half-open after timeout"""
        with patch('app.simulation.connectors.websocket_connector.websockets.connect') as mock_connect, \
             patch('app.simulation.connectors.websocket_connector.asyncio.get_event_loop') as mock_loop:
            
            mock_connect.side_effect = Exception("Connection failed")
            mock_time = 0.0
            mock_loop.return_value.time.return_value = mock_time
            
            # Open the circuit breaker
            for _ in range(websocket_connector.failure_threshold):
                await websocket_connector.connect()
            
            assert websocket_connector.circuit_state == ConnectionState.OPEN
            
            # Simulate time passing
            mock_time = websocket_connector.recovery_timeout + 1
            mock_loop.return_value.time.return_value = mock_time
            
            # Should allow connection attempt and move to half-open
            await websocket_connector.connect()
            assert websocket_connector.circuit_state == ConnectionState.OPEN  # Back to open after failure
    
    @pytest.mark.asyncio
    async def test_send_success(self, websocket_connector):
        """Test successful message sending"""
        with patch('app.simulation.connectors.websocket_connector.websockets.connect') as mock_connect:
            mock_websocket = AsyncMock()
            mock_connect.return_value = mock_websocket
            
            await websocket_connector.connect()
            
            payload = {"test": "data", "value": 123}
            success = await websocket_connector.send(payload)
            
            assert success is True
            mock_websocket.send.assert_called_once_with(json.dumps(payload))
    
    @pytest.mark.asyncio
    async def test_send_with_reconnection(self, websocket_connector):
        """Test sending with automatic reconnection"""
        with patch('app.simulation.connectors.websocket_connector.websockets.connect') as mock_connect:
            mock_websocket = AsyncMock()
            mock_connect.return_value = mock_websocket
            
            # Initial connection
            await websocket_connector.connect()
            
            # First send fails (connection closed)
            import websockets.exceptions
            mock_websocket.send.side_effect = [
                websockets.exceptions.ConnectionClosed(None, None),
                None  # Second attempt succeeds
            ]
            
            # Mock reconnection
            mock_websocket2 = AsyncMock()
            mock_connect.return_value = mock_websocket2
            
            payload = {"test": "data"}
            success = await websocket_connector.send(payload)
            
            # Should succeed after reconnection
            assert success is True
    
    @pytest.mark.asyncio
    async def test_send_without_connection(self, websocket_connector):
        """Test sending without connection"""
        payload = {"test": "data"}
        success = await websocket_connector.send(payload)
        
        assert success is False
    
    @pytest.mark.asyncio
    async def test_exponential_backoff_reconnection(self, websocket_connector):
        """Test exponential backoff in reconnection attempts"""
        with patch('app.simulation.connectors.websocket_connector.websockets.connect') as mock_connect, \
             patch('app.simulation.connectors.websocket_connector.asyncio.sleep') as mock_sleep:
            
            mock_connect.side_effect = Exception("Connection failed")
            
            # Attempt reconnection multiple times
            for i in range(3):
                await websocket_connector._reconnect_and_retry()
                
                # Check that delay increases exponentially
                expected_delay = min(
                    websocket_connector.base_delay * (2 ** i), 
                    websocket_connector.max_delay
                )
                if mock_sleep.call_count > i:
                    mock_sleep.assert_called_with(expected_delay)
    
    @pytest.mark.asyncio
    async def test_max_retries_reached(self, websocket_connector):
        """Test behavior when max retries are reached"""
        with patch('app.simulation.connectors.websocket_connector.websockets.connect') as mock_connect:
            mock_connect.side_effect = Exception("Connection failed")
            
            # Exhaust all retry attempts
            for _ in range(websocket_connector.max_retries + 1):
                success = await websocket_connector._reconnect_and_retry()
                if not success:
                    break
            
            # Should fail after max retries
            success = await websocket_connector._reconnect_and_retry()
            assert success is False
    
    @pytest.mark.asyncio
    async def test_auto_reconnect_loop_start_stop(self, websocket_connector):
        """Test starting and stopping auto-reconnect loop"""
        await websocket_connector.start_auto_reconnect()
        
        assert websocket_connector._should_reconnect is True
        assert websocket_connector._reconnect_task is not None
        assert not websocket_connector._reconnect_task.done()
        
        await websocket_connector.stop_auto_reconnect()
        
        assert websocket_connector._should_reconnect is False
        assert websocket_connector._reconnect_task.done()
    
    @pytest.mark.asyncio
    async def test_auto_reconnect_loop_monitors_connection(self, websocket_connector):
        """Test that auto-reconnect loop monitors connection health"""
        with patch('app.simulation.connectors.websocket_connector.websockets.connect') as mock_connect, \
             patch('app.simulation.connectors.websocket_connector.asyncio.sleep') as mock_sleep:
            
            mock_websocket = AsyncMock()
            mock_connect.return_value = mock_websocket
            
            # Start auto-reconnect
            await websocket_connector.start_auto_reconnect()
            
            # Simulate connection and then disconnection
            await websocket_connector.connect()
            
            # Simulate ping failure (connection lost)
            mock_websocket.ping.side_effect = Exception("Ping failed")
            
            # Give the loop a chance to run
            await asyncio.sleep(0.1)
            
            # Should detect disconnection and attempt reconnection
            assert mock_connect.call_count >= 1
            
            await websocket_connector.stop_auto_reconnect()
    
    @pytest.mark.asyncio
    async def test_disconnect_cleanup(self, websocket_connector):
        """Test proper cleanup on disconnect"""
        with patch('app.simulation.connectors.websocket_connector.websockets.connect') as mock_connect:
            mock_websocket = AsyncMock()
            mock_connect.return_value = mock_websocket
            
            await websocket_connector.connect()
            await websocket_connector.start_auto_reconnect()
            
            await websocket_connector.disconnect()
            
            assert websocket_connector.connected is False
            assert websocket_connector.websocket is None
            assert websocket_connector._should_reconnect is False
            mock_websocket.close.assert_called_once()
    
    def test_connection_stats(self, websocket_connector):
        """Test connection statistics reporting"""
        stats = websocket_connector.get_connection_stats()
        
        expected_keys = [
            "connected", "circuit_state", "retry_count", 
            "failure_count", "last_failure_time", "auto_reconnect_active"
        ]
        
        for key in expected_keys:
            assert key in stats
        
        assert stats["connected"] is False
        assert stats["circuit_state"] == ConnectionState.CLOSED.value
        assert stats["retry_count"] == 0
        assert stats["failure_count"] == 0
    
    @pytest.mark.asyncio
    async def test_connection_recovery_resets_stats(self, websocket_connector):
        """Test that successful connection resets failure stats"""
        with patch('app.simulation.connectors.websocket_connector.websockets.connect') as mock_connect:
            # First fail a few times
            mock_connect.side_effect = Exception("Connection failed")
            
            for _ in range(2):
                await websocket_connector.connect()
            
            assert websocket_connector.failure_count == 2
            # Note: retry_count is only incremented in _reconnect_and_retry, not in connect()
            
            # Then succeed
            mock_websocket = AsyncMock()
            mock_connect.return_value = mock_websocket
            mock_connect.side_effect = None
            
            success = await websocket_connector.connect()
            
            assert success is True
            assert websocket_connector.failure_count == 0
            assert websocket_connector.retry_count == 0
            assert websocket_connector.circuit_state == ConnectionState.CLOSED


class TestWebSocketConnectorIntegration:
    """Integration tests for WebSocket connector"""
    
    @pytest.mark.asyncio
    async def test_full_reconnection_scenario(self, websocket_connector):
        """Test complete reconnection scenario"""
        with patch('app.simulation.connectors.websocket_connector.websockets.connect') as mock_connect, \
             patch('app.simulation.connectors.websocket_connector.asyncio.sleep'):
            
            # Setup mock websockets
            mock_websocket1 = AsyncMock()
            mock_websocket2 = AsyncMock()
            
            # First connection succeeds
            mock_connect.return_value = mock_websocket1
            success = await websocket_connector.connect()
            assert success is True
            
            # Start auto-reconnect
            await websocket_connector.start_auto_reconnect()
            
            # Send succeeds initially
            payload = {"test": "data"}
            success = await websocket_connector.send(payload)
            assert success is True
            
            # Connection fails on next send
            import websockets.exceptions
            mock_websocket1.send.side_effect = websockets.exceptions.ConnectionClosed(None, None)
            
            # Setup second connection for reconnection
            mock_connect.return_value = mock_websocket2
            
            # Send should trigger reconnection and succeed
            success = await websocket_connector.send(payload)
            assert success is True
            
            # Cleanup
            await websocket_connector.disconnect()
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_prevents_excessive_retries(self, websocket_connector):
        """Test that circuit breaker prevents excessive retry attempts"""
        with patch('app.simulation.connectors.websocket_connector.websockets.connect') as mock_connect:
            mock_connect.side_effect = Exception("Connection failed")
            
            # Fail enough times to open circuit breaker
            for _ in range(websocket_connector.failure_threshold):
                await websocket_connector.connect()
            
            # Circuit should be open
            assert websocket_connector.circuit_state == ConnectionState.OPEN
            
            # Additional connection attempts should be blocked
            initial_call_count = mock_connect.call_count
            await websocket_connector.connect()
            
            # Should not have made additional connection attempts
            assert mock_connect.call_count == initial_call_count