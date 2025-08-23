import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectItem } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { useNotificationContext } from '@/components/providers/NotificationProvider'
import {
    useCreateTargetSystem,
    useTargetSystemConfigSchema,
    useTargetSystemTypes,
    useTestTargetSystemConnectionConfig,
    useUpdateTargetSystem
} from '@/hooks/useTargetSystems'
import { CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline'
import { useEffect, useState } from 'react'

const TARGET_TYPE_DESCRIPTIONS = {
    http: 'Envía datos a endpoints HTTP/HTTPS usando requests REST',
    mqtt: 'Publica mensajes a brokers MQTT para comunicación IoT',
    kafka: 'Envía eventos a tópicos de Apache Kafka para streaming',
    websocket: 'Mantiene conexiones WebSocket para datos en tiempo real',
    ftp: 'Sube archivos a servidores FTP/SFTP',
    pubsub: 'Integra con sistemas Pub/Sub como Google Cloud, AWS SNS/SQS'
}

export default function TargetSystemForm({ targetSystem, onClose }) {
    const [formData, setFormData] = useState({
        name: '',
        type: '',
        config: {}
    })
    const [testResult, setTestResult] = useState(null)
    const [isTestingConnection, setIsTestingConnection] = useState(false)

    const { data: supportedTypes = [] } = useTargetSystemTypes()
    const { data: configSchema } = useTargetSystemConfigSchema(formData.type)
    const createTargetSystem = useCreateTargetSystem()
    const updateTargetSystem = useUpdateTargetSystem()
    const testConnectionConfig = useTestTargetSystemConnectionConfig()
    const { showSuccess, showError, showWarning } = useNotificationContext()

    // Initialize form data when editing
    useEffect(() => {
        if (targetSystem) {
            setFormData({
                name: targetSystem.name || '',
                type: targetSystem.type || '',
                config: targetSystem.config || {}
            })
        }
    }, [targetSystem])

    const handleInputChange = (field, value) => {
        if (field.startsWith('config.')) {
            const configField = field.replace('config.', '')
            setFormData(prev => ({
                ...prev,
                config: {
                    ...prev.config,
                    [configField]: value
                }
            }))
        } else {
            setFormData(prev => ({
                ...prev,
                [field]: value
            }))
        }
        // Clear test result when config changes
        setTestResult(null)
    }

    const handleTypeChange = (newType) => {
        setFormData(prev => ({
            ...prev,
            type: newType,
            config: {} // Reset config when type changes
        }))
        setTestResult(null)
    }

    const handleTestConnection = async () => {
        if (!formData.type || Object.keys(formData.config).length === 0) {
            showWarning('Completa la configuración antes de probar la conexión')
            return
        }

        setIsTestingConnection(true)
        setTestResult(null)

        try {
            const result = await testConnectionConfig.mutateAsync({
                type: formData.type,
                config: formData.config
            })
            setTestResult(result)

            if (result.success) {
                showSuccess('Conexión exitosa')
            } else {
                showError(`Error de conexión: ${result.error}`)
            }
        } catch (error) {
            setTestResult({
                success: false,
                error: error.message || 'Error desconocido'
            })
            showError('Error al probar la conexión')
        } finally {
            setIsTestingConnection(false)
        }
    }

    const handleSubmit = async (e) => {
        e.preventDefault()

        if (!formData.name.trim()) {
            showError('El nombre es requerido')
            return
        }

        if (!formData.type) {
            showError('Selecciona un tipo de target system')
            return
        }

        try {
            if (targetSystem) {
                await updateTargetSystem.mutateAsync({
                    id: targetSystem.id,
                    ...formData
                })
                showSuccess('Target system actualizado exitosamente')
            } else {
                await createTargetSystem.mutateAsync(formData)
                showSuccess('Target system creado exitosamente')
            }
            onClose()
        } catch (error) {
            showError(`Error al ${targetSystem ? 'actualizar' : 'crear'} target system: ${error.message}`)
        }
    }

    const renderConfigFields = () => {
        if (!configSchema?.schema?.properties) {
            return null
        }

        const properties = configSchema.schema.properties
        const required = configSchema.schema.required || []

        return Object.entries(properties).map(([fieldName, fieldSchema]) => {
            const isRequired = required.includes(fieldName)
            const currentValue = formData.config[fieldName] || ''

            // Handle different field types
            if (fieldSchema.enum) {
                return (
                    <div key={fieldName} className="space-y-2">
                        <Label htmlFor={fieldName}>
                            {fieldSchema.title || fieldName}
                            {isRequired && <span className="text-red-500 ml-1">*</span>}
                        </Label>
                        <Select
                            value={currentValue}
                            onValueChange={(value) => handleInputChange(`config.${fieldName}`, value)}
                            placeholder={`Selecciona ${fieldSchema.title || fieldName}`}
                        >
                            {({ onSelect, selectedValue }) => (
                                <>
                                    {fieldSchema.enum.map((option) => (
                                        <SelectItem
                                            key={option}
                                            value={option}
                                            onSelect={onSelect}
                                            selectedValue={selectedValue}
                                        >
                                            {option}
                                        </SelectItem>
                                    ))}
                                </>
                            )}
                        </Select>
                        {fieldSchema.description && (
                            <p className="text-sm text-muted-foreground">{fieldSchema.description}</p>
                        )}
                    </div>
                )
            }

            if (fieldSchema.type === 'boolean') {
                return (
                    <div key={fieldName} className="space-y-2">
                        <Label htmlFor={fieldName}>
                            {fieldSchema.title || fieldName}
                            {isRequired && <span className="text-red-500 ml-1">*</span>}
                        </Label>
                        <Select
                            value={currentValue.toString()}
                            onValueChange={(value) => handleInputChange(`config.${fieldName}`, value === 'true')}
                            placeholder="Selecciona una opción"
                        >
                            {({ onSelect, selectedValue }) => (
                                <>
                                    <SelectItem
                                        value="false"
                                        onSelect={onSelect}
                                        selectedValue={selectedValue}
                                    >
                                        No
                                    </SelectItem>
                                    <SelectItem
                                        value="true"
                                        onSelect={onSelect}
                                        selectedValue={selectedValue}
                                    >
                                        Sí
                                    </SelectItem>
                                </>
                            )}
                        </Select>
                        {fieldSchema.description && (
                            <p className="text-sm text-muted-foreground">{fieldSchema.description}</p>
                        )}
                    </div>
                )
            }

            if (fieldSchema.type === 'integer' || fieldSchema.type === 'number') {
                return (
                    <div key={fieldName} className="space-y-2">
                        <Label htmlFor={fieldName}>
                            {fieldSchema.title || fieldName}
                            {isRequired && <span className="text-red-500 ml-1">*</span>}
                        </Label>
                        <Input
                            id={fieldName}
                            type="number"
                            value={currentValue}
                            onChange={(e) => handleInputChange(`config.${fieldName}`,
                                fieldSchema.type === 'integer' ? parseInt(e.target.value) || '' : parseFloat(e.target.value) || ''
                            )}
                            placeholder={fieldSchema.description || `Ingresa ${fieldSchema.title || fieldName}`}
                            min={fieldSchema.minimum}
                            max={fieldSchema.maximum}
                        />
                        {fieldSchema.description && (
                            <p className="text-sm text-muted-foreground">{fieldSchema.description}</p>
                        )}
                    </div>
                )
            }

            // Default to text input
            const isLongText = fieldSchema.description?.includes('JSON') || fieldName.includes('headers')

            if (isLongText) {
                return (
                    <div key={fieldName} className="space-y-2">
                        <Label htmlFor={fieldName}>
                            {fieldSchema.title || fieldName}
                            {isRequired && <span className="text-red-500 ml-1">*</span>}
                        </Label>
                        <Textarea
                            id={fieldName}
                            value={typeof currentValue === 'object' ? JSON.stringify(currentValue, null, 2) : currentValue}
                            onChange={(e) => {
                                let value = e.target.value
                                // Try to parse JSON for object fields
                                if (fieldName.includes('headers') || fieldSchema.type === 'object') {
                                    try {
                                        value = JSON.parse(value)
                                    } catch {
                                        // Keep as string if not valid JSON
                                    }
                                }
                                handleInputChange(`config.${fieldName}`, value)
                            }}
                            placeholder={fieldSchema.description || `Ingresa ${fieldSchema.title || fieldName}`}
                            rows={3}
                        />
                        {fieldSchema.description && (
                            <p className="text-sm text-muted-foreground">{fieldSchema.description}</p>
                        )}
                    </div>
                )
            }

            return (
                <div key={fieldName} className="space-y-2">
                    <Label htmlFor={fieldName}>
                        {fieldSchema.title || fieldName}
                        {isRequired && <span className="text-red-500 ml-1">*</span>}
                    </Label>
                    <Input
                        id={fieldName}
                        type={fieldSchema.format === 'password' ? 'password' : 'text'}
                        value={currentValue}
                        onChange={(e) => handleInputChange(`config.${fieldName}`, e.target.value)}
                        placeholder={fieldSchema.description || `Ingresa ${fieldSchema.title || fieldName}`}
                    />
                    {fieldSchema.description && (
                        <p className="text-sm text-muted-foreground">{fieldSchema.description}</p>
                    )}
                </div>
            )
        })
    }

    const isLoading = createTargetSystem.isLoading || updateTargetSystem.isLoading

    return (
        <form onSubmit={handleSubmit} className="space-y-6">
            {/* Basic Information */}
            <div className="space-y-4">
                <div className="space-y-2">
                    <Label htmlFor="name">
                        Nombre <span className="text-red-500">*</span>
                    </Label>
                    <Input
                        id="name"
                        value={formData.name}
                        onChange={(e) => handleInputChange('name', e.target.value)}
                        placeholder="Nombre descriptivo del target system"
                        required
                    />
                </div>

                <div className="space-y-2">
                    <Label htmlFor="type">
                        Tipo <span className="text-red-500">*</span>
                    </Label>
                    <Select
                        value={formData.type}
                        onValueChange={handleTypeChange}
                        placeholder="Selecciona el tipo de target system"
                    >
                        {({ onSelect, selectedValue }) => (
                            <>
                                {supportedTypes.map((type) => (
                                    <SelectItem
                                        key={type}
                                        value={type}
                                        onSelect={onSelect}
                                        selectedValue={selectedValue}
                                    >
                                        {type.toUpperCase()}
                                    </SelectItem>
                                ))}
                            </>
                        )}
                    </Select>
                    {formData.type && TARGET_TYPE_DESCRIPTIONS[formData.type] && (
                        <p className="text-sm text-muted-foreground">
                            {TARGET_TYPE_DESCRIPTIONS[formData.type]}
                        </p>
                    )}
                </div>
            </div>

            {/* Configuration Fields */}
            {formData.type && (
                <Card>
                    <CardHeader>
                        <CardTitle>Configuración de {formData.type.toUpperCase()}</CardTitle>
                        <CardDescription>
                            Configura los parámetros específicos para este tipo de target system
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        {renderConfigFields()}
                    </CardContent>
                </Card>
            )}

            {/* Connection Test */}
            {formData.type && Object.keys(formData.config).length > 0 && (
                <Card>
                    <CardHeader>
                        <CardTitle>Probar Conexión</CardTitle>
                        <CardDescription>
                            Verifica que la configuración sea correcta antes de guardar
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <Button
                            type="button"
                            variant="outline"
                            onClick={handleTestConnection}
                            disabled={isTestingConnection}
                            className="w-full"
                        >
                            {isTestingConnection ? (
                                <>
                                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2"></div>
                                    Probando conexión...
                                </>
                            ) : (
                                'Probar Conexión'
                            )}
                        </Button>

                        {testResult && (
                            <div className={`p-4 rounded-lg border ${testResult.success
                                ? 'bg-green-50 border-green-200 text-green-800'
                                : 'bg-red-50 border-red-200 text-red-800'
                                }`}>
                                <div className="flex items-center space-x-2">
                                    {testResult.success ? (
                                        <CheckCircleIcon className="w-5 h-5" />
                                    ) : (
                                        <XCircleIcon className="w-5 h-5" />
                                    )}
                                    <span className="font-medium">
                                        {testResult.success ? 'Conexión exitosa' : 'Error de conexión'}
                                    </span>
                                </div>
                                {testResult.message && (
                                    <p className="mt-2 text-sm">{testResult.message}</p>
                                )}
                                {testResult.error && (
                                    <p className="mt-2 text-sm">{testResult.error}</p>
                                )}
                                {testResult.details && (
                                    <p className="mt-1 text-xs opacity-75">{testResult.details}</p>
                                )}
                            </div>
                        )}
                    </CardContent>
                </Card>
            )}

            {/* Form Actions */}
            <div className="flex justify-end space-x-2 pt-4 border-t">
                <Button type="button" variant="outline" onClick={onClose}>
                    Cancelar
                </Button>
                <Button type="submit" disabled={isLoading}>
                    {isLoading ? (
                        <>
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2"></div>
                            {targetSystem ? 'Actualizando...' : 'Creando...'}
                        </>
                    ) : (
                        targetSystem ? 'Actualizar' : 'Crear'
                    )}
                </Button>
            </div>
        </form>
    )
}