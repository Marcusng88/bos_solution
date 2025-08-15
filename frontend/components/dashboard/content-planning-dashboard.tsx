"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ContentCalendar } from "./content-calendar"
import { AISuggestionsPanel } from "./ai-suggestions-panel"
import { CompetitorGapSuggestions } from "./competitor-gap-suggestions"
import { ContentStrategyInsights } from "./content-strategy-insights"
import { Plus, Calendar, Sparkles, Search, Target, AlertTriangle, Loader2 } from "lucide-react"
import { useApiClient } from "@/lib/api-client"
import { useToast } from "@/hooks/use-toast"

interface DashboardStats {
  scheduled_posts: { value: string; change: string }
  gap_opportunities: { value: string; change: string }
  competitive_edge: { value: string; change: string }
  threat_alerts: { value: string; change: string }
}

interface RecentActivity {
  action: string
  content: string
  time: string
  status: string
}

export function ContentPlanningDashboard() {
  const [selectedDate, setSelectedDate] = useState<Date>(new Date())
  const [dashboardStats, setDashboardStats] = useState<DashboardStats | null>(null)
  const [recentActivities, setRecentActivities] = useState<RecentActivity[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const { apiClient, userId } = useApiClient()
  const { toast } = useToast()

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setIsLoading(true)
      
      // Load dashboard stats and activities in parallel
      const [statsResponse, activitiesResponse] = await Promise.all([
        apiClient.getDashboardStats(userId),
        apiClient.getRecentActivities(userId)
      ])
      
      setDashboardStats(statsResponse as DashboardStats)
      setRecentActivities(activitiesResponse as RecentActivity[])
    } catch (error) {
      console.error('Error loading dashboard data:', error)
      toast({
        title: "Error loading dashboard",
        description: "Failed to load dashboard data. Using fallback data.",
        variant: "destructive"
      })
      
      // Fallback data in case of error
      setDashboardStats({
        scheduled_posts: { value: "24", change: "+3 from last week" },
        gap_opportunities: { value: "8", change: "High-impact content gaps" },
        competitive_edge: { value: "+23%", change: "vs competitor average" },
        threat_alerts: { value: "3", change: "Competitor moves to watch" }
      })
      
      setRecentActivities([
        {
          action: "Gap Identified",
          content: "Video content opportunity vs Nike",
          time: "1 hour ago",
          status: "opportunity"
        },
        {
          action: "AI Generated",
          content: "Summer Sale Campaign - Instagram Post",
          time: "2 hours ago",
          status: "success"
        },
        {
          action: "Competitor Alert",
          content: "Adidas launched sustainability campaign",
          time: "3 hours ago",
          status: "alert"
        },
        {
          action: "Published",
          content: "Weekly Newsletter Content",
          time: "6 hours ago",
          status: "draft"
        }
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const handleCreateContent = async () => {
    try {
      // Trigger AI analysis for new content suggestions
      await apiClient.getAIAnalysis(userId, "content_generation")
      toast({
        title: "AI Analysis Started",
        description: "Generating new content suggestions based on latest competitor insights..."
      })
      
      // Refresh suggestions after a short delay
      setTimeout(() => {
        loadDashboardData()
      }, 2000)
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to generate new content suggestions",
        variant: "destructive"
      })
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">AI Content Planning</h1>
          <p className="text-muted-foreground">Competitor-driven content strategy with AI assistance</p>
        </div>
        <Button onClick={handleCreateContent} disabled={isLoading}>
          {isLoading ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <Plus className="mr-2 h-4 w-4" />
          )}
          Create Content
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Scheduled Posts</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {isLoading ? (
                <Loader2 className="h-6 w-6 animate-spin" />
              ) : (
                dashboardStats?.scheduled_posts.value || "24"
              )}
            </div>
            <p className="text-xs text-muted-foreground">
              {dashboardStats?.scheduled_posts.change || "+3 from last week"}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Gap Opportunities</CardTitle>
            <Search className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {isLoading ? (
                <Loader2 className="h-6 w-6 animate-spin" />
              ) : (
                dashboardStats?.gap_opportunities.value || "8"
              )}
            </div>
            <p className="text-xs text-muted-foreground">
              {dashboardStats?.gap_opportunities.change || "High-impact content gaps"}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Competitive Edge</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {isLoading ? (
                <Loader2 className="h-6 w-6 animate-spin" />
              ) : (
                dashboardStats?.competitive_edge.value || "+23%"
              )}
            </div>
            <p className="text-xs text-muted-foreground">
              {dashboardStats?.competitive_edge.change || "vs competitor average"}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Threat Alerts</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              {isLoading ? (
                <Loader2 className="h-6 w-6 animate-spin" />
              ) : (
                dashboardStats?.threat_alerts.value || "3"
              )}
            </div>
            <p className="text-xs text-muted-foreground">
              {dashboardStats?.threat_alerts.change || "Competitor moves to watch"}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Competitive Intelligence Alert */}
      <Card className="border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-950/20">
        <CardContent className="pt-6">
          <div className="flex items-start gap-3">
            <Sparkles className="h-5 w-5 text-blue-600 mt-0.5" />
            <div className="flex-1">
              <h3 className="font-medium text-blue-900 dark:text-blue-100 mb-1">New Content Opportunities Detected</h3>
              <p className="text-sm text-blue-700 dark:text-blue-300 mb-3">
                Our AI found 3 high-impact content gaps based on competitor analysis. Nike is dominating video content
                while Adidas focuses on sustainability messaging.
              </p>
              <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
                View Opportunities
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Content Tabs */}
      <Tabs defaultValue="calendar" className="space-y-6">
        <TabsList>
          <TabsTrigger value="calendar">Content Calendar</TabsTrigger>
          <TabsTrigger value="gaps">Competitor Gaps</TabsTrigger>
          <TabsTrigger value="strategy">Strategy Insights</TabsTrigger>
        </TabsList>

        <TabsContent value="calendar" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Calendar Section */}
            <div className="lg:col-span-2">
              <Card>
                <CardHeader>
                  <CardTitle>Content Calendar</CardTitle>
                  <CardDescription>View and manage your scheduled content across all platforms</CardDescription>
                </CardHeader>
                <CardContent>
                  <ContentCalendar selectedDate={selectedDate} onDateSelect={setSelectedDate} />
                </CardContent>
              </Card>
            </div>

            {/* AI Suggestions Panel */}
            <div>
              <AISuggestionsPanel selectedDate={selectedDate} userId={userId} />
            </div>
          </div>
        </TabsContent>

        <TabsContent value="gaps" className="space-y-6">
          <CompetitorGapSuggestions userId={userId} />
        </TabsContent>

        <TabsContent value="strategy" className="space-y-6">
          <ContentStrategyInsights userId={userId} />
        </TabsContent>
      </Tabs>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>Latest updates on your content and competitive moves</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin" />
            </div>
          ) : (
            <div className="space-y-4">
              {recentActivities.map((activity, index) => (
                <div key={index} className="flex items-center justify-between py-2">
                  <div className="flex items-center gap-3">
                    <div
                      className={`w-2 h-2 rounded-full ${
                        activity.status === "success"
                          ? "bg-green-500"
                          : activity.status === "opportunity"
                            ? "bg-blue-500"
                            : activity.status === "alert"
                              ? "bg-orange-500"
                              : "bg-gray-500"
                      }`}
                    />
                    <div>
                      <p className="text-sm font-medium">
                        {activity.action} <span className="text-muted-foreground">{activity.content}</span>
                      </p>
                      <p className="text-xs text-muted-foreground">{activity.time}</p>
                    </div>
                  </div>
                  <Badge
                    variant={
                      activity.status === "success"
                        ? "default"
                        : activity.status === "opportunity"
                          ? "secondary"
                          : activity.status === "alert"
                            ? "destructive"
                            : "outline"
                    }
                  >
                    {activity.status}
                  </Badge>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
