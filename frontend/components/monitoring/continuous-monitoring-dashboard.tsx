"use client"

import { useState, useEffect, useCallback } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Bell, Eye, TrendingUp, Clock, Play, Pause, Loader2 } from "lucide-react"
import { MonitoringAlerts } from "./monitoring-alerts"
import { ScanningStatus } from "./scanning-status"
import { AnalysisResults } from "./analysis-results"
import { useApiClient, handleApiError, monitoringAPI } from "@/lib/api-client"
import { useToast } from "@/hooks/use-toast"

interface MonitoringStats {
  total_competitors: number
  unread_alerts: number
  recent_activity_24h: number
  last_scan_time?: string
}

interface MonitoringStatus {
  running: boolean
  total_active_jobs: number
  next_scheduled_run?: string
}

interface MonitoringData {
  id: string
  competitor_id: string
  platform: string
  post_id?: string
  post_url?: string
  content_text: string
  author_username?: string
  post_type: string
  engagement_metrics?: any
  detected_at: string
  posted_at?: string
  // New fields for website and web analysis
  source_url?: string;
  key_insights?: string[];
  alert_type?: string;
}

export function ContinuousMonitoringDashboard() {
  const [isMonitoring, setIsMonitoring] = useState(false)
  const [monitoringStats, setMonitoringStats] = useState<MonitoringStats | null>(null)
  const [monitoringStatus, setMonitoringStatus] = useState<MonitoringStatus | null>(null)
  const [monitoringData, setMonitoringData] = useState<MonitoringData[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isTogglingMonitoring, setIsTogglingMonitoring] = useState(false)
  const { apiClient, userId } = useApiClient()
  const { toast } = useToast()

  const fetchAllData = useCallback(async () => {
    if (!userId) return;
    setIsLoading(true);
    try {
      const [statusRes, statsRes, dataRes] = await Promise.all([
        apiClient.getMonitoringStatus(userId),
        apiClient.getMonitoringStats(userId),
        monitoringAPI.getMonitoringData(userId, { limit: 50 }),
      ]);

      if ((statusRes as any).success) {
        setMonitoringStatus((statusRes as any).status);
        setIsMonitoring((statusRes as any).status.running);
      }
      if ((statsRes as any).success) {
        setMonitoringStats((statsRes as any).stats);
      }
      if (dataRes.data) {
        setMonitoringData(dataRes.data);
      }
    } catch (error) {
      console.error('Error fetching monitoring data:', error);
      toast({
        title: "Error",
        description: handleApiError(error),
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  }, [userId, apiClient, toast]);

  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);


  // Handle monitoring toggle
  const handleMonitoringToggle = async (enabled: boolean) => {
    try {
      setIsTogglingMonitoring(true)
      
      let response
      if (enabled) {
        response = await apiClient.startContinuousMonitoring(userId)
      } else {
        response = await apiClient.stopContinuousMonitoring(userId)
      }

      if ((response as any).success) {
        setIsMonitoring(enabled)
        toast({
          title: "Success",
          description: (response as any).message,
        })
        
        // Refresh monitoring status
        const statusResponse = await apiClient.getMonitoringStatus(userId)
        if ((statusResponse as any).success) {
          setMonitoringStatus((statusResponse as any).status)
        }
      } else {
        toast({
          title: "Error",
          description: "Failed to toggle monitoring",
          variant: "destructive",
        })
      }
    } catch (error) {
      console.error('Error toggling monitoring:', error)
      toast({
        title: "Error",
        description: handleApiError(error),
        variant: "destructive",
      })
    } finally {
      setIsTogglingMonitoring(false)
    }
  }

  // Helper function to get last scan time
  const getLastScanTime = () => {
    if (monitoringStats?.last_scan_time) {
      const lastScan = new Date(monitoringStats.last_scan_time)
      const now = new Date()
      const diffMs = now.getTime() - lastScan.getTime()
      const diffMins = Math.floor(diffMs / 60000)
      
      if (diffMins < 1) return "Just now"
      if (diffMins < 60) return `${diffMins}m`
      const diffHours = Math.floor(diffMins / 60)
      return `${diffHours}h`
    }
    return "Never"
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Continuous Monitoring</h1>
          <p className="text-muted-foreground">Daily competitor surveillance and alerts</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium">Monitoring</span>
            <Switch 
              checked={isMonitoring} 
              onCheckedChange={handleMonitoringToggle}
              disabled={isTogglingMonitoring}
            />
            {isTogglingMonitoring ? (
              <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
            ) : isMonitoring ? (
              <Play className="h-4 w-4 text-green-500" />
            ) : (
              <Pause className="h-4 w-4 text-gray-400" />
            )}
          </div>
          <Button variant="outline" size="sm" onClick={() => window.location.reload()}>
            Scan Now
          </Button>
        </div>
      </div>

      {/* Status Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Eye className="h-5 w-5 text-blue-500" />
              <div>
                <p className="text-sm font-medium">Competitors Monitored</p>
                <p className="text-2xl font-bold">
                  {monitoringStats?.total_competitors ?? 0}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Bell className="h-5 w-5 text-orange-500" />
              <div>
                <p className="text-sm font-medium">Unread Alerts</p>
                <p className="text-2xl font-bold">
                  {monitoringStats?.unread_alerts ?? 0}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-green-500" />
              <div>
                <p className="text-sm font-medium">Activity (24h)</p>
                <p className="text-2xl font-bold">
                  {monitoringStats?.recent_activity_24h ?? 0}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-purple-500" />
              <div>
                <p className="text-sm font-medium">Last Scan</p>
                <p className="text-2xl font-bold">
                  {getLastScanTime()}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <Tabs defaultValue="analysis-results" className="space-y-4">
        <TabsList>
          <TabsTrigger value="analysis-results">Analysis Results</TabsTrigger>
          <TabsTrigger value="alerts">Recent Alerts</TabsTrigger>
          <TabsTrigger value="scanning">Scanning Status</TabsTrigger>
        </TabsList>

        <TabsContent value="analysis-results">
          <AnalysisResults results={monitoringData} />
        </TabsContent>

        <TabsContent value="alerts">
          <MonitoringAlerts userId={userId} />
        </TabsContent>

        <TabsContent value="scanning">
          <ScanningStatus userId={userId} />
        </TabsContent>
      </Tabs>
    </div>
  )
}
