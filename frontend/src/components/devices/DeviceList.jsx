import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import {
  ChevronLeftIcon,
  ChevronRightIcon,
  ClockIcon,
  CpuChipIcon,
  DocumentTextIcon,
  FunnelIcon,
  MagnifyingGlassIcon,
  PauseIcon,
  PencilIcon,
  PlayIcon,
  ServerIcon,
  TrashIcon
} from '@heroicons/react/24/outline'
import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { useDeleteDevice, useToggleDeviceEnabled } from '../../hooks'
import { useNotificationContext } from '../providers/NotificationProvider'

const ITEMS_PER_PAGE = 10

export default function DeviceList({
  devices = [],
  isLoading,
  projectId,
  showFilters = true,
  viewMode = 'table' // 'table' or 'cards'
}) {
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [currentPage, setCurrentPage] = useState(1)

  const toggleEnabled = useToggleDeviceEnabled()
  const deleteDevice = useDeleteDevice()
  const { showSuccess, showError } = useNotificationContext()

  // Filter and search devices
  const filteredDevices = useMemo(() => {
    return devices.filter(device => {
      const matchesSearch = device.name.toLowerCase().includes(searchTerm.toLowerCase())
      const matchesStatus = statusFilter === 'all' ||
        (statusFilter === 'enabled' && device.is_enabled) ||
        (statusFilter === 'disabled' && !device.is_enabled)

      return matchesSearch && matchesStatus
    })
  }, [devices, searchTerm, statusFilter])

  // Pagination
  const totalPages = Math.ceil(filteredDevices.length / ITEMS_PER_PAGE)
  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE
  const paginatedDevices = filteredDevices.slice(startIndex, startIndex + ITEMS_PER_PAGE)

  const handleToggleEnabled = async (device) => {
    try {
      await toggleEnabled.mutateAsync({
        id: device.id,
        enabled: !device.is_enabled
      })
      showSuccess(`Device "${device.name}" ${device.is_enabled ? 'disabled' : 'enabled'}`)
    } catch (error) {
      showError('Failed to update device status')
    }
  }

  const handleDelete = async (device) => {
    if (window.confirm(`Are you sure you want to delete "${device.name}"?`)) {
      try {
        await deleteDevice.mutateAsync(device.id)
        showSuccess(`Device "${device.name}" deleted successfully`)
      } catch (error) {
        showError('Failed to delete device')
      }
    }
  }

  // Loading state
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <CpuChipIcon className="w-5 h-5" />
            <span>Devices</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="animate-pulse">
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-gray-200 rounded" />
                    <div>
                      <div className="h-4 bg-gray-200 rounded w-24 mb-1" />
                      <div className="h-3 bg-gray-200 rounded w-16" />
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="h-6 bg-gray-200 rounded w-16" />
                    <div className="h-8 bg-gray-200 rounded w-8" />
                    <div className="h-8 bg-gray-200 rounded w-8" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  // Empty state
  if (devices.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <CpuChipIcon className="w-5 h-5" />
            <span>Devices</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <CpuChipIcon className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">No devices yet</h3>
            <p className="text-muted-foreground mb-4">
              Add your first IoT device to start simulating data
            </p>
            <Button asChild>
              <Link to={`/projects/${projectId}/devices/new`}>
                Add Device
              </Link>
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center space-x-2">
            <CpuChipIcon className="w-5 h-5" />
            <span>Devices ({filteredDevices.length})</span>
          </CardTitle>
          <Button asChild>
            <Link to={`/projects/${projectId}/devices/new`}>
              Add Device
            </Link>
          </Button>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Filters */}
        {showFilters && (
          <div className="flex items-center space-x-4 p-4 bg-muted/50 rounded-lg">
            <div className="flex items-center space-x-2 flex-1">
              <MagnifyingGlassIcon className="w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Search devices..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="max-w-sm"
              />
            </div>

            <div className="flex items-center space-x-2">
              <FunnelIcon className="w-4 h-4 text-muted-foreground" />
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
          </div>
        )}

        {/* Devices Table */}
        {viewMode === 'table' ? (
          <div className="border rounded-lg">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Device</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Interval</TableHead>
                  <TableHead>Configuration</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {paginatedDevices.map((device) => (
                  <TableRow key={device.id}>
                    <TableCell>
                      <div className="flex items-center space-x-3">
                        <div className="p-2 bg-blue-100 rounded-lg">
                          <CpuChipIcon className="w-4 h-4 text-blue-600" />
                        </div>
                        <div>
                          <div className="font-medium">{device.name}</div>
                          <div className="text-sm text-muted-foreground">
                            ID: {device.id.slice(0, 8)}...
                          </div>
                        </div>
                      </div>
                    </TableCell>

                    <TableCell>
                      <Badge variant={device.is_enabled ? 'success' : 'secondary'}>
                        {device.is_enabled ? 'Enabled' : 'Disabled'}
                      </Badge>
                    </TableCell>

                    <TableCell>
                      <div className="flex items-center space-x-1">
                        <ClockIcon className="w-3 h-3 text-muted-foreground" />
                        <span>{device.send_interval}s</span>
                      </div>
                    </TableCell>

                    <TableCell>
                      <div className="flex items-center space-x-2">
                        {device.payload ? (
                          <Badge variant="default" className="text-xs">
                            <DocumentTextIcon className="w-3 h-3 mr-1" />
                            {device.payload.name}
                          </Badge>
                        ) : (
                          <Badge variant="outline" className="text-xs">
                            No Payload
                          </Badge>
                        )}

                        {device.target_system ? (
                          <Badge variant="default" className="text-xs">
                            <ServerIcon className="w-3 h-3 mr-1" />
                            {device.target_system.name}
                          </Badge>
                        ) : (
                          <Badge variant="outline" className="text-xs">
                            No Target
                          </Badge>
                        )}
                      </div>
                    </TableCell>

                    <TableCell className="text-right">
                      <div className="flex items-center justify-end space-x-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleToggleEnabled(device)}
                          disabled={toggleEnabled.isLoading}
                          title={device.is_enabled ? 'Disable device' : 'Enable device'}
                        >
                          {device.is_enabled ? (
                            <PauseIcon className="w-4 h-4" />
                          ) : (
                            <PlayIcon className="w-4 h-4" />
                          )}
                        </Button>

                        <Button
                          variant="ghost"
                          size="sm"
                          asChild
                          title="Edit device"
                        >
                          <Link to={`/projects/${projectId}/devices/${device.id}/edit`}>
                            <PencilIcon className="w-4 h-4" />
                          </Link>
                        </Button>

                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(device)}
                          disabled={deleteDevice.isLoading}
                          className="text-red-600 hover:text-red-700"
                          title="Delete device"
                        >
                          <TrashIcon className="w-4 h-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        ) : (
          /* Cards View */
          <div className="space-y-4">
            {paginatedDevices.map((device) => (
              <Card key={device.id} className="hover:shadow-sm transition-shadow">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-blue-100 rounded-lg">
                        <CpuChipIcon className="w-5 h-5 text-blue-600" />
                      </div>
                      <div>
                        <h4 className="font-medium">{device.name}</h4>
                        <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                          <span className="flex items-center space-x-1">
                            <ClockIcon className="w-3 h-3" />
                            <span>Every {device.send_interval}s</span>
                          </span>
                          {device.payload && (
                            <span>Payload: {device.payload.name}</span>
                          )}
                          {device.target_system && (
                            <span>Target: {device.target_system.name}</span>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-2">
                      <Badge variant={device.is_enabled ? 'success' : 'secondary'}>
                        {device.is_enabled ? 'Enabled' : 'Disabled'}
                      </Badge>

                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleToggleEnabled(device)}
                        disabled={toggleEnabled.isLoading}
                      >
                        {device.is_enabled ? (
                          <PauseIcon className="w-4 h-4" />
                        ) : (
                          <PlayIcon className="w-4 h-4" />
                        )}
                      </Button>

                      <Button
                        variant="ghost"
                        size="sm"
                        asChild
                      >
                        <Link to={`/projects/${projectId}/devices/${device.id}/edit`}>
                          <PencilIcon className="w-4 h-4" />
                        </Link>
                      </Button>

                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(device)}
                        disabled={deleteDevice.isLoading}
                        className="text-red-600 hover:text-red-700"
                      >
                        <TrashIcon className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between pt-4">
            <div className="text-sm text-muted-foreground">
              Showing {startIndex + 1} to {Math.min(startIndex + ITEMS_PER_PAGE, filteredDevices.length)} of {filteredDevices.length} devices
            </div>

            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                disabled={currentPage === 1}
              >
                <ChevronLeftIcon className="w-4 h-4" />
                Previous
              </Button>

              <div className="flex items-center space-x-1">
                {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                  <Button
                    key={page}
                    variant={currentPage === page ? "default" : "outline"}
                    size="sm"
                    onClick={() => setCurrentPage(page)}
                    className="w-8 h-8 p-0"
                  >
                    {page}
                  </Button>
                ))}
              </div>

              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                disabled={currentPage === totalPages}
              >
                Next
                <ChevronRightIcon className="w-4 h-4" />
              </Button>
            </div>
          </div>
        )}

        {/* No results */}
        {filteredDevices.length === 0 && devices.length > 0 && (
          <div className="text-center py-8">
            <MagnifyingGlassIcon className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">No devices found</h3>
            <p className="text-muted-foreground mb-4">
              Try adjusting your search terms or filters
            </p>
            <Button
              variant="outline"
              onClick={() => {
                setSearchTerm('')
                setStatusFilter('all')
                setCurrentPage(1)
              }}
            >
              Clear Filters
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
}