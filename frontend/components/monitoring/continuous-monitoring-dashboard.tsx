"use client"

import { useState, useEffect, useCallback, useMemo } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Bell, Eye, TrendingUp, Clock, Play, Pause, Loader2, Search, RefreshCw } from "lucide-react"
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
  author_display_name?: string
  author_avatar_url?: string
  post_type: string
  engagement_metrics?: any
  media_urls?: any
  content_hash?: string
  language?: string
  sentiment_score?: number
  detected_at: string
  posted_at?: string
  is_new_post?: boolean
  is_content_change?: boolean
  previous_content_hash?: string
}

export function ContinuousMonitoringDashboard() {
  const [isMonitoring, setIsMonitoring] = useState(false)
  const [monitoringStats, setMonitoringStats] = useState<MonitoringStats | null>(null)
  const [monitoringStatus, setMonitoringStatus] = useState<MonitoringStatus | null>(null)
  const [monitoringData, setMonitoringData] = useState<MonitoringData[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isTogglingMonitoring, setIsTogglingMonitoring] = useState(false)
  const [isScanning, setIsScanning] = useState(false)
  const { apiClient, userId } = useApiClient()
  const { toast } = useToast()

  // Memoize the fetchAllData function to prevent infinite loops
  const fetchAllData = useCallback(async () => {
    if (!userId) {
      console.log('❌ No userId, skipping fetch');
      return;
    }
    console.log('🚀 Starting fetchAllData for user:', userId);
    console.log('🌐 API Base URL:', process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1');
    setIsLoading(true);
    try {
      console.log('📡 Making API calls...');
      
      // Test network connectivity first
      try {
        const testResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/health`);
        console.log('🌐 Network test response:', testResponse.status, testResponse.statusText);
      } catch (networkError) {
        console.error('❌ Network test failed:', networkError);
      }
      
      console.log('🔗 API Client base URL:', process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1');
      console.log('🔗 Monitoring API base URL:', process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1');
      
      const [statusRes, statsRes, dataRes] = await Promise.all([
        apiClient.getMonitoringStatus(userId),
        apiClient.getMonitoringStats(userId),
        monitoringAPI.getMonitoringData(userId, { limit: 50 }),
      ]);

      console.log('✅ API responses received:', { 
        statusRes: JSON.stringify(statusRes, null, 2), 
        statsRes: JSON.stringify(statsRes, null, 2), 
        dataRes: JSON.stringify(dataRes, null, 2) 
      });

      if ((statusRes as any).success) {
        console.log('✅ Status response successful, setting monitoring status');
        setMonitoringStatus((statusRes as any).status);
        setIsMonitoring((statusRes as any).status.running);
      } else {
        console.log('❌ Status response not successful:', statusRes);
      }
      
      if ((statsRes as any).success) {
        console.log('✅ Stats response successful, setting monitoring stats');
        setMonitoringStats((statsRes as any).stats);
      } else {
        console.log('❌ Stats response not successful:', statsRes);
      }
      
      if (dataRes.data) {
        console.log('✅ Data response successful, setting monitoring data');
        setMonitoringData(dataRes.data);
      } else {
        console.log('❌ Data response not successful or no data:', dataRes);
      }
    } catch (error) {
      console.error('❌ Error fetching monitoring data:', error);
      toast({
        title: "Error",
        description: handleApiError(error),
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
      console.log('🏁 fetchAllData completed');
    }
  }, [userId, toast]); // Remove apiClient from dependencies

  // Memoize the API client methods to prevent recreation
  const memoizedApiClient = useMemo(() => ({
    getMonitoringStatus: (userId: string) => apiClient.getMonitoringStatus(userId),
    startContinuousMonitoring: (userId: string) => apiClient.startContinuousMonitoring(userId),
    stopContinuousMonitoring: (userId: string) => apiClient.stopContinuousMonitoring(userId),
    runMonitoringForAllCompetitors: (userId: string) => apiClient.runMonitoringForAllCompetitors(userId),
  }), [apiClient]);

  useEffect(() => {
    if (userId) {
      console.log('🔄 Fetching monitoring data for user:', userId);
      fetchAllData();
    }
    
    // Cleanup function to prevent memory leaks
    return () => {
      console.log('🧹 Cleaning up monitoring dashboard');
    };
  }, [userId]); // Only depend on userId, not fetchAllData


  // Handle monitoring toggle
  const handleMonitoringToggle = async (enabled: boolean) => {
    try {
      setIsTogglingMonitoring(true)
      
      let response
      if (enabled) {
        response = await memoizedApiClient.startContinuousMonitoring(userId)
      } else {
        response = await memoizedApiClient.stopContinuousMonitoring(userId)
      }

      if ((response as any).success) {
        setIsMonitoring(enabled)
        toast({
          title: "Success",
          description: (response as any).message,
        })
        
        // Refresh monitoring status
        const statusResponse = await memoizedApiClient.getMonitoringStatus(userId)
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

  // Handle scan now button click
  const handleScanNow = async () => {
    if (!userId) {
      toast({
        title: "Error",
        description: "User not authenticated",
        variant: "destructive",
      });
      return;
    }

    try {
      setIsScanning(true);
      toast({
        title: "Scanning Started",
        description: "Initiating comprehensive competitor scan across all platforms...",
      });

      // Start the scan for all competitors
      const response = await memoizedApiClient.runMonitoringForAllCompetitors(userId);
      
      if ((response as any).success) {
        toast({
          title: "Scan Initiated",
          description: "Competitor monitoring scan has been started. This may take several minutes to complete.",
        });

        // Wait a bit then refresh the data to show progress
        setTimeout(() => {
          fetchAllData();
        }, 2000);

        // Continue refreshing every 10 seconds to show progress
        const refreshInterval = setInterval(() => {
          fetchAllData();
        }, 10000);

        // Stop refreshing after 2 minutes
        setTimeout(() => {
          clearInterval(refreshInterval);
          fetchAllData(); // Final refresh
        }, 120000);

      } else {
        toast({
          title: "Scan Failed",
          description: "Failed to initiate competitor scan. Please try again.",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error starting scan:', error);
      toast({
        title: "Scan Error",
        description: handleApiError(error),
        variant: "destructive",
      });
    } finally {
      setIsScanning(false);
    }
  };

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
          <Button 
            variant="outline" 
            size="sm" 
            onClick={handleScanNow}
            disabled={isScanning}
            className="min-w-[100px]"
          >
            {isScanning ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                Scanning...
              </>
            ) : (
              <>
                <Search className="h-4 w-4 mr-2" />
                Scan Now
              </>
            )}
          </Button>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={fetchAllData}
            disabled={isLoading}
            className="min-w-[100px]"
          >
            {isLoading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                Loading...
              </>
            ) : (
              <>
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </>
            )}
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

      {/* Debug Info */}
      <Card className="bg-gray-50">
        <CardContent className="p-4">
          <h3 className="font-semibold mb-2 text-sm">Debug Info</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
            <div><strong>User ID:</strong> {userId}</div>
            <div><strong>Loading:</strong> {isLoading ? 'Yes' : 'No'}</div>
            <div><strong>Data Count:</strong> {monitoringData.length}</div>
            <div><strong>Monitoring:</strong> {isMonitoring ? 'On' : 'Off'}</div>
          </div>
        </CardContent>
      </Card>

      {/* Main Content */}
      <Tabs defaultValue="analysis-results" className="space-y-4">
        <TabsList>
          <TabsTrigger value="analysis-results">Analysis Results</TabsTrigger>
          <TabsTrigger value="alerts">Recent Alerts</TabsTrigger>
          <TabsTrigger value="scanning">Scanning Status</TabsTrigger>
          <TabsTrigger value="debug">Debug</TabsTrigger>
        </TabsList>

        <TabsContent value="analysis-results">
          <div className="space-y-4">
            <div className="text-sm text-muted-foreground">
              Debug: {monitoringData.length} results loaded
            </div>
            <AnalysisResults results={monitoringData} />
          </div>
        </TabsContent>

        <TabsContent value="alerts">
          <MonitoringAlerts userId={userId} />
        </TabsContent>

        <TabsContent value="scanning">
          <ScanningStatus userId={userId} />
        </TabsContent>

        <TabsContent value="debug">
          <Card>
            <CardContent className="p-4">
              <h3 className="font-semibold mb-2">Debug Information</h3>
              <div className="space-y-2 text-sm">
                <div><strong>User ID:</strong> {userId}</div>
                <div><strong>Monitoring Status:</strong> {JSON.stringify(monitoringStatus, null, 2)}</div>
                <div><strong>Monitoring Stats:</strong> {JSON.stringify(monitoringStats, null, 2)}</div>
                <div><strong>Data Count:</strong> {monitoringData.length}</div>
                <div><strong>First Data Item:</strong> {monitoringData.length > 0 ? JSON.stringify(monitoringData[0], null, 2) : 'No data'}</div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
