"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { BarChart3, TrendingUp, DollarSign, Zap, MapPin } from "lucide-react"
import { formatCurrency } from "@/lib/utils"

export default function AnalyticsPage() {
  const savings = {
    vsBanks: 36117,
    vsWise: 8234,
    vsCrypto: 2145,
  }

  const costBreakdown = [
    { corridor: "USD → EUR", provider: "Wise", asset: "USD", chain: "Bank", cost: 3850, count: 124 },
    { corridor: "USD → INR", provider: "Wise", asset: "USD", chain: "Bank", cost: 4400, count: 98 },
    { corridor: "USD → USDC", provider: "Kraken", asset: "USDC", chain: "Ethereum", cost: 2200, count: 156 },
    { corridor: "EUR → GBP", provider: "Wise", asset: "EUR", chain: "Bank", cost: 2100, count: 67 },
  ]

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-4xl font-bold tracking-tight text-foreground">Analytics & Reporting</h1>
        <p className="text-muted-foreground">
          Savings dashboard, cost breakdown, and performance insights
        </p>
      </div>

      <Tabs defaultValue="savings" className="space-y-4">
        <TabsList>
          <TabsTrigger value="savings">Savings</TabsTrigger>
          <TabsTrigger value="cost">Cost Breakdown</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="forecasting">Forecasting</TabsTrigger>
          <TabsTrigger value="historical">Historical</TabsTrigger>
        </TabsList>

        <TabsContent value="savings" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader>
                <CardTitle>vs Traditional Banks</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-4xl font-bold tracking-tight text-foreground text-green-600">
                  {formatCurrency(savings.vsBanks)}
                </div>
                <div className="text-sm text-muted-foreground mt-1">This month</div>
                <div className="text-xs text-green-600 mt-2">+12.5% vs last month</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>vs Wise</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-4xl font-bold tracking-tight text-foreground text-green-600">
                  {formatCurrency(savings.vsWise)}
                </div>
                <div className="text-sm text-muted-foreground mt-1">This month</div>
                <div className="text-xs text-green-600 mt-2">+8.2% vs last month</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>vs Crypto Rails</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-4xl font-bold tracking-tight text-foreground text-green-600">
                  {formatCurrency(savings.vsCrypto)}
                </div>
                <div className="text-sm text-muted-foreground mt-1">This month</div>
                <div className="text-xs text-green-600 mt-2">+5.1% vs last month</div>
              </CardContent>
            </Card>
          </div>
          <Card>
            <CardHeader>
              <CardTitle>Total Savings Breakdown</CardTitle>
              <CardDescription>Savings by category this month</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex items-center justify-between p-2 border rounded">
                  <span>Fee Reduction</span>
                  <span className="font-medium text-green-600">$28,450</span>
                </div>
                <div className="flex items-center justify-between p-2 border rounded">
                  <span>FX Optimization</span>
                  <span className="font-medium text-green-600">$5,234</span>
                </div>
                <div className="flex items-center justify-between p-2 border rounded">
                  <span>Route Optimization</span>
                  <span className="font-medium text-green-600">$2,433</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="cost" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Cost Breakdown</CardTitle>
              <CardDescription>By corridor, provider, asset, and chain</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Corridor</TableHead>
                    <TableHead>Provider</TableHead>
                    <TableHead>Asset</TableHead>
                    <TableHead>Chain</TableHead>
                    <TableHead>Total Cost</TableHead>
                    <TableHead>Count</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {costBreakdown.map((item, idx) => (
                    <TableRow key={idx}>
                      <TableCell className="font-medium">{item.corridor}</TableCell>
                      <TableCell>{item.provider}</TableCell>
                      <TableCell>{item.asset}</TableCell>
                      <TableCell>{item.chain}</TableCell>
                      <TableCell>{formatCurrency(item.cost)}</TableCell>
                      <TableCell>{item.count}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="performance" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Speed Heatmap</CardTitle>
                <CardDescription>Average delivery time by corridor</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {["USD → EUR: 1.2h", "USD → INR: 1.5h", "USD → USDC: 0.3h", "EUR → GBP: 1.0h"].map((item) => (
                    <div key={item} className="flex items-center justify-between p-2 border rounded">
                      <span>{item.split(":")[0]}</span>
                      <span className="font-medium">{item.split(":")[1]}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Reliability Heatmap</CardTitle>
                <CardDescription>Success rate by corridor</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {["USD → EUR: 99.2%", "USD → INR: 98.8%", "USD → USDC: 99.5%", "EUR → GBP: 99.0%"].map((item) => (
                    <div key={item} className="flex items-center justify-between p-2 border rounded">
                      <span>{item.split(":")[0]}</span>
                      <span className="font-medium text-green-600">{item.split(":")[1]}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="forecasting" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Monthly Treasury Forecasting</CardTitle>
              <CardDescription>Projected treasury and spend</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid gap-4 md:grid-cols-3">
                  <div className="p-4 border rounded">
                    <div className="text-sm text-muted-foreground">This Month</div>
                    <div className="text-2xl font-bold mt-1">$12.5M</div>
                  </div>
                  <div className="p-4 border rounded">
                    <div className="text-sm text-muted-foreground">Next Month (Forecast)</div>
                    <div className="text-2xl font-bold mt-1">$13.2M</div>
                    <div className="text-xs text-green-600 mt-1">+5.6%</div>
                  </div>
                  <div className="p-4 border rounded">
                    <div className="text-sm text-muted-foreground">3-Month Forecast</div>
                    <div className="text-2xl font-bold mt-1">$40.1M</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Spend Forecasting</CardTitle>
              <CardDescription>Projected costs and savings</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex items-center justify-between p-2 border rounded">
                  <span>Projected Costs (Next Month)</span>
                  <span className="font-medium">$45,200</span>
                </div>
                <div className="flex items-center justify-between p-2 border rounded">
                  <span>Projected Savings (Next Month)</span>
                  <span className="font-medium text-green-600">$38,500</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="historical" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Historical Route Performance</CardTitle>
              <CardDescription>Insights from past route executions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="p-4 border rounded-lg">
                  <div className="font-medium mb-2">Top Performing Routes</div>
                  <div className="space-y-2">
                    {["USD → EUR via Wise (99.2% success)", "USD → USDC via Kraken (99.5% success)", "EUR → GBP via Wise (99.0% success)"].map((route) => (
                      <div key={route} className="text-sm p-2 border rounded">
                        {route}
                      </div>
                    ))}
                  </div>
                </div>
                <div className="p-4 border rounded-lg">
                  <div className="font-medium mb-2">Cost Trends</div>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span>Average cost per $10k</span>
                      <span className="font-medium">$38.50</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span>Trend (30 days)</span>
                      <span className="text-green-600">-2.3%</span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
