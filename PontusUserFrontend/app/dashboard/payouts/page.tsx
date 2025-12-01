"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Globe, Upload, FileText, Users, Zap, CheckCircle2, AlertCircle } from "lucide-react"
import { formatCurrency, formatDate } from "@/lib/utils"

export default function PayoutsPage() {
  const [batchMode, setBatchMode] = useState(false)
  const [invoiceFile, setInvoiceFile] = useState<File | null>(null)

  const recentPayouts = [
    { id: 1, recipient: "Vendor A", amount: 5000, currency: "USD", route: "USD → EUR", status: "completed", date: new Date() },
    { id: 2, recipient: "Contractor B", amount: 3200, currency: "USD", route: "USD → INR", status: "processing", date: new Date() },
    { id: 3, recipient: "Supplier C", amount: 8500, currency: "EUR", route: "EUR → GBP", status: "completed", date: new Date() },
  ]

  const handleInvoiceUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setInvoiceFile(e.target.files[0])
      // Simulate AI processing
      setTimeout(() => {
        alert("Invoice processed! AI has validated and matched to optimal route.")
      }, 1000)
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-4xl font-bold tracking-tight text-foreground">Global Payout OS</h1>
        <p className="text-muted-foreground">
          One-click vendor, contractor, supplier, and international payroll payments
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Quick Payout</CardTitle>
            <CardDescription>Single payment</CardDescription>
          </CardHeader>
          <CardContent>
            <Button className="w-full" onClick={() => setBatchMode(false)}>
              <Zap className="mr-2 h-4 w-4" />
              Create Payout
            </Button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Batch Payout</CardTitle>
            <CardDescription>Upload CSV for multiple payments</CardDescription>
          </CardHeader>
          <CardContent>
            <Button className="w-full" variant="outline" onClick={() => setBatchMode(true)}>
              <Upload className="mr-2 h-4 w-4" />
              Upload CSV
            </Button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Invoice Processing</CardTitle>
            <CardDescription>AI-powered invoice validation</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <Input
                type="file"
                accept=".pdf,.jpg,.png"
                onChange={handleInvoiceUpload}
                className="hidden"
                id="invoice-upload"
              />
              <Button className="w-full" variant="outline" asChild>
                <label htmlFor="invoice-upload" className="cursor-pointer">
                  <FileText className="mr-2 h-4 w-4" />
                  Upload Invoice
                </label>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {batchMode && (
        <Card>
          <CardHeader>
            <CardTitle>Batch Payout Configuration</CardTitle>
            <CardDescription>Configure batch payment parameters</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="p-4 border rounded-lg bg-green-50">
              <div className="font-medium text-green-900">Smart Batching Active</div>
              <div className="text-sm text-green-700 mt-1">
                Intelligent batching across recipients will reduce costs by ~$45
              </div>
            </div>
            <div className="space-y-2">
              <Input type="file" accept=".csv" />
              <Button className="w-full">
                <Upload className="mr-2 h-4 w-4" />
                Process Batch
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Recent Payouts</CardTitle>
          <CardDescription>Latest payment executions</CardDescription>
        </CardHeader>
        <CardContent>
          {recentPayouts.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Recipient</TableHead>
                  <TableHead>Amount</TableHead>
                  <TableHead>Route</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Date</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {recentPayouts.map((payout) => (
                  <TableRow key={payout.id}>
                    <TableCell className="font-medium">{payout.recipient}</TableCell>
                    <TableCell>{formatCurrency(payout.amount, payout.currency)}</TableCell>
                    <TableCell>{payout.route}</TableCell>
                    <TableCell>
                      {payout.status === "completed" ? (
                        <span className="flex items-center gap-1 text-green-600">
                          <CheckCircle2 className="h-4 w-4" />
                          Completed
                        </span>
                      ) : (
                        <span className="flex items-center gap-1 text-yellow-600">
                          <AlertCircle className="h-4 w-4" />
                          Processing
                        </span>
                      )}
                    </TableCell>
                    <TableCell>{formatDate(payout.date)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              No payouts yet. Create your first payout to get started.
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Smart Batching</CardTitle>
          <CardDescription>Intelligent batching across recipients to reduce costs</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="flex items-center justify-between p-3 border rounded-lg">
              <div>
                <div className="font-medium">Pending batch: 12 recipients</div>
                <div className="text-sm text-muted-foreground">Ready for optimization</div>
              </div>
              <div className="text-right">
                <div className="font-bold text-green-600">Estimated savings: $45</div>
                <div className="text-xs text-muted-foreground">vs individual payments</div>
              </div>
            </div>
            <Button className="w-full">
              <Zap className="mr-2 h-4 w-4" />
              Execute Batch
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
