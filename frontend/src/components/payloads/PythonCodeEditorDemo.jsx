import React, { useState } from 'react';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import PythonCodeEditor from './PythonCodeEditor';

const PythonCodeEditorDemo = () => {
    const [currentExample, setCurrentExample] = useState('basic');
    const [code, setCode] = useState('');
    const [isValid, setIsValid] = useState(true);

    const examples = {
        basic: {
            name: 'Basic Sensor Data',
            code: `import random
from datetime import datetime
import uuid

# Access device metadata
device_id = device_metadata.get('device_id', 'sensor-001')
location = device_metadata.get('location', 'Lab A')

# Generate basic sensor payload
result = {
    "device_id": device_id,
    "location": location,
    "timestamp": datetime.utcnow().isoformat(),
    "temperature": round(random.uniform(18.0, 25.0), 1),
    "humidity": random.randint(30, 80),
    "status": "online"
}`
        },
        advanced: {
            name: 'Advanced IoT Device',
            code: `import random
from datetime import datetime
import uuid
import math

# Device configuration
device_id = device_metadata.get('device_id', 'iot-device-001')
device_type = device_metadata.get('type', 'multi-sensor')

# Generate advanced payload with multiple sensors
base_temp = 22.0
temp_variation = random.uniform(-3.0, 3.0)
current_temp = base_temp + temp_variation

# Simulate realistic sensor correlations
humidity = max(30, min(90, 60 + (current_temp - 22) * -2 + random.uniform(-10, 10)))
pressure = 1013.25 + random.uniform(-20, 20)

# Battery simulation (decreases over time)
battery_base = random.randint(70, 100)
battery_noise = random.uniform(-5, 2)
battery_level = max(0, min(100, battery_base + battery_noise))

result = {
    "device_id": device_id,
    "device_type": device_type,
    "timestamp": datetime.utcnow().isoformat(),
    "session_id": str(uuid.uuid4()),
    "sensors": {
        "temperature": {
            "value": round(current_temp, 1),
            "unit": "°C",
            "accuracy": 0.1
        },
        "humidity": {
            "value": round(humidity, 1),
            "unit": "%",
            "accuracy": 2.0
        },
        "pressure": {
            "value": round(pressure, 2),
            "unit": "hPa",
            "accuracy": 0.5
        }
    },
    "system": {
        "battery_level": round(battery_level, 1),
        "signal_strength": random.randint(-90, -30),
        "uptime": random.randint(3600, 86400)
    },
    "location": {
        "latitude": 40.7128 + random.uniform(-0.01, 0.01),
        "longitude": -74.0060 + random.uniform(-0.01, 0.01),
        "altitude": random.uniform(0, 100)
    },
    "status": random.choice(["online", "warning", "maintenance"])
}`
        },
        timeseries: {
            name: 'Time Series Data',
            code: `import random
from datetime import datetime, timedelta
import math

# Generate time series data points
device_id = device_metadata.get('device_id', 'timeseries-001')
num_points = 5  # Generate 5 data points

# Base timestamp
base_time = datetime.utcnow()
data_points = []

for i in range(num_points):
    # Create timestamp for each point (1 minute intervals)
    point_time = base_time - timedelta(minutes=i)
    
    # Generate sinusoidal pattern with noise for realistic data
    time_factor = i * 0.1
    base_value = 50 + 20 * math.sin(time_factor)
    noise = random.uniform(-5, 5)
    value = round(base_value + noise, 2)
    
    data_points.append({
        "timestamp": point_time.isoformat(),
        "value": value,
        "quality": random.choice(["good", "fair", "poor"])
    })

result = {
    "device_id": device_id,
    "measurement_type": "continuous_monitoring",
    "timestamp": datetime.utcnow().isoformat(),
    "data_points": data_points,
    "statistics": {
        "count": len(data_points),
        "average": round(sum(p["value"] for p in data_points) / len(data_points), 2),
        "min": min(p["value"] for p in data_points),
        "max": max(p["value"] for p in data_points)
    }
}`
        }
    };

    const handleExampleChange = (exampleKey) => {
        setCurrentExample(exampleKey);
        setCode(examples[exampleKey].code);
    };

    const handleCodeChange = (newCode) => {
        setCode(newCode);
    };

    const handleValidation = (valid, errors) => {
        setIsValid(valid);
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h2 className="text-2xl font-bold">Python Code Editor Demo</h2>
                <p className="text-gray-600 mt-1">
                    Interactive demonstration of the Python code editor with syntax highlighting and validation
                </p>
            </div>

            {/* Example Selector */}
            <Card>
                <CardHeader>
                    <CardTitle className="text-lg">Code Examples</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="flex flex-wrap gap-2">
                        {Object.entries(examples).map(([key, example]) => (
                            <Button
                                key={key}
                                variant={currentExample === key ? 'default' : 'outline'}
                                size="sm"
                                onClick={() => handleExampleChange(key)}
                            >
                                {example.name}
                            </Button>
                        ))}
                    </div>
                </CardContent>
            </Card>

            {/* Status */}
            <div className="flex items-center gap-4">
                <Badge
                    variant={isValid ? 'default' : 'destructive'}
                    className="text-sm"
                >
                    {isValid ? '✅ Code Valid' : '❌ Code Invalid'}
                </Badge>
                <span className="text-sm text-gray-600">
                    Current example: <strong>{examples[currentExample].name}</strong>
                </span>
            </div>

            {/* Editor */}
            <PythonCodeEditor
                code={code || examples[currentExample].code}
                onChange={handleCodeChange}
                onValidate={handleValidation}
                height="600px"
                showPreview={true}
                deviceMetadata={{
                    device_id: 'demo-device-001',
                    type: 'demo-sensor',
                    location: 'Demo Lab',
                    firmware_version: '1.2.3'
                }}
            />

            {/* Features */}
            <Card>
                <CardHeader>
                    <CardTitle className="text-lg">Editor Features</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <h4 className="font-medium mb-2">Code Features</h4>
                            <ul className="text-sm space-y-1 text-gray-600">
                                <li>• Syntax highlighting for Python</li>
                                <li>• Auto-completion for common functions</li>
                                <li>• Real-time validation</li>
                                <li>• Error and warning detection</li>
                                <li>• Code folding and line numbers</li>
                            </ul>
                        </div>
                        <div>
                            <h4 className="font-medium mb-2">Security Features</h4>
                            <ul className="text-sm space-y-1 text-gray-600">
                                <li>• Restricted module imports</li>
                                <li>• Dangerous function detection</li>
                                <li>• Safe execution environment</li>
                                <li>• Input validation</li>
                                <li>• Sandboxed preview execution</li>
                            </ul>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
};

export default PythonCodeEditorDemo;