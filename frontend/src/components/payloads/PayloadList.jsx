import {
    Code,
    Copy,
    Edit,
    Layers,
    Plus,
    Search,
    Trash2
} from 'lucide-react';
import React, { useState } from 'react';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Input } from '../ui/input';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow
} from '../ui/table';

const PayloadList = ({
    payloads = [],
    onAdd,
    onEdit,
    onDelete,
    onDuplicate,
    loading = false,
    className = ""
}) => {
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedType, setSelectedType] = useState('all');

    // Filter payloads based on search and type
    const filteredPayloads = payloads.filter(payload => {
        const matchesSearch = payload.name.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesType = selectedType === 'all' || payload.type === selectedType;
        return matchesSearch && matchesType;
    });

    // Get payload type icon
    const getTypeIcon = (type) => {
        switch (type) {
            case 'visual':
                return <Layers className="w-4 h-4" />;
            case 'python':
                return <Code className="w-4 h-4" />;
            default:
                return <Layers className="w-4 h-4" />;
        }
    };

    // Get payload type badge color
    const getTypeBadgeColor = (type) => {
        switch (type) {
            case 'visual':
                return 'bg-blue-100 text-blue-800';
            case 'python':
                return 'bg-green-100 text-green-800';
            default:
                return 'bg-gray-100 text-gray-800';
        }
    };

    // Get field count for visual payloads
    const getFieldCount = (payload) => {
        if (payload.type === 'visual' && payload.schema?.fields) {
            return payload.schema.fields.length;
        }
        return 0;
    };

    // Format creation date
    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    };

    return (
        <div className={`space-y-6 ${className}`}>
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold">Payload Templates</h2>
                    <p className="text-gray-600 mt-1">
                        Manage JSON payload templates for your IoT devices
                    </p>
                </div>
                <Button onClick={onAdd}>
                    <Plus className="w-4 h-4 mr-2" />
                    New Payload
                </Button>
            </div>

            {/* Filters */}
            <Card>
                <CardContent className="pt-6">
                    <div className="flex flex-col sm:flex-row gap-4">
                        {/* Search */}
                        <div className="flex-1 relative">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                            <Input
                                placeholder="Search payloads..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="pl-10"
                            />
                        </div>

                        {/* Type Filter */}
                        <div className="flex gap-2">
                            <Button
                                variant={selectedType === 'all' ? 'default' : 'outline'}
                                size="sm"
                                onClick={() => setSelectedType('all')}
                            >
                                All ({payloads.length})
                            </Button>
                            <Button
                                variant={selectedType === 'visual' ? 'default' : 'outline'}
                                size="sm"
                                onClick={() => setSelectedType('visual')}
                            >
                                <Layers className="w-3 h-3 mr-1" />
                                Visual ({payloads.filter(p => p.type === 'visual').length})
                            </Button>
                            <Button
                                variant={selectedType === 'python' ? 'default' : 'outline'}
                                size="sm"
                                onClick={() => setSelectedType('python')}
                            >
                                <Code className="w-3 h-3 mr-1" />
                                Python ({payloads.filter(p => p.type === 'python').length})
                            </Button>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Payloads Table */}
            <Card>
                <CardHeader>
                    <CardTitle className="text-lg">
                        Payloads ({filteredPayloads.length})
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    {loading ? (
                        <div className="text-center py-8">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                            <p className="text-gray-600 mt-2">Loading payloads...</p>
                        </div>
                    ) : filteredPayloads.length === 0 ? (
                        <div className="text-center py-8">
                            {payloads.length === 0 ? (
                                <>
                                    <Layers className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                                        No payloads yet
                                    </h3>
                                    <p className="text-gray-600 mb-4">
                                        Create your first payload template to get started
                                    </p>
                                    <Button onClick={onAdd}>
                                        <Plus className="w-4 h-4 mr-2" />
                                        Create Payload
                                    </Button>
                                </>
                            ) : (
                                <>
                                    <Search className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                                        No matching payloads
                                    </h3>
                                    <p className="text-gray-600">
                                        Try adjusting your search or filter criteria
                                    </p>
                                </>
                            )}
                        </div>
                    ) : (
                        <div className="overflow-x-auto">
                            <Table>
                                <TableHeader>
                                    <TableRow>
                                        <TableHead>Name</TableHead>
                                        <TableHead>Type</TableHead>
                                        <TableHead>Details</TableHead>
                                        <TableHead>Created</TableHead>
                                        <TableHead className="text-right">Actions</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {filteredPayloads.map((payload) => (
                                        <TableRow key={payload.id}>
                                            <TableCell>
                                                <div className="flex items-center gap-3">
                                                    {getTypeIcon(payload.type)}
                                                    <div>
                                                        <div className="font-medium">{payload.name}</div>
                                                        {payload.description && (
                                                            <div className="text-sm text-gray-600 truncate max-w-xs">
                                                                {payload.description}
                                                            </div>
                                                        )}
                                                    </div>
                                                </div>
                                            </TableCell>
                                            <TableCell>
                                                <Badge
                                                    variant="secondary"
                                                    className={getTypeBadgeColor(payload.type)}
                                                >
                                                    {payload.type}
                                                </Badge>
                                            </TableCell>
                                            <TableCell>
                                                {payload.type === 'visual' ? (
                                                    <span className="text-sm text-gray-600">
                                                        {getFieldCount(payload)} fields
                                                    </span>
                                                ) : (
                                                    <span className="text-sm text-gray-600">
                                                        Python code
                                                    </span>
                                                )}
                                            </TableCell>
                                            <TableCell>
                                                <span className="text-sm text-gray-600">
                                                    {formatDate(payload.created_at)}
                                                </span>
                                            </TableCell>
                                            <TableCell>
                                                <div className="flex items-center justify-end gap-1">
                                                    <Button
                                                        variant="ghost"
                                                        size="sm"
                                                        onClick={() => onEdit?.(payload)}
                                                        className="h-8 w-8 p-0"
                                                    >
                                                        <Edit className="w-3 h-3" />
                                                    </Button>
                                                    <Button
                                                        variant="ghost"
                                                        size="sm"
                                                        onClick={() => onDuplicate?.(payload)}
                                                        className="h-8 w-8 p-0"
                                                    >
                                                        <Copy className="w-3 h-3" />
                                                    </Button>
                                                    <Button
                                                        variant="ghost"
                                                        size="sm"
                                                        onClick={() => onDelete?.(payload)}
                                                        className="h-8 w-8 p-0 text-red-600 hover:text-red-700"
                                                    >
                                                        <Trash2 className="w-3 h-3" />
                                                    </Button>
                                                </div>
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
};

export default PayloadList;