import { create } from 'zustand'
import { devtools } from 'zustand/middleware'

const useDeviceStore = create(
    devtools(
        (set, get) => ({
            // State
            devices: [],
            currentDevice: null,
            loading: false,
            error: null,

            // Actions
            setDevices: (devices) => set({ devices }),

            setCurrentDevice: (device) => set({ currentDevice: device }),

            addDevice: (device) => set((state) => ({
                devices: [...state.devices, device]
            })),

            updateDevice: (id, updates) => set((state) => ({
                devices: state.devices.map(device =>
                    device.id === id ? { ...device, ...updates } : device
                ),
                currentDevice: state.currentDevice?.id === id
                    ? { ...state.currentDevice, ...updates }
                    : state.currentDevice
            })),

            removeDevice: (id) => set((state) => ({
                devices: state.devices.filter(device => device.id !== id),
                currentDevice: state.currentDevice?.id === id ? null : state.currentDevice
            })),

            bulkUpdateDevices: (deviceIds, updates) => set((state) => ({
                devices: state.devices.map(device =>
                    deviceIds.includes(device.id) ? { ...device, ...updates } : device
                )
            })),

            setLoading: (loading) => set({ loading }),

            setError: (error) => set({ error }),

            clearError: () => set({ error: null }),

            // Computed values
            getDeviceById: (id) => {
                const { devices } = get()
                return devices.find(device => device.id === id)
            },

            getDevicesByProject: (projectId) => {
                const { devices } = get()
                return devices.filter(device => device.project_id === projectId)
            },

            getEnabledDevices: () => {
                const { devices } = get()
                return devices.filter(device => device.is_enabled)
            },

            getDevicesWithoutPayload: () => {
                const { devices } = get()
                return devices.filter(device => !device.has_payload)
            },

            getDevicesWithoutTarget: () => {
                const { devices } = get()
                return devices.filter(device => !device.has_target)
            }
        }),
        {
            name: 'device-store'
        }
    )
)

export default useDeviceStore