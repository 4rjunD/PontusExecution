"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Route,
  Zap,
  DollarSign,
  TrendingUp,
  Activity,
  Clock,
  CheckCircle2,
  AlertCircle,
} from "lucide-react"
import { healthCheck, getExecutionHistory } from "@/lib/api"
import { formatCurrency, formatDate } from "@/lib/utils"
import { SalesTracker } from "@/components/dashboard/sales-tracker"
import { GanttChart } from "@/components/dashboard/gantt-chart"

export default function DashboardPage() {
  const [health, setHealth] = useState<any>(null)
  const [executions, setExecutions] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchData() {
      try {
        const [healthData, execData] = await Promise.all([
          healthCheck(),
          getExecutionHistory(10),
        ])
        setHealth(healthData)
        setExecutions(execData.executions || [])
      } catch (error) {
        console.error("Error fetching dashboard data:", error)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const stats = [
    {
      title: "Total Savings",
      value: "$36,117",
      change: "+12.5%",
      icon: DollarSign,
      description: "vs traditional banks",
    },
    {
      title: "Routes Optimized",
      value: "1,247",
      change: "+8.2%",
      icon: Route,
      description: "This month",
    },
    {
      title: "Avg. Speed",
      value: "1.2h",
      change: "-15%",
      icon: Zap,
      description: "Faster than banks",
    },
    {
      title: "Success Rate",
      value: "99.2%",
      change: "+0.3%",
      icon: CheckCircle2,
      description: "Reliability score",
    },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-accent/20 p-6 space-y-6">
      <div className="space-y-1">
        <h1 className="text-4xl font-bold tracking-tight text-foreground">Dashboard</h1>
        <p className="text-muted-foreground text-lg">
          Overview of your multi-rail payment routing and execution
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <Card key={stat.title}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
                <Icon className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <p className="text-xs text-muted-foreground mt-1">
                  <span className="text-green-600">{stat.change}</span> {stat.description}
                </p>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="executions">Recent Executions</TabsTrigger>
          <TabsTrigger value="sales">Sales Tracker</TabsTrigger>
          <TabsTrigger value="tasks">Task Management</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
                <CardDescription>Common tasks and shortcuts</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                <button className="w-full text-left p-3 rounded-lg border hover:bg-accent">
                  <div className="font-medium">Create New Route</div>
                  <div className="text-sm text-muted-foreground">Optimize a payment route</div>
                </button>
                <button className="w-full text-left p-3 rounded-lg border hover:bg-accent">
                  <div className="font-medium">Batch Payout</div>
                  <div className="text-sm text-muted-foreground">Upload CSV for batch payments</div>
                </button>
                <button className="w-full text-left p-3 rounded-lg border hover:bg-accent">
                  <div className="font-medium">View Treasury</div>
                  <div className="text-sm text-muted-foreground">Check balances across rails</div>
                </button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>System Status</CardTitle>
                <CardDescription>Backend API connectivity</CardDescription>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="flex items-center gap-2">
                    <Activity className="h-4 w-4 animate-pulse" />
                    <span>Checking status...</span>
                  </div>
                ) : health ? (
                  <div className="flex items-center gap-2 text-green-600">
                    <CheckCircle2 className="h-4 w-4" />
                    <span>API Connected</span>
                  </div>
                ) : (
                  <div className="flex items-center gap-2 text-red-600">
                    <AlertCircle className="h-4 w-4" />
                    <span>API Disconnected</span>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="executions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recent Executions</CardTitle>
              <CardDescription>Latest payment route executions</CardDescription>
            </CardHeader>
            <CardContent>
              {executions.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  No executions yet. Create your first route to get started.
                </div>
              ) : (
                <div className="space-y-4">
                  {executions.map((exec) => (
                    <div
                      key={exec.execution_id}
                      className="flex items-center justify-between p-4 border rounded-lg"
                    >
                      <div>
                        <div className="font-medium">
                          {exec.from_asset} → {exec.to_asset}
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {formatCurrency(exec.amount)} • {exec.status}
                        </div>
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {exec.created_at ? formatDate(exec.created_at) : "N/A"}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="sales" className="space-y-4">
          <SalesTracker />
        </TabsContent>

        <TabsContent value="tasks" className="space-y-4">
          <GanttChart />
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Performance Analytics</CardTitle>
              <CardDescription>Route optimization and cost savings</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-muted-foreground">
                Analytics charts will be displayed here
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

