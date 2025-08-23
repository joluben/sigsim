"""
Base target connector interface
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class TargetConnector(ABC):
    """Abstract base class for target system connectors"""
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        Establish connection to the target system
        
        Returns:
            True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def send(self, payload: Dict[str, Any]) -> bool:
        """
        Send payload to the target system
        
        Args:
            payload: Dictionary representing the JSON payload
            
        Returns:
            True if send successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def disconnect(self):
        """
        Close connection to the target system
        """
        pass