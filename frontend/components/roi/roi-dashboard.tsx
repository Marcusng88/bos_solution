"use client"

import { useState, useEffect } from "react"
import { useUser } from "@clerk/nextjs"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { roiApi, type TimeRange } from "@/lib/api-client"
import ROITrends from "./roi-trends"
import ChannelPerformance from "./channel-performance"
import { RevenueOverview } from "./revenue-overview"
import { TrendingUp, TrendingDown, DollarSign, Target, BarChart3, Download, FileText } from "lucide-react"
import { CostAnalysis } from "./cost-analysis"
import { ProfitabilityMetrics } from "./profitability-metrics"
import { ReportGenerator } from "./report-generator"
import PlatformPerformanceTable from "./platform-performance-table"

export default function ROIDashboard() {
  const { user } = useUser()
  const [selectedRange, setSelectedRange] = useState<TimeRange>("7d")
  const [overview, setOverview] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [showReportGenerator, setShowReportGenerator] = useState(false)

  useEffect(() => {
    if (!user) return

    const fetchOverview = async () => {
      try {
        setLoading(true)
        console.log(`🚀 Frontend: Fetching overview for range: ${selectedRange}`)
        
        // Fetch ALL data from backend (no date filtering)
        const response = await roiApi.overview(user.id, selectedRange)
        console.log(`📊 Backend overview response:`, response)
        
        if ('all_data' in response) {
          // Frontend filtering logic - this is the key change!
          const allData = response.all_data
          console.log(`📊 Total rows received: ${allData.length}`)
          
          // Filter data based on the selected range
          const filteredData = filterDataByRange(allData, selectedRange)
          console.log(`📊 Filtered data for ${selectedRange}: ${filteredData.length} rows`)
          
          // Calculate overview metrics from filtered data
          const overviewMetrics = calculateOverviewMetrics(filteredData)
          console.log(`📊 Overview metrics calculated:`, overviewMetrics)
          
          setOverview(overviewMetrics)
        } else {
          console.error('❌ Unexpected overview response format:', response)
          setOverview({})
        }
      } catch (error) {
        console.error('Failed to fetch overview:', error)
        setOverview({})
      } finally {
        setLoading(false)
      }
    }

    fetchOverview()
  }, [user, selectedRange])

  // Frontend filtering function - handles 7d, 30d, 90d logic
  const filterDataByRange = (allData: any[], selectedRange: TimeRange) => {
    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate()) // Start of today
    
    // Calculate start date based on range (exclude today's incomplete data)
    let startDate: Date
    switch (selectedRange) {
      case '7d':
        startDate = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000)
        break
      case '30d':
        startDate = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000)
        break
      case '90d':
        startDate = new Date(today.getTime() - 90 * 24 * 60 * 60 * 1000)
        break
      default:
        startDate = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000)
    }
    
    console.log(`📅 Frontend filtering: ${startDate.toISOString()} to ${today.toISOString()}`)
    
    // Filter data within the range
    return allData.filter(row => {
      const rowDate = new Date(row.created_at)
      return rowDate >= startDate && rowDate < today // Exclude today
    })
  }

  // Calculate overview metrics from filtered data
  const calculateOverviewMetrics = (filteredData: any[]) => {
    if (!filteredData || filteredData.length === 0) {
      return {}
    }
    
    const total_revenue = filteredData.reduce((sum, row) => sum + parseFloat(row.revenue_generated || 0), 0)
    const total_spend = filteredData.reduce((sum, row) => sum + parseFloat(row.ad_spend || 0), 0)
    const total_roi = total_spend > 0 ? ((total_revenue - total_spend) / total_spend) * 100 : 0
    const total_views = filteredData.reduce((sum, row) => sum + parseInt(row.views || 0), 0)
    const total_engagement = filteredData.reduce((sum, row) => 
      sum + parseInt(row.likes || 0) + parseInt(row.comments || 0) + parseInt(row.shares || 0), 0
    )
    
    return {
      total_revenue,
      total_spend,
      total_roi,
      total_views,
      total_engagement
    }
  }

  if (!user) {
    return <div className="text-center py-8">Please sign in to view ROI dashboard</div>
  }

  return (
    <div className="space-y-6">
      {/* Header with Time Range Selector and Report Generator */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">ROI Dashboard</h1>
          <p className="text-muted-foreground">Track your marketing return on investment and key metrics</p>
        </div>
        <div className="flex items-center gap-2">
          <Select value={selectedRange} onValueChange={(value: TimeRange) => setSelectedRange(value)}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7d">Last 7 days</SelectItem>
              <SelectItem value="30d">Last 30 days</SelectItem>
              <SelectItem value="90d">Last 90 days</SelectItem>
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
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => window.open('/dashboard/roi/platform-performance', '_blank')}
            >
              <BarChart3 className="h-4 w-4 mr-2" />
              Platform Performance
            </Button>
          </div>
        </div>
      </div>

             {/* Report Generator */}
       {showReportGenerator && (
         <div className="mb-6 p-4 bg-muted rounded-lg">
           <ReportGenerator />
         </div>
       )}

      {/* Overview Metrics Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="bg-gradient-to-br from-emerald-50 to-emerald-100 border-emerald-200 hover:shadow-lg transition-all duration-300">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-emerald-800">Total ROI</CardTitle>
            <div className="p-2 bg-emerald-200 rounded-full">
              <DollarSign className="h-4 w-4 text-emerald-700" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-emerald-700">
              {loading ? "..." : overview?.total_roi ? `${Math.round(overview.total_roi || 0)}%` : "--"}
            </div>
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
            <div className="text-3xl font-bold text-blue-700">
              {loading ? "..." : overview?.total_revenue ? `$${overview.total_revenue.toLocaleString()}` : "--"}
            </div>
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
            <div className="text-3xl font-bold text-orange-700">
              {loading ? "..." : overview?.total_spend ? `$${overview.total_spend.toLocaleString()}` : "--"}
            </div>
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
            <div className="text-3xl font-bold text-purple-700">
              {loading ? "..." : overview?.total_revenue && overview?.total_spend ? 
                `$${(overview.total_revenue - overview.total_spend).toLocaleString()}` : "--"}
            </div>
            <div className="flex items-center text-xs text-purple-600 mt-2">
              <TrendingUp className="h-3 w-3 mr-1" />
              +3.2% from last month
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Dashboard Content with Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="platforms">Platform Performance</TabsTrigger>
          <TabsTrigger value="revenue">Revenue</TabsTrigger>
          <TabsTrigger value="costs">Costs</TabsTrigger>
          <TabsTrigger value="profitability">Profitability</TabsTrigger>
        </TabsList>

                 <TabsContent value="overview" className="space-y-4">
           <div className="grid gap-4 lg:grid-cols-2">
             <ROITrends userId={user.id} range={selectedRange} />
             <ChannelPerformance userId={user.id} range={selectedRange} />
           </div>
         </TabsContent>

                 <TabsContent value="platforms" className="space-y-4">
           <PlatformPerformanceTable range={selectedRange} />
         </TabsContent>

        <TabsContent value="revenue" className="space-y-4">
          <RevenueOverview range={selectedRange} />
        </TabsContent>

        <TabsContent value="costs" className="space-y-4">
          <CostAnalysis range={selectedRange} />
        </TabsContent>

        <TabsContent value="profitability" className="space-y-4">
          <ProfitabilityMetrics range={selectedRange} />
        </TabsContent>
      </Tabs>
    </div>
  )
}
