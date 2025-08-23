"""
Validation service for business logic validation
"""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.repositories.project_repository import ProjectRepository
from app.repositories.device_repository import DeviceRepository
from app.repositories.payload_repository import PayloadRepository
from app.repositories.target_repository import TargetSystemRepository
from app.models.target import TargetType
from app.models.payload import PayloadType
from app.utils.logger import app_logger


class ValidationError(Exception):
    """Custom validation error"""
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


class ValidationService:
    """Service for business logic validation"""
    
    def __init__(self, db: Session):
        self.project_repository = ProjectRepository(db)
        self.device_repository = DeviceRepository(db)
        self.payload_repository = PayloadRepository(db)
        self.target_repository = TargetSystemRepository(db)
        self.logger = app_logger
    
    async def validate_project_creation(self, project_data: Dict[str, Any]) -> List[str]:
        """Validate project creation data"""
        errors = []
        
        # Check if name already exists
        if await self.project_repository.name_exists(project_data.get('name', '')):
            errors.append("Project name already exists")
        
        return errors
    
    async def validate_project_update(self, project_id: str, project_data: Dict[str, Any]) -> List[str]:
        """Validate project update data"""
        errors = []
        
        # Check if project exists
        if not await self.project_repository.exists(project_id):
            errors.append("Project not found")
            return errors
        
        # Check if new name already exists (if name is being updated)
        if 'name' in project_data:
            if await self.project_repository.name_exists(project_data['name'], exclude_id=project_id):
                errors.append("Project name already exists")
        
        return errors
    
    async def validate_device_creation(self, device_data: Dict[str, Any]) -> List[str]:
        """Validate device creation data"""
        errors = []
        
        # Check if project exists
        project_id = device_data.get('project_id')
        if not project_id or not await self.project_repository.exists(project_id):
            errors.append("Project not found")
        
        # Check if payload exists (if provided)
        payload_id = device_data.get('payload_id')
        if payload_id and not await self.payload_repository.exists(payload_id):
            errors.append("Payload not found")
        
        # Check if target system exists (if provided)
        target_id = device_data.get('target_system_id')
        if target_id and not await self.target_repository.exists(target_id):
            errors.append("Target system not found")
        
        return errors
    
    async def validate_device_update(self, device_id: str, device_data: Dict[str, Any]) -> List[str]:
        """Validate device update data"""
        errors = []
        
        # Check if device exists
        if not await self.device_repository.exists(device_id):
            errors.append("Device not found")
            return errors
        
        # Check if payload exists (if being updated)
        if 'payload_id' in device_data and device_data['payload_id']:
            if not await self.payload_repository.exists(device_data['payload_id']):
                errors.append("Payload not found")
        
        # Check if target system exists (if being updated)
        if 'target_system_id' in device_data and device_data['target_system_id']:
            if not await self.target_repository.exists(device_data['target_system_id']):
                errors.append("Target system not found")
        
        return errors
    
    async def validate_payload_creation(self, payload_data: Dict[str, Any]) -> List[str]:
        """Validate payload creation data"""
        errors = []
        
        # Check if name already exists
        if await self.payload_repository.name_exists(payload_data.get('name', '')):
            errors.append("Payload name already exists")
        
        # Validate payload type specific requirements
        payload_type = payload_data.get('type')
        if payload_type == PayloadType.VISUAL:
            if not payload_data.get('schema'):
                errors.append("Schema is required for visual payloads")
            else:
                schema_errors = self._validate_payload_schema(payload_data['schema'])
                errors.extend(schema_errors)
        elif payload_type == PayloadType.PYTHON:
            if not payload_data.get('python_code'):
                errors.append("Python code is required for python payloads")
            else:
                code_errors = self._validate_python_code(payload_data['python_code'])
                errors.extend(code_errors)
        
        return errors
    
    async def validate_payload_update(self, payload_id: str, payload_data: Dict[str, Any]) -> List[str]:
        """Validate payload update data"""
        errors = []
        
        # Check if payload exists
        if not await self.payload_repository.exists(payload_id):
            errors.append("Payload not found")
            return errors
        
        # Check if new name already exists (if name is being updated)
        if 'name' in payload_data:
            if await self.payload_repository.name_exists(payload_data['name'], exclude_id=payload_id):
                errors.append("Payload name already exists")
        
        # Validate schema if provided
        if 'schema' in payload_data and payload_data['schema']:
            schema_errors = self._validate_payload_schema(payload_data['schema'])
            errors.extend(schema_errors)
        
        # Validate python code if provided
        if 'python_code' in payload_data and payload_data['python_code']:
            code_errors = self._validate_python_code(payload_data['python_code'])
            errors.extend(code_errors)
        
        return errors
    
    async def validate_target_system_creation(self, target_data: Dict[str, Any]) -> List[str]:
        """Validate target system creation data"""
        errors = []
        
        # Check if name already exists
        if await self.target_repository.name_exists(target_data.get('name', '')):
            errors.append("Target system name already exists")
        
        # Validate target type specific configuration
        target_type = target_data.get('type')
        config = target_data.get('config', {})
        
        if target_type == TargetType.MQTT:
            config_errors = self._validate_mqtt_config(config)
            errors.extend(config_errors)
        elif target_type == TargetType.HTTP:
            config_errors = self._validate_http_config(config)
            errors.extend(config_errors)
        elif target_type == TargetType.KAFKA:
            config_errors = self._validate_kafka_config(config)
            errors.extend(config_errors)
        elif target_type == TargetType.WEBSOCKET:
            config_errors = self._validate_websocket_config(config)
            errors.extend(config_errors)
        
        return errors
    
    async def validate_target_system_update(self, target_id: str, target_data: Dict[str, Any]) -> List[str]:
        """Validate target system update data"""
        errors = []
        
        # Check if target system exists
        if not await self.target_repository.exists(target_id):
            errors.append("Target system not found")
            return errors
        
        # Check if new name already exists (if name is being updated)
        if 'name' in target_data:
            if await self.target_repository.name_exists(target_data['name'], exclude_id=target_id):
                errors.append("Target system name already exists")
        
        return errors
    
    def _validate_payload_schema(self, schema: Dict[str, Any]) -> List[str]:
        """Validate payload schema structure"""
        errors = []
        
        if not isinstance(schema, dict):
            errors.append("Schema must be a dictionary")
            return errors
        
        if 'fields' not in schema:
            errors.append("Schema must contain 'fields' array")
            return errors
        
        fields = schema['fields']
        if not isinstance(fields, list):
            errors.append("Schema fields must be an array")
            return errors
        
        for i, field in enumerate(fields):
            if not isinstance(field, dict):
                errors.append(f"Field {i} must be a dictionary")
                continue
            
            if 'name' not in field:
                errors.append(f"Field {i} missing 'name'")
            
            if 'type' not in field:
                errors.append(f"Field {i} missing 'type'")
            
            if 'generator' not in field:
                errors.append(f"Field {i} missing 'generator'")
        
        return errors
    
    def _validate_python_code(self, code: str) -> List[str]:
        """Validate Python code syntax"""
        errors = []
        
        try:
            compile(code, '<string>', 'exec')
        except SyntaxError as e:
            errors.append(f"Python syntax error: {e}")
        except Exception as e:
            errors.append(f"Python code error: {e}")
        
        return errors
    
    def _validate_mqtt_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate MQTT configuration"""
        errors = []
        required_fields = ['host', 'port', 'topic']
        
        for field in required_fields:
            if field not in config:
                errors.append(f"MQTT configuration missing '{field}'")
        
        if 'port' in config:
            port = config['port']
            if not isinstance(port, int) or port < 1 or port > 65535:
                errors.append("MQTT port must be between 1 and 65535")
        
        return errors
    
    def _validate_http_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate HTTP configuration"""
        errors = []
        
        if 'url' not in config:
            errors.append("HTTP configuration missing 'url'")
        
        if 'method' in config:
            method = config['method'].upper()
            if method not in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
                errors.append("Invalid HTTP method")
        
        return errors
    
    def _validate_kafka_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate Kafka configuration"""
        errors = []
        required_fields = ['bootstrap_servers', 'topic']
        
        for field in required_fields:
            if field not in config:
                errors.append(f"Kafka configuration missing '{field}'")
        
        return errors
    
    def _validate_websocket_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate WebSocket configuration"""
        errors = []
        
        if 'url' not in config:
            errors.append("WebSocket configuration missing 'url'")
        else:
            url = config['url']
            if not (url.startswith('ws://') or url.startswith('wss://')):
                errors.append("WebSocket URL must start with ws:// or wss://")
        
        return errors