"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { useEffect, useState } from "react"
import { useUser } from "@clerk/nextjs"
import { roiApi, type TimeRange } from "@/lib/api-client"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { RevenueOverview } from "./revenue-overview"
import { CostAnalysis } from "./cost-analysis"
import { ProfitabilityMetrics } from "./profitability-metrics"
import { ROITrends } from "./roi-trends"
import { ChannelPerformance } from "./channel-performance"
import { ReportGenerator } from "./report-generator"
import { TrendingUp, TrendingDown, DollarSign, Target, BarChart3, Download, FileText } from "lucide-react"

export function ROIDashboard() {
  const { user } = useUser()
  const [range, setRange] = useState<TimeRange>("30d")
  const [overview, setOverview] = useState<any>(null)
  const [showReportGenerator, setShowReportGenerator] = useState(false)

  useEffect(() => {
    if (!user) return
    roiApi.overview(user.id, range).then(setOverview).catch(() => setOverview(null))
  }, [user, range])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">ROI Dashboard</h1>
          <p className="text-muted-foreground">Track your marketing return on investment and key metrics</p>
        </div>
        <div className="flex items-center gap-2">
          <Select value={range} onValueChange={(v) => setRange(v as TimeRange)}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7d">Last 7 days</SelectItem>
              <SelectItem value="30d">Last 30 days</SelectItem>
              <SelectItem value="90d">Last 90 days</SelectItem>
              <SelectItem value="1y">Last year</SelectItem>
            </SelectContent>
          </Select>
          <div className="flex items-center gap-2">
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => setShowReportGenerator(!showReportGenerator)}
            >
              <FileText className="h-4 w-4 mr-2" />
              {showReportGenerator ? "Hide Report" : "Generate Report"}
            </Button>
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => window.open('/dashboard/roi/reports', '_blank')}
            >
              <Download className="h-4 w-4 mr-2" />
              Full Report
            </Button>
          </div>
        </div>
      </div>

      {/* Report Generator */}
      {showReportGenerator && (
        <div className="mb-6">
          <ReportGenerator />
        </div>
      )}

      {/* Key Metrics Overview */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="bg-gradient-to-br from-emerald-50 to-emerald-100 border-emerald-200 hover:shadow-lg transition-all duration-300">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-emerald-800">Total ROI</CardTitle>
            <div className="p-2 bg-emerald-200 rounded-full">
              <DollarSign className="h-4 w-4 text-emerald-700" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-emerald-700">{overview ? `${Math.round(overview.total_roi || 0)}%` : "--"}</div>
            <div className="flex items-center text-xs text-emerald-600 mt-2">
              <TrendingUp className="h-3 w-3 mr-1" />
              +12% from last month
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200 hover:shadow-lg transition-all duration-300">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-blue-800">Revenue Generated</CardTitle>
            <div className="p-2 bg-blue-200 rounded-full">
              <BarChart3 className="h-4 w-4 text-blue-700" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-blue-700">{overview ? `$${Math.round(overview.total_revenue || 0).toLocaleString()}` : "--"}</div>
            <div className="flex items-center text-xs text-blue-600 mt-2">
              <TrendingUp className="h-3 w-3 mr-1" />
              +18% from last month
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200 hover:shadow-lg transition-all duration-300">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-orange-800">Total Ad Spend</CardTitle>
            <div className="p-2 bg-orange-200 rounded-full">
              <Target className="h-4 w-4 text-orange-700" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-orange-700">{overview ? `$${Math.round(overview.total_spend || 0).toLocaleString()}` : "--"}</div>
            <div className="flex items-center text-xs text-orange-600 mt-2">
              <TrendingDown className="h-3 w-3 mr-1" />
              -5% from last month
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200 hover:shadow-lg transition-all duration-300">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-purple-800">Profit Margin</CardTitle>
            <div className="p-2 bg-purple-200 rounded-full">
              <TrendingUp className="h-4 w-4 text-purple-700" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-purple-700">{overview ? `${Math.round(((overview.total_revenue || 0) - (overview.total_spend || 0)) / Math.max(overview.total_revenue || 1, 1) * 100)}%` : "--"}</div>
            <div className="flex items-center text-xs text-purple-600 mt-2">
              <TrendingUp className="h-3 w-3 mr-1" />
              +3.2% from last month
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Dashboard Content */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="revenue">Revenue</TabsTrigger>
          <TabsTrigger value="costs">Costs</TabsTrigger>
          <TabsTrigger value="profitability">Profitability</TabsTrigger>
          <TabsTrigger value="channels">Channels</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 lg:grid-cols-2">
            <ROITrends range={range} />
            <ChannelPerformance range={range} />
          </div>
          <ProfitabilityMetrics range={range} />
        </TabsContent>

        <TabsContent value="revenue" className="space-y-4">
          <RevenueOverview range={range} />
        </TabsContent>

        <TabsContent value="costs" className="space-y-4">
          <CostAnalysis range={range} />
        </TabsContent>

        <TabsContent value="profitability" className="space-y-4">
          <ProfitabilityMetrics range={range} />
        </TabsContent>

        <TabsContent value="channels" className="space-y-4">
          <ChannelPerformance range={range} />
        </TabsContent>
      </Tabs>
    </div>
  )
}
