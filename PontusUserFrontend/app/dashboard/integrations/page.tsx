"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Database, CheckCircle2, XCircle } from "lucide-react"

export default function IntegrationsPage() {
  const integrations = [
    { name: "Wise Business", status: "connected", type: "Bank Rail" },
    { name: "Kraken", status: "connected", type: "Exchange" },
    { name: "Nium", status: "disconnected", type: "Bank Rail" },
    { name: "Transak", status: "connected", type: "On/Off-Ramp" },
    { name: "Socket", status: "connected", type: "Bridge" },
    { name: "LI.FI", status: "connected", type: "Bridge" },
    { name: "0x", status: "connected", type: "Liquidity" },
    { name: "Uniswap", status: "connected", type: "Liquidity" },
  ]

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-4xl font-bold tracking-tight text-foreground">Integrations</h1>
        <p className="text-muted-foreground">
          Connected services and API providers
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {integrations.map((integration) => (
          <Card key={integration.name}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">{integration.name}</CardTitle>
                {integration.status === "connected" ? (
                  <CheckCircle2 className="h-5 w-5 text-green-600" />
                ) : (
                  <XCircle className="h-5 w-5 text-red-600" />
                )}
              </div>
              <CardDescription>{integration.type}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className={`text-sm font-medium ${
                integration.status === "connected" ? "text-green-600" : "text-red-600"
              }`}>
                {integration.status === "connected" ? "Connected" : "Disconnected"}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

