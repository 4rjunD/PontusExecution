"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { TrendingUp, DollarSign, Users, Activity } from "lucide-react"

export function SalesTracker() {
  const stats = [
    { label: "Total Revenue", value: "$1,247,890", change: "+12.5%", icon: DollarSign },
    { label: "Active Routes", value: "1,247", change: "+8.2%", icon: Activity },
    { label: "Customers", value: "342", change: "+15.3%", icon: Users },
    { label: "Avg. Transaction", value: "$3,642", change: "+5.1%", icon: TrendingUp },
  ]

  const recentTransactions = [
    { id: 1, customer: "Acme Corp", amount: 12500, route: "USD → EUR", status: "completed", time: "2m ago" },
    { id: 2, customer: "TechStart Inc", amount: 8500, route: "USD → INR", status: "processing", time: "5m ago" },
    { id: 3, customer: "Global Ltd", amount: 23400, route: "EUR → GBP", status: "completed", time: "12m ago" },
    { id: 4, customer: "Finance Co", amount: 15600, route: "USD → USDC", status: "completed", time: "18m ago" },
  ]

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <Card key={stat.label}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{stat.label}</CardTitle>
                <Icon className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <p className="text-xs text-green-600 mt-1">{stat.change}</p>
              </CardContent>
            </Card>
          )
        })}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Live Transactions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recentTransactions.map((tx) => (
              <div
                key={tx.id}
                className="flex items-center justify-between p-4 border rounded-lg hover:bg-accent transition-colors"
              >
                <div className="flex-1">
                  <div className="font-medium">{tx.customer}</div>
                  <div className="text-sm text-muted-foreground">{tx.route}</div>
                </div>
                <div className="text-right">
                  <div className="font-bold">${tx.amount.toLocaleString()}</div>
                  <div className="text-xs text-muted-foreground">{tx.time}</div>
                </div>
                <div className="ml-4">
                  <span
                    className={`px-2 py-1 rounded text-xs font-medium ${
                      tx.status === "completed"
                        ? "bg-green-100 text-green-800"
                        : "bg-yellow-100 text-yellow-800"
                    }`}
                  >
                    {tx.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

