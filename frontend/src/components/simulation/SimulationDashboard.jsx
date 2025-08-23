import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import HelpTooltip from '@/components/ui/help-tooltip';
import { useSimulationStatus } from '@/hooks/useSimulation';
import { useSimulationLogNotifications } from '@/hooks/useSimulationNotifications';
import { useSimulationWebSocket } from '@/hooks/useWebSocket';
import {
    ClockIcon,
    Cog6ToothIcon,
    DevicePhoneMobileIcon,
    ExclamationTriangleIcon,
    PaperAirplaneIcon,
    PlayIcon,
    StopIcon
} from '@heroicons/react/24/outline';
import { useState } from 'react';
import ConnectionAlert from './ConnectionAlert';
import ConnectionStatus from './ConnectionStatus';
import DeviceStatusGrid from './DeviceStatusGrid';
import LogViewer from './LogViewer';
import SimulationControls from './SimulationControls';
import SimulationNotifications from './SimulationNotifications';

export default function SimulationDashboard() {
    const [selectedProject, setSelectedProject] = useState(null);
    const [showNotificationSettings, setShowNotificationSettings] = useState(false);

    // Fetch simulation status
    const { data: simulationStatuses = [], isLoading, error } = useSimulationStatus();

    // WebSocket for real-time updates
    const { connectionStatus } = useSimulationWebSocket();

    // Simulation notifications for selected project
    const { notifications: simNotifications } = useSimulationLogNotifications(selectedProject);

    // Simulation operations with retry and notifications
    const { emergencyStop, isEmergencyStoppingAll } = useSimulationOperations();

    // Calculate overall statistics
    const totalProjects = simulationStatuses.length;
    const runningProjects = simulationStatuses.filter(s => s.is_running).length;
    const totalDevices = simulationStatuses.reduce((sum, s) => sum + s.total_devices, 0);
    const activeDevices = simulationStatuses.reduce((sum, s) => sum + s.active_devices, 0);
    const totalMessagesSent = simulationStatuses.reduce((sum, s) => sum + s.messages_sent, 0);
    const totalErrors = simulationStatuses.reduce((sum, s) => sum + s.errors.length, 0);

    const handleEmergencyStop = () => {
        if (window.confirm('Are you sure you want to stop all running simulations?')) {
            emergencyStop();
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
            {/* Simulation Notifications Handler */}
            <SimulationNotifications simulationStatuses={simulationStatuses} />
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

                    {/* Notification Settings Toggle */}
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setShowNotificationSettings(!showNotificationSettings)}
                    >
                        <Cog6ToothIcon className="w-4 h-4 mr-2" />
                        {showNotificationSettings ? 'Hide' : 'Show'} Settings
                    </Button>

                    {/* Emergency Stop */}
                    {runningProjects > 0 && (
                        <Button
                            variant="destructive"
                            size="sm"
                            onClick={handleEmergencyStop}
                            disabled={isEmergencyStoppingAll}
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
                        <div className="flex items-center space-x-2">
                            <CardTitle className="text-sm font-medium">Running Projects</CardTitle>
                            <HelpTooltip
                                content="Number of projects currently running simulations. Running projects actively send data to configured targets."
                                type="info"
                            />
                        </div>
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
                        <div className="flex items-center space-x-2">
                            <CardTitle className="text-sm font-medium">Active Devices</CardTitle>
                            <HelpTooltip
                                content="Number of devices currently sending data. Devices may be inactive due to errors, configuration issues, or being disabled."
                                type="info"
                            />
                        </div>
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
                        <div className="flex items-center space-x-2">
                            <CardTitle className="text-sm font-medium">Messages Sent</CardTitle>
                            <HelpTooltip
                                content="Total number of messages successfully sent to target systems across all running simulations. This counter resets when the application restarts."
                                type="info"
                            />
                        </div>
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
                        <div className="flex items-center space-x-2">
                            <CardTitle className="text-sm font-medium">Errors</CardTitle>
                            <HelpTooltip
                                content="Number of recent errors across all devices. Includes connection failures, payload generation errors, and send failures. Check individual devices for details."
                                type="warning"
                            />
                        </div>
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

            {/* Notification Settings */}
            {showNotificationSettings && (
                <div className="space-y-4">
                    <h2 className="text-xl font-semibold">Notification Settings</h2>
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                        <NotificationSettings />
                        <ConnectionStatus />
                    </div>
                </div>
            )}

            {/* Connection Issues Alert */}
            {simulationStatuses.length > 0 && (
                <ConnectionAlert
                    devices={simulationStatuses.flatMap(status => status.devices || [])}
                    onRetryConnection={(deviceId) => {
                        console.log('Retry connection for device:', deviceId);
                        // TODO: Implement retry logic
                    }}
                    onConfigureTarget={(deviceId) => {
                        console.log('Configure target for device:', deviceId);
                        // TODO: Navigate to device configuration
                    }}
                    onViewLogs={() => {
                        // Scroll to logs section or open logs modal
                        const logsSection = document.querySelector('[data-logs-section]');
                        if (logsSection) {
                            logsSection.scrollIntoView({ behavior: 'smooth' });
                        }
                    }}
                />
            )}

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
                            <Card
                                key={status.project_id}
                                data-project-id={status.project_id}
                                className={`overflow-hidden cursor-pointer transition-all hover:shadow-md ${selectedProject === status.project_id ? 'ring-2 ring-blue-500' : ''
                                    }`}
                                onClick={() => setSelectedProject(
                                    selectedProject === status.project_id ? null : status.project_id
                                )}
                            >
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
                                            {selectedProject === status.project_id && (
                                                <Badge variant="outline" className="bg-blue-50 text-blue-700">
                                                    Selected
                                                </Badge>
                                            )}
                                        </div>

                                        <div onClick={(e) => e.stopPropagation()}>
                                            <SimulationControls
                                                projectId={status.project_id}
                                                isRunning={status.is_running}
                                            />
                                        </div>
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

            {/* Real-time Logs Section */}
            {selectedProject && (
                <div className="space-y-4">
                    <h2 className="text-xl font-semibold">Real-time Logs</h2>
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                        <div className="lg:col-span-2">
                            <LogViewer projectId={selectedProject} />
                        </div>
                        <div>
                            <ConnectionStatus projectId={selectedProject} />
                        </div>
                    </div>
                </div>
            )}

            {/* Global Logs when no specific project is selected */}
            {!selectedProject && runningProjects > 0 && (
                <div className="space-y-4">
                    <div className="flex items-center justify-between">
                        <h2 className="text-xl font-semibold">Global Simulation Logs</h2>
                        <div className="flex items-center space-x-2">
                            <span className="text-sm text-muted-foreground">Select a project to view specific logs</span>
                        </div>
                    </div>

                    <div className="grid gap-4">
                        {simulationStatuses
                            .filter(status => status.is_running)
                            .map((status) => (
                                <div key={status.project_id} className="space-y-2">
                                    <div className="flex items-center justify-between">
                                        <h3 className="text-lg font-medium">Project {status.project_id}</h3>
                                        <Button
                                            size="sm"
                                            variant="outline"
                                            onClick={() => setSelectedProject(status.project_id)}
                                        >
                                            View Logs
                                        </Button>
                                    </div>
                                    <LogViewer projectId={status.project_id} className="h-64" />
                                </div>
                            ))
                        }
                    </div>
                </div>
            )}
        </div>
    );
}