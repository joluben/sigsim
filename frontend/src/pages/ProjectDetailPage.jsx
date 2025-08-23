import { useParams } from 'react-router-dom'
import { ProjectDetail } from '../components/projects'

export default function ProjectDetailPage() {
  const { id } = useParams()

  return <ProjectDetail projectId={id} />
}