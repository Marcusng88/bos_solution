"use client"

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
  RefreshCw
} from "lucide-react"

export function CompetitorInvestigationDashboard() {
  const [competitors, setCompetitors] = useState<Competitor[]>([])
  const [monitoringData, setMonitoringData] = useState<MonitoringData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [timeRange, setTimeRange] = useState("7d")
  const [selectedIndustry, setSelectedIndustry] = useState("all")
  const [showAddModal, setShowAddModal] = useState(false)
  const [selectedCompetitor, setSelectedCompetitor] = useState<Competitor | null>(null)
  const [showDetailsDialog, setShowDetailsDialog] = useState(false)
  const { user, isLoaded } = useUser()

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
            platforms: ["youtube", "website"],
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            scan_frequency_minutes: 60,
            user_id: "demo-user-1"
          },
          {
            id: "demo-2", 
            name: "Demo Competitor 2",
            industry: "E-commerce",
            status: "active",
            platforms: ["instagram", "facebook"],
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            scan_frequency_minutes: 60,
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
          platforms: ["youtube", "website"],
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          scan_frequency_minutes: 60,
          user_id: "demo-user-1"
        },
        {
          id: "demo-2",
          name: "Demo Competitor 2", 
          industry: "E-commerce",
          status: "active",
          platforms: ["instagram", "facebook"],
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          scan_frequency_minutes: 60,
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

  // Handle competitor details dialog close
  const handleDetailsDialogClose = () => {
    setShowDetailsDialog(false)
    setSelectedCompetitor(null)
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
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading investigation data...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Competitor Investigation</h2>
          <p className="text-muted-foreground">
            Deep dive into competitor strategies and performance
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" size="sm" onClick={refreshData}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh Data
          </Button>
          <Button onClick={() => setShowAddModal(true)} className="bg-primary hover:bg-primary/90">
            <Users className="h-4 w-4 mr-2" />
            Add Competitor
          </Button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <Card className="border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-950/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-800 dark:text-red-200">
              <AlertTriangle className="h-5 w-5" />
              API Connection Issue
            </CardTitle>
            <CardDescription className="text-red-700 dark:text-red-300">
              {error} - Showing demo data for development purposes
            </CardDescription>
          </CardHeader>
        </Card>
      )}


      {/* Filters */}
      <div className="flex items-center gap-4">
        <Select value={selectedIndustry} onValueChange={setSelectedIndustry}>
          <SelectTrigger className="w-40">
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
      <Card>
        <CardHeader>
          <CardTitle>Competitors ({filteredCompetitors.length})</CardTitle>
          <CardDescription>
            Active competitors being monitored
          </CardDescription>
        </CardHeader>
        <CardContent>
          {filteredCompetitors.length > 0 ? (
            <div className="space-y-4">
              {filteredCompetitors.map((competitor) => (
                <div
                  key={competitor.id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                      <span className="font-semibold text-primary">
                        {competitor.name.slice(0, 2).toUpperCase()}
                      </span>
                    </div>
                    <div>
                      <h3 className="font-medium">{competitor.name}</h3>
                      <p className="text-sm text-muted-foreground">{competitor.industry}</p>
                      <div className="flex items-center gap-2 mt-1">
                        {(competitor.platforms || []).map((platform) => (
                          <Badge key={platform} variant="secondary" className="text-xs">
                            {platform}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant={competitor.status === 'active' ? 'default' : 'secondary'}>
                      {competitor.status}
                    </Badge>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => {
                        setSelectedCompetitor(competitor)
                        setShowDetailsDialog(true)
                      }}
                    >
                      View Details
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <Users className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p className="text-lg font-medium">No competitors found</p>
              <p className="text-sm">Try adjusting your search or filters</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Investigation Tabs */}
      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="gaps">Content Gaps</TabsTrigger>
          <TabsTrigger value="monitoring">Monitoring</TabsTrigger>
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

      {/* Competitor Details Dialog */}
      {selectedCompetitor && showDetailsDialog && (
        <CompetitorDetailsDialog
          competitor={selectedCompetitor}
          onCompetitorUpdated={handleCompetitorAdded}
        />
      )}

      {/* Add Competitor Modal */}
      <AddCompetitorModal 
        isOpen={showAddModal} 
        onClose={() => setShowAddModal(false)}
        onCompetitorAdded={handleCompetitorAdded} 
      />
    </div>
  )
}
