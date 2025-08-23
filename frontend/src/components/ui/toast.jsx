import { XMarkIcon } from '@heroicons/react/24/outline'
import {
    CheckCircleIcon,
    ExclamationCircleIcon,
    ExclamationTriangleIcon,
    InformationCircleIcon
} from '@heroicons/react/24/solid'
import { useEffect, useState } from 'react'

const iconMap = {
  success: CheckCircleIcon,
  error: ExclamationCircleIcon,
  warning: ExclamationTriangleIcon,
  info: InformationCircleIcon,
}

const colorMap = {
  success: 'bg-green-50 border-green-200 text-green-800',
  error: 'bg-red-50 border-red-200 text-red-800',
  warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
  info: 'bg-blue-50 border-blue-200 text-blue-800',
}

const iconColorMap = {
  success: 'text-green-400',
  error: 'text-red-400',
  warning: 'text-yellow-400',
  info: 'text-blue-400',
}

export function Toast({ notification, onClose }) {
  const [isVisible, setIsVisible] = useState(true)
  const Icon = iconMap[notification.type] || InformationCircleIcon

  useEffect(() => {
    if (notification.duration > 0) {
      const timer = setTimeout(() => {
        setIsVisible(false)
        setTimeout(() => onClose(notification.id), 300) // Wait for animation
      }, notification.duration)

      return () => clearTimeout(timer)
    }
  }, [notification.duration, notification.id, onClose])

  const handleClose = () => {
    setIsVisible(false)
    setTimeout(() => onClose(notification.id), 300)
  }

  return (
    <div
      className={`
        transform transition-all duration-300 ease-in-out
        ${isVisible ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'}
        max-w-sm w-full border rounded-lg p-4 shadow-lg
        ${colorMap[notification.type]}
      `}
    >
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <Icon className={`h-5 w-5 ${iconColorMap[notification.type]}`} />
        </div>
        <div className="ml-3 w-0 flex-1">
          {notification.title && (
            <p className="text-sm font-medium">{notification.title}</p>
          )}
          <p className={`text-sm ${notification.title ? 'mt-1' : ''}`}>
            {notification.message}
          </p>
        </div>
        <div className="ml-4 flex-shrink-0 flex">
          <button
            className="inline-flex text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            onClick={handleClose}
          >
            <span className="sr-only">Close</span>
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>
      </div>
    </div>
  )
}

export function ToastContainer({ notifications, onClose }) {
  return (
    <div className="fixed top-4 right-4 z-50 space-y-2">
      {notifications.map((notification) => (
        <Toast
          key={notification.id}
          notification={notification}
          onClose={onClose}
        />
      ))}
    </div>
  )
}