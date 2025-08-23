import { useCallback, useEffect, useRef, useState } from 'react';
import { useQueryClient } from 'react-query';
import { queryKeys } from './queryClient';

// WebSocket hook for real-time updates
export const useWebSocket = (url, options = {}) => {
    const {
        onOpen,
        onMessage,
        onError,
        onClose,
        reconnectAttempts = 5,
        reconnectInterval = 3000,
        enabled = true,
    } = options;

    const [connectionStatus, setConnectionStatus] = useState('Disconnected');
    const [lastMessage, setLastMessage] = useState(null);
    const wsRef = useRef(null);
    const reconnectTimeoutRef = useRef(null);
    const reconnectCountRef = useRef(0);

    const connect = useCallback(() => {
        if (!enabled || !url) return;

        try {
            const wsUrl = url.startsWith('ws') ? url : `ws://localhost:8000${url}`;
            wsRef.current = new WebSocket(wsUrl);

            wsRef.current.onopen = (event) => {
                setConnectionStatus('Connected');
                reconnectCountRef.current = 0;
                onOpen?.(event);
            };

            wsRef.current.onmessage = (event) => {
                const message = JSON.parse(event.data);
                setLastMessage(message);
                onMessage?.(message);
            };

            wsRef.current.onerror = (event) => {
                setConnectionStatus('Error');
                onError?.(event);
            };

            wsRef.current.onclose = (event) => {
                setConnectionStatus('Disconnected');
                onClose?.(event);

                // Attempt to reconnect if not manually closed
                if (
                    enabled &&
                    !event.wasClean &&
                    reconnectCountRef.current < reconnectAttempts
                ) {
                    reconnectCountRef.current += 1;
                    reconnectTimeoutRef.current = setTimeout(() => {
                        setConnectionStatus('Reconnecting');
                        connect();
                    }, reconnectInterval);
                }
            };
        } catch (error) {
            setConnectionStatus('Error');
            onError?.(error);
        }
    }, [url, enabled, onOpen, onMessage, onError, onClose, reconnectAttempts, reconnectInterval]);

    const disconnect = useCallback(() => {
        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
        }
        if (wsRef.current) {
            wsRef.current.close(1000, 'Manual disconnect');
        }
    }, []);

    const sendMessage = useCallback((message) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify(message));
            return true;
        }
        return false;
    }, []);

    useEffect(() => {
        connect();
        return disconnect;
    }, [connect, disconnect]);

    return {
        connectionStatus,
        lastMessage,
        sendMessage,
        disconnect,
        reconnect: connect,
    };
};

// Hook for simulation real-time updates
export const useSimulationWebSocket = () => {
    const queryClient = useQueryClient();

    return useWebSocket('/ws/simulation', {
        onMessage: (message) => {
            const { type, data } = message;

            switch (type) {
                case 'simulation_status_update':
                    // Update simulation status cache
                    queryClient.setQueryData(queryKeys.simulation.status, data);
                    break;

                case 'project_status_update':
                    // Update specific project simulation status
                    if (data.project_id) {
                        queryClient.setQueryData(
                            queryKeys.projects.simulationStatus(data.project_id),
                            data
                        );
                    }
                    break;

                case 'device_status_update':
                    // Update specific device simulation status
                    if (data.device_id) {
                        queryClient.setQueryData(
                            queryKeys.devices.simulationStatus(data.device_id),
                            data
                        );
                    }
                    break;

                case 'simulation_log':
                    // Add new log entry to the cache
                    queryClient.setQueryData(queryKeys.simulation.logs, (oldData) => {
                        if (!oldData) return [data];
                        return [data, ...oldData.slice(0, 99)]; // Keep only last 100 logs
                    });
                    break;

                case 'active_projects_update':
                    // Update active projects list
                    queryClient.setQueryData(queryKeys.simulation.activeProjects, data);
                    break;

                default:
                    console.log('Unknown WebSocket message type:', type);
            }
        },
        onError: (error) => {
            console.error('Simulation WebSocket error:', error);
        },
    });
};