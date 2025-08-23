"""
Visual payload generator - integrates with JsonBuilderGenerator
"""
from typing import Dict, Any, Optional
from app.simulation.payload_generators.base_generator import PayloadGenerator
from app.simulation.payload_generators.json_builder import JsonBuilderGenerator


class VisualPayloadGenerator(PayloadGenerator):
    """
    Visual payload generator that uses the JsonBuilderGenerator
    This is a wrapper to maintain compatibility with the simulation engine
    """
    
    def __init__(self, schema: Dict[str, Any]):
        """
        Initialize with a payload schema
        
        Args:
            schema: Dictionary containing the payload schema with fields configuration
        """
        self.json_builder = JsonBuilderGenerator(schema)
    
    async def generate(self, device_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate payload using the visual schema
        
        Args:
            device_metadata: Optional device-specific metadata to include
            
        Returns:
            Dictionary representing the JSON payload
        """
        return await self.json_builder.generate(device_metadata)