import { useMutation, useQuery, useQueryClient } from 'react-query';
import { targetSystemService } from '../services';
import { queryKeys } from './queryClient';

// Hook for fetching all target systems
export const useTargetSystems = () => {
    return useQuery({
        queryKey: queryKeys.targetSystems.all,
        queryFn: targetSystemService.getAll,
        select: (data) => data || [],
    });
};

// Hook for fetching a single target system
export const useTargetSystem = (id, options = {}) => {
    return useQuery({
        queryKey: queryKeys.targetSystems.detail(id),
        queryFn: () => targetSystemService.getById(id),
        enabled: !!id,
        ...options,
    });
};

// Hook for fetching supported target system types
export const useTargetSystemTypes = () => {
    return useQuery({
        queryKey: queryKeys.targetSystems.types,
        queryFn: targetSystemService.getSupportedTypes,
        staleTime: 30 * 60 * 1000, // 30 minutes - types don't change often
    });
};

// Hook for fetching configuration schema for a target system type
export const useTargetSystemConfigSchema = (type, options = {}) => {
    return useQuery({
        queryKey: queryKeys.targetSystems.schema(type),
        queryFn: () => targetSystemService.getConfigSchema(type),
        enabled: !!type,
        staleTime: 30 * 60 * 1000, // 30 minutes - schemas don't change often
        ...options,
    });
};

// Hook for creating a target system
export const useCreateTargetSystem = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: targetSystemService.create,
        onSuccess: (newTargetSystem) => {
            // Invalidate and refetch target systems list
            queryClient.invalidateQueries(queryKeys.targetSystems.all);

            // Add the new target system to the cache
            queryClient.setQueryData(
                queryKeys.targetSystems.detail(newTargetSystem.id),
                newTargetSystem
            );
        },
        onError: (error) => {
            console.error('Error creating target system:', error);
        },
    });
};

// Hook for updating a target system
export const useUpdateTargetSystem = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ id, ...data }) => targetSystemService.update(id, data),
        onSuccess: (updatedTargetSystem) => {
            // Update the target system in cache
            queryClient.setQueryData(
                queryKeys.targetSystems.detail(updatedTargetSystem.id),
                updatedTargetSystem
            );

            // Invalidate target systems list to ensure consistency
            queryClient.invalidateQueries(queryKeys.targetSystems.all);
        },
        onError: (error) => {
            console.error('Error updating target system:', error);
        },
    });
};

// Hook for deleting a target system
export const useDeleteTargetSystem = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: targetSystemService.delete,
        onSuccess: (_, deletedId) => {
            // Remove target system from cache
            queryClient.removeQueries(queryKeys.targetSystems.detail(deletedId));

            // Invalidate target systems list
            queryClient.invalidateQueries(queryKeys.targetSystems.all);
        },
        onError: (error) => {
            console.error('Error deleting target system:', error);
        },
    });
};

// Hook for testing connection to a target system
export const useTestTargetSystemConnection = () => {
    return useMutation({
        mutationFn: targetSystemService.testConnection,
        onError: (error) => {
            console.error('Error testing target system connection:', error);
        },
    });
};

// Hook for testing connection with configuration (before saving)
export const useTestTargetSystemConnectionConfig = () => {
    return useMutation({
        mutationFn: targetSystemService.testConnectionConfig,
        onError: (error) => {
            console.error('Error testing target system connection config:', error);
        },
    });
};