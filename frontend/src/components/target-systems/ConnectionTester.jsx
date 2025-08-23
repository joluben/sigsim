import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { useTestTargetSystemConnection } from '@/hooks/useTargetSystems'
import { CheckCircleIcon, ClockIcon, XCircleIcon } from '@heroicons/react/24/outline'
import { useEffect, useState } from 'react'

export default function ConnectionTester({ targetSystem, onClose }) {
    const [testResult, setTestResult] = useState(null)
    const [isAutoTesting, setIsAutoTesting] = useState(true)

    const testConnection = useTestTargetSystemConnection()

    // Auto-test on mount
    useEffect(() => {
        if (isAutoTesting && targetSystem) {
            handleTest()
            setIsAutoTesting(false)
        }
    }, [targetSystem, isAutoTesting])

    const handleTest = async () => {
        setTestResult(null)

        try {
            const result = await testConnection.mutateAsync(targetSystem.id)
            setTestResult(result)
        } catch (error) {
            setTestResult({
                success: false,
                error: error.message || 'Error desconocido',
                details: 'No se pudo conectar con el target system'
            })
        }
    }

    const getStatusBadge = () => {
        if (testConnection.isLoading) {
            return (
                <Badge variant="outline" className="text-yellow-600 border-yellow-300">
                    <ClockIcon className="w-3 h-3 mr-1" />
                    Probando...
                </Badge>
            )
        }

        if (!testResult) {
            return (
                <Badge variant="outline">
                    Sin probar
                </Badge>
            )
        }

        if (testResult.success) {
            return (
                <Badge className="bg-green-100 text-green-800 border-green-300">
                    <CheckCircleIcon className="w-3 h-3 mr-1" />
                    Conexión exitosa
                </Badge>
            )
        }

        return (
            <Badge variant="destructive">
                <XCircleIcon className="w-3 h-3 mr-1" />
                Error de conexión
            </Badge>
        )
    }

    const getConfigSummary = () => {
        const { config, type } = targetSystem

        switch (type) {
            case 'http':
                return `${config.method || 'POST'} ${config.url}`
            case 'mqtt':
                return `${config.host}:${config.port || 1883} → ${config.topic}`
            case 'kafka':
                return `${config.bootstrap_servers} → ${config.topic}`
            case 'websocket':
                return config.url
            case 'ftp':
                return `${config.host}:${config.port || 21}`
            case 'pubsub':
                return `${config.provider} → ${config.topic}`
            default:
                return 'Configuración personalizada'
        }
    }

    return (
        <div className="space-y-6">
            {/* Target System Info */}
            <div className="space-y-3">
                <div className="flex items-center justify-between">
                    <h3 className="font-semibold">{targetSystem.name}</h3>
                    {getStatusBadge()}
                </div>

                <div className="text-sm text-muted-foreground">
                    <p><strong>Tipo:</strong> {targetSystem.type.toUpperCase()}</p>
                    <p><strong>Configuración:</strong> {getConfigSummary()}</p>
                </div>
            </div>

            {/* Test Progress */}
            {testConnection.isLoading && (
                <div className="flex items-center space-x-3 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-yellow-600"></div>
                    <div>
                        <p className="font-medium text-yellow-800">Probando conexión...</p>
                        <p className="text-sm text-yellow-600">
                            Verificando conectividad y enviando payload de prueba
                        </p>
                    </div>
                </div>
            )}

            {/* Test Results */}
            {testResult && (
                <div className={`p-4 rounded-lg border ${testResult.success
                        ? 'bg-green-50 border-green-200'
                        : 'bg-red-50 border-red-200'
                    }`}>
                    <div className="flex items-start space-x-3">
                        {testResult.success ? (
                            <CheckCircleIcon className="w-6 h-6 text-green-600 mt-0.5" />
                        ) : (
                            <XCircleIcon className="w-6 h-6 text-red-600 mt-0.5" />
                        )}

                        <div className="flex-1">
                            <h4 className={`font-medium ${testResult.success ? 'text-green-800' : 'text-red-800'
                                }`}>
                                {testResult.success ? 'Conexión exitosa' : 'Error de conexión'}
                            </h4>

                            {testResult.message && (
                                <p className={`mt-1 text-sm ${testResult.success ? 'text-green-700' : 'text-red-700'
                                    }`}>
                                    {testResult.message}
                                </p>
                            )}

                            {testResult.error && (
                                <p className="mt-1 text-sm text-red-700">
                                    <strong>Error:</strong> {testResult.error}
                                </p>
                            )}

                            {testResult.details && (
                                <p className="mt-1 text-xs text-gray-600">
                                    {testResult.details}
                                </p>
                            )}

                            {/* Show test payload if successful */}
                            {testResult.success && testResult.test_payload && (
                                <details className="mt-3">
                                    <summary className="text-sm font-medium cursor-pointer text-green-700 hover:text-green-800">
                                        Ver payload de prueba
                                    </summary>
                                    <pre className="mt-2 p-2 bg-green-100 rounded text-xs overflow-x-auto">
                                        {JSON.stringify(testResult.test_payload, null, 2)}
                                    </pre>
                                </details>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* Connection Tips */}
            {testResult && !testResult.success && (
                <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <h4 className="font-medium text-blue-800 mb-2">Consejos para solucionar problemas:</h4>
                    <ul className="text-sm text-blue-700 space-y-1">
                        {targetSystem.type === 'http' && (
                            <>
                                <li>• Verifica que la URL sea accesible desde tu red</li>
                                <li>• Comprueba que el método HTTP sea correcto</li>
                                <li>• Revisa los headers de autenticación si son necesarios</li>
                            </>
                        )}
                        {targetSystem.type === 'mqtt' && (
                            <>
                                <li>• Verifica que el broker MQTT esté ejecutándose</li>
                                <li>• Comprueba las credenciales de usuario y contraseña</li>
                                <li>• Asegúrate de que el puerto esté abierto (1883 o 8883 para TLS)</li>
                            </>
                        )}
                        {targetSystem.type === 'kafka' && (
                            <>
                                <li>• Verifica que el cluster de Kafka esté disponible</li>
                                <li>• Comprueba la configuración de bootstrap servers</li>
                                <li>• Revisa los permisos del tópico</li>
                            </>
                        )}
                        {targetSystem.type === 'websocket' && (
                            <>
                                <li>• Verifica que el servidor WebSocket esté activo</li>
                                <li>• Comprueba la URL y el protocolo (ws:// o wss://)</li>
                                <li>• Revisa los headers de autenticación</li>
                            </>
                        )}
                        <li>• Verifica la conectividad de red y firewall</li>
                        <li>• Comprueba que no haya problemas de DNS</li>
                    </ul>
                </div>
            )}

            {/* Actions */}
            <div className="flex justify-between pt-4 border-t">
                <Button
                    variant="outline"
                    onClick={handleTest}
                    disabled={testConnection.isLoading}
                >
                    {testConnection.isLoading ? 'Probando...' : 'Probar de nuevo'}
                </Button>

                <Button onClick={onClose}>
                    Cerrar
                </Button>
            </div>
        </div>
    )
}