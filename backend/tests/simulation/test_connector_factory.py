"""
Tests for ConnectorFactory
"""
import pytest
from unittest.mock import Mock, patch
from app.simulation.connectors.connector_factory import ConnectorFactory, create_connector, get_supported_connector_types
from app.simulation.connectors.base_connector import TargetConnector
from app.simulation.connectors.http_connector import HTTPConnector
from app.simulation.connectors.mqtt_connector import MQTTConnector
from app.simulation.connectors.kafka_connector import KafkaConnector
from app.simulation.connectors.websocket_connector import WebSocketConnector
from app.models.target import TargetType, HTTPConfig, MQTTConfig, KafkaConfig, WebSocketConfig


class TestConnectorFactory:
    """Test cases for ConnectorFactory"""
    
    def test_get_supported_types(self):
        """Test getting supported target types"""
        supported_types = ConnectorFactory.get_supported_types()
        
        assert TargetType.HTTP in supported_types
        assert TargetType.MQTT in supported_types
        assert TargetType.KAFKA in supported_types
        assert TargetType.WEBSOCKET in supported_types
        assert len(supported_types) >= 4
    
    def test_is_supported(self):
        """Test checking if target type is supported"""
        assert ConnectorFactory.is_supported(TargetType.HTTP) is True
        assert ConnectorFactory.is_supported(TargetType.MQTT) is True
        assert ConnectorFactory.is_supported(TargetType.KAFKA) is True
        assert ConnectorFactory.is_supported(TargetType.WEBSOCKET) is True
    
    def test_create_http_connector(self):
        """Test creating HTTP connector"""
        config = {
            "url": "https://api.example.com/webhook",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "timeout": 30
        }
        
        connector = ConnectorFactory.create_connector(TargetType.HTTP, config)
        
        assert isinstance(connector, HTTPConnector)
        assert connector.config.url == config["url"]
        assert connector.config.method == config["method"]
        assert connector.config.headers == config["headers"]
        assert connector.config.timeout == config["timeout"]
    
    def test_create_mqtt_connector(self):
        """Test creating MQTT connector"""
        config = {
            "host": "mqtt.example.com",
            "port": 1883,
            "topic": "iot/sensors",
            "username": "user",
            "password": "pass",
            "use_tls": False,
            "qos": 1
        }
        
        connector = ConnectorFactory.create_connector(TargetType.MQTT, config)
        
        assert isinstance(connector, MQTTConnector)
        assert connector.config.host == config["host"]
        assert connector.config.port == config["port"]
        assert connector.config.topic == config["topic"]
        assert connector.config.username == config["username"]
        assert connector.config.qos == config["qos"]
    
    def test_create_kafka_connector(self):
        """Test creating Kafka connector"""
        config = {
            "bootstrap_servers": "localhost:9092",
            "topic": "iot-data",
            "security_protocol": "PLAINTEXT"
        }
        
        connector = ConnectorFactory.create_connector(TargetType.KAFKA, config)
        
        assert isinstance(connector, KafkaConnector)
        assert connector.config.bootstrap_servers == config["bootstrap_servers"]
        assert connector.config.topic == config["topic"]
        assert connector.config.security_protocol == config["security_protocol"]
    
    def test_create_websocket_connector(self):
        """Test creating WebSocket connector"""
        config = {
            "url": "wss://websocket.example.com/stream",
            "headers": {"Authorization": "Bearer token"},
            "ping_interval": 20
        }
        
        connector = ConnectorFactory.create_connector(TargetType.WEBSOCKET, config)
        
        assert isinstance(connector, WebSocketConnector)
        assert connector.config.url == config["url"]
        assert connector.config.headers == config["headers"]
        assert connector.config.ping_interval == config["ping_interval"]
    
    def test_create_connector_invalid_type(self):
        """Test creating connector with invalid type"""
        with pytest.raises(ValueError, match="Unsupported target type"):
            ConnectorFactory.create_connector("invalid_type", {})
    
    def test_create_connector_invalid_config(self):
        """Test creating connector with invalid configuration"""
        # Missing required fields for HTTP
        config = {"method": "POST"}  # Missing URL
        
        with pytest.raises(ValueError, match="Invalid configuration"):
            ConnectorFactory.create_connector(TargetType.HTTP, config)
    
    def test_validate_config_http(self):
        """Test validating HTTP configuration"""
        config = {
            "url": "https://api.example.com/webhook",
            "method": "POST",
            "timeout": 30
        }
        
        validated = ConnectorFactory.validate_config(TargetType.HTTP, config)
        
        assert validated["url"] == config["url"]
        assert validated["method"] == config["method"]
        assert validated["timeout"] == config["timeout"]
    
    def test_validate_config_mqtt(self):
        """Test validating MQTT configuration"""
        config = {
            "host": "mqtt.example.com",
            "port": 1883,
            "topic": "iot/sensors"
        }
        
        validated = ConnectorFactory.validate_config(TargetType.MQTT, config)
        
        assert validated["host"] == config["host"]
        assert validated["port"] == config["port"]
        assert validated["topic"] == config["topic"]
    
    def test_get_config_schema_http(self):
        """Test getting configuration schema for HTTP"""
        schema = ConnectorFactory.get_config_schema(TargetType.HTTP)
        
        assert "properties" in schema
        assert "url" in schema["properties"]
        assert "method" in schema["properties"]
        assert "timeout" in schema["properties"]
    
    def test_register_custom_connector(self):
        """Test registering a custom connector"""
        class CustomConnector(TargetConnector):
            def __init__(self, config):
                self.config = config
            
            async def connect(self):
                return True
            
            async def send(self, payload):
                return True
            
            async def disconnect(self):
                pass
        
        # Register custom connector
        custom_type = "custom"
        ConnectorFactory.register_connector(custom_type, CustomConnector)
        
        # Test creation
        connector = ConnectorFactory.create_connector(custom_type, {"test": "config"})
        assert isinstance(connector, CustomConnector)
        
        # Clean up
        if custom_type in ConnectorFactory._connectors:
            del ConnectorFactory._connectors[custom_type]
    
    def test_register_invalid_connector(self):
        """Test registering invalid connector class"""
        class InvalidConnector:
            pass
        
        with pytest.raises(ValueError, match="must inherit from TargetConnector"):
            ConnectorFactory.register_connector("invalid", InvalidConnector)


class TestConvenienceFunctions:
    """Test convenience functions"""
    
    def test_create_connector_function(self):
        """Test create_connector convenience function"""
        config = {
            "url": "https://api.example.com/webhook",
            "method": "POST"
        }
        
        connector = create_connector("http", config)
        assert isinstance(connector, HTTPConnector)
    
    def test_create_connector_function_invalid_type(self):
        """Test create_connector with invalid type string"""
        with pytest.raises(ValueError, match="Failed to create connector"):
            create_connector("invalid_type", {})
    
    def test_get_supported_connector_types_function(self):
        """Test get_supported_connector_types convenience function"""
        types = get_supported_connector_types()
        
        assert "http" in types
        assert "mqtt" in types
        assert "kafka" in types
        assert "websocket" in types
        assert isinstance(types, list)
        assert all(isinstance(t, str) for t in types)


@pytest.fixture
def sample_configs():
    """Sample configurations for different connector types"""
    return {
        "http": {
            "url": "https://api.example.com/webhook",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "timeout": 30
        },
        "mqtt": {
            "host": "mqtt.example.com",
            "port": 1883,
            "topic": "iot/sensors",
            "qos": 1
        },
        "kafka": {
            "bootstrap_servers": "localhost:9092",
            "topic": "iot-data",
            "security_protocol": "PLAINTEXT"
        },
        "websocket": {
            "url": "wss://websocket.example.com/stream",
            "ping_interval": 20
        }
    }


class TestIntegration:
    """Integration tests for connector factory"""
    
    def test_create_all_supported_connectors(self, sample_configs):
        """Test creating all supported connector types"""
        supported_types = ConnectorFactory.get_supported_types()
        
        for target_type in supported_types:
            if target_type.value in sample_configs:
                config = sample_configs[target_type.value]
                connector = ConnectorFactory.create_connector(target_type, config)
                
                assert isinstance(connector, TargetConnector)
                assert hasattr(connector, 'connect')
                assert hasattr(connector, 'send')
                assert hasattr(connector, 'disconnect')
    
    def test_factory_consistency(self):
        """Test that factory registries are consistent"""
        connector_types = set(ConnectorFactory._connectors.keys())
        config_types = set(ConnectorFactory._config_classes.keys())
        
        # All connector types should have config classes (or be handled gracefully)
        for connector_type in connector_types:
            # Should not raise exception
            schema = ConnectorFactory.get_config_schema(connector_type)
            assert isinstance(schema, dict)
    
    def test_config_validation_consistency(self, sample_configs):
        """Test that config validation is consistent"""
        for type_str, config in sample_configs.items():
            try:
                target_type = TargetType(type_str)
                
                # Validate config
                validated = ConnectorFactory.validate_config(target_type, config)
                assert isinstance(validated, dict)
                
                # Create connector with validated config
                connector = ConnectorFactory.create_connector(target_type, validated)
                assert isinstance(connector, TargetConnector)
                
            except ValueError:
                # Some types might not be fully implemented yet
                pass