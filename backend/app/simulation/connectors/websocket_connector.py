"""
WebSocket target connector
"""
import json
import asyncio
import websockets
from typing import Dict, Any
from app.simulation.connectors.base_connector import TargetConnector
from app.models.target import WebSocketConfig


class WebSocketConnector(TargetConnector):
    """Connector for WebSocket endpoints"""
    
    def __init__(self, config: WebSocketConfig):
        self.config = config
        self.websocket = None
        self.connected = False
    
    async def connect(self) -> bool:
        """Connect to WebSocket endpoint"""
        try:
            extra_headers = self.config.headers if self.config.headers else None
            
            self.websocket = await websockets.connect(
                self.config.url,
                extra_headers=extra_headers,
                ping_interval=self.config.ping_interval
            )
            
            self.connected = True
            return True
            
        except Exception as e:
            print(f"WebSocket connection failed: {e}")
            return False
    
    async def send(self, payload: Dict[str, Any]) -> bool:
        """Send message via WebSocket"""
        if not self.connected or not self.websocket:
            return False
        
        try:
            message = json.dumps(payload)
            await self.websocket.send(message)
            return True
            
        except Exception as e:
            print(f"WebSocket send failed: {e}")
            return False
    
    async def disconnect(self):
        """Close WebSocket connection"""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
            self.connected = False