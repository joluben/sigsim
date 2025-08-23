"""
Base payload generator interface
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class PayloadGenerator(ABC):
    """Abstract base class for payload generators"""
    
    @abstractmethod
    async def generate(self, device_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a payload dictionary
        
        Args:
            device_metadata: Optional device-specific metadata to include
            
        Returns:
            Dictionary representing the JSON payload
        """
        pass