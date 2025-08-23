import { useMemo } from 'react'

export const useDeviceValidation = (device) => {
    return useMemo(() => {
        if (!device) {
            return {
                isValid: false,
                errors: ['Device not found'],
                warnings: [],
                isSimulationReady: false
            }
        }

        const errors = []
        const warnings = []

        // Required fields validation
        if (!device.name || device.name.trim().length === 0) {
            errors.push('Device name is required')
        }

        if (!device.payload_id) {
            errors.push('Payload generator is required')
        }

        if (!device.target_system_id) {
            errors.push('Target system is required')
        }

        // Send interval validation
        if (!device.send_interval || device.send_interval <= 0) {
            errors.push('Send interval must be greater than 0')
        } else if (device.send_interval > 3600) {
            warnings.push('Send interval is very high (>1 hour)')
        } else if (device.send_interval < 5) {
            warnings.push('Send interval is very low (<5 seconds)')
        }

        // Name validation
        if (device.name && device.name.length < 2) {
            errors.push('Device name must be at least 2 characters')
        } else if (device.name && device.name.length > 100) {
            errors.push('Device name must be less than 100 characters')
        }

        // Metadata validation (warnings only)
        if (device.metadata && Object.keys(device.metadata).length === 0) {
            warnings.push('No custom metadata defined (optional)')
        }

        const isValid = errors.length === 0
        const isSimulationReady = isValid && device.is_enabled

        return {
            isValid,
            errors,
            warnings,
            isSimulationReady,
            hasRequiredFields: !!(device.name && device.payload_id && device.target_system_id),
            hasValidInterval: device.send_interval > 0 && device.send_interval <= 3600
        }
    }, [device])
}

export const useDevicesValidation = (devices = []) => {
    return useMemo(() => {
        const validationResults = devices.map(device => ({
            device,
            validation: useDeviceValidation(device)
        }))

        const totalDevices = devices.length
        const validDevices = validationResults.filter(r => r.validation.isValid).length
        const simulationReadyDevices = validationResults.filter(r => r.validation.isSimulationReady).length
        const devicesWithErrors = validationResults.filter(r => r.validation.errors.length > 0).length
        const devicesWithWarnings = validationResults.filter(r => r.validation.warnings.length > 0).length

        const allErrors = validationResults.flatMap(r =>
            r.validation.errors.map(error => ({
                deviceId: r.device.id,
                deviceName: r.device.name,
                error
            }))
        )

        const allWarnings = validationResults.flatMap(r =>
            r.validation.warnings.map(warning => ({
                deviceId: r.device.id,
                deviceName: r.device.name,
                warning
            }))
        )

        return {
            totalDevices,
            validDevices,
            simulationReadyDevices,
            devicesWithErrors,
            devicesWithWarnings,
            allErrors,
            allWarnings,
            validationResults,
            isProjectSimulationReady: simulationReadyDevices > 0,
            allDevicesValid: validDevices === totalDevices && totalDevices > 0
        }
    }, [devices])
}

// Hook for validating device configuration before simulation
export const useSimulationValidation = (project, devices = []) => {
    const deviceValidation = useDevicesValidation(devices)

    return useMemo(() => {
        const errors = []
        const warnings = []

        // Project validation
        if (!project) {
            errors.push('Project not found')
            return { isValid: false, errors, warnings, canStartSimulation: false }
        }

        if (!project.name || project.name.trim().length === 0) {
            errors.push('Project name is required')
        }

        // Devices validation
        if (devices.length === 0) {
            errors.push('At least one device is required for simulation')
        } else {
            if (deviceValidation.simulationReadyDevices === 0) {
                errors.push('No devices are ready for simulation')
            }

            if (deviceValidation.devicesWithErrors > 0) {
                errors.push(`${deviceValidation.devicesWithErrors} device(s) have configuration errors`)
            }

            if (deviceValidation.devicesWithWarnings > 0) {
                warnings.push(`${deviceValidation.devicesWithWarnings} device(s) have configuration warnings`)
            }
        }

        const isValid = errors.length === 0
        const canStartSimulation = isValid && deviceValidation.simulationReadyDevices > 0

        return {
            isValid,
            errors,
            warnings,
            canStartSimulation,
            deviceValidation,
            readyDevicesCount: deviceValidation.simulationReadyDevices,
            totalDevicesCount: deviceValidation.totalDevices
        }
    }, [project, devices, deviceValidation])
}