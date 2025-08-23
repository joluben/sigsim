# Requirements Document

## Introduction

El simulador de dispositivos IoT es una aplicación web que permite a desarrolladores y testers generar flujos de datos de telemetría en tiempo real sin necesidad de hardware físico. La aplicación proporciona una interfaz visual intuitiva para configurar proyectos de simulación, definir dispositivos virtuales, diseñar payloads JSON personalizables, y configurar sistemas de destino donde se enviarán los datos generados. El sistema está diseñado para ser flexible, escalable y soportar miles de dispositivos simulados enviando datos concurrentemente a múltiples plataformas de destino.

## Requirements

## Frontend Requirements

### Requirement 1

**User Story:** Como desarrollador IoT, quiero una interfaz web intuitiva para gestionar proyectos de simulación, para poder crear y organizar diferentes escenarios o proyectos de testing de forma visual.

#### Acceptance Criteria

1. WHEN el usuario accede a la aplicación THEN el sistema SHALL mostrar una interfaz React con componentes shadcn/ui
2. WHEN el usuario crea un proyecto THEN el sistema SHALL mostrar un formulario para asignar nombre descriptivo único
3. WHEN el usuario navega por la aplicación THEN el sistema SHALL mantener una experiencia responsiva en diferentes tamaños de pantalla
4. WHEN el usuario interactúa con formularios THEN el sistema SHALL proporcionar validación en tiempo real
5. WHEN el usuario realiza acciones THEN el sistema SHALL proporcionar feedback visual inmediato

### Requirement 2

**User Story:** Como usuario técnico, quiero un constructor visual de JSON intuitivo, para poder definir payloads complejos sin necesidad de escribir código manualmente.

#### Acceptance Criteria

1. WHEN el usuario define un payload THEN el sistema SHALL ofrecer un constructor visual de JSON con interfaz drag-and-drop
2. WHEN el usuario usa el constructor visual THEN el sistema SHALL permitir agregar campos con nombre, tipo de dato y reglas de generación
3. WHEN el usuario define reglas de generación THEN el sistema SHALL mostrar opciones para números aleatorios, listas predefinidas, UUIDs, timestamps y booleanos
4. WHEN el usuario requiere lógica compleja THEN el sistema SHALL proporcionar un editor de código Python integrado en la interfaz
5. WHEN el usuario escribe código Python THEN el sistema SHALL mostrar syntax highlighting y validación básica

### Requirement 3

**User Story:** Como usuario del simulador, quiero formularios intuitivos para configurar dispositivos y destinos, para poder establecer conexiones sin conocimiento técnico profundo.

#### Acceptance Criteria

1. WHEN el usuario configura un dispositivo THEN el sistema SHALL mostrar formularios para metadata, payload, destino y frecuencia
2. WHEN el usuario configura destinos THEN el sistema SHALL mostrar formularios específicos según el tipo (MQTT, HTTP, Kafka, etc.)
3. WHEN el usuario selecciona un tipo de destino THEN el sistema SHALL mostrar solo los campos relevantes para ese protocolo
4. WHEN el usuario completa formularios THEN el sistema SHALL validar campos requeridos antes de guardar
5. WHEN hay errores de configuración THEN el sistema SHALL mostrar mensajes de error claros y específicos

### Requirement 4

**User Story:** Como tester de sistemas IoT, quiero visualizar en tiempo real el estado de la simulación y los logs de envío, para poder monitorear y debuggear el comportamiento de los dispositivos.

#### Acceptance Criteria

1. WHEN la simulación está activa THEN el sistema SHALL mostrar el estado de cada dispositivo (activo/inactivo)
2. WHEN los dispositivos envían datos THEN el sistema SHALL mostrar logs en tiempo real de los últimos mensajes enviados
3. WHEN hay actualizaciones en tiempo real THEN el sistema SHALL usar WebSockets para notificaciones instantáneas
4. WHEN el usuario inicia/detiene simulación THEN el sistema SHALL mostrar controles claros de play/stop a nivel proyecto
5. WHEN hay errores de envío THEN el sistema SHALL mostrar notificaciones de error en la interfaz

## Backend Requirements

### Requirement 5

**User Story:** Como desarrollador del sistema, quiero una API REST robusta que maneje la lógica de negocio, para poder separar claramente frontend y backend.

#### Acceptance Criteria

1. WHEN el frontend solicita operaciones THEN el sistema SHALL exponer APIs REST con FastAPI
2. WHEN se crean/modifican entidades THEN el sistema SHALL validar datos y retornar respuestas JSON estructuradas
3. WHEN hay errores THEN el sistema SHALL retornar códigos HTTP apropiados y mensajes de error descriptivos
4. WHEN se requiere comunicación en tiempo real THEN el sistema SHALL soportar conexiones WebSocket
5. WHEN se ejecutan operaciones concurrentes THEN el sistema SHALL manejar requests asíncronamente

### Requirement 6

**User Story:** Como administrador de sistemas, quiero que el backend soporte múltiples protocolos de destino, para poder enviar datos a diferentes plataformas IoT.

#### Acceptance Criteria

1. WHEN se configura MQTT THEN el sistema SHALL conectar a brokers con host, puerto, tópico y credenciales
2. WHEN se configura HTTP/HTTPS THEN el sistema SHALL enviar requests con métodos, URLs y headers personalizados
3. WHEN se configura Kafka THEN el sistema SHALL conectar a clusters con configuración de brokers y tópicos
4. WHEN se configura WebSocket THEN el sistema SHALL mantener conexiones persistentes para streaming
5. WHEN se configura FTP/SFTP THEN el sistema SHALL subir archivos con credenciales y rutas específicas
6. WHEN se configuran colas Pub/Sub THEN el sistema SHALL integrar con Google Cloud, Amazon SNS/SQS, AMQP
7. WHEN los destinos requieren autenticación THEN el sistema SHALL manejar tokens, API keys, certificados y credenciales

### Requirement 7

**User Story:** Como usuario del simulador, quiero que el sistema ejecute simulaciones escalables en tiempo real, para poder probar con miles de dispositivos concurrentemente.

#### Acceptance Criteria

1. WHEN se inicia un proyecto THEN el sistema SHALL activar todos los dispositivos habilitados usando tareas asíncronas
2. WHEN se detiene un proyecto THEN el sistema SHALL cancelar inmediatamente todas las tareas de envío
3. WHEN múltiples dispositivos están activos THEN el sistema SHALL manejar el envío concurrente sin bloqueos
4. WHEN un dispositivo envía datos THEN el sistema SHALL generar payload según reglas definidas y enviarlo al destino
5. WHEN se ejecutan funciones Python personalizadas THEN el sistema SHALL ejecutarlas de forma segura y aislada
6. WHEN hay miles de dispositivos THEN el sistema SHALL mantener performance usando programación asíncrona

### Requirement 8

**User Story:** Como usuario del sistema, quiero que mis configuraciones se persistan correctamente, para poder recuperar mi trabajo entre sesiones.

#### Acceptance Criteria

1. WHEN se crean proyectos THEN el sistema SHALL persistir configuración en almacenamiento local
2. WHEN se reinicia la aplicación THEN el sistema SHALL cargar automáticamente configuraciones previas
3. WHEN se modifican configuraciones THEN el sistema SHALL guardar cambios automáticamente
4. WHEN se exporta un proyecto THEN el sistema SHALL generar archivo HTML con toda la configuración
5. WHEN se requiere escalabilidad futura THEN el sistema SHALL estar preparado para base de datos y multi-usuario

## Architecture & System Requirements

### Requirement 9

**User Story:** Como administrador de infraestructura, quiero una arquitectura moderna y escalable, para poder desplegar y mantener la aplicación fácilmente.

#### Acceptance Criteria

1. WHEN se despliega la aplicación THEN el sistema SHALL usar arquitectura separada frontend/backend
2. WHEN se ejecuta el despliegue THEN el sistema SHALL estar completamente contenedorizado con Docker
3. WHEN se orquesta la aplicación THEN el sistema SHALL usar Docker Compose para coordinar servicios
4. WHEN se inicia la aplicación THEN el sistema SHALL estar disponible inmediatamente sin configuración adicional
5. WHEN se escala la aplicación THEN el sistema SHALL soportar múltiples réplicas del backend

### Requirement 10

**User Story:** Como desarrollador del sistema, quiero una arquitectura que no almacene datos de telemetría, para mantener el sistema ligero y enfocado en streaming.

#### Acceptance Criteria

1. WHEN se ejecuta la simulación THEN el sistema SHALL transmitir datos directamente a endpoints externos
2. WHEN se generan mensajes THEN el sistema SHALL NO almacenar datos de telemetría localmente
3. WHEN se requiere persistencia THEN el sistema SHALL almacenar solo configuración de proyectos y destinos
4. WHEN se muestran logs THEN el sistema SHALL mantener solo buffer temporal en memoria para visualización
5. WHEN se reinicia el sistema THEN el sistema SHALL recuperar configuraciones pero no datos históricos de telemetría