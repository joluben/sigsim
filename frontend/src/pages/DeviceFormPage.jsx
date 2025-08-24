import { Button } from '@/components/ui/button'
import { ArrowLeftIcon } from '@heroicons/react/24/outline'
import { Link, useNavigate, useParams } from 'react-router-dom'
import DeviceProjectAssignment from '../components/devices/DeviceProjectAssignment'
import { useDevice, useProject } from '../hooks'

export default function DeviceFormPage() {
  const { projectId, deviceId } = useParams()
  const navigate = useNavigate()
  const isEditing = !!deviceId

  // Fetch data
  const { data: project, isLoading: projectLoading } = useProject(projectId)
  const { data: device, isLoading: deviceLoading } = useDevice(deviceId, {
    enabled: isEditing
  })

  const handleSuccess = (result) => {
    navigate(`/projects/${projectId}`)
  }

  const handleCancel = () => {
    navigate(`/projects/${projectId}`)
  }

  // Loading state
  if (projectLoading || (isEditing && deviceLoading)) {
    return (
      <div className="space-y-6">
        <div className="flex items-center space-x-4">
          <div className="w-8 h-8 bg-gray-200 rounded animate-pulse" />
          <div className="h-8 bg-gray-200 rounded w-48 animate-pulse" />
        </div>
        <div className="h-96 bg-gray-200 rounded animate-pulse" />
      </div>
    )
  }

  // Error state
  if (!project || (isEditing && !device)) {
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
        <div className="text-center py-12">
          <p className="text-red-600">
            {!project ? 'Project not found' : 'Device not found'}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <Button variant="ghost" size="sm" asChild>
          <Link to={`/projects/${projectId}`}>
            <ArrowLeftIcon className="w-4 h-4 mr-2" />
            Back to {project.name}
          </Link>
        </Button>
        <div>
          <h1 className="text-3xl font-bold">
            {isEditing ? `Edit ${device.name}` : 'Add New Device'}
          </h1>
          <p className="text-muted-foreground">
            {isEditing
              ? 'Update the device configuration'
              : `Add a new device to ${project.name}`
            }
          </p>
        </div>
      </div>

      {/* Form */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <DeviceFormSimple
            device={device}
            projectId={projectId}
            onSuccess={handleSuccess}
            onCancel={handleCancel}
          />
        </div>

        {/* Project Assignment - Only show when editing */}
        {isEditing && device && (
          <div className="space-y-6">
            <DeviceProjectAssignment
              device={device}
              currentProject={project}
              onAssignmentChange={(updatedDevice, newProject) => {
                // Navigate to the new project if device was moved
                if (newProject && newProject.id !== projectId) {
                  navigate(`/projects/${newProject.id}`)
                }
              }}
            />
          </div>
        )}
      </div>
    </div>
  )
}