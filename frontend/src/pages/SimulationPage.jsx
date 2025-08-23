import { LogViewer, SimulationDashboard } from '@/components/simulation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useState } from 'react';

export default function SimulationPage() {
  const [testProjectId, setTestProjectId] = useState('');
  const [showLogViewer, setShowLogViewer] = useState(false);

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Simulation Control</h1>
          <p className="text-muted-foreground">
            Monitor and control your IoT device simulations
          </p>
        </div>
      </div>

      {/* Test LogViewer Section */}
      <Card>
        <CardHeader>
          <CardTitle>Test Log Viewer</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center space-x-4">
            <div className="flex-1">
              <Label htmlFor="projectId">Project ID</Label>
              <Input
                id="projectId"
                placeholder="Enter project ID to test logs"
                value={testProjectId}
                onChange={(e) => setTestProjectId(e.target.value)}
              />
            </div>
            <Button
              onClick={() => setShowLogViewer(!showLogViewer)}
              disabled={!testProjectId.trim()}
            >
              {showLogViewer ? 'Hide' : 'Show'} Log Viewer
            </Button>
          </div>

          {showLogViewer && testProjectId && (
            <LogViewer projectId={testProjectId.trim()} />
          )}
        </CardContent>
      </Card>

      {/* Main Simulation Dashboard */}
      <SimulationDashboard />
    </div>
  );
}