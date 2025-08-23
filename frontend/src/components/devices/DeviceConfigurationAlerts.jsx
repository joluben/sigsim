import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import {
    ExclamationTriangleIcon,
    WrenchScrewdriverIcon
} from '@heroicons/react/24/outline'
import { Link } from 'react-router-dom'
import { useDevicesValidation } from '../../hooks'

export default function DeviceConfigurationAlerts({
    projects = [],
    className = ""
}) {
    // Get all devices from all projects
    const allDevices = projects.flatMap(project =>
        (project.devices || []).map(device => ({
            ...device,
            projectId: project.id,
            projectName: project.name
        }))
    )

    const validation = useDevicesValidation(allDevices)

    // Don't show if everything is configured
    if (validation.allDevicesValid || validation.totalDevices === 0) {
        return null
    }

    const criticalIssues = validation.allErrors.filter(error =>
        error.error.includes('required') || error.error.includes('Payload') || error.error.includes('Target')
    )

    const devicesByProject = validation.validationResults.reduce((acc, result) => {
        const projectId = result.device.projectId
        if (!acc[projectId]) {
            acc[projectId] = {
                projectName: result.device.projectName,
                devices: []
            }
        }
        if (!result.validation.isValid) {
            acc[projectId].devices.push(result)
        }
        return acc
    }, {})

    return (
        <Card className={`border-yellow-200 ${className}`}>
            <CardHeader>
                <div className="flex items-center space-x-2">
                    <ExclamationTriangleIcon className="w-5 h-5 text-yellow-600" />
                    <div>
                        <CardTitle className="text-yellow-900">Configuration Issues Found</CardTitle>
                        <CardDescription>
                            {validation.devicesWithErrors} device{validation.devicesWithErrors > 1 ? 's' : ''} need{validation.devicesWithErrors === 1 ? 's' : ''} attention
                        </CardDescription>
                    </div>
                </div>
            </CardHeader>

            <CardContent className="space-y-4">
                {/* Summary */}
                <div className="grid grid-cols-3 gap-4">
                    <div className="text-center p-3 bg-red-50 rounded-lg">
                        <div className="text-lg font-bold text-red-600">{criticalIssues.length}</div>
                        <div className="text-xs text-red-700">Critical Issues</div>
                    </div>
                    <div className="text-center p-3 bg-yellow-50 rounded-lg">
                        <div className="text-lg font-bold text-yellow-600">{validation.devicesWithWarnings}</div>
                        <div className="text-xs text-yellow-700">Warnings</div>
                    </div>
                    <div className="text-center p-3 bg-green-50 rounded-lg">
                        <div className="text-lg font-bold text-green-600">{validation.simulationReadyDevices}</div>
                        <div className="text-xs text-green-700">Ready</div>
                    </div>
                </div>

                {/* Issues by Project */}
                <div className="space-y-3">
                    <h4 className="font-medium text-sm">Issues by Project</h4>
                    {Object.entries(devicesByProject).map(([projectId, projectData]) => (
                        <div key={projectId} className="border rounded-lg p-3">
                            <div className="flex items-center justify-between mb-2">
                                <div className="flex items-center space-x-2">
                                    <h5 className="font-medium text-sm">{projectData.projectName}</h5>
                                    <Badge variant="destructive" className="text-xs">
                                        {projectData.devices.length} issue{projectData.devices.length > 1 ? 's' : ''}
                                    </Badge>
                                </div>
                                <Button variant="outline" size="sm" asChild>
                                    <Link to={`/projects/${projectId}`}>
                                        <WrenchScrewdriverIcon className="w-3 h-3 mr-1" />
                                        Fix Issues
                                    </Link>
                                </Button>
                            </div>

                            <div className="space-y-1">
                                {projectData.devices.slice(0, 3).map((result) => (
                                    <div key={result.device.id} className="text-xs text-muted-foreground">
                                        <span className="font-medium">{result.device.name}:</span>
                                        <span className="ml-1">
                                            {result.validation.errors.slice(0, 2).join(', ')}
                                            {result.validation.errors.length > 2 && ` +${result.validation.errors.length - 2} more`}
                                        </span>
                                    </div>
                                ))}
                                {projectData.devices.length > 3 && (
                                    <div className="text-xs text-muted-foreground">
                                        +{projectData.devices.length - 3} more devices with issues
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                </div>

                {/* Quick Actions */}
                <div className="pt-3 border-t">
                    <div className="flex items-center justify-between">
                        <p className="text-sm text-muted-foreground">
                            Fix these issues to enable simulation for all devices
                        </p>
                        <div className="flex items-center space-x-2">
                            <Button variant="outline" size="sm" asChild>
                                <Link to="/payloads">
                                    Add Payloads
                                </Link>
                            </Button>
                            <Button variant="outline" size="sm" asChild>
                                <Link to="/targets">
                                    Add Targets
                                </Link>
                            </Button>
                        </div>
                    </div>
                </div>
            </CardContent>
        </Card>
    )
}