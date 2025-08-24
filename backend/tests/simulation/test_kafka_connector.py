"""
Tests for Kafka connector
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.simulation.connectors.kafka_connector import KafkaConnector
from app.models.target import KafkaConfig


@pytest.fixture
def basic_kafka_config():
    """Basic Kafka configuration for testing"""
    return KafkaConfig(
        bootstrap_servers="localhost:9092",
        topic="test-topic"
    )


@pytest.fixture
def kafka_config_with_partition():
    """Kafka configuration with specific partition"""
    return KafkaConfig(
        bootstrap_servers="localhost:9092",
        topic="test-topic",
        partition=2
    )


@pytest.fixture
def kafka_config_with_key_field():
    """Kafka configuration with key field"""
    return KafkaConfig(
        bootstrap_servers="localhost:9092",
        topic="test-topic",
        key_field="device_id"
    )


@pytest.fixture
def kafka_config_with_static_key():
    """Kafka configuration with static key"""
    return KafkaConfig(
        bootstrap_servers="localhost:9092",
        topic="test-topic",
        key_static="static-key"
    )


class TestKafkaConnector:
    """Test cases for KafkaConnector"""
    
    @pytest.mark.asyncio
    async def test_connect_success(self, basic_kafka_config):
        """Test successful connection to Kafka"""
        connector = KafkaConnector(basic_kafka_config)
        
        with patch('app.simulation.connectors.kafka_connector.AIOKafkaProducer') as mock_producer_class:
            mock_producer = AsyncMock()
            mock_producer_class.return_value = mock_producer
            
            result = await connector.connect()
            
            assert result is True
            assert connector.producer == mock_producer
            mock_producer.start.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_connect_failure(self, basic_kafka_config):
        """Test connection failure"""
        connector = KafkaConnector(basic_kafka_config)
        
        with patch('app.simulation.connectors.kafka_connector.AIOKafkaProducer') as mock_producer_class:
            mock_producer = AsyncMock()
            mock_producer.start.side_effect = Exception("Connection failed")
            mock_producer_class.return_value = mock_producer
            
            result = await connector.connect()
            
            assert result is False
            assert connector.producer is None
    
    @pytest.mark.asyncio
    async def test_send_basic_message(self, basic_kafka_config):
        """Test sending basic message without partition or key"""
        connector = KafkaConnector(basic_kafka_config)
        mock_producer = AsyncMock()
        connector.producer = mock_producer
        
        payload = {"temperature": 25.5, "humidity": 60}
        
        result = await connector.send(payload)
        
        assert result is True
        mock_producer.send_and_wait.assert_called_once_with(
            topic="test-topic",
            value=payload
        )
    
    @pytest.mark.asyncio
    async def test_send_with_partition(self, kafka_config_with_partition):
        """Test sending message to specific partition"""
        connector = KafkaConnector(kafka_config_with_partition)
        mock_producer = AsyncMock()
        connector.producer = mock_producer
        
        payload = {"temperature": 25.5, "humidity": 60}
        
        result = await connector.send(payload)
        
        assert result is True
        mock_producer.send_and_wait.assert_called_once_with(
            topic="test-topic",
            value=payload,
            partition=2
        )
    
    @pytest.mark.asyncio
    async def test_send_with_static_key(self, kafka_config_with_static_key):
        """Test sending message with static key"""
        connector = KafkaConnector(kafka_config_with_static_key)
        mock_producer = AsyncMock()
        connector.producer = mock_producer
        
        payload = {"temperature": 25.5, "humidity": 60}
        
        result = await connector.send(payload)
        
        assert result is True
        mock_producer.send_and_wait.assert_called_once_with(
            topic="test-topic",
            value=payload,
            key=b"static-key"
        )
    
    @pytest.mark.asyncio
    async def test_send_with_key_field(self, kafka_config_with_key_field):
        """Test sending message with key from payload field"""
        connector = KafkaConnector(kafka_config_with_key_field)
        mock_producer = AsyncMock()
        connector.producer = mock_producer
        
        payload = {"device_id": "sensor-001", "temperature": 25.5, "humidity": 60}
        
        result = await connector.send(payload)
        
        assert result is True
        mock_producer.send_and_wait.assert_called_once_with(
            topic="test-topic",
            value=payload,
            key=b"sensor-001"
        )
    
    @pytest.mark.asyncio
    async def test_send_with_missing_key_field(self, kafka_config_with_key_field):
        """Test sending message when key field is missing from payload"""
        connector = KafkaConnector(kafka_config_with_key_field)
        mock_producer = AsyncMock()
        connector.producer = mock_producer
        
        payload = {"temperature": 25.5, "humidity": 60}  # Missing device_id
        
        result = await connector.send(payload)
        
        assert result is True
        # Should send without key when field is missing
        mock_producer.send_and_wait.assert_called_once_with(
            topic="test-topic",
            value=payload
        )
    
    @pytest.mark.asyncio
    async def test_send_with_numeric_key_field(self, kafka_config_with_key_field):
        """Test sending message with numeric key from payload field"""
        connector = KafkaConnector(kafka_config_with_key_field)
        mock_producer = AsyncMock()
        connector.producer = mock_producer
        
        payload = {"device_id": 12345, "temperature": 25.5, "humidity": 60}
        
        result = await connector.send(payload)
        
        assert result is True
        mock_producer.send_and_wait.assert_called_once_with(
            topic="test-topic",
            value=payload,
            key=b"12345"
        )
    
    @pytest.mark.asyncio
    async def test_send_failure(self, basic_kafka_config):
        """Test send failure"""
        connector = KafkaConnector(basic_kafka_config)
        mock_producer = AsyncMock()
        mock_producer.send_and_wait.side_effect = Exception("Send failed")
        connector.producer = mock_producer
        
        payload = {"temperature": 25.5}
        
        result = await connector.send(payload)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_send_without_connection(self, basic_kafka_config):
        """Test send without established connection"""
        connector = KafkaConnector(basic_kafka_config)
        # No producer set
        
        payload = {"temperature": 25.5}
        
        result = await connector.send(payload)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_disconnect(self, basic_kafka_config):
        """Test disconnection"""
        connector = KafkaConnector(basic_kafka_config)
        mock_producer = AsyncMock()
        connector.producer = mock_producer
        
        await connector.disconnect()
        
        mock_producer.stop.assert_called_once()
        assert connector.producer is None
    
    @pytest.mark.asyncio
    async def test_disconnect_without_connection(self, basic_kafka_config):
        """Test disconnection without established connection"""
        connector = KafkaConnector(basic_kafka_config)
        # No producer set
        
        # Should not raise exception
        await connector.disconnect()
        
        assert connector.producer is None


class TestKafkaConfigValidation:
    """Test cases for KafkaConfig validation"""
    
    def test_valid_basic_config(self):
        """Test valid basic configuration"""
        config = KafkaConfig(
            bootstrap_servers="localhost:9092",
            topic="test-topic"
        )
        assert config.bootstrap_servers == "localhost:9092"
        assert config.topic == "test-topic"
        assert config.partition is None
        assert config.key_field is None
        assert config.key_static is None
    
    def test_valid_config_with_partition(self):
        """Test valid configuration with partition"""
        config = KafkaConfig(
            bootstrap_servers="localhost:9092",
            topic="test-topic",
            partition=5
        )
        assert config.partition == 5
    
    def test_invalid_negative_partition(self):
        """Test invalid negative partition"""
        with pytest.raises(ValueError):
            KafkaConfig(
                bootstrap_servers="localhost:9092",
                topic="test-topic",
                partition=-1
            )
    
    def test_valid_config_with_key_field(self):
        """Test valid configuration with key field"""
        config = KafkaConfig(
            bootstrap_servers="localhost:9092",
            topic="test-topic",
            key_field="device_id"
        )
        assert config.key_field == "device_id"
        assert config.key_static is None
    
    def test_valid_config_with_static_key(self):
        """Test valid configuration with static key"""
        config = KafkaConfig(
            bootstrap_servers="localhost:9092",
            topic="test-topic",
            key_static="my-key"
        )
        assert config.key_static == "my-key"
        assert config.key_field is None
    
    def test_invalid_both_key_options(self):
        """Test invalid configuration with both key options"""
        with pytest.raises(ValueError, match="Cannot specify both key_field and key_static"):
            KafkaConfig(
                bootstrap_servers="localhost:9092",
                topic="test-topic",
                key_field="device_id",
                key_static="my-key"
            )