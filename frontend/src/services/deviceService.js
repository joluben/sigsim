import api from './api';

export const deviceService = {
    // Get all devices for a project
    getByProject: async (projectId) => {
        const response = await api.get(`/devices/project/${projectId}`);
        return response.data;
    },

    // Get device by ID
    getById: async (id) => {
        const response = await api.get(`/devices/${id}`);
        return response.data;
    },

    // Create new device
    create: async (deviceData) => {
        const response = await api.post('/devices', deviceData);
        return response.data;
    },

    // Update device
    update: async (id, deviceData) => {
        const response = await api.put(`/devices/${id}`, deviceData);
        return response.data;
    },

    // Delete device
    delete: async (id) => {
        const response = await api.delete(`/devices/${id}`);
        return response.data;
    },

    // Toggle device enabled status
    toggleEnabled: async (id, enabled) => {
        const response = await api.patch(`/devices/${id}/enabled`, { enabled });
        return response.data;
    },

    // Get device simulation status
    getSimulationStatus: async (id) => {
        const response = await api.get(`/devices/${id}/simulation/status`);
        return response.data;
    },

    // Test device configuration (generate sample payload)
    testConfiguration: async (id) => {
        const response = await api.post(`/devices/${id}/test`);
        return response.data;
    }
};