import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import {
  ArrowLeftIcon,
  Cog6ToothIcon,
  CpuChipIcon,
  DocumentArrowDownIcon,
  ExclamationTriangleIcon,
  PauseIcon,
  PencilIcon,
  PlayIcon,
  PlusIcon,
  TrashIcon
} from '@heroicons/react/24/outline'
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  useDeleteProject,
  useDevicesByProject,
  useExportProject,
  useProject,
  useStartProjectSimulation,
  useStopProjectSimulation
} from '../../hooks'
import DeviceList from '../devices/DeviceList'
import { useNotificationContext } from '../providers/NotificationProvider'
import ProjectForm from './ProjectForm'

export default function ProjectDetail({ projectId }) {
  const [isEditing, setIsEditing] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const navigate = useNavigate()
  const { showSuccess, showError } = useNotificationContext()

  // Data fetching
  const { data: project, isLoading: projectLoading, error: projectError } = useProject(projectId)
  const { data: devices = [], isLoading: devicesLoading } = useDevicesByProject(projectId)

  // Validation
  const simulationValidation = useSimulationValidation(project, devices)

  // Mutations
  const deleteProject = useDeleteProject()
  const startSimulation = useStartProjectSimulation()
  const stopSimulation = useStopProjectSimulation()
  const exportProject = useExportProject()

  // Handlers
  const handleEdit = () => setIsEditing(true)
  const handleCancelEdit = () => setIsEditing(false)
  const handleEditSuccess = () => {
    setIsEditing(false)
  }

  const handleDelete = async () => {
    try {
      await deleteProject.mutateAsync(projectId)
      showSuccess(`Project "${project.name}" deleted successfully`)
      navigate('/projects')
    } catch (error) {
      showError('Failed to delete project')
    }
    setShowDeleteConfirm(false)
  }

  const handleToggleSimulation = async () => {
    try {
      if (project.is_running) {
        await stopSimulation.mutateAsync(projectId)
        showSuccess(`Stopped simulation for ${project.name}`)
      } else {
        await startSimulation.mutateAsync(projectId)
        showSuccess(`Started simulation for ${project.name}`)
      }
    } catch (error) {
      showError(`Failed to ${project.is_running ? 'stop' : 'start'} simulation`)
    }
  }

  const handleExport = async () => {
    try {
      await exportProject.mutateAsync(projectId)
      showSuccess('Project exported successfully')
    } catch (error) {
      showError('Failed to export project')
    }
  }

  // Loading state
  if (projectLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center space-x-4">
          <div className="w-8 h-8 bg-gray-200 rounded animate-pulse" />
          <div className="h-8 bg-gray-200 rounded w-48 animate-pulse" />
        </div>
        <Card className="animate-pulse">
          <CardHeader>
            <div className="h-6 bg-gray-200 rounded w-1/3" />
            <div className="h-4 bg-gray-200 rounded w-2/3" />
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="h-4 bg-gray-200 rounded w-full" />
              <div className="h-4 bg-gray-200 rounded w-3/4" />
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  // Error state
  if (projectError) {
    return (
      <div className="space-y-6">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="sm" asChild>
            <Link to="/projects">
              <ArrowLeftIcon className="w-4 h-4 mr-2" />
              Back to Projects
            </Link>
          </Button>
        </div>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-red-600">Error loading project: {projectError.message}</p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (!project) {
    return (
      <div className="space-y-6">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="sm" asChild>
            <Link to="/projects">
              <ArrowLeftIcon className="w-4 h-4 mr-2" />
              Back to Projects
            </Link>
          </Button>
        </div>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-muted-foreground">Project not found</p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  // Edit mode
  if (isEditing) {
    return (
      <div className="space-y-6">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="sm" onClick={handleCancelEdit}>
            <ArrowLeftIcon className="w-4 h-4 mr-2" />
            Back to Project
          </Button>
        </div>
        <ProjectForm
          project={project}
          onSuccess={handleEditSuccess}
          onCancel={handleCancelEdit}
        />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="sm" asChild>
            <Link to="/projects">
              <ArrowLeftIcon className="w-4 h-4 mr-2" />
              Back to Projects
            </Link>
          </Button>
          <div>
            <h1 className="text-3xl font-bold">{project.name}</h1>
            <p className="text-muted-foreground">
              Created {new Date(project.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <Badge variant={project.is_running ? 'success' : 'secondary'}>
            {project.is_running ? (
              <>
                <PlayIcon className="w-3 h-3 mr-1" />
                Running
              </>
            ) : (
              <>
                <PauseIcon className="w-3 h-3 mr-1" />
                Stopped
              </>
            )}
          </Badge>
        </div>
      </div>

      {/* Project Info Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Project Information</CardTitle>
              <CardDescription>
                {project.description || 'No description provided'}
              </CardDescription>
            </div>
            <div className="flex items-center space-x-2">
              <Button variant="outline" size="sm" onClick={handleExport}>
                <DocumentArrowDownIcon className="w-4 h-4 mr-2" />
                Export
              </Button>
              <Button variant="outline" size="sm" onClick={handleEdit}>
                <PencilIcon className="w-4 h-4 mr-2" />
                Edit
              </Button>
              <Button
                variant="destructive"
                size="sm"
                onClick={() => setShowDeleteConfirm(true)}
              >
                <TrashIcon className="w-4 h-4 mr-2" />
                Delete
              </Button>
            </div>
          </div>
        </CardHeader>

        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center space-x-3">
              <CpuChipIcon className="w-5 h-5 text-muted-foreground" />
              <div>
                <p className="text-sm font-medium">Devices</p>
                <p className="text-2xl font-bold">{devices.length}</p>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <Cog6ToothIcon className="w-5 h-5 text-muted-foreground" />
              <div>
                <p className="text-sm font-medium">Status</p>
                <p className="text-2xl font-bold">
                  {project.is_running ? 'Active' : 'Inactive'}
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <PlayIcon className="w-5 h-5 text-muted-foreground" />
              <div>
                <p className="text-sm font-medium">Last Updated</p>
                <p className="text-sm text-muted-foreground">
                  {new Date(project.updated_at).toLocaleDateString()}
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Simulation Control */}
      <Card>
        <CardHeader>
          <CardTitle>Simulation Control</CardTitle>
          <CardDescription>
            Start or stop the simulation for this project
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Validation Messages */}
          {!simulationValidation.canStartSimulation && !project.is_running && (
            <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <div className="flex items-start space-x-2">
                <ExclamationTriangleIcon className="w-5 h-5 text-yellow-600 mt-0.5" />
                <div>
                  <p className="font-medium text-sm text-yellow-900">Simulation Not Ready</p>
                  <ul className="text-sm text-yellow-700 mt-1 space-y-1">
                    {simulationValidation.errors.map((error, index) => (
                      <li key={index}>• {error}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}

          {simulationValidation.warnings.length > 0 && (
            <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-start space-x-2">
                <ExclamationTriangleIcon className="w-5 h-5 text-blue-600 mt-0.5" />
                <div>
                  <p className="font-medium text-sm text-blue-900">Configuration Warnings</p>
                  <ul className="text-sm text-blue-700 mt-1 space-y-1">
                    {simulationValidation.warnings.map((warning, index) => (
                      <li key={index}>• {warning}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}

          <div className="flex items-center space-x-4">
            <Button
              onClick={handleToggleSimulation}
              disabled={
                startSimulation.isLoading ||
                stopSimulation.isLoading ||
                (!project.is_running && !simulationValidation.canStartSimulation)
              }
              variant={project.is_running ? "destructive" : "default"}
            >
              {project.is_running ? (
                <>
                  <PauseIcon className="w-4 h-4 mr-2" />
                  Stop Simulation
                </>
              ) : (
                <>
                  <PlayIcon className="w-4 h-4 mr-2" />
                  Start Simulation
                </>
              )}
            </Button>

            {project.is_running ? (
              <p className="text-sm text-muted-foreground">
                Simulation is currently running with {simulationValidation.readyDevicesCount} active devices
              </p>
            ) : simulationValidation.canStartSimulation ? (
              <p className="text-sm text-muted-foreground">
                Ready to simulate with {simulationValidation.readyDevicesCount} configured devices
              </p>
            ) : (
              <p className="text-sm text-muted-foreground">
                Configure devices to enable simulation
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Device Configuration Summary */}
      {devices.length > 0 && (
        <DeviceConfigurationSummary devices={devices} />
      )}

      {/* Devices Section */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Devices ({devices.length})</CardTitle>
              <CardDescription>
                Manage the IoT devices in this project
              </CardDescription>
            </div>
            <Button asChild>
              <Link to={`/projects/${projectId}/devices/new`}>
                <PlusIcon className="w-4 h-4 mr-2" />
                Add Device
              </Link>
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <DeviceList
            devices={devices}
            isLoading={devicesLoading}
            projectId={projectId}
          />
        </CardContent>
      </Card>

      {/* Delete Confirmation Dialog */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>Delete Project</CardTitle>
              <CardDescription>
                Are you sure you want to delete "{project.name}"? This action cannot be undone.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-end space-x-2">
                <Button
                  variant="outline"
                  onClick={() => setShowDeleteConfirm(false)}
                >
                  Cancel
                </Button>
                <Button
                  variant="destructive"
                  onClick={handleDelete}
                  disabled={deleteProject.isLoading}
                >
                  {deleteProject.isLoading ? 'Deleting...' : 'Delete'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}