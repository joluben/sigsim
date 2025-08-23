import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import {
    PlusIcon,
    TagIcon,
    TrashIcon
} from '@heroicons/react/24/outline'
import { useState } from 'react'

const METADATA_TYPES = [
    { value: 'string', label: 'Text', icon: '📝' },
    { value: 'number', label: 'Number', icon: '🔢' },
    { value: 'boolean', label: 'Boolean', icon: '✅' },
    { value: 'json', label: 'JSON', icon: '📋' }
]

export default function DeviceMetadataEditor({ metadata = {}, onChange }) {
    const [newKey, setNewKey] = useState('')
    const [newValue, setNewValue] = useState('')
    const [newType, setNewType] = useState('string')
    const [editingKey, setEditingKey] = useState(null)

    const metadataEntries = Object.entries(metadata)

    const handleAddProperty = () => {
        if (!newKey.trim()) return

        let processedValue = newValue

        // Process value based on type
        switch (newType) {
            case 'number':
                processedValue = parseFloat(newValue) || 0
                break
            case 'boolean':
                processedValue = newValue.toLowerCase() === 'true'
                break
            case 'json':
                try {
                    processedValue = JSON.parse(newValue)
                } catch {
                    processedValue = newValue
                }
                break
            default:
                processedValue = newValue
        }

        const updatedMetadata = {
            ...metadata,
            [newKey]: processedValue
        }

        onChange(updatedMetadata)
        setNewKey('')
        setNewValue('')
        setNewType('string')
    }

    const handleRemoveProperty = (key) => {
        const updatedMetadata = { ...metadata }
        delete updatedMetadata[key]
        onChange(updatedMetadata)
    }

    const handleUpdateProperty = (oldKey, newKey, newValue) => {
        const updatedMetadata = { ...metadata }

        if (oldKey !== newKey) {
            delete updatedMetadata[oldKey]
        }

        updatedMetadata[newKey] = newValue
        onChange(updatedMetadata)
        setEditingKey(null)
    }



    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center space-x-2 text-base">
                    <TagIcon className="w-4 h-4" />
                    <span>Device Properties</span>
                </CardTitle>
            </CardHeader>

            <CardContent className="space-y-4">
                {/* Existing Properties */}
                {metadataEntries.length > 0 && (
                    <div className="space-y-2">
                        <Label className="text-sm font-medium">Current Properties</Label>
                        <div className="space-y-2">
                            {metadataEntries.map(([key, value]) => (
                                <PropertyItem
                                    key={key}
                                    propertyKey={key}
                                    value={value}
                                    isEditing={editingKey === key}
                                    onEdit={() => setEditingKey(key)}
                                    onSave={(newKey, newValue) => handleUpdateProperty(key, newKey, newValue)}
                                    onCancel={() => setEditingKey(null)}
                                    onRemove={() => handleRemoveProperty(key)}
                                />
                            ))}
                        </div>
                    </div>
                )}

                {/* Add New Property */}
                <div className="space-y-3 p-4 border rounded-lg bg-muted/50">
                    <Label className="text-sm font-medium">Add New Property</Label>

                    <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                        <div className="space-y-1">
                            <Label className="text-xs">Property Name</Label>
                            <Input
                                placeholder="e.g., deviceId"
                                value={newKey}
                                onChange={(e) => setNewKey(e.target.value)}
                                className="h-8"
                            />
                        </div>

                        <div className="space-y-1">
                            <Label className="text-xs">Type</Label>
                            <Select value={newType} onValueChange={setNewType}>
                                <SelectTrigger className="h-8">
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    {METADATA_TYPES.map((type) => (
                                        <SelectItem key={type.value} value={type.value}>
                                            <div className="flex items-center space-x-2">
                                                <span>{type.icon}</span>
                                                <span>{type.label}</span>
                                            </div>
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="space-y-1">
                            <Label className="text-xs">Value</Label>
                            <Input
                                placeholder={getPlaceholderForType(newType)}
                                value={newValue}
                                onChange={(e) => setNewValue(e.target.value)}
                                className="h-8"
                            />
                        </div>

                        <div className="space-y-1">
                            <Label className="text-xs opacity-0">Action</Label>
                            <Button
                                type="button"
                                size="sm"
                                onClick={handleAddProperty}
                                disabled={!newKey.trim()}
                                className="h-8 w-full"
                            >
                                <PlusIcon className="w-3 h-3 mr-1" />
                                Add
                            </Button>
                        </div>
                    </div>
                </div>

                {/* Help Text */}
                <div className="text-xs text-muted-foreground space-y-1">
                    <p>• Properties will be available in payload generators as <code>device_metadata.propertyName</code></p>
                    <p>• JSON values should be valid JSON format (e.g., {`{"lat": 40.7128, "lng": -74.0060}`})</p>
                    <p>• Boolean values should be "true" or "false"</p>
                </div>
            </CardContent>
        </Card>
    )
}

// Helper functions moved outside component to avoid scope issues
function getValueType(value) {
    if (typeof value === 'boolean') return 'boolean'
    if (typeof value === 'number') return 'number'
    if (typeof value === 'object') return 'json'
    return 'string'
}

function formatValue(value) {
    if (typeof value === 'object') {
        return JSON.stringify(value, null, 2)
    }
    return String(value)
}

function getPlaceholderForType(type) {
    switch (type) {
        case 'string':
            return 'Enter text value'
        case 'number':
            return 'Enter number'
        case 'boolean':
            return 'true or false'
        case 'json':
            return '{"key": "value"}'
        default:
            return 'Enter value'
    }
}

function PropertyItem({
    propertyKey,
    value,
    isEditing,
    onEdit,
    onSave,
    onCancel,
    onRemove
}) {
    const [editKey, setEditKey] = useState(propertyKey)
    const [editValue, setEditValue] = useState(formatValue(value))

    const valueType = getValueType(value)
    const typeInfo = METADATA_TYPES.find(t => t.value === valueType)

    const handleSave = () => {
        let processedValue = editValue

        switch (valueType) {
            case 'number':
                processedValue = parseFloat(editValue) || 0
                break
            case 'boolean':
                processedValue = editValue.toLowerCase() === 'true'
                break
            case 'json':
                try {
                    processedValue = JSON.parse(editValue)
                } catch {
                    processedValue = editValue
                }
                break
            default:
                processedValue = editValue
        }

        onSave(editKey, processedValue)
    }

    if (isEditing) {
        return (
            <div className="flex items-center space-x-2 p-2 border rounded-lg bg-background">
                <Input
                    value={editKey}
                    onChange={(e) => setEditKey(e.target.value)}
                    className="h-8 flex-1"
                    placeholder="Property name"
                />
                <Badge variant="outline" className="text-xs">
                    {typeInfo?.icon} {typeInfo?.label}
                </Badge>
                <Input
                    value={editValue}
                    onChange={(e) => setEditValue(e.target.value)}
                    className="h-8 flex-2"
                    placeholder="Value"
                />
                <Button size="sm" onClick={handleSave} className="h-8">
                    Save
                </Button>
                <Button size="sm" variant="outline" onClick={onCancel} className="h-8">
                    Cancel
                </Button>
            </div>
        )
    }

    return (
        <div className="flex items-center justify-between p-2 border rounded-lg bg-background hover:bg-muted/50 transition-colors">
            <div className="flex items-center space-x-3 flex-1">
                <Badge variant="outline" className="text-xs">
                    {typeInfo?.icon} {typeInfo?.label}
                </Badge>
                <div className="flex-1">
                    <span className="font-medium text-sm">{propertyKey}</span>
                    <div className="text-xs text-muted-foreground truncate max-w-xs">
                        {formatValue(value)}
                    </div>
                </div>
            </div>

            <div className="flex items-center space-x-1">
                <Button size="sm" variant="ghost" onClick={onEdit} className="h-7 w-7 p-0">
                    <TagIcon className="w-3 h-3" />
                </Button>
                <Button
                    size="sm"
                    variant="ghost"
                    onClick={onRemove}
                    className="h-7 w-7 p-0 text-red-600 hover:text-red-700"
                >
                    <TrashIcon className="w-3 h-3" />
                </Button>
            </div>
        </div>
    )
}