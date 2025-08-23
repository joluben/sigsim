import { useMemo, useState } from 'react'
import { ProjectForm, ProjectList } from '../components/projects'
import { useNotificationContext } from '../components/providers/NotificationProvider'
import { useProjects } from '../hooks'

export default function ProjectsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [showCreateForm, setShowCreateForm] = useState(false)
  
  // Use our custom hooks
  const { data: projects = [], isLoading, error } = useProjects()
  const { showError } = useNotificationContext()

  // Filter projects based on search term
  const filteredProjects = useMemo(() => {
    return projects.filter(project =>
      project.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (project.description && project.description.toLowerCase().includes(searchTerm.toLowerCase()))
    )
  }, [projects, searchTerm])

  // Handlers
  const handleCreateProject = () => {
    setShowCreateForm(true)
  }

  const handleCreateSuccess = () => {
    setShowCreateForm(false)
  }

  const handleCreateCancel = () => {
    setShowCreateForm(false)
  }

  // Error state
  if (error) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Projects</h1>
            <p className="text-red-600">Error loading projects: {error.message}</p>
          </div>
        </div>
      </div>
    )
  }

  // Show create form
  if (showCreateForm) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Create New Project</h1>
            <p className="text-muted-foreground">
              Fill in the details to create a new IoT simulation project
            </p>
          </div>
        </div>
        <ProjectForm
          onSuccess={handleCreateSuccess}
          onCancel={handleCreateCancel}
        />
      </div>
    )
  }

  return (
    <ProjectList
      projects={filteredProjects}
      isLoading={isLoading}
      onCreateProject={handleCreateProject}
      searchTerm={searchTerm}
      onSearchChange={setSearchTerm}
    />
  )
}