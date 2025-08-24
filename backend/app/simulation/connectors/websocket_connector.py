"""
WebSocket target connector with automatic reconnection
"""
import json
import asyncio
import websockets
import logging
from typing import Dict, Any, Optional
from enum import Enum
from app.simulation.connectors.base_connector import TargetConnector
from app.models.target import WebSocketConfig


logger = logging.getLogger(__name__)


class ConnectionState(Enum):
    """Connection states for circuit breaker pattern"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit breaker open, not attempting connections
    HALF_OPEN = "half_open"  # Testing if connection is restored


class WebSocketConnector(TargetConnector):
    """Connector for WebSocket endpoints with automatic reconnection"""
    
    def __init__(self, config: WebSocketConfig):
        self.config = config
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.connected = False
        
        # Reconnection parameters
        self.max_retries = 5
        self.base_delay = 1.0  # Base delay in seconds
        self.max_delay = 60.0  # Maximum delay in seconds
        self.retry_count = 0
        
        # Circuit breaker parameters
        self.circuit_state = ConnectionState.CLOSED
        self.failure_count = 0
        self.failure_threshold = 3
        self.recovery_timeout = 30.0  # Time to wait before trying half-open
        self.last_failure_time = 0.0
        
        # Connection management
        self._reconnect_task: Optional[asyncio.Task] = None
        self._should_reconnect = True
        self._connection_lock = asyncio.Lock()
    
    async def connect(self) -> bool:
        """Connect to WebSocket endpoint with circuit breaker"""
        async with self._connection_lock:
            # Check circuit breaker state
            if not self._should_attempt_connection():
                return False
            
            try:
                await self._establish_connection()
                self._on_connection_success()
                return True
                
            except Exception as e:
                self._on_connection_failure(e)
                return False
    
    async def _establish_connection(self):
        """Establish WebSocket connection"""
        extra_headers = self.config.headers if self.config.headers else None
        
        # Use websockets.connect as a context manager to properly handle the connection
        self.websocket = await websockets.connect(
            self.config.url,
            extra_headers=extra_headers,
            ping_interval=self.config.ping_interval,
            close_timeout=10.0
        )
        
        self.connected = True
        logger.info(f"WebSocket connected to {self.config.url}")
    
    def _should_attempt_connection(self) -> bool:
        """Check if connection attempt should be made based on circuit breaker state"""
        current_time = asyncio.get_event_loop().time()
        
        if self.circuit_state == ConnectionState.CLOSED:
            return True
        elif self.circuit_state == ConnectionState.OPEN:
            # Check if enough time has passed to try half-open
            if current_time - self.last_failure_time >= self.recovery_timeout:
                self.circuit_state = ConnectionState.HALF_OPEN
                logger.info("Circuit breaker moving to HALF_OPEN state")
                return True
            return False
        elif self.circuit_state == ConnectionState.HALF_OPEN:
            return True
        
        return False
    
    def _on_connection_success(self):
        """Handle successful connection"""
        self.retry_count = 0
        self.failure_count = 0
        self.circuit_state = ConnectionState.CLOSED
        logger.info("WebSocket connection established successfully")
    
    def _on_connection_failure(self, error: Exception):
        """Handle connection failure"""
        self.failure_count += 1
        self.last_failure_time = asyncio.get_event_loop().time()
        
        logger.warning(f"WebSocket connection failed (attempt {self.failure_count}): {error}")
        
        # Update circuit breaker state
        if self.failure_count >= self.failure_threshold:
            self.circuit_state = ConnectionState.OPEN
            logger.warning(f"Circuit breaker OPEN after {self.failure_count} failures")
        elif self.circuit_state == ConnectionState.HALF_OPEN:
            self.circuit_state = ConnectionState.OPEN
            logger.warning("Circuit breaker back to OPEN from HALF_OPEN")
    
    async def send(self, payload: Dict[str, Any]) -> bool:
        """Send message via WebSocket with automatic reconnection"""
        # Try to send with current connection
        if await self._try_send(payload):
            return True
        
        # If send failed, try to reconnect and send again
        if self._should_reconnect and await self._reconnect_and_retry():
            return await self._try_send(payload)
        
        return False
    
    async def _try_send(self, payload: Dict[str, Any]) -> bool:
        """Attempt to send payload through current connection"""
        if not self.connected or not self.websocket:
            return False
        
        try:
            message = json.dumps(payload)
            await self.websocket.send(message)
            return True
            
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket connection closed during send")
            self.connected = False
            return False
        except Exception as e:
            logger.error(f"WebSocket send failed: {e}")
            self.connected = False
            return False
    
    async def _reconnect_and_retry(self) -> bool:
        """Attempt to reconnect with exponential backoff"""
        if self.retry_count >= self.max_retries:
            logger.error(f"Max reconnection attempts ({self.max_retries}) reached")
            return False
        
        # Calculate delay with exponential backoff
        delay = min(self.base_delay * (2 ** self.retry_count), self.max_delay)
        self.retry_count += 1
        
        logger.info(f"Attempting reconnection {self.retry_count}/{self.max_retries} after {delay}s delay")
        
        try:
            await asyncio.sleep(delay)
            return await self.connect()
        except Exception as e:
            logger.error(f"Reconnection attempt {self.retry_count} failed: {e}")
            return False
    
    async def start_auto_reconnect(self):
        """Start background task for automatic reconnection monitoring"""
        if self._reconnect_task and not self._reconnect_task.done():
            return
        
        self._should_reconnect = True
        self._reconnect_task = asyncio.create_task(self._auto_reconnect_loop())
    
    async def stop_auto_reconnect(self):
        """Stop automatic reconnection"""
        self._should_reconnect = False
        if self._reconnect_task and not self._reconnect_task.done():
            self._reconnect_task.cancel()
            try:
                await self._reconnect_task
            except asyncio.CancelledError:
                pass
    
    async def _auto_reconnect_loop(self):
        """Background loop to monitor connection and reconnect if needed"""
        while self._should_reconnect:
            try:
                # Check connection health
                if self.connected and self.websocket:
                    try:
                        # Send ping to check if connection is alive
                        await self.websocket.ping()
                        await asyncio.sleep(self.config.ping_interval)
                        continue
                    except Exception:
                        logger.warning("WebSocket ping failed, connection lost")
                        self.connected = False
                
                # If not connected, try to reconnect
                if not self.connected:
                    logger.info("Attempting automatic reconnection...")
                    await self.connect()
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in auto-reconnect loop: {e}")
                await asyncio.sleep(10)  # Wait longer on error
    
    async def disconnect(self):
        """Close WebSocket connection and stop reconnection"""
        await self.stop_auto_reconnect()
        
        if self.websocket:
            try:
                await self.websocket.close()
            except Exception as e:
                logger.warning(f"Error closing WebSocket: {e}")
            finally:
                self.websocket = None
                self.connected = False
        
        logger.info("WebSocket disconnected")
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics for monitoring"""
        return {
            "connected": self.connected,
            "circuit_state": self.circuit_state.value,
            "retry_count": self.retry_count,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time,
            "auto_reconnect_active": self._should_reconnect and self._reconnect_task and not self._reconnect_task.done()
        }