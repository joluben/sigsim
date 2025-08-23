import { create } from 'zustand'
import { devtools } from 'zustand/middleware'

const useProjectStore = create(
    devtools(
        (set, get) => ({
            // State
            projects: [],
            currentProject: null,
            loading: false,
            error: null,

            // Actions
            setProjects: (projects) => set({ projects }),

            setCurrentProject: (project) => set({ currentProject: project }),

            addProject: (project) => set((state) => ({
                projects: [...state.projects, project]
            })),

            updateProject: (id, updates) => set((state) => ({
                projects: state.projects.map(project =>
                    project.id === id ? { ...project, ...updates } : project
                ),
                currentProject: state.currentProject?.id === id
                    ? { ...state.currentProject, ...updates }
                    : state.currentProject
            })),

            removeProject: (id) => set((state) => ({
                projects: state.projects.filter(project => project.id !== id),
                currentProject: state.currentProject?.id === id ? null : state.currentProject
            })),

            setLoading: (loading) => set({ loading }),

            setError: (error) => set({ error }),

            clearError: () => set({ error: null }),

            // Computed values
            getProjectById: (id) => {
                const { projects } = get()
                return projects.find(project => project.id === id)
            },

            getRunningProjects: () => {
                const { projects } = get()
                return projects.filter(project => project.is_running)
            },

            getTotalDeviceCount: () => {
                const { projects } = get()
                return projects.reduce((total, project) => total + (project.device_count || 0), 0)
            }
        }),
        {
            name: 'project-store'
        }
    )
)

export default useProjectStore