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


class PayloadGeneratorFactory:
    """Factory for creating payload generators"""
    
    @staticmethod
    def create_generator(generator_type: str, config: Dict[str, Any]) -> PayloadGenerator:
        """
        Create a payload generator based on type and configuration
        
        Args:
            generator_type: Type of generator ('json_builder', 'python_code', 'visual')
            config: Configuration dictionary for the generator
            
        Returns:
            PayloadGenerator instance
            
        Raises:
            ValueError: If generator_type is not supported
        """
        from .json_builder import JsonBuilderGenerator
        from .python_runner import PythonCodeGenerator
        
        if generator_type == "json_builder":
            return JsonBuilderGenerator(config)
        elif generator_type == "python_code":
            # Extract Python code from config
            python_code = config.get("code", "result = {}")
            return PythonCodeGenerator(python_code)
        else:
            raise ValueError(f"Unsupported generator type: {generator_type}")