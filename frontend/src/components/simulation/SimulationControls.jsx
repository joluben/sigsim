import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { useStartProjectSimulation, useStopProjectSimulation } from '@/hooks/useProjects';
import {
    CheckCircleIcon,
    ExclamationTriangleIcon,
    PlayIcon,
    StopIcon
} from '@heroicons/react/24/outline';
import { useState } from 'react';

export default function SimulationControls({ projectId, isRunning }) {
    const [isStarting, setIsStarting] = useState(false);
    const [isStopping, setIsStopping] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    const startSimulation = useStartProjectSimulation();
    const stopSimulation = useStopProjectSimulation();

    const handleStart = async () => {
        setIsStarting(true);
        setError(null);
        setSuccess(null);

        try {
            await startSimulation.mutateAsync(projectId);
            setSuccess('Simulation started successfully');
            setTimeout(() => setSuccess(null), 3000);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to start simulation');
            setTimeout(() => setError(null), 5000);
        } finally {
            setIsStarting(false);
        }
    };

    const handleStop = async () => {
        setIsStopping(true);
        setError(null);
        setSuccess(null);

        try {
            await stopSimulation.mutateAsync(projectId);
            setSuccess('Simulation stopped successfully');
            setTimeout(() => setSuccess(null), 3000);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to stop simulation');
            setTimeout(() => setError(null), 5000);
        } finally {
            setIsStopping(false);
        }
    };

    return (
        <div className="flex items-center space-x-2">
            {/* Success/Error Messages */}
            {success && (
                <Alert className="py-1 px-2 border-green-200 bg-green-50">
                    <CheckCircleIcon className="h-3 w-3 text-green-600" />
                    <AlertDescription className="text-xs text-green-700">
                        {success}
                    </AlertDescription>
                </Alert>
            )}

            {error && (
                <Alert variant="destructive" className="py-1 px-2">
                    <ExclamationTriangleIcon className="h-3 w-3" />
                    <AlertDescription className="text-xs">
                        {error}
                    </AlertDescription>
                </Alert>
            )}

            {/* Control Buttons */}
            {!isRunning ? (
                <Button
                    size="sm"
                    onClick={handleStart}
                    disabled={isStarting}
                    className="min-w-[80px]"
                >
                    {isStarting ? (
                        <>
                            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                            Starting...
                        </>
                    ) : (
                        <>
                            <PlayIcon className="w-4 h-4 mr-2" />
                            Start
                        </>
                    )}
                </Button>
            ) : (
                <Button
                    size="sm"
                    variant="destructive"
                    onClick={handleStop}
                    disabled={isStopping}
                    className="min-w-[80px]"
                >
                    {isStopping ? (
                        <>
                            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                            Stopping...
                        </>
                    ) : (
                        <>
                            <StopIcon className="w-4 h-4 mr-2" />
                            Stop
                        </>
                    )}
                </Button>
            )}
        </div>
    );
}