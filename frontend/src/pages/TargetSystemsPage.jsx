import { TargetSystemList } from '@/components/target-systems'

export default function TargetSystemsPage() {
  return (
    <div className="container mx-auto py-6">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Target Systems</h1>
          <p className="text-muted-foreground">
            Configura los sistemas de destino donde se enviarán los datos de telemetría de tus dispositivos IoT
          </p>
        </div>

        <TargetSystemList />
      </div>
    </div>
  )
}