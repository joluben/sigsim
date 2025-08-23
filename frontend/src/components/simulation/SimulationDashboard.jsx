import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useEmergencyStopSimulation, useSimulationStatus } from '@/hooks/useSimulation';
import { useSimulationWebSocket } from '@/hooks/useWebSocket';
import {
    ClockIcon,
    DevicePhoneMobileIcon,
    ExclamationTriangleIcon,
    PaperAirplaneIcon,
    PlayIcon,
    StopIcon
} from '@heroicons/react/24/outline';
import { useState } from 'react';
import DeviceStatusGrid from './DeviceStatusGrid';
import SimulationControls from './SimulationControls';

export default function SimulationDashboard() {
    const [selectedProject, setSelectedProject] = useState(null);

    // Fetch simulation status
    const { data: simulationStatuses = [], isLoading, error } = useSimulationStatus();

    // WebSocket for real-time updates
    const { connectionStatus } = useSimulationWebSocket();

    // Emergency stop mutation
    const emergencyStopMutation = useEmergencyStopSimulation();

    // Calculate overall statistics
    const totalProjects = simulationStatuses.length;
    const runningProjects = simulationStatuses.filter(s => s.is_running).length;
    const totalDevices = simulationStatuses.reduce((sum, s) => sum + s.total_devices, 0);
    const activeDevices = simulationStatuses.reduce((sum, s) => sum + s.active_devices, 0);
    const totalMessagesSent = simulationStatuses.reduce((sum, s) => sum + s.messages_sent, 0);
    const totalErrors = simulationStatuses.reduce((sum, s) => sum + s.errors.length, 0);

    const handleEmergencyStop = async () => {
        if (window.confirm('Are you sure you want to stop all running simulations?')) {
            await emergencyStopMutation.mutateAsync();
        }
    };

    if (isLoading) {
        return (
            <div className="space-y-6">
                <div className="animate-pulse">
                    <div className="h-8 bg-gray-200 rounded w-1/4 mb-2"></div>
                    <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    {[...Array(4)].map((_, i) => (
                        <div key={i} className="animate-pulse">
                            <div className="h-32 bg-gray-200 rounded"></div>
                        </div>
                    ))}
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <Alert variant="destructive">
                <ExclamationTriangleIcon className="h-4 w-4" />
                <AlertDescription>
                    Failed to load simulation status: {error.message}
                </AlertDescription>
            </Alert>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-start">
                <div>
                    <h1 className="text-3xl font-bold">Simulation Dashboard</h1>
                    <p className="text-muted-foreground">
                        Monitor and control your IoT device simulations in real-time
                    </p>
                </div>

                <div className="flex items-center space-x-4">
                    {/* WebSocket Status */}
                    <div className="flex items-center space-x-2">
                        <div className={`w-2 h-2 rounded-full ${connectionStatus === 'Connected' ? 'bg-green-500' :
                                connectionStatus === 'Reconnecting' ? 'bg-yellow-500' : 'bg-red-500'
                            }`} />
                        <span className="text-sm text-muted-foreground">{connectionStatus}</span>
                    </div>

                    {/* Emergency Stop */}
                    {runningProjects > 0 && (
                        <Button
                            variant="destructive"
                            size="sm"
                            onClick={handleEmergencyStop}
                            disabled={emergencyStopMutation.isLoading}
                        >
                            <StopIcon className="w-4 h-4 mr-2" />
                            Emergency Stop All
                        </Button>
                    )}
                </div>
            </div>

            {/* Overall Statistics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Running Projects</CardTitle>
                        <PlayIcon className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{runningProjects}</div>
                        <p className="text-xs text-muted-foreground">
                            of {totalProjects} total projects
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Active Devices</CardTitle>
                        <DevicePhoneMobileIcon className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{activeDevices}</div>
                        <p className="text-xs text-muted-foreground">
                            of {totalDevices} total devices
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Messages Sent</CardTitle>
                        <PaperAirplaneIcon className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{totalMessagesSent.toLocaleString()}</div>
                        <p className="text-xs text-muted-foreground">
                            across all simulations
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Errors</CardTitle>
                        <ExclamationTriangleIcon className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-red-600">{totalErrors}</div>
                        <p className="text-xs text-muted-foreground">
                            total error count
                        </p>
                    </CardContent>
                </Card>
            </div>

            {/* Project Simulations */}
            <div className="space-y-4">
                <h2 className="text-xl font-semibold">Project Simulations</h2>

                {simulationStatuses.length === 0 ? (
                    <Card>
                        <CardContent className="pt-6">
                            <div className="text-center text-muted-foreground">
                                <DevicePhoneMobileIcon className="mx-auto h-12 w-12 mb-4" />
                                <p>No projects configured for simulation</p>
                                <p className="text-sm">Create a project with devices to get started</p>
                            </div>
                        </CardContent>
                    </Card>
                ) : (
                    <div className="grid gap-4">
                        {simulationStatuses.map((status) => (
                            <Card key={status.project_id} className="overflow-hidden">
                                <CardHeader>
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center space-x-3">
                                            <CardTitle className="text-lg">Project {status.project_id}</CardTitle>
                                            <Badge variant={status.is_running ? "default" : "secondary"}>
                                                {status.is_running ? "Running" : "Stopped"}
                                            </Badge>
                                            {status.errors.length > 0 && (
                                                <Badge variant="destructive">
                                                    {status.errors.length} Error{status.errors.length !== 1 ? 's' : ''}
                                                </Badge>
                                            )}
                                        </div>

                                        <SimulationControls
                                            projectId={status.project_id}
                                            isRunning={status.is_running}
                                        />
                                    </div>

                                    <CardDescription>
                                        <div className="flex items-center space-x-4 text-sm">
                                            <span>{status.active_devices} of {status.total_devices} devices active</span>
                                            <span>{status.messages_sent.toLocaleString()} messages sent</span>
                                            {status.last_activity && (
                                                <span className="flex items-center">
                                                    <ClockIcon className="w-3 h-3 mr-1" />
                                                    Last activity: {new Date(status.last_activity).toLocaleTimeString()}
                                                </span>
                                            )}
                                        </div>
                                    </CardDescription>
                                </CardHeader>

                                <CardContent>
                                    {/* Device Status Grid */}
                                    <DeviceStatusGrid
                                        devices={status.devices}
                                        projectId={status.project_id}
                                    />

                                    {/* Errors */}
                                    {status.errors.length > 0 && (
                                        <div className="mt-4 space-y-2">
                                            <h4 className="text-sm font-medium text-red-600">Recent Errors:</h4>
                                            {status.errors.slice(0, 3).map((error, index) => (
                                                <Alert key={index} variant="destructive" className="py-2">
                                                    <ExclamationTriangleIcon className="h-4 w-4" />
                                                    <AlertDescription className="text-sm">
                                                        <span className="font-medium">Device {error.device_id}:</span> {error.error_message}
                                                        <span className="text-xs ml-2">
                                                            ({new Date(error.timestamp).toLocaleTimeString()})
                                                        </span>
                                                    </AlertDescription>
                                                </Alert>
                                            ))}
                                            {status.errors.length > 3 && (
                                                <p className="text-xs text-muted-foreground">
                                                    ... and {status.errors.length - 3} more errors
                                                </p>
                                            )}
                                        </div>
                                    )}
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}