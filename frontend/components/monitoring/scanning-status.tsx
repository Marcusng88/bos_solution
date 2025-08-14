"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { CheckCircle, Clock, AlertCircle, Loader2 } from "lucide-react"

const competitors = [
  { name: "Nike", status: "scanning", progress: 75, lastScan: "2 minutes ago", changes: 3 },
  { name: "Adidas", status: "complete", progress: 100, lastScan: "5 minutes ago", changes: 1 },
  { name: "Puma", status: "complete", progress: 100, lastScan: "8 minutes ago", changes: 5 },
  { name: "Under Armour", status: "pending", progress: 0, lastScan: "15 minutes ago", changes: 0 },
  { name: "New Balance", status: "error", progress: 45, lastScan: "12 minutes ago", changes: 0 },
  { name: "Reebok", status: "complete", progress: 100, lastScan: "10 minutes ago", changes: 2 },
]

const scanTypes = [
  { name: "Social Media Posts", status: "active", progress: 85 },
  { name: "Website Changes", status: "active", progress: 92 },
  { name: "Pricing Updates", status: "active", progress: 78 },
  { name: "Ad Campaigns", status: "active", progress: 65 },
  { name: "Content Analysis", status: "queued", progress: 0 },
]

export function ScanningStatus() {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case "scanning":
        return <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
      case "complete":
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case "pending":
        return <Clock className="h-4 w-4 text-orange-500" />
      case "error":
        return <AlertCircle className="h-4 w-4 text-red-500" />
      default:
        return <Clock className="h-4 w-4 text-gray-400" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "scanning":
        return "bg-blue-100 text-blue-800"
      case "complete":
        return "bg-green-100 text-green-800"
      case "pending":
        return "bg-orange-100 text-orange-800"
      case "error":
        return "bg-red-100 text-red-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Competitor Scanning Status */}
      <Card>
        <CardHeader>
          <CardTitle>Competitor Scanning</CardTitle>
          <CardDescription>Real-time monitoring status for each competitor</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {competitors.map((competitor) => (
            <div key={competitor.name} className="flex items-center justify-between p-3 border rounded-lg">
              <div className="flex items-center gap-3">
                {getStatusIcon(competitor.status)}
                <div>
                  <p className="font-medium">{competitor.name}</p>
                  <p className="text-sm text-muted-foreground">Last scan: {competitor.lastScan}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="text-right">
                  <Badge className={getStatusColor(competitor.status)}>{competitor.status}</Badge>
                  {competitor.changes > 0 && (
                    <p className="text-xs text-muted-foreground mt-1">{competitor.changes} changes</p>
                  )}
                </div>
                <div className="w-20">
                  <Progress value={competitor.progress} className="h-2" />
                </div>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Scan Types Status */}
      <Card>
        <CardHeader>
          <CardTitle>Scanning Categories</CardTitle>
          <CardDescription>Progress across different monitoring types</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {scanTypes.map((scanType) => (
            <div key={scanType.name} className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="font-medium">{scanType.name}</span>
                  <Badge className={getStatusColor(scanType.status)}>{scanType.status}</Badge>
                </div>
                <span className="text-sm text-muted-foreground">{scanType.progress}%</span>
              </div>
              <Progress value={scanType.progress} className="h-2" />
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}
