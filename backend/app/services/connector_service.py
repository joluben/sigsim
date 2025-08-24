"""
Service for managing target system connectors
"""
from typing import Dict, Any, List
from app.simulation.connectors import ConnectorFactory, TargetConnector
from app.models.target import TargetType
from app.repositories.target_repository import TargetSystemRepository


class ConnectorService:
    """Service for managing target system connectors"""
    
    def __init__(self, target_repository: TargetSystemRepository):
        self.target_repository = target_repository
        self._active_connectors: Dict[str, TargetConnector] = {}
    
    async def create_connector(self, target_system_id: str) -> TargetConnector:
        """
        Create a connector for a target system
        
        Args:
            target_system_id: ID of the target system
            
        Returns:
            TargetConnector instance
            
        Raises:
            ValueError: If target system not found or unsupported
        """
        # Get target system from repository
        target_system = await self.target_repository.get_by_id(target_system_id)
        if not target_system:
            raise ValueError(f"Target system not found: {target_system_id}")
        
        # Create connector using factory
        target_type = TargetType(target_system.type)
        connector = ConnectorFactory.create_connector(target_type, target_system.config)
        
        return connector
    
    async def get_or_create_connector(self, target_system_id: str) -> TargetConnector:
        """
        Get existing connector or create new one
        
        Args:
            target_system_id: ID of the target system
            
        Returns:
            TargetConnector instance
        """
        # Check if connector already exists and is connected
        if target_system_id in self._active_connectors:
            connector = self._active_connectors[target_system_id]
            # You might want to add a health check here
            return connector
        
        # Create new connector
        connector = await self.create_connector(target_system_id)
        self._active_connectors[target_system_id] = connector
        
        return connector
    
    async def connect_target(self, target_system_id: str) -> bool:
        """
        Connect to a target system
        
        Args:
            target_system_id: ID of the target system
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            connector = await self.get_or_create_connector(target_system_id)
            return await connector.connect()
        except Exception as e:
            print(f"Failed to connect to target {target_system_id}: {e}")
            return False
    
    async def send_to_target(self, target_system_id: str, payload: Dict[str, Any]) -> bool:
        """
        Send payload to a target system
        
        Args:
            target_system_id: ID of the target system
            payload: Data to send
            
        Returns:
            True if send successful, False otherwise
        """
        try:
            connector = await self.get_or_create_connector(target_system_id)
            return await connector.send(payload)
        except Exception as e:
            print(f"Failed to send to target {target_system_id}: {e}")
            return False
    
    async def disconnect_target(self, target_system_id: str):
        """
        Disconnect from a target system
        
        Args:
            target_system_id: ID of the target system
        """
        if target_system_id in self._active_connectors:
            connector = self._active_connectors[target_system_id]
            try:
                await connector.disconnect()
            except Exception as e:
                print(f"Error disconnecting from target {target_system_id}: {e}")
            finally:
                del self._active_connectors[target_system_id]
    
    async def disconnect_all(self):
        """Disconnect from all active target systems"""
        for target_id in list(self._active_connectors.keys()):
            await self.disconnect_target(target_id)
    
    async def test_connection(self, target_system_id: str) -> Dict[str, Any]:
        """
        Test connection to a target system
        
        Args:
            target_system_id: ID of the target system
            
        Returns:
            Dictionary with test results
        """
        try:
            connector = await self.create_connector(target_system_id)
            
            # Test connection
            connect_success = await connector.connect()
            if not connect_success:
                return {
                    'success': False,
                    'error': 'Failed to connect to target system',
                    'details': 'Connection attempt failed'
                }
            
            # Test sending a sample payload
            test_payload = {
                'test': True,
                'timestamp': '2024-01-01T00:00:00Z',
                'message': 'Connection test from IoT Simulator'
            }
            
            send_success = await connector.send(test_payload)
            await connector.disconnect()
            
            if send_success:
                return {
                    'success': True,
                    'message': 'Connection test successful',
                    'test_payload': test_payload
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to send test payload',
                    'details': 'Send operation failed'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Connection test failed: {str(e)}',
                'details': str(e)
            }
    
    def get_supported_types(self) -> List[str]:
        """
        Get list of supported target types
        
        Returns:
            List of supported target type strings
        """
        return [t.value for t in ConnectorFactory.get_supported_types()]
    
    def get_config_schema(self, target_type: str) -> Dict[str, Any]:
        """
        Get configuration schema for a target type
        
        Args:
            target_type: Target type string
            
        Returns:
            Configuration schema dictionary
        """
        try:
            target_enum = TargetType(target_type.lower())
            return ConnectorFactory.get_config_schema(target_enum)
        except ValueError:
            return {}
    
    def validate_config(self, target_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate configuration for a target type
        
        Args:
            target_type: Target type string
            config: Configuration to validate
            
        Returns:
            Validated configuration dictionary
            
        Raises:
            ValueError: If configuration is invalid
        """
        target_enum = TargetType(target_type.lower())
        return ConnectorFactory.validate_config(target_enum, config)
    
    def get_active_connections(self) -> List[str]:
        """
        Get list of active connection IDs
        
        Returns:
            List of target system IDs with active connections
        """
        return list(self._active_connectors.keys())
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on all active connections
        
        Returns:
            Dictionary with health check results
        """
        results = {
            'total_connections': len(self._active_connectors),
            'healthy_connections': 0,
            'unhealthy_connections': 0,
            'connection_details': {}
        }
        
        for target_id, connector in self._active_connectors.items():
            try:
                # Simple health check - try to send a minimal test payload
                test_payload = {'health_check': True}
                success = await connector.send(test_payload)
                
                if success:
                    results['healthy_connections'] += 1
                    results['connection_details'][target_id] = {
                        'status': 'healthy',
                        'last_check': 'now'
                    }
                else:
                    results['unhealthy_connections'] += 1
                    results['connection_details'][target_id] = {
                        'status': 'unhealthy',
                        'error': 'Send test failed'
                    }
                    
            except Exception as e:
                results['unhealthy_connections'] += 1
                results['connection_details'][target_id] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        return results