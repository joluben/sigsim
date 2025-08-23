import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import {
    CpuChipIcon,
    FolderIcon,
    FunnelIcon,
    MagnifyingGlassIcon,
    PlusIcon
} from '@heroicons/react/24/outline'
import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { DeviceList } from '../components/devices'
import { useProjects } from '../hooks'

export default function DevicesPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [projectFilter, setProjectFilter] = useState('all')
  const [statusFilter, setStatusFilter] = useState('all')

  // Fetch all projects to get their devices
  const { data: projects = [], isLoading } = useProjects()

  // Flatten all devices from all projects
  const allDevices = useMemo(() => {
    return projects.flatMap(project => 
      (project.devices || []).map(device => ({
        ...device,
        project: {
          id: project.id,
          name: project.name
        }
      }))
    )
  }, [projects])

  // Filter devices
  const filteredDevices = useMemo(() => {
    return allDevices.filter(device => {
      const matchesSearch = device.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        device.project.name.toLowerCase().includes(searchTerm.toLowerCase())
      
      const matchesProject = projectFilter === 'all' || device.project.id === projectFilter
      
      const matchesStatus = statusFilter === 'all' || 
        (statusFilter === 'enabled' && device.is_enabled) ||
        (statusFilter === 'disabled' && !device.is_enabled)
      
      return matchesSearch && matchesProject && matchesStatus
    })
  }, [allDevices, searchTerm, projectFilter, statusFilter])

  // Group devices by project for display
  const devicesByProject = useMemo(() => {
    const grouped = {}
    filteredDevices.forEach(device => {
      const projectId = device.project.id
      if (!grouped[projectId]) {
        grouped[projectId] = {
          project: device.project,
          devices: []
        }
      }
      grouped[projectId].devices.push(device)
    })
    return Object.values(grouped)
  }, [filteredDevices])

  const totalDevices = allDevices.length
  const enabledDevices = allDevices.filter(d => d.is_enabled).length

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">All Devices</h1>
          <p className="text-muted-foreground">
            Manage all your IoT devices across projects
          </p>
        </div>
        <Button asChild>
          <Link to="/projects">
            <PlusIcon className="w-4 h-4 mr-2" />
            Add Device to Project
          </Link>
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Devices</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalDevices}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Active Devices</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{enabledDevices}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Projects</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{projects.length}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Inactive Devices</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-600">{totalDevices - enabledDevices}</div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <FunnelIcon className="w-5 h-5" />
            <span>Filters</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 flex-1">
              <MagnifyingGlassIcon className="w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Search devices or projects..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="max-w-sm"
              />
            </div>
            
            <Select value={projectFilter} onValueChange={setProjectFilter}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="All Projects" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Projects</SelectItem>
                {projects.map((project) => (
                  <SelectItem key={project.id} value={project.id}>
                    <div className="flex items-center space-x-2">
                      <FolderIcon className="w-4 h-4" />
                      <span>{project.name}</span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="enabled">Enabled</SelectItem>
                <SelectItem value="disabled">Disabled</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Devices by Project */}
      {isLoading ? (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-muted-foreground">Loading devices...</p>
            </div>
          </CardContent>
        </Card>
      ) : devicesByProject.length === 0 ? (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center py-8">
              <CpuChipIcon className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium mb-2">
                {allDevices.length === 0 ? 'No devices found' : 'No devices match your filters'}
              </h3>
              <p className="text-muted-foreground mb-4">
                {allDevices.length === 0 
                  ? 'Create a project and add devices to get started'
                  : 'Try adjusting your search terms or filters'
                }
              </p>
              {allDevices.length === 0 ? (
                <Button asChild>
                  <Link to="/projects">
                    <PlusIcon className="w-4 h-4 mr-2" />
                    Create Project
                  </Link>
                </Button>
              ) : (
                <Button
                  variant="outline"
                  onClick={() => {
                    setSearchTerm('')
                    setProjectFilter('all')
                    setStatusFilter('all')
                  }}
                >
                  Clear Filters
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-6">
          {devicesByProject.map(({ project, devices }) => (
            <Card key={project.id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="flex items-center space-x-2">
                      <FolderIcon className="w-5 h-5" />
                      <span>{project.name}</span>
                      <Badge variant="outline">{devices.length} devices</Badge>
                    </CardTitle>
                    <CardDescription>
                      Devices in this project
                    </CardDescription>
                  </div>
                  <Button variant="outline" size="sm" asChild>
                    <Link to={`/projects/${project.id}`}>
                      View Project
                    </Link>
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <DeviceList
                  devices={devices}
                  isLoading={false}
                  projectId={project.id}
                  showFilters={false}
                  viewMode="table"
                />
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}