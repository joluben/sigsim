"""
Custom validation utilities
"""
import re
from typing import Any, Dict
from urllib.parse import urlparse


def validate_url(url: str) -> bool:
    """Validate URL format"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def validate_mqtt_config(config: Dict[str, Any]) -> bool:
    """Validate MQTT configuration"""
    required_fields = ['host', 'port', 'topic']
    
    for field in required_fields:
        if field not in config:
            return False
    
    # Validate port range
    port = config.get('port')
    if not isinstance(port, int) or port < 1 or port > 65535:
        return False
    
    # Validate topic format (basic validation)
    topic = config.get('topic')
    if not isinstance(topic, str) or not topic.strip():
        return False
    
    return True


def validate_http_config(config: Dict[str, Any]) -> bool:
    """Validate HTTP configuration"""
    url = config.get('url')
    if not url or not validate_url(url):
        return False
    
    method = config.get('method', 'POST').upper()
    if method not in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
        return False
    
    return True


def validate_kafka_config(config: Dict[str, Any]) -> bool:
    """Validate Kafka configuration"""
    required_fields = ['bootstrap_servers', 'topic']
    
    for field in required_fields:
        if field not in config:
            return False
    
    # Basic validation for bootstrap servers format
    servers = config.get('bootstrap_servers')
    if not isinstance(servers, str) or not servers.strip():
        return False
    
    return True


def validate_websocket_config(config: Dict[str, Any]) -> bool:
    """Validate WebSocket configuration"""
    url = config.get('url')
    if not url:
        return False
    
    # Check if URL starts with ws:// or wss://
    if not (url.startswith('ws://') or url.startswith('wss://')):
        return False
    
    return True


def validate_target_config(target_type: str, config: Dict[str, Any]) -> bool:
    """Validate target system configuration based on type"""
    validators = {
        'mqtt': validate_mqtt_config,
        'http': validate_http_config,
        'kafka': validate_kafka_config,
        'websocket': validate_websocket_config,
    }
    
    validator = validators.get(target_type)
    if not validator:
        return False
    
    return validator(config)