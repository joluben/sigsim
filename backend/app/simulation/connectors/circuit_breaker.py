"""
Circuit breaker pattern implementation for target connectors
"""
import asyncio
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable, Any, Optional


class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open, failing fast
    HALF_OPEN = "half_open"  # Testing if service is back


class CircuitBreaker:
    """
    Circuit breaker implementation to prevent cascading failures
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitState.CLOSED
        
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If circuit is open or function fails
        """
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
            
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True
        
        return datetime.utcnow() - self.last_failure_time >= timedelta(seconds=self.recovery_timeout)
    
    def _on_success(self):
        """Handle successful operation"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        """Handle failed operation"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
    
    def get_state(self) -> dict:
        """Get current circuit breaker state"""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time,
            "failure_threshold": self.failure_threshold,
            "recovery_timeout": self.recovery_timeout
        }
    
    def reset(self):
        """Manually reset the circuit breaker"""
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED


class ResilientConnector:
    """
    Base class for connectors with circuit breaker support
    """
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout
        )
    
    async def send_with_circuit_breaker(self, send_func: Callable, payload: dict) -> bool:
        """
        Send payload using circuit breaker protection
        
        Args:
            send_func: The actual send function to call
            payload: Payload to send
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = await self.circuit_breaker.call(send_func, payload)
            return result
        except Exception as e:
            print(f"Circuit breaker prevented call or call failed: {e}")
            return False
    
    def get_circuit_state(self) -> dict:
        """Get circuit breaker state"""
        return self.circuit_breaker.get_state()
    
    def reset_circuit(self):
        """Reset circuit breaker"""
        self.circuit_breaker.reset()