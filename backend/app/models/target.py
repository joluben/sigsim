"""
Target System Pydantic models for API validation
"""
from pydantic import BaseModel, Field, validator
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum
from urllib.parse import urlparse


class TargetType(str, Enum):
    MQTT = "mqtt"
    HTTP = "http"
    KAFKA = "kafka"
    WEBSOCKET = "websocket"
    FTP = "ftp"
    PUBSUB = "pubsub"


class TargetSystemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Target system name")
    type: TargetType = Field(..., description="Target system type")
    config: Dict[str, Any] = Field(..., description="Target system configuration")
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Target system name cannot be empty')
        return v.strip()
    
    @validator('config')
    def validate_config(cls, v, values):
        target_type = values.get('type')
        if not v:
            raise ValueError('Configuration is required')
        
        # Validate configuration based on target type
        if target_type == TargetType.MQTT:
            return cls._validate_mqtt_config(v)
        elif target_type == TargetType.HTTP:
            return cls._validate_http_config(v)
        elif target_type == TargetType.KAFKA:
            return cls._validate_kafka_config(v)
        elif target_type == TargetType.WEBSOCKET:
            return cls._validate_websocket_config(v)
        
        return v
    
    @staticmethod
    def _validate_mqtt_config(config):
        required_fields = ['host', 'port', 'topic']
        for field in required_fields:
            if field not in config:
                raise ValueError(f'MQTT configuration missing required field: {field}')
        
        port = config.get('port')
        if not isinstance(port, int) or port < 1 or port > 65535:
            raise ValueError('MQTT port must be between 1 and 65535')
        
        return config
    
    @staticmethod
    def _validate_http_config(config):
        if 'url' not in config:
            raise ValueError('HTTP configuration missing required field: url')
        
        url = config['url']
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError('Invalid HTTP URL format')
        
        method = config.get('method', 'POST').upper()
        if method not in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
            raise ValueError('Invalid HTTP method')
        
        return config
    
    @staticmethod
    def _validate_kafka_config(config):
        required_fields = ['bootstrap_servers', 'topic']
        for field in required_fields:
            if field not in config:
                raise ValueError(f'Kafka configuration missing required field: {field}')
        
        return config
    
    @staticmethod
    def _validate_websocket_config(config):
        if 'url' not in config:
            raise ValueError('WebSocket configuration missing required field: url')
        
        url = config['url']
        if not (url.startswith('ws://') or url.startswith('wss://')):
            raise ValueError('WebSocket URL must start with ws:// or wss://')
        
        return config


class TargetSystemCreate(TargetSystemBase):
    """Model for creating a new target system"""
    pass


class TargetSystemUpdate(BaseModel):
    """Model for updating an existing target system"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Target system name")
    type: Optional[TargetType] = Field(None, description="Target system type")
    config: Optional[Dict[str, Any]] = Field(None, description="Target system configuration")
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Target system name cannot be empty')
        return v.strip() if v else v


class TargetSystemResponse(TargetSystemBase):
    """Model for target system API responses"""
    id: str = Field(..., description="Target system unique identifier")
    created_at: datetime = Field(..., description="Target system creation timestamp")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TargetSystemSummary(BaseModel):
    """Lightweight target system model for listings"""
    id: str = Field(..., description="Target system unique identifier")
    name: str = Field(..., description="Target system name")
    type: TargetType = Field(..., description="Target system type")
    created_at: datetime = Field(..., description="Target system creation timestamp")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Specific config models for different target types
class MQTTConfig(BaseModel):
    """MQTT target system configuration"""
    host: str = Field(..., description="MQTT broker host")
    port: int = Field(default=1883, ge=1, le=65535, description="MQTT broker port")
    topic: str = Field(..., description="MQTT topic")
    username: Optional[str] = Field(None, description="MQTT username")
    password: Optional[str] = Field(None, description="MQTT password")
    use_tls: bool = Field(default=False, description="Use TLS encryption")
    qos: int = Field(default=0, ge=0, le=2, description="Quality of Service level")


class HTTPConfig(BaseModel):
    """HTTP target system configuration"""
    url: str = Field(..., description="HTTP endpoint URL")
    method: str = Field(default="POST", description="HTTP method")
    headers: Dict[str, str] = Field(default_factory=dict, description="HTTP headers")
    timeout: int = Field(default=30, ge=1, le=300, description="Request timeout in seconds")
    
    @validator('method')
    def validate_method(cls, v):
        if v.upper() not in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
            raise ValueError('Invalid HTTP method')
        return v.upper()


class KafkaConfig(BaseModel):
    """Kafka target system configuration"""
    bootstrap_servers: str = Field(..., description="Kafka bootstrap servers")
    topic: str = Field(..., description="Kafka topic")
    security_protocol: str = Field(default="PLAINTEXT", description="Security protocol")
    sasl_mechanism: Optional[str] = Field(None, description="SASL mechanism")
    sasl_username: Optional[str] = Field(None, description="SASL username")
    sasl_password: Optional[str] = Field(None, description="SASL password")


class WebSocketConfig(BaseModel):
    """WebSocket target system configuration"""
    url: str = Field(..., description="WebSocket URL")
    headers: Dict[str, str] = Field(default_factory=dict, description="WebSocket headers")
    ping_interval: int = Field(default=20, ge=1, le=300, description="Ping interval in seconds")
    
    @validator('url')
    def validate_url(cls, v):
        if not (v.startswith('ws://') or v.startswith('wss://')):
            raise ValueError('WebSocket URL must start with ws:// or wss://')
        return v


class FTPConfig(BaseModel):
    """FTP target system configuration"""
    host: str = Field(..., description="FTP server host")
    port: int = Field(default=21, ge=1, le=65535, description="FTP server port")
    username: str = Field(..., description="FTP username")
    password: str = Field(..., description="FTP password")
    path: str = Field(default="/", description="FTP path")
    use_sftp: bool = Field(default=False, description="Use SFTP instead of FTP")


class PubSubConfig(BaseModel):
    """Pub/Sub target system configuration"""
    provider: str = Field(..., description="Pub/Sub provider (gcp, aws, azure)")
    topic: str = Field(..., description="Topic name")
    credentials: Dict[str, Any] = Field(..., description="Provider-specific credentials")
    
    @validator('provider')
    def validate_provider(cls, v):
        if v.lower() not in ['gcp', 'aws', 'azure']:
            raise ValueError('Provider must be one of: gcp, aws, azure')
        return v.lower()