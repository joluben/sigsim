import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
    BellIcon,
    Cog6ToothIcon,
    UserCircleIcon
} from '@heroicons/react/24/outline'
import { useLocation } from 'react-router-dom'

const pageNames = {
  '/': 'Dashboard',
  '/projects': 'Projects',
  '/devices': 'Devices', 
  '/payloads': 'Payloads',
  '/targets': 'Target Systems',
  '/simulation': 'Simulation'
}

export default function Header() {
  const location = useLocation()
  const currentPage = pageNames[location.pathname] || 'IoT Simulator'

  return (
    <header className="bg-background border-b border-border px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Page title and breadcrumb */}
        <div className="flex items-center space-x-4">
          <h1 className="text-2xl font-semibold text-foreground">
            {currentPage}
          </h1>
          
          {/* Status indicators */}
          <div className="flex items-center space-x-2">
            <Badge variant="success" className="text-xs">
              API Connected
            </Badge>
            <Badge variant="secondary" className="text-xs">
              0 Active Simulations
            </Badge>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center space-x-2">
          {/* Notifications */}
          <Button variant="ghost" size="icon" className="relative">
            <BellIcon className="w-5 h-5" />
            <span className="absolute -top-1 -right-1 w-3 h-3 bg-destructive rounded-full text-xs flex items-center justify-center text-white">
              3
            </span>
          </Button>

          {/* Settings */}
          <Button variant="ghost" size="icon">
            <Cog6ToothIcon className="w-5 h-5" />
          </Button>

          {/* User menu */}
          <Button variant="ghost" size="icon">
            <UserCircleIcon className="w-5 h-5" />
          </Button>
        </div>
      </div>
    </header>
  )
}