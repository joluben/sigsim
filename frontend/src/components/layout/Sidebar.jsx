import { cn } from '@/lib/utils'
import {
    CpuChipIcon,
    DocumentTextIcon,
    FolderIcon,
    HomeIcon,
    PlayIcon,
    ServerIcon
} from '@heroicons/react/24/outline'
import { Link, useLocation } from 'react-router-dom'

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Projects', href: '/projects', icon: FolderIcon },
  { name: 'Devices', href: '/devices', icon: CpuChipIcon },
  { name: 'Payloads', href: '/payloads', icon: DocumentTextIcon },
  { name: 'Target Systems', href: '/targets', icon: ServerIcon },
  { name: 'Simulation', href: '/simulation', icon: PlayIcon },
]

export default function Sidebar() {
  const location = useLocation()

  return (
    <div className="w-64 bg-card border-r border-border">
      <div className="flex flex-col h-full">
        {/* Logo */}
        <div className="flex items-center px-6 py-4 border-b border-border">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <CpuChipIcon className="w-5 h-5 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-lg font-semibold">IoT Simulator</h1>
              <p className="text-xs text-muted-foreground">Device Management</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-4 space-y-1">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href || 
              (item.href !== '/' && location.pathname.startsWith(item.href))
            
            return (
              <Link
                key={item.name}
                to={item.href}
                className={cn(
                  'flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                )}
              >
                <item.icon className="w-5 h-5 mr-3" />
                {item.name}
              </Link>
            )
          })}
        </nav>

        {/* Footer */}
        <div className="px-4 py-4 border-t border-border">
          <div className="text-xs text-muted-foreground">
            <p>Version 1.0.0</p>
            <p>© 2024 IoT Simulator</p>
          </div>
        </div>
      </div>
    </div>
  )
}