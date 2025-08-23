import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
    ArrowPathIcon,
    Cog6ToothIcon,
    ExclamationTriangleIcon,
    WifiIcon,
    XCircleIcon
} from '@heroicons/react/24/outline';
import { useState } from 'react';

const ConnectionAlert = ({
    devices = [],
    onRetryConnection,
    onConfigureTarget,
    onViewLogs,
    className = ""
}) => {
    const [retryingDevices, setRetryingDevices] = useState(new Set());

    // Filter devices with connection issues
    const connectionIssues = devices.filter(device =>
        device.connection_errors > 0 ||
        device.consecutive_errors > 3 ||
        !device.is_connected
    );

    const criticalIssues = connectionIssues.filter(device =>
        device.consecutive_errors > 5 || device.connection_errors > 10
    );

    const handleRetry = async (deviceId) => {
        setRetryingDevices(prev => new Set([...prev, deviceId]));
        try {
            await onRetryConnection?.(deviceId);
        } finally {
            setRetryingDevices(prev => {
                const newSet = new Set(prev);
                newSet.delete(deviceId);
                return newSet;
            });
        }
    };

    if (connectionIssues.length === 0) {
        return null;
    }

    return (
        <Card className={`border-orange-200 bg-orange-50 ${className}`}>
            <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                        <ExclamationTriangleIcon className="h-5 w-5 text-orange-600" />
                        <CardTitle className="text-lg text-orange-800">
                            Connection Issues Detected
                        </CardTitle>
                        <Badge variant="destructive" className="text-xs">
                            {connectionIssues.length} device{connectionIssues.length !== 1 ? 's' : ''}
                        </Badge>
                    </div>

                    {criticalIssues.length > 0 && (
                        <Badge variant="destructive" className="bg-red-600">
                            {criticalIssues.length} Critical
                        </Badge>
                    )}
                </div>
            </CardHeader>

            <CardContent className="space-y-4">
                {/* Summary Alert */}
                <Alert variant="destructive" className="border-orange-300 bg-orange-100">
                    <WifiIcon className="h-4 w-4" />
                    <AlertDescription className="text-orange-800">
                        {connectionIssues.length} device{connectionIssues.length !== 1 ? 's are' : ' is'} experiencing
                        connectivity issues. This may affect data transmission and simulation accuracy.
                        {criticalIssues.length > 0 && (
                            <span className="font-medium text-red-700 ml-1">
                                {criticalIssues.length} device{criticalIssues.length !== 1 ? 's have' : ' has'} critical issues.
                            </span>
                        )}
                    </AlertDescription>
                </Alert>

                {/* Device List */}
                <div className="space-y-2">
                    <h4 className="text-sm font-medium text-orange-800">Affected Devices:</h4>
                    <div className="grid gap-2">
                        {connectionIssues.map((device) => (
                            <div
                                key={device.device_id}
                                className={`flex items-center justify-between p-3 rounded-lg border ${device.consecutive_errors > 5
                                        ? 'border-red-300 bg-red-50'
                                        : 'border-orange-300 bg-orange-100'
                                    }`}
                            >
                                <div className="flex items-center space-x-3">
                                    <div className="flex-shrink-0">
                                        {device.consecutive_errors > 5 ? (
                                            <XCircleIcon className="h-5 w-5 text-red-600" />
                                        ) : (
                                            <ExclamationTriangleIcon className="h-5 w-5 text-orange-600" />
                                        )}
                                    </div>

                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center space-x-2">
                                            <p className="text-sm font-medium text-gray-900 truncate">
                                                {device.device_name}
                                            </p>
                                            {device.consecutive_errors > 5 && (
                                                <Badge variant="destructive" className="text-xs">
                                                    Critical
                                                </Badge>
                                            )}
                                        </div>

                                        <div className="flex items-center space-x-4 text-xs text-gray-600 mt-1">
                                            <span>
                                                Connection errors: {device.connection_errors}
                                            </span>
                                            <span>
                                                Consecutive errors: {device.consecutive_errors}
                                            </span>
                                            {device.last_error && (
                                                <span className="text-red-600 truncate max-w-xs">
                                                    Last: {device.last_error}
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                </div>

                                <div className="flex items-center space-x-2">
                                    <Button
                                        size="sm"
                                        variant="outline"
                                        onClick={() => handleRetry(device.device_id)}
                                        disabled={retryingDevices.has(device.device_id)}
                                        className="text-xs"
                                    >
                                        {retryingDevices.has(device.device_id) ? (
                                            <>
                                                <ArrowPathIcon className="w-3 h-3 mr-1 animate-spin" />
                                                Retrying...
                                            </>
                                        ) : (
                                            <>
                                                <ArrowPathIcon className="w-3 h-3 mr-1" />
                                                Retry
                                            </>
                                        )}
                                    </Button>

                                    <Button
                                        size="sm"
                                        variant="outline"
                                        onClick={() => onConfigureTarget?.(device.device_id)}
                                        className="text-xs"
                                    >
                                        <Cog6ToothIcon className="w-3 h-3 mr-1" />
                                        Configure
                                    </Button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Action Buttons */}
                <div className="flex items-center justify-between pt-2 border-t border-orange-200">
                    <div className="text-xs text-orange-700">
                        Last updated: {new Date().toLocaleTimeString()}
                    </div>

                    <div className="flex space-x-2">
                        <Button
                            size="sm"
                            variant="outline"
                            onClick={() => onViewLogs?.()}
                            className="text-xs"
                        >
                            View Logs
                        </Button>

                        <Button
                            size="sm"
                            onClick={() => {
                                connectionIssues.forEach(device => {
                                    if (!retryingDevices.has(device.device_id)) {
                                        handleRetry(device.device_id);
                                    }
                                });
                            }}
                            disabled={retryingDevices.size > 0}
                            className="text-xs"
                        >
                            {retryingDevices.size > 0 ? (
                                <>
                                    <ArrowPathIcon className="w-3 h-3 mr-1 animate-spin" />
                                    Retrying All...
                                </>
                            ) : (
                                <>
                                    <ArrowPathIcon className="w-3 h-3 mr-1" />
                                    Retry All
                                </>
                            )}
                        </Button>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
};

export default ConnectionAlert;