"""
Connector Factory for creating target system connectors
"""
from typing import Dict, Any, Type
from app.simulation.connectors.base_connector import TargetConnector
from app.simulation.connectors.http_connector import HTTPConnector
from app.simulation.connectors.mqtt_connector import MQTTConnector
from app.simulation.connectors.kafka_connector import KafkaConnector
from app.simulation.connectors.websocket_connector import WebSocketConnector
from app.simulation.connectors.ftp_connector import FTPConnector
from app.simulation.connectors.pubsub_connector import PubSubConnector
from app.models.target import (
    TargetType, 
    HTTPConfig, 
    MQTTConfig, 
    KafkaConfig, 
    WebSocketConfig,
    FTPConfig,
    PubSubConfig
)


class ConnectorFactory:
    """Factory class for creating target system connectors"""
    
    # Registry of connector classes by target type
    _connectors: Dict[TargetType, Type[TargetConnector]] = {
        TargetType.HTTP: HTTPConnector,
        TargetType.MQTT: MQTTConnector,
        TargetType.KAFKA: KafkaConnector,
        TargetType.WEBSOCKET: WebSocketConnector,
        TargetType.FTP: FTPConnector,
        TargetType.PUBSUB: PubSubConnector,
    }
    
    # Registry of config classes by target type
    _config_classes: Dict[TargetType, Type] = {
        TargetType.HTTP: HTTPConfig,
        TargetType.MQTT: MQTTConfig,
        TargetType.KAFKA: KafkaConfig,
        TargetType.WEBSOCKET: WebSocketConfig,
        TargetType.FTP: FTPConfig,
        TargetType.PUBSUB: PubSubConfig,
    }
    
    @classmethod
    def create_connector(cls, target_type: TargetType, config: Dict[str, Any]) -> TargetConnector:
        """
        Create a connector instance for the specified target type
        
        Args:
            target_type: The type of target system
            config: Configuration dictionary for the target system
            
        Returns:
            TargetConnector instance
            
        Raises:
            ValueError: If target type is not supported or config is invalid
        """
        if target_type not in cls._connectors:
            raise ValueError(f"Unsupported target type: {target_type}")
        
        # Get the appropriate config class and validate configuration
        config_class = cls._config_classes.get(target_type)
        if config_class:
            try:
                validated_config = config_class(**config)
            except Exception as e:
                raise ValueError(f"Invalid configuration for {target_type}: {e}")
        else:
            # For types without specific config classes, use raw config
            validated_config = config
        
        # Get the connector class and create instance
        connector_class = cls._connectors[target_type]
        return connector_class(validated_config)
    
    @classmethod
    def get_supported_types(cls) -> list[TargetType]:
        """
        Get list of supported target types
        
        Returns:
            List of supported TargetType values
        """
        return list(cls._connectors.keys())
    
    @classmethod
    def is_supported(cls, target_type: TargetType) -> bool:
        """
        Check if a target type is supported
        
        Args:
            target_type: The target type to check
            
        Returns:
            True if supported, False otherwise
        """
        return target_type in cls._connectors
    
    @classmethod
    def register_connector(cls, target_type: TargetType, connector_class: Type[TargetConnector], config_class: Type = None):
        """
        Register a new connector type
        
        Args:
            target_type: The target type identifier
            connector_class: The connector implementation class
            config_class: Optional configuration class for validation
        """
        if not issubclass(connector_class, TargetConnector):
            raise ValueError("Connector class must inherit from TargetConnector")
        
        cls._connectors[target_type] = connector_class
        if config_class:
            cls._config_classes[target_type] = config_class
    
    @classmethod
    def get_config_schema(cls, target_type: TargetType) -> Dict[str, Any]:
        """
        Get the configuration schema for a target type
        
        Args:
            target_type: The target type
            
        Returns:
            Dictionary representing the configuration schema
        """
        config_class = cls._config_classes.get(target_type)
        if config_class:
            return config_class.schema()
        return {}
    
    @classmethod
    def validate_config(cls, target_type: TargetType, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate configuration for a target type
        
        Args:
            target_type: The target type
            config: Configuration dictionary to validate
            
        Returns:
            Validated configuration dictionary
            
        Raises:
            ValueError: If configuration is invalid
        """
        config_class = cls._config_classes.get(target_type)
        if config_class:
            try:
                validated_config = config_class(**config)
                return validated_config.dict()
            except Exception as e:
                raise ValueError(f"Invalid configuration for {target_type}: {e}")
        
        # For types without specific config classes, return as-is
        return config


# Convenience function for creating connectors
def create_connector(target_type: str, config: Dict[str, Any]) -> TargetConnector:
    """
    Convenience function to create a connector
    
    Args:
        target_type: String representation of target type
        config: Configuration dictionary
        
    Returns:
        TargetConnector instance
    """
    try:
        target_enum = TargetType(target_type.lower())
        return ConnectorFactory.create_connector(target_enum, config)
    except ValueError as e:
        raise ValueError(f"Failed to create connector: {e}")


# Convenience function to get supported types as strings
def get_supported_connector_types() -> list[str]:
    """
    Get list of supported connector types as strings
    
    Returns:
        List of supported target type strings
    """
    return [t.value for t in ConnectorFactory.get_supported_types()]