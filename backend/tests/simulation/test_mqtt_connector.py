"""
Tests for MQTT Connector
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from app.simulation.connectors.mqtt_connector import MQTTConnector
from app.simulation.connectors.connector_factory import ConnectorFactory
from app.models.target import MQTTConfig, TargetType


class TestMQTTConnector:
    """Test cases for MQTT Connector"""
    
    def test_mqtt_connector_initialization(self):
        """Test MQTT connector initialization"""
        config = MQTTConfig(
            host="mqtt.example.com",
            port=1883,
            topic="iot/sensors",
            username="user",
            password="pass",
            use_tls=False,
            qos=1
        )
        
        connector = MQTTConnector(config)
        
        assert connector.config == config
        assert connector.client is None
        assert connector.connected is False
        assert connector.connection_event is not None
    
    @patch('paho.mqtt.client.Client')
    async def test_mqtt_connect_success(self, mock_client_class):
        """Test successful MQTT connection"""
        # Setup mock
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        config = MQTTConfig(
            host="mqtt.example.com",
            port=1883,
            topic="iot/sensors",
            qos=1
        )
        
        connector = MQTTConnector(config)
        
        # Simulate successful connection
        async def simulate_connection():
            await asyncio.sleep(0.1)
            connector._on_connect(mock_client, None, None, 0)
        
        # Start connection simulation
        asyncio.create_task(simulate_connection())
        
        # Test connection
        result = await connector.connect()
        
        assert result is True
        assert connector.connected is True
        assert mock_client.connect_async.called
        assert mock_client.loop_start.called
    
    @patch('paho.mqtt.client.Client')
    async def test_mqtt_connect_with_credentials(self, mock_client_class):
        """Test MQTT connection with credentials"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        config = MQTTConfig(
            host="mqtt.example.com",
            port=1883,
            topic="iot/sensors",
            username="testuser",
            password="testpass",
            qos=1
        )
        
        connector = MQTTConnector(config)
        
        # Simulate successful connection
        async def simulate_connection():
            await asyncio.sleep(0.1)
            connector._on_connect(mock_client, None, None, 0)
        
        asyncio.create_task(simulate_connection())
        
        result = await connector.connect()
        
        assert result is True
        mock_client.username_pw_set.assert_called_once_with("testuser", "testpass")
    
    @patch('paho.mqtt.client.Client')
    async def test_mqtt_connect_with_tls(self, mock_client_class):
        """Test MQTT connection with TLS"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        config = MQTTConfig(
            host="mqtt.example.com",
            port=8883,
            topic="iot/sensors",
            use_tls=True,
            qos=1
        )
        
        connector = MQTTConnector(config)
        
        # Simulate successful connection
        async def simulate_connection():
            await asyncio.sleep(0.1)
            connector._on_connect(mock_client, None, None, 0)
        
        asyncio.create_task(simulate_connection())
        
        result = await connector.connect()
        
        assert result is True
        mock_client.tls_set.assert_called_once()
    
    @patch('paho.mqtt.client.Client')
    async def test_mqtt_connect_failure(self, mock_client_class):
        """Test MQTT connection failure"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        config = MQTTConfig(
            host="invalid.mqtt.broker",
            port=1883,
            topic="iot/sensors",
            qos=1
        )
        
        connector = MQTTConnector(config)
        
        # Simulate connection failure
        async def simulate_failure():
            await asyncio.sleep(0.1)
            connector._on_connect(mock_client, None, None, 1)  # Connection refused
        
        asyncio.create_task(simulate_failure())
        
        result = await connector.connect()
        
        assert result is False
        assert connector.connected is False
    
    @patch('paho.mqtt.client.Client')
    async def test_mqtt_send_success(self, mock_client_class):
        """Test successful MQTT message sending"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock publish result
        mock_result = Mock()
        mock_result.rc = 0  # MQTT_ERR_SUCCESS
        mock_result.wait_for_publish = Mock()
        mock_client.publish.return_value = mock_result
        
        config = MQTTConfig(
            host="mqtt.example.com",
            port=1883,
            topic="iot/sensors",
            qos=1
        )
        
        connector = MQTTConnector(config)
        connector.connected = True  # Simulate connected state
        connector.client = mock_client
        
        payload = {
            "device_id": "sensor-001",
            "temperature": 23.5,
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
        result = await connector.send(payload)
        
        assert result is True
        mock_client.publish.assert_called_once_with(
            "iot/sensors",
            '{"device_id": "sensor-001", "temperature": 23.5, "timestamp": "2024-01-01T12:00:00Z"}',
            qos=1
        )
        mock_result.wait_for_publish.assert_called_once_with(timeout=5)
    
    @patch('paho.mqtt.client.Client')
    async def test_mqtt_send_not_connected(self, mock_client_class):
        """Test MQTT send when not connected"""
        config = MQTTConfig(
            host="mqtt.example.com",
            port=1883,
            topic="iot/sensors",
            qos=1
        )
        
        connector = MQTTConnector(config)
        # Don't set connected = True
        
        payload = {"test": "data"}
        result = await connector.send(payload)
        
        assert result is False
    
    @patch('paho.mqtt.client.Client')
    async def test_mqtt_send_failure(self, mock_client_class):
        """Test MQTT send failure"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock publish failure
        mock_result = Mock()
        mock_result.rc = 1  # Error code
        mock_result.wait_for_publish = Mock()
        mock_client.publish.return_value = mock_result
        
        config = MQTTConfig(
            host="mqtt.example.com",
            port=1883,
            topic="iot/sensors",
            qos=1
        )
        
        connector = MQTTConnector(config)
        connector.connected = True
        connector.client = mock_client
        
        payload = {"test": "data"}
        result = await connector.send(payload)
        
        assert result is False
    
    @patch('paho.mqtt.client.Client')
    async def test_mqtt_disconnect(self, mock_client_class):
        """Test MQTT disconnection"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        config = MQTTConfig(
            host="mqtt.example.com",
            port=1883,
            topic="iot/sensors",
            qos=1
        )
        
        connector = MQTTConnector(config)
        connector.client = mock_client
        connector.connected = True
        
        await connector.disconnect()
        
        mock_client.loop_stop.assert_called_once()
        mock_client.disconnect.assert_called_once()
        assert connector.connected is False
    
    def test_mqtt_on_connect_callback_success(self):
        """Test MQTT on_connect callback for success"""
        config = MQTTConfig(
            host="mqtt.example.com",
            port=1883,
            topic="iot/sensors",
            qos=1
        )
        
        connector = MQTTConnector(config)
        
        # Test successful connection callback
        connector._on_connect(None, None, None, 0)
        
        assert connector.connected is True
        assert connector.connection_event.is_set()
    
    def test_mqtt_on_connect_callback_failure(self):
        """Test MQTT on_connect callback for failure"""
        config = MQTTConfig(
            host="mqtt.example.com",
            port=1883,
            topic="iot/sensors",
            qos=1
        )
        
        connector = MQTTConnector(config)
        
        # Test failed connection callback
        connector._on_connect(None, None, None, 1)  # Connection refused
        
        assert connector.connected is False
        assert connector.connection_event.is_set()
    
    def test_mqtt_on_disconnect_callback(self):
        """Test MQTT on_disconnect callback"""
        config = MQTTConfig(
            host="mqtt.example.com",
            port=1883,
            topic="iot/sensors",
            qos=1
        )
        
        connector = MQTTConnector(config)
        connector.connected = True
        
        # Test disconnect callback
        connector._on_disconnect(None, None, None)
        
        assert connector.connected is False


class TestMQTTConnectorFactoryIntegration:
    """Test MQTT connector integration with factory"""
    
    def test_mqtt_connector_creation_via_factory(self):
        """Test creating MQTT connector via factory"""
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
        assert connector.config.password == config["password"]
        assert connector.config.use_tls == config["use_tls"]
        assert connector.config.qos == config["qos"]
    
    def test_mqtt_connector_config_validation(self):
        """Test MQTT config validation via factory"""
        # Valid config
        valid_config = {
            "host": "mqtt.example.com",
            "port": 1883,
            "topic": "iot/sensors"
        }
        
        validated = ConnectorFactory.validate_config(TargetType.MQTT, valid_config)
        assert validated["host"] == valid_config["host"]
        assert validated["port"] == valid_config["port"]
        assert validated["topic"] == valid_config["topic"]
        
        # Invalid config - missing required fields
        invalid_config = {
            "host": "mqtt.example.com"
            # Missing port and topic
        }
        
        with pytest.raises(ValueError):
            ConnectorFactory.validate_config(TargetType.MQTT, invalid_config)
    
    def test_mqtt_connector_schema(self):
        """Test getting MQTT connector schema"""
        schema = ConnectorFactory.get_config_schema(TargetType.MQTT)
        
        assert "properties" in schema
        assert "host" in schema["properties"]
        assert "port" in schema["properties"]
        assert "topic" in schema["properties"]
        assert "username" in schema["properties"]
        assert "password" in schema["properties"]
        assert "use_tls" in schema["properties"]
        assert "qos" in schema["properties"]
    
    def test_mqtt_connector_is_supported(self):
        """Test that MQTT connector is supported by factory"""
        assert ConnectorFactory.is_supported(TargetType.MQTT) is True
        assert TargetType.MQTT in ConnectorFactory.get_supported_types()


@pytest.fixture
def mqtt_config():
    """Sample MQTT configuration for tests"""
    return MQTTConfig(
        host="mqtt.example.com",
        port=1883,
        topic="iot/sensors",
        username="testuser",
        password="testpass",
        use_tls=False,
        qos=1
    )


@pytest.fixture
def mqtt_config_tls():
    """Sample MQTT configuration with TLS for tests"""
    return MQTTConfig(
        host="mqtt.example.com",
        port=8883,
        topic="iot/sensors",
        use_tls=True,
        qos=2
    )


class TestMQTTConnectorIntegration:
    """Integration tests for MQTT connector"""
    
    def test_mqtt_connector_with_different_qos_levels(self, mqtt_config):
        """Test MQTT connector with different QoS levels"""
        for qos in [0, 1, 2]:
            mqtt_config.qos = qos
            connector = MQTTConnector(mqtt_config)
            assert connector.config.qos == qos
    
    def test_mqtt_connector_with_different_ports(self, mqtt_config):
        """Test MQTT connector with different ports"""
        for port in [1883, 8883, 9001]:
            mqtt_config.port = port
            connector = MQTTConnector(mqtt_config)
            assert connector.config.port == port
    
    def test_mqtt_connector_topic_validation(self, mqtt_config):
        """Test MQTT connector with different topic formats"""
        valid_topics = [
            "iot/sensors",
            "devices/sensor-001/data",
            "home/livingroom/temperature",
            "factory/line1/machine2/status"
        ]
        
        for topic in valid_topics:
            mqtt_config.topic = topic
            connector = MQTTConnector(mqtt_config)
            assert connector.config.topic == topic
    
    @patch('paho.mqtt.client.Client')
    async def test_mqtt_connector_error_handling(self, mock_client_class, mqtt_config):
        """Test MQTT connector error handling"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Test connection timeout
        connector = MQTTConnector(mqtt_config)
        
        # Don't trigger the connection event (simulate timeout)
        result = await connector.connect()
        
        # Should return False due to timeout
        assert result is False
        assert connector.connected is False