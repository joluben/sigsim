# IoT Device Simulator

Una aplicación web moderna para simular dispositivos IoT enviando datos de telemetría en tiempo real a múltiples sistemas de destino.

## 🚀 Características

- **Gestión de Proyectos**: Organiza simulaciones en proyectos independientes
- **Dispositivos Virtuales**: Configura múltiples dispositivos con metadata personalizada
- **Generación de Payloads**: Constructor visual JSON o código Python personalizado
- **Múltiples Destinos**: MQTT, HTTP, Kafka, WebSocket, FTP, Pub/Sub
- **Simulación Escalable**: Soporte para miles de dispositivos concurrentes
- **Logs en Tiempo Real**: Monitoreo de mensajes enviados via WebSocket
- **Arquitectura Moderna**: React + FastAPI + Docker

## 🏗 Arquitectura

```
Frontend (React) ←→ Backend (FastAPI) ←→ Target Systems
     ↓                    ↓
  shadcn/ui         Simulation Engine
  Tailwind CSS      Payload Generators
  Zustand           Target Connectors
```

## 🛠 Tecnologías

### Backend
- **FastAPI**: Framework web de alto rendimiento
- **SQLAlchemy**: ORM para base de datos
- **SQLite**: Base de datos (MVP)
- **asyncio**: Programación asíncrona
- **paho-mqtt**: Cliente MQTT
- **aiohttp**: Cliente HTTP asíncrono
- **aiokafka**: Cliente Kafka asíncrono

### Frontend
- **React 18**: Framework UI
- **shadcn/ui**: Componentes UI
- **Tailwind CSS**: Framework CSS
- **Zustand**: State management
- **React Query**: Data fetching
- **Monaco Editor**: Editor de código

## 🚀 Inicio Rápido

### Prerrequisitos
- Docker y Docker Compose
- Node.js 18+ (para desarrollo)
- Python 3.11+ (para desarrollo)

### Instalación con Docker

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd iot-simulator
```

2. **Iniciar con Docker Compose**
```bash
docker-compose up -d
```

3. **Acceder a la aplicación**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Documentación API: http://localhost:8000/docs

### Desarrollo Local

#### Setup Completo
```bash
# Usar el Makefile para ver comandos disponibles
make help

# O seguir setup manual:
```

#### Backend
```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements-dev.txt
make run  # o uvicorn app.main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

#### Herramientas de Desarrollo
```bash
# Linting
make lint           # Todo el código
make backend-lint   # Solo backend
make frontend-lint  # Solo frontend

# Formatting
make format         # Todo el código
make backend-format # Solo backend
make frontend-format # Solo frontend

# Testing
make test           # Todos los tests
make backend-test   # Solo backend
make frontend-test  # Solo frontend

# Pre-commit hooks
pre-commit install
pre-commit run --all-files
```

## 📖 Uso

### 1. Crear un Proyecto
- Ve a la página de proyectos
- Haz clic en "Nuevo Proyecto"
- Asigna un nombre y descripción

### 2. Configurar Target Systems
- Ve a "Target Systems"
- Crea destinos (MQTT, HTTP, etc.)
- Configura credenciales y parámetros

### 3. Crear Payloads
- Ve a "Payloads"
- Usa el constructor visual o código Python
- Define la estructura de datos JSON

### 4. Agregar Dispositivos
- En tu proyecto, agrega dispositivos
- Asigna payload y target system
- Configura metadata y frecuencia de envío

### 5. Ejecutar Simulación
- Ve a la página de simulación
- Inicia el proyecto
- Monitorea logs en tiempo real

## 🔧 Configuración

### Variables de Entorno

Crea un archivo `.env` en el directorio `backend/`:

```env
DATABASE_URL=sqlite:///./data/app.db
CORS_ORIGINS=http://localhost:3000
SECRET_KEY=your-secret-key-here
MAX_DEVICES_PER_PROJECT=1000
MAX_CONCURRENT_PROJECTS=10
```

### Target Systems Soportados

#### MQTT
```json
{
  "host": "broker.hivemq.com",
  "port": 1883,
  "topic": "iot/devices/data",
  "username": "optional",
  "password": "optional",
  "use_tls": false,
  "qos": 0
}
```

#### HTTP
```json
{
  "url": "https://api.example.com/telemetry",
  "method": "POST",
  "headers": {
    "Authorization": "Bearer token",
    "Content-Type": "application/json"
  },
  "timeout": 30
}
```

#### Kafka
```json
{
  "bootstrap_servers": "localhost:9092",
  "topic": "iot-telemetry",
  "security_protocol": "PLAINTEXT"
}
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📊 Monitoreo

La aplicación incluye:
- **Health Check**: `/health` endpoint
- **Métricas**: Dispositivos activos, mensajes enviados
- **Logs**: Eventos de simulación en tiempo real
- **Estado**: Estado de cada dispositivo individual

## 🔒 Seguridad

- **Sandboxing**: Ejecución segura de código Python
- **Validación**: Validación de entrada en todos los endpoints
- **CORS**: Configuración de orígenes permitidos
- **Rate Limiting**: Límites de dispositivos y proyectos

## 🚀 Despliegue en Producción

### Docker Compose (Recomendado)
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes
Ver archivos de configuración en `/k8s/`

### Variables de Producción
- Cambiar `SECRET_KEY`
- Configurar base de datos externa (PostgreSQL)
- Configurar reverse proxy (nginx)
- Habilitar HTTPS

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🆘 Soporte

- **Documentación**: Ver `/docs`
- **Issues**: GitHub Issues
- **Discusiones**: GitHub Discussions

## 🗺 Roadmap

- [ ] Autenticación de usuarios
- [ ] Métricas avanzadas y dashboards
- [ ] Simulación bidireccional (comandos)
- [ ] Templates de dispositivos
- [ ] Integración con cloud providers
- [ ] API para automatización
- [ ] Simulación de fallos de red
- [ ] Escalamiento horizontal