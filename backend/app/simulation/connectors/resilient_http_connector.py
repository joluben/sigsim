"""
Resilient HTTP/HTTPS target connector with circuit breaker
"""
import json
import aiohttp
from datetime import datetime
from typing import Dict, Any
from app.simulation.connectors.base_connector import TargetConnector
from app.simulation.connectors.circuit_breaker import ResilientConnector
from app.models.target import HTTPConfig


class ResilientHTTPConnector(TargetConnector, ResilientConnector):
    """Resilient connector for HTTP/HTTPS endpoints with circuit breaker"""
    
    def __init__(self, config: HTTPConfig, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        TargetConnector.__init__(self)
        ResilientConnector.__init__(self, failure_threshold, recovery_timeout)
        
        self.config = config
        self.session: aiohttp.ClientSession = None
        self.connection_pool_size = 10
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
    
    async def connect(self) -> bool:
        """Initialize HTTP session with connection pooling"""
        try:
            if self.session and not self.session.closed:
                return True
            
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            connector = aiohttp.TCPConnector(
                limit=self.connection_pool_size,
                limit_per_host=self.connection_pool_size,
                ttl_dns_cache=300,
                use_dns_cache=True,
            )
            
            self.session = aiohttp.ClientSession(
                headers=self.config.headers,
                timeout=timeout,
                connector=connector
            )
            
            # Test connection with a simple request
            await self._test_connection()
            return True
            
        except Exception as e:
            print(f"HTTP connection failed: {e}")
            if self.session:
                await self.session.close()
                self.session = None
            return False
    
    async def send(self, payload: Dict[str, Any]) -> bool:
        """Send HTTP request with payload using circuit breaker"""
        if not self.session or self.session.closed:
            if not await self.connect():
                return False
        
        self.total_requests += 1
        
        # Use circuit breaker for resilient sending
        success = await self.send_with_circuit_breaker(self._send_internal, payload)
        
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        
        return success
    
    async def _send_internal(self, payload: Dict[str, Any]) -> bool:
        """Internal send method protected by circuit breaker"""
        try:
            method = self.config.method.upper()
            
            # Add timestamp if not present
            if 'timestamp' not in payload:
                payload['timestamp'] = datetime.utcnow().isoformat()
            
            # Add request metadata
            payload['_request_id'] = f"{self.total_requests}_{datetime.utcnow().timestamp()}"
            
            if method == "GET":
                async with self.session.get(self.config.url, params=payload) as response:
                    return await self._handle_response(response, method)
            elif method == "POST":
                async with self.session.post(self.config.url, json=payload) as response:
                    return await self._handle_response(response, method)
            elif method == "PUT":
                async with self.session.put(self.config.url, json=payload) as response:
                    return await self._handle_response(response, method)
            elif method == "PATCH":
                async with self.session.patch(self.config.url, json=payload) as response:
                    return await self._handle_response(response, method)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
        except aiohttp.ClientError as e:
            print(f"HTTP client error: {e}")
            # Close session to force reconnection
            await self.disconnect()
            raise e
        except Exception as e:
            print(f"HTTP send failed: {e}")
            raise e
    
    async def _handle_response(self, response: aiohttp.ClientResponse, method: str) -> bool:
        """Handle HTTP response"""
        success = response.status < 400
        
        if not success:
            error_text = await response.text()
            error_msg = f"HTTP {method} failed with status {response.status}: {error_text}"
            print(error_msg)
            
            # For certain status codes, close connection
            if response.status >= 500:
                await self.disconnect()
            
            raise aiohttp.ClientResponseError(
                request_info=response.request_info,
                history=response.history,
                status=response.status,
                message=error_text
            )
        
        return True
    
    async def _test_connection(self):
        """Test connection to the target endpoint"""
        try:
            # Simple HEAD request to test connectivity
            async with self.session.head(self.config.url) as response:
                # Accept any response that indicates the server is reachable
                if response.status < 500:
                    return True
                else:
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status
                    )
        except Exception as e:
            print(f"Connection test failed: {e}")
            raise e
    
    async def disconnect(self):
        """Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connector statistics"""
        circuit_state = self.get_circuit_state()
        
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": self.successful_requests / max(self.total_requests, 1),
            "circuit_breaker": circuit_state,
            "is_connected": self.session is not None and not self.session.closed
        }