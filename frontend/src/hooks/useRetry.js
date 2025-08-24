import { useCallback, useState } from 'react';
import { useNotifications } from './useNotifications';

/**
 * Hook for API retry logic with exponential backoff
 */
export const useApiRetry = () => {
    const [retryState, setRetryState] = useState({});
    const { showError, showWarning } = useNotifications();

    /**
     * Execute a function with retry logic
     * @param {Function} fn - Function to execute
     * @param {Object} options - Retry options
     * @param {number} options.maxRetries - Maximum number of retries (default: 3)
     * @param {number} options.baseDelay - Base delay in ms (default: 1000)
     * @param {number} options.maxDelay - Maximum delay in ms (default: 10000)
     * @param {Function} options.onRetry - Callback on retry
     * @param {boolean} options.showNotifications - Show retry notifications (default: true)
     * @returns {Promise} - Promise that resolves with the result or rejects with the final error
     */
    const executeWithRetry = useCallback(async (fn, options = {}) => {
        const {
            maxRetries = 3,
            baseDelay = 1000,
            maxDelay = 10000,
            onRetry,
            showNotifications = true
        } = options;

        let lastError;

        for (let attempt = 0; attempt <= maxRetries; attempt++) {
            try {
                const result = await fn();
                // Reset retry state on success
                setRetryState(prev => ({ ...prev, [fn.name]: null }));
                return result;
            } catch (error) {
                lastError = error;

                // If this is the last attempt, throw the error
                if (attempt === maxRetries) {
                    if (showNotifications) {
                        showError(
                            `Operation failed after ${maxRetries + 1} attempts: ${error.message}`,
                            { title: 'Operation Failed' }
                        );
                    }
                    throw error;
                }

                // Calculate delay with exponential backoff
                const delay = Math.min(baseDelay * Math.pow(2, attempt), maxDelay);

                // Update retry state
                setRetryState(prev => ({
                    ...prev,
                    [fn.name]: {
                        attempt: attempt + 1,
                        maxRetries,
                        nextRetryIn: delay
                    }
                }));

                // Call onRetry callback if provided
                if (onRetry) {
                    onRetry(error, attempt + 1);
                } else if (showNotifications) {
                    showWarning(
                        `Attempt ${attempt + 1} failed. Retrying in ${delay}ms...`,
                        {
                            title: 'Retrying Operation',
                            duration: delay
                        }
                    );
                }

                // Wait before retrying
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }

        throw lastError;
    }, [showError, showWarning]);

    /**
     * Check if a function is currently being retried
     * @param {string} fnName - Function name
     * @returns {boolean} - True if currently retrying
     */
    const isRetrying = useCallback((fnName) => {
        return retryState[fnName] !== null && retryState[fnName] !== undefined;
    }, [retryState]);

    /**
     * Get retry information for a function
     * @param {string} fnName - Function name
     * @returns {Object|null} - Retry information or null
     */
    const getRetryInfo = useCallback((fnName) => {
        return retryState[fnName] || null;
    }, [retryState]);

    /**
     * Clear retry state for a function
     * @param {string} fnName - Function name
     */
    const clearRetryState = useCallback((fnName) => {
        setRetryState(prev => {
            const newState = { ...prev };
            delete newState[fnName];
            return newState;
        });
    }, []);

    return {
        executeWithRetry,
        isRetrying,
        getRetryInfo,
        clearRetryState,
        retryState
    };
};

/**
 * Hook for simple retry logic without notifications
 */
export const useSimpleRetry = () => {
    /**
     * Execute a function with simple retry logic
     * @param {Function} fn - Function to execute
     * @param {number} maxRetries - Maximum number of retries (default: 3)
     * @param {number} delay - Delay between retries in ms (default: 1000)
     * @returns {Promise} - Promise that resolves with the result or rejects with the final error
     */
    const retry = useCallback(async (fn, maxRetries = 3, delay = 1000) => {
        let lastError;

        for (let attempt = 0; attempt <= maxRetries; attempt++) {
            try {
                return await fn();
            } catch (error) {
                lastError = error;

                if (attempt === maxRetries) {
                    throw error;
                }

                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }

        throw lastError;
    }, []);

    return { retry };
};

export default useApiRetry;