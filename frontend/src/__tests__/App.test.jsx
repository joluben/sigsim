import { render, screen } from '../test/utils'
import App from '../App'

// Mock the pages to avoid complex dependencies
jest.mock('../pages/ProjectsPage', () => {
  return function ProjectsPage() {
    return <div>Projects Page</div>
  }
})

jest.mock('../pages/ProjectDetailPage', () => {
  return function ProjectDetailPage() {
    return <div>Project Detail Page</div>
  }
})

jest.mock('../pages/DevicesPage', () => {
  return function DevicesPage() {
    return <div>Devices Page</div>
  }
})

jest.mock('../pages/PayloadBuilderPage', () => {
  return function PayloadBuilderPage() {
    return <div>Payload Builder Page</div>
  }
})

jest.mock('../pages/TargetSystemsPage', () => {
  return function TargetSystemsPage() {
    return <div>Target Systems Page</div>
  }
})

jest.mock('../pages/SimulationPage', () => {
  return function SimulationPage() {
    return <div>Simulation Page</div>
  }
})

jest.mock('../components/layout/Layout', () => {
  return function Layout({ children }) {
    return <div data-testid="layout">{children}</div>
  }
})

describe('App', () => {
  test('renders without crashing', () => {
    render(<App />)
    expect(screen.getByTestId('layout')).toBeInTheDocument()
  })

  test('renders projects page by default', () => {
    render(<App />)
    expect(screen.getByText('Projects Page')).toBeInTheDocument()
  })
})