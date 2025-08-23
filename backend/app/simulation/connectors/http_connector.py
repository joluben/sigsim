"""
HTTP/HTTPS target connector
"""
import json
import aiohttp
from typing import Dict, Any
from app.simulation.connectors.base_connector import TargetConnector
from app.models.target import HTTPConfig


class HTTPConnector(TargetConnector):
    """Connector for HTTP/HTTPS endpoints"""
    
    def __init__(self, config: HTTPConfig):
        self.config = config
        self.session: aiohttp.ClientSession = None
    
    async def connect(self) -> bool:
        """Initialize HTTP session"""
        try:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self.session = aiohttp.ClientSession(
                headers=self.config.headers,
                timeout=timeout
            )
            return True
        except Exception as e:
            print(f"HTTP connection failed: {e}")
            return False
    
    async def send(self, payload: Dict[str, Any]) -> bool:
        """Send HTTP request with payload"""
        if not self.session:
            # Try to reconnect if session is not available
            if not await self.connect():
                return False
        
        try:
            method = self.config.method.upper()
            
            # Add timestamp if not present
            if 'timestamp' not in payload:
                from datetime import datetime
                payload['timestamp'] = datetime.utcnow().isoformat()
            
            if method == "GET":
                async with self.session.get(self.config.url, params=payload) as response:
                    success = response.status < 400
                    if not success:
                        print(f"HTTP GET failed with status {response.status}: {await response.text()}")
                    return success
            elif method == "POST":
                async with self.session.post(self.config.url, json=payload) as response:
                    success = response.status < 400
                    if not success:
                        print(f"HTTP POST failed with status {response.status}: {await response.text()}")
                    return success
            elif method == "PUT":
                async with self.session.put(self.config.url, json=payload) as response:
                    success = response.status < 400
                    if not success:
                        print(f"HTTP PUT failed with status {response.status}: {await response.text()}")
                    return success
            elif method == "PATCH":
                async with self.session.patch(self.config.url, json=payload) as response:
                    success = response.status < 400
                    if not success:
                        print(f"HTTP PATCH failed with status {response.status}: {await response.text()}")
                    return success
            else:
                print(f"Unsupported HTTP method: {method}")
                return False
                
        except aiohttp.ClientError as e:
            print(f"HTTP client error: {e}")
            # Close session to force reconnection on next attempt
            await self.disconnect()
            return False
        except Exception as e:
            print(f"HTTP send failed: {e}")
            return False
    
    async def disconnect(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None