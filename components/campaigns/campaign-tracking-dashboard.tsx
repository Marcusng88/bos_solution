"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { CampaignOverview } from "./campaign-overview"
import { PerformanceCharts } from "./performance-charts"
import { CampaignList } from "./campaign-list"
import { AISummary } from "./ai-summary"
import { CompetitorBenchmarking } from "./competitor-benchmarking"
import { ShareOfVoiceAnalysis } from "./share-of-voice-analysis"
import { Plus, TrendingUp, DollarSign, MousePointer, Target, AlertTriangle } from "lucide-react"

export function CampaignTrackingDashboard() {
  const [timeRange, setTimeRange] = useState("7d")
  const [selectedCampaign, setSelectedCampaign] = useState("all")

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Performance Tracking</h1>
          <p className="text-muted-foreground">Monitor your performance vs competitors with AI insights</p>
        </div>
        <div className="flex items-center gap-3">
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="24h">Last 24h</SelectItem>
              <SelectItem value="7d">Last 7 days</SelectItem>
              <SelectItem value="30d">Last 30 days</SelectItem>
              <SelectItem value="90d">Last 90 days</SelectItem>
            </SelectContent>
          </Select>
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            New Campaign
          </Button>
        </div>
      </div>

      {/* Key Metrics with Competitor Comparison */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Spend</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">$12,847</div>
            <p className="text-xs text-muted-foreground">+8.2% from last period</p>
            <div className="text-xs text-blue-600 mt-1">15% below Nike avg</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Clicks</CardTitle>
            <MousePointer className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">24,567</div>
            <p className="text-xs text-muted-foreground">+12.5% from last period</p>
            <div className="text-xs text-green-600 mt-1">8% above industry avg</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Conversions</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">1,234</div>
            <p className="text-xs text-muted-foreground">+15.3% from last period</p>
            <div className="text-xs text-green-600 mt-1">12% above Adidas</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Share of Voice</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">18.4%</div>
            <p className="text-xs text-muted-foreground">+2.1% from last period</p>
            <div className="text-xs text-orange-600 mt-1">3rd in category</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Competitive Threats</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">4</div>
            <p className="text-xs text-muted-foreground">Active competitor campaigns</p>
            <div className="text-xs text-red-600 mt-1">Nike launched major push</div>
          </CardContent>
        </Card>
      </div>

      {/* AI Summary with Competitor Context */}
      <AISummary timeRange={timeRange} />

      {/* Main Content */}
      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="benchmarking">Competitor Benchmarking</TabsTrigger>
          <TabsTrigger value="share-of-voice">Share of Voice</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="campaigns">All Campaigns</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <CampaignOverview timeRange={timeRange} />
        </TabsContent>

        <TabsContent value="benchmarking" className="space-y-6">
          <CompetitorBenchmarking timeRange={timeRange} />
        </TabsContent>

        <TabsContent value="share-of-voice" className="space-y-6">
          <ShareOfVoiceAnalysis timeRange={timeRange} />
        </TabsContent>

        <TabsContent value="performance" className="space-y-6">
          <PerformanceCharts timeRange={timeRange} />
        </TabsContent>

        <TabsContent value="campaigns" className="space-y-6">
          <CampaignList />
        </TabsContent>
      </Tabs>
    </div>
  )
}
