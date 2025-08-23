"""
MQTT target connector
"""
import json
import asyncio
from typing import Dict, Any
import paho.mqtt.client as mqtt
from app.simulation.connectors.base_connector import TargetConnector
from app.models.target import MQTTConfig


class MQTTConnector(TargetConnector):
    """Connector for MQTT brokers"""
    
    def __init__(self, config: MQTTConfig):
        self.config = config
        self.client: mqtt.Client = None
        self.connected = False
        self.connection_event = asyncio.Event()
    
    async def connect(self) -> bool:
        """Connect to MQTT broker"""
        try:
            self.client = mqtt.Client()
            
            # Set callbacks
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            
            # Configure authentication
            if self.config.username:
                self.client.username_pw_set(
                    self.config.username,
                    self.config.password
                )
            
            # Configure TLS
            if self.config.use_tls:
                self.client.tls_set()
            
            # Connect to broker
            self.client.connect_async(self.config.host, self.config.port, 60)
            self.client.loop_start()
            
            # Wait for connection
            await asyncio.wait_for(self.connection_event.wait(), timeout=10)
            return self.connected
            
        except Exception as e:
            print(f"MQTT connection failed: {e}")
            return False
    
    async def send(self, payload: Dict[str, Any]) -> bool:
        """Publish message to MQTT topic"""
        if not self.connected:
            # Try to reconnect if not connected
            if not await self.connect():
                return False
        
        try:
            # Add timestamp if not present
            if 'timestamp' not in payload:
                from datetime import datetime
                payload['timestamp'] = datetime.utcnow().isoformat()
            
            message = json.dumps(payload, default=str)  # Handle datetime objects
            result = self.client.publish(
                self.config.topic,
                message,
                qos=self.config.qos
            )
            
            # Wait for message to be sent
            try:
                result.wait_for_publish(timeout=10)
                success = result.rc == mqtt.MQTT_ERR_SUCCESS
                
                if not success:
                    print(f"MQTT publish failed with return code: {result.rc}")
                    # If publish failed, mark as disconnected to force reconnection
                    self.connected = False
                
                return success
            except Exception as wait_error:
                print(f"MQTT publish timeout or error: {wait_error}")
                self.connected = False
                return False
            
        except json.JSONEncodeError as e:
            print(f"MQTT JSON encoding failed: {e}")
            return False
        except Exception as e:
            print(f"MQTT send failed: {e}")
            self.connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
    
    def _on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            self.connected = True
            self.connection_event.set()
        else:
            print(f"MQTT connection failed with code {rc}")
            self.connected = False
            self.connection_event.set()
    
    def _on_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        self.connected = False