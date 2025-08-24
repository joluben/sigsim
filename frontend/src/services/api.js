import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || import.meta.env.REACT_APP_API_URL || '/api',
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: false,
});

// Request interceptor for adding auth tokens (future use)
api.interceptors.request.use(
    (config) => {
        // Add auth token when implemented
        // const token = localStorage.getItem('token');
        // if (token) {
        //   config.headers.Authorization = `Bearer ${token}`;
        // }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor for handling errors globally
api.interceptors.response.use(
    (response) => response,
    (error) => {
        // Handle common errors
        if (error.response?.status === 401) {
            // Handle unauthorized access
            console.warn('Unauthorized access');
        } else if (error.response?.status >= 500) {
            // Handle server errors
            console.error('Server error:', error.response.data);
        }

        return Promise.reject(error);
    }
);

export default api;