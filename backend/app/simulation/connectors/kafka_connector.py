"""
Kafka target connector
"""
import json
from typing import Dict, Any
from aiokafka import AIOKafkaProducer
from app.simulation.connectors.base_connector import TargetConnector
from app.models.target import KafkaConfig


class KafkaConnector(TargetConnector):
    """Connector for Apache Kafka"""
    
    def __init__(self, config: KafkaConfig):
        self.config = config
        self.producer: AIOKafkaProducer = None
    
    async def connect(self) -> bool:
        """Connect to Kafka cluster"""
        try:
            # Configure producer
            producer_config = {
                'bootstrap_servers': self.config.bootstrap_servers,
                'value_serializer': lambda v: json.dumps(v).encode('utf-8')
            }
            
            # Add security configuration if needed
            if self.config.security_protocol != "PLAINTEXT":
                producer_config['security_protocol'] = self.config.security_protocol
                
                if self.config.sasl_mechanism:
                    producer_config['sasl_mechanism'] = self.config.sasl_mechanism
                    producer_config['sasl_plain_username'] = self.config.sasl_username
                    producer_config['sasl_plain_password'] = self.config.sasl_password
            
            self.producer = AIOKafkaProducer(**producer_config)
            await self.producer.start()
            return True
            
        except Exception as e:
            print(f"Kafka connection failed: {e}")
            self.producer = None
            return False
    
    async def send(self, payload: Dict[str, Any]) -> bool:
        """Send message to Kafka topic with partition and key support"""
        if not self.producer:
            return False
        
        try:
            # Determine message key
            message_key = self._get_message_key(payload)
            
            # Prepare send arguments
            send_args = {
                'topic': self.config.topic,
                'value': payload
            }
            
            # Add key if specified
            if message_key is not None:
                send_args['key'] = message_key.encode('utf-8') if isinstance(message_key, str) else str(message_key).encode('utf-8')
            
            # Add partition if specified
            if self.config.partition is not None:
                send_args['partition'] = self.config.partition
            
            await self.producer.send_and_wait(**send_args)
            return True
            
        except Exception as e:
            print(f"Kafka send failed: {e}")
            return False
    
    def _get_message_key(self, payload: Dict[str, Any]) -> str:
        """Extract or generate message key from payload"""
        # Use static key if configured
        if self.config.key_static:
            return self.config.key_static
        
        # Use field from payload as key
        if self.config.key_field:
            key_value = payload.get(self.config.key_field)
            if key_value is not None:
                return str(key_value)
            else:
                print(f"Warning: Key field '{self.config.key_field}' not found in payload")
        
        # No key specified
        return None
    
    async def disconnect(self):
        """Close Kafka producer"""
        if self.producer:
            await self.producer.stop()
            self.producer = None