"use client"

import { useState, useEffect, useCallback, useMemo } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Input } from "@/components/ui/input"
import { Bell, Eye, TrendingUp, Clock, Play, Pause, Loader2, Search, RefreshCw, Filter } from "lucide-react"
import { MonitoringAlerts } from "./monitoring-alerts"
import { ScanningStatus } from "./scanning-status"
import { AnalysisResults } from "./analysis-results"
import { MonitoringDataDetailsModal } from "./monitoring-data-details-modal"
import { useApiClient, handleApiError, monitoringAPI } from "@/lib/api-client"
import { useToast } from "@/hooks/use-toast"
import GradientText from "@/components/effects/GradientText"
import ShinyText from "@/components/effects/ShinyText"
import "../../styles/competitor-animations.css"

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
  const [selectedDataForQuickView, setSelectedDataForQuickView] = useState<MonitoringData | null>(null)
  const [isQuickViewModalOpen, setIsQuickViewModalOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState("")
  const [isVisible, setIsVisible] = useState(false)
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

      if ((statusRes as any).success && (statusRes as any).status) {
        console.log('✅ Status response successful, setting monitoring status');
        const statusData = (statusRes as any).status;
        setMonitoringStatus({
          running: statusData.running || false,
          total_active_jobs: statusData.total_active_jobs || 0,
          next_scheduled_run: statusData.next_scheduled_run
        });
        setIsMonitoring(statusData.running || false);
      } else {
        console.log('❌ Status response not successful:', statusRes);
        setMonitoringStatus({
          running: false,
          total_active_jobs: 0,
          next_scheduled_run: undefined
        });
        setIsMonitoring(false);
      }
      
      if ((statsRes as any).success && (statsRes as any).stats) {
        console.log('✅ Stats response successful, setting monitoring stats');
        const statsData = (statsRes as any).stats;
        setMonitoringStats({
          total_competitors: statsData.total_competitors || 0,
          unread_alerts: statsData.unread_alerts || 0,
          recent_activity_24h: statsData.recent_activity_24h || 0,
          last_scan_time: statsData.last_scan_time
        });
      } else {
        console.log('❌ Stats response not successful:', statsRes);
        setMonitoringStats({
          total_competitors: 0,
          unread_alerts: 0,
          recent_activity_24h: 0,
          last_scan_time: undefined
        });
      }
      
      if (dataRes.data) {
        console.log('✅ Data response successful, setting monitoring data');
        setMonitoringData(dataRes.data);
      } else if (Array.isArray(dataRes)) {
        console.log('✅ Data response successful (array format), setting monitoring data');
        setMonitoringData(dataRes);
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
    
    setIsVisible(true);
    
    // Cleanup function to prevent memory leaks
    return () => {
      console.log('🧹 Cleaning up monitoring dashboard');
    };
  }, [userId]); // Only depend on userId, not fetchAllData


  // Handle monitoring toggle
  const handleMonitoringToggle = async (enabled: boolean) => {
    try {
      setIsTogglingMonitoring(true)
      
      if (enabled) {
        // Start continuous monitoring
        const result = await apiClient.startContinuousMonitoring(userId) as any
        if (result.success) {
          setIsMonitoring(true)
          toast({
            title: "Success",
            description: result.message || "Monitoring started successfully",
          })
          
          // Update monitoring status
          setMonitoringStatus({
            running: true,
            total_active_jobs: 1,
            next_scheduled_run: new Date(Date.now() + 300000).toISOString() // 5 minutes from now
          })
        } else {
          throw new Error(result.message || "Failed to start monitoring")
        }
      } else {
        // Stop continuous monitoring
        const result = await apiClient.stopContinuousMonitoring(userId) as any
        if (result.success) {
          setIsMonitoring(false)
          toast({
            title: "Success",
            description: result.message || "Monitoring stopped successfully",
          })
          
          // Update monitoring status
          setMonitoringStatus({
            running: false,
            total_active_jobs: 0,
            next_scheduled_run: undefined
          })
        } else {
          throw new Error(result.message || "Failed to stop monitoring")
        }
      }
    } catch (error) {
      console.error('Error toggling monitoring:', error)
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to toggle monitoring",
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

      // Call the actual API to run monitoring for all competitors
      const result = await apiClient.runMonitoringForAllCompetitors(userId) as any;
      
      if (result.success) {
        toast({
          title: "Scan Initiated",
          description: result.message || "Competitor monitoring scan has been started. This may take several minutes to complete.",
        });

        // Refresh data after a short delay to show initial results
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
        throw new Error(result.message || "Failed to start scan");
      }

    } catch (error) {
      console.error('Error starting scan:', error);
      toast({
        title: "Scan Error",
        description: error instanceof Error ? error.message : "Failed to initiate competitor scan. Please try again.",
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

  // Filter monitoring data based on search query
  const filteredMonitoringData = useMemo(() => {
    if (!searchQuery.trim()) return monitoringData
    
    const query = searchQuery.toLowerCase()
    return monitoringData.filter(item => 
      item.content_text.toLowerCase().includes(query) ||
      item.platform.toLowerCase().includes(query) ||
      item.post_type.toLowerCase().includes(query) ||
      (item.author_username && item.author_username.toLowerCase().includes(query)) ||
      (item.author_display_name && item.author_display_name.toLowerCase().includes(query))
    )
  }, [monitoringData, searchQuery])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    )
  }

  return (
    <div className="relative">
      {/* Subtle background overlay for depth */}
      <div className="absolute inset-0 bg-gradient-to-br from-transparent via-blue-950/3 to-purple-950/3 pointer-events-none"></div>
      
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-500/4 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-500/4 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }}></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-r from-blue-500/2 to-purple-500/2 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
      </div>

      <div className={`relative z-10 space-y-6 transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
      {/* Header */}
      <div className={`flex items-center justify-between transition-all duration-1000 delay-200 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'}`}>
        <div>
          <h1 className="text-3xl font-bold">
            <GradientText>Continuous Monitoring</GradientText>
          </h1>
          <div className="text-muted-foreground">
            <ShinyText text="Daily competitor surveillance and alerts" />
          </div>
        </div>
        <div className={`flex items-center gap-4 transition-all duration-1000 delay-400 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'}`}>
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
      <div className={`grid grid-cols-1 md:grid-cols-4 gap-4 transition-all duration-1000 delay-600 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'}`}>
        <Card className="glass-card transition-all duration-300 hover:scale-105 hover:shadow-xl border-white/20 animate-fade-in-up" style={{ animationDelay: '100ms' }}>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <div className="relative p-2.5 rounded-xl bg-gradient-to-r from-blue-500 to-indigo-600 shadow-lg overflow-hidden">
                <div className="absolute inset-0 bg-white/10 animate-pulse"></div>
                <Eye className="relative h-5 w-5 text-white" />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-300">Competitors Monitored</p>
                <p className="text-2xl font-bold text-white bg-gradient-to-r from-white to-slate-200 bg-clip-text text-transparent">
                  {monitoringStats?.total_competitors ?? 0}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="glass-card transition-all duration-300 hover:scale-105 hover:shadow-xl border-white/20 animate-fade-in-up" style={{ animationDelay: '200ms' }}>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <div className="relative p-2.5 rounded-xl bg-gradient-to-r from-orange-500 to-red-600 shadow-lg overflow-hidden">
                <div className="absolute inset-0 bg-white/10 animate-pulse"></div>
                <Bell className="relative h-5 w-5 text-white" />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-300">Unread Alerts</p>
                <p className="text-2xl font-bold text-orange-600 bg-gradient-to-r from-orange-400 to-orange-600 bg-clip-text text-transparent">
                  {monitoringStats?.unread_alerts ?? 0}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="glass-card transition-all duration-300 hover:scale-105 hover:shadow-xl border-white/20 animate-fade-in-up" style={{ animationDelay: '300ms' }}>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <div className="relative p-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 shadow-lg overflow-hidden">
                <div className="absolute inset-0 bg-white/10 animate-pulse"></div>
                <TrendingUp className="relative h-5 w-5 text-white" />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-300">Activity (24h)</p>
                <p className="text-2xl font-bold text-green-600 bg-gradient-to-r from-green-400 to-green-600 bg-clip-text text-transparent">
                  {monitoringStats?.recent_activity_24h ?? 0}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="glass-card transition-all duration-300 hover:scale-105 hover:shadow-xl border-white/20 animate-fade-in-up" style={{ animationDelay: '400ms' }}>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <div className="relative p-2.5 rounded-xl bg-gradient-to-r from-purple-500 to-violet-600 shadow-lg overflow-hidden">
                <div className="absolute inset-0 bg-white/10 animate-pulse"></div>
                <Clock className="relative h-5 w-5 text-white" />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-300">Last Scan</p>
                <p className="text-2xl font-bold text-purple-600 bg-gradient-to-r from-purple-400 to-purple-600 bg-clip-text text-transparent">
                  {getLastScanTime()}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>



      {/* Data Summary */}
      {monitoringData.length > 0 && (
        <Card className={`glass-card transition-all duration-300 hover:scale-105 hover:shadow-xl border-white/20 animate-fade-in-up delay-800 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold">Recent Activity Summary</h3>
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setSelectedDataForQuickView(monitoringData[0])
                  setIsQuickViewModalOpen(true)
                }}
                className="text-xs"
              >
                <Eye className="h-3 w-3 mr-1" />
                View Latest Details
              </Button>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground">Core Platforms</p>
                <p className="font-medium">
                  YouTube, Web Content, Website
                </p>
              </div>
              <div>
                <p className="text-muted-foreground">New Posts</p>
                <p className="font-medium">
                  {monitoringData.filter(item => item.is_new_post).length}
                </p>
              </div>
              <div>
                <p className="text-muted-foreground">Content Changes</p>
                <p className="font-medium">
                  {monitoringData.filter(item => item.is_content_change).length}
                </p>
              </div>
              <div>
                <p className="text-muted-foreground">Latest Activity</p>
                <p className="font-medium">
                  {monitoringData.length > 0 
                    ? new Date(monitoringData[0].detected_at).toLocaleDateString()
                    : 'N/A'
                  }
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Main Content */}
      <Tabs defaultValue="analysis-results" className={`space-y-4 transition-all duration-1000 delay-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
        <TabsList className="glass-card p-1 bg-slate-800/40 border border-white/20 backdrop-blur-md">
          <TabsTrigger value="analysis-results" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-600 data-[state=active]:to-purple-600 data-[state=active]:text-white data-[state=active]:shadow-lg font-semibold text-slate-300 transition-all duration-300">Analysis Results</TabsTrigger>
          <TabsTrigger value="alerts" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-600 data-[state=active]:to-purple-600 data-[state=active]:text-white data-[state=active]:shadow-lg font-semibold text-slate-300 transition-all duration-300">Recent Alerts</TabsTrigger>
        </TabsList>

        {/* Search and Filter */}
        <div className={`flex items-center gap-4 transition-all duration-700 delay-1200 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'}`}>
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search monitoring data..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
          <div className="text-sm text-muted-foreground">
            {filteredMonitoringData.length} of {monitoringData.length} results
          </div>
          {searchQuery && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSearchQuery("")}
              className="text-xs"
            >
              Clear Search
            </Button>
          )}
          {searchQuery && filteredMonitoringData.length > 0 && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setSelectedDataForQuickView(filteredMonitoringData[0])
                setIsQuickViewModalOpen(true)
              }}
              className="text-xs"
            >
              <Eye className="h-3 w-3 mr-1" />
              View First Result
            </Button>
          )}
        </div>

        <TabsContent value="analysis-results">
          <div className={`space-y-4 transition-all duration-700 delay-1400 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'}`}>
            <div className="flex items-center justify-between">
              <div className="text-sm text-muted-foreground">
                {monitoringData.length} results loaded
              </div>
              <div className="text-xs text-muted-foreground">
                Click "Details" button on any item to view full information
              </div>
            </div>
            <AnalysisResults results={filteredMonitoringData} />
          </div>
        </TabsContent>

        <TabsContent value="alerts">
          <div className={`transition-all duration-700 delay-1400 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'}`}>
            <MonitoringAlerts userId={userId} />
          </div>
        </TabsContent>

        <TabsContent value="scanning">
          <div className={`transition-all duration-700 delay-1400 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'}`}>
            <ScanningStatus userId={userId} />
          </div>
        </TabsContent>
      </Tabs>

      {/* Quick View Modal */}
      {selectedDataForQuickView && (
        <MonitoringDataDetailsModal
          isOpen={isQuickViewModalOpen}
          onClose={() => setIsQuickViewModalOpen(false)}
          data={selectedDataForQuickView}
        />
      )}
    </div>
    </div>
  )
}
