import React, { useState } from 'react';
import { PayloadForm, PayloadList } from '../components/payloads';

// Mock data for demonstration
const mockPayloads = [
  {
    id: '1',
    name: 'Temperature Sensor',
    description: 'Basic temperature and humidity sensor data',
    type: 'visual',
    schema: {
      fields: [
        {
          name: 'device_id',
          type: 'string',
          generator: { type: 'fixed', value: 'temp-001' }
        },
        {
          name: 'temperature',
          type: 'number',
          generator: { type: 'random_float', min: 18.0, max: 25.0, decimals: 1 }
        },
        {
          name: 'humidity',
          type: 'number',
          generator: { type: 'random_int', min: 30, max: 80 }
        },
        {
          name: 'timestamp',
          type: 'timestamp'
        }
      ]
    },
    created_at: '2024-01-15T10:30:00Z'
  },
  {
    id: '2',
    name: 'Smart Thermostat',
    description: 'Advanced thermostat with multiple sensors',
    type: 'python',
    python_code: `def generate_payload():
    return {
        "device_id": device_metadata.get("device_id", "thermostat-001"),
        "timestamp": datetime.utcnow().isoformat(),
        "temperature": random.uniform(18.0, 25.0),
        "humidity": random.randint(30, 80),
        "target_temp": random.uniform(20.0, 24.0),
        "mode": random.choice(["heat", "cool", "auto"]),
        "fan_speed": random.choice(["low", "medium", "high"])
    }

generate_payload()`,
    created_at: '2024-01-14T15:45:00Z'
  }
];

export default function PayloadBuilderPage() {
  const [payloads, setPayloads] = useState(mockPayloads);
  const [currentView, setCurrentView] = useState('list'); // 'list', 'create', 'edit'
  const [editingPayload, setEditingPayload] = useState(null);
  const [loading, setLoading] = useState(false);

  // Handle adding new payload
  const handleAdd = () => {
    setEditingPayload(null);
    setCurrentView('create');
  };

  // Handle editing payload
  const handleEdit = (payload) => {
    setEditingPayload(payload);
    setCurrentView('edit');
  };

  // Handle deleting payload
  const handleDelete = (payload) => {
    if (window.confirm(`Are you sure you want to delete "${payload.name}"?`)) {
      setPayloads(prev => prev.filter(p => p.id !== payload.id));
    }
  };

  // Handle duplicating payload
  const handleDuplicate = (payload) => {
    const duplicated = {
      ...payload,
      id: Date.now().toString(),
      name: `${payload.name} (Copy)`,
      created_at: new Date().toISOString()
    };
    setPayloads(prev => [duplicated, ...prev]);
  };

  // Handle saving payload
  const handleSave = async (payloadData) => {
    setLoading(true);

    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));

    if (editingPayload) {
      // Update existing payload
      setPayloads(prev => prev.map(p =>
        p.id === editingPayload.id
          ? { ...payloadData, id: editingPayload.id, created_at: editingPayload.created_at }
          : p
      ));
    } else {
      // Create new payload
      const newPayload = {
        ...payloadData,
        id: Date.now().toString(),
        created_at: new Date().toISOString()
      };
      setPayloads(prev => [newPayload, ...prev]);
    }

    setLoading(false);
    setCurrentView('list');
    setEditingPayload(null);
  };

  // Handle canceling form
  const handleCancel = () => {
    setCurrentView('list');
    setEditingPayload(null);
  };

  return (
    <div className="space-y-6">
      {currentView === 'list' ? (
        <PayloadList
          payloads={payloads}
          onAdd={handleAdd}
          onEdit={handleEdit}
          onDelete={handleDelete}
          onDuplicate={handleDuplicate}
          loading={loading}
        />
      ) : (
        <PayloadForm
          payload={editingPayload}
          onSave={handleSave}
          onCancel={handleCancel}
        />
      )}
    </div>
  );
}