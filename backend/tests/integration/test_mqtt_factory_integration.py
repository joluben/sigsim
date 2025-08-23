"""
Integration tests for MQTT connector with ConnectorFactory
"""
import pytest
import asyncio
from unittest.mock import Mock, patch
from app.simulation.connectors import ConnectorFactory, get_supported_connector_types
from app.simulation.connectors.mqtt_connector import MQTTConnector
from app.models.target import TargetType


class TestMQTTFactoryIntegration:
    """Integration tests for MQTT connector with factory system"""
    
    def test_mqtt_in_supported_types(self):
        """Test that MQTT is in supported connector types"""
        supported_types = get_supported_connector_types()
        assert "mqtt" in supported_types
        
        factory_types = ConnectorFactory.get_supported_types()
        assert TargetType.MQTT in factory_types
    
    def test_mqtt_factory_creation_minimal_config(self):
        """Test creating MQTT connector with minimal configuration"""
        config = {
            "host": "mqtt.example.com",
            "port": 1883,
            "topic": "iot/sensors"
        }
        
        connector = ConnectorFactory.create_connector(TargetType.MQTT, config)
        
        assert isinstance(connector, MQTTConnector)
        assert connector.config.host == "mqtt.example.com"
        assert connector.config.port == 1883
        assert connector.config.topic == "iot/sensors"
        assert connector.config.qos == 0  # Default value
        assert connector.config.use_tls is False  # Default value
    
    def test_mqtt_factory_creation_full_config(self):
        """Test creating MQTT connector with full configuration"""
        config = {
            "host": "secure-mqtt.example.com",
            "port": 8883,
            "topic": "iot/secure/sensors",
            "username": "iot_user",
            "password": "secure_password",
            "use_tls": True,
            "qos": 2
        }
        
        connector = ConnectorFactory.create_connector(TargetType.MQTT, config)
        
        assert isinstance(connector, MQTTConnector)
        assert connector.config.host == "secure-mqtt.example.com"
        assert connector.config.port == 8883
        assert connector.config.topic == "iot/secure/sensors"
        assert connector.config.username == "iot_user"
        assert connector.config.password == "secure_password"
        assert connector.config.use_tls is True
        assert connector.config.qos == 2
    
    def test_mqtt_config_validation_success(self):
        """Test successful MQTT configuration validation"""
        config = {
            "host": "mqtt.example.com",
            "port": 1883,
            "topic": "iot/sensors",
            "qos": 1
        }
        
        validated = ConnectorFactory.validate_config(TargetType.MQTT, config)
        
        assert validated["host"] == config["host"]
        assert validated["port"] == config["port"]
        assert validated["topic"] == config["topic"]
        assert validated["qos"] == config["qos"]
    
    def test_mqtt_config_validation_missing_host(self):
        """Test MQTT configuration validation with missing host"""
        config = {
            "port": 1883,
            "topic": "iot/sensors"
        }
        
        with pytest.raises(ValueError, match="field required"):
            ConnectorFactory.validate_config(TargetType.MQTT, config)
    
    def test_mqtt_config_validation_missing_topic(self):
        """Test MQTT configuration validation with missing topic"""
        config = {
            "host": "mqtt.example.com",
            "port": 1883
        }
        
        with pytest.raises(ValueError, match="field required"):
            ConnectorFactory.validate_config(TargetType.MQTT, config)
    
    def test_mqtt_config_validation_invalid_port(self):
        """Test MQTT configuration validation with invalid port"""
        config = {
            "host": "mqtt.example.com",
            "port": 70000,  # Invalid port number
            "topic": "iot/sensors"
        }
        
        with pytest.raises(ValueError):
            ConnectorFactory.validate_config(TargetType.MQTT, config)
    
    def test_mqtt_config_validation_invalid_qos(self):
        """Test MQTT configuration validation with invalid QoS"""
        config = {
            "host": "mqtt.example.com",
            "port": 1883,
            "topic": "iot/sensors",
            "qos": 5  # Invalid QoS level (must be 0, 1, or 2)
        }
        
        with pytest.raises(ValueError):
            ConnectorFactory.validate_config(TargetType.MQTT, config)
    
    def test_mqtt_config_schema(self):
        """Test getting MQTT configuration schema"""
        schema = ConnectorFactory.get_config_schema(TargetType.MQTT)
        
        assert isinstance(schema, dict)
        assert "properties" in schema
        
        properties = schema["properties"]
        assert "host" in properties
        assert "port" in properties
        assert "topic" in properties
        assert "username" in properties
        assert "password" in properties
        assert "use_tls" in properties
        assert "qos" in properties
        
        # Check required fields
        if "required" in schema:
            required = schema["required"]
            assert "host" in required
            assert "topic" in required
    
    @patch('paho.mqtt.client.Client')
    async def test_mqtt_factory_connector_functionality(self, mock_client_class):
        """Test that factory-created MQTT connector works correctly"""
        # Setup mock
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock successful publish
        mock_result = Mock()
        mock_result.rc = 0
        mock_result.wait_for_publish = Mock()
        mock_client.publish.return_value = mock_result
        
        config = {
            "host": "mqtt.example.com",
            "port": 1883,
            "topic": "iot/sensors",
            "qos": 1
        }
        
        # Create connector via factory
        connector = ConnectorFactory.create_connector(TargetType.MQTT, config)
        
        # Simulate connection
        async def simulate_connection():
            await asyncio.sleep(0.1)
            connector._on_connect(mock_client, None, None, 0)
        
        asyncio.create_task(simulate_connection())
        
        # Test connection
        connected = await connector.connect()
        assert connected is True
        
        # Test sending
        payload = {"device_id": "test", "value": 42}
        sent = await connector.send(payload)
        assert sent is True
        
        # Verify MQTT client was called correctly
        mock_client.connect_async.assert_called_once_with("mqtt.example.com", 1883, 60)
        mock_client.publish.assert_called_once()
        
        # Test disconnection
        await connector.disconnect()
        mock_client.disconnect.assert_called_once()
    
    def test_mqtt_factory_error_handling(self):
        """Test factory error handling for MQTT connector"""
        # Test with completely invalid config
        with pytest.raises(ValueError):
            ConnectorFactory.create_connector(TargetType.MQTT, {})
        
        # Test with partially invalid config
        with pytest.raises(ValueError):
            ConnectorFactory.create_connector(TargetType.MQTT, {"host": "test"})
    
    def test_mqtt_convenience_function(self):
        """Test MQTT connector creation via convenience function"""
        from app.simulation.connectors import create_connector
        
        config = {
            "host": "mqtt.example.com",
            "port": 1883,
            "topic": "iot/sensors"
        }
        
        connector = create_connector("mqtt", config)
        assert isinstance(connector, MQTTConnector)
    
    def test_mqtt_convenience_function_case_insensitive(self):
        """Test MQTT connector creation with different case"""
        from app.simulation.connectors import create_connector
        
        config = {
            "host": "mqtt.example.com",
            "port": 1883,
            "topic": "iot/sensors"
        }
        
        # Test different cases
        for type_str in ["mqtt", "MQTT", "Mqtt"]:
            connector = create_connector(type_str, config)
            assert isinstance(connector, MQTTConnector)


class TestMQTTConfigurationVariations:
    """Test various MQTT configuration scenarios"""
    
    def test_mqtt_default_values(self):
        """Test MQTT connector with default values"""
        config = {
            "host": "mqtt.example.com",
            "topic": "iot/sensors"
        }
        
        connector = ConnectorFactory.create_connector(TargetType.MQTT, config)
        
        # Check default values
        assert connector.config.port == 1883  # Default MQTT port
        assert connector.config.qos == 0      # Default QoS
        assert connector.config.use_tls is False  # Default TLS setting
        assert connector.config.username is None  # Default auth
        assert connector.config.password is None  # Default auth
    
    def test_mqtt_tls_configuration(self):
        """Test MQTT connector with TLS configuration"""
        config = {
            "host": "secure-mqtt.example.com",
            "port": 8883,
            "topic": "iot/secure/sensors",
            "use_tls": True
        }
        
        connector = ConnectorFactory.create_connector(TargetType.MQTT, config)
        
        assert connector.config.use_tls is True
        assert connector.config.port == 8883  # Common TLS port
    
    def test_mqtt_authentication_configuration(self):
        """Test MQTT connector with authentication"""
        config = {
            "host": "auth-mqtt.example.com",
            "port": 1883,
            "topic": "iot/auth/sensors",
            "username": "device_user",
            "password": "device_password"
        }
        
        connector = ConnectorFactory.create_connector(TargetType.MQTT, config)
        
        assert connector.config.username == "device_user"
        assert connector.config.password == "device_password"
    
    def test_mqtt_qos_levels(self):
        """Test MQTT connector with different QoS levels"""
        base_config = {
            "host": "mqtt.example.com",
            "port": 1883,
            "topic": "iot/sensors"
        }
        
        for qos in [0, 1, 2]:
            config = {**base_config, "qos": qos}
            connector = ConnectorFactory.create_connector(TargetType.MQTT, config)
            assert connector.config.qos == qos
    
    def test_mqtt_topic_variations(self):
        """Test MQTT connector with different topic formats"""
        base_config = {
            "host": "mqtt.example.com",
            "port": 1883
        }
        
        topics = [
            "simple",
            "iot/sensors",
            "devices/sensor-001/data",
            "home/livingroom/temperature",
            "factory/line1/machine2/status"
        ]
        
        for topic in topics:
            config = {**base_config, "topic": topic}
            connector = ConnectorFactory.create_connector(TargetType.MQTT, config)
            assert connector.config.topic == topic


@pytest.fixture
def mqtt_configs():
    """Various MQTT configurations for testing"""
    return {
        "basic": {
            "host": "mqtt.example.com",
            "port": 1883,
            "topic": "iot/sensors"
        },
        "with_auth": {
            "host": "mqtt.example.com",
            "port": 1883,
            "topic": "iot/sensors",
            "username": "user",
            "password": "pass"
        },
        "with_tls": {
            "host": "secure-mqtt.example.com",
            "port": 8883,
            "topic": "iot/secure/sensors",
            "use_tls": True
        },
        "full_config": {
            "host": "full-mqtt.example.com",
            "port": 8883,
            "topic": "iot/full/sensors",
            "username": "full_user",
            "password": "full_pass",
            "use_tls": True,
            "qos": 2
        }
    }


class TestMQTTFactoryWithVariousConfigs:
    """Test MQTT factory with various configuration scenarios"""
    
    def test_all_config_variations(self, mqtt_configs):
        """Test factory with all configuration variations"""
        for config_name, config in mqtt_configs.items():
            connector = ConnectorFactory.create_connector(TargetType.MQTT, config)
            
            assert isinstance(connector, MQTTConnector)
            assert connector.config.host == config["host"]
            assert connector.config.port == config["port"]
            assert connector.config.topic == config["topic"]
            
            # Check optional fields
            if "username" in config:
                assert connector.config.username == config["username"]
            if "password" in config:
                assert connector.config.password == config["password"]
            if "use_tls" in config:
                assert connector.config.use_tls == config["use_tls"]
            if "qos" in config:
                assert connector.config.qos == config["qos"]
    
    def test_config_validation_for_all_variations(self, mqtt_configs):
        """Test configuration validation for all variations"""
        for config_name, config in mqtt_configs.items():
            # Should not raise exception
            validated = ConnectorFactory.validate_config(TargetType.MQTT, config)
            
            assert isinstance(validated, dict)
            assert "host" in validated
            assert "port" in validated
            assert "topic" in validated