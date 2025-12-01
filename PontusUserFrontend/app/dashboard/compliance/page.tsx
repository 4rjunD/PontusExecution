"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Shield, CheckCircle2, AlertTriangle, FileText, Users, Settings } from "lucide-react"
import { formatDate } from "@/lib/utils"

export default function CompliancePage() {
  const validations = [
    { id: 1, invoice: "INV-2025-001", vendor: "Vendor A", amount: 5000, status: "approved", validated: new Date(), aiConfidence: 98 },
    { id: 2, invoice: "INV-2025-002", vendor: "Vendor B", amount: 3200, status: "approved", validated: new Date(), aiConfidence: 95 },
    { id: 3, invoice: "INV-2025-003", vendor: "Vendor C", amount: 8500, status: "pending", validated: null, aiConfidence: 87 },
  ]

  const rules = [
    { id: 1, name: "USD → EUR Corridor", type: "corridor", status: "active", matches: 24 },
    { id: 2, name: "Max Amount: $50,000", type: "amount", status: "active", matches: 3 },
    { id: 3, name: "Require Invoice for >$10k", type: "invoice", status: "active", matches: 12 },
    { id: 4, name: "Block High-Risk Countries", type: "country", status: "active", matches: 0 },
  ]

  const auditLogs = [
    { timestamp: new Date(), user: "Finance Team", action: "Invoice Validated", details: "INV-2025-001", result: "Approved" },
    { timestamp: new Date(), user: "System", action: "Rule Enforced", details: "USD → EUR Corridor", result: "Passed" },
    { timestamp: new Date(), user: "Finance Team", action: "Payment Executed", details: "$5,000 to Vendor A", result: "Completed" },
  ]

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-4xl font-bold tracking-tight text-foreground">Compliance & Controls</h1>
        <p className="text-muted-foreground">
          Automatic validation, rule enforcement, and audit logs
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Invoice Validation</CardTitle>
            <CardDescription>AI-powered validation status</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold tracking-tight text-foreground text-green-600">98.5%</div>
            <div className="text-sm text-muted-foreground mt-1">Success rate</div>
            <div className="text-xs text-muted-foreground mt-2">1,247 validated this month</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Rule Enforcement</CardTitle>
            <CardDescription>Corridor-based rules active</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold tracking-tight text-foreground">24</div>
            <div className="text-sm text-muted-foreground mt-1">Active rules</div>
            <div className="text-xs text-muted-foreground mt-2">39 matches this month</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Suspicious Patterns</CardTitle>
            <CardDescription>AML detection alerts</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold tracking-tight text-foreground text-green-600">0</div>
            <div className="text-sm text-muted-foreground mt-1">No alerts</div>
            <div className="text-xs text-muted-foreground mt-2">All clear</div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Automatic Invoice Validation
          </CardTitle>
          <CardDescription>AI reads, validates, and matches invoices to optimal routes</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Invoice</TableHead>
                <TableHead>Vendor</TableHead>
                <TableHead>Amount</TableHead>
                <TableHead>AI Confidence</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Validated</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {validations.map((val) => (
                <TableRow key={val.id}>
                  <TableCell className="font-medium">{val.invoice}</TableCell>
                  <TableCell>{val.vendor}</TableCell>
                  <TableCell>${val.amount.toLocaleString()}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <span>{val.aiConfidence}%</span>
                      {val.aiConfidence >= 95 && (
                        <CheckCircle2 className="h-4 w-4 text-green-600" />
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    {val.status === "approved" ? (
                      <span className="px-2 py-1 rounded text-xs bg-green-100 text-green-800">
                        Approved
                      </span>
                    ) : (
                      <span className="px-2 py-1 rounded text-xs bg-yellow-100 text-yellow-800">
                        Pending
                      </span>
                    )}
                  </TableCell>
                  <TableCell>{val.validated ? formatDate(val.validated) : "Pending"}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Corridor-Based Rule Enforcement
          </CardTitle>
          <CardDescription>JSON constraint file rules and enforcement</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {rules.map((rule) => (
              <div key={rule.id} className="flex items-center justify-between p-3 border rounded-lg">
                <div>
                  <div className="font-medium">{rule.name}</div>
                  <div className="text-sm text-muted-foreground capitalize">{rule.type} rule</div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium">{rule.matches} matches</div>
                  <span className="px-2 py-1 rounded text-xs bg-green-100 text-green-800">
                    {rule.status}
                  </span>
                </div>
              </div>
            ))}
            <Button variant="outline" className="w-full">
              <Settings className="mr-2 h-4 w-4" />
              Manage Rules
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Role-Based Access Control (RBAC)
          </CardTitle>
          <CardDescription>Finance team permissions and access</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 border rounded-lg">
              <div>
                <div className="font-medium">Finance Manager</div>
                <div className="text-sm text-muted-foreground">Full access</div>
              </div>
              <span className="px-2 py-1 rounded text-xs bg-blue-100 text-blue-800">Admin</span>
            </div>
            <div className="flex items-center justify-between p-3 border rounded-lg">
              <div>
                <div className="font-medium">Finance Analyst</div>
                <div className="text-sm text-muted-foreground">View and execute</div>
              </div>
              <span className="px-2 py-1 rounded text-xs bg-green-100 text-green-800">User</span>
            </div>
            <div className="flex items-center justify-between p-3 border rounded-lg">
              <div>
                <div className="font-medium">Viewer</div>
                <div className="text-sm text-muted-foreground">Read-only</div>
              </div>
              <span className="px-2 py-1 rounded text-xs bg-gray-100 text-gray-800">Viewer</span>
            </div>
            <Button variant="outline" className="w-full">
              <Users className="mr-2 h-4 w-4" />
              Manage Roles
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Full Action-Level Audit Logs</CardTitle>
          <CardDescription>Complete audit trail of all actions</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Timestamp</TableHead>
                <TableHead>User</TableHead>
                <TableHead>Action</TableHead>
                <TableHead>Details</TableHead>
                <TableHead>Result</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {auditLogs.map((log, idx) => (
                <TableRow key={idx}>
                  <TableCell>{formatDate(log.timestamp)}</TableCell>
                  <TableCell>{log.user}</TableCell>
                  <TableCell className="font-medium">{log.action}</TableCell>
                  <TableCell>{log.details}</TableCell>
                  <TableCell>
                    <span className="px-2 py-1 rounded text-xs bg-green-100 text-green-800">
                      {log.result}
                    </span>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          <Button variant="outline" className="w-full mt-4">
            <FileText className="mr-2 h-4 w-4" />
            Export Audit Logs
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
