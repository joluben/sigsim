import api from './api';

export const targetSystemService = {
    // Get all target systems
    getAll: async () => {
        const response = await api.get('/targets');
        return response.data;
    },

    // Get target system by ID
    getById: async (id) => {
        const response = await api.get(`/targets/${id}`);
        return response.data;
    },

    // Create new target system
    create: async (targetSystemData) => {
        const response = await api.post('/targets', targetSystemData);
        return response.data;
    },

    // Update target system
    update: async (id, targetSystemData) => {
        const response = await api.put(`/targets/${id}`, targetSystemData);
        return response.data;
    },

    // Delete target system
    delete: async (id) => {
        const response = await api.delete(`/targets/${id}`);
        return response.data;
    },

    // Test connection to target system
    testConnection: async (id) => {
        const response = await api.post(`/connectors/test`, {
            target_system_id: id
        });
        return response.data;
    },

    // Test connection with configuration (before saving)
    testConnectionConfig: async ({ type, config }) => {
        const response = await api.post('/simulation/connectors/test', {
            target_type: type,
            config: config
        });
        return response.data;
    },

    // Get supported target system types
    getSupportedTypes: async () => {
        const response = await api.get('/simulation/connectors/types');
        return response.data.supported_types || [];
    },

    // Get configuration schema for a target system type
    getConfigSchema: async (type) => {
        const response = await api.get(`/simulation/connectors/${type}/schema`);
        return response.data;
    }
};