import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import {
    DocumentArrowDownIcon,
    FolderIcon,
    MagnifyingGlassIcon,
    PauseIcon,
    PencilIcon,
    PlayIcon,
    PlusIcon,
    TrashIcon
} from '@heroicons/react/24/outline'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import {
    useDeleteProject,
    useExportProject,
    useStartProjectSimulation,
    useStopProjectSimulation
} from '../../hooks'
import { useNotificationContext } from '../providers/NotificationProvider'

export default function ProjectList({ 
  projects = [], 
  isLoading, 
  onCreateProject,
  searchTerm,
  onSearchChange 
}) {
  const [deletingProject, setDeletingProject] = useState(null)
  const { showSuccess, showError } = useNotificationContext()

  // Mutations
  const deleteProject = useDeleteProject()
  const startSimulation = useStartProjectSimulation()
  const stopSimulation = useStopProjectSimulation()
  const exportProject = useExportProject()

  // Handlers
  const handleToggleSimulation = async (project) => {
    try {
      if (project.is_running) {
        await stopSimulation.mutateAsync(project.id)
        showSuccess(`Stopped simulation for ${project.name}`)
      } else {
        await startSimulation.mutateAsync(project.id)
        showSuccess(`Started simulation for ${project.name}`)
      }
    } catch (error) {
      showError(`Failed to ${project.is_running ? 'stop' : 'start'} simulation`)
    }
  }

  const handleDelete = async (project) => {
    if (window.confirm(`Are you sure you want to delete "${project.name}"? This action cannot be undone.`)) {
      try {
        setDeletingProject(project.id)
        await deleteProject.mutateAsync(project.id)
        showSuccess(`Project "${project.name}" deleted successfully`)
      } catch (error) {
        showError('Failed to delete project')
      } finally {
        setDeletingProject(null)
      }
    }
  }

  const handleExport = async (project) => {
    try {
      await exportProject.mutateAsync(project.id)
      showSuccess(`Project "${project.name}" exported successfully`)
    } catch (error) {
      showError('Failed to export project')
    }
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Projects</h1>
            <p className="text-muted-foreground">Loading projects...</p>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </CardHeader>
              <CardContent>
                <div className="h-3 bg-gray-200 rounded w-full mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-2/3"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Projects</h1>
          <p className="text-muted-foreground">
            Manage your IoT simulation projects
          </p>
        </div>
        <Button onClick={onCreateProject}>
          <PlusIcon className="w-4 h-4 mr-2" />
          New Project
        </Button>
      </div>

      {/* Search */}
      <div className="flex items-center space-x-4">
        <div className="relative flex-1 max-w-sm">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Search projects..."
            value={searchTerm}
            onChange={(e) => onSearchChange(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Projects Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {projects.map((project) => (
          <Card key={project.id} className="hover:shadow-md transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-2">
                  <FolderIcon className="w-5 h-5 text-muted-foreground" />
                  <CardTitle className="text-lg">{project.name}</CardTitle>
                </div>
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
              <CardDescription className="line-clamp-2">
                {project.description || 'No description provided'}
              </CardDescription>
            </CardHeader>
            
            <CardContent>
              <div className="flex items-center justify-between text-sm text-muted-foreground mb-4">
                <span>{project.devices?.length || 0} devices</span>
                <span>
                  Created {new Date(project.created_at).toLocaleDateString()}
                </span>
              </div>
              
              {/* Action Buttons */}
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <Button asChild variant="outline" size="sm" className="flex-1">
                    <Link to={`/projects/${project.id}`}>
                      View Details
                    </Link>
                  </Button>
                  <Button 
                    variant={project.is_running ? "destructive" : "default"} 
                    size="sm"
                    onClick={() => handleToggleSimulation(project)}
                    disabled={startSimulation.isLoading || stopSimulation.isLoading}
                  >
                    {project.is_running ? (
                      <>
                        <PauseIcon className="w-4 h-4 mr-1" />
                        Stop
                      </>
                    ) : (
                      <>
                        <PlayIcon className="w-4 h-4 mr-1" />
                        Start
                      </>
                    )}
                  </Button>
                </div>
                
                <div className="flex items-center space-x-1">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleExport(project)}
                    disabled={exportProject.isLoading}
                    className="flex-1"
                  >
                    <DocumentArrowDownIcon className="w-4 h-4 mr-1" />
                    Export
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    asChild
                  >
                    <Link to={`/projects/${project.id}/edit`}>
                      <PencilIcon className="w-4 h-4" />
                    </Link>
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDelete(project)}
                    disabled={deletingProject === project.id}
                    className="text-red-600 hover:text-red-700"
                  >
                    <TrashIcon className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Empty state */}
      {projects.length === 0 && (
        <div className="text-center py-12">
          <FolderIcon className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-medium mb-2">No projects found</h3>
          <p className="text-muted-foreground mb-4">
            {searchTerm ? 'Try adjusting your search terms' : 'Get started by creating your first project'}
          </p>
          <Button onClick={onCreateProject}>
            <PlusIcon className="w-4 h-4 mr-2" />
            Create Project
          </Button>
        </div>
      )}
    </div>
  )
}