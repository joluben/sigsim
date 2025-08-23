import api from './api';

export const payloadService = {
    // Get all payloads
    getAll: async () => {
        const response = await api.get('/payloads');
        return response.data;
    },

    // Get payload by ID
    getById: async (id) => {
        const response = await api.get(`/payloads/${id}`);
        return response.data;
    },

    // Create new payload
    create: async (payloadData) => {
        const response = await api.post('/payloads', payloadData);
        return response.data;
    },

    // Update payload
    update: async (id, payloadData) => {
        const response = await api.put(`/payloads/${id}`, payloadData);
        return response.data;
    },

    // Delete payload
    delete: async (id) => {
        const response = await api.delete(`/payloads/${id}`);
        return response.data;
    },

    // Generate sample payload
    generateSample: async (id, deviceMetadata = {}) => {
        const response = await api.post(`/payloads/${id}/generate`, {
            device_metadata: deviceMetadata
        });
        return response.data;
    },

    // Validate payload configuration
    validate: async (payloadData) => {
        const response = await api.post('/payloads/validate', payloadData);
        return response.data;
    },

    // Test Python code execution (for Python payloads)
    testPythonCode: async (pythonCode, deviceMetadata = {}) => {
        const response = await api.post('/payloads/test-python', {
            python_code: pythonCode,
            device_metadata: deviceMetadata
        });
        return response.data;
    }
};