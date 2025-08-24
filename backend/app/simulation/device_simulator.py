"""
Individual device simulator
"""
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from app.models.device import DeviceResponse
from app.simulation.payload_generators.base_generator import PayloadGenerator
from app.simulation.connectors.base_connector import TargetConnector
from app.models.simulation import SimulationLogEntry
from app.simulation.metrics import metrics_collector


class DeviceStats:
    """Statistics for a device simulator"""
    
    def __init__(self):
        self.messages_sent = 0
        self.errors = 0
        self.connection_errors = 0
        self.send_errors = 0
        self.last_message_at: Optional[datetime] = None
        self.last_error: Optional[str] = None
        self.last_success_at: Optional[datetime] = None
        self.consecutive_errors = 0
        self.total_retries = 0
    
    def increment_messages(self):
        """Increment message count"""
        self.messages_sent += 1
        self.last_message_at = datetime.utcnow()
        self.last_success_at = datetime.utcnow()
        self.consecutive_errors = 0  # Reset consecutive errors on success
    
    def record_error(self, error: str, error_type: str = "general"):
        """Record an error"""
        self.errors += 1
        self.consecutive_errors += 1
        self.last_error = error
        
        if error_type == "connection":
            self.connection_errors += 1
        elif error_type == "send":
            self.send_errors += 1
    
    def record_retry(self):
        """Record a retry attempt"""
        self.total_retries += 1


class DeviceSimulator:
    """Simulates an individual IoT device"""
    
    def __init__(
        self,
        device_config: DeviceResponse,
        payload_generator: PayloadGenerator,
        target_connector: TargetConnector,
        log_callback=None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        max_consecutive_errors: int = 10
    ):
        self.config = device_config
        self.payload_generator = payload_generator
        self.connector = target_connector
        self.log_callback = log_callback
        self.is_running = False
        self.stats = DeviceStats()
        
        # Retry configuration
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.max_consecutive_errors = max_consecutive_errors
        
        # Connection state
        self.is_connected = False
        self.last_connection_attempt = None
        
        # Metrics tracking
        self.device_metrics = metrics_collector.get_or_create_device_metrics(
            device_config.id, device_config.name
        )
        self.connector_id = f"{device_config.id}_{target_connector.__class__.__name__}"
    
    async def run(self):
        """Main simulation loop for the device"""
        self.is_running = True
        
        # Log device started
        await self._log_event("started", "Device simulation started")
        
        try:
            # Start auto-reconnection for WebSocket connectors
            await self._start_auto_reconnection()
            
            # Initial connection to target system
            await self._ensure_connection()
            
            while self.is_running:
                try:
                    # Check if we need to stop due to too many consecutive errors
                    if self.stats.consecutive_errors >= self.max_consecutive_errors:
                        await self._log_event(
                            "error", 
                            f"Device stopped due to {self.max_consecutive_errors} consecutive errors"
                        )
                        break
                    
                    # Generate payload with device metadata
                    payload = await self._generate_payload()
                    
                    # Send payload with retry logic
                    success = await self._send_with_retry(payload)
                    
                    if success:
                        self.stats.increment_messages()
                        await self._log_event(
                            "message_sent",
                            f"Message sent successfully to {self.connector.__class__.__name__}",
                            payload
                        )
                    else:
                        self.stats.record_error("Failed to send message after retries", "send")
                        await self._log_event("error", "Failed to send message to target system after retries")
                    
                    # Wait for next interval
                    await asyncio.sleep(self.config.send_interval)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    error_msg = f"Unexpected error in device simulation: {str(e)}"
                    self.stats.record_error(error_msg)
                    await self._log_event("error", error_msg)
                    
                    # Wait before retrying (adaptive delay based on consecutive errors)
                    retry_delay = min(30, self.retry_delay * (2 ** min(self.stats.consecutive_errors, 5)))
                    await asyncio.sleep(retry_delay)
        
        except asyncio.CancelledError:
            pass
        finally:
            self.is_running = False
            await self._stop_auto_reconnection()
            await self._safe_disconnect()
            await self._log_event("stopped", "Device simulation stopped")
    
    async def _log_event(self, event_type: str, message: str, payload: Dict[str, Any] = None):
        """Log a simulation event"""
        if self.log_callback:
            log_entry = SimulationLogEntry(
                timestamp=datetime.utcnow(),
                device_id=self.config.id,
                device_name=self.config.name,
                event_type=event_type,
                message=message,
                payload=payload
            )
            await self.log_callback(log_entry)
    
    async def _start_auto_reconnection(self):
        """Start auto-reconnection for WebSocket connectors"""
        from app.simulation.connectors.websocket_connector import WebSocketConnector
        
        if isinstance(self.connector, WebSocketConnector):
            await self.connector.start_auto_reconnect()
            await self._log_event("info", "Auto-reconnection started for WebSocket connector")
    
    async def _stop_auto_reconnection(self):
        """Stop auto-reconnection for WebSocket connectors"""
        from app.simulation.connectors.websocket_connector import WebSocketConnector
        
        if isinstance(self.connector, WebSocketConnector):
            await self.connector.stop_auto_reconnect()
            await self._log_event("info", "Auto-reconnection stopped for WebSocket connector")
    
    async def _ensure_connection(self):
        """Ensure connection to target system with retry logic"""
        from app.simulation.connectors.websocket_connector import WebSocketConnector
        
        if self.is_connected:
            return True
        
        # For WebSocket connectors with auto-reconnection, just try once
        # as they handle their own reconnection logic
        if isinstance(self.connector, WebSocketConnector):
            try:
                self.last_connection_attempt = datetime.utcnow()
                success = await self.connector.connect()
                
                if success:
                    self.is_connected = True
                    await self._log_event("connected", f"Connected to {self.connector.__class__.__name__}")
                    return True
                else:
                    await self._log_event("warning", "WebSocket connection failed, auto-reconnection will handle retries")
                    return False
                    
            except Exception as e:
                error_msg = f"WebSocket connection failed: {str(e)}"
                self.stats.record_error(error_msg, "connection")
                await self._log_event("warning", error_msg + ", auto-reconnection will handle retries")
                return False
        
        # For other connectors, use the original retry logic
        for attempt in range(self.max_retries + 1):
            try:
                self.last_connection_attempt = datetime.utcnow()
                success = await self.connector.connect()
                
                if success:
                    self.is_connected = True
                    await self._log_event("connected", f"Connected to {self.connector.__class__.__name__}")
                    return True
                else:
                    if attempt < self.max_retries:
                        self.stats.record_retry()
                        await self._log_event("warning", f"Connection attempt {attempt + 1} failed, retrying...")
                        await asyncio.sleep(self.retry_delay * (2 ** attempt))
                    
            except Exception as e:
                error_msg = f"Connection attempt {attempt + 1} failed: {str(e)}"
                self.stats.record_error(error_msg, "connection")
                
                if attempt < self.max_retries:
                    self.stats.record_retry()
                    await self._log_event("warning", error_msg + ", retrying...")
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                else:
                    await self._log_event("error", f"Failed to connect after {self.max_retries + 1} attempts")
        
        return False
    
    async def _generate_payload(self) -> Dict[str, Any]:
        """Generate payload with error handling"""
        try:
            payload = await self.payload_generator.generate(
                device_metadata=self.config.metadata
            )
            
            # Ensure payload is a dictionary
            if not isinstance(payload, dict):
                raise ValueError(f"Payload generator returned invalid type: {type(payload)}")
            
            # Add device identification to payload if not present
            if 'device_id' not in payload and self.config.id:
                payload['device_id'] = self.config.id
            if 'device_name' not in payload and self.config.name:
                payload['device_name'] = self.config.name
            
            # Record successful payload generation
            self.device_metrics.record_message_generated()
            
            return payload
            
        except Exception as e:
            # Record payload generation failure
            self.device_metrics.record_payload_failure()
            
            # Return a basic payload if generation fails
            error_msg = f"Payload generation failed: {str(e)}"
            self.stats.record_error(error_msg)
            await self._log_event("warning", error_msg + ", using fallback payload")
            
            return {
                "device_id": self.config.id,
                "device_name": self.config.name,
                "timestamp": datetime.utcnow().isoformat(),
                "error": "payload_generation_failed",
                "message": str(e)
            }
    
    async def _send_with_retry(self, payload: Dict[str, Any]) -> bool:
        """Send payload with retry logic"""
        from app.simulation.connectors.websocket_connector import WebSocketConnector
        
        start_time = datetime.utcnow()
        
        # For WebSocket connectors, rely on their internal retry logic
        if isinstance(self.connector, WebSocketConnector):
            try:
                send_start = datetime.utcnow()
                success = await self.connector.send(payload)
                response_time = (datetime.utcnow() - send_start).total_seconds()
                
                if success:
                    # Record successful send
                    payload_size = len(str(payload).encode('utf-8'))
                    metrics_collector.record_connector_success(
                        self.connector_id,
                        self.connector.__class__.__name__,
                        response_time,
                        payload_size
                    )
                    self.device_metrics.record_message_sent()
                    self.is_connected = True  # Update connection status
                    return True
                else:
                    # WebSocket connector handles its own retries, so this is a final failure
                    metrics_collector.record_connector_failure(
                        self.connector_id,
                        self.connector.__class__.__name__,
                        "WebSocket send failed after internal retries"
                    )
                    self.device_metrics.record_send_failure()
                    self.is_connected = False  # Update connection status
                    return False
                    
            except Exception as e:
                error_msg = f"WebSocket send failed: {str(e)}"
                self.stats.record_error(error_msg, "send")
                metrics_collector.record_connector_failure(
                    self.connector_id,
                    self.connector.__class__.__name__,
                    str(e)
                )
                self.device_metrics.record_send_failure()
                self.is_connected = False
                return False
        
        # For other connectors, use the original retry logic
        for attempt in range(self.max_retries + 1):
            try:
                # Ensure we're connected before sending
                if not self.is_connected:
                    connection_success = await self._ensure_connection()
                    if not connection_success:
                        # Record connection failure
                        metrics_collector.record_connector_failure(
                            self.connector_id,
                            self.connector.__class__.__name__,
                            "Connection failed",
                            is_connection_error=True
                        )
                        self.device_metrics.record_send_failure()
                        return False
                
                # Attempt to send
                send_start = datetime.utcnow()
                success = await self.connector.send(payload)
                response_time = (datetime.utcnow() - send_start).total_seconds()
                
                if success:
                    # Record successful send
                    payload_size = len(str(payload).encode('utf-8'))
                    metrics_collector.record_connector_success(
                        self.connector_id,
                        self.connector.__class__.__name__,
                        response_time,
                        payload_size
                    )
                    self.device_metrics.record_message_sent()
                    return True
                else:
                    # Send failed, but no exception - might be a temporary issue
                    if attempt < self.max_retries:
                        self.stats.record_retry()
                        self.device_metrics.record_retry()
                        await self._log_event("warning", f"Send attempt {attempt + 1} failed, retrying...")
                        await asyncio.sleep(self.retry_delay * (2 ** attempt))
                        
                        # Mark as disconnected to force reconnection on next attempt
                        self.is_connected = False
                    else:
                        # Record final failure
                        metrics_collector.record_connector_failure(
                            self.connector_id,
                            self.connector.__class__.__name__,
                            "Send failed after retries"
                        )
                        self.device_metrics.record_send_failure()
                    
            except Exception as e:
                error_msg = f"Send attempt {attempt + 1} failed: {str(e)}"
                
                if attempt < self.max_retries:
                    self.stats.record_retry()
                    self.device_metrics.record_retry()
                    await self._log_event("warning", error_msg + ", retrying...")
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                    
                    # Mark as disconnected to force reconnection on next attempt
                    self.is_connected = False
                else:
                    self.stats.record_error(error_msg, "send")
                    # Record final failure with exception details
                    metrics_collector.record_connector_failure(
                        self.connector_id,
                        self.connector.__class__.__name__,
                        str(e)
                    )
                    self.device_metrics.record_send_failure()
                    await self._log_event("error", f"Send failed after {self.max_retries + 1} attempts: {str(e)}")
        
        return False
    
    async def _safe_disconnect(self):
        """Safely disconnect from target system"""
        try:
            if self.is_connected:
                await self.connector.disconnect()
                self.is_connected = False
                await self._log_event("disconnected", "Disconnected from target system")
        except Exception as e:
            await self._log_event("warning", f"Error during disconnect: {str(e)}")
    
    def get_status(self):
        """Get current device status"""
        from app.simulation.connectors.websocket_connector import WebSocketConnector
        
        status = {
            "device_id": self.config.id,
            "device_name": self.config.name,
            "is_running": self.is_running,
            "is_connected": self.is_connected,
            "messages_sent": self.stats.messages_sent,
            "errors": self.stats.errors,
            "connection_errors": self.stats.connection_errors,
            "send_errors": self.stats.send_errors,
            "consecutive_errors": self.stats.consecutive_errors,
            "total_retries": self.stats.total_retries,
            "last_message_at": self.stats.last_message_at,
            "last_success_at": self.stats.last_success_at,
            "last_error": self.stats.last_error,
            "last_connection_attempt": self.last_connection_attempt
        }
        
        # Add WebSocket-specific connection statistics
        if isinstance(self.connector, WebSocketConnector):
            websocket_stats = self.connector.get_connection_stats()
            status["websocket_stats"] = websocket_stats
        
        return status