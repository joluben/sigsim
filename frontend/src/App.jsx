import { Route, Routes } from 'react-router-dom'
import Layout from './components/layout/Layout'
import { NotificationProvider } from './components/providers/NotificationProvider'
import DeviceFormPage from './pages/DeviceFormPage'
import DevicesPage from './pages/DevicesPage'
import PayloadBuilderPage from './pages/PayloadBuilderPage'
import ProjectDetailPage from './pages/ProjectDetailPage'
import ProjectsPage from './pages/ProjectsPage'
import SimulationPage from './pages/SimulationPage'
import TargetSystemsPage from './pages/TargetSystemsPage'

function App() {
  return (
    <NotificationProvider>
      <Layout>
        <Routes>
          <Route path="/" element={<ProjectsPage />} />
          <Route path="/projects" element={<ProjectsPage />} />
          <Route path="/projects/:id" element={<ProjectDetailPage />} />
          <Route path="/projects/:projectId/devices/new" element={<DeviceFormPage />} />
          <Route path="/devices" element={<DevicesPage />} />
          <Route path="/projects/:projectId/devices/:deviceId/edit" element={<DeviceFormPage />} />
          <Route path="/payloads" element={<PayloadBuilderPage />} />
          <Route path="/targets" element={<TargetSystemsPage />} />
          <Route path="/simulation" element={<SimulationPage />} />
        </Routes>
      </Layout>
    </NotificationProvider>
  )
}

export default App