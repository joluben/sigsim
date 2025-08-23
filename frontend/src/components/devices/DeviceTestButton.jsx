import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import {
    CheckCircleIcon,
    ClockIcon,
    ExclamationCircleIcon,
    PlayIcon
} from '@heroicons/react/24/outline'
import { useState } from 'react'
import { useTestDeviceConfiguration } from '../../hooks'
import { useNotificationContext } from '../providers/NotificationProvider'

export default function DeviceTestButton({ deviceId, device, className = "" }) {
  const [testResult, setTestResult] = useState(null)
  const testDevice = useTestDeviceConfiguration()
  const { showSuccess, showError } = useNotificationContext()

  const handleTest = async () => {
    try {
      const result = await testDevice.mutateAsync(deviceId)
      setTestResult(result)
      showSuccess('Device configuration test completed successfully')
    } catch (error) {
      const errorMessage = error.response?.data?.message || error.message || 'Test failed'
      showError(`Device test failed: ${errorMessage}`)
      setTestResult({
        success: false,
        error: errorMessage
      })
    }
  }

  return (
    <div className={`space-y-4 ${className}`}>
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Test Configuration</CardTitle>
          <CardDescription>
            Test the device configuration by generating a sample payload and attempting to send it
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Button
            onClick={handleTest}
            disabled={testDevice.isLoading}
            className="w-full"
          >
            {testDevice.isLoading ? (
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Testing...</span>
              </div>
            ) : (
              <>
                <PlayIcon className="w-4 h-4 mr-2" />
                Test Device Configuration
              </>
            )}
          </Button>

          {testResult && (
            <div className={`p-4 rounded-lg border ${
              testResult.success 
                ? 'bg-green-50 border-green-200' 
                : 'bg-red-50 border-red-200'
            }`}>
              <div className="flex items-center space-x-2 mb-2">
                {testResult.success ? (
                  <CheckCircleIcon className="w-5 h-5 text-green-600" />
                ) : (
                  <ExclamationCircleIcon className="w-5 h-5 text-red-600" />
                )}
                <span className={`font-medium ${
                  testResult.success ? 'text-green-800' : 'text-red-800'
                }`}>
                  {testResult.success ? 'Test Successful' : 'Test Failed'}
                </span>
              </div>

              {testResult.success && testResult.payload && (
                <div className="space-y-2">
                  <p className="text-sm text-green-700">
                    Generated payload successfully:
                  </p>
                  <pre className="text-xs bg-white p-2 rounded border overflow-x-auto">
                    {JSON.stringify(testResult.payload, null, 2)}
                  </pre>
                  {testResult.sent_at && (
                    <div className="flex items-center space-x-1 text-xs text-green-600">
                      <ClockIcon className="w-3 h-3" />
                      <span>Sent at: {new Date(testResult.sent_at).toLocaleString()}</span>
                    </div>
                  )}
                </div>
              )}

              {!testResult.success && testResult.error && (
                <p className="text-sm text-red-700">
                  Error: {testResult.error}
                </p>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}