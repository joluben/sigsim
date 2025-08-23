# Payload Generator Integration

## Overview

La tarea 7.2 implementa la integración completa de los generadores de payload con los simuladores de dispositivos. Esta integración permite que los dispositivos virtuales generen datos de telemetría usando tanto esquemas visuales como código Python personalizado.

## Components Integrated

### 1. Visual Payload Generator
- **File**: `app/simulation/payload_generators/visual_generator.py`
- **Purpose**: Wrapper que integra el JsonBuilderGenerator con el motor de simulación
- **Usage**: Genera payloads basados en esquemas JSON configurables

### 2. Python Code Generator
- **File**: `app/simulation/payload_generators/python_runner.py`
- **Purpose**: Ejecuta código Python personalizado de forma segura para generar payloads
- **Usage**: Permite lógica compleja de generación de datos

### 3. Enhanced Device Simulator
- **File**: `app/simulation/device_simulator.py`
- **Improvements**:
  - Mejor manejo de metadata de dispositivos
  - Validación de payloads generados
  - Inyección automática de device_id y device_name
  - Manejo robusto de errores con reintentos inteligentes

### 4. Updated Simulation Engine
- **File**: `app/simulation/engine.py`
- **Improvements**:
  - Detección automática del tipo de payload (visual vs python)
  - Instanciación correcta de generadores según configuración
  - Estadísticas mejoradas con datos reales de dispositivos
  - Mejor manejo de errores durante la inicialización

## Integration Flow

```
1. SimulationEngine.start_project()
   ↓
2. Load device configuration from database
   ↓
3. For each device:
   - Load payload configuration
   - Determine payload type (visual/python)
   - Create appropriate PayloadGenerator
   - Create TargetConnector
   - Create DeviceSimulator with both components
   ↓
4. DeviceSimulator.run()
   - Generate payload using PayloadGenerator
   - Add device metadata to payload
   - Send payload using TargetConnector
   - Log results and update statistics
   - Wait for next interval
```

## Key Features Implemented

### Metadata Integration
- Device metadata is automatically passed to payload generators
- Metadata can override generated values
- Device ID and name are automatically injected if not present

### Error Handling
- Invalid Python code is caught during generator creation
- Runtime errors during payload generation are logged
- Intelligent retry delays (shorter than normal interval)
- Graceful degradation when generators fail

### Statistics and Monitoring
- Real-time message counts per device
- Error tracking with last error message
- Device status reporting (running/stopped)
- Project-level aggregated statistics

### Type Safety
- Payload type detection from database configuration
- Validation that generators return dictionary objects
- Proper error messages for configuration issues

## Usage Examples

### Visual Payload Configuration
```json
{
  "type": "visual",
  "schema": {
    "fields": [
      {
        "name": "temperature",
        "type": "number",
        "generator": {
          "type": "random_float",
          "min": 18.0,
          "max": 25.0,
          "decimals": 1
        }
      }
    ]
  }
}
```

### Python Payload Configuration
```json
{
  "type": "python",
  "python_code": "import random\nfrom datetime import datetime\n\nresult = {\n    'temperature': round(random.uniform(18.0, 25.0), 1),\n    'timestamp': datetime.utcnow().isoformat(),\n    'device_id': device_metadata.get('device_id', 'unknown')\n}"
}
```

## Testing

The integration can be tested by:
1. Creating a project with devices
2. Configuring payloads (both visual and python types)
3. Starting the simulation
4. Monitoring logs and statistics through WebSocket connection
5. Verifying payloads are sent to target systems

## Next Steps

This integration enables:
- Task 7.3: Integration with target connectors (already partially implemented)
- Task 8.1: Real-time simulation dashboard
- Task 8.2: Live log viewing with actual payload data