"""
Python code payload generator with safe execution
"""
import ast
import sys
import random
import uuid
import math
import json
from datetime import datetime
from typing import Dict, Any, Optional, Set
from app.simulation.payload_generators.base_generator import PayloadGenerator


class SafePythonExecutor:
    """Safe Python code executor with sandboxing"""
    
    # Allowed built-in functions and modules
    ALLOWED_BUILTINS = {
        'abs', 'all', 'any', 'bool', 'dict', 'enumerate', 'filter', 'float',
        'int', 'len', 'list', 'map', 'max', 'min', 'range', 'round', 'str',
        'sum', 'tuple', 'zip'
    }
    
    ALLOWED_MODULES = {
        'random', 'datetime', 'uuid', 'math', 'json'
    }
    
    def __init__(self):
        self.compiled_code = None
    
    def validate_code(self, code: str) -> bool:
        """Validate that the code is safe to execute"""
        try:
            tree = ast.parse(code)
            validator = CodeValidator(self.ALLOWED_BUILTINS, self.ALLOWED_MODULES)
            validator.visit(tree)
            return True
        except (SyntaxError, ValueError) as e:
            print(f"Code validation failed: {e}")
            return False
    
    def compile_code(self, code: str) -> bool:
        """Compile the Python code"""
        if not self.validate_code(code):
            return False
        
        try:
            self.compiled_code = compile(code, '<user_code>', 'exec')
            return True
        except SyntaxError as e:
            print(f"Code compilation failed: {e}")
            return False
    
    async def execute(self, device_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute the compiled code safely"""
        if not self.compiled_code:
            raise ValueError("No code compiled")
        
        # Create safe execution context
        safe_globals = {
            '__builtins__': {name: getattr(__builtins__, name) for name in self.ALLOWED_BUILTINS},
            'random': random,
            'datetime': datetime,
            'uuid': uuid,
            'math': math,
            'json': json,
        }
        
        safe_locals = {
            'device_metadata': device_metadata or {},
            'result': {}
        }
        
        try:
            exec(self.compiled_code, safe_globals, safe_locals)
            return safe_locals.get('result', {})
        except Exception as e:
            print(f"Code execution failed: {e}")
            return {"error": str(e)}


class CodeValidator(ast.NodeVisitor):
    """AST visitor to validate Python code safety"""
    
    def __init__(self, allowed_builtins: Set[str], allowed_modules: Set[str]):
        self.allowed_builtins = allowed_builtins
        self.allowed_modules = allowed_modules
    
    def visit_Import(self, node):
        """Check import statements"""
        for alias in node.names:
            if alias.name not in self.allowed_modules:
                raise ValueError(f"Import not allowed: {alias.name}")
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """Check from-import statements"""
        if node.module not in self.allowed_modules:
            raise ValueError(f"Import not allowed: {node.module}")
        self.generic_visit(node)
    
    def visit_Call(self, node):
        """Check function calls"""
        # Allow calls to allowed built-ins and module functions
        if isinstance(node.func, ast.Name):
            if node.func.id not in self.allowed_builtins:
                # Check if it's a module function
                pass  # Will be checked at runtime
        self.generic_visit(node)
    
    def visit_Attribute(self, node):
        """Check attribute access"""
        # Prevent access to dangerous attributes
        dangerous_attrs = ['__import__', '__builtins__', 'exec', 'eval', 'open', 'file']
        if isinstance(node.attr, str) and node.attr in dangerous_attrs:
            raise ValueError(f"Attribute access not allowed: {node.attr}")
        self.generic_visit(node)


class PythonCodeGenerator(PayloadGenerator):
    """Payload generator that executes user Python code"""
    
    def __init__(self, python_code: str):
        self.code = python_code
        self.executor = SafePythonExecutor()
        
        # Compile code on initialization
        if not self.executor.compile_code(python_code):
            raise ValueError("Failed to compile Python code")
    
    async def generate(self, device_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate payload by executing Python code"""
        return await self.executor.execute(device_metadata)


# Example Python code:
EXAMPLE_PYTHON_CODE = '''
import random
from datetime import datetime
import uuid

# Access device metadata
device_id = device_metadata.get('device_id', 'unknown')
location = device_metadata.get('location', 'default')

# Generate payload
result = {
    "device_id": device_id,
    "location": location,
    "timestamp": datetime.utcnow().isoformat(),
    "session_id": str(uuid.uuid4()),
    "temperature": round(random.uniform(18.0, 25.0), 1),
    "humidity": random.randint(30, 80),
    "battery_level": random.randint(20, 100),
    "status": random.choice(["online", "offline", "maintenance"]),
    "readings": [
        {"sensor": "temp", "value": round(random.uniform(20, 30), 2)},
        {"sensor": "pressure", "value": round(random.uniform(1000, 1100), 1)}
    ]
}
'''