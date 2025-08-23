import { Check, Copy, RefreshCw } from 'lucide-react';
import React, { useEffect, useState } from 'react';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';

const PayloadPreview = ({ schema, className = "" }) => {
    const [previewData, setPreviewData] = useState({});
    const [isGenerating, setIsGenerating] = useState(false);
    const [copied, setCopied] = useState(false);

    // Generate sample payload based on schema
    const generateSamplePayload = () => {
        if (!schema?.fields || schema.fields.length === 0) {
            return {};
        }

        const payload = {};

        schema.fields.forEach(field => {
            const { name, type, generator = {} } = field;

            switch (type) {
                case 'string':
                    payload[name] = generateStringValue(generator);
                    break;
                case 'number':
                    payload[name] = generateNumberValue(generator);
                    break;
                case 'boolean':
                    payload[name] = generateBooleanValue(generator);
                    break;
                case 'uuid':
                    payload[name] = generateUUID();
                    break;
                case 'timestamp':
                    payload[name] = new Date().toISOString();
                    break;
                default:
                    payload[name] = null;
            }
        });

        return payload;
    };

    // Generate string values
    const generateStringValue = (generator) => {
        const { type = 'fixed', value, choices, length = 10 } = generator;

        switch (type) {
            case 'fixed':
                return value || 'default';
            case 'random_choice':
                return choices && choices.length > 0
                    ? choices[Math.floor(Math.random() * choices.length)]
                    : 'option1';
            case 'random_string':
                const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
                return Array.from({ length }, () => chars.charAt(Math.floor(Math.random() * chars.length))).join('');
            default:
                return 'default';
        }
    };

    // Generate number values
    const generateNumberValue = (generator) => {
        const { type = 'fixed', value, min = 0, max = 100, decimals = 2 } = generator;

        switch (type) {
            case 'fixed':
                return value !== undefined ? value : 0;
            case 'random_int':
                return Math.floor(Math.random() * (max - min + 1)) + min;
            case 'random_float':
                const randomFloat = Math.random() * (max - min) + min;
                return parseFloat(randomFloat.toFixed(decimals));
            default:
                return 0;
        }
    };

    // Generate boolean values
    const generateBooleanValue = (generator) => {
        const { type = 'fixed', value } = generator;

        switch (type) {
            case 'fixed':
                return value !== undefined ? value : true;
            case 'random':
                return Math.random() < 0.5;
            default:
                return true;
        }
    };

    // Generate UUID (simple version for preview)
    const generateUUID = () => {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    };

    // Handle refresh
    const handleRefresh = async () => {
        setIsGenerating(true);
        // Add small delay for better UX
        setTimeout(() => {
            setPreviewData(generateSamplePayload());
            setIsGenerating(false);
        }, 300);
    };

    // Handle copy to clipboard
    const handleCopy = async () => {
        try {
            const jsonString = JSON.stringify(previewData, null, 2);
            await navigator.clipboard.writeText(jsonString);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error('Failed to copy to clipboard:', err);
        }
    };

    // Generate initial preview when schema changes
    useEffect(() => {
        setPreviewData(generateSamplePayload());
    }, [schema]);

    // Format JSON for display
    const formatJSON = (obj) => {
        if (Object.keys(obj).length === 0) {
            return '{}';
        }
        return JSON.stringify(obj, null, 2);
    };

    // Get value type for styling
    const getValueType = (value) => {
        if (value === null) return 'null';
        if (typeof value === 'string') return 'string';
        if (typeof value === 'number') return 'number';
        if (typeof value === 'boolean') return 'boolean';
        return 'unknown';
    };

    // Render JSON with syntax highlighting
    const renderHighlightedJSON = (obj) => {
        if (Object.keys(obj).length === 0) {
            return <span className="text-gray-500">{'{ }'}</span>;
        }

        const entries = Object.entries(obj);

        return (
            <div className="font-mono text-sm">
                <span className="text-gray-600">{'{'}</span>
                <div className="ml-4">
                    {entries.map(([key, value], index) => (
                        <div key={key} className="flex">
                            <span className="text-blue-600">"{key}"</span>
                            <span className="text-gray-600">: </span>
                            <span className={`
                ${getValueType(value) === 'string' ? 'text-green-600' : ''}
                ${getValueType(value) === 'number' ? 'text-purple-600' : ''}
                ${getValueType(value) === 'boolean' ? 'text-orange-600' : ''}
                ${getValueType(value) === 'null' ? 'text-gray-400' : ''}
              `}>
                                {getValueType(value) === 'string' ? `"${value}"` : String(value)}
                            </span>
                            {index < entries.length - 1 && <span className="text-gray-600">,</span>}
                        </div>
                    ))}
                </div>
                <span className="text-gray-600">{'}'}</span>
            </div>
        );
    };

    return (
        <Card className={className}>
            <CardHeader>
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <CardTitle className="text-base">Payload Preview</CardTitle>
                        <Badge variant="outline" className="text-xs">
                            {schema?.fields?.length || 0} fields
                        </Badge>
                    </div>
                    <div className="flex items-center gap-2">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={handleRefresh}
                            disabled={isGenerating}
                            className="h-8"
                        >
                            <RefreshCw className={`w-3 h-3 mr-1 ${isGenerating ? 'animate-spin' : ''}`} />
                            Refresh
                        </Button>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={handleCopy}
                            disabled={Object.keys(previewData).length === 0}
                            className="h-8"
                        >
                            {copied ? (
                                <Check className="w-3 h-3 mr-1" />
                            ) : (
                                <Copy className="w-3 h-3 mr-1" />
                            )}
                            {copied ? 'Copied!' : 'Copy'}
                        </Button>
                    </div>
                </div>
            </CardHeader>
            <CardContent>
                {schema?.fields?.length === 0 ? (
                    <div className="text-center py-8 text-gray-500">
                        <p>No fields defined</p>
                        <p className="text-sm mt-1">Add fields to see a preview</p>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {/* Highlighted JSON Display */}
                        <div className="bg-gray-50 rounded-lg p-4 border">
                            {renderHighlightedJSON(previewData)}
                        </div>

                        {/* Field Summary */}
                        <div className="text-xs text-gray-600">
                            <p className="font-medium mb-2">Field Summary:</p>
                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                                {schema.fields.map((field, index) => (
                                    <div key={index} className="flex items-center gap-2">
                                        <Badge variant="outline" className="text-xs">
                                            {field.type}
                                        </Badge>
                                        <span className="truncate">{field.name}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}
            </CardContent>
        </Card>
    );
};

export default PayloadPreview;