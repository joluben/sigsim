import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import {
  ClockIcon,
  CpuChipIcon,
  DocumentTextIcon,
  ServerIcon
} from '@heroicons/react/24/outline'
import { useEffect } from 'react'
import {
  useCreateDevice,
  usePayloads,
  useTargetSystems,
  useUpdateDevice
} from '../../hooks'
import { useFormValidation, validationRules } from '../../hooks/useFormValidation'
import { useNotificationContext } from '../providers/NotificationProvider'
import DeviceConfigurationValidator from './DeviceConfigurationValidator'
import DeviceMetadataEditor from './DeviceMetadataEditor'

const deviceValidationRules = {
  name: [
    validationRules.required,
    validationRules.minLength(2),
    validationRules.maxLength(100)
  ],
  send_interval: [
    validationRules.required,
    validationRules.positiveNumber,
    validationRules.range(1, 3600)
  ],
  payload_id: [
    validationRules.required
  ],
  target_system_id: [
    validationRules.required
  ]
}

export default function DeviceForm({
  device = null,
  projectId,
  onSuccess,
  onCancel,
  className = ""
}) {
  const isEditing = !!device
  const { showSuccess, showError } = useNotificationContext()

  // Data fetching
  const { data: payloads = [], isLoading: payloadsLoading } = usePayloads()
  const { data: targetSystems = [], isLoading: targetsLoading } = useTargetSystems()

  // Mutations
  const createDevice = useCreateDevice()
  const updateDevice = useUpdateDevice()

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
      send_interval: 10,
      payload_id: '',
      target_system_id: '',
      is_enabled: true,
      metadata: {}
    },
    deviceValidationRules
  )

  // Set initial values when editing
  useEffect(() => {
    if (device) {
      setFormValues({
        name: device.name || '',
        send_interval: device.send_interval || 10,
        payload_id: device.payload_id || '',
        target_system_id: device.target_system_id || '',
        is_enabled: device.is_enabled ?? true,
        metadata: device.metadata || {}
      })
    }
  }, [device, setFormValues])

  const onSubmit = async (formData) => {
    try {
      let result
      if (isEditing) {
        result = await updateDevice.mutateAsync({
          id: device.id,
          ...formData
        })
        showSuccess(`Device "${result.name}" updated successfully`)
      } else {
        result = await createDevice.mutateAsync({
          projectId,
          ...formData
        })
        showSuccess(`Device "${result.name}" created successfully`)
      }

      onSuccess?.(result)
    } catch (error) {
      const message = error.response?.data?.message || error.message || 'An error occurred'
      showError(`Failed to ${isEditing ? 'update' : 'create'} device: ${message}`)
    }
  }

  const handleFormSubmit = (e) => {
    e.preventDefault()
    handleSubmit(onSubmit)
  }

  const handleMetadataChange = (metadata) => {
    handleChange('metadata', metadata)
  }

  const selectedPayload = payloads.find(p => p.id === values.payload_id)
  const selectedTarget = targetSystems.find(t => t.id === values.target_system_id)

  return (
    <div className={`space-y-6 ${className}`}>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <CpuChipIcon className="w-5 h-5" />
            <span>{isEditing ? 'Edit Device' : 'Create New Device'}</span>
          </CardTitle>
          <CardDescription>
            {isEditing
              ? 'Update the device configuration below.'
              : 'Configure a new IoT device for your simulation project.'
            }
          </CardDescription>
        </CardHeader>

        <CardContent>
          <form onSubmit={handleFormSubmit} className="space-y-6">
            {/* Basic Information */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Basic Information</h3>

              {/* Device Name */}
              <div className="space-y-2">
                <Label htmlFor="name">
                  Device Name <span className="text-red-500">*</span>
                </Label>
                <Input
                  id="name"
                  type="text"
                  placeholder="Enter device name"
                  value={values.name}
                  onChange={(e) => handleChange('name', e.target.value)}
                  onBlur={() => handleBlur('name')}
                  className={errors.name && touched.name ? 'border-red-500' : ''}
                />
                {errors.name && touched.name && (
                  <p className="text-sm text-red-500">{errors.name}</p>
                )}
              </div>

              {/* Send Interval */}
              <div className="space-y-2">
                <Label htmlFor="send_interval" className="flex items-center space-x-2">
                  <ClockIcon className="w-4 h-4" />
                  <span>Send Interval (seconds) <span className="text-red-500">*</span></span>
                </Label>
                <Input
                  id="send_interval"
                  type="number"
                  min="1"
                  max="3600"
                  placeholder="10"
                  value={values.send_interval}
                  onChange={(e) => handleChange('send_interval', parseInt(e.target.value) || '')}
                  onBlur={() => handleBlur('send_interval')}
                  className={errors.send_interval && touched.send_interval ? 'border-red-500' : ''}
                />
                {errors.send_interval && touched.send_interval && (
                  <p className="text-sm text-red-500">{errors.send_interval}</p>
                )}
                <p className="text-sm text-muted-foreground">
                  How often the device should send data (1-3600 seconds)
                </p>
              </div>

              {/* Device Status */}
              <div className="space-y-2">
                <Label>Device Status</Label>
                <div className="flex items-center space-x-4">
                  <label className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="radio"
                      name="is_enabled"
                      checked={values.is_enabled === true}
                      onChange={() => handleChange('is_enabled', true)}
                      className="w-4 h-4 text-blue-600"
                    />
                    <span>Enabled</span>
                    <Badge variant="success" className="text-xs">Active</Badge>
                  </label>
                  <label className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="radio"
                      name="is_enabled"
                      checked={values.is_enabled === false}
                      onChange={() => handleChange('is_enabled', false)}
                      className="w-4 h-4 text-blue-600"
                    />
                    <span>Disabled</span>
                    <Badge variant="secondary" className="text-xs">Inactive</Badge>
                  </label>
                </div>
              </div>
            </div>

            {/* Configuration */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Configuration</h3>

              {/* Payload Selection */}
              <div className="space-y-2">
                <Label className="flex items-center space-x-2">
                  <DocumentTextIcon className="w-4 h-4" />
                  <span>Payload Generator <span className="text-red-500">*</span></span>
                </Label>
                <Select
                  value={values.payload_id}
                  onValueChange={(value) => handleChange('payload_id', value)}
                  disabled={payloadsLoading}
                >
                  <SelectTrigger className={errors.payload_id && touched.payload_id ? 'border-red-500' : ''}>
                    <SelectValue placeholder={payloadsLoading ? "Loading payloads..." : "Select a payload generator"} />
                  </SelectTrigger>
                  <SelectContent>
                    {payloads.map((payload) => (
                      <SelectItem key={payload.id} value={payload.id}>
                        <div className="flex items-center space-x-2">
                          <Badge variant={payload.type === 'visual' ? 'default' : 'secondary'} className="text-xs">
                            {payload.type}
                          </Badge>
                          <span>{payload.name}</span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {selectedPayload && (
                  <div className="p-3 bg-muted rounded-md">
                    <p className="text-sm font-medium">Selected Payload:</p>
                    <p className="text-sm text-muted-foreground">{selectedPayload.name}</p>
                    <Badge variant={selectedPayload.type === 'visual' ? 'default' : 'secondary'} className="text-xs mt-1">
                      {selectedPayload.type === 'visual' ? 'Visual Builder' : 'Python Code'}
                    </Badge>
                  </div>
                )}
                {errors.payload_id && touched.payload_id && (
                  <p className="text-sm text-red-500">{errors.payload_id}</p>
                )}
              </div>

              {/* Target System Selection */}
              <div className="space-y-2">
                <Label className="flex items-center space-x-2">
                  <ServerIcon className="w-4 h-4" />
                  <span>Target System <span className="text-red-500">*</span></span>
                </Label>
                <Select
                  value={values.target_system_id}
                  onValueChange={(value) => handleChange('target_system_id', value)}
                  disabled={targetsLoading}
                >
                  <SelectTrigger className={errors.target_system_id && touched.target_system_id ? 'border-red-500' : ''}>
                    <SelectValue placeholder={targetsLoading ? "Loading targets..." : "Select a target system"} />
                  </SelectTrigger>
                  <SelectContent>
                    {targetSystems.map((target) => (
                      <SelectItem key={target.id} value={target.id}>
                        <div className="flex items-center space-x-2">
                          <Badge variant="outline" className="text-xs">
                            {target.type.toUpperCase()}
                          </Badge>
                          <span>{target.name}</span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {selectedTarget && (
                  <div className="p-3 bg-muted rounded-md">
                    <p className="text-sm font-medium">Selected Target:</p>
                    <p className="text-sm text-muted-foreground">{selectedTarget.name}</p>
                    <Badge variant="outline" className="text-xs mt-1">
                      {selectedTarget.type.toUpperCase()}
                    </Badge>
                  </div>
                )}
                {errors.target_system_id && touched.target_system_id && (
                  <p className="text-sm text-red-500">{errors.target_system_id}</p>
                )}
              </div>
            </div>

            {/* Device Metadata */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Device Metadata</h3>
              <p className="text-sm text-muted-foreground">
                Add custom properties that will be included in the generated payloads
              </p>
              <DeviceMetadataEditor
                metadata={values.metadata}
                onChange={handleMetadataChange}
              />
            </div>

            {/* Form Actions */}
            <div className="flex items-center justify-end space-x-2 pt-4 border-t">
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
                className="min-w-[120px]"
              >
                {isSubmitting ? (
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>{isEditing ? 'Updating...' : 'Creating...'}</span>
                  </div>
                ) : (
                  isEditing ? 'Update Device' : 'Create Device'
                )}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Configuration Validation and Testing - Only show when editing */}
      {isEditing && device && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <DeviceConfigurationValidator
            device={{
              ...device,
              ...values,
              payload: selectedPayload,
              target_system: selectedTarget
            }}
          />
          <DeviceConfigurationTest
            device={{
              ...device,
              ...values,
              payload: selectedPayload,
              target_system: selectedTarget
            }}
          />
        </div>
      )}
    </div>
  )
}