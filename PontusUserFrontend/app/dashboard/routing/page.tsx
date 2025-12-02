"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Route, Zap, Play, Pause, Square, RefreshCw, GitCompare, FileText, Clock } from "lucide-react"
import { optimizeRoute, executeRoute, getRouteSegments } from "@/lib/api"
import { formatCurrency, formatDate } from "@/lib/utils"

export default function RoutingPage() {
  const [fromAsset, setFromAsset] = useState("USD")
  const [toAsset, setToAsset] = useState("EUR")
  const [amount, setAmount] = useState("1000")
  const [loading, setLoading] = useState(false)
  const [route, setRoute] = useState<any>(null)
  const [execution, setExecution] = useState<any>(null)
  const [comparisonRoutes, setComparisonRoutes] = useState<any[]>([])
  const [auditTrail, setAuditTrail] = useState<any[]>([])

  const handleOptimize = async () => {
    setLoading(true)
    try {
      const result = await optimizeRoute({
        from_asset: fromAsset,
        to_asset: toAsset,
        amount: parseFloat(amount),
      })
      setRoute(result)
      
      // Simulate comparison routes
      setComparisonRoutes([
        { name: "Direct Bank", cost: parseFloat(amount) * 0.03 + 35, time: 72, reliability: 4.2 },
        { name: "Wise Direct", cost: parseFloat(amount) * 0.0035, time: 1.5, reliability: 4.8 },
        { name: "Crypto Route", cost: parseFloat(amount) * 0.004, time: 0.5, reliability: 4.5 },
        result,
      ])
    } catch (error) {
      console.error("Error optimizing route:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleExecute = async () => {
    if (!route) return
    setLoading(true)
    try {
      const result = await executeRoute({
        from_asset: fromAsset,
        to_asset: toAsset,
        amount: parseFloat(amount),
        parallel: false,
        enable_ai_rerouting: true,
      })
      setExecution(result)
      
      // Create audit trail
      setAuditTrail([
        { timestamp: new Date(), action: "Route Optimized", details: `Selected route: ${route.route?.length || 0} segments` },
        { timestamp: new Date(), action: "Execution Started", details: `Amount: ${formatCurrency(parseFloat(amount))}` },
        ...(result.segment_executions || []).map((seg: any, idx: number) => ({
          timestamp: new Date(),
          action: `Segment ${idx + 1} Executed`,
          details: `${seg.from_asset} → ${seg.to_asset} via ${seg.provider}`,
          fees: seg.fees_paid,
          status: seg.status,
        })),
      ])
    } catch (error) {
      console.error("Error executing route:", error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-4xl font-bold tracking-tight text-foreground">Route & Execute</h1>
        <p className="text-muted-foreground">
          AI-powered multi-rail payment routing and execution
        </p>
      </div>

      <Tabs defaultValue="optimize" className="space-y-4">
        <TabsList>
          <TabsTrigger value="optimize">Optimize Route</TabsTrigger>
          <TabsTrigger value="simulate">Simulation Mode</TabsTrigger>
          <TabsTrigger value="compare">Compare Routes</TabsTrigger>
          <TabsTrigger value="audit">Audit Trail</TabsTrigger>
        </TabsList>

        <TabsContent value="optimize" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Route Configuration</CardTitle>
              <CardDescription>Configure your payment route parameters</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-3">
                <div>
                  <label className="text-sm font-medium mb-2 block">From Asset</label>
                  <select
                    className="w-full px-3 py-2 border rounded-md"
                    value={fromAsset}
                    onChange={(e) => setFromAsset(e.target.value)}
                  >
                    <option value="USD">USD</option>
                    <option value="EUR">EUR</option>
                    <option value="GBP">GBP</option>
                    <option value="INR">INR</option>
                    <option value="USDC">USDC</option>
                    <option value="USDT">USDT</option>
                  </select>
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">To Asset</label>
                  <select
                    className="w-full px-3 py-2 border rounded-md"
                    value={toAsset}
                    onChange={(e) => setToAsset(e.target.value)}
                  >
                    <option value="USD">USD</option>
                    <option value="EUR">EUR</option>
                    <option value="GBP">GBP</option>
                    <option value="INR">INR</option>
                    <option value="USDC">USDC</option>
                    <option value="USDT">USDT</option>
                  </select>
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Amount</label>
                  <Input
                    type="number"
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    placeholder="1000"
                  />
                </div>
              </div>
              <Button onClick={handleOptimize} disabled={loading} className="w-full">
                {loading ? (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                    Optimizing...
                  </>
                ) : (
                  <>
                    <Route className="mr-2 h-4 w-4" />
                    Optimize Route
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {route && (
            <Card>
              <CardHeader>
                <CardTitle>Optimized Route</CardTitle>
                <CardDescription>Best route found based on cost, speed, and reliability</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4 md:grid-cols-3">
                  <div>
                    <div className="text-sm text-muted-foreground">Total Cost</div>
                    <div className="text-2xl font-bold">
                      {formatCurrency(route.cost_percent ? (parseFloat(amount) * route.cost_percent / 100) : 0)}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {route.cost_percent?.toFixed(2)}% of amount
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">Estimated Time</div>
                    <div className="text-2xl font-bold">{route.eta_hours?.toFixed(1)}h</div>
                    <div className="text-xs text-muted-foreground">Average delivery</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">Reliability</div>
                    <div className="text-2xl font-bold">{route.reliability?.toFixed(1)}/5</div>
                    <div className="text-xs text-muted-foreground">Success rate</div>
                  </div>
                </div>

                {route.route && route.route.length > 0 && (
                  <div className="space-y-2">
                    <div className="font-medium">Route Segments:</div>
                    {route.route.map((segment: any, idx: number) => (
                      <div key={idx} className="flex items-center gap-2 p-2 border rounded">
                        <span className="font-medium">{segment.from_asset}</span>
                        <span>→</span>
                        <span className="font-medium">{segment.to_asset}</span>
                        <span className="ml-auto text-sm text-muted-foreground">
                          {segment.provider}
                        </span>
                      </div>
                    ))}
                  </div>
                )}

                <Button onClick={handleExecute} disabled={loading} className="w-full">
                  <Play className="mr-2 h-4 w-4" />
                  Execute Route
                </Button>
              </CardContent>
            </Card>
          )}

          {execution && (
            <Card>
              <CardHeader>
                <CardTitle>Execution Status</CardTitle>
                <CardDescription>Real-time execution tracking</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span>Status:</span>
                    <span className="font-medium">{execution.status}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Execution ID:</span>
                    <span className="font-mono text-sm">{execution.execution_id}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Final Amount:</span>
                    <span className="font-medium">
                      {formatCurrency(execution.final_amount || 0, execution.to_asset)}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="simulate">
          <Card>
            <CardHeader>
              <CardTitle>Simulation Mode</CardTitle>
              <CardDescription>Test routes without moving real money</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="p-4 border rounded-lg bg-blue-50">
                  <div className="font-medium text-blue-900">Testnet Execution</div>
                  <div className="text-sm text-blue-700 mt-1">
                    All transactions are simulated on testnets. No real money will be moved.
                  </div>
                </div>
                <Button className="w-full">
                  <Zap className="mr-2 h-4 w-4" />
                  Start Simulation
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="compare">
          <Card>
            <CardHeader>
              <CardTitle>Route Comparison</CardTitle>
              <CardDescription>Compare multiple route options side by side</CardDescription>
            </CardHeader>
            <CardContent>
              {comparisonRoutes.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Route</TableHead>
                      <TableHead>Cost</TableHead>
                      <TableHead>Time (hours)</TableHead>
                      <TableHead>Reliability</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {comparisonRoutes.map((r, idx) => (
                      <TableRow key={idx}>
                        <TableCell className="font-medium">{r.name || "Optimized"}</TableCell>
                        <TableCell>{formatCurrency(r.cost || 0)}</TableCell>
                        <TableCell>{r.time || r.eta_hours || "N/A"}</TableCell>
                        <TableCell>{r.reliability || "N/A"}/5</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  Optimize a route first to see comparisons
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="audit">
          <Card>
            <CardHeader>
              <CardTitle>Per-Transaction Audit Trail</CardTitle>
              <CardDescription>Complete history of route chosen, fees, timestamps, and confirmations</CardDescription>
            </CardHeader>
            <CardContent>
              {auditTrail.length > 0 ? (
                <div className="space-y-4">
                  {auditTrail.map((entry, idx) => (
                    <div key={idx} className="flex items-start gap-4 p-4 border rounded-lg">
                      <Clock className="h-5 w-5 text-muted-foreground mt-0.5" />
                      <div className="flex-1">
                        <div className="font-medium">{entry.action}</div>
                        <div className="text-sm text-muted-foreground">{entry.details}</div>
                        {entry.fees && (
                          <div className="text-sm mt-1">Fees: {formatCurrency(entry.fees)}</div>
                        )}
                        <div className="text-xs text-muted-foreground mt-1">
                          {formatDate(entry.timestamp)}
                        </div>
                      </div>
                      {entry.status && (
                        <span className={`px-2 py-1 rounded text-xs ${
                          entry.status === "completed" ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"
                        }`}>
                          {entry.status}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  No audit trail yet. Execute a route to see the complete history.
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
