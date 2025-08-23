import { useMutation, useQuery, useQueryClient } from 'react-query';
import { simulationService } from '../services';
import { queryKeys } from './queryClient';

// Hook for fetching overall simulation status
export const useSimulationStatus = (options = {}) => {
    return useQuery({
        queryKey: queryKeys.simulation.status,
        queryFn: simulationService.getStatus,
        refetchInterval: 2000, // Refetch every 2 seconds for real-time status
        ...options,
    });
};

// Hook for fetching simulation logs
export const useSimulationLogs = (limit = 100, offset = 0, options = {}) => {
    return useQuery({
        queryKey: [...queryKeys.simulation.logs, { limit, offset }],
        queryFn: () => simulationService.getLogs(limit, offset),
        refetchInterval: 3000, // Refetch every 3 seconds for real-time logs
        ...options,
    });
};

// Hook for fetching simulation metrics
export const useSimulationMetrics = (options = {}) => {
    return useQuery({
        queryKey: queryKeys.simulation.metrics,
        queryFn: simulationService.getMetrics,
        refetchInterval: 5000, // Refetch every 5 seconds for metrics
        ...options,
    });
};

// Hook for fetching active projects
export const useActiveProjects = (options = {}) => {
    return useQuery({
        queryKey: queryKeys.simulation.activeProjects,
        queryFn: simulationService.getActiveProjects,
        refetchInterval: 3000, // Refetch every 3 seconds
        ...options,
    });
};

// Hook for clearing simulation logs
export const useClearSimulationLogs = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: simulationService.clearLogs,
        onSuccess: () => {
            // Invalidate logs to refresh the view
            queryClient.invalidateQueries(queryKeys.simulation.logs);
        },
        onError: (error) => {
            console.error('Error clearing simulation logs:', error);
        },
    });
};

// Hook for emergency stop all simulations
export const useEmergencyStopSimulation = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: simulationService.emergencyStop,
        onSuccess: () => {
            // Invalidate all simulation-related queries
            queryClient.invalidateQueries(queryKeys.simulation.status);
            queryClient.invalidateQueries(queryKeys.simulation.activeProjects);
            queryClient.invalidateQueries(queryKeys.projects.simulationStatus);
        },
        onError: (error) => {
            console.error('Error performing emergency stop:', error);
        },
    });
};