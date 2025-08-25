# Implementation Plan - Simulador de Dispositivos IoT

## 1. Setup del Proyecto y Estructura Base

- [x] 1.1 Configurar estructura de directorios del proyecto
  - Crear estructura backend con FastAPI siguiendo Clean Architecture
  - Crear estructura frontend con React y configuración de shadcn/ui
  - Configurar Docker y docker-compose para desarrollo
  - _Requirements: 9.1, 9.2, 9.3, 9.4_

- [x] 1.2 Configurar herramientas de desarrollo y CI/CD básico
  - Configurar linting, formatting y pre-commit hooks
  - Configurar pytest para backend y Jest para frontend
  - Crear Dockerfiles optimizados para desarrollo y producción
  - _Requirements: 9.1, 9.2, 9.3_

## 2. Backend Core - Modelos y Persistencia

- [x] 2.1 Implementar modelos de datos y configuración de base de datos
  - Crear modelos SQLAlchemy para Project, Device, Payload, TargetSystem
  - Configurar SQLite y Alembic para migraciones
  - Implementar modelos Pydantic para validación de APIs
  - _Requirements: 8.1, 8.2, 8.3_

- [x] 2.2 Implementar repositorios y servicios base
  - Crear BaseRepository con operaciones CRUD genéricas
  - Implementar repositorios específicos para cada entidad
  - Crear servicios de negocio con validaciones
  - _Requirements: 5.1, 5.2, 8.1_

- [x] 2.3 Crear APIs REST básicas para gestión de entidades
  - Implementar endpoints CRUD para proyectos
  - Implementar endpoints CRUD para dispositivos
  - Implementar endpoints CRUD para payloads y target systems
  - Configurar manejo de errores y validaciones
  - _Requirements: 5.1, 5.2, 5.3_

## 3. Frontend Core - Componentes Base y Navegación

- [x] 3.1 Configurar React con shadcn/ui y routing
  - Configurar React Router para navegación
  - Implementar layout base con navegación
  - Configurar Tailwind CSS y componentes shadcn/ui
  - Configurar Zustand para state management
  - _Requirements: 1.1, 1.3_

- [x] 3.2 Implementar servicios de API y hooks personalizados
  - Crear cliente HTTP con axios/fetch para comunicación con backend
  - Implementar React Query para data fetching y cache
  - Crear hooks personalizados para cada entidad (useProjects, useDevices, etc.)
  - _Requirements: 1.1, 1.5_

- [x] 3.3 Crear componentes base para gestión de proyectos
  - Implementar ProjectForm para crear/editar proyectos
  - Completar ProjectDetail con vista de dispositivos
  - Agregar validación de formularios con React Hook Form
  - Integrar notificaciones en ProjectsPage (useNotificationContext missing)
  - _Requirements: 1.1, 1.2, 1.4, 3.4_

## 4. Gestión de Dispositivos

- [x] 4.1 Implementar componentes para gestión de dispositivos
  - Completar DeviceList con tabla filtrable y paginación
  - Implementar DeviceForm con campos para metadata, payload y target
  - Crear DeviceMetadataEditor para edición de propiedades personalizadas
  - _Requirements: 3.1, 3.2, 3.4_

- [x] 4.2 Integrar dispositivos con proyectos
  - Conectar dispositivos con proyectos en la UI
  - Implementar asignación de payloads y target systems
  - Crear validaciones para configuración de dispositivos
  - _Requirements: 3.1, 3.2, 3.4_

## 5. Sistema de Target Systems (Destinos)

- [x] 5.1 Implementar conectores base para sistemas de destino
  - [x] Crear interfaz base TargetConnector con métodos connect/send/disconnect
  - [x] Implementar HTTPConnector para endpoints REST
  - [x] Crear sistema de factory para instanciar conectores según tipo
  - _Requirements: 6.2, 6.7_

- [x] 5.2 Implementar conector MQTT
  - [x] Crear MQTTConnector usando paho-mqtt
  - [x] Implementar configuración de host, puerto, tópico y credenciales
  - [x] Agregar soporte para TLS/SSL y QoS
  - [x] Integrar conector MQTT con el sistema de factory
  - _Requirements: 6.1, 6.7_

- [x] 5.3 Crear sistema de factory para conectores
  - Implementar ConnectorFactory para instanciar conectores según tipo
  - Crear método get_connector que reciba configuración y retorne conector apropiado
  - Integrar factory con el motor de simulación
  - _Requirements: 6.2, 6.7_

- [x] 5.4 Crear UI para configuración de target systems
  - Implementar TargetSystemList con tipos soportados
  - Crear TargetSystemForm dinámico según tipo seleccionado
  - Agregar ConnectionTester para validar conectividad
  - _Requirements: 3.1, 3.2, 3.3, 3.5_

## 6. JSON Schema Builder - Constructor Visual de Payloads

- [ ] 6.1 Configuración e infraestructura del JSON Schema Builder
  - [x] 6.1.1 Inicializar módulo JSON Schema Builder en la app existente
    - Crear estructura de carpetas: `components/SchemaBuilder/`
    - Instalar dependencias: Ajv para validación, Monaco Editor, @dnd-kit para drag-and-drop
    - Configurar tipos TypeScript para JSONSchemaField, RandomRules, etc.
    - _Requirements: 2.1, 2.8, 2.12_

  - [x] 6.1.2 Crear interfaces y tipos base del sistema
    - Definir interfaces JSONSchemaField, RandomRules, JSONSchemaTemplate
    - Crear tipos para generadores de campo específicos por tipo de dato
    - Implementar validaciones Zod para formularios del constructor
    - _Requirements: 2.2, 2.3, 2.1.1_

- [ ] 6.2 Componente principal y layout del Schema Builder
  - [x] 6.2.1 Implementar componente principal JSONSchemaBuilder
    - Crear layout principal con dos paneles: editor visual y vista previa JSON
    - Implementar barra de herramientas con botones Guardar, Validar, Cargar, Exportar
    - Configurar sistema de pestañas para alternar entre vista visual y JSON
    - _Requirements: 2.1, 2.8, 2.1.9_

  - [x] 6.2.2 Crear sistema de navegación y estado del builder
    - Implementar Zustand store para estado del schema en construcción
    - Crear contexto React para compartir estado entre componentes
    - Agregar sistema de undo/redo para cambios en el schema
    - _Requirements: 2.8, 2.9, 2.11_

- [ ] 6.3 Editor visual de campos (SchemaVisualEditor)
  - [ ] 6.3.1 Implementar listado de campos definidos
    - Crear FieldList component con shadcn/ui cards para mostrar campos
    - Mostrar nombre, tipo, valor fijo/aleatorio y acciones (editar/eliminar)
    - Implementar drag-and-drop para reordenar campos usando @dnd-kit
    - _Requirements: 2.2, 2.3, 2.12, 2.1.11_

  - [ ] 6.3.2 Crear formulario de configuración de campos
    - Implementar FieldConfigPanel con React Hook Form y shadcn/ui
    - Crear FieldTypeSelector con iconos para cada tipo de dato
    - Agregar toggle para valor fijo vs aleatorio con validación condicional
    - _Requirements: 2.2, 2.3, 2.4, 2.1.4_

  - [ ] 6.3.3 Implementar configuración de valores fijos
    - Crear inputs específicos por tipo: text, number, date picker, boolean toggle
    - Implementar validación en tiempo real según el tipo seleccionado
    - Agregar preview del valor fijo en el formulario
    - _Requirements: 2.4, 2.1.5_

- [ ] 6.4 Sistema de reglas de generación aleatoria
  - [ ] 6.4.1 Crear RandomRulesEditor para configuración de reglas
    - Implementar formularios específicos por tipo de dato con shadcn/ui
    - Para strings: campos pattern (regex), minLength, maxLength
    - Para números: campos minimum, maximum, multipleOf, exclusiveMinimum/Maximum
    - Para fechas: date pickers para minDate y maxDate
    - _Requirements: 2.5, 2.1.1, 2.1.2, 2.1.3_

  - [ ] 6.4.2 Agregar validación de reglas de generación
    - Validar que maximum >= minimum para números
    - Validar que maxLength >= minLength para strings
    - Validar patrones regex y mostrar errores específicos
    - Validar rangos de fechas lógicos
    - _Requirements: 2.9, 2.1.8_

  - [ ] 6.4.3 Implementar preview de reglas aleatorias
    - Crear SampleGenerator para mostrar ejemplos de valores generados
    - Mostrar múltiples muestras para que el usuario vea la variabilidad
    - Actualizar preview en tiempo real al cambiar reglas
    - _Requirements: 2.1.6_

- [ ] 6.5 Soporte para estructuras complejas (objetos y arrays)
  - [ ] 6.5.1 Implementar NestedObjectEditor para objetos anidados
    - Crear interfaz recursiva para agregar subcampos dentro de objetos
    - Implementar navegación breadcrumb para niveles de anidamiento
    - Agregar validación de nombres únicos dentro del mismo nivel
    - _Requirements: 2.6, 2.1.12_

  - [ ] 6.5.2 Crear ArrayItemEditor para configuración de arrays
    - Implementar selector de tipo para elementos del array
    - Agregar configuración de minItems y maxItems
    - Permitir definir esquemas complejos para elementos (objetos anidados)
    - _Requirements: 2.7, 2.1.1_

  - [ ] 6.5.3 Agregar visualización jerárquica de estructuras complejas
    - Crear TreeView component para mostrar estructura anidada
    - Implementar collapse/expand para objetos y arrays
    - Agregar indicadores visuales de profundidad y tipo
    - _Requirements: 2.6, 2.7_

- [ ] 6.6 Vista previa y validación en tiempo real
  - [ ] 6.6.1 Implementar SchemaPreview con Monaco Editor
    - Integrar Monaco Editor para mostrar JSON Schema generado
    - Configurar syntax highlighting y formateo automático
    - Actualizar preview en tiempo real al modificar campos
    - _Requirements: 2.8, 2.14_

  - [ ] 6.6.2 Crear sistema de validación con Ajv
    - Implementar JSONSchemaValidator usando biblioteca Ajv
    - Mostrar errores de validación con mensajes específicos y ubicación
    - Resaltar campos problemáticos en el editor visual
    - _Requirements: 2.9, 2.1.7, 2.1.8_

  - [ ] 6.6.3 Agregar generación de datos de muestra
    - Implementar SampleDataGenerator basado en el schema construido
    - Mostrar múltiples ejemplos de datos generados
    - Permitir regenerar muestras para validar reglas aleatorias
    - _Requirements: 2.1.6_

- [ ] 6.7 Persistencia y gestión de plantillas
  - [ ] 6.7.1 Implementar sistema de guardado y carga
    - Crear funcionalidad para guardar schema en base de datos
    - Implementar carga de schemas existentes y reconstrucción de UI
    - Agregar validación de integridad al cargar schemas
    - _Requirements: 2.10, 2.11_

  - [ ] 6.7.2 Crear sistema de plantillas reutilizables
    - Implementar SchemaTemplateManager para CRUD de plantillas
    - Agregar categorización de plantillas (IoT, Web, Mobile, etc.)
    - Crear galería de plantillas predefinidas comunes
    - _Requirements: 2.1.12_

  - [ ] 6.7.3 Agregar funcionalidades de importación/exportación
    - Implementar importación de JSON Schema estándar existente
    - Crear exportación a JSON Schema válido según especificación
    - Agregar funcionalidad de duplicar campos existentes
    - _Requirements: 2.1.9, 2.1.10, 2.1.11_

- [ ] 6.8 Editor de código Python integrado (alternativa avanzada)
  - [ ] 6.8.1 Implementar PythonCodeEditor con Monaco
    - Integrar Monaco Editor con syntax highlighting para Python
    - Configurar autocompletado y validación básica de sintaxis
    - Crear sistema de preview para código Python personalizado
    - _Requirements: 2.13, 2.14_

  - [ ] 6.8.2 Crear sistema de ejecución segura de Python
    - Implementar SafePythonExecutor con sandboxing y timeout
    - Agregar contexto predefinido (datetime, random, uuid, math, faker)
    - Crear validador de código Python para detectar código malicioso
    - _Requirements: 2.13, 7.5_

- [ ] 6.9 Backend APIs para JSON Schema Builder
  - [ ] 6.9.1 Implementar APIs de validación y conversión
    - Crear endpoint POST /api/schema/validate para validar campos
    - Implementar POST /api/schema/convert-to-standard para generar JSON Schema
    - Agregar POST /api/schema/generate-sample para datos de muestra
    - _Requirements: 2.1.7, 2.1.6, 2.1.9_

  - [ ] 6.9.2 Crear APIs para gestión de plantillas
    - Implementar CRUD completo para plantillas (/api/schema/templates)
    - Agregar filtrado por categoría y búsqueda de plantillas
    - Crear endpoint para importar/exportar JSON Schema estándar
    - _Requirements: 2.1.12, 2.1.9, 2.1.10_

- [ ] 6.10 Generadores de payload basados en JSON Schema
  - [ ] 6.10.1 Implementar JSONSchemaPayloadGenerator
    - Crear generador que procese campos visuales y produzca JSON
    - Implementar generadores específicos: StringGenerator, NumberGenerator, etc.
    - Agregar soporte para objetos anidados y arrays con ObjectGenerator y ArrayGenerator
    - _Requirements: 7.4, 2.5, 2.6, 2.7_

  - [ ] 6.10.2 Integrar generadores con motor de simulación
    - Conectar JSONSchemaPayloadGenerator con DeviceSimulator
    - Implementar generación periódica según reglas definidas
    - Agregar manejo de metadata de dispositivo en payloads generados
    - _Requirements: 7.4, 7.5_

## 7. Motor de Simulación

- [x] 7.1 Implementar SimulationEngine core
  - Crear SimulationEngine para orquestar proyectos
  - Implementar SimulationProject para manejar dispositivos de un proyecto
  - Crear DeviceSimulator para simular dispositivos individuales
  - _Requirements: 7.1, 7.2, 7.3_

- [x] 7.2 Integrar generadores de payload con simuladores
  - Conectar PayloadGenerators con DeviceSimulator
  - Implementar generación periódica según intervalo configurado
  - Agregar manejo de metadata de dispositivo en payloads
  - _Requirements: 7.4, 7.5_

- [x] 7.3 Integrar conectores de destino con simuladores
  - Conectar TargetConnectors con DeviceSimulator
  - Implementar envío asíncrono de datos a destinos
  - Agregar manejo de errores y reintentos
  - _Requirements: 7.3, 7.4_

- [x] 7.4 Crear APIs de control de simulación
  - Implementar endpoints para start/stop de proyectos
  - Crear endpoint para obtener estado de simulación
  - Agregar WebSocket para notificaciones en tiempo real
  - _Requirements: 5.4, 7.1, 7.2_

## 8. UI de Control de Simulación

- [x] 8.1 Implementar dashboard de simulación
  - Crear SimulationDashboard con controles start/stop
  - Implementar DeviceStatusGrid para mostrar estado de dispositivos
  - Agregar indicadores visuales de estado (activo/inactivo/error)
  - _Requirements: 4.1, 4.4_

- [x] 8.2 Crear sistema de logs en tiempo real
  - Implementar LogViewer para mostrar mensajes enviados
  - Configurar WebSocket client para actualizaciones en tiempo real
  - Crear buffer temporal para logs sin persistencia
  - _Requirements: 4.2, 4.3, 10.4_

- [x] 8.3 Agregar notificaciones y manejo de errores
  - Implementar sistema de notificaciones para errores de simulación
  - Crear alertas visuales para fallos de conectividad
  - Agregar tooltips y ayuda contextual
  - _Requirements: 4.5, 3.5_

## 9. Conectores Adicionales

- [ ] 9.1 Implementar conector Kafka
  - [x] Crear KafkaConnector usando aiokafka
  - [x] Configurar bootstrap servers, tópicos y configuración SSL
  - [x] Agregar manejo de particiones y keys





  - [x] Integrar conector Kafka con el sistema de factory





  - _Requirements: 6.3, 6.7_

- [ ] 9.2 Implementar conector WebSocket
  - [x] Crear WebSocketConnector para streaming persistente
  - [x] Configurar conexiones ws:// y wss://
  - [x] Implementar reconexión automática




  - [x] Integrar conector WebSocket con el sistema de factory



  - _Requirements: 6.4, 6.7_

- [ ] 9.3 Agregar conectores para colas Pub/Sub y FTP
  - [x] Implementar FTPConnector para transferencia de archivos





  - [ ] Implementar conector genérico para sistemas AMQP
  - [ ] Crear configuración para Google Cloud Pub/Sub
  - [ ] Agregar soporte para Amazon SNS/SQS
  - _Requirements: 6.5, 6.7_

## 10. Funcionalidades Avanzadas

- [ ] 10.1 Implementar exportación de proyectos
  - Crear funcionalidad de export a HTML con configuración completa
  - Implementar serialización de proyectos con dispositivos y payloads
  - Agregar opción de descarga desde la UI
  - _Requirements: 8.4_

- [ ] 10.2 Optimizar rendimiento para simulaciones masivas
  - Implementar connection pooling para conectores
  - Agregar batching de mensajes cuando sea posible
  - Optimizar uso de memoria en simulaciones con miles de dispositivos
  - _Requirements: 7.6, 9.5_

- [ ] 10.3 Agregar métricas y monitoreo
  - Implementar contadores de mensajes enviados por dispositivo
  - Crear métricas de latencia y throughput
  - Agregar dashboard de performance en la UI
  - _Requirements: 7.6_

## 11. Testing y Documentación

- [ ] 11.1 Implementar tests unitarios para backend
  - Completar tests para repositorios y servicios
  - Implementar tests para generadores de payload
  - Agregar tests para conectores con mocks
  - _Requirements: 5.1, 5.2, 6.1, 6.2, 6.3_

- [ ] 11.2 Implementar tests para frontend
  - Crear tests para componentes principales con React Testing Library
  - Implementar tests para hooks personalizados
  - Agregar tests de integración para flujos completos
  - _Requirements: 1.1, 1.2, 1.4_

- [ ] 11.3 Crear tests de integración end-to-end
  - Implementar tests de simulación completa
  - Crear tests de conectividad con servicios externos mock
  - Agregar tests de performance con múltiples dispositivos
  - _Requirements: 7.1, 7.2, 7.3, 7.6_

## 12. Despliegue y Configuración Final

- [x] 12.1 Optimizar configuración de Docker para producción
  - Crear multi-stage builds para imágenes optimizadas
  - Configurar variables de entorno y secrets
  - Implementar health checks y restart policies
  - _Requirements: 9.1, 9.2, 9.3, 9.4_

- [ ] 12.2 Crear documentación de usuario
  - Escribir guía de instalación y configuración
  - Crear tutoriales para casos de uso comunes
  - Documentar APIs y configuración de conectores
  - _Requirements: 9.4_

- [ ] 12.3 Preparar para escalabilidad futura
  - Documentar límites de performance actuales
  - Crear guías para escalamiento horizontal
  - Preparar arquitectura para autenticación multi-usuario
  - _Requirements: 8.5, 9.5_