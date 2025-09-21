"use client"

import '../../styles/competitor-animations.css'
import { useState, useEffect } from "react"
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
import { useUser } from "@clerk/nextjs"
import { Competitor, MonitoringData } from "@/lib/types"
import { 
  Filter, 
  TrendingUp, 
  AlertTriangle, 
  Users, 
  Target, 
  BarChart3,
  Eye,
  Activity,
  Zap,
  RefreshCw,
  Youtube,
  Globe,
  Search,
  Loader2,
  Clock
} from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import GradientText from "@/components/effects/GradientText"
import ShinyText from "@/components/effects/ShinyText"

export function CompetitorInvestigationDashboard() {
  const [competitors, setCompetitors] = useState<Competitor[]>([])
  const [monitoringData, setMonitoringData] = useState<MonitoringData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [timeRange, setTimeRange] = useState("7d")
  const [selectedIndustry, setSelectedIndustry] = useState("all")
  const [showAddModal, setShowAddModal] = useState(false)
  const [scanningStates, setScanningStates] = useState<Record<string, Record<string, boolean>>>({})
  const [isVisible, setIsVisible] = useState(false)
  const { user, isLoaded } = useUser()
  const { toast } = useToast()

  // Set visibility for animations
  useEffect(() => {
    setIsVisible(true)
  }, [])

  // Fetch competitors data
  const fetchCompetitors = async () => {
    if (!user?.id) {
      console.log('No user ID available, skipping API call')
      return
    }

    console.log('🔍 Fetching competitors with user ID:', user.id)
    
    try {
      setError(null)
      const response = await fetch('/api/v1/competitors', {
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': user.id,
        },
      })
      
      console.log('📡 Competitors API response status:', response.status)
      console.log('📡 Competitors API response headers:', Object.fromEntries(response.headers.entries()))
      
      if (response.ok) {
        const data = await response.json()
        console.log('✅ Competitors data received:', data)
        setCompetitors(data)
      } else {
        const errorText = await response.text()
        console.error('❌ Failed to fetch competitors:', response.status, errorText)
        setError(`Failed to fetch competitors: ${response.status} - ${errorText}`)
        // Set fallback data for development
        setCompetitors([
          {
            id: "demo-1",
            name: "Demo Competitor 1",
            industry: "Technology",
            status: "active",
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            scan_frequency_minutes: 1440,
            user_id: "demo-user-1"
          },
          {
            id: "demo-2", 
            name: "Demo Competitor 2",
            industry: "E-commerce",
            status: "active",
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            scan_frequency_minutes: 1440,
            user_id: "demo-user-1"
          }
        ])
      }
    } catch (error) {
      console.error('❌ Error fetching competitors:', error)
      setError('Failed to connect to competitors API')
      // Set fallback data for development
      setCompetitors([
        {
          id: "demo-1",
          name: "Demo Competitor 1",
          industry: "Technology",
          status: "active",
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          scan_frequency_minutes: 1440,
          user_id: "demo-user-1"
        },
        {
          id: "demo-2",
          name: "Demo Competitor 2", 
          industry: "E-commerce",
          status: "active",
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          scan_frequency_minutes: 1440,
          user_id: "demo-user-1"
        }
      ])
    }
  }

  // Fetch monitoring data
  const fetchMonitoringData = async () => {
    if (!user?.id) {
      console.log('No user ID available, skipping API call')
      return
    }

    console.log('🔍 Fetching monitoring data with user ID:', user.id)
    
    try {
      setError(null)
      const response = await fetch('/api/v1/monitoring/data', {
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': user.id,
        },
      })
      
      console.log('📡 Monitoring API response status:', response.status)
      console.log('📡 Monitoring API response headers:', Object.fromEntries(response.headers.entries()))
      
      if (response.ok) {
        const data = await response.json()
        console.log('✅ Monitoring data received:', data)
        setMonitoringData(data)
      } else {
        const errorText = await response.text()
        console.error('❌ Failed to fetch monitoring data:', response.status, errorText)
        setError(`Failed to fetch monitoring data: ${response.status} - ${errorText}`)
        // Set fallback data for development
        setMonitoringData([
          {
            id: "demo-1",
            competitor_id: "demo-1",
            platform: "youtube",
            content_text: "Demo video content about new product features",
            content_hash: "demo-hash-1",
            detected_at: new Date().toISOString(),
            is_content_change: true
          },
          {
            id: "demo-2",
            competitor_id: "demo-2", 
            platform: "instagram",
            content_text: "Demo image post showcasing new collection",
            content_hash: "demo-hash-2",
            detected_at: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
            is_content_change: false
          }
        ])
      }
    } catch (error) {
      console.error('❌ Error fetching monitoring data:', error)
      setError('Failed to connect to monitoring API')
      // Set fallback data for development
      setMonitoringData([
        {
          id: "demo-1",
          competitor_id: "demo-1",
          platform: "youtube",
          content_text: "Demo video content about new product features",
          content_hash: "demo-hash-1",
          detected_at: new Date().toISOString(),
          is_content_change: true
        },
        {
          id: "demo-2",
          competitor_id: "demo-2",
          platform: "instagram", 
          content_text: "Demo image post showcasing new collection",
          content_hash: "demo-hash-2",
          detected_at: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
          is_content_change: false
        }
      ])
    } finally {
      setLoading(false)
    }
  }

  // Refresh all data
  const refreshData = async () => {
    setLoading(true)
    setError(null)
    await Promise.all([fetchCompetitors(), fetchMonitoringData()])
  }

  // Handle competitor added
  const handleCompetitorAdded = () => {
    setShowAddModal(false)
    fetchCompetitors() // Refresh the competitors list
  }

  // Handle agent invocation for specific platform
  const handleAgentInvocation = async (competitorId: string, platform: string) => {
    if (!user?.id) {
      toast({
        title: "Authentication Error",
        description: "Please sign in to use this feature",
        variant: "destructive"
      })
      return
    }

    // Set scanning state for this specific competitor and platform
    setScanningStates(prev => ({
      ...prev,
      [competitorId]: {
        ...prev[competitorId],
        [platform]: true
      }
    }))

    try {
      const response = await fetch(`/api/v1/monitoring/scan-platform/${platform}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': user.id,
        },
        body: JSON.stringify({
          competitor_id: competitorId
        })
      })

      if (response.ok) {
        const result = await response.json()
        toast({
          title: `${platform.charAt(0).toUpperCase() + platform.slice(1)} Scan Complete`,
          description: result.message,
          variant: "default"
        })
        
        // Refresh monitoring data to show new results
        await fetchMonitoringData()
      } else {
        const errorData = await response.json()
        toast({
          title: "Scan Failed",
          description: errorData.detail || `Failed to scan ${platform}`,
          variant: "destructive"
        })
      }
    } catch (error) {
      console.error(`Error invoking ${platform} agent:`, error)
      toast({
        title: "Scan Error",
        description: `Failed to invoke ${platform} agent. Please try again.`,
        variant: "destructive"
      })
    } finally {
      // Clear scanning state
      setScanningStates(prev => ({
        ...prev,
        [competitorId]: {
          ...prev[competitorId],
          [platform]: false
        }
      }))
    }
  }

  useEffect(() => {
    if (isLoaded && user?.id) {
      fetchCompetitors()
    }
  }, [isLoaded, user?.id])

  useEffect(() => {
    if (isLoaded && user?.id) {
      fetchMonitoringData()
    }
  }, [isLoaded, user?.id])

  // Filter competitors based on industry only
  const filteredCompetitors = competitors.filter(competitor => {
    const matchesIndustry = selectedIndustry === "all" || 
                          (competitor.industry && competitor.industry === selectedIndustry)
    return matchesIndustry
  })

  // Get unique industries for filter (safely handle null values)
  const industries = ["all", ...Array.from(new Set(
    competitors
      .map(c => c.industry)
      .filter((industry): industry is string => 
        industry !== undefined && 
        industry !== null && 
        industry.trim() !== ''
      )
  ))]

  // Show loading state while user is being loaded
  if (!isLoaded) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading user authentication...</p>
        </div>
      </div>
    )
  }

  // Show error if user is not authenticated
  if (!user?.id) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 mx-auto mb-4 text-red-500" />
          <p className="text-lg font-medium text-red-600">Authentication Required</p>
          <p className="text-sm text-muted-foreground">Please sign in to view competitor intelligence</p>
          <div className="mt-4 p-4 bg-gray-100 dark:bg-gray-800 rounded-lg text-left text-sm">
            <p><strong>Debug Info:</strong></p>
            <p>User loaded: {isLoaded ? 'Yes' : 'No'}</p>
            <p>User object: {JSON.stringify(user, null, 2)}</p>
          </div>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="relative mb-6">
            <div className="w-16 h-16 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin mx-auto"></div>
            <div className="absolute inset-0 w-16 h-16 border-4 border-purple-500/20 border-t-purple-500 rounded-full animate-spin mx-auto" style={{ animationDirection: 'reverse', animationDuration: '1.5s' }}></div>
          </div>
          <div className="space-y-2">
            <ShinyText 
              text="Loading Intelligence Data..." 
              disabled={false} 
              speed={3} 
              className="text-xl font-semibold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent"
            />
            <p className="text-slate-400">Analyzing competitor activities and trends...</p>
          </div>
        </div>
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

      <div className={`relative z-10 space-y-8 transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
      {/* Header */}
      <div className={`flex items-center justify-between transition-all duration-1000 delay-200 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'}`}>
        <div>
          <h2 className="text-4xl font-bold tracking-tight mb-2">
            <GradientText
              colors={["#60a5fa", "#a78bfa", "#34d399", "#fbbf24"]}
              animationSpeed={6}
              showBorder={false}
              className="text-4xl font-bold"
            >
              Competitor Intelligence Hub
            </GradientText>
          </h2>
          <div className="text-lg text-slate-300">
            <ShinyText 
              text="Deep dive into competitor strategies and performance with AI-powered insights" 
              disabled={false} 
              speed={4} 
              className="text-lg text-slate-300"
            />
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={refreshData}
            className="bg-white/10 border-white/20 text-white hover:bg-white/20 hover:border-white/30 transition-all duration-300 backdrop-blur-sm"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh Data
          </Button>
          <Button 
            onClick={() => setShowAddModal(true)} 
            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white border-0 shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-300 backdrop-blur-sm"
          >
            <Users className="h-4 w-4 mr-2" />
            Add Competitor
          </Button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <Card className={`border-red-500/50 bg-gradient-to-r from-red-900/20 to-orange-900/20 backdrop-blur-sm transition-all duration-1000 delay-300 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'}`}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-300">
              <AlertTriangle className="h-5 w-5 animate-pulse" />
              API Connection Issue
            </CardTitle>
            <CardDescription className="text-red-200">
              {error} - Showing demo data for development purposes
            </CardDescription>
          </CardHeader>
        </Card>
      )}

      {/* Filters */}
      <div className={`flex items-center gap-4 transition-all duration-1000 delay-400 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'}`}>
        <Select value={selectedIndustry} onValueChange={setSelectedIndustry}>
          <SelectTrigger className="w-48 bg-white/10 border-white/20 text-white backdrop-blur-sm hover:bg-white/20 transition-all duration-300">
            <SelectValue placeholder="Industry" />
          </SelectTrigger>
          <SelectContent>
            {industries.map((industry) => (
              <SelectItem key={industry} value={industry}>
                {industry === "all" ? "All Industries" : industry}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Competitor List */}
      <Card className={`bg-slate-800/20 backdrop-blur-xl border-slate-700/30 shadow-lg transition-all duration-1000 delay-500 hover:bg-slate-800/30 hover:border-slate-600/40 hover:shadow-xl ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'}`}>
        <CardHeader>
          <CardTitle className="text-white text-xl">
            <div className="flex items-center gap-2">
              <Target className="h-6 w-6 text-blue-400" />
              Competitors ({filteredCompetitors.length})
            </div>
          </CardTitle>
          <CardDescription className="text-slate-300">
            Active competitors being monitored. Use the agent buttons to run specific monitoring scans:
            <br />
            <span className="text-sm text-slate-400">
              • <strong className="text-red-400">YouTube:</strong> Analyze video content, channels, and engagement metrics
              <br />
              • <strong className="text-blue-400">Browser:</strong> Search web content and analyze online presence  
              <br />
              • <strong className="text-green-400">Website:</strong> Analyze website content, structure, and updates
            </span>
          </CardDescription>
        </CardHeader>
        <CardContent>
          {filteredCompetitors.length > 0 ? (
            <div className="space-y-4">
              {filteredCompetitors.map((competitor, index) => (
                <div
                  key={competitor.id}
                  className={`group relative overflow-hidden p-6 border border-slate-600/30 rounded-xl bg-gradient-to-r from-slate-800/40 to-slate-700/40 backdrop-blur-lg hover:from-blue-900/25 hover:to-purple-900/25 transition-all duration-500 hover:scale-[1.02] hover:shadow-xl hover:shadow-blue-500/15 hover:border-blue-400/40 animate-fade-in-up shadow-md`}
                  style={{ 
                    animationDelay: `${index * 0.1}s`,
                    animationFillMode: 'both'
                  }}
                >
                  {/* Animated background glow */}
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-pink-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 rounded-xl"></div>
                  
                  {/* Scanning pulse effect */}
                  {Object.values(scanningStates[competitor.id] || {}).some(Boolean) && (
                    <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 to-purple-500/20 animate-pulse rounded-xl"></div>
                  )}

                  <div className="relative z-10 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="relative w-16 h-16 bg-gradient-to-br from-blue-500/30 to-purple-500/30 rounded-xl flex items-center justify-center backdrop-blur-sm border border-white/20 group-hover:scale-110 transition-all duration-300">
                        <span className="font-bold text-white text-xl">
                          {competitor.name.slice(0, 2).toUpperCase()}
                        </span>
                        {/* Scanning indicator */}
                        {Object.values(scanningStates[competitor.id] || {}).some(Boolean) && (
                          <div className="absolute -top-2 -right-2 w-6 h-6 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center shadow-lg">
                            <Loader2 className="h-4 w-4 text-white animate-spin" />
                          </div>
                        )}
                        {/* Floating particles effect */}
                        <div className="absolute top-1 right-1 w-2 h-2 bg-blue-400/50 rounded-full animate-ping group-hover:animate-pulse"></div>
                        <div className="absolute bottom-2 left-2 w-1 h-1 bg-purple-400/50 rounded-full animate-pulse delay-75"></div>
                      </div>
                      <div className="space-y-2">
                        <h3 className="font-bold text-xl text-white group-hover:text-blue-200 transition-colors duration-300">
                          {competitor.name}
                        </h3>
                        <p className="text-slate-300 group-hover:text-white transition-colors duration-300">
                          {competitor.industry}
                        </p>
                        {/* Enhanced scanning status indicator */}
                        {Object.entries(scanningStates[competitor.id] || {}).some(([platform, isScanning]) => isScanning) && (
                          <div className="flex items-center gap-2 p-2 bg-blue-500/20 rounded-lg border border-blue-400/30 backdrop-blur-sm">
                            <Loader2 className="h-4 w-4 text-blue-400 animate-spin" />
                            <span className="text-sm text-blue-300 font-medium">
                              Scanning: {Object.entries(scanningStates[competitor.id] || {})
                                .filter(([platform, isScanning]) => isScanning)
                                .map(([platform]) => platform.charAt(0).toUpperCase() + platform.slice(1))
                                .join(", ")}
                            </span>
                          </div>
                        )}
                        {/* Enhanced status indicators */}
                        <div className="flex items-center gap-3">
                          <div className="flex items-center gap-1">
                            <Clock className="h-4 w-4 text-slate-400" />
                            <span className="text-sm text-slate-400">
                              {competitor.last_scan_at 
                                ? `Last scanned: ${new Date(competitor.last_scan_at).toLocaleDateString()}`
                                : "No recent scans"
                              }
                            </span>
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          <div className="flex items-center gap-1">
                            <Activity className="h-4 w-4 text-green-400" />
                            <span className="text-sm text-slate-300">Auto-scan: every 24 hours</span>
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          <Badge variant="secondary" className="text-xs bg-blue-500/20 text-blue-300 border-blue-400/30">
                            Core Monitoring
                          </Badge>
                          <span className="text-sm text-slate-400">YouTube, Web, Website</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      {/* Enhanced Agent Invocation Buttons */}
                      <div className="flex items-center gap-3 border-r border-white/20 pr-4">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleAgentInvocation(competitor.id, "youtube")}
                          disabled={scanningStates[competitor.id]?.["youtube"] || Object.values(scanningStates[competitor.id] || {}).some(Boolean)}
                          className="flex items-center gap-2 bg-red-500/20 border-red-400/30 text-red-300 hover:bg-red-500/30 hover:border-red-400/50 hover:text-red-200 hover:scale-105 transition-all duration-300 backdrop-blur-sm"
                          title="Analyze YouTube content, channels, and engagement metrics"
                        >
                          <Youtube className="h-4 w-4" />
                          {scanningStates[competitor.id]?.["youtube"] ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                          ) : (
                            "YouTube"
                          )}
                        </Button>
                        
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleAgentInvocation(competitor.id, "browser")}
                          disabled={scanningStates[competitor.id]?.["browser"] || Object.values(scanningStates[competitor.id] || {}).some(Boolean)}
                          className="flex items-center gap-2 bg-blue-500/20 border-blue-400/30 text-blue-300 hover:bg-blue-500/30 hover:border-blue-400/50 hover:text-blue-200 hover:scale-105 transition-all duration-300 backdrop-blur-sm"
                          title="Search web content and analyze online presence"
                        >
                          <Search className="h-4 w-4" />
                          {scanningStates[competitor.id]?.["browser"] ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                          ) : (
                            "Browser"
                          )}
                        </Button>
                        
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleAgentInvocation(competitor.id, "website")}
                          disabled={scanningStates[competitor.id]?.["website"] || Object.values(scanningStates[competitor.id] || {}).some(Boolean)}
                          className="flex items-center gap-2 bg-green-500/20 border-green-400/30 text-green-300 hover:bg-green-500/30 hover:border-green-400/50 hover:text-green-200 hover:scale-105 transition-all duration-300 backdrop-blur-sm"
                          title="Analyze website content, structure, and updates"
                        >
                          <Globe className="h-4 w-4" />
                          {scanningStates[competitor.id]?.["website"] ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                          ) : (
                            "Website"
                          )}
                        </Button>
                      </div>
                      
                      <div className="flex items-center gap-3">
                        <Badge 
                          variant={competitor.status === 'active' ? 'default' : 'secondary'}
                          className={competitor.status === 'active' 
                            ? 'bg-green-500/20 text-green-300 border-green-400/30' 
                            : 'bg-slate-500/20 text-slate-300 border-slate-400/30'
                          }
                        >
                          {competitor.status}
                        </Badge>
                        <CompetitorDetailsDialog
                          competitor={competitor}
                          onCompetitorUpdated={handleCompetitorAdded}
                          onCompetitorDeleted={handleCompetitorAdded}
                          trigger={
                            <Button 
                              variant="outline" 
                              size="sm"
                              className="bg-white/10 border-white/20 text-white hover:bg-white/20 hover:border-white/30 hover:scale-105 transition-all duration-300 backdrop-blur-sm"
                            >
                              <Eye className="h-4 w-4 mr-2" />
                              View Details
                            </Button>
                          }
                        />
                      </div>
                    </div>
                  </div>
                  
                  {/* Animated border on hover */}
                  <div className="absolute inset-0 rounded-xl border-2 border-transparent group-hover:border-blue-400/30 transition-all duration-500"></div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-slate-300">
              <div className="relative">
                <Users className="h-20 w-20 mx-auto mb-6 opacity-50" />
                <div className="absolute inset-0 h-20 w-20 mx-auto bg-blue-500/20 rounded-full animate-ping"></div>
              </div>
              <p className="text-xl font-medium mb-2">No competitors found</p>
              <p className="text-sm text-slate-400">Try adjusting your search or filters, or add a new competitor to get started</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Investigation Tabs */}
      <Tabs defaultValue="overview" className={`space-y-8 transition-all duration-1000 delay-600 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'}`}>
        <TabsList className="grid w-full grid-cols-4 bg-slate-800/25 backdrop-blur-xl border-slate-600/30 h-12 shadow-md">
          <TabsTrigger 
            value="overview" 
            className="text-white data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-600 data-[state=active]:to-purple-600 data-[state=active]:text-white transition-all duration-300 hover:bg-white/20"
          >
            <BarChart3 className="h-4 w-4 mr-2" />
            Overview
          </TabsTrigger>
          <TabsTrigger 
            value="performance" 
            className="text-white data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-600 data-[state=active]:to-purple-600 data-[state=active]:text-white transition-all duration-300 hover:bg-white/20"
          >
            <TrendingUp className="h-4 w-4 mr-2" />
            Performance
          </TabsTrigger>
          <TabsTrigger 
            value="gaps" 
            className="text-white data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-600 data-[state=active]:to-purple-600 data-[state=active]:text-white transition-all duration-300 hover:bg-white/20"
          >
            <Target className="h-4 w-4 mr-2" />
            Content Gaps
          </TabsTrigger>
          <TabsTrigger 
            value="monitoring" 
            className="text-white data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-600 data-[state=active]:to-purple-600 data-[state=active]:text-white transition-all duration-300 hover:bg-white/20"
          >
            <Activity className="h-4 w-4 mr-2" />
            Monitoring
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <CompetitorOverview 
            timeRange={timeRange} 
            monitoringData={monitoringData}
          />
        </TabsContent>

        <TabsContent value="performance" className="space-y-6">
          <CompetitorPerformance 
            timeRange={timeRange} 
            monitoringData={monitoringData}
          />
        </TabsContent>

        <TabsContent value="gaps" className="space-y-6">
          <ContentGapAnalysis 
            monitoringData={monitoringData}
          />
        </TabsContent>

        <TabsContent value="monitoring" className="space-y-6">
          <SocialMediaMonitoring 
            monitoringData={monitoringData}
          />
        </TabsContent>
      </Tabs>

      {/* Add Competitor Modal */}
      <AddCompetitorModal 
        isOpen={showAddModal} 
        onClose={() => setShowAddModal(false)}
        onCompetitorAdded={handleCompetitorAdded} 
      />
      </div>
    </div>
  )
}
