import api from './api';

export const projectService = {
    // Get all projects
    getAll: async () => {
        const response = await api.get('/projects');
        return response.data;
    },

    // Get project by ID
    getById: async (id) => {
        const response = await api.get(`/projects/${id}`);
        return response.data;
    },

    // Create new project
    create: async (projectData) => {
        const response = await api.post('/projects', projectData);
        return response.data;
    },

    // Update project
    update: async (id, projectData) => {
        const response = await api.put(`/projects/${id}`, projectData);
        return response.data;
    },

    // Delete project
    delete: async (id) => {
        const response = await api.delete(`/projects/${id}`);
        return response.data;
    },

    // Export project
    export: async (id) => {
        const response = await api.get(`/projects/${id}/export`, {
            responseType: 'blob'
        });
        return response.data;
    },

    // Get project simulation status
    getSimulationStatus: async (id) => {
        const response = await api.get(`/simulation/${id}/status`);
        return response.data;
    },

    // Start project simulation
    startSimulation: async (id) => {
        const response = await api.post(`/simulation/${id}/start`);
        return response.data;
    },

    // Stop project simulation
    stopSimulation: async (id) => {
        const response = await api.post(`/simulation/${id}/stop`);
        return response.data;
    }
};