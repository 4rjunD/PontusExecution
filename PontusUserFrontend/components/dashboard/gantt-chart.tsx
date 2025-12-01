"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Calendar, Clock, CheckCircle2 } from "lucide-react"

export function GanttChart() {
  const tasks = [
    {
      id: 1,
      name: "Route Optimization",
      start: "2025-11-22",
      end: "2025-11-23",
      progress: 75,
      status: "in-progress",
    },
    {
      id: 2,
      name: "Payment Execution",
      start: "2025-11-23",
      end: "2025-11-24",
      progress: 0,
      status: "pending",
    },
    {
      id: 3,
      name: "Reconciliation",
      start: "2025-11-24",
      end: "2025-11-25",
      progress: 0,
      status: "pending",
    },
    {
      id: 4,
      name: "Invoice Processing",
      start: "2025-11-22",
      end: "2025-11-22",
      progress: 100,
      status: "completed",
    },
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-green-500"
      case "in-progress":
        return "bg-blue-500"
      default:
        return "bg-gray-300"
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Calendar className="h-5 w-5" />
          Task Management & Calendar
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {tasks.map((task) => (
            <div key={task.id} className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {task.status === "completed" ? (
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                  ) : (
                    <Clock className="h-4 w-4 text-blue-600" />
                  )}
                  <span className="font-medium">{task.name}</span>
                </div>
                <span className="text-sm text-muted-foreground">
                  {task.start} - {task.end}
                </span>
              </div>
              <div className="relative h-6 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className={`absolute h-full ${getStatusColor(task.status)} transition-all`}
                  style={{ width: `${task.progress}%` }}
                />
                <div className="absolute inset-0 flex items-center justify-center text-xs font-medium">
                  {task.progress}%
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

