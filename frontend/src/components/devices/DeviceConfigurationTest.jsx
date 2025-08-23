import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import {
    CheckCircleIcon,
    PlayIcon,
    XCircleIcon
} from '@heroicons/react/24/outline'
import { useState } from 'react'
import { useTestDeviceConfiguration } from '../../hooks'
import { useNotificationContext } from '../providers/NotificationProvider'

export default function DeviceConfigurationTest({ device, className = "" }) {
    const [testResult, setTestResult] = useState(null)
    const testConfiguration = useTestDeviceConfiguration()
    const { showSuccess, showError } = useNotificationContext()

    const handleTest = async () => {
        try {
            setTestResult(null)
            const result = await testConfiguration.mutateAsync(device.id)
            setTestResult(result)
            showSuccess('Device configuration test completed successfully')
        } catch (error) {
            const errorMessage = error.response?.data?.message || error.message || 'Test failed'
            showError(`Configuration test failed: ${errorMessage}`)
            setTestResult({
                success: false,
                error: errorMessage,
                timestamp: new Date().toISOString()
            })
        }
    }

    const canTest = device.payload_id && device.target_system_id

    return (
        <Card className={className}>
            <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                    <PlayIcon className="w-5 h-5" />
                    <span>Configuration Test</span>
                </CardTitle>
                <CardDescription>
                    Test the device configuration by generating a sample payload
                </CardDescription>
            </CardHeader>

            <CardContent className="space-y-4">
                {/* Test Button */}
                <div className="flex items-center justify-between">
                    <div>
                        <p className="text-sm font-medium">Test Configuration</p>
                        <p className="text-sm text-muted-foreground">
                            Generate a sample payload to verify the configuration
                        </p>
                    </div>
                    <Button
                        onClick={handleTest}
                        disabled={!canTest || testConfiguration.isLoading}
                        variant="outline"
                    >
                        {testConfiguration.isLoading ? (
                            <div className="flex items-center space-x-2">
                                <div className="w-4 h-4 border-2 border-gray-600 border-t-transparent rounded-full animate-spin" />
                                <span>Testing...</span>
                            </div>
                        ) : (
                            <>
                                <PlayIcon className="w-4 h-4 mr-2" />
                                Test Configuration
                            </>
                        )}
                    </Button>
                </div>

                {/* Prerequisites */}
                {!canTest && (
                    <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                        <div className="flex items-start space-x-2">
                            <XCircleIcon className="w-5 h-5 text-yellow-600 mt-0.5" />
                            <div>
                                <p className="font-medium text-sm text-yellow-900">Configuration Required</p>
                                <p className="text-sm text-yellow-700">
                                    Assign a payload generator and target system before testing
                                </p>
                            </div>
                        </div>
                    </div>
                )}

                {/* Test Results */}
                {testResult && (
                    <div className={`p-3 rounded-lg border ${testResult.success
                            ? 'bg-green-50 border-green-200'
                            : 'bg-red-50 border-red-200'
                        }`}>
                        <div className="flex items-start space-x-2">
                            {testResult.success ? (
                                <CheckCircleIcon className="w-5 h-5 text-green-600 mt-0.5" />
                            ) : (
                                <XCircleIcon className="w-5 h-5 text-red-600 mt-0.5" />
                            )}
                            <div className="flex-1">
                                <div className="flex items-center justify-between mb-2">
                                    <p className={`font-medium text-sm ${testResult.success ? 'text-green-900' : 'text-red-900'
                                        }`}>
                                        {testResult.success ? 'Test Successful' : 'Test Failed'}
                                    </p>
                                    <Badge variant={testResult.success ? 'success' : 'destructive'} className="text-xs">
                                        {new Date(testResult.timestamp).toLocaleTimeString()}
                                    </Badge>
                                </div>

                                {testResult.success ? (
                                    <div className="space-y-2">
                                        <p className="text-sm text-green-700">
                                            Configuration is working correctly
                                        </p>
                                        {testResult.payload && (
                                            <div>
                                                <p className="text-xs font-medium text-green-800 mb-1">Sample Payload:</p>
                                                <pre className="text-xs bg-green-100 p-2 rounded border overflow-x-auto">
                                                    {JSON.stringify(testResult.payload, null, 2)}
                                                </pre>
                                            </div>
                                        )}
                                        {testResult.target_info && (
                                            <div>
                                                <p className="text-xs font-medium text-green-800 mb-1">Target Connection:</p>
                                                <p className="text-xs text-green-700">
                                                    {testResult.target_info.status || 'Connected successfully'}
                                                </p>
                                            </div>
                                        )}
                                    </div>
                                ) : (
                                    <div className="space-y-2">
                                        <p className="text-sm text-red-700">
                                            {testResult.error || 'Configuration test failed'}
                                        </p>
                                        {testResult.details && (
                                            <div>
                                                <p className="text-xs font-medium text-red-800 mb-1">Error Details:</p>
                                                <pre className="text-xs bg-red-100 p-2 rounded border overflow-x-auto">
                                                    {JSON.stringify(testResult.details, null, 2)}
                                                </pre>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                )}

                {/* Test History */}
                {testResult && (
                    <div className="pt-2 border-t">
                        <p className="text-xs text-muted-foreground">
                            Last tested: {new Date(testResult.timestamp).toLocaleString()}
                        </p>
                    </div>
                )}
            </CardContent>
        </Card>
    )
}