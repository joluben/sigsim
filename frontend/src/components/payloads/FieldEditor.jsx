import React, { useEffect, useState } from 'react';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from '../ui/dialog';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Textarea } from '../ui/textarea';

const FieldEditor = ({
    field,
    onSave,
    onCancel,
    existingFieldNames = []
}) => {
    const [formData, setFormData] = useState({
        name: '',
        type: 'string',
        generator: {
            type: 'fixed',
            value: ''
        }
    });
    const [errors, setErrors] = useState({});

    // Initialize form data when field prop changes
    useEffect(() => {
        if (field) {
            setFormData({
                name: field.name || '',
                type: field.type || 'string',
                generator: field.generator || {
                    type: 'fixed',
                    value: ''
                }
            });
        }
    }, [field]);

    // Validate form
    const validateForm = () => {
        const newErrors = {};

        // Validate field name
        if (!formData.name.trim()) {
            newErrors.name = 'Field name is required';
        } else if (!/^[a-zA-Z_][a-zA-Z0-9_]*$/.test(formData.name)) {
            newErrors.name = 'Field name must be a valid identifier';
        } else if (existingFieldNames.includes(formData.name)) {
            newErrors.name = 'Field name already exists';
        }

        // Validate generator based on type
        const { type, generator } = formData;

        if (type === 'string' && generator.type === 'fixed' && !generator.value) {
            newErrors.generator = 'Fixed value is required';
        }

        if (type === 'string' && generator.type === 'random_choice') {
            if (!generator.choices || generator.choices.length === 0) {
                newErrors.generator = 'At least one choice is required';
            }
        }

        if (type === 'string' && generator.type === 'random_string') {
            if (!generator.length || generator.length < 1) {
                newErrors.generator = 'Length must be at least 1';
            }
        }

        if (type === 'number' && generator.type === 'fixed') {
            if (generator.value === '' || generator.value === null || generator.value === undefined) {
                newErrors.generator = 'Fixed value is required';
            }
        }

        if (type === 'number' && (generator.type === 'random_int' || generator.type === 'random_float')) {
            if (generator.min === '' || generator.min === null || generator.min === undefined) {
                newErrors.generator = 'Minimum value is required';
            }
            if (generator.max === '' || generator.max === null || generator.max === undefined) {
                newErrors.generator = 'Maximum value is required';
            }
            if (generator.min >= generator.max) {
                newErrors.generator = 'Maximum must be greater than minimum';
            }
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    // Handle form submission
    const handleSubmit = (e) => {
        e.preventDefault();
        if (validateForm()) {
            onSave(formData);
        }
    };

    // Update field name
    const handleNameChange = (value) => {
        setFormData(prev => ({ ...prev, name: value }));
        if (errors.name) {
            setErrors(prev => ({ ...prev, name: null }));
        }
    };

    // Update field type
    const handleTypeChange = (type) => {
        let defaultGenerator;

        switch (type) {
            case 'string':
                defaultGenerator = { type: 'fixed', value: '' };
                break;
            case 'number':
                defaultGenerator = { type: 'fixed', value: 0 };
                break;
            case 'boolean':
                defaultGenerator = { type: 'fixed', value: true };
                break;
            case 'uuid':
            case 'timestamp':
                defaultGenerator = {};
                break;
            default:
                defaultGenerator = { type: 'fixed', value: '' };
        }

        setFormData(prev => ({
            ...prev,
            type,
            generator: defaultGenerator
        }));
    };

    // Update generator configuration
    const handleGeneratorChange = (key, value) => {
        setFormData(prev => ({
            ...prev,
            generator: {
                ...prev.generator,
                [key]: value
            }
        }));
        if (errors.generator) {
            setErrors(prev => ({ ...prev, generator: null }));
        }
    };

    // Render generator configuration based on type
    const renderGeneratorConfig = () => {
        const { type, generator } = formData;

        if (type === 'uuid' || type === 'timestamp') {
            return (
                <Card>
                    <CardContent className="pt-4">
                        <p className="text-sm text-gray-600">
                            {type === 'uuid' ? 'UUIDs are automatically generated' : 'Timestamps use current time'}
                        </p>
                    </CardContent>
                </Card>
            );
        }

        return (
            <Card>
                <CardHeader>
                    <CardTitle className="text-sm">Generator Configuration</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    {/* Generator Type Selection */}
                    <div>
                        <Label htmlFor="generator-type">Generator Type</Label>
                        <Select
                            value={generator.type}
                            onValueChange={(value) => handleGeneratorChange('type', value)}
                        >
                            <SelectTrigger>
                                <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="fixed">Fixed Value</SelectItem>
                                {type === 'string' && (
                                    <>
                                        <SelectItem value="random_choice">Random Choice</SelectItem>
                                        <SelectItem value="random_string">Random String</SelectItem>
                                    </>
                                )}
                                {type === 'number' && (
                                    <>
                                        <SelectItem value="random_int">Random Integer</SelectItem>
                                        <SelectItem value="random_float">Random Float</SelectItem>
                                    </>
                                )}
                                {type === 'boolean' && (
                                    <SelectItem value="random">Random Boolean</SelectItem>
                                )}
                            </SelectContent>
                        </Select>
                    </div>

                    {/* Generator-specific configuration */}
                    {generator.type === 'fixed' && (
                        <div>
                            <Label htmlFor="fixed-value">Fixed Value</Label>
                            {type === 'string' ? (
                                <Input
                                    id="fixed-value"
                                    value={generator.value || ''}
                                    onChange={(e) => handleGeneratorChange('value', e.target.value)}
                                    placeholder="Enter fixed value"
                                />
                            ) : type === 'number' ? (
                                <Input
                                    id="fixed-value"
                                    type="number"
                                    value={generator.value || ''}
                                    onChange={(e) => handleGeneratorChange('value', parseFloat(e.target.value) || 0)}
                                    placeholder="Enter fixed number"
                                />
                            ) : type === 'boolean' ? (
                                <Select
                                    value={generator.value?.toString()}
                                    onValueChange={(value) => handleGeneratorChange('value', value === 'true')}
                                >
                                    <SelectTrigger>
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="true">True</SelectItem>
                                        <SelectItem value="false">False</SelectItem>
                                    </SelectContent>
                                </Select>
                            ) : null}
                        </div>
                    )}

                    {generator.type === 'random_choice' && (
                        <div>
                            <Label htmlFor="choices">Choices (one per line)</Label>
                            <Textarea
                                id="choices"
                                value={generator.choices?.join('\n') || ''}
                                onChange={(e) => handleGeneratorChange('choices', e.target.value.split('\n').filter(c => c.trim()))}
                                placeholder="option1&#10;option2&#10;option3"
                                rows={4}
                            />
                        </div>
                    )}

                    {generator.type === 'random_string' && (
                        <div>
                            <Label htmlFor="string-length">String Length</Label>
                            <Input
                                id="string-length"
                                type="number"
                                min="1"
                                max="1000"
                                value={generator.length || 10}
                                onChange={(e) => handleGeneratorChange('length', parseInt(e.target.value) || 10)}
                            />
                        </div>
                    )}

                    {(generator.type === 'random_int' || generator.type === 'random_float') && (
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <Label htmlFor="min-value">Minimum</Label>
                                <Input
                                    id="min-value"
                                    type="number"
                                    step={generator.type === 'random_float' ? '0.01' : '1'}
                                    value={generator.min || ''}
                                    onChange={(e) => handleGeneratorChange('min', parseFloat(e.target.value) || 0)}
                                />
                            </div>
                            <div>
                                <Label htmlFor="max-value">Maximum</Label>
                                <Input
                                    id="max-value"
                                    type="number"
                                    step={generator.type === 'random_float' ? '0.01' : '1'}
                                    value={generator.max || ''}
                                    onChange={(e) => handleGeneratorChange('max', parseFloat(e.target.value) || 100)}
                                />
                            </div>
                            {generator.type === 'random_float' && (
                                <div className="col-span-2">
                                    <Label htmlFor="decimals">Decimal Places</Label>
                                    <Input
                                        id="decimals"
                                        type="number"
                                        min="0"
                                        max="10"
                                        value={generator.decimals || 2}
                                        onChange={(e) => handleGeneratorChange('decimals', parseInt(e.target.value) || 2)}
                                    />
                                </div>
                            )}
                        </div>
                    )}
                </CardContent>
            </Card>
        );
    };

    return (
        <Dialog open={true} onOpenChange={onCancel}>
            <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                    <DialogTitle>
                        {field?._index !== undefined ? 'Edit Field' : 'Add New Field'}
                    </DialogTitle>
                </DialogHeader>

                <form onSubmit={handleSubmit} className="space-y-6">
                    {/* Basic Field Configuration */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-sm">Basic Configuration</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div>
                                <Label htmlFor="field-name">Field Name</Label>
                                <Input
                                    id="field-name"
                                    value={formData.name}
                                    onChange={(e) => handleNameChange(e.target.value)}
                                    placeholder="e.g., temperature, device_id"
                                    className={errors.name ? 'border-red-500' : ''}
                                />
                                {errors.name && (
                                    <p className="text-sm text-red-600 mt-1">{errors.name}</p>
                                )}
                            </div>

                            <div>
                                <Label htmlFor="field-type">Field Type</Label>
                                <Select
                                    value={formData.type}
                                    onValueChange={handleTypeChange}
                                >
                                    <SelectTrigger>
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="string">String</SelectItem>
                                        <SelectItem value="number">Number</SelectItem>
                                        <SelectItem value="boolean">Boolean</SelectItem>
                                        <SelectItem value="uuid">UUID</SelectItem>
                                        <SelectItem value="timestamp">Timestamp</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Generator Configuration */}
                    {renderGeneratorConfig()}

                    {errors.generator && (
                        <p className="text-sm text-red-600">{errors.generator}</p>
                    )}

                    <DialogFooter>
                        <Button type="button" variant="outline" onClick={onCancel}>
                            Cancel
                        </Button>
                        <Button type="submit">
                            {field?._index !== undefined ? 'Update Field' : 'Add Field'}
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    );
};

export default FieldEditor;