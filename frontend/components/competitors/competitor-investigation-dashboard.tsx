"use client"

import { useState, useEffect, useCallback } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Progress } from "@/components/ui/progress"
import { CompetitorOverview } from "./competitor-overview"
import { ContentGapAnalysis } from "./content-gap-analysis"
import { SocialMediaMonitoring } from "./social-media-monitoring"
import { CompetitorPerformance } from "./competitor-performance"
import { AddCompetitorModal } from "./add-competitor-modal"
import { CompetitorDetailsDialog } from "./competitor-details-dialog"
import { Search, TrendingUp, AlertTriangle, Eye, RefreshCw, Plus, Loader2 } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { competitorAPI, monitoringAPI } from "@/lib/api-client"
import { Competitor, CompetitorStats } from "@/lib/types"
import { useUser } from "@clerk/nextjs"
import { AnalysisResults } from "../monitoring/analysis-results"

export function CompetitorInvestigationDashboard() {
  const [timeRange, setTimeRange] = useState("7d")
  const [selectedCompetitor, setSelectedCompetitor] = useState("all")
  const [isScanning, setIsScanning] = useState(false)
  const [scanningCompetitors, setScanningCompetitors] = useState<Set<string>>(new Set())
  const [scanResults, setScanResults] = useState<any>(null)
  const [scanProgress, setScanProgress] = useState<{current: number, total: number}>({current: 0, total: 0})
  const [competitors, setCompetitors] = useState<Competitor[]>([])
  const [stats, setStats] = useState<CompetitorStats | null>(null)
  const [monitoringData, setMonitoringData] = useState<any[]>([])
  const [monitoringStats, setMonitoringStats] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const { toast } = useToast()
  const { user } = useUser()

  // Fetch competitors and stats
  const fetchCompetitors = useCallback(async () => {
    if (!user?.id) return
    
    try {
      setIsLoading(true)
      const [competitorsData, statsData] = await Promise.all([
        competitorAPI.getCompetitors(user.id),
        competitorAPI.getCompetitorStats(user.id)
      ])
      setCompetitors(competitorsData)
      setStats(statsData)
    } catch (error) {
      console.error("Error fetching competitors:", error)
      toast({
        title: "Error",
        description: "Failed to fetch competitors data",
        variant: "destructive"
      })
    } finally {
      setIsLoading(false)
    }
  }, [toast, user])

  // Fetch monitoring data
  const fetchMonitoringData = useCallback(async () => {
    if (!user?.id) return
    
    try {
      const [data, stats] = await Promise.all([
        monitoringAPI.getMonitoringData(user.id, { limit: 100 }),
        monitoringAPI.getMonitoringStats(user.id)
      ])
      setMonitoringData(data.data || [])
      setMonitoringStats(stats.stats || {})
    } catch (error) {
      console.error("Error fetching monitoring data:", error)
    }
  }, [user])

  // Fetch stats only
  const fetchStats = async () => {
    if (!user?.id) return
    
    try {
      const statsData = await competitorAPI.getCompetitorStats(user.id)
      setStats(statsData)
    } catch (error) {
      console.error("Error fetching stats:", error)
    }
  }

  // Refresh data
  const refreshData = async () => {
    setIsRefreshing(true)
    try {
      await Promise.all([
        fetchCompetitors(),
        fetchStats(),
        fetchMonitoringData()
      ])
      // Clear scan results when refreshing
      setScanResults(null)
    } catch (error) {
      console.error("Error refreshing data:", error)
    } finally {
      setIsRefreshing(false)
    }
  }

  // Clear scan results
  const clearScanResults = () => {
    setScanResults(null)
  }

  // Handle competitor added
  const handleCompetitorAdded = useCallback(() => {
    fetchCompetitors()
  }, [fetchCompetitors])

  // Handle platform-specific scan
  const handlePlatformScan = async (competitorId: string, platform: string) => {
    if (!user?.id) {
      toast({
        title: "Authentication Error",
        description: "Please log in again to continue",
        variant: "destructive"
      })
      return
    }

    try {
      // Set this competitor as scanning
      setScanningCompetitors(prev => new Set(prev).add(competitorId))
      
      toast({
        title: "Starting Scan",
        description: `Starting ${platform} scan for competitor...`,
      })

      // Call the platform-specific scan endpoint
      const result = await monitoringAPI.scanPlatform(user.id, platform, competitorId)
      
      toast({
        title: "Scan Complete",
        description: `${platform} scan completed successfully`,
      })

      // Refresh data after scan
      await Promise.all([
        fetchCompetitors(),
        fetchMonitoringData()
      ])

    } catch (error) {
      console.error(`Error in ${platform} scan:`, error)
      toast({
        title: "Scan Error",
        description: `Failed to complete ${platform} scan: ${error instanceof Error ? error.message : "Unknown error"}`,
        variant: "destructive"
      })
    } finally {
      // Remove from scanning set
      setScanningCompetitors(prev => {
        const newSet = new Set(prev)
        newSet.delete(competitorId)
        return newSet
      })
    }
  }

  // Start scan
  const startScan = async () => {
    console.log('🚀 startScan called');
    
    if (competitors.length === 0) {
      console.log('❌ No competitors found');
      toast({
        title: "No Competitors",
        description: "Please add competitors first before starting a scan",
        variant: "destructive"
      })
      return
    }

    if (!user?.id) {
      console.log('❌ No user ID found');
      toast({
        title: "Authentication Error",
        description: "Please log in again to continue",
        variant: "destructive"
      })
      return
    }

    console.log('✅ Starting scan process...');
    setIsScanning(true)
    // Set all active competitors as scanning
    const activeCompetitors = competitors.filter(c => c.status === 'active')
    console.log('📊 Active competitors:', activeCompetitors);
    setScanningCompetitors(new Set(activeCompetitors.map(c => c.id)))
    setScanProgress({current: 0, total: activeCompetitors.length})
    
    try {
      console.log(`🚀 Starting scan for user: ${user.id}`)
      console.log(`📊 Found ${activeCompetitors.length} active competitors to scan`)
      
      // Call the backend scan endpoint
      console.log('📡 Calling competitorAPI.scanAllCompetitors...');
      const scanResult = await competitorAPI.scanAllCompetitors(user.id)
      console.log('✅ Scan result received:', scanResult)
      
      setScanResults(scanResult)
      setScanProgress({current: scanResult.competitors_scanned || 0, total: scanResult.total_competitors || 0})
      
      toast({
        title: "Scan Complete",
        description: `Successfully scanned ${scanResult.competitors_scanned || 0} competitors. ${scanResult.successful_scans || 0} successful, ${scanResult.failed_scans || 0} failed.`
      })
      
      // Refresh data after scan
      console.log('🔄 Refreshing competitor data...');
      await Promise.all([
        fetchCompetitors(),
        fetchMonitoringData()
      ])
      console.log('✅ Competitor data refreshed');
    } catch (error) {
      console.error("❌ Error during scan:", error)
      toast({
        title: "Scan Error",
        description: error instanceof Error ? error.message : "Failed to complete competitor scan",
        variant: "destructive"
      })
    } finally {
      console.log('🏁 Scan process completed, cleaning up...');
      setIsScanning(false)
      setScanningCompetitors(new Set())
      setScanProgress({current: 0, total: 0})
    }
  }

  // Load data on component mount
  useEffect(() => {
    if (user) {
      fetchCompetitors()
      fetchMonitoringData()
    }
  }, [fetchCompetitors, fetchMonitoringData, user])

  // Format last scan time
  const formatLastScan = (lastScanAt?: string) => {
    if (!lastScanAt) return "Never scanned"
    
    const lastScan = new Date(lastScanAt)
    const now = new Date()
    const diffMs = now.getTime() - lastScan.getTime()
    const diffMins = Math.floor(diffMs / (1000 * 60))
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
    
    if (diffMins < 60) return `${diffMins} minutes ago`
    if (diffHours < 24) return `${diffHours} hours ago`
    return `${diffDays} days ago`
  }

  // Get status badge variant
  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'active': return 'default'
      case 'paused': return 'secondary'
      case 'error': return 'destructive'
      default: return 'outline'
    }
  }

  // Calculate real metrics from monitoring data
  const calculateMetrics = () => {
    const totalPosts = monitoringData.length
    const alertWorthyPosts = monitoringData.filter(post => post.is_alert_worthy).length
    const recentPosts = monitoringData.filter(post => {
      const postDate = new Date(post.detected_at)
      const now = new Date()
      const diffDays = (now.getTime() - postDate.getTime()) / (1000 * 60 * 60 * 24)
      return diffDays <= 7
    }).length

    return {
      totalPosts,
      alertWorthyPosts,
      recentPosts,
      contentGaps: Math.max(0, totalPosts - recentPosts) // Simple gap calculation
    }
  }

  const metrics = calculateMetrics()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Loading competitor data...</span>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Competitor Intelligence</h1>
          <p className="text-muted-foreground">AI-powered competitive analysis and monitoring</p>
        </div>
        <div className="flex items-center gap-3">
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7d">Last 7 days</SelectItem>
              <SelectItem value="30d">Last 30 days</SelectItem>
              <SelectItem value="90d">Last 90 days</SelectItem>
            </SelectContent>
          </Select>
          <Button onClick={startScan} disabled={isScanning || competitors.length === 0}>
            <RefreshCw className={`mr-2 h-4 w-4 ${isScanning ? "animate-spin" : ""}`} />
            {isScanning ? "Scanning..." : "Scan Now"}
          </Button>
          <Button variant="outline" onClick={refreshData} disabled={isRefreshing}>
            <RefreshCw className={`mr-2 h-4 w-4 ${isRefreshing ? "animate-spin" : ""}`} />
            Refresh
          </Button>
          <AddCompetitorModal onCompetitorAdded={handleCompetitorAdded} />
        </div>
      </div>


      {/* Scan Progress Indicator */}
      {isScanning && scanProgress.total > 0 && (
        <Card className="border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-950/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <RefreshCw className="h-5 w-5 text-blue-600 animate-spin" />
              Scanning Competitors...
            </CardTitle>
            <CardDescription>
              Scanning {scanProgress.current} of {scanProgress.total} competitors
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between text-sm text-muted-foreground">
                <span>Progress</span>
                <span>{Math.round((scanProgress.current / scanProgress.total) * 100)}%</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                <div 
                  className="bg-blue-600 h-3 rounded-full transition-all duration-300"
                  style={{ width: `${(scanProgress.current / scanProgress.total) * 100}%` }}
                ></div>
              </div>
              <div className="text-center text-sm text-muted-foreground">
                {scanProgress.current} of {scanProgress.total} competitors processed
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Competitors Tracked</CardTitle>
            <Eye className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_competitors || 0}</div>
            <p className="text-xs text-muted-foreground">
              {stats?.active_competitors || 0} actively monitored
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Content Gaps Found</CardTitle>
            <Search className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.contentGaps}</div>
            <p className="text-xs text-muted-foreground">
              {metrics.recentPosts} recent posts analyzed
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Threat Alerts</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">{metrics.alertWorthyPosts}</div>
            <p className="text-xs text-muted-foreground">
              AI-detected significant events
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Posts Analyzed</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.totalPosts}</div>
            <p className="text-xs text-muted-foreground">
              Across all platforms
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Scan Results Summary */}
      {scanResults && (
        <Card className="border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-950/20">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <RefreshCw className="h-5 w-5 text-blue-600" />
                Last Scan Results
              </CardTitle>
              <Button variant="outline" size="sm" onClick={clearScanResults}>
                Clear Results
              </Button>
            </div>
            <CardDescription>
              Scan completed at {new Date(scanResults.scan_started_at).toLocaleString()}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <AnalysisResults results={scanResults.results || []} />
          </CardContent>
        </Card>
      )}

      {/* Competitor Status Overview */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Competitor Status</CardTitle>
              <CardDescription>Real-time monitoring status and recent activity</CardDescription>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={refreshData}
              disabled={isRefreshing}
            >
              <RefreshCw className={`mr-2 h-4 w-4 ${isRefreshing ? "animate-spin" : ""}`} />
              Refresh
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {competitors.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <Eye className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p className="text-lg font-medium">No competitors added yet</p>
              <p className="text-sm">Add your first competitor to start monitoring their activities</p>
            </div>
          ) : (
            <div className="space-y-4">
              {competitors.map((competitor) => (
                <div key={competitor.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-gray-100 dark:bg-gray-800 rounded-lg flex items-center justify-center">
                      <span className="font-semibold text-sm">{competitor.name.slice(0, 2).toUpperCase()}</span>
                    </div>
                    <div>
                      <h3 className="font-medium">{competitor.name}</h3>
                      <p className="text-sm text-muted-foreground">
                        Last scan: {formatLastScan(competitor.last_scan_at)}
                      </p>
                      {competitor.industry && (
                        <p className="text-xs text-muted-foreground">{competitor.industry}</p>
                      )}
                      {competitor.platforms && competitor.platforms.length > 0 && (
                        <div className="flex items-center gap-1 mt-1">
                          {competitor.platforms.slice(0, 3).map((platform) => (
                            <Badge key={platform} variant="outline" className="text-xs">
                              {platform}
                            </Badge>
                          ))}
                          {competitor.platforms.length > 3 && (
                            <Badge variant="outline" className="text-xs">
                              +{competitor.platforms.length - 3}
                            </Badge>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    {scanningCompetitors.has(competitor.id) && (
                      <div className="flex items-center gap-2 text-blue-600">
                        <RefreshCw className="h-4 w-4 animate-spin" />
                        <span className="text-xs">Scanning...</span>
                      </div>
                    )}
                    
                    {/* Platform-specific scan buttons */}
                    <div className="flex items-center gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handlePlatformScan(competitor.id, 'youtube')}
                        disabled={scanningCompetitors.has(competitor.id)}
                        className="h-8 px-2 text-xs"
                      >
                        <RefreshCw className="h-3 w-3 mr-1" />
                        YouTube
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handlePlatformScan(competitor.id, 'website')}
                        disabled={scanningCompetitors.has(competitor.id)}
                        className="h-8 px-2 text-xs"
                      >
                        <RefreshCw className="h-3 w-3 mr-1" />
                        Website
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handlePlatformScan(competitor.id, 'browser')}
                        disabled={scanningCompetitors.has(competitor.id)}
                        className="h-8 px-2 text-xs"
                      >
                        <RefreshCw className="h-3 w-3 mr-1" />
                        Web
                      </Button>
                    </div>
                    
                    <Badge variant={getStatusBadgeVariant(competitor.status)}>
                      {competitor.status}
                    </Badge>
                    <Badge variant="outline" className="text-xs">
                      {competitor.scan_frequency_minutes}min
                    </Badge>
                    <CompetitorDetailsDialog 
                      competitor={competitor} 
                      onCompetitorUpdated={handleCompetitorAdded}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Main Analysis Tabs */}
      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="content-gaps">Content Gaps</TabsTrigger>
          <TabsTrigger value="social-monitoring">Social Monitoring</TabsTrigger>
          <TabsTrigger value="performance">Performance Comparison</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <CompetitorOverview timeRange={timeRange} monitoringData={monitoringData} />
        </TabsContent>

        <TabsContent value="content-gaps" className="space-y-6">
          <ContentGapAnalysis monitoringData={monitoringData} />
        </TabsContent>

        <TabsContent value="social-monitoring" className="space-y-6">
          <SocialMediaMonitoring monitoringData={monitoringData} />
        </TabsContent>

        <TabsContent value="performance" className="space-y-6">
          <CompetitorPerformance timeRange={timeRange} monitoringData={monitoringData} />
        </TabsContent>
      </Tabs>
    </div>
  )
}
