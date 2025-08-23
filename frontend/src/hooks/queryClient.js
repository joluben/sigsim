import { QueryClient } from 'react-query';

// Create a client with default configuration
export const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            // Stale time: 5 minutes
            staleTime: 5 * 60 * 1000,
            // Cache time: 10 minutes
            cacheTime: 10 * 60 * 1000,
            // Retry failed requests 3 times
            retry: 3,
            // Retry delay with exponential backoff
            retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
            // Refetch on window focus
            refetchOnWindowFocus: false,
            // Refetch on reconnect
            refetchOnReconnect: true,
        },
        mutations: {
            // Retry failed mutations once
            retry: 1,
        },
    },
});

// Query keys for consistent cache management
export const queryKeys = {
    projects: {
        all: ['projects'],
        detail: (id) => ['projects', id],
        simulationStatus: (id) => ['projects', id, 'simulation-status'],
    },
    devices: {
        all: ['devices'],
        byProject: (projectId) => ['devices', 'project', projectId],
        detail: (id) => ['devices', id],
        simulationStatus: (id) => ['devices', id, 'simulation-status'],
    },
    payloads: {
        all: ['payloads'],
        detail: (id) => ['payloads', id],
    },
    targetSystems: {
        all: ['target-systems'],
        detail: (id) => ['target-systems', id],
        types: ['target-systems', 'types'],
        schema: (type) => ['target-systems', 'types', type, 'schema'],
    },
    simulation: {
        status: ['simulation', 'status'],
        logs: ['simulation', 'logs'],
        metrics: ['simulation', 'metrics'],
        activeProjects: ['simulation', 'active-projects'],
    },
};