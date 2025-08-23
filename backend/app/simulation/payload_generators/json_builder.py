"""
Visual JSON builder payload generator
"""
import random
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from app.simulation.payload_generators.base_generator import PayloadGenerator


class FieldGenerator:
    """Generates values for individual JSON fields"""
    
    def __init__(self, field_config: Dict[str, Any]):
        self.config = field_config
        self.field_type = field_config.get("type", "string")
        self.generator_config = field_config.get("generator", {})
    
    async def generate(self) -> Any:
        """Generate a value based on field configuration"""
        if self.field_type == "string":
            return await self._generate_string()
        elif self.field_type == "number":
            return await self._generate_number()
        elif self.field_type == "boolean":
            return await self._generate_boolean()
        elif self.field_type == "uuid":
            return str(uuid.uuid4())
        elif self.field_type == "timestamp":
            return datetime.utcnow().isoformat()
        else:
            return None
    
    async def _generate_string(self) -> str:
        """Generate string value"""
        generator_type = self.generator_config.get("type", "fixed")
        
        if generator_type == "fixed":
            return self.generator_config.get("value", "default")
        elif generator_type == "random_choice":
            choices = self.generator_config.get("choices", ["option1", "option2"])
            return random.choice(choices)
        elif generator_type == "random_string":
            length = self.generator_config.get("length", 10)
            chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
            return ''.join(random.choice(chars) for _ in range(length))
        else:
            return "default"
    
    async def _generate_number(self) -> Union[int, float]:
        """Generate number value"""
        generator_type = self.generator_config.get("type", "fixed")
        
        if generator_type == "fixed":
            return self.generator_config.get("value", 0)
        elif generator_type == "random_int":
            min_val = self.generator_config.get("min", 0)
            max_val = self.generator_config.get("max", 100)
            return random.randint(min_val, max_val)
        elif generator_type == "random_float":
            min_val = self.generator_config.get("min", 0.0)
            max_val = self.generator_config.get("max", 100.0)
            decimals = self.generator_config.get("decimals", 2)
            return round(random.uniform(min_val, max_val), decimals)
        else:
            return 0
    
    async def _generate_boolean(self) -> bool:
        """Generate boolean value"""
        generator_type = self.generator_config.get("type", "fixed")
        
        if generator_type == "fixed":
            return self.generator_config.get("value", True)
        elif generator_type == "random":
            return random.choice([True, False])
        else:
            return True


class JsonBuilderGenerator(PayloadGenerator):
    """Payload generator based on visual JSON schema"""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
        self.field_generators = {}
        self._build_generators()
    
    def _build_generators(self):
        """Build field generators from schema"""
        fields = self.schema.get("fields", [])
        for field in fields:
            field_name = field.get("name")
            if field_name:
                self.field_generators[field_name] = FieldGenerator(field)
    
    async def generate(self, device_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate payload based on schema"""
        result = {}
        
        # Generate fields from schema
        for field_name, generator in self.field_generators.items():
            result[field_name] = await generator.generate()
        
        # Override with device metadata if provided
        if device_metadata:
            result.update(device_metadata)
        
        return result


# Example schema format:
EXAMPLE_SCHEMA = {
    "fields": [
        {
            "name": "device_id",
            "type": "string",
            "generator": {
                "type": "fixed",
                "value": "device-001"
            }
        },
        {
            "name": "temperature",
            "type": "number",
            "generator": {
                "type": "random_float",
                "min": 18.0,
                "max": 25.0,
                "decimals": 1
            }
        },
        {
            "name": "humidity",
            "type": "number",
            "generator": {
                "type": "random_int",
                "min": 30,
                "max": 80
            }
        },
        {
            "name": "status",
            "type": "string",
            "generator": {
                "type": "random_choice",
                "choices": ["online", "offline", "maintenance"]
            }
        },
        {
            "name": "timestamp",
            "type": "timestamp"
        },
        {
            "name": "session_id",
            "type": "uuid"
        }
    ]
}