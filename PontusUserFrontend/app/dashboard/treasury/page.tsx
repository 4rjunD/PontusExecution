"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  Wallet,
  TrendingUp,
  ArrowRightLeft,
  DollarSign,
  Zap,
  Activity,
  Clock,
  CheckCircle2,
  AlertCircle,
  Users,
  Shield,
  FileText,
  Play,
  Pause,
  RefreshCw,
  Calendar,
  BarChart3,
  Settings,
  Eye,
  XCircle,
} from "lucide-react"
import { formatCurrency, formatDate } from "@/lib/utils"
import {
  getUnifiedBalances,
  getTreasuryFXRates,
  getGasPrices,
  getLiquidityData,
  getRebalancingRules,
  getCashPositioning,
  getPayoutForecast,
  getOptimalTime,
  getCorridorLiquidity,
} from "@/lib/api"

interface Balance {
  asset: string
  total_amount: number
  sources: Array<{
    source_type: string
    source_id: string
    asset: string
    amount: number
    network: string | null
    location: string
    last_updated: string
  }>
  usd_value: number
  allocation_percentage: number
}

interface RebalancingRule {
  id: string
  name: string
  source_asset: string
  target_asset: string
  target_percentage: number
  threshold_deviation: number
  status: string
  savings_estimate: number
}

interface CashPosition {
  asset: string
  recommended_allocation: number
  current_allocation: number
  optimal_rail: string
  reasoning: string
  estimated_savings: number
}

interface PayoutForecast {
  date: string
  amount: number
  currency: string
  recipient: string
  status: string
  optimal_route: string | null
  estimated_cost: number | null
}

interface AuditLog {
  id: string
  timestamp: string
  action: string
  user: string
  details: string
  status: string
}

interface Vendor {
  id: string
  name: string
  whitelisted: boolean
  last_payment: string
  total_paid: number
}

export default function TreasuryPage() {
  const [balances, setBalances] = useState<Balance[]>([])
  const [totalValue, setTotalValue] = useState(0)
  const [fxRates, setFxRates] = useState<any>({})
  const [gasPrices, setGasPrices] = useState<any>({})
  const [liquidity, setLiquidity] = useState<any>({})
  const [rebalancingRules, setRebalancingRules] = useState<RebalancingRule[]>([])
  const [cashPositions, setCashPositions] = useState<CashPosition[]>([])
  const [payoutForecasts, setPayoutForecasts] = useState<PayoutForecast[]>([])
  const [loading, setLoading] = useState(true)
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date())
  
  // Approval workflow state
  const [pendingApprovals, setPendingApprovals] = useState<any[]>([])
  const [vendors, setVendors] = useState<Vendor[]>([
    { id: "1", name: "Acme Corp", whitelisted: true, last_payment: "2024-01-15", total_paid: 50000 },
    { id: "2", name: "Tech Solutions Inc", whitelisted: true, last_payment: "2024-01-10", total_paid: 75000 },
    { id: "3", name: "Global Services", whitelisted: false, last_payment: "2024-01-05", total_paid: 30000 },
  ])
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([
    { id: "1", timestamp: new Date().toISOString(), action: "Rebalance Executed", user: "System", details: "USD → USDC: $5,000", status: "completed" },
    { id: "2", timestamp: new Date(Date.now() - 3600000).toISOString(), action: "Payout Approved", user: "Admin", details: "Vendor: Acme Corp, $10,000", status: "approved" },
    { id: "3", timestamp: new Date(Date.now() - 7200000).toISOString(), action: "Anomaly Detected", user: "System", details: "Unusual transfer pattern detected", status: "flagged" },
  ])
  const [anomalies, setAnomalies] = useState<any[]>([
    { id: "1", type: "Unusual Amount", description: "Transfer amount 3x higher than average", severity: "medium", detected: new Date().toISOString() },
    { id: "2", type: "New Recipient", description: "First payment to new vendor", severity: "low", detected: new Date(Date.now() - 3600000).toISOString() },
  ])

  const fetchTreasuryData = async () => {
    try {
      setLoading(true)
      const [
        balanceData,
        fxData,
        gasData,
        liquidityData,
        rulesData,
        positionData,
        forecastData,
      ] = await Promise.all([
        getUnifiedBalances(),
        getTreasuryFXRates().catch(() => ({ rates: {} })),
        getGasPrices().catch(() => ({ gas_prices: {} })),
        getLiquidityData().catch(() => ({ liquidity: {} })),
        getRebalancingRules(),
        getCashPositioning(),
        getPayoutForecast(30),
      ])

      setBalances(balanceData.balances || [])
      setTotalValue(balanceData.total_usd_value || 0)
      setFxRates(fxData.rates || {})
      setGasPrices(gasData.gas_prices || {})
      setLiquidity(liquidityData.liquidity || {})
      setRebalancingRules(rulesData.rules || [])
      setCashPositions(positionData.recommendations || [])
      setPayoutForecasts(forecastData.forecasts || [])
      setLastUpdate(new Date())
    } catch (error) {
      console.error("Error fetching treasury data:", error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchTreasuryData()
    // Refresh every 5 seconds
    const interval = setInterval(fetchTreasuryData, 5000)
    return () => clearInterval(interval)
  }, [])

  const handleRebalance = async (ruleId: string) => {
    // Simulate rebalancing execution
    alert(`Executing rebalancing rule: ${ruleId}`)
    // In production, this would call the backend API
  }

  const handleApprove = (approvalId: string) => {
    setPendingApprovals(prev => prev.filter(a => a.id !== approvalId))
    setAuditLogs(prev => [{
      id: Date.now().toString(),
      timestamp: new Date().toISOString(),
      action: "Payout Approved",
      user: "Current User",
      details: `Approval ID: ${approvalId}`,
      status: "approved"
    }, ...prev])
  }

  const handleReject = (approvalId: string) => {
    setPendingApprovals(prev => prev.filter(a => a.id !== approvalId))
    setAuditLogs(prev => [{
      id: Date.now().toString(),
      timestamp: new Date().toISOString(),
      action: "Payout Rejected",
      user: "Current User",
      details: `Approval ID: ${approvalId}`,
      status: "rejected"
    }, ...prev])
  }

  const toggleVendorWhitelist = (vendorId: string) => {
    setVendors(prev => prev.map(v => 
      v.id === vendorId ? { ...v, whitelisted: !v.whitelisted } : v
    ))
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-accent/20 p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h1 className="text-4xl font-bold tracking-tight text-foreground">Treasury Management</h1>
          <p className="text-muted-foreground text-lg">
            Unified balance view and automated rebalancing across all rails
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={fetchTreasuryData} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
          <div className="text-xs text-muted-foreground">
            Last updated: {lastUpdate.toLocaleTimeString()}
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Value</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{formatCurrency(totalValue)}</div>
            <div className="text-xs text-green-600 mt-1">+2.5% this month</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Active Rules</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{rebalancingRules.filter(r => r.status === "active").length}</div>
            <div className="text-xs text-muted-foreground mt-1">Rebalancing rules</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Pending Approvals</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{pendingApprovals.length}</div>
            <div className="text-xs text-muted-foreground mt-1">Awaiting review</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Anomalies</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-orange-600">{anomalies.length}</div>
            <div className="text-xs text-muted-foreground mt-1">Require attention</div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="balances" className="space-y-4">
        <TabsList>
          <TabsTrigger value="balances">Unified Balances</TabsTrigger>
          <TabsTrigger value="rebalancing">Rebalancing</TabsTrigger>
          <TabsTrigger value="forecasting">Payout Forecasting</TabsTrigger>
          <TabsTrigger value="positioning">Cash Positioning</TabsTrigger>
          <TabsTrigger value="approvals">Approvals</TabsTrigger>
          <TabsTrigger value="vendors">Vendors</TabsTrigger>
          <TabsTrigger value="audit">Audit Logs</TabsTrigger>
          <TabsTrigger value="liquidity">Liquidity Dashboard</TabsTrigger>
        </TabsList>

        {/* Unified Balances Tab */}
        <TabsContent value="balances" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Unified Balance View</CardTitle>
              <CardDescription>
                All balances across banks, Wise, exchanges, on/off-ramps, and stablecoin wallets
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Asset</TableHead>
                    <TableHead>Total Amount</TableHead>
                    <TableHead>USD Value</TableHead>
                    <TableHead>Allocation</TableHead>
                    <TableHead>Sources</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loading ? (
                    <TableRow>
                      <TableCell colSpan={5} className="text-center py-8">
                        <RefreshCw className="h-6 w-6 animate-spin mx-auto" />
                        <p className="mt-2 text-sm text-muted-foreground">Loading balances...</p>
                      </TableCell>
                    </TableRow>
                  ) : balances.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">
                        No balances found
                      </TableCell>
                    </TableRow>
                  ) : (
                    balances.map((balance, idx) => (
                      <TableRow key={idx}>
                        <TableCell className="font-medium">{balance.asset}</TableCell>
                        <TableCell>{formatCurrency(balance.total_amount, balance.asset)}</TableCell>
                        <TableCell>{formatCurrency(balance.usd_value)}</TableCell>
                        <TableCell>{balance.allocation_percentage.toFixed(1)}%</TableCell>
                        <TableCell>
                          <div className="flex flex-col gap-1">
                            {balance.sources.map((source, sIdx) => (
                              <span key={sIdx} className="text-xs text-muted-foreground">
                                {source.location} ({source.source_type})
                              </span>
                            ))}
                          </div>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Rebalancing Tab */}
        <TabsContent value="rebalancing" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Automated Rebalancing Rules</CardTitle>
                <CardDescription>Configure automatic rebalancing between assets and rails</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {rebalancingRules.map((rule) => (
                    <div key={rule.id} className="p-4 border rounded-lg">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="font-medium">{rule.name}</div>
                          <div className="text-sm text-muted-foreground mt-1">
                            {rule.source_asset} → {rule.target_asset} ({rule.target_percentage}%)
                          </div>
                          <div className="text-sm text-green-600 mt-1">
                            Savings: {formatCurrency(rule.savings_estimate)}/month
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className={`px-2 py-1 rounded text-xs ${
                            rule.status === "active" ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-800"
                          }`}>
                            {rule.status}
                          </span>
                          {rule.status === "active" && (
                            <Button size="sm" variant="outline" onClick={() => handleRebalance(rule.id)}>
                              <Play className="h-3 w-3" />
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                  <Button variant="outline" className="w-full">
                    <ArrowRightLeft className="mr-2 h-4 w-4" />
                    Add Rebalancing Rule
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Route Simulation</CardTitle>
                <CardDescription>Simulate rebalancing routes before execution</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium">From Asset</label>
                    <Select defaultValue="USD">
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="USD">USD</SelectItem>
                        <SelectItem value="EUR">EUR</SelectItem>
                        <SelectItem value="USDC">USDC</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-sm font-medium">To Asset</label>
                    <Select defaultValue="USDC">
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="USDC">USDC</SelectItem>
                        <SelectItem value="EUR">EUR</SelectItem>
                        <SelectItem value="USD">USD</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Amount</label>
                    <Input type="number" placeholder="10000" />
                  </div>
                  <Button className="w-full">
                    <Zap className="mr-2 h-4 w-4" />
                    Simulate Route
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Payout Forecasting Tab */}
        <TabsContent value="forecasting" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Upcoming Payout Forecast</CardTitle>
              <CardDescription>Forecasted payouts for the next 30 days</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Date</TableHead>
                    <TableHead>Recipient</TableHead>
                    <TableHead>Amount</TableHead>
                    <TableHead>Optimal Route</TableHead>
                    <TableHead>Est. Cost</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Action</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {payoutForecasts.map((forecast, idx) => (
                    <TableRow key={idx}>
                      <TableCell>{formatDate(forecast.date)}</TableCell>
                      <TableCell className="font-medium">{forecast.recipient}</TableCell>
                      <TableCell>{formatCurrency(forecast.amount, forecast.currency)}</TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {forecast.optimal_route || "Calculating..."}
                      </TableCell>
                      <TableCell>
                        {forecast.estimated_cost ? formatCurrency(forecast.estimated_cost) : "N/A"}
                      </TableCell>
                      <TableCell>
                        <span className={`px-2 py-1 rounded text-xs ${
                          forecast.status === "scheduled" ? "bg-blue-100 text-blue-800" :
                          forecast.status === "pending" ? "bg-yellow-100 text-yellow-800" :
                          "bg-green-100 text-green-800"
                        }`}>
                          {forecast.status}
                        </span>
                      </TableCell>
                      <TableCell>
                        <Button size="sm" variant="outline">
                          <Eye className="h-3 w-3 mr-1" />
                          View
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Cash Positioning Tab */}
        <TabsContent value="positioning" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Cash Positioning Recommendations</CardTitle>
              <CardDescription>Optimal asset allocation and rail recommendations</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {cashPositions.map((position, idx) => (
                  <div key={idx} className="p-4 border rounded-lg">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="font-medium">{position.asset}</div>
                        <div className="text-sm text-muted-foreground mt-1">
                          {position.reasoning}
                        </div>
                        <div className="mt-2 flex items-center gap-4">
                          <div>
                            <span className="text-xs text-muted-foreground">Current: </span>
                            <span className="font-medium">{position.current_allocation.toFixed(1)}%</span>
                          </div>
                          <div>
                            <span className="text-xs text-muted-foreground">Recommended: </span>
                            <span className="font-medium text-green-600">{position.recommended_allocation.toFixed(1)}%</span>
                          </div>
                          <div>
                            <span className="text-xs text-muted-foreground">Optimal Rail: </span>
                            <span className="font-medium">{position.optimal_rail}</span>
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-medium text-green-600">
                          {formatCurrency(position.estimated_savings)} savings
                        </div>
                        <Button size="sm" variant="outline" className="mt-2">
                          Optimize
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Optimal Time to Convert</CardTitle>
              <CardDescription>Get recommendations for cheapest times/routes to convert or move funds</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid gap-4 md:grid-cols-3">
                  <div>
                    <label className="text-sm font-medium">From Asset</label>
                    <Select defaultValue="USD">
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="USD">USD</SelectItem>
                        <SelectItem value="EUR">EUR</SelectItem>
                        <SelectItem value="USDC">USDC</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-sm font-medium">To Asset</label>
                    <Select defaultValue="EUR">
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="EUR">EUR</SelectItem>
                        <SelectItem value="USD">USD</SelectItem>
                        <SelectItem value="USDC">USDC</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Amount</label>
                    <Input type="number" placeholder="10000" />
                  </div>
                </div>
                <Button>
                  <Clock className="mr-2 h-4 w-4" />
                  Find Optimal Time & Route
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Approvals Tab */}
        <TabsContent value="approvals" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Pending Approvals</CardTitle>
              <CardDescription>Actions requiring approval</CardDescription>
            </CardHeader>
            <CardContent>
              {pendingApprovals.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  No pending approvals
                </div>
              ) : (
                <div className="space-y-3">
                  {pendingApprovals.map((approval) => (
                    <div key={approval.id} className="p-4 border rounded-lg">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="font-medium">{approval.action}</div>
                          <div className="text-sm text-muted-foreground mt-1">{approval.details}</div>
                          <div className="text-xs text-muted-foreground mt-1">
                            Requested by: {approval.requested_by} • {formatDate(approval.requested_at)}
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Button size="sm" variant="outline" onClick={() => handleReject(approval.id)}>
                            <XCircle className="h-3 w-3 mr-1" />
                            Reject
                          </Button>
                          <Button size="sm" onClick={() => handleApprove(approval.id)}>
                            <CheckCircle2 className="h-3 w-3 mr-1" />
                            Approve
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Anomaly Detection</CardTitle>
              <CardDescription>Suspicious patterns and anomalies detected</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {anomalies.map((anomaly) => (
                  <div key={anomaly.id} className="p-4 border rounded-lg border-orange-200 bg-orange-50">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <AlertCircle className="h-4 w-4 text-orange-600" />
                          <span className="font-medium">{anomaly.type}</span>
                          <span className={`px-2 py-0.5 rounded text-xs ${
                            anomaly.severity === "high" ? "bg-red-100 text-red-800" :
                            anomaly.severity === "medium" ? "bg-orange-100 text-orange-800" :
                            "bg-yellow-100 text-yellow-800"
                          }`}>
                            {anomaly.severity}
                          </span>
                        </div>
                        <div className="text-sm text-muted-foreground mt-1">{anomaly.description}</div>
                        <div className="text-xs text-muted-foreground mt-1">
                          Detected: {formatDate(anomaly.detected)}
                        </div>
                      </div>
                      <Button size="sm" variant="outline">
                        <Eye className="h-3 w-3 mr-1" />
                        Review
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Vendors Tab */}
        <TabsContent value="vendors" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Vendor Whitelisting</CardTitle>
              <CardDescription>Manage vendor whitelist for automated approvals</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Vendor Name</TableHead>
                    <TableHead>Whitelisted</TableHead>
                    <TableHead>Last Payment</TableHead>
                    <TableHead>Total Paid</TableHead>
                    <TableHead>Action</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {vendors.map((vendor) => (
                    <TableRow key={vendor.id}>
                      <TableCell className="font-medium">{vendor.name}</TableCell>
                      <TableCell>
                        <span className={`px-2 py-1 rounded text-xs ${
                          vendor.whitelisted ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-800"
                        }`}>
                          {vendor.whitelisted ? "Yes" : "No"}
                        </span>
                      </TableCell>
                      <TableCell>{formatDate(vendor.last_payment)}</TableCell>
                      <TableCell>{formatCurrency(vendor.total_paid)}</TableCell>
                      <TableCell>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => toggleVendorWhitelist(vendor.id)}
                        >
                          {vendor.whitelisted ? "Remove" : "Add"} to Whitelist
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Audit Logs Tab */}
        <TabsContent value="audit" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Audit Logs</CardTitle>
              <CardDescription>Full action-level audit trail for every treasury action</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Timestamp</TableHead>
                    <TableHead>Action</TableHead>
                    <TableHead>User</TableHead>
                    <TableHead>Details</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {auditLogs.map((log) => (
                    <TableRow key={log.id}>
                      <TableCell className="text-sm">{formatDate(log.timestamp)}</TableCell>
                      <TableCell className="font-medium">{log.action}</TableCell>
                      <TableCell>{log.user}</TableCell>
                      <TableCell className="text-sm text-muted-foreground">{log.details}</TableCell>
                      <TableCell>
                        <span className={`px-2 py-1 rounded text-xs ${
                          log.status === "completed" || log.status === "approved" ? "bg-green-100 text-green-800" :
                          log.status === "rejected" ? "bg-red-100 text-red-800" :
                          "bg-yellow-100 text-yellow-800"
                        }`}>
                          {log.status}
                        </span>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Liquidity Dashboard Tab */}
        <TabsContent value="liquidity" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Real-time FX Rates</CardTitle>
                <CardDescription>Live foreign exchange rates</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {Object.entries(fxRates).slice(0, 10).map(([pair, data]: [string, any]) => (
                    <div key={pair} className="flex items-center justify-between p-2 border rounded">
                      <span className="font-medium">{pair}</span>
                      <span className="text-sm">{data.rate?.toFixed(4) || "N/A"}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Gas Prices</CardTitle>
                <CardDescription>Real-time gas prices across networks</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {Object.entries(gasPrices).map(([network, data]: [string, any]) => (
                    <div key={network} className="flex items-center justify-between p-2 border rounded">
                      <span className="font-medium">{network}</span>
                      <span className="text-sm">{data.price_gwei?.toFixed(0) || "N/A"} gwei</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Corridor Liquidity</CardTitle>
              <CardDescription>Liquidity data for specific currency corridors</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2 mb-4">
                <div>
                  <label className="text-sm font-medium">From Currency</label>
                  <Select defaultValue="USD">
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="USD">USD</SelectItem>
                      <SelectItem value="EUR">EUR</SelectItem>
                      <SelectItem value="GBP">GBP</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="text-sm font-medium">To Currency</label>
                  <Select defaultValue="EUR">
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="EUR">EUR</SelectItem>
                      <SelectItem value="USD">USD</SelectItem>
                      <SelectItem value="GBP">GBP</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <Button>
                <BarChart3 className="mr-2 h-4 w-4" />
                Check Corridor Liquidity
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
