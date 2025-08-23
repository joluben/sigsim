import Editor from '@monaco-editor/react';
import {
    AlertTriangle,
    Check,
    CheckCircle,
    Code,
    Copy,
    Eye,
    Play,
    RefreshCw
} from 'lucide-react';
import React, { useEffect, useRef, useState } from 'react';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';

const PythonCodeEditor = ({
    code = '',
    onChange,
    onValidate,
    className = "",
    height = "400px",
    showPreview = true,
    deviceMetadata = {}
}) => {
    const [editorCode, setEditorCode] = useState(code);
    const [validationErrors, setValidationErrors] = useState([]);
    const [isValidating, setIsValidating] = useState(false);
    const [previewResult, setPreviewResult] = useState(null);
    const [isGeneratingPreview, setIsGeneratingPreview] = useState(false);
    const [copied, setCopied] = useState(false);
    const editorRef = useRef(null);

    // Update editor when code prop changes
    useEffect(() => {
        if (code !== editorCode) {
            setEditorCode(code);
        }
    }, [code]);

    // Handle editor mount
    const handleEditorDidMount = (editor, monaco) => {
        editorRef.current = editor;

        // Configure Python language features
        monaco.languages.python = monaco.languages.python || {};

        // Add custom Python snippets
        monaco.languages.registerCompletionItemProvider('python', {
            provideCompletionItems: (model, position) => {
                const suggestions = [
                    {
                        label: 'device_metadata',
                        kind: monaco.languages.CompletionItemKind.Variable,
                        insertText: 'device_metadata',
                        documentation: 'Device-specific metadata dictionary'
                    },
                    {
                        label: 'result',
                        kind: monaco.languages.CompletionItemKind.Variable,
                        insertText: 'result',
                        documentation: 'Output payload dictionary'
                    },
                    {
                        label: 'datetime.utcnow()',
                        kind: monaco.languages.CompletionItemKind.Function,
                        insertText: 'datetime.utcnow().isoformat()',
                        documentation: 'Current UTC timestamp as ISO string'
                    },
                    {
                        label: 'random.uniform',
                        kind: monaco.languages.CompletionItemKind.Function,
                        insertText: 'random.uniform(${1:min}, ${2:max})',
                        insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                        documentation: 'Random float between min and max'
                    },
                    {
                        label: 'random.randint',
                        kind: monaco.languages.CompletionItemKind.Function,
                        insertText: 'random.randint(${1:min}, ${2:max})',
                        insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                        documentation: 'Random integer between min and max (inclusive)'
                    },
                    {
                        label: 'random.choice',
                        kind: monaco.languages.CompletionItemKind.Function,
                        insertText: 'random.choice([${1:options}])',
                        insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                        documentation: 'Random choice from list'
                    },
                    {
                        label: 'uuid.uuid4()',
                        kind: monaco.languages.CompletionItemKind.Function,
                        insertText: 'str(uuid.uuid4())',
                        documentation: 'Generate random UUID as string'
                    }
                ];
                return { suggestions };
            }
        });

        // Set editor options
        editor.updateOptions({
            fontSize: 14,
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            wordWrap: 'on',
            lineNumbers: 'on',
            folding: true,
            selectOnLineNumbers: true,
            automaticLayout: true
        });
    };

    // Handle code changes
    const handleCodeChange = (value) => {
        setEditorCode(value || '');
        onChange?.(value || '');

        // Clear previous validation errors
        setValidationErrors([]);

        // Debounced validation
        clearTimeout(window.pythonValidationTimeout);
        window.pythonValidationTimeout = setTimeout(() => {
            validateCode(value || '');
        }, 1000);
    };

    // Validate Python code
    const validateCode = async (codeToValidate) => {
        if (!codeToValidate.trim()) {
            setValidationErrors([]);
            return;
        }

        setIsValidating(true);

        try {
            // Basic syntax validation using a simple approach
            const errors = [];

            // Check for basic Python syntax issues
            const lines = codeToValidate.split('\n');
            let indentLevel = 0;
            let inFunction = false;

            lines.forEach((line, index) => {
                const trimmedLine = line.trim();
                const lineNumber = index + 1;

                // Skip empty lines and comments
                if (!trimmedLine || trimmedLine.startsWith('#')) return;

                // Check for dangerous imports/functions
                const dangerousPatterns = [
                    /import\s+os/,
                    /from\s+os/,
                    /import\s+subprocess/,
                    /import\s+sys/,
                    /\bexec\s*\(/,
                    /\beval\s*\(/,
                    /\bopen\s*\(/,
                    /\b__import__\b/
                ];

                dangerousPatterns.forEach(pattern => {
                    if (pattern.test(trimmedLine)) {
                        errors.push({
                            line: lineNumber,
                            column: 1,
                            message: 'Potentially unsafe operation detected',
                            severity: 'error'
                        });
                    }
                });

                // Check for result assignment
                if (trimmedLine.includes('result =') || trimmedLine.includes('result[')) {
                    // Good, result is being set
                }
            });

            // Check if result is assigned somewhere
            if (!codeToValidate.includes('result')) {
                errors.push({
                    line: 1,
                    column: 1,
                    message: 'Code should assign a dictionary to the "result" variable',
                    severity: 'warning'
                });
            }

            setValidationErrors(errors);
            onValidate?.(errors.length === 0, errors);

        } catch (error) {
            const syntaxError = {
                line: 1,
                column: 1,
                message: `Syntax error: ${error.message}`,
                severity: 'error'
            };
            setValidationErrors([syntaxError]);
            onValidate?.(false, [syntaxError]);
        } finally {
            setIsValidating(false);
        }
    };

    // Generate preview
    const generatePreview = async () => {
        if (!editorCode.trim()) {
            setPreviewResult({ error: 'No code to execute' });
            return;
        }

        setIsGeneratingPreview(true);

        try {
            // Simulate code execution for preview
            // In a real implementation, this would call the backend
            const mockResult = await simulateCodeExecution(editorCode, deviceMetadata);
            setPreviewResult(mockResult);
        } catch (error) {
            setPreviewResult({ error: error.message });
        } finally {
            setIsGeneratingPreview(false);
        }
    };

    // Simulate code execution (mock implementation)
    const simulateCodeExecution = async (code, metadata) => {
        // This is a mock implementation for preview
        // In production, this would call the backend API

        await new Promise(resolve => setTimeout(resolve, 500)); // Simulate delay

        // Simple mock result based on common patterns
        if (code.includes('temperature')) {
            return {
                device_id: metadata.device_id || 'device-001',
                timestamp: new Date().toISOString(),
                temperature: 22.5,
                humidity: 65,
                status: 'online'
            };
        }

        return {
            device_id: metadata.device_id || 'device-001',
            timestamp: new Date().toISOString(),
            value: Math.random() * 100,
            status: 'active'
        };
    };

    // Copy code to clipboard
    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(editorCode);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error('Failed to copy code:', err);
        }
    };

    // Get validation status
    const getValidationStatus = () => {
        if (isValidating) return { icon: RefreshCw, color: 'text-blue-600', text: 'Validating...', spin: true };
        if (validationErrors.length === 0) return { icon: CheckCircle, color: 'text-green-600', text: 'Valid' };

        const hasErrors = validationErrors.some(e => e.severity === 'error');
        if (hasErrors) return { icon: AlertTriangle, color: 'text-red-600', text: 'Errors' };
        return { icon: AlertTriangle, color: 'text-yellow-600', text: 'Warnings' };
    };

    const validationStatus = getValidationStatus();

    return (
        <div className={`space-y-4 ${className}`}>
            {/* Editor */}
            <Card>
                <CardHeader>
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <CardTitle className="text-lg flex items-center gap-2">
                                <Code className="w-5 h-5" />
                                Python Code Editor
                            </CardTitle>
                            <Badge
                                variant="outline"
                                className={`${validationStatus.color} border-current`}
                            >
                                <validationStatus.icon
                                    className={`w-3 h-3 mr-1 ${validationStatus.spin ? 'animate-spin' : ''}`}
                                />
                                {validationStatus.text}
                            </Badge>
                        </div>
                        <div className="flex items-center gap-2">
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={handleCopy}
                                className="h-8"
                            >
                                {copied ? (
                                    <Check className="w-3 h-3 mr-1" />
                                ) : (
                                    <Copy className="w-3 h-3 mr-1" />
                                )}
                                {copied ? 'Copied!' : 'Copy'}
                            </Button>
                            {showPreview && (
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={generatePreview}
                                    disabled={isGeneratingPreview || validationErrors.some(e => e.severity === 'error')}
                                    className="h-8"
                                >
                                    {isGeneratingPreview ? (
                                        <RefreshCw className="w-3 h-3 mr-1 animate-spin" />
                                    ) : (
                                        <Play className="w-3 h-3 mr-1" />
                                    )}
                                    Preview
                                </Button>
                            )}
                        </div>
                    </div>
                </CardHeader>
                <CardContent>
                    <div className="border rounded-lg overflow-hidden">
                        <Editor
                            height={height}
                            defaultLanguage="python"
                            value={editorCode}
                            onChange={handleCodeChange}
                            onMount={handleEditorDidMount}
                            theme="vs-light"
                            options={{
                                fontSize: 14,
                                minimap: { enabled: false },
                                scrollBeyondLastLine: false,
                                wordWrap: 'on',
                                lineNumbers: 'on',
                                folding: true,
                                selectOnLineNumbers: true,
                                automaticLayout: true,
                                padding: { top: 16, bottom: 16 }
                            }}
                        />
                    </div>

                    {/* Validation Errors */}
                    {validationErrors.length > 0 && (
                        <div className="mt-4 space-y-2">
                            {validationErrors.map((error, index) => (
                                <div
                                    key={index}
                                    className={`flex items-start gap-2 p-3 rounded-lg text-sm ${error.severity === 'error'
                                            ? 'bg-red-50 border border-red-200 text-red-800'
                                            : 'bg-yellow-50 border border-yellow-200 text-yellow-800'
                                        }`}
                                >
                                    <AlertTriangle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                                    <div>
                                        <span className="font-medium">Line {error.line}: </span>
                                        {error.message}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Help Text */}
                    <div className="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
                        <h4 className="font-medium text-blue-900 mb-2">Available Variables & Modules:</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-blue-800">
                            <div>
                                <p className="font-medium mb-1">Variables:</p>
                                <ul className="space-y-1">
                                    <li><code className="bg-blue-100 px-1 rounded">device_metadata</code> - Device data</li>
                                    <li><code className="bg-blue-100 px-1 rounded">result</code> - Output payload (required)</li>
                                </ul>
                            </div>
                            <div>
                                <p className="font-medium mb-1">Modules:</p>
                                <ul className="space-y-1">
                                    <li><code className="bg-blue-100 px-1 rounded">random</code> - Random number generation</li>
                                    <li><code className="bg-blue-100 px-1 rounded">datetime</code> - Date and time utilities</li>
                                    <li><code className="bg-blue-100 px-1 rounded">uuid</code> - UUID generation</li>
                                    <li><code className="bg-blue-100 px-1 rounded">math</code> - Mathematical functions</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Preview */}
            {showPreview && previewResult && (
                <Card>
                    <CardHeader>
                        <CardTitle className="text-lg flex items-center gap-2">
                            <Eye className="w-5 h-5" />
                            Preview Result
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        {previewResult.error ? (
                            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                                <div className="flex items-start gap-2">
                                    <AlertTriangle className="w-4 h-4 mt-0.5 text-red-600 flex-shrink-0" />
                                    <div>
                                        <p className="font-medium text-red-800">Execution Error</p>
                                        <p className="text-sm text-red-700 mt-1">{previewResult.error}</p>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="bg-gray-50 rounded-lg p-4 border">
                                <pre className="text-sm font-mono overflow-x-auto">
                                    {JSON.stringify(previewResult, null, 2)}
                                </pre>
                            </div>
                        )}
                    </CardContent>
                </Card>
            )}
        </div>
    );
};

export default PythonCodeEditor;