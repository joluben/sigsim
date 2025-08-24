import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import React from 'react'

export default function DeviceFormSimple({ device, projectId, onSuccess, onCancel }) {
    return (
        <Card>
            <CardHeader>
                <CardTitle>Device Form Test</CardTitle>
                <CardDescription>This is a simple test component</CardDescription>
            </CardHeader>
            <CardContent>
                <p>Device: {device ? device.name : 'New Device'}</p>
                <p>Project ID: {projectId}</p>
                <button onClick={() => onSuccess && onSuccess()}>Success</button>
                <button onClick={() => onCancel && onCancel()}>Cancel</button>
            </CardContent>
        </Card>
    )
}