import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useWebSocket } from '@/hooks/useWebSocket';
import {
    CheckCircleIcon,
    ClockIcon,
    ExclamationTriangleIcon,
    PaperAirplaneIcon,
    PlayIcon,
    StopIcon,
    TrashIcon,
    XCircleIcon
} from '@heroicons/react/24/outline';
import { useCallback, useEffect, useState } from 'react';

const LogViewer = ({ projectId, className = "" }) => {
    const [logs, setLogs] = useState([]);
    const [isAutoScroll, setIsAutoScroll] = useState(true);
    const [filter, setFilter] = useState('all'); // 'all', 'messages', 'errors', 'events'

    // WebSocket connection for real-time logs
    const { connectionStatus, lastMessage } = useWebSocket(
        projectId ? `/simulation/${projectId}/logs` : null,
        {
            enabled: !!projectId,
            onMessage: (message) => {
                // Add new log entry to the beginning of the array
                setLogs(prevLogs => {
                    const newLogs = [message, ...prevLogs];
                    // Keep only the last 500 logs to prevent memory issues
                    return newLogs.slice(0, 500);
                });
            },
            onError: (error) => {
                console.error('WebSocket error:', error);
            }
        }
    );

    // Auto-scroll to top when new messages arrive
    useEffect(() => {
        if (isAutoScroll && lastMessage) {
            const scrollArea = document.querySelector('[data-radix-scroll-area-viewport]');
            if (scrollArea) {
                scrollArea.scrollTop = 0;
            }
        }
    }, [lastMessage, isAutoScroll]);

    const clearLogs = useCallback(() => {
        setLogs([]);
    }, []);

    const getEventIcon = (eventType) => {
        switch (eventType) {
            case 'message_sent':
                return <PaperAirplaneIcon className="w-4 h-4 text-green-600" />;
            case 'error':
                return <XCircleIcon className="w-4 h-4 text-red-600" />;
            case 'warning':
                return <ExclamationTriangleIcon className="w-4 h-4 text-yellow-600" />;
            case 'started':
                return <PlayIcon className="w-4 h-4 text-blue-600" />;
            case 'stopped':
                return <StopIcon className="w-4 h-4 text-gray-600" />;
            case 'connected':
                return <CheckCircleIcon className="w-4 h-4 text-green-600" />;
            case 'disconnected':
                return <XCircleIcon className="w-4 h-4 text-red-600" />;
            default:
                return <ClockIcon className="w-4 h-4 text-gray-600" />;
        }
    };

    const getEventBadge = (eventType) => {
        switch (eventType) {
            case 'message_sent':
                return <Badge variant="default" className="text-xs">Message</Badge>;
            case 'error':
                return <Badge variant="destructive" className="text-xs">Error</Badge>;
            case 'warning':
                return <Badge variant="secondary" className="text-xs bg-yellow-100 text-yellow-800">Warning</Badge>;
            case 'started':
                return <Badge variant="default" className="text-xs bg-blue-100 text-blue-800">Started</Badge>;
            case 'stopped':
                return <Badge variant="secondary" className="text-xs">Stopped</Badge>;
            case 'connected':
                return <Badge variant="default" className="text-xs bg-green-100 text-green-800">Connected</Badge>;
            case 'disconnected':
                return <Badge variant="destructive" className="text-xs">Disconnected</Badge>;
            default:
                return <Badge variant="secondary" className="text-xs">Event</Badge>;
        }
    };

    const getFilteredLogs = () => {
        switch (filter) {
            case 'messages':
                return logs.filter(log => log.event_type === 'message_sent');
            case 'errors':
                return logs.filter(log => log.event_type === 'error');
            case 'events':
                return logs.filter(log => ['started', 'stopped', 'connected', 'disconnected'].includes(log.event_type));
            default:
                return logs;
        }
    };

    const formatTimestamp = (timestamp) => {
        const date = new Date(timestamp);
        return date.toLocaleTimeString('en-US', {
            hour12: false,
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            fractionalSecondDigits: 3
        });
    };

    const filteredLogs = getFilteredLogs();

    return (
        <Card className={className}>
            <CardHeader>
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                        <CardTitle className="text-lg">Real-time Logs</CardTitle>
                        <div className="flex items-center space-x-2">
                            <div className={`w-2 h-2 rounded-full ${connectionStatus === 'Connected' ? 'bg-green-500' :
                                    connectionStatus === 'Reconnecting' ? 'bg-yellow-500' : 'bg-red-500'
                                }`} />
                            <span className="text-sm text-muted-foreground">{connectionStatus}</span>
                        </div>
                    </div>

                    <div className="flex items-center space-x-2">
                        {/* Filter buttons */}
                        <div className="flex items-center space-x-1">
                            <Button
                                size="sm"
                                variant={filter === 'all' ? 'default' : 'outline'}
                                onClick={() => setFilter('all')}
                                className="text-xs"
                            >
                                All ({logs.length})
                            </Button>
                            <Button
                                size="sm"
                                variant={filter === 'messages' ? 'default' : 'outline'}
                                onClick={() => setFilter('messages')}
                                className="text-xs"
                            >
                                Messages ({logs.filter(l => l.event_type === 'message_sent').length})
                            </Button>
                            <Button
                                size="sm"
                                variant={filter === 'errors' ? 'default' : 'outline'}
                                onClick={() => setFilter('errors')}
                                className="text-xs"
                            >
                                Errors ({logs.filter(l => l.event_type === 'error').length})
                            </Button>
                            <Button
                                size="sm"
                                variant={filter === 'events' ? 'default' : 'outline'}
                                onClick={() => setFilter('events')}
                                className="text-xs"
                            >
                                Events ({logs.filter(l => ['started', 'stopped', 'connected', 'disconnected'].includes(l.event_type)).length})
                            </Button>
                        </div>

                        {/* Auto-scroll toggle */}
                        <Button
                            size="sm"
                            variant={isAutoScroll ? 'default' : 'outline'}
                            onClick={() => setIsAutoScroll(!isAutoScroll)}
                            className="text-xs"
                        >
                            Auto-scroll
                        </Button>

                        {/* Clear logs */}
                        <Button
                            size="sm"
                            variant="outline"
                            onClick={clearLogs}
                            disabled={logs.length === 0}
                            className="text-xs"
                        >
                            <TrashIcon className="w-3 h-3 mr-1" />
                            Clear
                        </Button>
                    </div>
                </div>
            </CardHeader>

            <CardContent>
                <ScrollArea className="h-96 w-full">
                    {filteredLogs.length === 0 ? (
                        <div className="flex items-center justify-center h-32 text-muted-foreground">
                            <div className="text-center">
                                <ClockIcon className="mx-auto h-8 w-8 mb-2" />
                                <p>No logs available</p>
                                <p className="text-sm">
                                    {connectionStatus === 'Connected'
                                        ? 'Waiting for simulation events...'
                                        : 'Connect to see real-time logs'
                                    }
                                </p>
                            </div>
                        </div>
                    ) : (
                        <div className="space-y-2">
                            {filteredLogs.map((log, index) => (
                                <div
                                    key={`${log.timestamp}-${index}`}
                                    className={`flex items-start space-x-3 p-3 rounded-lg border ${log.event_type === 'error' ? 'border-red-200 bg-red-50' :
                                            log.event_type === 'warning' ? 'border-yellow-200 bg-yellow-50' :
                                                log.event_type === 'message_sent' ? 'border-green-200 bg-green-50' :
                                                    'border-gray-200 bg-gray-50'
                                        }`}
                                >
                                    {/* Event icon */}
                                    <div className="flex-shrink-0 mt-0.5">
                                        {getEventIcon(log.event_type)}
                                    </div>

                                    {/* Log content */}
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center justify-between mb-1">
                                            <div className="flex items-center space-x-2">
                                                <span className="text-sm font-medium text-gray-900">
                                                    {log.device_name}
                                                </span>
                                                {getEventBadge(log.event_type)}
                                            </div>
                                            <span className="text-xs text-muted-foreground font-mono">
                                                {formatTimestamp(log.timestamp)}
                                            </span>
                                        </div>

                                        <p className="text-sm text-gray-700 mb-2">
                                            {log.message}
                                        </p>

                                        {/* Payload preview for message_sent events */}
                                        {log.event_type === 'message_sent' && log.payload && (
                                            <details className="mt-2">
                                                <summary className="text-xs text-muted-foreground cursor-pointer hover:text-gray-700">
                                                    View payload
                                                </summary>
                                                <pre className="mt-1 text-xs bg-white p-2 rounded border overflow-x-auto">
                                                    {JSON.stringify(log.payload, null, 2)}
                                                </pre>
                                            </details>
                                        )}

                                        {/* Device ID for reference */}
                                        <div className="text-xs text-muted-foreground mt-1">
                                            Device ID: {log.device_id}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </ScrollArea>
            </CardContent>
        </Card>
    );
};

export default LogViewer;