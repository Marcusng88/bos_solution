"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { CheckCircle, Clock, AlertCircle, Loader2, RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { apiClient, handleApiError } from "@/lib/api-client"
import { useToast } from "@/hooks/use-toast"

interface Competitor {
  id: string
  name: string
  status: string
  website_url?: string
  social_media_handles?: any
  scan_frequency_minutes?: number
  last_scan?: string
  monitoring_status?: {
    last_successful_scan?: string
    last_failed_scan?: string
    is_scanning: boolean
    consecutive_failures: number
    scan_error_message?: string
  }
}

interface ScanningStatusProps {
  userId: string
}

// Mock scan types data since we don't have specific endpoints for these yet
const scanTypes = [
  { name: "Social Media Posts", status: "active", progress: 85 },
  { name: "Website Changes", status: "active", progress: 92 },
  { name: "Pricing Updates", status: "active", progress: 78 },
  { name: "Ad Campaigns", status: "active", progress: 65 },
  { name: "Content Analysis", status: "queued", progress: 0 },
]

export function ScanningStatus({ userId }: ScanningStatusProps) {
  const [competitors, setCompetitors] = useState<Competitor[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [runningScans, setRunningScans] = useState<Set<string>>(new Set())
  const { toast } = useToast()

  // Fetch competitors on component mount
  useEffect(() => {
    const fetchCompetitors = async () => {
      try {
        setIsLoading(true)
        const response = await apiClient.getCompetitors(userId)
        
        if (Array.isArray(response)) {
          setCompetitors(response)
        }
      } catch (error) {
        console.error('Error fetching competitors:', error)
        toast({
          title: "Error",
          description: handleApiError(error),
          variant: "destructive",
        })
      } finally {
        setIsLoading(false)
      }
    }

    fetchCompetitors()
  }, [userId]) // Remove toast from dependencies

  // Run monitoring for a specific competitor
  const runScanForCompetitor = async (competitorId: string) => {
    try {
      setRunningScans(prev => new Set([...prev, competitorId]))
      
      const response = await apiClient.runMonitoringForCompetitor(userId, competitorId)
      
      if ((response as any).success) {
        toast({
          title: "Success",
          description: `Monitoring started for ${(response as any).competitor_name}`,
        })
        
        // Refresh competitors data after a short delay
        setTimeout(() => {
          apiClient.getCompetitors(userId).then(response => {
            if (Array.isArray(response)) {
              setCompetitors(response)
            }
          })
        }, 2000)
      }
    } catch (error) {
      console.error('Error running scan:', error)
      toast({
        title: "Error",
        description: handleApiError(error),
        variant: "destructive",
      })
    } finally {
      setRunningScans(prev => {
        const newSet = new Set(prev)
        newSet.delete(competitorId)
        return newSet
      })
    }
  }

  // Get competitor status based on monitoring status
  const getCompetitorStatus = (competitor: Competitor) => {
    if (runningScans.has(competitor.id) || competitor.monitoring_status?.is_scanning) {
      return "scanning"
    }
    if (competitor.monitoring_status?.consecutive_failures && competitor.monitoring_status.consecutive_failures > 0) {
      return "error"
    }
    if (competitor.monitoring_status?.last_successful_scan) {
      return "complete"
    }
    return "pending"
  }

  // Get last scan time
  const getLastScanTime = (competitor: Competitor) => {
    const lastScan = competitor.monitoring_status?.last_successful_scan || competitor.last_scan
    if (!lastScan) return "Never"
    
    const date = new Date(lastScan)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    
    if (diffMins < 1) return "Just now"
    if (diffMins < 60) return `${diffMins}m ago`
    const diffHours = Math.floor(diffMins / 60)
    if (diffHours < 24) return `${diffHours}h ago`
    const diffDays = Math.floor(diffHours / 24)
    return `${diffDays}d ago`
  }

  // Calculate progress (mock implementation)
  const getProgress = (competitor: Competitor) => {
    const status = getCompetitorStatus(competitor)
    switch (status) {
      case "scanning":
        return Math.floor(Math.random() * 30) + 50 // 50-80% for scanning
      case "complete":
        return 100
      case "error":
        return Math.floor(Math.random() * 50) + 10 // 10-60% for error
      default:
        return 0
    }
  }

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

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-32">
        <Loader2 className="h-6 w-6 animate-spin" />
      </div>
    )
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
          {competitors.length === 0 ? (
            <div className="text-center py-8">
              <AlertCircle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium mb-2">No competitors added</h3>
              <p className="text-muted-foreground">Add competitors to start monitoring their activities.</p>
            </div>
          ) : (
            competitors.map((competitor) => {
              const status = getCompetitorStatus(competitor)
              const progress = getProgress(competitor)
              
              return (
                <div key={competitor.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center gap-3">
                    {getStatusIcon(status)}
                    <div>
                      <p className="font-medium">{competitor.name}</p>
                      <p className="text-sm text-muted-foreground">
                        Last scan: {getLastScanTime(competitor)}
                      </p>
                      {competitor.monitoring_status?.scan_error_message && (
                        <p className="text-xs text-red-500 mt-1">
                          {competitor.monitoring_status.scan_error_message}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="text-right">
                      <Badge className={getStatusColor(status)}>{status}</Badge>
                      <Button
                        size="sm"
                        variant="outline"
                        className="mt-2"
                        onClick={() => runScanForCompetitor(competitor.id)}
                        disabled={runningScans.has(competitor.id) || status === "scanning"}
                      >
                        {runningScans.has(competitor.id) ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <>
                            <RefreshCw className="h-4 w-4 mr-1" />
                            Scan Now
                          </>
                        )}
                      </Button>
                    </div>
                    <div className="w-20">
                      <Progress value={progress} className="h-2" />
                    </div>
                  </div>
                </div>
              )
            })
          )}
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
