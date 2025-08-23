import api from './api';

export const simulationService = {
    // Get overall simulation status
    getStatus: async () => {
        const response = await api.get('/simulation/status');
        return response.data;
    },

    // Get simulation logs
    getLogs: async (limit = 100, offset = 0) => {
        const response = await api.get('/simulation/logs', {
            params: { limit, offset }
        });
        return response.data;
    },

    // Get simulation metrics
    getMetrics: async () => {
        const response = await api.get('/simulation/metrics');
        return response.data;
    },

    // Clear simulation logs
    clearLogs: async () => {
        const response = await api.delete('/simulation/logs');
        return response.data;
    },

    // Get active projects
    getActiveProjects: async () => {
        const response = await api.get('/simulation/status');
        return response.data;
    },

    // Emergency stop all simulations
    emergencyStop: async () => {
        const response = await api.post('/simulation/emergency-stop');
        return response.data;
    }
};