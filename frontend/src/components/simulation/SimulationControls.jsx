import { Button } from '@/components/ui/button';
import { useSimulationOperations } from '@/hooks/useSimulationOperations';
import {
    PlayIcon,
    StopIcon
} from '@heroicons/react/24/outline';

export default function SimulationControls({ projectId, isRunning }) {
    const {
        startSimulation,
        stopSimulation,
        isStarting,
        isStopping
    } = useSimulationOperations();

    const handleStart = () => {
        startSimulation(projectId);
    };

    const handleStop = () => {
        stopSimulation(projectId);
    };

    return (
        <div className="flex items-center space-x-2">
            {/* Control Buttons - Notifications are handled by useSimulationOperations */}
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