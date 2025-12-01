"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Code, Key, Webhook, TestTube } from "lucide-react"
import { Button } from "@/components/ui/button"

export default function DeveloperPage() {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-4xl font-bold tracking-tight text-foreground">Developer Platform</h1>
        <p className="text-muted-foreground">
          API access, webhooks, and sandbox mode
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>API Keys</CardTitle>
            <CardDescription>Manage your API credentials</CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="outline" className="w-full">
              <Key className="mr-2 h-4 w-4" />
              Generate API Key
            </Button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Webhooks</CardTitle>
            <CardDescription>Configure status updates and audit logs</CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="outline" className="w-full">
              <Webhook className="mr-2 h-4 w-4" />
              Add Webhook
            </Button>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>API Documentation</CardTitle>
          <CardDescription>Complete API reference and examples</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="p-3 border rounded">
              <div className="font-medium">Route Optimization</div>
              <div className="text-sm text-muted-foreground">GET /api/routes/optimize</div>
            </div>
            <div className="p-3 border rounded">
              <div className="font-medium">Execute Route</div>
              <div className="text-sm text-muted-foreground">POST /api/routes/execute</div>
            </div>
            <div className="p-3 border rounded">
              <div className="font-medium">Execution Status</div>
              <div className="text-sm text-muted-foreground">GET /api/routes/executions/:id</div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Sandbox Mode</CardTitle>
          <CardDescription>Testnet execution for development</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium">Testnet Execution</div>
              <div className="text-sm text-muted-foreground">Safe testing environment</div>
            </div>
            <Button variant="outline">
              <TestTube className="mr-2 h-4 w-4" />
              Enable Sandbox
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

