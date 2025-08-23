"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Skeleton } from "@/components/ui/skeleton"
import { ContentCalendar } from "./content-calendar"
import { AISuggestionsPanel } from "./ai-suggestions-panel"
import { CompetitorGapSuggestions } from "./competitor-gap-suggestions"
import { ContentStrategyInsights } from "./content-strategy-insights"
import { AIContentGenerator } from "./ai-content-generator"
import { Plus, Calendar, Sparkles, Search, Target, AlertTriangle, Settings, RefreshCw } from "lucide-react"
import { useContentPlanning } from "@/hooks/use-content-planning"

export function ContentPlanningDashboard() {
  const [selectedDate, setSelectedDate] = useState<Date>(new Date())
  const {
    dashboardData,
    supportedOptions,
    loading,
    error,
    selectedIndustry,
    changeIndustry,
    refreshData,
    isReady
  } = useContentPlanning({ 
    autoLoad: true // This only loads basic dashboard data, not AI agent
  })

  return (
    <div className="space-y-6 overflow-hidden w-full max-w-full content-container">{/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">AI Content Planning</h1>
          <p className="text-muted-foreground">Competitor-driven content strategy with AI assistance</p>
        </div>
        <div className="flex items-center gap-3">
          {/* Industry Selector */}
          {supportedOptions && (
            <Select value={selectedIndustry} onValueChange={changeIndustry}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Select Industry" />
              </SelectTrigger>
              <SelectContent>
                {supportedOptions.industries.map((industry) => (
                  <SelectItem key={industry} value={industry}>
                    {industry.charAt(0).toUpperCase() + industry.slice(1)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
          
          <Button 
            variant="outline" 
            onClick={refreshData} 
            disabled={loading}
          >
            <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          
          <Button variant="outline" asChild>
            <Link href="/dashboard/settings">
              <Settings className="mr-2 h-4 w-4" />
              Settings
            </Link>
          </Button>
          
          {/* AI Content Generator - Only invokes AI agent when clicked */}
          <AIContentGenerator
            trigger={
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Create Content
              </Button>
            }
          />
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Scheduled Posts</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {loading || !dashboardData ? (
              <div className="space-y-2">
                <Skeleton className="h-8 w-12" />
                <Skeleton className="h-4 w-24" />
              </div>
            ) : (
              <>
                <div className="text-2xl font-bold">{dashboardData.summary.scheduled_posts}</div>
                <p className="text-xs text-muted-foreground">AI-optimized schedule</p>
              </>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Gap Opportunities</CardTitle>
            <Search className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {loading || !dashboardData ? (
              <div className="space-y-2">
                <Skeleton className="h-8 w-12" />
                <Skeleton className="h-4 w-32" />
              </div>
            ) : (
              <>
                <div className="text-2xl font-bold">{dashboardData.summary.gap_opportunities}</div>
                <p className="text-xs text-muted-foreground">High-impact content gaps</p>
              </>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Competitive Edge</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {loading || !dashboardData ? (
              <div className="space-y-2">
                <Skeleton className="h-8 w-16" />
                <Skeleton className="h-4 w-28" />
              </div>
            ) : (
              <>
                <div className="text-2xl font-bold">{dashboardData.summary.competitive_edge}</div>
                <p className="text-xs text-muted-foreground">vs competitor average</p>
              </>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Threat Alerts</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {loading || !dashboardData ? (
              <div className="space-y-2">
                <Skeleton className="h-8 w-8" />
                <Skeleton className="h-4 w-32" />
              </div>
            ) : (
              <>
                <div className="text-2xl font-bold text-orange-600">{dashboardData.summary.threat_alerts}</div>
                <p className="text-xs text-muted-foreground">Competitor moves to watch</p>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Competitive Intelligence Alert */}
      {dashboardData?.competitive_intelligence?.new_opportunities && 
       Array.isArray(dashboardData.competitive_intelligence.new_opportunities) &&
       dashboardData.competitive_intelligence.new_opportunities.length > 0 && (
        <Card className="border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-950/20">
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              <Sparkles className="h-5 w-5 text-blue-600 mt-0.5" />
              <div className="flex-1">
                <h3 className="font-medium text-blue-900 dark:text-blue-100 mb-1">New Content Opportunities Detected</h3>
                <p className="text-sm text-blue-700 dark:text-blue-300 mb-3">
                  Our AI found {dashboardData?.summary?.gap_opportunities || 0} high-impact content gaps based on competitor analysis. 
                  {dashboardData.competitive_intelligence.new_opportunities.slice(0, 2).map((opp: any, idx: number) => (
                    <span key={idx}> {typeof opp === 'string' ? opp : (opp.description || opp.title || 'New opportunity detected')}.{idx === 0 && ' '}</span>
                  ))}
                </p>
                <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
                  View Opportunities
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Main Content Tabs */}
      <Tabs defaultValue="calendar" className="space-y-6">
        <TabsList>
          <TabsTrigger value="calendar">Content Calendar</TabsTrigger>
          <TabsTrigger value="gaps">Competitor Gaps</TabsTrigger>
          <TabsTrigger value="strategy">Strategy Insights</TabsTrigger>
        </TabsList>

        <TabsContent value="calendar" className="space-y-6">
          <div className="space-y-6 w-full max-w-full overflow-hidden">
            {/* AI Suggestions Panel - Now above the calendar */}
            <div className="w-full">
              <AISuggestionsPanel selectedDate={selectedDate} />
            </div>

            {/* Calendar Section - Now below the suggestions */}
            <div className="w-full">
              <Card className="w-full max-w-full">
                <CardHeader>
                  <CardTitle>Content Calendar</CardTitle>
                  <CardDescription>View and manage your scheduled content across all platforms</CardDescription>
                </CardHeader>
                <CardContent className="overflow-hidden">
                  <ContentCalendar selectedDate={selectedDate} onDateSelect={setSelectedDate} />
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="gaps" className="space-y-6">
          <CompetitorGapSuggestions />
        </TabsContent>

        <TabsContent value="strategy" className="space-y-6">
          <ContentStrategyInsights />
        </TabsContent>
      </Tabs>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>Latest updates on your content and competitive moves</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {loading || !dashboardData ? (
              Array.from({ length: 4 }).map((_, index) => (
                <div key={index} className="flex items-center gap-3 py-2">
                  <Skeleton className="w-2 h-2 rounded-full" />
                  <div className="flex-1 space-y-1">
                    <Skeleton className="h-4 w-48" />
                    <Skeleton className="h-3 w-20" />
                  </div>
                  <Skeleton className="h-6 w-16" />
                </div>
              ))
            ) : (
              dashboardData.recent_activity?.map((activity, index) => (
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
              )) || []
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
