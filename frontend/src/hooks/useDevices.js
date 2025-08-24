import { useMutation, useQuery, useQueryClient } from 'react-query';
import { deviceService } from '../services';
import { queryKeys } from './queryClient';

// Hook for fetching devices by project
export const useDevicesByProject = (projectId, options = {}) => {
    return useQuery({
        queryKey: queryKeys.devices.byProject(projectId),
        queryFn: () => deviceService.getByProject(projectId),
        enabled: !!projectId,
        select: (data) => data || [],
        ...options,
    });
};

// Hook for fetching a single device
export const useDevice = (id, options = {}) => {
    return useQuery({
        queryKey: queryKeys.devices.detail(id),
        queryFn: () => deviceService.getById(id),
        enabled: !!id,
        ...options,
    });
};

// Hook for device simulation status
export const useDeviceSimulationStatus = (id, options = {}) => {
    return useQuery({
        queryKey: queryKeys.devices.simulationStatus(id),
        queryFn: () => deviceService.getSimulationStatus(id),
        enabled: !!id,
        refetchInterval: 3000, // Refetch every 3 seconds for real-time status
        ...options,
    });
};

// Hook for creating a device
export const useCreateDevice = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ projectId, ...deviceData }) =>
            deviceService.create({ project_id: projectId, ...deviceData }),
        onSuccess: (newDevice) => {
            // Invalidate devices list for the project
            queryClient.invalidateQueries(
                queryKeys.devices.byProject(newDevice.project_id)
            );

            // Add the new device to the cache
            queryClient.setQueryData(
                queryKeys.devices.detail(newDevice.id),
                newDevice
            );

            // Also invalidate the project to update device count
            queryClient.invalidateQueries(
                queryKeys.projects.detail(newDevice.project_id)
            );
        },
        onError: (error) => {
            console.error('Error creating device:', error);
        },
    });
};

// Hook for updating a device
export const useUpdateDevice = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ id, ...data }) => deviceService.update(id, data),
        onSuccess: (updatedDevice) => {
            // Update the device in cache
            queryClient.setQueryData(
                queryKeys.devices.detail(updatedDevice.id),
                updatedDevice
            );

            // Invalidate devices list for the project
            queryClient.invalidateQueries(
                queryKeys.devices.byProject(updatedDevice.project_id)
            );
        },
        onError: (error) => {
            console.error('Error updating device:', error);
        },
    });
};

// Hook for deleting a device
export const useDeleteDevice = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: deviceService.delete,
        onMutate: async (deviceId) => {
            // Get device data before deletion for cleanup
            const device = queryClient.getQueryData(queryKeys.devices.detail(deviceId));
            return { device };
        },
        onSuccess: (_, deviceId, context) => {
            // Remove device from cache
            queryClient.removeQueries(queryKeys.devices.detail(deviceId));

            // Invalidate devices list for the project if we have the project ID
            if (context?.device?.project_id) {
                queryClient.invalidateQueries(
                    queryKeys.devices.byProject(context.device.project_id)
                );

                // Also invalidate the project to update device count
                queryClient.invalidateQueries(
                    queryKeys.projects.detail(context.device.project_id)
                );
            }
        },
        onError: (error) => {
            console.error('Error deleting device:', error);
        },
    });
};

// Hook for toggling device enabled status
export const useToggleDeviceEnabled = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ id, enabled }) => deviceService.toggleEnabled(id, enabled),
        onSuccess: (updatedDevice) => {
            // Update the device in cache
            queryClient.setQueryData(
                queryKeys.devices.detail(updatedDevice.id),
                updatedDevice
            );

            // Invalidate devices list for the project
            queryClient.invalidateQueries(
                queryKeys.devices.byProject(updatedDevice.project_id)
            );
        },
        onError: (error) => {
            console.error('Error toggling device status:', error);
        },
    });
};

// Hook for testing device configuration
export const useTestDeviceConfiguration = () => {
    return useMutation({
        mutationFn: deviceService.testConfiguration,
        onError: (error) => {
            console.error('Error testing device configuration:', error);
        },
    });
};