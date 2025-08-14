"use client"

import { useState } from "react"
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
import { Search, TrendingUp, AlertTriangle, Eye, RefreshCw, Plus } from "lucide-react"

export function CompetitorInvestigationDashboard() {
  const [timeRange, setTimeRange] = useState("30d")
  const [selectedCompetitor, setSelectedCompetitor] = useState("all")
  const [isScanning, setIsScanning] = useState(false)

  const competitors = [
    { name: "Nike", status: "active", lastScan: "2 hours ago", threats: 3 },
    { name: "Adidas", status: "active", lastScan: "4 hours ago", threats: 1 },
    { name: "Under Armour", status: "active", lastScan: "6 hours ago", threats: 2 },
  ]

  const startScan = () => {
    setIsScanning(true)
    setTimeout(() => setIsScanning(false), 3000)
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
          <Button onClick={startScan} disabled={isScanning}>
            <RefreshCw className={`mr-2 h-4 w-4 ${isScanning ? "animate-spin" : ""}`} />
            {isScanning ? "Scanning..." : "Scan Now"}
          </Button>
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Add Competitor
          </Button>
        </div>
      </div>

      {/* Scanning Progress */}
      {isScanning && (
        <Card className="border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-950/20">
          <CardContent className="pt-6">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-blue-900 dark:text-blue-100">
                  AI Competitor Analysis in Progress
                </span>
                <span className="text-sm text-blue-700 dark:text-blue-300">67%</span>
              </div>
              <Progress value={67} className="h-2" />
              <div className="text-xs text-blue-600 dark:text-blue-400">
                Analyzing social media activity, content strategies, and engagement patterns...
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
            <div className="text-2xl font-bold">{competitors.length}</div>
            <p className="text-xs text-muted-foreground">All actively monitored</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Content Gaps Found</CardTitle>
            <Search className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">12</div>
            <p className="text-xs text-muted-foreground">+3 new opportunities</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Threat Alerts</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">6</div>
            <p className="text-xs text-muted-foreground">Requires attention</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Share of Voice</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">23.4%</div>
            <p className="text-xs text-muted-foreground">+2.1% vs competitors</p>
          </CardContent>
        </Card>
      </div>

      {/* Competitor Status Overview */}
      <Card>
        <CardHeader>
          <CardTitle>Competitor Status</CardTitle>
          <CardDescription>Real-time monitoring status and recent activity</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {competitors.map((competitor, index) => (
              <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 bg-gray-100 dark:bg-gray-800 rounded-lg flex items-center justify-center">
                    <span className="font-semibold text-sm">{competitor.name.slice(0, 2)}</span>
                  </div>
                  <div>
                    <h3 className="font-medium">{competitor.name}</h3>
                    <p className="text-sm text-muted-foreground">Last scan: {competitor.lastScan}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Badge
                    variant={competitor.threats > 2 ? "destructive" : competitor.threats > 0 ? "secondary" : "default"}
                  >
                    {competitor.threats} threats
                  </Badge>
                  <Badge variant="outline" className="text-green-600 border-green-600">
                    {competitor.status}
                  </Badge>
                  <Button variant="ghost" size="sm">
                    View Details
                  </Button>
                </div>
              </div>
            ))}
          </div>
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
          <CompetitorOverview timeRange={timeRange} />
        </TabsContent>

        <TabsContent value="content-gaps" className="space-y-6">
          <ContentGapAnalysis />
        </TabsContent>

        <TabsContent value="social-monitoring" className="space-y-6">
          <SocialMediaMonitoring />
        </TabsContent>

        <TabsContent value="performance" className="space-y-6">
          <CompetitorPerformance timeRange={timeRange} />
        </TabsContent>
      </Tabs>
    </div>
  )
}
