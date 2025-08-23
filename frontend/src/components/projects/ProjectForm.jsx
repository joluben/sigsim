import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useEffect } from 'react'
import { useCreateProject, useUpdateProject } from '../../hooks'
import { useFormValidation, validationRules } from '../../hooks/useFormValidation'
import { useNotificationContext } from '../providers/NotificationProvider'

const projectValidationRules = {
  name: [
    validationRules.required,
    validationRules.minLength(2),
    validationRules.maxLength(100)
  ],
  description: [
    validationRules.maxLength(500)
  ]
}

export default function ProjectForm({ 
  project = null, 
  onSuccess, 
  onCancel,
  className = "" 
}) {
  const isEditing = !!project
  const { showSuccess, showError } = useNotificationContext()
  
  // Mutations
  const createProject = useCreateProject()
  const updateProject = useUpdateProject()
  
  // Form validation
  const {
    values,
    errors,
    touched,
    isSubmitting,
    handleChange,
    handleBlur,
    handleSubmit,
    setFormValues,
    isValid
  } = useFormValidation(
    {
      name: '',
      description: ''
    },
    projectValidationRules
  )

  // Set initial values when editing
  useEffect(() => {
    if (project) {
      setFormValues({
        name: project.name || '',
        description: project.description || ''
      })
    }
  }, [project, setFormValues])

  const onSubmit = async (formData) => {
    try {
      let result
      if (isEditing) {
        result = await updateProject.mutateAsync({
          id: project.id,
          ...formData
        })
        showSuccess(`Project "${result.name}" updated successfully`)
      } else {
        result = await createProject.mutateAsync(formData)
        showSuccess(`Project "${result.name}" created successfully`)
      }
      
      onSuccess?.(result)
    } catch (error) {
      const message = error.response?.data?.message || error.message || 'An error occurred'
      showError(`Failed to ${isEditing ? 'update' : 'create'} project: ${message}`)
    }
  }

  const handleFormSubmit = (e) => {
    e.preventDefault()
    handleSubmit(onSubmit)
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>
          {isEditing ? 'Edit Project' : 'Create New Project'}
        </CardTitle>
        <CardDescription>
          {isEditing 
            ? 'Update the project information below.'
            : 'Fill in the details to create a new IoT simulation project.'
          }
        </CardDescription>
      </CardHeader>
      
      <CardContent>
        <form onSubmit={handleFormSubmit} className="space-y-4">
          {/* Project Name */}
          <div className="space-y-2">
            <Label htmlFor="name">
              Project Name <span className="text-red-500">*</span>
            </Label>
            <Input
              id="name"
              type="text"
              placeholder="Enter project name"
              value={values.name}
              onChange={(e) => handleChange('name', e.target.value)}
              onBlur={() => handleBlur('name')}
              className={errors.name && touched.name ? 'border-red-500' : ''}
            />
            {errors.name && touched.name && (
              <p className="text-sm text-red-500">{errors.name}</p>
            )}
          </div>

          {/* Project Description */}
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              placeholder="Enter project description (optional)"
              value={values.description}
              onChange={(e) => handleChange('description', e.target.value)}
              onBlur={() => handleBlur('description')}
              className={errors.description && touched.description ? 'border-red-500' : ''}
              rows={3}
            />
            {errors.description && touched.description && (
              <p className="text-sm text-red-500">{errors.description}</p>
            )}
          </div>

          {/* Form Actions */}
          <div className="flex items-center justify-end space-x-2 pt-4">
            {onCancel && (
              <Button
                type="button"
                variant="outline"
                onClick={onCancel}
                disabled={isSubmitting}
              >
                Cancel
              </Button>
            )}
            <Button
              type="submit"
              disabled={!isValid || isSubmitting}
              className="min-w-[100px]"
            >
              {isSubmitting ? (
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>{isEditing ? 'Updating...' : 'Creating...'}</span>
                </div>
              ) : (
                isEditing ? 'Update Project' : 'Create Project'
              )}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}