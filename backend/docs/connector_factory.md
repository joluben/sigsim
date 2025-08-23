# ConnectorFactory System

El sistema ConnectorFactory proporciona una interfaz unificada para crear y gestionar conectores a diferentes sistemas de destino (target systems) en el simulador IoT.

## Arquitectura

### Componentes Principales

1. **TargetConnector (Base)**: Interfaz abstracta que define los métodos básicos
2. **ConnectorFactory**: Factory class que crea instancias de conectores
3. **Conectores Específicos**: Implementaciones para cada tipo de sistema
4. **Modelos de Configuración**: Validación con Pydantic

### Conectores Soportados

| Tipo | Descripción | Configuración Requerida |
|------|-------------|------------------------|
| HTTP | Endpoints REST/HTTP | url, method, headers, timeout |
| MQTT | Brokers MQTT | host, port, topic, credentials |
| Kafka | Apache Kafka | bootstrap_servers, topic, security |
| WebSocket | Conexiones WebSocket | url, headers, ping_interval |
| FTP | Transferencia de archivos | host, port, credentials, path |
| PubSub | Sistemas Pub/Sub | provider, topic, credentials |

## Uso Básico

### 1. Crear un Conector

```python
from app.simulation.connectors import ConnectorFactory
from app.models.target import TargetType

# Configuración para HTTP
config = {
    "url": "https://api.example.com/webhook",
    "method": "POST",
    "headers": {"Content-Type": "application/json"},
    "timeout": 30
}

# Crear conector
connector = ConnectorFactory.create_connector(TargetType.HTTP, config)
```

### 2. Usar el Conector

```python
# Conectar
await connector.connect()

# Enviar datos
payload = {
    "device_id": "sensor-001",
    "temperature": 23.5,
    "timestamp": "2024-01-01T12:00:00Z"
}

success = await connector.send(payload)

# Desconectar
await connector.disconnect()
```

### 3. Función de Conveniencia

```python
from app.simulation.connectors import create_connector

# Crear usando string
connector = create_connector("http", config)
```

## Configuraciones por Tipo

### HTTP/HTTPS

```python
config = {
    "url": "https://api.example.com/webhook",
    "method": "POST",  # GET, POST, PUT, PATCH, DELETE
    "headers": {
        "Content-Type": "application/json",
        "Authorization": "Bearer token"
    },
    "timeout": 30  # segundos
}
```

### MQTT

```python
config = {
    "host": "mqtt.example.com",
    "port": 1883,  # 8883 para TLS
    "topic": "iot/sensors/data",
    "username": "mqtt_user",  # opcional
    "password": "mqtt_pass",  # opcional
    "use_tls": False,
    "qos": 1  # 0, 1, o 2
}
```

#### Configuración Detallada MQTT

**Campos Requeridos:**
- `host`: Hostname o IP del broker MQTT
- `topic`: Tópico MQTT donde publicar mensajes

**Campos Opcionales:**
- `port`: Puerto del broker (default: 1883, TLS: 8883)
- `username`: Usuario para autenticación
- `password`: Contraseña para autenticación
- `use_tls`: Habilitar encriptación TLS/SSL (default: false)
- `qos`: Nivel de Quality of Service (0, 1, o 2, default: 0)

**Ejemplos de Configuración:**

```python
# Configuración básica
basic_config = {
    "host": "mqtt.example.com",
    "topic": "iot/sensors"
}

# Con autenticación
auth_config = {
    "host": "mqtt.example.com",
    "port": 1883,
    "topic": "iot/sensors",
    "username": "device_user",
    "password": "device_password",
    "qos": 1
}

# Con TLS/SSL
tls_config = {
    "host": "secure-mqtt.example.com",
    "port": 8883,
    "topic": "iot/secure/sensors",
    "use_tls": True,
    "qos": 2
}

# Configuración completa
full_config = {
    "host": "full-mqtt.example.com",
    "port": 8883,
    "topic": "iot/production/sensors",
    "username": "production_user",
    "password": "secure_password",
    "use_tls": True,
    "qos": 2
}
```

**Niveles de QoS:**
- `0`: At most once (fire and forget) - Más rápido, sin garantías
- `1`: At least once (acknowledged delivery) - Garantiza entrega, puede duplicar
- `2`: Exactly once (assured delivery) - Más lento, garantiza entrega única

### Kafka

```python
config = {
    "bootstrap_servers": "localhost:9092",
    "topic": "iot-data",
    "security_protocol": "PLAINTEXT",  # PLAINTEXT, SSL, SASL_PLAINTEXT, SASL_SSL
    "sasl_mechanism": "PLAIN",  # opcional
    "sasl_username": "kafka_user",  # opcional
    "sasl_password": "kafka_pass"  # opcional
}
```

### WebSocket

```python
config = {
    "url": "wss://websocket.example.com/stream",
    "headers": {
        "Authorization": "Bearer token"
    },
    "ping_interval": 20  # segundos
}
```

## Funciones Avanzadas

### 1. Validación de Configuración

```python
# Validar configuración antes de crear conector
try:
    validated_config = ConnectorFactory.validate_config(TargetType.HTTP, config)
    print("Configuración válida")
except ValueError as e:
    print(f"Configuración inválida: {e}")
```

### 2. Obtener Schema de Configuración

```python
# Obtener schema para documentación o UI
schema = ConnectorFactory.get_config_schema(TargetType.HTTP)
print(schema)
```

### 3. Tipos Soportados

```python
# Listar todos los tipos soportados
from app.simulation.connectors import get_supported_connector_types

types = get_supported_connector_types()
print(f"Tipos soportados: {types}")
```

### 4. Registrar Conector Personalizado

```python
class CustomConnector(TargetConnector):
    def __init__(self, config):
        self.config = config
    
    async def connect(self):
        # Implementar conexión
        return True
    
    async def send(self, payload):
        # Implementar envío
        return True
    
    async def disconnect(self):
        # Implementar desconexión
        pass

# Registrar el conector personalizado
ConnectorFactory.register_connector("custom", CustomConnector)
```

## Integración con el Sistema

### En el Motor de Simulación

```python
# El motor de simulación usa el factory automáticamente
from app.simulation.engine import SimulationEngine

engine = SimulationEngine.get_instance()
await engine.start_project(project_id, repositories...)
```

### En el Servicio de Conectores

```python
from app.services.connector_service import ConnectorService

service = ConnectorService(target_repository)

# Crear y probar conector
connector = await service.create_connector(target_system_id)
test_result = await service.test_connection(target_system_id)
```

### En las APIs

```python
# Endpoint para probar configuración
@router.post("/connectors/test")
async def test_connector_configuration(target_type: str, config: dict):
    connector = ConnectorFactory.create_connector(TargetType(target_type), config)
    # ... resto de la lógica
```

## Manejo de Errores

### Errores Comunes

1. **Tipo no soportado**:
   ```python
   try:
       connector = ConnectorFactory.create_connector("invalid_type", config)
   except ValueError as e:
       print(f"Tipo no soportado: {e}")
   ```

2. **Configuración inválida**:
   ```python
   try:
       connector = ConnectorFactory.create_connector(TargetType.HTTP, {})
   except ValueError as e:
       print(f"Configuración inválida: {e}")
   ```

3. **Error de conexión**:
   ```python
   connected = await connector.connect()
   if not connected:
       print("No se pudo conectar al sistema de destino")
   ```

4. **Error de envío**:
   ```python
   success = await connector.send(payload)
   if not success:
       print("No se pudo enviar el payload")
   ```

## Testing

### Ejecutar Tests

```bash
# Tests del factory
pytest backend/tests/simulation/test_connector_factory.py -v

# Demo interactivo
python backend/examples/connector_factory_demo.py
```

### Tests Unitarios

Los tests cubren:
- Creación de conectores para todos los tipos
- Validación de configuraciones
- Manejo de errores
- Funciones de conveniencia
- Registro de conectores personalizados

## Extensibilidad

### Agregar Nuevo Conector

1. **Crear la clase del conector**:
   ```python
   class NewConnector(TargetConnector):
       def __init__(self, config):
           self.config = config
       
       async def connect(self):
           # Implementar
           pass
       
       async def send(self, payload):
           # Implementar
           pass
       
       async def disconnect(self):
           # Implementar
           pass
   ```

2. **Crear modelo de configuración**:
   ```python
   class NewConfig(BaseModel):
       host: str
       port: int = 8080
       # ... otros campos
   ```

3. **Registrar en el factory**:
   ```python
   # En connector_factory.py
   _connectors[TargetType.NEW] = NewConnector
   _config_classes[TargetType.NEW] = NewConfig
   ```

4. **Agregar al enum**:
   ```python
   # En models/target.py
   class TargetType(str, Enum):
       # ... tipos existentes
       NEW = "new"
   ```

## Mejores Prácticas

1. **Siempre validar configuraciones** antes de crear conectores
2. **Manejar errores de conexión** apropiadamente
3. **Desconectar recursos** después del uso
4. **Usar connection pooling** para conectores que lo soporten
5. **Implementar timeouts** para evitar bloqueos
6. **Logging apropiado** para debugging
7. **Tests unitarios** para nuevos conectores

## Troubleshooting

### Problemas Comunes

1. **"Unsupported target type"**: Verificar que el tipo esté en TargetType enum
2. **"Invalid configuration"**: Revisar campos requeridos para el tipo
3. **Conexión falla**: Verificar conectividad de red y credenciales
4. **Envío falla**: Verificar formato de payload y permisos

### Debug

```python
# Habilitar logging detallado
import logging
logging.basicConfig(level=logging.DEBUG)

# Verificar configuración
schema = ConnectorFactory.get_config_schema(target_type)
print(f"Schema: {schema}")

# Probar conexión paso a paso
connector = ConnectorFactory.create_connector(target_type, config)
connected = await connector.connect()
print(f"Connected: {connected}")
```