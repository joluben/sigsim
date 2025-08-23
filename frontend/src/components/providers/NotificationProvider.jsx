import { createContext, useContext } from 'react'
import { useNotifications } from '../../hooks/useNotifications'
import { ToastContainer } from '../ui/toast'

const NotificationContext = createContext()

export function NotificationProvider({ children }) {
  const notificationMethods = useNotifications()

  return (
    <NotificationContext.Provider value={notificationMethods}>
      {children}
      <ToastContainer
        notifications={notificationMethods.notifications}
        onClose={notificationMethods.removeNotification}
      />
    </NotificationContext.Provider>
  )
}

export function useNotificationContext() {
  const context = useContext(NotificationContext)
  if (!context) {
    throw new Error('useNotificationContext must be used within a NotificationProvider')
  }
  return context
}