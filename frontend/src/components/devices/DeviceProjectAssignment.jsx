import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import {
    ArrowRightIcon,
    FolderIcon
} from '@heroicons/react/24/outline'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useProjects, useUpdateDevice } from '../../hooks'
import { useNotificationContext } from '../providers/NotificationProvider'

export default function DeviceProjectAssignment({
    device,
    currentProject,
    onAssignmentChange,
    className = ""
}) {
    const [isChangingProject, setIsChangingProject] = useState(false)
    const [selectedProjectId, setSelectedProjectId] = useState('')

    const { data: projects = [], isLoading: projectsLoading } = useProjects()
    const updateDevice = useUpdateDevice()
    const { showSuccess, showError } = useNotificationContext()

    const handleStartChange = () => {
        setIsChangingProject(true)
        setSelectedProjectId('')
    }

    const handleCancelChange = () => {
        setIsChangingProject(false)
        setSelectedProjectId('')
    }

    const handleConfirmChange = async () => {
        if (!selectedProjectId) return

        try {
            const updatedDevice = await updateDevice.mutateAsync({
                id: device.id,
                project_id: selectedProjectId
            })

            const newProject = projects.find(p => p.id === selectedProjectId)
            showSuccess(`Device "${device.name}" moved to project "${newProject?.name}"`)

            setIsChangingProject(false)
            setSelectedProjectId('')
            onAssignmentChange?.(updatedDevice, newProject)
        } catch (error) {
            showError('Failed to reassign device to project')
        }
    }

    const availableProjects = projects.filter(p => p.id !== currentProject?.id)

    return (
        <Card className={className}>
            <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                    <FolderIcon className="w-5 h-5" />
                    <span>Project Assignment</span>
                </CardTitle>
                <CardDescription>
                    Manage which project this device belongs to
                </CardDescription>
            </CardHeader>

            <CardContent className="space-y-4">
                {!isChangingProject ? (
                    <>
                        {/* Current Assignment */}
                        <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                            <div className="flex items-center space-x-3">
                                <div className="p-2 bg-blue-100 rounded-lg">
                                    <FolderIcon className="w-4 h-4 text-blue-600" />
                                </div>
                                <div>
                                    <p className="font-medium">{currentProject?.name || 'Unknown Project'}</p>
                                    <p className="text-sm text-muted-foreground">
                                        Current project assignment
                                    </p>
                                </div>
                            </div>
                            <div className="flex items-center space-x-2">
                                <Badge variant="default">Current</Badge>
                                <Button
                                    variant="outline"
                                    size="sm"
                                    asChild
                                >
                                    <Link to={`/projects/${currentProject?.id}`}>
                                        View Project
                                    </Link>
                                </Button>
                            </div>
                        </div>

                        {/* Change Project Button */}
                        {availableProjects.length > 0 && (
                            <div className="flex items-center justify-between pt-2 border-t">
                                <div>
                                    <p className="text-sm font-medium">Reassign to Different Project</p>
                                    <p className="text-sm text-muted-foreground">
                                        Move this device to another project
                                    </p>
                                </div>
                                <Button
                                    variant="outline"
                                    onClick={handleStartChange}
                                    disabled={projectsLoading}
                                >
                                    <ArrowRightIcon className="w-4 h-4 mr-2" />
                                    Change Project
                                </Button>
                            </div>
                        )}

                        {availableProjects.length === 0 && (
                            <div className="text-center py-4 text-muted-foreground">
                                <p className="text-sm">No other projects available</p>
                                <p className="text-xs">Create more projects to enable reassignment</p>
                            </div>
                        )}
                    </>
                ) : (
                    <>
                        {/* Project Selection */}
                        <div className="space-y-3">
                            <div>
                                <p className="text-sm font-medium mb-2">Select New Project</p>
                                <Select
                                    value={selectedProjectId}
                                    onValueChange={setSelectedProjectId}
                                    disabled={projectsLoading}
                                >
                                    <SelectTrigger>
                                        <SelectValue placeholder="Choose a project..." />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {availableProjects.map((project) => (
                                            <SelectItem key={project.id} value={project.id}>
                                                <div className="flex items-center space-x-2">
                                                    <FolderIcon className="w-4 h-4" />
                                                    <span>{project.name}</span>
                                                    {project.description && (
                                                        <span className="text-muted-foreground text-xs">
                                                            - {project.description.slice(0, 30)}...
                                                        </span>
                                                    )}
                                                </div>
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>

                            {selectedProjectId && (
                                <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                                    <div className="flex items-center space-x-2">
                                        <ArrowRightIcon className="w-4 h-4 text-blue-600" />
                                        <p className="text-sm font-medium text-blue-900">
                                            Moving to: {projects.find(p => p.id === selectedProjectId)?.name}
                                        </p>
                                    </div>
                                    <p className="text-xs text-blue-700 mt-1">
                                        The device will be moved to the selected project and removed from the current one.
                                    </p>
                                </div>
                            )}
                        </div>

                        {/* Action Buttons */}
                        <div className="flex items-center justify-end space-x-2 pt-3 border-t">
                            <Button
                                variant="outline"
                                onClick={handleCancelChange}
                                disabled={updateDevice.isLoading}
                            >
                                Cancel
                            </Button>
                            <Button
                                onClick={handleConfirmChange}
                                disabled={!selectedProjectId || updateDevice.isLoading}
                            >
                                {updateDevice.isLoading ? (
                                    <div className="flex items-center space-x-2">
                                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                                        <span>Moving...</span>
                                    </div>
                                ) : (
                                    <>
                                        <ArrowRightIcon className="w-4 h-4 mr-2" />
                                        Confirm Move
                                    </>
                                )}
                            </Button>
                        </div>
                    </>
                )}
            </CardContent>
        </Card>
    )
}