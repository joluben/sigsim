import { useCallback, useState } from 'react';

// Simple notification system (can be replaced with a more sophisticated solution later)
export const useNotifications = () => {
    const [notifications, setNotifications] = useState([]);

    const addNotification = useCallback((notification) => {
        const id = Date.now() + Math.random();
        const newNotification = {
            id,
            type: 'info', // 'success', 'error', 'warning', 'info'
            title: '',
            message: '',
            duration: 5000, // Auto-dismiss after 5 seconds
            ...notification,
        };

        setNotifications(prev => [...prev, newNotification]);

        // Auto-dismiss notification
        if (newNotification.duration > 0) {
            setTimeout(() => {
                removeNotification(id);
            }, newNotification.duration);
        }

        return id;
    }, []);

    const removeNotification = useCallback((id) => {
        setNotifications(prev => prev.filter(notification => notification.id !== id));
    }, []);

    const clearAllNotifications = useCallback(() => {
        setNotifications([]);
    }, []);

    // Convenience methods
    const showSuccess = useCallback((message, title = 'Success') => {
        return addNotification({ type: 'success', title, message });
    }, [addNotification]);

    const showError = useCallback((message, title = 'Error') => {
        return addNotification({ type: 'error', title, message, duration: 8000 });
    }, [addNotification]);

    const showWarning = useCallback((message, title = 'Warning') => {
        return addNotification({ type: 'warning', title, message });
    }, [addNotification]);

    const showInfo = useCallback((message, title = 'Info') => {
        return addNotification({ type: 'info', title, message });
    }, [addNotification]);

    return {
        notifications,
        addNotification,
        removeNotification,
        clearAllNotifications,
        showSuccess,
        showError,
        showWarning,
        showInfo,
    };
};

// Hook for handling API errors with notifications
export const useApiErrorHandler = () => {
    const { showError } = useNotifications();

    const handleError = useCallback((error, customMessage) => {
        let message = customMessage || 'An unexpected error occurred';

        if (error.response?.data?.message) {
            message = error.response.data.message;
        } else if (error.message) {
            message = error.message;
        }

        showError(message);
        console.error('API Error:', error);
    }, [showError]);

    return { handleError };
};