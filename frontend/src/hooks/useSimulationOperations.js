import { useMutation, useQueryClient } from 'react-query';
import { simulationService } from '../services';
import { queryKeys } from './queryClient';
import { useNotifications } from './useNotifications';
import { useApiRetry } from './useRetry';

/**
 * Hook for simulation operations with retry logic and notifications
 */
export const useSimulationOperations = () => {
    const queryClient = useQueryClient();
    const { executeWithRetry } = useApiRetry();
    const { showSuccess, showError, showWarning } = useNotifications();

    // Start simulation mutation with retry and notifications
    const startSimulationMutation = useMutation(
        (projectId) => executeWithRetry(
            () => simulationService.startSimulation(projectId),
            {
                maxRetries: 3,
                onRetry: (error, attempt) => {
                    showWarning(
                        `Failed to start simulation. Retrying... (${attempt}/3)`,
                        {
                            title: 'Starting Simulation',
                            duration: 3000
                        }
                    );
                }
            }
        ),
        {
            onSuccess: (data, projectId) => {
                showSuccess(
                    `Simulation started successfully for project ${projectId}`,
                    { title: 'Simulation Started' }
                );
                // Invalidate relevant queries
                queryClient.invalidateQueries(queryKeys.simulation.status);
                queryClient.invalidateQueries(queryKeys.simulation.activeProjects);
                queryClient.invalidateQueries(queryKeys.projects.simulationStatus);
            },
            onError: (error, projectId) => {
                showError(
                    `Failed to start simulation for project ${projectId}`,
                    {
                        title: 'Simulation Start Failed',
                        persistent: true,
                        action: {
                            label: 'Retry',
                            onClick: () => startSimulationMutation.mutate(projectId)
                        }
                    }
                );
            }
        }
    );

    // Stop simulation mutation with retry and notifications
    const stopSimulationMutation = useMutation(
        (projectId) => executeWithRetry(
            () => simulationService.stopSimulation(projectId),
            {
                maxRetries: 3,
                onRetry: (error, attempt) => {
                    showWarning(
                        `Failed to stop simulation. Retrying... (${attempt}/3)`,
                        {
                            title: 'Stopping Simulation',
                            duration: 3000
                        }
                    );
                }
            }
        ),
        {
            onSuccess: (data, projectId) => {
                showSuccess(
                    `Simulation stopped successfully for project ${projectId}`,
                    { title: 'Simulation Stopped' }
                );
                // Invalidate relevant queries
                queryClient.invalidateQueries(queryKeys.simulation.status);
                queryClient.invalidateQueries(queryKeys.simulation.activeProjects);
                queryClient.invalidateQueries(queryKeys.projects.simulationStatus);
            },
            onError: (error, projectId) => {
                showError(
                    `Failed to stop simulation for project ${projectId}`,
                    {
                        title: 'Simulation Stop Failed',
                        persistent: true,
                        action: {
                            label: 'Retry',
                            onClick: () => stopSimulationMutation.mutate(projectId)
                        }
                    }
                );
            }
        }
    );

    // Emergency stop mutation with retry and notifications
    const emergencyStopMutation = useMutation(
        () => executeWithRetry(
            () => simulationService.emergencyStop(),
            {
                maxRetries: 5, // More retries for emergency stop
                onRetry: (error, attempt) => {
                    showWarning(
                        `Emergency stop failed. Retrying... (${attempt}/5)`,
                        {
                            title: 'Emergency Stop',
                            duration: 2000
                        }
                    );
                }
            }
        ),
        {
            onSuccess: () => {
                showSuccess(
                    'All simulations stopped successfully',
                    { title: 'Emergency Stop Complete' }
                );
                // Invalidate all simulation-related queries
                queryClient.invalidateQueries(queryKeys.simulation.status);
                queryClient.invalidateQueries(queryKeys.simulation.activeProjects);
                queryClient.invalidateQueries(queryKeys.projects.simulationStatus);
            },
            onError: (error) => {
                showError(
                    'Failed to perform emergency stop. Some simulations may still be running.',
                    {
                        title: 'Emergency Stop Failed',
                        persistent: true,
                        action: {
                            label: 'Retry Emergency Stop',
                            onClick: () => emergencyStopMutation.mutate()
                        }
                    }
                );
            }
        }
    );

    // Test connection mutation
    const testConnectionMutation = useMutation(
        () => executeWithRetry(
            () => simulationService.testConnection(),
            {
                maxRetries: 3,
                showNotifications: false // We'll handle notifications manually
            }
        ),
        {
            onSuccess: (result) => {
                if (result.success) {
                    showSuccess(
                        'Connection to simulation service is working properly',
                        { title: 'Connection Test Successful' }
                    );
                } else {
                    showError(
                        `Connection test failed: ${result.error}`,
                        { title: 'Connection Test Failed' }
                    );
                }
            },
            onError: (error) => {
                showError(
                    `Connection test failed: ${error.message}`,
                    {
                        title: 'Connection Test Failed',
                        action: {
                            label: 'Retry Test',
                            onClick: () => testConnectionMutation.mutate()
                        }
                    }
                );
            }
        }
    );

    // Clear logs mutation
    const clearLogsMutation = useMutation(
        () => executeWithRetry(
            () => simulationService.clearLogs(),
            {
                maxRetries: 2,
                showNotifications: false
            }
        ),
        {
            onSuccess: () => {
                showSuccess(
                    'Simulation logs cleared successfully',
                    { title: 'Logs Cleared' }
                );
                queryClient.invalidateQueries(queryKeys.simulation.logs);
            },
            onError: (error) => {
                showError(
                    `Failed to clear logs: ${error.message}`,
                    { title: 'Clear Logs Failed' }
                );
            }
        }
    );

    return {
        // Mutations
        startSimulation: startSimulationMutation.mutate,
        stopSimulation: stopSimulationMutation.mutate,
        emergencyStop: emergencyStopMutation.mutate,
        testConnection: testConnectionMutation.mutate,
        clearLogs: clearLogsMutation.mutate,

        // Loading states
        isStarting: startSimulationMutation.isLoading,
        isStopping: stopSimulationMutation.isLoading,
        isEmergencyStoppingAll: emergencyStopMutation.isLoading,
        isTestingConnection: testConnectionMutation.isLoading,
        isClearingLogs: clearLogsMutation.isLoading,

        // Error states
        startError: startSimulationMutation.error,
        stopError: stopSimulationMutation.error,
        emergencyStopError: emergencyStopMutation.error,
        connectionError: testConnectionMutation.error,
        clearLogsError: clearLogsMutation.error,

        // Reset functions
        resetStartError: startSimulationMutation.reset,
        resetStopError: stopSimulationMutation.reset,
        resetEmergencyStopError: emergencyStopMutation.reset,
        resetConnectionError: testConnectionMutation.reset,
        resetClearLogsError: clearLogsMutation.reset,
    };
};