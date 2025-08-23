import { XMarkIcon } from '@heroicons/react/24/outline'
import { createContext, useContext } from 'react'
import { Button } from './button'

const DialogContext = createContext()

export function Dialog({ children, open, onOpenChange }) {
  return (
    <DialogContext.Provider value={{ open, onOpenChange }}>
      {children}
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div 
            className="fixed inset-0 bg-black bg-opacity-50" 
            onClick={() => onOpenChange?.(false)}
          />
          <div className="relative z-10">
            {children}
          </div>
        </div>
      )}
    </DialogContext.Provider>
  )
}

export function DialogTrigger({ children, asChild, ...props }) {
  const { onOpenChange } = useContext(DialogContext)
  
  if (asChild) {
    return children
  }
  
  return (
    <Button onClick={() => onOpenChange?.(true)} {...props}>
      {children}
    </Button>
  )
}

export function DialogContent({ children, className = "" }) {
  const { onOpenChange } = useContext(DialogContext)
  
  return (
    <div className={`
      bg-white rounded-lg shadow-lg max-w-md w-full mx-4 max-h-[90vh] overflow-auto
      ${className}
    `}>
      <div className="absolute top-4 right-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onOpenChange?.(false)}
        >
          <XMarkIcon className="w-4 h-4" />
        </Button>
      </div>
      {children}
    </div>
  )
}

export function DialogHeader({ children, className = "" }) {
  return (
    <div className={`px-6 py-4 border-b ${className}`}>
      {children}
    </div>
  )
}

export function DialogTitle({ children, className = "" }) {
  return (
    <h2 className={`text-lg font-semibold ${className}`}>
      {children}
    </h2>
  )
}

export function DialogDescription({ children, className = "" }) {
  return (
    <p className={`text-sm text-muted-foreground mt-1 ${className}`}>
      {children}
    </p>
  )
}

export function DialogFooter({ children, className = "" }) {
  return (
    <div className={`px-6 py-4 border-t flex items-center justify-end space-x-2 ${className}`}>
      {children}
    </div>
  )
}