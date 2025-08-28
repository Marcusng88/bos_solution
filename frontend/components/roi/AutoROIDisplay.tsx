"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from "recharts"
import { useEffect, useState } from "react"
import { useUser } from "@clerk/nextjs"
import { roiApi, type TimeRange } from "@/lib/api-client"
import { TrendingUp, TrendingDown, DollarSign, Target, Eye, ThumbsUp, MessageCircle, Share2, MousePointer } from "lucide-react"

interface AutoROIMetrics {
  platform: string
  impressions: number
  engagement: number
  revenue: number
  spend: number
  avg_roi: number
  avg_roas: number
  posts: number
  total_clicks: number
  profit: number
  engagement_rate: number
  click_through_rate: number
  efficiency_score: number
}

export function AutoROIDisplay() {
  const { user } = useUser()
  const [range, setRange] = useState<TimeRange>("7d")
  const [metrics, setMetrics] = useState<AutoROIMetrics[]>([])
  const [loading, setLoading] = useState(true)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)

  useEffect(() => {
    if (!user) return
    
    const fetchMetrics = async () => {
      try {
        setLoading(true)
        // Get channel performance data which includes the latest metrics
        const response = await roiApi.channelPerformance(range)
        setMetrics(response.rows || [])
        setLastUpdate(new Date())
      } catch (error) {
        console.error('Failed to fetch auto ROI metrics:', error)
        setMetrics([])
      } finally {
        setLoading(false)
      }
    }

    fetchMetrics()
    
    // Auto-refresh every 5 minutes
    const interval = setInterval(fetchMetrics, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [user, range])

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
            Loading Auto ROI Data...
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="h-4 bg-gray-200 rounded animate-pulse"></div>
            <div className="h-4 bg-gray-200 rounded animate-pulse w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded animate-pulse w-1/2"></div>
          </div>
        </CardContent>
      </Card>
    )
  }

  const totalMetrics = metrics.reduce(
    (acc, m) => ({
      impressions: acc.impressions + (m.impressions || 0),
      engagement: acc.engagement + (m.engagement || 0),
      revenue: acc.revenue + (m.revenue || 0),
      spend: acc.spend + (m.spend || 0),
      roi: acc.roi + (m.avg_roi || 0),
    }),
    { impressions: 0, engagement: 0, revenue: 0, spend: 0, roi: 0 }
  )

  const avgROI = metrics.length > 0 ? totalMetrics.roi / metrics.length : 0
  const profit = totalMetrics.revenue - totalMetrics.spend
  const engagementRate = totalMetrics.impressions > 0 ? (totalMetrics.engagement / totalMetrics.impressions) * 100 : 0

  const platformColors: Record<string, string> = {
    facebook: "#1877F2",
    instagram: "#E4405F", 
    youtube: "#FF0000",
    twitter: "#1DA1F2",
    linkedin: "#0077B5"
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
              Auto ROI Analytics
            </div>
            <div className="text-sm text-muted-foreground">
              Last updated: {lastUpdate?.toLocaleTimeString()}
            </div>
          </CardTitle>
          <CardDescription>
            Real-time ROI metrics automatically generated from your social media performance
          </CardDescription>
        </CardHeader>
      </Card>

      {/* Key Metrics Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average ROI</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${avgROI >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {avgROI.toFixed(1)}%
            </div>
            <div className="flex items-center text-xs text-muted-foreground">
              {avgROI >= 0 ? (
                <TrendingUp className="h-3 w-3 mr-1 text-green-500" />
              ) : (
                <TrendingDown className="h-3 w-3 mr-1 text-red-500" />
              )}
              {avgROI >= 100 ? 'Excellent' : avgROI >= 50 ? 'Good' : avgROI >= 0 ? 'Positive' : 'Needs attention'}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${totalMetrics.revenue.toLocaleString()}</div>
            <div className="flex items-center text-xs text-muted-foreground">
              <TrendingUp className="h-3 w-3 mr-1 text-green-500" />
              From {metrics.length} platforms
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Net Profit</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              ${Math.abs(profit).toLocaleString()}
            </div>
            <div className="flex items-center text-xs text-muted-foreground">
              {profit >= 0 ? (
                <TrendingUp className="h-3 w-3 mr-1 text-green-500" />
              ) : (
                <TrendingDown className="h-3 w-3 mr-1 text-red-500" />
              )}
              {profit >= 0 ? 'Profitable' : 'Loss'}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Engagement Rate</CardTitle>
            <ThumbsUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{engagementRate.toFixed(2)}%</div>
            <div className="flex items-center text-xs text-muted-foreground">
              <Eye className="h-3 w-3 mr-1" />
              {totalMetrics.impressions.toLocaleString()} total impressions
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Platform Performance */}
      <Card>
        <CardHeader>
          <CardTitle>Platform Performance</CardTitle>
          <CardDescription>ROI breakdown by social media platform</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {metrics.map((metric, index) => {
              const platformProfit = metric.profit || 0
              const platformROI = metric.avg_roi || 0
              
              return (
                <div key={`${metric.platform}-${index}`} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center gap-3">
                    <div 
                      className="w-4 h-4 rounded"
                      style={{ backgroundColor: platformColors[metric.platform] || "#6B7280" }}
                    ></div>
                    <div>
                      <div className="font-medium capitalize">{metric.platform}</div>
                      <div className="text-sm text-muted-foreground">
                        {(metric.impressions || 0).toLocaleString()} impressions
                      </div>
                    </div>
                  </div>
                  
                  <div className="text-right">
                    <div className={`font-medium ${platformROI >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {platformROI.toFixed(1)}% ROI
                    </div>
                    <div className="text-sm text-muted-foreground">
                      ${Math.abs(platformProfit).toLocaleString()} {platformProfit >= 0 ? 'profit' : 'loss'}
                    </div>
                  </div>
                  
                  <div className="w-24">
                    <Progress 
                      value={Math.min(Math.max(platformROI + 100, 0), 200) / 2} 
                      className="h-2"
                    />
                  </div>
                </div>
              )
            })}
          </div>
          
          {metrics.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              <Target className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No ROI data available yet.</p>
              <p className="text-sm">Start creating content to see your automatic ROI analytics.</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* ROI Trends Chart */}
      {metrics.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>ROI Trends</CardTitle>
            <CardDescription>Platform performance comparison</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={metrics}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="platform" />
                <YAxis />
                <Tooltip 
                  formatter={(value: any, name: string) => [
                    `${Number(value).toFixed(1)}%`, 
                    'ROI'
                  ]}
                />
                <Bar 
                  dataKey="avg_roi" 
                  fill="#3B82F6"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {/* Auto-Update Status */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              Auto-updating every 5 minutes
            </div>
            <Badge variant="outline" className="text-xs">
              Live Data
            </Badge>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
