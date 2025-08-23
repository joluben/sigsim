"""
Pub/Sub target connector for cloud messaging services
"""
import json
import asyncio
from typing import Dict, Any
from app.simulation.connectors.base_connector import TargetConnector
from app.models.target import PubSubConfig


class PubSubConnector(TargetConnector):
    """Connector for cloud Pub/Sub services (GCP, AWS, Azure)"""
    
    def __init__(self, config: PubSubConfig):
        self.config = config
        self.client = None
        self.connected = False
    
    async def connect(self) -> bool:
        """Connect to Pub/Sub service"""
        try:
            if self.config.provider == 'gcp':
                return await self._connect_gcp()
            elif self.config.provider == 'aws':
                return await self._connect_aws()
            elif self.config.provider == 'azure':
                return await self._connect_azure()
            else:
                print(f"Unsupported Pub/Sub provider: {self.config.provider}")
                return False
                
        except Exception as e:
            print(f"Pub/Sub connection failed: {e}")
            return False
    
    async def send(self, payload: Dict[str, Any]) -> bool:
        """Send message to Pub/Sub topic"""
        if not self.connected:
            return False
        
        try:
            if self.config.provider == 'gcp':
                return await self._send_gcp(payload)
            elif self.config.provider == 'aws':
                return await self._send_aws(payload)
            elif self.config.provider == 'azure':
                return await self._send_azure(payload)
            else:
                return False
                
        except Exception as e:
            print(f"Pub/Sub send failed: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from Pub/Sub service"""
        if self.client:
            try:
                if self.config.provider == 'gcp':
                    await self._disconnect_gcp()
                elif self.config.provider == 'aws':
                    await self._disconnect_aws()
                elif self.config.provider == 'azure':
                    await self._disconnect_azure()
            except:
                pass  # Ignore errors during disconnect
            finally:
                self.client = None
                self.connected = False
    
    async def _connect_gcp(self) -> bool:
        """Connect to Google Cloud Pub/Sub"""
        try:
            from google.cloud import pubsub_v1
            from google.oauth2 import service_account
            
            # Create credentials from service account info
            credentials_info = self.config.credentials.get('service_account_info')
            if credentials_info:
                credentials = service_account.Credentials.from_service_account_info(credentials_info)
                self.client = pubsub_v1.PublisherClient(credentials=credentials)
            else:
                # Use default credentials
                self.client = pubsub_v1.PublisherClient()
            
            # Validate topic exists or create topic path
            project_id = self.config.credentials.get('project_id')
            if not project_id:
                raise ValueError("GCP project_id is required in credentials")
            
            self.topic_path = self.client.topic_path(project_id, self.config.topic)
            self.connected = True
            return True
            
        except ImportError:
            print("Google Cloud Pub/Sub library not installed. Install with: pip install google-cloud-pubsub")
            return False
        except Exception as e:
            print(f"GCP Pub/Sub connection failed: {e}")
            return False
    
    async def _send_gcp(self, payload: Dict[str, Any]) -> bool:
        """Send message to GCP Pub/Sub"""
        try:
            message_data = json.dumps(payload).encode('utf-8')
            future = self.client.publish(self.topic_path, message_data)
            
            # Wait for publish to complete
            await asyncio.get_event_loop().run_in_executor(None, future.result)
            return True
            
        except Exception as e:
            print(f"GCP Pub/Sub send failed: {e}")
            return False
    
    async def _disconnect_gcp(self):
        """Disconnect from GCP Pub/Sub"""
        # GCP client doesn't require explicit disconnect
        pass
    
    async def _connect_aws(self) -> bool:
        """Connect to AWS SNS/SQS"""
        try:
            import boto3
            
            # Create SNS client with credentials
            aws_credentials = self.config.credentials
            self.client = boto3.client(
                'sns',
                region_name=aws_credentials.get('region', 'us-east-1'),
                aws_access_key_id=aws_credentials.get('access_key_id'),
                aws_secret_access_key=aws_credentials.get('secret_access_key')
            )
            
            # Store topic ARN
            self.topic_arn = aws_credentials.get('topic_arn')
            if not self.topic_arn:
                # Try to find topic by name
                response = self.client.list_topics()
                for topic in response.get('Topics', []):
                    if topic['TopicArn'].endswith(f":{self.config.topic}"):
                        self.topic_arn = topic['TopicArn']
                        break
                
                if not self.topic_arn:
                    raise ValueError(f"Topic '{self.config.topic}' not found")
            
            self.connected = True
            return True
            
        except ImportError:
            print("AWS SDK not installed. Install with: pip install boto3")
            return False
        except Exception as e:
            print(f"AWS SNS connection failed: {e}")
            return False
    
    async def _send_aws(self, payload: Dict[str, Any]) -> bool:
        """Send message to AWS SNS"""
        try:
            message = json.dumps(payload)
            
            # Publish message
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.publish(
                    TopicArn=self.topic_arn,
                    Message=message
                )
            )
            
            return 'MessageId' in response
            
        except Exception as e:
            print(f"AWS SNS send failed: {e}")
            return False
    
    async def _disconnect_aws(self):
        """Disconnect from AWS SNS"""
        # AWS client doesn't require explicit disconnect
        pass
    
    async def _connect_azure(self) -> bool:
        """Connect to Azure Service Bus"""
        try:
            from azure.servicebus.aio import ServiceBusClient
            
            # Create Service Bus client
            connection_string = self.config.credentials.get('connection_string')
            if not connection_string:
                raise ValueError("Azure Service Bus connection_string is required")
            
            self.client = ServiceBusClient.from_connection_string(connection_string)
            self.connected = True
            return True
            
        except ImportError:
            print("Azure Service Bus library not installed. Install with: pip install azure-servicebus")
            return False
        except Exception as e:
            print(f"Azure Service Bus connection failed: {e}")
            return False
    
    async def _send_azure(self, payload: Dict[str, Any]) -> bool:
        """Send message to Azure Service Bus"""
        try:
            from azure.servicebus import ServiceBusMessage
            
            message = ServiceBusMessage(json.dumps(payload))
            
            async with self.client:
                sender = self.client.get_topic_sender(topic_name=self.config.topic)
                async with sender:
                    await sender.send_messages(message)
            
            return True
            
        except Exception as e:
            print(f"Azure Service Bus send failed: {e}")
            return False
    
    async def _disconnect_azure(self):
        """Disconnect from Azure Service Bus"""
        if self.client:
            await self.client.close()