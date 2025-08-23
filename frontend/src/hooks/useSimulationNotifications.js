import { useNotificationContext } from '@/components/providers/NotificationProvider';
import { useCallback } from 'react';
import { useWebSocket } from './useWebSocket';

// Hook for handling simulation-specific notifications
export const useSimulationNotifications = () => {
    const { showError, showWarning, showSuccess, showInfo } = useNotificationContext();

    // Notification handlers for different simulation events
    const handleDeviceError = useCallback((deviceName, error, deviceId) => {
        showError(
            `Device "${deviceName}" encountered an error: ${error}`,
            'Device Error',
            {
                duration: 10000, // Keep error notifications longer
                actions: [
                    {
                        label: 'View Device',
                        onClick: () => {
                            // Navigate to device details or show device info
                            console.log('Navigate to device:', deviceId);
                        }
                    }
                ]
            }
        );
    }, [showError]);

    const handleConnectionError = useCallback((deviceName, targetType, error) => {
        showError(
            `Failed to connect "${deviceName}" to ${targetType}: ${error}`,
            'Connection Failed',
            {
                duration: 8000,
                actions: [
                    {
                        label: 'Check Configuration',
                        onClick: () => {
                            console.log('Check target configuration');
                        }
                    }
                ]
            }
        );
    }, [showError]);

    const handleSimulationStarted = useCallback((projectId, deviceCount) => {
        showSuccess(
            `Simulation started successfully with ${deviceCount} device${deviceCount !== 1 ? 's' : ''}`,
            'Simulation Started'
        );
    }, [showSuccess]);

    const handleSimulationStopped = useCallback((projectId, reason = 'User request') => {
        showInfo(
            `Simulation stopped: ${reason}`,
            'Simulation Stopped'
        );
    }, [showInfo]);

    const handlePayloadError = useCallback((deviceName, error) => {
        showWarning(
            `Payload generation failed for "${deviceName}": ${error}`,
            'Payload Error',
            {
                duration: 6000
            }
        );
    }, [showWarning]);

    const handleMaxErrorsReached = useCallback((deviceName, errorCount) => {
        showError(
            `Device "${deviceName}" stopped after ${errorCount} consecutive errors`,
            'Device Stopped',
            {
                duration: 12000,
                actions: [
                    {
                        label: 'Restart Device',
                        onClick: () => {
                            console.log('Restart device:', deviceName);
                        }
                    }
                ]
            }
        );
    }, [showError]);

    const handleBulkErrors = useCallback((errorCount, projectId) => {
        if (errorCount > 5) {
            showError(
                `Multiple devices are experiencing errors (${errorCount} errors detected)`,
                'Multiple Device Errors',
                {
                    duration: 15000,
                    actions: [
                        {
                            label: 'View Project',
                            onClick: () => {
                                console.log('Navigate to project:', projectId);
                            }
                        },
                        {
                            label: 'Stop Simulation',
                            onClick: () => {
                                console.log('Emergency stop simulation');
                            }
                        }
                    ]
                }
            );
        }
    }, [showError]);

    return {
        handleDeviceError,
        handleConnectionError,
        handleSimulationStarted,
        handleSimulationStopped,
        handlePayloadError,
        handleMaxErrorsReached,
        handleBulkErrors
    };
};

// Hook for monitoring simulation logs and triggering notifications
export const useSimulationLogNotifications = (projectId) => {
    const notifications = useSimulationNotifications();
    const errorCounts = new Map(); // Track error counts per device

    // WebSocket connection for monitoring logs
    const { lastMessage } = useWebSocket(
        projectId ? `/simulation/${projectId}/logs` : null,
        {
            enabled: !!projectId,
            onMessage: (logEntry) => {
                if (!logEntry || !logEntry.event_type) return;

                const { event_type, device_name, device_id, message } = logEntry;

                switch (event_type) {
                    case 'error':
                        // Track consecutive errors
                        const currentErrors = errorCounts.get(device_id) || 0;
                        errorCounts.set(device_id, currentErrors + 1);

                        if (message.includes('connection') || message.includes('connect')) {
                            notifications.handleConnectionError(device_name, 'Unknown', message);
                        } else if (message.includes('payload')) {
                            notifications.handlePayloadError(device_name, message);
                        } else if (message.includes('consecutive errors')) {
                            notifications.handleMaxErrorsReached(device_name, currentErrors);
                        } else {
                            notifications.handleDeviceError(device_name, message, device_id);
                        }
                        break;

                    case 'message_sent':
                        // Reset error count on successful message
                        errorCounts.set(device_id, 0);
                        break;

                    case 'started':
                        if (device_name === 'System') {
                            // This is a project start event
                            notifications.handleSimulationStarted(projectId, 1);
                        }
                        break;

                    case 'stopped':
                        if (device_name === 'System') {
                            notifications.handleSimulationStopped(projectId);
                        }
                        break;

                    case 'warning':
                        if (message.includes('connection') || message.includes('retry')) {
                            // Don't show notifications for retry warnings to avoid spam
                            break;
                        }
                        notifications.handlePayloadError(device_name, message);
                        break;
                }

                // Check for bulk errors
                const totalErrors = Array.from(errorCounts.values()).reduce((sum, count) => sum + count, 0);
                if (totalErrors > 5) {
                    notifications.handleBulkErrors(totalErrors, projectId);
                }
            }
        }
    );

    return {
        notifications,
        errorCounts: errorCounts.size
    };
};

// Hook for API error notifications with enhanced error handling
export const useEnhancedApiErrorHandler = () => {
    const { showError, showWarning } = useNotificationContext();

    const handleApiError = useCallback((error, context = '') => {
        let title = 'API Error';
        let message = 'An unexpected error occurred';
        let duration = 8000;

        if (error.response) {
            // Server responded with error status
            const status = error.response.status;
            const data = error.response.data;

            switch (status) {
                case 400:
                    title = 'Invalid Request';
                    message = data?.detail || data?.message || 'The request was invalid';
                    break;
                case 401:
                    title = 'Authentication Required';
                    message = 'Please log in to continue';
                    break;
                case 403:
                    title = 'Access Denied';
                    message = 'You do not have permission to perform this action';
                    break;
                case 404:
                    title = 'Not Found';
                    message = data?.detail || 'The requested resource was not found';
                    break;
                case 422:
                    title = 'Validation Error';
                    message = data?.detail || 'Please check your input and try again';
                    if (Array.isArray(data?.detail)) {
                        message = data.detail.map(err => err.msg).join(', ');
                    }
                    break;
                case 500:
                    title = 'Server Error';
                    message = 'An internal server error occurred. Please try again later.';
                    duration = 10000;
                    break;
                default:
                    title = `Error ${status}`;
                    message = data?.detail || data?.message || `Server returned status ${status}`;
            }
        } else if (error.request) {
            // Network error
            title = 'Network Error';
            message = 'Unable to connect to the server. Please check your connection.';
            duration = 10000;
        } else {
            // Other error
            message = error.message || 'An unexpected error occurred';
        }

        if (context) {
            message = `${context}: ${message}`;
        }

        if (error.response?.status >= 500) {
            showError(message, title, { duration });
        } else if (error.response?.status >= 400) {
            showWarning(message, title, { duration: duration * 0.75 });
        } else {
            showError(message, title, { duration });
        }

        console.error('Enhanced API Error:', {
            context,
            error,
            status: error.response?.status,
            data: error.response?.data
        });
    }, [showError, showWarning]);

    return { handleApiError };
};