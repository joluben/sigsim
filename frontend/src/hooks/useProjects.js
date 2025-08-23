import { useMutation, useQuery, useQueryClient } from 'react-query';
import { projectService } from '../services';
import { queryKeys } from './queryClient';

// Hook for fetching all projects
export const useProjects = () => {
    return useQuery({
        queryKey: queryKeys.projects.all,
        queryFn: projectService.getAll,
        select: (data) => data || [],
    });
};

// Hook for fetching a single project
export const useProject = (id, options = {}) => {
    return useQuery({
        queryKey: queryKeys.projects.detail(id),
        queryFn: () => projectService.getById(id),
        enabled: !!id,
        ...options,
    });
};

// Hook for project simulation status
export const useProjectSimulationStatus = (id, options = {}) => {
    return useQuery({
        queryKey: queryKeys.projects.simulationStatus(id),
        queryFn: () => projectService.getSimulationStatus(id),
        enabled: !!id,
        refetchInterval: 2000, // Refetch every 2 seconds for real-time status
        ...options,
    });
};

// Hook for creating a project
export const useCreateProject = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: projectService.create,
        onSuccess: (newProject) => {
            // Invalidate and refetch projects list
            queryClient.invalidateQueries(queryKeys.projects.all);

            // Add the new project to the cache
            queryClient.setQueryData(
                queryKeys.projects.detail(newProject.id),
                newProject
            );
        },
        onError: (error) => {
            console.error('Error creating project:', error);
        },
    });
};

// Hook for updating a project
export const useUpdateProject = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ id, ...data }) => projectService.update(id, data),
        onSuccess: (updatedProject) => {
            // Update the project in cache
            queryClient.setQueryData(
                queryKeys.projects.detail(updatedProject.id),
                updatedProject
            );

            // Invalidate projects list to ensure consistency
            queryClient.invalidateQueries(queryKeys.projects.all);
        },
        onError: (error) => {
            console.error('Error updating project:', error);
        },
    });
};

// Hook for deleting a project
export const useDeleteProject = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: projectService.delete,
        onSuccess: (_, deletedId) => {
            // Remove project from cache
            queryClient.removeQueries(queryKeys.projects.detail(deletedId));

            // Invalidate projects list
            queryClient.invalidateQueries(queryKeys.projects.all);

            // Also invalidate related devices
            queryClient.invalidateQueries(queryKeys.devices.byProject(deletedId));
        },
        onError: (error) => {
            console.error('Error deleting project:', error);
        },
    });
};

// Hook for exporting a project
export const useExportProject = () => {
    return useMutation({
        mutationFn: projectService.export,
        onSuccess: (blob, projectId) => {
            // Create download link
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `project-${projectId}-export.html`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);
        },
        onError: (error) => {
            console.error('Error exporting project:', error);
        },
    });
};

// Hook for starting project simulation
export const useStartProjectSimulation = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: projectService.startSimulation,
        onSuccess: (_, projectId) => {
            // Invalidate simulation status to get updated state
            queryClient.invalidateQueries(queryKeys.projects.simulationStatus(projectId));
            queryClient.invalidateQueries(queryKeys.simulation.status);
            queryClient.invalidateQueries(queryKeys.simulation.activeProjects);
        },
        onError: (error) => {
            console.error('Error starting simulation:', error);
        },
    });
};

// Hook for stopping project simulation
export const useStopProjectSimulation = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: projectService.stopSimulation,
        onSuccess: (_, projectId) => {
            // Invalidate simulation status to get updated state
            queryClient.invalidateQueries(queryKeys.projects.simulationStatus(projectId));
            queryClient.invalidateQueries(queryKeys.simulation.status);
            queryClient.invalidateQueries(queryKeys.simulation.activeProjects);
        },
        onError: (error) => {
            console.error('Error stopping simulation:', error);
        },
    });
};