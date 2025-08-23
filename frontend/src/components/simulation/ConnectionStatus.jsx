import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useSimulationOperations } from '@/hooks/useSimulationOperations';
import { useWebSocket } from '@/hooks/useWebSocket';
import {
    ArrowPathIcon,
    CheckCircleIcon,
    ExclamationTriangleIcon,
    SignalIcon,
    XCircleIcon
} from '@heroicons/react/24/outline';
import { useState } from 'react';

const ConnectionStatus = ({ projectId, className = "" }) => {
    const { testConnection, isTestingConnection } = useSimulationOperations();
    const [lastTestTime, setLastTestTime] = useState(null);

    // WebSocket connection status for the project
    const { connectionStatus: wsStatus, retryCount, isRetrying } = useWebSocket(
        projectId ? `/simulation/${projectId}/logs` : null,
        {
            enabled: !!projectId,
            showConnectionNotifications: false // We'll handle notifications here
        }
    );

    const handleTestConnection = () => {
        testConnection();
        setLastTestTime(new Date());
    };

    const getApiStatusIcon = () => {
        if (isTestingConnection) {
            return <ArrowPathIcon className="w-4 h-4 animate-spin text-blue-600" />;
        }
        // For now, assume API is working if we're not testing
        return <CheckCircleIcon className="w-4 h-4 text-green-600" />;
    };

    const getApiStatusBadge = () => {
        if (isTestingConnection) {
            return <Badge variant="secondary">Testing...</Badge>;
        }
        return <Badge variant="default" className="bg-green-100 text-green-800">Connected</Badge>;
    };

    const getWebSocketStatusIcon = () => {
        switch (wsStatus) {
            case 'Connected':
                return <CheckCircleIcon className="w-4 h-4 text-green-600" />;
            case 'Connecting':
            case 'Reconnecting':
                return <ArrowPathIcon className="w-4 h-4 animate-spin text-blue-600" />;
            case 'Error':
            case 'Failed':
                return <XCircleIcon className="w-4 h-4 text-red-600" />;
            default:
                return <ExclamationTriangleIcon className="w-4 h-4 text-gray-600" />;
        }
    };

    const getWebSocketStatusBadge = () => {
        switch (wsStatus) {
            case 'Connected':
                return <Badge variant="default" className="bg-green-100 text-green-800">Connected</Badge>;
            case 'Connecting':
                return <Badge variant="secondary" className="bg-blue-100 text-blue-800">Connecting</Badge>;
            case 'Reconnecting':
                return <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
                    Reconnecting {retryCount > 0 && `(${retryCount})`}
                </Badge>;
            case 'Error':
            case 'Failed':
                return <Badge variant="destructive">Failed</Badge>;
            default:
                return <Badge variant="secondary">Disconnected</Badge>;
        }
    };

    return (
        <Card className={className}>
            <CardHeader>
                <div className="flex items-center justify-between">
                    <CardTitle className="text-lg flex items-center space-x-2">
                        <SignalIcon className="w-5 h-5" />
                        <span>Connection Status</span>
                    </CardTitle>
                    <Button
                        size="sm"
                        variant="outline"
                        onClick={handleTestConnection}
                        disabled={isTestingConnection}
                        className="text-xs"
                    >
                        {isTestingConnection ? (
                            <>
                                <ArrowPathIcon className="w-3 h-3 mr-1 animate-spin" />
                                Testing...
                            </>
                        ) : (
                            'Test Connection'
                        )}
                    </Button>
                </div>
            </CardHeader>
            <CardContent className="space-y-4">
                {/* API Connection Status */}
                <div className="flex items-center justify-between p-3 rounded-lg border">
                    <div className="flex items-center space-x-3">
                        {getApiStatusIcon()}
                        <div>
                            <h4 className="font-medium text-sm">API Connection</h4>
                            <p className="text-xs text-muted-foreground">
                                REST API for simulation control
                            </p>
                        </div>
                    </div>
                    {getApiStatusBadge()}
                </div>

                {/* WebSocket Connection Status */}
                {projectId && (
                    <div className="flex items-center justify-between p-3 rounded-lg border">
                        <div className="flex items-center space-x-3">
                            {getWebSocketStatusIcon()}
                            <div>
                                <h4 className="font-medium text-sm">WebSocket Connection</h4>
                                <p className="text-xs text-muted-foreground">
                                    Real-time logs for project {projectId}
                                </p>
                            </div>
                        </div>
                        {getWebSocketStatusBadge()}
                    </div>
                )}

                {/* Connection Details */}
                <div className="text-xs text-muted-foreground space-y-1">
                    {lastTestTime && (
                        <p>Last test: {lastTestTime.toLocaleTimeString()}</p>
                    )}
                    {retryCount > 0 && (
                        <p>WebSocket retry attempts: {retryCount}</p>
                    )}
                    {isRetrying && (
                        <p className="text-yellow-600">Attempting to reconnect...</p>
                    )}
                </div>

                {/* Connection Tips */}
                {(wsStatus === 'Failed' || wsStatus === 'Error') && (
                    <div className="p-3 rounded-lg bg-yellow-50 border border-yellow-200">
                        <h5 className="font-medium text-sm text-yellow-800 mb-1">
                            Connection Issues
                        </h5>
                        <ul className="text-xs text-yellow-700 space-y-1">
                            <li>• Check if the backend server is running</li>
                            <li>• Verify network connectivity</li>
                            <li>• Try refreshing the page</li>
                            <li>• Check browser console for errors</li>
                        </ul>
                    </div>
                )}
            </CardContent>
        </Card>
    );
};

export default ConnectionStatus;