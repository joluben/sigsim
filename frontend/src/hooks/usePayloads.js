import { useMutation, useQuery, useQueryClient } from 'react-query';
import { payloadService } from '../services';
import { queryKeys } from './queryClient';

// Hook for fetching all payloads
export const usePayloads = () => {
    return useQuery({
        queryKey: queryKeys.payloads.all,
        queryFn: payloadService.getAll,
        select: (data) => data || [],
    });
};

// Hook for fetching a single payload
export const usePayload = (id, options = {}) => {
    return useQuery({
        queryKey: queryKeys.payloads.detail(id),
        queryFn: () => payloadService.getById(id),
        enabled: !!id,
        ...options,
    });
};

// Hook for creating a payload
export const useCreatePayload = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: payloadService.create,
        onSuccess: (newPayload) => {
            // Invalidate and refetch payloads list
            queryClient.invalidateQueries(queryKeys.payloads.all);

            // Add the new payload to the cache
            queryClient.setQueryData(
                queryKeys.payloads.detail(newPayload.id),
                newPayload
            );
        },
        onError: (error) => {
            console.error('Error creating payload:', error);
        },
    });
};

// Hook for updating a payload
export const useUpdatePayload = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ id, ...data }) => payloadService.update(id, data),
        onSuccess: (updatedPayload) => {
            // Update the payload in cache
            queryClient.setQueryData(
                queryKeys.payloads.detail(updatedPayload.id),
                updatedPayload
            );

            // Invalidate payloads list to ensure consistency
            queryClient.invalidateQueries(queryKeys.payloads.all);
        },
        onError: (error) => {
            console.error('Error updating payload:', error);
        },
    });
};

// Hook for deleting a payload
export const useDeletePayload = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: payloadService.delete,
        onSuccess: (_, deletedId) => {
            // Remove payload from cache
            queryClient.removeQueries(queryKeys.payloads.detail(deletedId));

            // Invalidate payloads list
            queryClient.invalidateQueries(queryKeys.payloads.all);
        },
        onError: (error) => {
            console.error('Error deleting payload:', error);
        },
    });
};

// Hook for generating sample payload
export const useGeneratePayloadSample = () => {
    return useMutation({
        mutationFn: ({ id, deviceMetadata }) =>
            payloadService.generateSample(id, deviceMetadata),
        onError: (error) => {
            console.error('Error generating payload sample:', error);
        },
    });
};

// Hook for validating payload configuration
export const useValidatePayload = () => {
    return useMutation({
        mutationFn: payloadService.validate,
        onError: (error) => {
            console.error('Error validating payload:', error);
        },
    });
};

// Hook for testing Python code
export const useTestPythonCode = () => {
    return useMutation({
        mutationFn: ({ pythonCode, deviceMetadata }) =>
            payloadService.testPythonCode(pythonCode, deviceMetadata),
        onError: (error) => {
            console.error('Error testing Python code:', error);
        },
    });
};