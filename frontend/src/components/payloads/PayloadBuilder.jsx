import { Edit, GripVertical, Plus, Trash2 } from 'lucide-react';
import React, { useCallback, useState } from 'react';
import { DragDropContext, Draggable, Droppable } from 'react-beautiful-dnd';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import FieldEditor from './FieldEditor';
import PayloadPreview from './PayloadPreview';

const PayloadBuilder = ({
    schema = { fields: [] },
    onChange,
    className = ""
}) => {
    const [fields, setFields] = useState(schema.fields || []);
    const [editingField, setEditingField] = useState(null);
    const [showFieldEditor, setShowFieldEditor] = useState(false);

    // Handle drag and drop reordering
    const handleDragEnd = useCallback((result) => {
        if (!result.destination) return;

        const newFields = Array.from(fields);
        const [reorderedField] = newFields.splice(result.source.index, 1);
        newFields.splice(result.destination.index, 0, reorderedField);

        setFields(newFields);
        onChange?.({ ...schema, fields: newFields });
    }, [fields, schema, onChange]);

    // Add new field
    const handleAddField = useCallback(() => {
        setEditingField({
            name: '',
            type: 'string',
            generator: {
                type: 'fixed',
                value: ''
            }
        });
        setShowFieldEditor(true);
    }, []);

    // Edit existing field
    const handleEditField = useCallback((index) => {
        setEditingField({ ...fields[index], _index: index });
        setShowFieldEditor(true);
    }, [fields]);

    // Delete field
    const handleDeleteField = useCallback((index) => {
        const newFields = fields.filter((_, i) => i !== index);
        setFields(newFields);
        onChange?.({ ...schema, fields: newFields });
    }, [fields, schema, onChange]);

    // Save field from editor
    const handleSaveField = useCallback((fieldData) => {
        let newFields;

        if (fieldData._index !== undefined) {
            // Editing existing field
            newFields = [...fields];
            newFields[fieldData._index] = {
                name: fieldData.name,
                type: fieldData.type,
                generator: fieldData.generator
            };
        } else {
            // Adding new field
            newFields = [...fields, {
                name: fieldData.name,
                type: fieldData.type,
                generator: fieldData.generator
            }];
        }

        setFields(newFields);
        onChange?.({ ...schema, fields: newFields });
        setShowFieldEditor(false);
        setEditingField(null);
    }, [fields, schema, onChange]);

    // Cancel field editing
    const handleCancelEdit = useCallback(() => {
        setShowFieldEditor(false);
        setEditingField(null);
    }, []);

    // Get field type badge color
    const getFieldTypeBadge = (type) => {
        const colors = {
            string: 'bg-blue-100 text-blue-800',
            number: 'bg-green-100 text-green-800',
            boolean: 'bg-purple-100 text-purple-800',
            uuid: 'bg-orange-100 text-orange-800',
            timestamp: 'bg-gray-100 text-gray-800'
        };
        return colors[type] || 'bg-gray-100 text-gray-800';
    };

    // Get generator description
    const getGeneratorDescription = (field) => {
        const { type, generator } = field;
        const genType = generator?.type || 'fixed';

        if (type === 'uuid') return 'Auto-generated UUID';
        if (type === 'timestamp') return 'Current timestamp';

        switch (genType) {
            case 'fixed':
                return `Fixed: ${generator?.value || 'N/A'}`;
            case 'random_choice':
                return `Random from: [${generator?.choices?.join(', ') || 'N/A'}]`;
            case 'random_string':
                return `Random string (${generator?.length || 10} chars)`;
            case 'random_int':
                return `Random int (${generator?.min || 0}-${generator?.max || 100})`;
            case 'random_float':
                return `Random float (${generator?.min || 0}-${generator?.max || 100})`;
            case 'random':
                return 'Random boolean';
            default:
                return 'Unknown generator';
        }
    };

    return (
        <div className={`space-y-6 ${className}`}>
            {/* Header */}
            <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">JSON Schema Builder</h3>
                <Button onClick={handleAddField} size="sm">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Field
                </Button>
            </div>

            {/* Fields List */}
            <Card>
                <CardHeader>
                    <CardTitle className="text-base">Fields ({fields.length})</CardTitle>
                </CardHeader>
                <CardContent>
                    {fields.length === 0 ? (
                        <div className="text-center py-8 text-gray-500">
                            <p>No fields defined yet.</p>
                            <p className="text-sm mt-1">Click "Add Field" to get started.</p>
                        </div>
                    ) : (
                        <DragDropContext onDragEnd={handleDragEnd}>
                            <Droppable droppableId="fields">
                                {(provided) => (
                                    <div
                                        {...provided.droppableProps}
                                        ref={provided.innerRef}
                                        className="space-y-2"
                                    >
                                        {fields.map((field, index) => (
                                            <Draggable
                                                key={`${field.name}-${index}`}
                                                draggableId={`field-${index}`}
                                                index={index}
                                            >
                                                {(provided, snapshot) => (
                                                    <div
                                                        ref={provided.innerRef}
                                                        {...provided.draggableProps}
                                                        className={`
                              flex items-center gap-3 p-3 border rounded-lg bg-white
                              ${snapshot.isDragging ? 'shadow-lg' : 'shadow-sm'}
                              hover:shadow-md transition-shadow
                            `}
                                                    >
                                                        {/* Drag Handle */}
                                                        <div
                                                            {...provided.dragHandleProps}
                                                            className="text-gray-400 hover:text-gray-600 cursor-grab"
                                                        >
                                                            <GripVertical className="w-4 h-4" />
                                                        </div>

                                                        {/* Field Info */}
                                                        <div className="flex-1 min-w-0">
                                                            <div className="flex items-center gap-2 mb-1">
                                                                <span className="font-medium text-sm">
                                                                    {field.name || 'Unnamed Field'}
                                                                </span>
                                                                <Badge
                                                                    variant="secondary"
                                                                    className={getFieldTypeBadge(field.type)}
                                                                >
                                                                    {field.type}
                                                                </Badge>
                                                            </div>
                                                            <p className="text-xs text-gray-600 truncate">
                                                                {getGeneratorDescription(field)}
                                                            </p>
                                                        </div>

                                                        {/* Actions */}
                                                        <div className="flex items-center gap-1">
                                                            <Button
                                                                variant="ghost"
                                                                size="sm"
                                                                onClick={() => handleEditField(index)}
                                                                className="h-8 w-8 p-0"
                                                            >
                                                                <Edit className="w-3 h-3" />
                                                            </Button>
                                                            <Button
                                                                variant="ghost"
                                                                size="sm"
                                                                onClick={() => handleDeleteField(index)}
                                                                className="h-8 w-8 p-0 text-red-600 hover:text-red-700"
                                                            >
                                                                <Trash2 className="w-3 h-3" />
                                                            </Button>
                                                        </div>
                                                    </div>
                                                )}
                                            </Draggable>
                                        ))}
                                        {provided.placeholder}
                                    </div>
                                )}
                            </Droppable>
                        </DragDropContext>
                    )}
                </CardContent>
            </Card>

            {/* Preview */}
            <PayloadPreview schema={{ fields }} />

            {/* Field Editor Modal */}
            {showFieldEditor && (
                <FieldEditor
                    field={editingField}
                    onSave={handleSaveField}
                    onCancel={handleCancelEdit}
                    existingFieldNames={fields.map(f => f.name).filter((_, i) => i !== editingField?._index)}
                />
            )}
        </div>
    );
};

export default PayloadBuilder;