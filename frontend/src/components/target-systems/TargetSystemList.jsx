import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { useNotificationContext } from '@/components/providers/NotificationProvider'
import { useDeleteTargetSystem, useTargetSystems, useTestTargetSystemConnection } from '@/hooks/useTargetSystems'
import { CheckCircleIcon, PencilIcon, PlusIcon, ServerIcon, TrashIcon, XCircleIcon } from '@heroicons/react/24/outline'
import { useState } from 'react'
import ConnectionTester from './ConnectionTester'
import TargetSystemForm from './TargetSystemForm'

const TARGET_TYPE_LABELS = {
    http: 'HTTP/HTTPS',
    mqtt: 'MQTT',
    kafka: 'Apache Kafka',
    websocket: 'WebSocket',
    ftp: 'FTP/SFTP',
    pubsub: 'Pub/Sub'
}

const TARGET_TYPE_COLORS = {
    http: 'bg-blue-100 text-blue-800',
    mqtt: 'bg-green-100 text-green-800',
    kafka: 'bg-purple-100 text-purple-800',
    websocket: 'bg-orange-100 text-orange-800',
    ftp: 'bg-yellow-100 text-yellow-800',
    pubsub: 'bg-pink-100 text-pink-800'
}

export default function TargetSystemList() {
    const [selectedSystem, setSelectedSystem] = useState(null)
    const [isFormOpen, setIsFormOpen] = useState(false)
    const [isTestOpen, setIsTestOpen] = useState(false)
    const [testingSystem, setTestingSystem] = useState(null)

    const { data: targetSystems = [], isLoading, error } = useTargetSystems()
    const deleteTargetSystem = useDeleteTargetSystem()
    const testConnection = useTestTargetSystemConnection()
    const { showSuccess, showError, showWarning } = useNotificationContext()

    const handleEdit = (system) => {
        setSelectedSystem(system)
        setIsFormOpen(true)
    }

    const handleDelete = async (system) => {
        if (window.confirm(`¿Estás seguro de que quieres eliminar "${system.name}"?`)) {
            try {
                await deleteTargetSystem.mutateAsync(system.id)
                showSuccess('Target system eliminado exitosamente')
            } catch (error) {
                showError('Error al eliminar target system')
            }
        }
    }

    const handleTest = (system) => {
        setTestingSystem(system)
        setIsTestOpen(true)
    }

    const handleFormClose = () => {
        setIsFormOpen(false)
        setSelectedSystem(null)
    }

    const handleTestClose = () => {
        setIsTestOpen(false)
        setTestingSystem(null)
    }

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
                    <p className="text-muted-foreground">Cargando target systems...</p>
                </div>
            </div>
        )
    }

    if (error) {
        return (
            <Card>
                <CardContent className="pt-6">
                    <div className="text-center text-red-600">
                        <XCircleIcon className="w-8 h-8 mx-auto mb-2" />
                        <p>Error al cargar target systems: {error.message}</p>
                    </div>
                </CardContent>
            </Card>
        )
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-2xl font-bold">Target Systems</h2>
                    <p className="text-muted-foreground">
                        Configura los sistemas de destino donde se enviarán los datos de telemetría
                    </p>
                </div>
                <Dialog open={isFormOpen} onOpenChange={setIsFormOpen}>
                    <DialogTrigger asChild>
                        <Button onClick={() => setSelectedSystem(null)}>
                            <PlusIcon className="w-4 h-4 mr-2" />
                            Nuevo Target System
                        </Button>
                    </DialogTrigger>
                    <DialogContent className="max-w-2xl">
                        <DialogHeader>
                            <DialogTitle>
                                {selectedSystem ? 'Editar Target System' : 'Nuevo Target System'}
                            </DialogTitle>
                            <DialogDescription>
                                {selectedSystem
                                    ? 'Modifica la configuración del target system'
                                    : 'Configura un nuevo sistema de destino para tus datos IoT'
                                }
                            </DialogDescription>
                        </DialogHeader>
                        <TargetSystemForm
                            targetSystem={selectedSystem}
                            onClose={handleFormClose}
                        />
                    </DialogContent>
                </Dialog>
            </div>

            {targetSystems.length === 0 ? (
                <Card>
                    <CardContent className="pt-6">
                        <div className="text-center">
                            <ServerIcon className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                            <h3 className="text-lg font-semibold mb-2">No hay target systems configurados</h3>
                            <p className="text-muted-foreground mb-4">
                                Crea tu primer target system para comenzar a enviar datos de telemetría
                            </p>
                            <Button onClick={() => setIsFormOpen(true)}>
                                <PlusIcon className="w-4 h-4 mr-2" />
                                Crear Target System
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            ) : (
                <Card>
                    <CardHeader>
                        <CardTitle>Target Systems Configurados</CardTitle>
                        <CardDescription>
                            {targetSystems.length} sistema{targetSystems.length !== 1 ? 's' : ''} configurado{targetSystems.length !== 1 ? 's' : ''}
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Nombre</TableHead>
                                    <TableHead>Tipo</TableHead>
                                    <TableHead>Configuración</TableHead>
                                    <TableHead>Estado</TableHead>
                                    <TableHead className="text-right">Acciones</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {targetSystems.map((system) => (
                                    <TableRow key={system.id}>
                                        <TableCell className="font-medium">{system.name}</TableCell>
                                        <TableCell>
                                            <Badge className={TARGET_TYPE_COLORS[system.type] || 'bg-gray-100 text-gray-800'}>
                                                {TARGET_TYPE_LABELS[system.type] || system.type.toUpperCase()}
                                            </Badge>
                                        </TableCell>
                                        <TableCell>
                                            <div className="text-sm text-muted-foreground">
                                                {system.type === 'http' && system.config?.url && (
                                                    <span>{system.config.method || 'POST'} {system.config.url}</span>
                                                )}
                                                {system.type === 'mqtt' && system.config?.host && (
                                                    <span>{system.config.host}:{system.config.port || 1883}/{system.config.topic}</span>
                                                )}
                                                {system.type === 'kafka' && system.config?.bootstrap_servers && (
                                                    <span>{system.config.bootstrap_servers} → {system.config.topic}</span>
                                                )}
                                                {system.type === 'websocket' && system.config?.url && (
                                                    <span>{system.config.url}</span>
                                                )}
                                                {system.type === 'ftp' && system.config?.host && (
                                                    <span>{system.config.host}:{system.config.port || 21}</span>
                                                )}
                                                {system.type === 'pubsub' && system.config?.topic && (
                                                    <span>{system.config.provider} → {system.config.topic}</span>
                                                )}
                                            </div>
                                        </TableCell>
                                        <TableCell>
                                            <Badge variant="outline" className="text-xs">
                                                Configurado
                                            </Badge>
                                        </TableCell>
                                        <TableCell className="text-right">
                                            <div className="flex justify-end space-x-2">
                                                <Button
                                                    variant="outline"
                                                    size="sm"
                                                    onClick={() => handleTest(system)}
                                                >
                                                    <CheckCircleIcon className="w-4 h-4" />
                                                </Button>
                                                <Button
                                                    variant="outline"
                                                    size="sm"
                                                    onClick={() => handleEdit(system)}
                                                >
                                                    <PencilIcon className="w-4 h-4" />
                                                </Button>
                                                <Button
                                                    variant="outline"
                                                    size="sm"
                                                    onClick={() => handleDelete(system)}
                                                    disabled={deleteTargetSystem.isLoading}
                                                >
                                                    <TrashIcon className="w-4 h-4" />
                                                </Button>
                                            </div>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </CardContent>
                </Card>
            )}

            {/* Connection Test Dialog */}
            <Dialog open={isTestOpen} onOpenChange={setIsTestOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Probar Conexión</DialogTitle>
                        <DialogDescription>
                            Probando conexión con {testingSystem?.name}
                        </DialogDescription>
                    </DialogHeader>
                    {testingSystem && (
                        <ConnectionTester
                            targetSystem={testingSystem}
                            onClose={handleTestClose}
                        />
                    )}
                </DialogContent>
            </Dialog>
        </div>
    )
}