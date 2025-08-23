import { create } from 'zustand'
import { devtools } from 'zustand/middleware'

const useSimulationStore = create(
    devtools(
        (set, get) => ({
            // State
            runningSimulations: {},
            simulationLogs: [],
            connected: false,
            loading: false,
            error: null,

            // Actions
            setRunningSimulations: (simulations) => set({ runningSimulations: simulations }),

            updateSimulationStatus: (projectId, status) => set((state) => ({
                runningSimulations: {
                    ...state.runningSimulations,
                    [projectId]: status
                }
            })),

            removeSimulation: (projectId) => set((state) => {
                const { [projectId]: removed, ...rest } = state.runningSimulations
                return { runningSimulations: rest }
            }),

            addSimulationLog: (logEntry) => set((state) => ({
                simulationLogs: [logEntry, ...state.simulationLogs].slice(0, 1000) // Keep last 1000 logs
            })),

            clearSimulationLogs: () => set({ simulationLogs: [] }),

            setConnected: (connected) => set({ connected }),

            setLoading: (loading) => set({ loading }),

            setError: (error) => set({ error }),

            clearError: () => set({ error: null }),

            // Computed values
            getSimulationStatus: (projectId) => {
                const { runningSimulations } = get()
                return runningSimulations[projectId] || null
            },

            isProjectRunning: (projectId) => {
                const { runningSimulations } = get()
                return runningSimulations[projectId]?.is_running || false
            },

            getTotalActiveDevices: () => {
                const { runningSimulations } = get()
                return Object.values(runningSimulations).reduce(
                    (total, sim) => total + (sim.active_devices || 0), 0
                )
            },

            getTotalMessagesSent: () => {
                const { runningSimulations } = get()
                return Object.values(runningSimulations).reduce(
                    (total, sim) => total + (sim.messages_sent || 0), 0
                )
            },

            getLogsForProject: (projectId) => {
                const { simulationLogs } = get()
                return simulationLogs.filter(log => log.project_id === projectId)
            }
        }),
        {
            name: 'simulation-store'
        }
    )
)

export default useSimulationStore