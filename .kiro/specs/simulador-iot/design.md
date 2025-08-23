# Design Document - Simulador de Dispositivos IoT

## Overview

El simulador de dispositivos IoT es una aplicación web moderna que permite generar datos de telemetría sintéticos en tiempo real. La solución utiliza una arquitectura desacoplada con React en el frontend y FastAPI en el backend, diseñada para escalar desde unos pocos dispositivos hasta miles de simuladores concurrentes.

### Principios de Diseño

1. **Separación de Responsabilidades**: Frontend para UI/UX, Backend para lógica de negocio y simulación
2. **Escalabilidad Asíncrona**: Uso de asyncio para manejar miles de dispositivos concurrentes
3. **Flexibilidad de Datos**: Soporte tanto para generación visual como programática de payloads
4. **Streaming First**: No almacenamiento de telemetría, transmisión directa a destinos
5. **Containerización**: Despliegue completo con Docker para portabilidad
6. **Portabilidad**: expotación e importación de proyectos con todos sus dispositivos y payloads

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Pages     │  │ Components  │  │      Services       │  │
│  │             │  │             │  │   (API Clients)     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                         HTTP/WebSocket
                              │
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Controllers │  │   Services  │  │    Repositories     │  │
│  │   (API)     │  │  (Business  │  │   (Data Access)     │  │
│  │             │  │    Logic)   │  │                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Simulation  │  │   Target    │  │     Payload         │  │
│  │   Engine    │  │  Connectors │  │   Generators        │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
              ┌─────────────┐    ┌─────────────┐
              │   Config    │    │  Simulation │
              │ Storage     │    │   State     │
              │ (SQLite)    │    │ (In-Memory) │
              └─────────────┘    └─────────────┘
```

### Technology Stack

**Frontend:**
- React 18 con hooks y functional components
- shadcn/ui para componentes UI consistentes
- Tailwind CSS para estilos utilitarios
- Zustand para state management ligero
- React Query para data fetching y cache
- Monaco Editor para editor de código Python
- WebSocket client para actualizaciones en tiempo real

**Backend:**
- FastAPI para APIs REST de alto rendimiento
- SQLAlchemy + Alembic para ORM y migraciones
- SQLite para persistencia de configuración (MVP)
- Pydantic para validación de datos
- asyncio para programación asíncrona
- Librerías específicas: paho-mqtt, aiohttp, aiokafka, websockets

## Components and Interfaces

### Frontend Components

#### 1. Project Management
```typescript
interface Project {
  id: string;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
  devices: Device[];
  is_running: boolean;
}

// Componentes principales
- ProjectList: Lista de proyectos con acciones CRUD
- ProjectForm: Formulario para crear/editar proyectos
- ProjectDetail: Vista detallada con dispositivos y configuración
- ProjectExport: Modal para exportar proyectos
```

#### 2. Device Configuration
```typescript
interface Device {
  id: string;
  project_id: string;
  name: string;
  metadata: Record<string, any>;
  payload_id: string;
  target_system_id: string;
  send_interval: number; // segundos
  is_enabled: boolean;
}

// Componentes principales
- DeviceList: Lista de dispositivos por proyecto
- DeviceForm: Formulario de configuración de dispositivo
- DeviceMetadataEditor: Editor de metadata personalizada
```

#### 3. Payload Builder
```typescript
interface PayloadSchema {
  id: string;
  name: string;
  type: 'visual' | 'python';
  schema?: JSONSchema; // Para tipo visual
  python_code?: string; // Para tipo python
}

interface JSONSchema {
  fields: JSONField[];
}

interface JSONField {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'object' | 'array';
  generator: FieldGenerator;
}

// Componentes principales
- PayloadBuilder: Constructor visual drag-and-drop
- FieldEditor: Editor de campos individuales
- PythonCodeEditor: Editor Monaco para código Python
- PayloadPreview: Vista previa del JSON generado
```

#### 4. Target Systems
```typescript
interface TargetSystem {
  id: string;
  name: string;
  type: 'mqtt' | 'http' | 'kafka' | 'websocket' | 'ftp' | 'pubsub';
  config: TargetConfig;
}

// Configuraciones específicas por tipo
interface MQTTConfig {
  host: string;
  port: number;
  topic: string;
  username?: string;
  password?: string;
  use_tls: boolean;
}

// Componentes principales
- TargetSystemList: Lista de sistemas configurados
- TargetSystemForm: Formulario dinámico según tipo
- ConnectionTester: Prueba de conectividad
```

#### 5. Simulation Control
```typescript
interface SimulationStatus {
  project_id: string;
  is_running: boolean;
  active_devices: number;
  messages_sent: number;
  last_activity: string;
  errors: SimulationError[];
}

// Componentes principales
- SimulationDashboard: Panel de control principal
- DeviceStatusGrid: Estado de dispositivos individuales
- LogViewer: Visualización de logs en tiempo real
- SimulationControls: Botones start/stop/pause
```

### Backend Services

#### 1. Simulation Engine
```python
class SimulationEngine:
    """Orquestador principal de simulaciones"""
    
    def __init__(self):
        self.running_projects: Dict[str, SimulationProject] = {}
        self.observers: List[SimulationObserver] = []
    
    async def start_project(self, project_id: str) -> bool:
        """Inicia simulación de un proyecto"""
        
    async def stop_project(self, project_id: str) -> bool:
        """Detiene simulación de un proyecto"""
        
    async def get_project_status(self, project_id: str) -> SimulationStatus:
        """Obtiene estado actual de simulación"""

class SimulationProject:
    """Representa un proyecto en ejecución"""
    
    def __init__(self, project_config: Project):
        self.config = project_config
        self.device_simulators: List[DeviceSimulator] = []
        self.tasks: List[asyncio.Task] = []
        self.is_running = False
    
    async def start_all_devices(self):
        """Inicia todos los dispositivos del proyecto"""
        
    async def stop_all_devices(self):
        """Detiene todos los dispositivos del proyecto"""
```

#### 2. Device Simulator
```python
class DeviceSimulator:
    """Simula un dispositivo IoT individual"""
    
    def __init__(
        self,
        device_config: Device,
        payload_generator: PayloadGenerator,
        target_connector: TargetConnector
    ):
        self.config = device_config
        self.payload_generator = payload_generator
        self.connector = target_connector
        self.is_running = False
        self.stats = DeviceStats()
    
    async def run(self):
        """Bucle principal del dispositivo"""
        while self.is_running:
            try:
                # Generar payload
                payload = await self.payload_generator.generate(
                    device_metadata=self.config.metadata
                )
                
                # Enviar a destino
                success = await self.connector.send(payload)
                
                # Actualizar estadísticas
                self.stats.update(success)
                
                # Notificar observers
                await self._notify_observers(payload, success)
                
                # Esperar intervalo
                await asyncio.sleep(self.config.send_interval)
                
            except Exception as e:
                await self._handle_error(e)
```

#### 3. Payload Generators
```python
class PayloadGenerator(ABC):
    """Interfaz base para generadores de payload"""
    
    @abstractmethod
    async def generate(self, device_metadata: Dict = None) -> Dict:
        """Genera un payload JSON"""
        pass

class VisualPayloadGenerator(PayloadGenerator):
    """Generador basado en esquema visual"""
    
    def __init__(self, schema: JSONSchema):
        self.schema = schema
        self.field_generators = self._build_generators()
    
    async def generate(self, device_metadata: Dict = None) -> Dict:
        """Aplica reglas del schema para generar JSON"""
        result = {}
        
        for field in self.schema.fields:
            generator = self.field_generators[field.name]
            result[field.name] = await generator.generate()
        
        # Sobrescribir con metadata del dispositivo si aplica
        if device_metadata:
            result.update(device_metadata)
            
        return result

class PythonPayloadGenerator(PayloadGenerator):
    """Generador basado en código Python personalizado"""
    
    def __init__(self, python_code: str):
        self.code = python_code
        self.executor = SafePythonExecutor()
    
    async def generate(self, device_metadata: Dict = None) -> Dict:
        """Ejecuta código Python del usuario"""
        context = {
            'device_metadata': device_metadata or {},
            'datetime': datetime,
            'random': random,
            'uuid': uuid,
            'math': math
        }
        
        return await self.executor.execute(self.code, context)
```

#### 4. Target Connectors
```python
class TargetConnector(ABC):
    """Interfaz base para conectores de destino"""
    
    @abstractmethod
    async def connect(self) -> bool:
        """Establece conexión con el destino"""
        pass
    
    @abstractmethod
    async def send(self, payload: Dict) -> bool:
        """Envía payload al destino"""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Cierra conexión"""
        pass

class MQTTConnector(TargetConnector):
    """Conector para brokers MQTT"""
    
    def __init__(self, config: MQTTConfig):
        self.config = config
        self.client = None
    
    async def connect(self) -> bool:
        """Conecta al broker MQTT"""
        self.client = mqtt.Client()
        
        if self.config.username:
            self.client.username_pw_set(
                self.config.username, 
                self.config.password
            )
        
        if self.config.use_tls:
            self.client.tls_set()
        
        await self.client.connect(self.config.host, self.config.port)
        return True
    
    async def send(self, payload: Dict) -> bool:
        """Publica mensaje en tópico MQTT"""
        message = json.dumps(payload)
        result = self.client.publish(self.config.topic, message)
        return result.rc == mqtt.MQTT_ERR_SUCCESS

class HTTPConnector(TargetConnector):
    """Conector para endpoints HTTP/HTTPS"""
    
    def __init__(self, config: HTTPConfig):
        self.config = config
        self.session = None
    
    async def connect(self) -> bool:
        """Inicializa sesión HTTP"""
        self.session = aiohttp.ClientSession(
            headers=self.config.headers,
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return True
    
    async def send(self, payload: Dict) -> bool:
        """Envía POST request con payload"""
        try:
            async with self.session.post(
                self.config.url,
                json=payload
            ) as response:
                return response.status < 400
        except Exception:
            return False
```

## Data Models

### Database Schema (SQLAlchemy)

```python
class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    devices = relationship("Device", back_populates="project", cascade="all, delete-orphan")

class Device(Base):
    __tablename__ = "devices"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    name = Column(String, nullable=False)
    metadata = Column(JSON, default=dict)
    payload_id = Column(String, ForeignKey("payloads.id"))
    target_system_id = Column(String, ForeignKey("target_systems.id"))
    send_interval = Column(Integer, default=10)  # segundos
    is_enabled = Column(Boolean, default=True)
    
    # Relaciones
    project = relationship("Project", back_populates="devices")
    payload = relationship("Payload")
    target_system = relationship("TargetSystem")

class Payload(Base):
    __tablename__ = "payloads"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    type = Column(Enum(PayloadType), nullable=False)  # 'visual' | 'python'
    schema = Column(JSON)  # Para tipo visual
    python_code = Column(Text)  # Para tipo python
    created_at = Column(DateTime, default=datetime.utcnow)

class TargetSystem(Base):
    __tablename__ = "target_systems"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, unique=True)
    type = Column(Enum(TargetType), nullable=False)
    config = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### API Models (Pydantic)

```python
class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None

class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    devices: List[DeviceResponse] = []
    is_running: bool = False

class DeviceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    payload_id: str
    target_system_id: str
    send_interval: int = Field(default=10, ge=1, le=3600)
    is_enabled: bool = True

class PayloadCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: PayloadType
    schema: Optional[Dict] = None
    python_code: Optional[str] = None
    
    @validator('schema')
    def validate_schema(cls, v, values):
        if values.get('type') == PayloadType.VISUAL and not v:
            raise ValueError('Schema is required for visual payloads')
        return v
    
    @validator('python_code')
    def validate_python_code(cls, v, values):
        if values.get('type') == PayloadType.PYTHON and not v:
            raise ValueError('Python code is required for python payloads')
        return v
```

## Error Handling

### Error Categories

1. **Validation Errors**: Datos de entrada inválidos
2. **Connection Errors**: Fallos de conectividad con destinos
3. **Execution Errors**: Errores en generación de payloads o envío
4. **System Errors**: Errores internos del sistema

### Error Response Format

```python
class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Ejemplo de uso
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error="VALIDATION_ERROR",
            message="Invalid input data",
            details=exc.errors()
        ).dict()
    )
```

### Resilience Patterns

1. **Circuit Breaker**: Para conexiones a destinos externos
2. **Retry Logic**: Reintentos con backoff exponencial
3. **Timeout Handling**: Timeouts configurables por tipo de destino
4. **Graceful Degradation**: Continuar simulación aunque algunos dispositivos fallen

## Testing Strategy

### Unit Testing
- **Frontend**: Jest + React Testing Library para componentes
- **Backend**: pytest para servicios, repositorios y conectores
- **Payload Generators**: Tests para validar generación correcta
- **Target Connectors**: Tests con mocks para cada protocolo

### Integration Testing
- **API Endpoints**: Tests end-to-end de APIs REST
- **Database Operations**: Tests de persistencia y consultas
- **Simulation Engine**: Tests de orquestación completa
- **WebSocket Communication**: Tests de comunicación en tiempo real

### Performance Testing
- **Load Testing**: Simulación con miles de dispositivos
- **Memory Usage**: Monitoreo de uso de memoria durante simulación
- **Connection Pooling**: Eficiencia de reutilización de conexiones
- **Async Performance**: Medición de throughput asíncrono

### Security Testing
- **Python Code Execution**: Validación de sandboxing seguro
- **Input Validation**: Tests de inyección y datos maliciosos
- **Connection Security**: Validación de TLS/SSL en conectores
- **Authentication**: Tests de autenticación cuando se implemente

## Deployment Architecture

### Docker Configuration

```dockerfile
# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```dockerfile
# Frontend Dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
```

### Docker Compose

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./data/app.db
      - CORS_ORIGINS=http://localhost:3000
    volumes:
      - ./data:/app/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
    environment:
      - REACT_APP_API_URL=http://localhost:8000

  # Servicios opcionales para desarrollo/testing
  mosquitto:
    image: eclipse-mosquitto:2.0
    ports:
      - "1883:1883"
      - "9001:9001"
    volumes:
      - ./mosquitto.conf:/mosquitto/config/mosquitto.conf

  kafka:
    image: confluentinc/cp-kafka:latest
    environment:
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
    ports:
      - "9092:9092"
    depends_on:
      - zookeeper

  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
    ports:
      - "2181:2181"
```

### Environment Configuration

```python
class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./data/app.db"
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000"]
    
    # Security
    secret_key: str = "your-secret-key-here"
    
    # Simulation limits
    max_devices_per_project: int = 1000
    max_concurrent_projects: int = 10
    
    # Performance
    connection_pool_size: int = 100
    request_timeout: int = 30
    
    class Config:
        env_file = ".env"
```

Este diseño proporciona una base sólida para implementar el simulador IoT con todas las funcionalidades requeridas, manteniendo flexibilidad para futuras extensiones y optimizaciones de rendimiento.