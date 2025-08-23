import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import {
    CheckCircleIcon,
    ClockIcon,
    CpuChipIcon,
    DocumentTextIcon,
    ExclamationTriangleIcon,
    ServerIcon,
    XCircleIcon
} from '@heroicons/react/24/outline'

export default function DeviceConfigurationSummary({ devices = [], className = "" }) {
    const totalDevices = devices.length
    const enabledDevices = devices.filter(d => d.is_enabled).length
    const fullyConfiguredDevices = devices.filter(d =>
        d.payload_id && d.target_system_id && d.send_interval > 0
    ).length
    const devicesWithIssues = totalDevices - fullyConfiguredDevices

    const getConfigurationStatus = (device) => {
        const hasPayload = !!device.payload_id
        const hasTarget = !!device.target_system_id
        const hasValidInterval = device.send_interval > 0 && device.send_interval <= 3600

        if (hasPayload && hasTarget && hasValidInterval) {
            return { status: 'complete', icon: CheckCircleIcon, color: 'text-green-600' }
        }
        if (!hasPayload || !hasTarget) {
            return { status: 'incomplete', icon: XCircleIcon, color: 'text-red-600' }
        }
        return { status: 'warning', icon: ExclamationTriangleIcon, color: 'text-yellow-600' }
    }

    const getStatusBadge = () => {
        if (devicesWithIssues === 0) {
            return <Badge variant="success">All Configured</Badge>
        }
        if (fullyConfiguredDevices === 0) {
            return <Badge variant="destructive">Needs Configuration</Badge>
        }
        return <Badge variant="warning">Partial Configuration</Badge>
    }

    return (
        <Card className={className}>
            <CardHeader>
                <div className="flex items-center justify-between">
                    <div>
                        <CardTitle className="flex items-center space-x-2">
                            <CpuChipIcon className="w-5 h-5" />
                            <span>Device Configuration Summary</span>
                        </CardTitle>
                        <CardDescription>
                            Overview of device configuration status
                        </CardDescription>
                    </div>
                    {getStatusBadge()}
                </div>
            </CardHeader>

            <CardContent className="space-y-4">
                {/* Statistics */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="text-center p-3 bg-muted rounded-lg">
                        <div className="text-2xl font-bold">{totalDevices}</div>
                        <div className="text-sm text-muted-foreground">Total Devices</div>
                    </div>

                    <div className="text-center p-3 bg-green-50 rounded-lg">
                        <div className="text-2xl font-bold text-green-600">{enabledDevices}</div>
                        <div className="text-sm text-muted-foreground">Enabled</div>
                    </div>

                    <div className="text-center p-3 bg-blue-50 rounded-lg">
                        <div className="text-2xl font-bold text-blue-600">{fullyConfiguredDevices}</div>
                        <div className="text-sm text-muted-foreground">Configured</div>
                    </div>

                    <div className="text-center p-3 bg-red-50 rounded-lg">
                        <div className="text-2xl font-bold text-red-600">{devicesWithIssues}</div>
                        <div className="text-sm text-muted-foreground">Need Setup</div>
                    </div>
                </div>

                {/* Device List */}
                {totalDevices > 0 && (
                    <div className="space-y-2">
                        <h4 className="font-medium text-sm">Device Status</h4>
                        <div className="space-y-2 max-h-48 overflow-y-auto">
                            {devices.map((device) => {
                                const config = getConfigurationStatus(device)
                                const StatusIcon = config.icon

                                return (
                                    <div key={device.id} className="flex items-center justify-between p-2 border rounded-lg">
                                        <div className="flex items-center space-x-3">
                                            <StatusIcon className={`w-4 h-4 ${config.color}`} />
                                            <div>
                                                <p className="text-sm font-medium">{device.name}</p>
                                                <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                                                    <span className="flex items-center space-x-1">
                                                        <ClockIcon className="w-3 h-3" />
                                                        <span>{device.send_interval}s</span>
                                                    </span>
                                                    {device.payload_id && (
                                                        <span className="flex items-center space-x-1">
                                                            <DocumentTextIcon className="w-3 h-3" />
                                                            <span>Payload</span>
                                                        </span>
                                                    )}
                                                    {device.target_system_id && (
                                                        <span className="flex items-center space-x-1">
                                                            <ServerIcon className="w-3 h-3" />
                                                            <span>Target</span>
                                                        </span>
                                                    )}
                                                </div>
                                            </div>
                                        </div>

                                        <div className="flex items-center space-x-2">
                                            <Badge variant={device.is_enabled ? 'success' : 'secondary'} className="text-xs">
                                                {device.is_enabled ? 'On' : 'Off'}
                                            </Badge>
                                            <Badge
                                                variant={config.status === 'complete' ? 'success' :
                                                    config.status === 'incomplete' ? 'destructive' : 'warning'}
                                                className="text-xs"
                                            >
                                                {config.status === 'complete' ? 'Ready' :
                                                    config.status === 'incomplete' ? 'Setup' : 'Check'}
                                            </Badge>
                                        </div>
                                    </div>
                                )
                            })}
                        </div>
                    </div>
                )}

                {/* Empty State */}
                {totalDevices === 0 && (
                    <div className="text-center py-6">
                        <CpuChipIcon className="w-12 h-12 text-muted-foreground mx-auto mb-2" />
                        <p className="text-sm text-muted-foreground">No devices configured yet</p>
                    </div>
                )}

                {/* Configuration Issues */}
                {devicesWithIssues > 0 && (
                    <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                        <div className="flex items-start space-x-2">
                            <ExclamationTriangleIcon className="w-5 h-5 text-yellow-600 mt-0.5" />
                            <div>
                                <p className="font-medium text-sm text-yellow-900">Configuration Required</p>
                                <p className="text-sm text-yellow-700">
                                    {devicesWithIssues} device{devicesWithIssues > 1 ? 's' : ''} need{devicesWithIssues === 1 ? 's' : ''} payload generators and target systems to be simulation-ready.
                                </p>
                            </div>
                        </div>
                    </div>
                )}
            </CardContent>
        </Card>
    )
}