"""
Integration tests for Kafka connector with partition and key support
"""
import pytest
from unittest.mock import AsyncMock, patch
from app.simulation.connectors.connector_factory import ConnectorFactory
from app.models.target import TargetType


class TestKafkaIntegration:
    """Integration tests for Kafka connector"""
    
    @pytest.mark.asyncio
    async def test_kafka_connector_with_partition_and_key_integration(self):
        """Test complete integration of Kafka connector with partition and key support"""
        
        # Configuration with partition and key field
        config = {
            'bootstrap_servers': 'localhost:9092',
            'topic': 'iot-data',
            'partition': 1,
            'key_field': 'sensor_id',
            'security_protocol': 'PLAINTEXT'
        }
        
        # Create connector through factory
        connector = ConnectorFactory.create_connector(TargetType.KAFKA, config)
        
        # Mock the Kafka producer
        with patch('app.simulation.connectors.kafka_connector.AIOKafkaProducer') as mock_producer_class:
            mock_producer = AsyncMock()
            mock_producer_class.return_value = mock_producer
            
            # Test connection
            result = await connector.connect()
            assert result is True
            
            # Test sending message with partition and key
            payload = {
                'sensor_id': 'temp-001',
                'temperature': 23.5,
                'humidity': 65.2,
                'timestamp': '2024-01-01T12:00:00Z'
            }
            
            result = await connector.send(payload)
            assert result is True
            
            # Verify the producer was called with correct parameters
            mock_producer.send_and_wait.assert_called_once_with(
                topic='iot-data',
                value=payload,
                key=b'temp-001',  # Key from sensor_id field
                partition=1       # Specified partition
            )
            
            # Test disconnection
            await connector.disconnect()
            mock_producer.stop.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_kafka_connector_with_static_key_integration(self):
        """Test Kafka connector with static key"""
        
        config = {
            'bootstrap_servers': 'localhost:9092',
            'topic': 'iot-data',
            'key_static': 'building-a',
            'security_protocol': 'PLAINTEXT'
        }
        
        connector = ConnectorFactory.create_connector(TargetType.KAFKA, config)
        
        with patch('app.simulation.connectors.kafka_connector.AIOKafkaProducer') as mock_producer_class:
            mock_producer = AsyncMock()
            mock_producer_class.return_value = mock_producer
            
            await connector.connect()
            
            payload = {
                'sensor_id': 'temp-001',
                'temperature': 23.5
            }
            
            result = await connector.send(payload)
            assert result is True
            
            # Verify static key is used
            mock_producer.send_and_wait.assert_called_once_with(
                topic='iot-data',
                value=payload,
                key=b'building-a'  # Static key
            )
    
    @pytest.mark.asyncio
    async def test_kafka_connector_without_partition_or_key(self):
        """Test Kafka connector without partition or key (basic mode)"""
        
        config = {
            'bootstrap_servers': 'localhost:9092',
            'topic': 'iot-data',
            'security_protocol': 'PLAINTEXT'
        }
        
        connector = ConnectorFactory.create_connector(TargetType.KAFKA, config)
        
        with patch('app.simulation.connectors.kafka_connector.AIOKafkaProducer') as mock_producer_class:
            mock_producer = AsyncMock()
            mock_producer_class.return_value = mock_producer
            
            await connector.connect()
            
            payload = {
                'sensor_id': 'temp-001',
                'temperature': 23.5
            }
            
            result = await connector.send(payload)
            assert result is True
            
            # Verify no key or partition is specified
            mock_producer.send_and_wait.assert_called_once_with(
                topic='iot-data',
                value=payload
            )
    
    def test_kafka_config_validation_through_factory(self):
        """Test that factory properly validates Kafka configuration"""
        
        # Valid config
        valid_config = {
            'bootstrap_servers': 'localhost:9092',
            'topic': 'test-topic',
            'partition': 2,
            'key_field': 'device_id'
        }
        
        connector = ConnectorFactory.create_connector(TargetType.KAFKA, valid_config)
        assert connector is not None
        assert connector.config.partition == 2
        assert connector.config.key_field == 'device_id'
        
        # Invalid config - both key options specified
        invalid_config = {
            'bootstrap_servers': 'localhost:9092',
            'topic': 'test-topic',
            'key_field': 'device_id',
            'key_static': 'static-key'
        }
        
        with pytest.raises(ValueError, match="Cannot specify both key_field and key_static"):
            ConnectorFactory.create_connector(TargetType.KAFKA, invalid_config)
        
        # Invalid config - negative partition
        invalid_partition_config = {
            'bootstrap_servers': 'localhost:9092',
            'topic': 'test-topic',
            'partition': -1
        }
        
        with pytest.raises(ValueError):
            ConnectorFactory.create_connector(TargetType.KAFKA, invalid_partition_config)