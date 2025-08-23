import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import {
    CheckCircleIcon,
    ClockIcon,
    ExclamationTriangleIcon,
    PaperAirplaneIcon,
    XCircleIcon
} from '@heroicons/react/24/outline';

export default function DeviceStatusGrid({ devices = [], projectId }) {
    if (devices.length === 0) {
        return (
            <div className="text-center text-muted-foreground py-8">
                <p>No devices configured for this project</p>
            </div>
        );
    }

    const getStatusIcon = (device) => {
        if (device.error) {
            return <XCircleIcon className="w-4 h-4 text-red-500" />;
        }
        if (device.is_running) {
            return <CheckCircleIcon className="w-4 h-4 text-green-500" />;
        }
        return <ClockIcon className="w-4 h-4 text-gray-400" />;
    };

    const getStatusColor = (device) => {
        if (device.error) return 'border-red-200 bg-red-50';
        if (device.is_running) return 'border-green-200 bg-green-50';
        return 'border-gray-200 bg-gray-50';
    };

    const getStatusBadge = (device) => {
        if (device.error) {
            return <Badge variant="destructive" className="text-xs">Error</Badge>;
        }
        if (device.is_running) {
            return <Badge variant="default" className="text-xs">Active</Badge>;
        }
        return <Badge variant="secondary" className="text-xs">Inactive</Badge>;
    };

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <h4 className="text-sm font-medium">Device Status</h4>
                <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                    <div className="flex items-center space-x-1">
                        <CheckCircleIcon className="w-3 h-3 text-green-500" />
                        <span>Active</span>
                    </div>
                    <div className="flex items-center space-x-1">
                        <ClockIcon className="w-3 h-3 text-gray-400" />
                        <span>Inactive</span>
                    </div>
                    <div className="flex items-center space-x-1">
                        <XCircleIcon className="w-3 h-3 text-red-500" />
                        <span>Error</span>
                    </div>
                </div>
            </div>

            {/* Grid Layout for devices */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
                {devices.map((device) => (
                    <TooltipProvider key={device.device_id}>
                        <Tooltip>
                            <TooltipTrigger asChild>
                                <Card className={`cursor-pointer transition-all hover:shadow-md ${getStatusColor(device)}`}>
                                    <CardContent className="p-3">
                                        <div className="flex items-start justify-between mb-2">
                                            <div className="flex items-center space-x-2 min-w-0 flex-1">
                                                {getStatusIcon(device)}
                                                <span className="text-sm font-medium truncate">
                                                    {device.device_name}
                                                </span>
                                            </div>
                                            {getStatusBadge(device)}
                                        </div>

                                        <div className="space-y-1">
                                            <div className="flex items-center justify-between text-xs">
                                                <span className="text-muted-foreground">Messages:</span>
                                                <span className="font-medium">{device.messages_sent.toLocaleString()}</span>
                                            </div>

                                            {device.last_message_at && (
                                                <div className="flex items-center justify-between text-xs">
                                                    <span className="text-muted-foreground">Last sent:</span>
                                                    <span className="font-medium">
                                                        {new Date(device.last_message_at).toLocaleTimeString()}
                                                    </span>
                                                </div>
                                            )}

                                            {device.error && (
                                                <div className="flex items-start space-x-1 text-xs text-red-600 mt-2">
                                                    <ExclamationTriangleIcon className="w-3 h-3 mt-0.5 flex-shrink-0" />
                                                    <span className="truncate">{device.error}</span>
                                                </div>
                                            )}
                                        </div>
                                    </CardContent>
                                </Card>
                            </TooltipTrigger>

                            <TooltipContent side="top" className="max-w-xs">
                                <div className="space-y-2">
                                    <div className="font-medium">{device.device_name}</div>
                                    <div className="text-xs space-y-1">
                                        <div>ID: {device.device_id}</div>
                                        <div>Status: {device.is_running ? 'Running' : 'Stopped'}</div>
                                        <div>Messages sent: {device.messages_sent.toLocaleString()}</div>
                                        {device.last_message_at && (
                                            <div>
                                                Last message: {new Date(device.last_message_at).toLocaleString()}
                                            </div>
                                        )}
                                        {device.error && (
                                            <div className="text-red-600 mt-2">
                                                <div className="font-medium">Error:</div>
                                                <div>{device.error}</div>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </TooltipContent>
                        </Tooltip>
                    </TooltipProvider>
                ))}
            </div>

            {/* Summary Stats */}
            <div className="flex items-center justify-between pt-2 border-t text-xs text-muted-foreground">
                <div className="flex items-center space-x-4">
                    <span>Total: {devices.length}</span>
                    <span className="text-green-600">
                        Active: {devices.filter(d => d.is_running && !d.error).length}
                    </span>
                    <span className="text-red-600">
                        Errors: {devices.filter(d => d.error).length}
                    </span>
                </div>

                <div className="flex items-center space-x-1">
                    <PaperAirplaneIcon className="w-3 h-3" />
                    <span>
                        Total messages: {devices.reduce((sum, d) => sum + d.messages_sent, 0).toLocaleString()}
                    </span>
                </div>
            </div>
        </div>
    );
}