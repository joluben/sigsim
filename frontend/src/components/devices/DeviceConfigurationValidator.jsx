import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import {
    CheckCircleIcon,
    ExclamationTriangleIcon,
    XCircleIcon
} from '@heroicons/react/24/outline'

export default function DeviceConfigurationValidator({ device, className = "" }) {
    const validations = [
        {
            key: 'payload',
            label: 'Payload Generator',
            isValid: !!device.payload_id,
            message: device.payload_id
                ? `Configured: ${device.payload?.name || 'Unknown payload'}`
                : 'No payload generator assigned',
            severity: 'error'
        },
        {
            key: 'target',
            label: 'Target System',
            isValid: !!device.target_system_id,
            message: device.target_system_id
                ? `Configured: ${device.target_system?.name || 'Unknown target'}`
                : 'No target system assigned',
            severity: 'error'
        },
        {
            key: 'interval',
            label: 'Send Interval',
            isValid: device.send_interval > 0 && device.send_interval <= 3600,
            message: device.send_interval > 0 && device.send_interval <= 3600
                ? `Every ${device.send_interval} seconds`
                : 'Invalid send interval (must be 1-3600 seconds)',
            severity: 'warning'
        },
        {
            key: 'metadata',
            label: 'Device Metadata',
            isValid: true, // Metadata is optional
            message: Object.keys(device.metadata || {}).length > 0
                ? `${Object.keys(device.metadata).length} custom properties`
                : 'No custom metadata (optional)',
            severity: 'info'
        }
    ]

    const errors = validations.filter(v => !v.isValid && v.severity === 'error')
    const warnings = validations.filter(v => !v.isValid && v.severity === 'warning')
    const isFullyConfigured = errors.length === 0

    const getIcon = (validation) => {
        if (validation.isValid) {
            return <CheckCircleIcon className="w-4 h-4 text-green-600" />
        }
        if (validation.severity === 'error') {
            return <XCircleIcon className="w-4 h-4 text-red-600" />
        }
        return <ExclamationTriangleIcon className="w-4 h-4 text-yellow-600" />
    }

    const getStatusBadge = () => {
        if (isFullyConfigured) {
            return <Badge variant="success">Fully Configured</Badge>
        }
        if (errors.length > 0) {
            return <Badge variant="destructive">Configuration Required</Badge>
        }
        return <Badge variant="warning">Minor Issues</Badge>
    }

    return (
        <Card className={className}>
            <CardHeader>
                <div className="flex items-center justify-between">
                    <div>
                        <CardTitle className="text-lg">Configuration Status</CardTitle>
                        <CardDescription>
                            Device configuration validation for {device.name}
                        </CardDescription>
                    </div>
                    {getStatusBadge()}
                </div>
            </CardHeader>

            <CardContent className="space-y-4">
                {/* Summary */}
                {!isFullyConfigured && (
                    <div className="p-3 rounded-lg bg-muted">
                        <div className="flex items-start space-x-2">
                            <ExclamationTriangleIcon className="w-5 h-5 text-yellow-600 mt-0.5" />
                            <div>
                                <p className="font-medium text-sm">Configuration Issues Found</p>
                                <p className="text-sm text-muted-foreground">
                                    {errors.length > 0 && `${errors.length} critical issue${errors.length > 1 ? 's' : ''}`}
                                    {errors.length > 0 && warnings.length > 0 && ', '}
                                    {warnings.length > 0 && `${warnings.length} warning${warnings.length > 1 ? 's' : ''}`}
                                </p>
                            </div>
                        </div>
                    </div>
                )}

                {/* Validation Items */}
                <div className="space-y-3">
                    {validations.map((validation) => (
                        <div key={validation.key} className="flex items-start space-x-3">
                            {getIcon(validation)}
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center justify-between">
                                    <p className="text-sm font-medium">{validation.label}</p>
                                    {validation.severity === 'error' && !validation.isValid && (
                                        <Badge variant="destructive" className="text-xs">Required</Badge>
                                    )}
                                    {validation.severity === 'warning' && !validation.isValid && (
                                        <Badge variant="warning" className="text-xs">Warning</Badge>
                                    )}
                                </div>
                                <p className="text-sm text-muted-foreground">{validation.message}</p>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Simulation Readiness */}
                <div className="pt-3 border-t">
                    <div className="flex items-center space-x-2">
                        {isFullyConfigured ? (
                            <CheckCircleIcon className="w-5 h-5 text-green-600" />
                        ) : (
                            <XCircleIcon className="w-5 h-5 text-red-600" />
                        )}
                        <div>
                            <p className="text-sm font-medium">
                                {isFullyConfigured ? 'Ready for Simulation' : 'Not Ready for Simulation'}
                            </p>
                            <p className="text-sm text-muted-foreground">
                                {isFullyConfigured
                                    ? 'This device can be included in project simulations'
                                    : 'Complete the required configuration to enable simulation'
                                }
                            </p>
                        </div>
                    </div>
                </div>
            </CardContent>
        </Card>
    )
}