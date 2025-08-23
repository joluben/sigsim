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
            return False
    
    async def send(self, payload: Dict[str, Any]) -> bool:
        """Send message to Kafka topic"""
        if not self.producer:
            return False
        
        try:
            await self.producer.send_and_wait(
                self.config.topic,
                payload
            )
            return True
            
        except Exception as e:
            print(f"Kafka send failed: {e}")
            return False
    
    async def disconnect(self):
        """Close Kafka producer"""
        if self.producer:
            await self.producer.stop()
            self.producer = None