"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { FileText, Download, CheckCircle2, AlertCircle, DollarSign } from "lucide-react"
import { formatCurrency, formatDate } from "@/lib/utils"

export default function ReconciliationPage() {
  const matched = [
    { payment: "PAY-001", invoice: "INV-2025-001", amount: 5000, currency: "USD", date: new Date(), status: "matched" },
    { payment: "PAY-002", invoice: "INV-2025-002", amount: 3200, currency: "USD", date: new Date(), status: "matched" },
    { payment: "PAY-003", invoice: "INV-2025-003", amount: 8500, currency: "EUR", date: new Date(), status: "matched" },
  ]

  const pending = [
    { payment: "PAY-004", invoice: "INV-2025-004", amount: 1200, currency: "USD", date: new Date(), issue: "Amount mismatch" },
    { payment: "PAY-005", invoice: null, amount: 500, currency: "USD", date: new Date(), issue: "No invoice found" },
  ]

  const fxDeltas = [
    { transaction: "PAY-001", original: 5000, fxImpact: 15.50, accounting: 5015.50, currency: "USD" },
    { transaction: "PAY-003", original: 8500, fxImpact: -23.40, accounting: 8476.60, currency: "EUR" },
  ]

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-4xl font-bold tracking-tight text-foreground">Reconciliation & Accounting Automation</h1>
        <p className="text-muted-foreground">
          Automatic matching and accounting automation
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Matched</CardTitle>
            <CardDescription>Payments → Invoices</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold tracking-tight text-foreground text-green-600">1,247</div>
            <div className="text-sm text-muted-foreground mt-1">This month</div>
            <div className="text-xs text-green-600 mt-2">98.5% match rate</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Pending</CardTitle>
            <CardDescription>Requires review</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold tracking-tight text-foreground">12</div>
            <div className="text-sm text-muted-foreground mt-1">Items</div>
            <div className="text-xs text-yellow-600 mt-2">Needs attention</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>FX Delta</CardTitle>
            <CardDescription>Accounting impact</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold tracking-tight text-foreground">$234</div>
            <div className="text-sm text-muted-foreground mt-1">This month</div>
            <div className="text-xs text-muted-foreground mt-2">Tracked automatically</div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Automatic Matching</CardTitle>
          <CardDescription>Payments → Invoices → Confirmations</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <h3 className="font-medium mb-2">Matched Transactions</h3>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Payment</TableHead>
                    <TableHead>Invoice</TableHead>
                    <TableHead>Amount</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {matched.map((item) => (
                    <TableRow key={item.payment}>
                      <TableCell className="font-medium">{item.payment}</TableCell>
                      <TableCell>{item.invoice}</TableCell>
                      <TableCell>{formatCurrency(item.amount, item.currency)}</TableCell>
                      <TableCell>{formatDate(item.date)}</TableCell>
                      <TableCell>
                        <span className="flex items-center gap-1 text-green-600">
                          <CheckCircle2 className="h-4 w-4" />
                          Matched
                        </span>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
            <div>
              <h3 className="font-medium mb-2">Pending Review</h3>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Payment</TableHead>
                    <TableHead>Invoice</TableHead>
                    <TableHead>Amount</TableHead>
                    <TableHead>Issue</TableHead>
                    <TableHead>Action</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {pending.map((item) => (
                    <TableRow key={item.payment}>
                      <TableCell className="font-medium">{item.payment}</TableCell>
                      <TableCell>{item.invoice || "N/A"}</TableCell>
                      <TableCell>{formatCurrency(item.amount, item.currency)}</TableCell>
                      <TableCell>
                        <span className="text-yellow-600">{item.issue}</span>
                      </TableCell>
                      <TableCell>
                        <Button variant="outline" size="sm">Review</Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <DollarSign className="h-5 w-5" />
            FX Delta Tracking for Accounting
          </CardTitle>
          <CardDescription>Track FX impact on accounting records</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Transaction</TableHead>
                <TableHead>Original Amount</TableHead>
                <TableHead>FX Impact</TableHead>
                <TableHead>Accounting Amount</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {fxDeltas.map((item) => (
                <TableRow key={item.transaction}>
                  <TableCell className="font-medium">{item.transaction}</TableCell>
                  <TableCell>{formatCurrency(item.original, item.currency)}</TableCell>
                  <TableCell className={item.fxImpact > 0 ? "text-green-600" : "text-red-600"}>
                    {item.fxImpact > 0 ? "+" : ""}{formatCurrency(item.fxImpact, item.currency)}
                  </TableCell>
                  <TableCell className="font-medium">{formatCurrency(item.accounting, item.currency)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Multi-Rail Ledger</CardTitle>
          <CardDescription>Normalized cost and FX impact tracking</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="p-4 border rounded-lg">
              <div className="font-medium mb-2">Ledger Summary</div>
              <div className="grid gap-4 md:grid-cols-4">
                <div>
                  <div className="text-sm text-muted-foreground">Total Transactions</div>
                  <div className="text-xl font-bold">1,247</div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Total Volume</div>
                  <div className="text-xl font-bold">$12.5M</div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">FX Impact</div>
                  <div className="text-xl font-bold">$234</div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Cost Savings</div>
                  <div className="text-xl font-bold text-green-600">$36,117</div>
                </div>
              </div>
            </div>
            <Button variant="outline" className="w-full">
              <FileText className="mr-2 h-4 w-4" />
              View Full Ledger
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Export to Accounting Systems</CardTitle>
          <CardDescription>Multi-rail ledger with normalized cost and FX impact</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <Button variant="outline" className="w-full">
              <Download className="mr-2 h-4 w-4" />
              QuickBooks
            </Button>
            <Button variant="outline" className="w-full">
              <Download className="mr-2 h-4 w-4" />
              Xero
            </Button>
            <Button variant="outline" className="w-full">
              <Download className="mr-2 h-4 w-4" />
              NetSuite
            </Button>
          </div>
          <div className="mt-4 p-3 bg-blue-50 rounded-lg">
            <div className="text-sm text-blue-900">
              Exports include: normalized costs, FX deltas, multi-rail breakdown, and audit trail
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
