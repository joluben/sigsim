import { CheckIcon, ChevronDownIcon } from '@heroicons/react/24/outline'
import { useEffect, useRef, useState } from 'react'

export function Select({ 
  value, 
  onValueChange, 
  placeholder = "Select an option...",
  disabled = false,
  className = "",
  children 
}) {
  const [isOpen, setIsOpen] = useState(false)
  const selectRef = useRef(null)

  useEffect(() => {
    function handleClickOutside(event) {
      if (selectRef.current && !selectRef.current.contains(event.target)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleSelect = (selectedValue) => {
    onValueChange?.(selectedValue)
    setIsOpen(false)
  }

  return (
    <div className={`relative ${className}`} ref={selectRef}>
      <SelectTrigger 
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        isOpen={isOpen}
      >
        <SelectValue value={value} placeholder={placeholder} />
      </SelectTrigger>
      
      {isOpen && (
        <SelectContent>
          {children && typeof children === 'function' 
            ? children({ onSelect: handleSelect, selectedValue: value })
            : children
          }
        </SelectContent>
      )}
    </div>
  )
}

export function SelectTrigger({ children, onClick, disabled, isOpen, className = "" }) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className={`
        flex h-10 w-full items-center justify-between rounded-md border border-input 
        bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground 
        focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 
        disabled:cursor-not-allowed disabled:opacity-50
        ${className}
      `}
    >
      {children}
      <ChevronDownIcon className={`h-4 w-4 opacity-50 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
    </button>
  )
}

export function SelectValue({ value, placeholder }) {
  return (
    <span className={value ? '' : 'text-muted-foreground'}>
      {value || placeholder}
    </span>
  )
}

export function SelectContent({ children, className = "" }) {
  return (
    <div className={`
      absolute top-full left-0 right-0 z-50 mt-1 max-h-60 overflow-auto rounded-md 
      border bg-popover text-popover-foreground shadow-md
      ${className}
    `}>
      {children}
    </div>
  )
}

export function SelectItem({ value, onSelect, selectedValue, children, className = "" }) {
  const isSelected = value === selectedValue

  return (
    <div
      className={`
        relative flex w-full cursor-default select-none items-center rounded-sm py-1.5 pl-8 pr-2 
        text-sm outline-none hover:bg-accent hover:text-accent-foreground 
        focus:bg-accent focus:text-accent-foreground data-[disabled]:pointer-events-none 
        data-[disabled]:opacity-50 cursor-pointer
        ${className}
      `}
      onClick={() => onSelect?.(value)}
    >
      {isSelected && (
        <span className="absolute left-2 flex h-3.5 w-3.5 items-center justify-center">
          <CheckIcon className="h-4 w-4" />
        </span>
      )}
      {children}
    </div>
  )
}

export function SelectLabel({ children, className = "" }) {
  return (
    <div className={`py-1.5 pl-8 pr-2 text-sm font-semibold ${className}`}>
      {children}
    </div>
  )
}

export function SelectSeparator({ className = "" }) {
  return <div className={`-mx-1 my-1 h-px bg-muted ${className}`} />
}