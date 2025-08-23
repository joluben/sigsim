import { Code, Layers, Save, X } from 'lucide-react';
import React, { useEffect, useState } from 'react';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Textarea } from '../ui/textarea';
import PayloadBuilder from './PayloadBuilder';

const PayloadForm = ({
    payload = null,
    onSave,
    onCancel,
    className = ""
}) => {
    const [formData, setFormData] = useState({
        name: '',
        description: '',
        type: 'visual',
        schema: { fields: [] },
        python_code: ''
    });
    const [errors, setErrors] = useState({});
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Initialize form data when payload prop changes
    useEffect(() => {
        if (payload) {
            setFormData({
                name: payload.name || '',
                description: payload.description || '',
                type: payload.type || 'visual',
                schema: payload.schema || { fields: [] },
                python_code: payload.python_code || ''
            });
        } else {
            setFormData({
                name: '',
                description: '',
                type: 'visual',
                schema: { fields: [] },
                python_code: ''
            });
        }
    }, [payload]);

    // Validate form
    const validateForm = () => {
        const newErrors = {};

        // Validate name
        if (!formData.name.trim()) {
            newErrors.name = 'Payload name is required';
        } else if (formData.name.length < 3) {
            newErrors.name = 'Payload name must be at least 3 characters';
        }

        // Validate based on type
        if (formData.type === 'visual') {
            if (!formData.schema.fields || formData.schema.fields.length === 0) {
                newErrors.schema = 'At least one field is required for visual payloads';
            }
        } else if (formData.type === 'python') {
            if (!formData.python_code.trim()) {
                newErrors.python_code = 'Python code is required for Python payloads';
            }
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    // Handle form submission
    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!validateForm()) {
            return;
        }

        setIsSubmitting(true);

        try {
            await onSave?.(formData);
        } catch (error) {
            console.error('Error saving payload:', error);
            setErrors({ submit: 'Failed to save payload. Please try again.' });
        } finally {
            setIsSubmitting(false);
        }
    };

    // Handle input changes
    const handleInputChange = (field, value) => {
        setFormData(prev => ({ ...prev, [field]: value }));

        // Clear error for this field
        if (errors[field]) {
            setErrors(prev => ({ ...prev, [field]: null }));
        }
    };

    // Handle schema changes from PayloadBuilder
    const handleSchemaChange = (newSchema) => {
        setFormData(prev => ({ ...prev, schema: newSchema }));

        // Clear schema error
        if (errors.schema) {
            setErrors(prev => ({ ...prev, schema: null }));
        }
    };

    // Handle type change
    const handleTypeChange = (newType) => {
        setFormData(prev => ({
            ...prev,
            type: newType,
            // Reset type-specific data when switching
            schema: newType === 'visual' ? prev.schema : { fields: [] },
            python_code: newType === 'python' ? prev.python_code : ''
        }));

        // Clear type-specific errors
        setErrors(prev => ({
            ...prev,
            schema: null,
            python_code: null
        }));
    };

    return (
        <div className={`space-y-6 ${className}`}>
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold">
                        {payload ? 'Edit Payload' : 'Create New Payload'}
                    </h2>
                    <p className="text-gray-600 mt-1">
                        {payload ? 'Modify your payload template' : 'Create a new payload template for your IoT devices'}
                    </p>
                </div>
                <div className="flex items-center gap-2">
                    <Button variant="outline" onClick={onCancel}>
                        <X className="w-4 h-4 mr-2" />
                        Cancel
                    </Button>
                    <Button
                        onClick={handleSubmit}
                        disabled={isSubmitting}
                        className="min-w-[100px]"
                    >
                        {isSubmitting ? (
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        ) : (
                            <>
                                <Save className="w-4 h-4 mr-2" />
                                {payload ? 'Update' : 'Create'}
                            </>
                        )}
                    </Button>
                </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
                {/* Basic Information */}
                <Card>
                    <CardHeader>
                        <CardTitle className="text-lg">Basic Information</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <Label htmlFor="payload-name">Payload Name *</Label>
                                <Input
                                    id="payload-name"
                                    value={formData.name}
                                    onChange={(e) => handleInputChange('name', e.target.value)}
                                    placeholder="e.g., Temperature Sensor Data"
                                    className={errors.name ? 'border-red-500' : ''}
                                />
                                {errors.name && (
                                    <p className="text-sm text-red-600 mt-1">{errors.name}</p>
                                )}
                            </div>

                            <div>
                                <Label htmlFor="payload-type">Payload Type *</Label>
                                <Select
                                    value={formData.type}
                                    onValueChange={handleTypeChange}
                                >
                                    <SelectTrigger>
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="visual">
                                            <div className="flex items-center gap-2">
                                                <Layers className="w-4 h-4" />
                                                Visual Builder
                                            </div>
                                        </SelectItem>
                                        <SelectItem value="python">
                                            <div className="flex items-center gap-2">
                                                <Code className="w-4 h-4" />
                                                Python Code
                                            </div>
                                        </SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>
                        </div>

                        <div>
                            <Label htmlFor="payload-description">Description</Label>
                            <Textarea
                                id="payload-description"
                                value={formData.description}
                                onChange={(e) => handleInputChange('description', e.target.value)}
                                placeholder="Optional description of this payload template..."
                                rows={3}
                            />
                        </div>
                    </CardContent>
                </Card>

                {/* Payload Configuration */}
                <Card>
                    <CardHeader>
                        <div className="flex items-center justify-between">
                            <CardTitle className="text-lg">Payload Configuration</CardTitle>
                            <Badge
                                variant="secondary"
                                className={formData.type === 'visual' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'}
                            >
                                {formData.type === 'visual' ? (
                                    <><Layers className="w-3 h-3 mr-1" /> Visual</>
                                ) : (
                                    <><Code className="w-3 h-3 mr-1" /> Python</>
                                )}
                            </Badge>
                        </div>
                    </CardHeader>
                    <CardContent>
                        {formData.type === 'visual' ? (
                            <div>
                                <PayloadBuilder
                                    schema={formData.schema}
                                    onChange={handleSchemaChange}
                                />
                                {errors.schema && (
                                    <p className="text-sm text-red-600 mt-2">{errors.schema}</p>
                                )}
                            </div>
                        ) : (
                            <div>
                                <PythonCodeEditor
                                    code={formData.python_code}
                                    onChange={(code) => handleInputChange('python_code', code)}
                                    onValidate={(isValid, validationErrors) => {
                                        if (!isValid && validationErrors.some(e => e.severity === 'error')) {
                                            setErrors(prev => ({
                                                ...prev,
                                                python_code: 'Code contains errors that must be fixed'
                                            }));
                                        } else {
                                            setErrors(prev => ({
                                                ...prev,
                                                python_code: null
                                            }));
                                        }
                                    }}
                                    height="500px"
                                    showPreview={true}
                                    deviceMetadata={{
                                        device_id: 'preview-device',
                                        location: 'Test Lab'
                                    }}
                                />
                                {errors.python_code && (
                                    <p className="text-sm text-red-600 mt-2">{errors.python_code}</p>
                                )}
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* Submit Error */}
                {errors.submit && (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                        <p className="text-sm text-red-600">{errors.submit}</p>
                    </div>
                )}
            </form>
        </div>
    );
};

export default PayloadForm;