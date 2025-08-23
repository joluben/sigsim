import { useNotifications } from '@/hooks/useNotifications';
import { useEffect } from 'react';

/**
 * Component that monitors simulation status and shows notifications for errors
 */
const SimulationNotifications = ({ simulationStatuses = [] }) => {
    const { showError, showWarning, showSuccess } = useNotifications();

    useEffect(() => {
        if (!simulationStatuses.length) return;

        // Check for new errors across all simulations
        simulationStatuses.forEach(status => {
            if (status.errors && status.errors.length > 0) {
                // Show notification for recent errors (within last 30 seconds)
                const recentErrors = status.errors.filter(error => {
                    const errorTime = new Date(error.timestamp);
                    const now = new Date();
                    return (now - errorTime) < 30000; // 30 seconds
                });

                recentErrors.forEach(error => {
                    showError(
                        `Device ${error.device_id}: ${error.error_message}`,
                        {
                            title: `Project ${status.project_id} Error`,
                            action: {
                                label: 'View Details',
                                onClick: () => {
                                    // Scroll to the project card
                                    const projectCard = document.querySelector(`[data-project-id="${status.project_id}"]`);
                                    if (projectCard) {
                                        projectCard.scrollIntoView({ behavior: 'smooth' });
                                        projectCard.click(); // Expand the project
                                    }
                                }
                            }
                        }
                    );
                });
            }

            // Check for devices that just went offline
            if (status.devices) {
                const offlineDevices = status.devices.filter(device =>
                    device.status === 'error' && device.last_error
                );

                offlineDevices.forEach(device => {
                    const errorTime = new Date(device.last_error.timestamp);
                    const now = new Date();

                    // Only show notification for recent offline events
                    if ((now - errorTime) < 30000) {
                        showWarning(
                            `Device ${device.device_id} went offline: ${device.last_error.message}`,
                            {
                                title: 'Device Offline',
                                action: {
                                    label: 'Retry Connection',
                                    onClick: () => {
                                        // TODO: Implement device retry logic
                                        console.log('Retry connection for device:', device.device_id);
                                    }
                                }
                            }
                        );
                    }
                });
            }
        });
    }, [simulationStatuses, showError, showWarning, showSuccess]);

    // This component doesn't render anything, it just handles notifications
    return null;
};

export default SimulationNotifications;