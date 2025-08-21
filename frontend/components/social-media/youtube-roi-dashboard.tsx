"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, Area, AreaChart
} from "recharts"
import { 
  DollarSign, Eye, Heart, MessageCircle, TrendingUp, TrendingDown, 
  Users, Clock, Target, ThumbsUp, Share2, Play, BarChart3, AlertCircle
} from "lucide-react"
import { useYouTubeStore } from '@/hooks/use-youtube'

interface ROIAnalytics {
  channel_overview: {
    channel_title: string
    total_subscribers: number
    total_videos: number
    total_views: number
    subscriber_growth_rate: number
  }
  performance_metrics: {
    total_views_period: number
    total_likes_period: number
    total_comments_period: number
    total_watch_time_hours: number
    videos_analyzed: number
    avg_engagement_rate: number
    top_performing_video: {
      title: string
      video_id: string
      roi_score: number
      engagement_rate: number
    } | null
  }
  engagement_analytics: {
    likes_to_views_ratio: number
    comments_to_views_ratio: number
    subscriber_conversion_rate: number
  }
  content_insights: {
    optimal_video_length: number
    best_performing_tags: Array<{tag: string, count: number}>
  }
  revenue_estimates?: {
    estimated_monthly_revenue: number
    estimated_annual_revenue: number
    revenue_per_subscriber: number
    estimated_rpm: number
  }
  roi_recommendations: Array<{
    priority: string
    category: string
    recommendation: string
    expected_impact: string
  }>
}

interface VideoPerformance {
  video_id: string
  title: string
  views: number
  likes: number
  comments: number
  engagement_rate: number
  watch_time_hours: number
  roi_score: number
}

export function YouTubeROIDashboard() {
  const [analytics, setAnalytics] = useState<ROIAnalytics | null>(null)
  const [videoPerformances, setVideoPerformances] = useState<VideoPerformance[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [daysBack, setDaysBack] = useState(7)
  const [includeRevenue, setIncludeRevenue] = useState(true)
  
  const { isConnected, getROIAnalytics, connect } = useYouTubeStore()

  const fetchROIAnalytics = async () => {
    if (!isConnected) {
      setError('Not connected to YouTube')
      return
    }

    setLoading(true)
    setError(null)
    
    try {
      const result = await getROIAnalytics(daysBack, includeRevenue)
      
      if (result.success) {
        setAnalytics(result.roi_analytics)
        setVideoPerformances(result.video_performances || [])
      } else {
        setError(result.error || 'Failed to fetch ROI analytics')
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (isConnected) {
      fetchROIAnalytics()
    }
  }, [isConnected, daysBack, includeRevenue])

  const formatNumber = (num: number) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
    return num.toString()
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(amount)
  }

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'high': return 'destructive'
      case 'medium': return 'default'
      case 'low': return 'secondary'
      default: return 'outline'
    }
  }

  const getEngagementColor = (rate: number) => {
    if (rate >= 4) return 'text-green-600'
    if (rate >= 2) return 'text-yellow-600'
    return 'text-red-600'
  }

  if (!isConnected) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-red-500" />
            YouTube ROI Dashboard
          </CardTitle>
          <CardDescription>
            Comprehensive analytics and ROI insights for your YouTube channel
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-6">
            <p className="text-muted-foreground mb-4">
              Connect your YouTube account to view detailed ROI analytics
            </p>
            <Button onClick={connect} className="flex items-center gap-2">
              <Play className="h-4 w-4" />
              Connect YouTube
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header Controls */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-red-500" />
            YouTube ROI Dashboard
            {analytics?.channel_overview.channel_title && (
              <Badge variant="outline">{analytics.channel_overview.channel_title}</Badge>
            )}
          </CardTitle>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <label className="text-sm">Analysis Period:</label>
              <select 
                value={daysBack} 
                onChange={(e) => setDaysBack(Number(e.target.value))}
                className="px-3 py-1 border rounded-md text-sm"
              >
                <option value={1}>Last 1 day</option>
                <option value={7}>Last 7 days</option>
                <option value={14}>Last 14 days</option>
                <option value={30}>Last 30 days</option>
                <option value={90}>Last 90 days</option>
              </select>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={includeRevenue}
                onChange={(e) => setIncludeRevenue(e.target.checked)}
                id="include-revenue"
              />
              <label htmlFor="include-revenue" className="text-sm">Include Revenue Estimates</label>
            </div>
            <Button 
              onClick={fetchROIAnalytics} 
              disabled={loading}
              size="sm"
            >
              {loading ? 'Loading...' : 'Refresh Data'}
            </Button>
          </div>
        </CardHeader>
      </Card>

      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-red-700">
              <AlertCircle className="h-4 w-4" />
              <p>{error}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {loading && (
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          </CardContent>
        </Card>
      )}

      {analytics && !loading && (
        <Tabs defaultValue="overview" className="space-y-4">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="performance">Performance</TabsTrigger>
            <TabsTrigger value="engagement">Engagement</TabsTrigger>
            <TabsTrigger value="content">Content Insights</TabsTrigger>
            <TabsTrigger value="revenue">Revenue</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              {/* Key Metrics Cards */}
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Subscribers</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {formatNumber(analytics.channel_overview.total_subscribers)}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Across {analytics.channel_overview.total_videos} videos
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Period Views</CardTitle>
                  <Eye className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {formatNumber(analytics.performance_metrics.total_views_period)}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Last {daysBack} days
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Avg Engagement</CardTitle>
                  <Heart className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className={`text-2xl font-bold ${getEngagementColor(analytics.performance_metrics.avg_engagement_rate)}`}>
                    {analytics.performance_metrics.avg_engagement_rate}%
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {analytics.performance_metrics.videos_analyzed} videos analyzed
                  </p>
                </CardContent>
              </Card>

              {analytics.revenue_estimates && (
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Est. Monthly Revenue</CardTitle>
                    <DollarSign className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-green-600">
                      {formatCurrency(analytics.revenue_estimates.estimated_monthly_revenue)}
                    </div>
                    <p className="text-xs text-muted-foreground">
                      RPM: ${analytics.revenue_estimates.estimated_rpm}
                    </p>
                  </CardContent>
                </Card>
              )}
            </div>

            {/* Top Performing Video */}
            {analytics.performance_metrics.top_performing_video && (
              <Card className="mt-6">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Target className="h-4 w-4" />
                    Top Performing Video (Period)
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium line-clamp-1">
                        {analytics.performance_metrics.top_performing_video.title}
                      </h4>
                      <p className="text-sm text-muted-foreground">
                        Engagement Rate: {analytics.performance_metrics.top_performing_video.engagement_rate}%
                      </p>
                    </div>
                    <Badge variant="secondary">
                      ROI Score: {analytics.performance_metrics.top_performing_video.roi_score.toFixed(1)}
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* ROI Recommendations */}
            {analytics.roi_recommendations.length > 0 && (
              <Card className="mt-6">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-4 w-4" />
                    ROI Recommendations
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {analytics.roi_recommendations.map((rec, index) => (
                      <div key={index} className="border-l-4 border-blue-500 pl-4">
                        <div className="flex items-center gap-2 mb-1">
                          <Badge variant={getPriorityColor(rec.priority) as any}>
                            {rec.priority} Priority
                          </Badge>
                          <Badge variant="outline">{rec.category}</Badge>
                        </div>
                        <p className="text-sm font-medium mb-1">{rec.recommendation}</p>
                        <p className="text-xs text-green-600">Expected Impact: {rec.expected_impact}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Performance Tab */}
          <TabsContent value="performance">
            <div className="grid gap-4 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Video Performance Metrics</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Total Watch Time</span>
                      <span className="font-medium">
                        {analytics.performance_metrics.total_watch_time_hours.toFixed(1)} hours
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Total Likes</span>
                      <span className="font-medium">
                        {formatNumber(analytics.performance_metrics.total_likes_period)}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Total Comments</span>
                      <span className="font-medium">
                        {formatNumber(analytics.performance_metrics.total_comments_period)}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {videoPerformances.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Top Videos by ROI Score</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {videoPerformances.slice(0, 5).map((video, index) => (
                        <div key={video.video_id} className="flex items-center justify-between">
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium truncate">{video.title}</p>
                            <p className="text-xs text-muted-foreground">
                              {formatNumber(video.views)} views • {video.engagement_rate.toFixed(1)}% engagement
                            </p>
                          </div>
                          <Badge variant="outline">
                            {video.roi_score.toFixed(1)}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          {/* Engagement Tab */}
          <TabsContent value="engagement">
            <div className="grid gap-4 md:grid-cols-3">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Likes-to-Views Ratio</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {analytics.engagement_analytics.likes_to_views_ratio.toFixed(3)}%
                  </div>
                  <Progress 
                    value={analytics.engagement_analytics.likes_to_views_ratio * 20} 
                    className="mt-2"
                  />
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Comments-to-Views Ratio</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {analytics.engagement_analytics.comments_to_views_ratio.toFixed(3)}%
                  </div>
                  <Progress 
                    value={analytics.engagement_analytics.comments_to_views_ratio * 100} 
                    className="mt-2"
                  />
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Avg Engagement Rate</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className={`text-2xl font-bold ${getEngagementColor(analytics.performance_metrics.avg_engagement_rate)}`}>
                    {analytics.performance_metrics.avg_engagement_rate}%
                  </div>
                  <Progress 
                    value={analytics.performance_metrics.avg_engagement_rate * 10} 
                    className="mt-2"
                  />
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Content Insights Tab */}
          <TabsContent value="content">
            <div className="grid gap-4 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Content Optimization</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Optimal Video Length</span>
                      <span className="font-medium">
                        {Math.floor(analytics.content_insights.optimal_video_length / 60)}:
                        {String(analytics.content_insights.optimal_video_length % 60).padStart(2, '0')}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {analytics.content_insights.best_performing_tags.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Top Performing Tags</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {analytics.content_insights.best_performing_tags.slice(0, 10).map((tag, index) => (
                        <div key={index} className="flex justify-between items-center">
                          <span className="text-sm truncate">{tag.tag}</span>
                          <Badge variant="secondary">{tag.count}</Badge>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          {/* Revenue Tab */}
          <TabsContent value="revenue">
            {analytics.revenue_estimates ? (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm">Monthly Revenue</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-green-600">
                      {formatCurrency(analytics.revenue_estimates.estimated_monthly_revenue)}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm">Annual Projection</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-green-600">
                      {formatCurrency(analytics.revenue_estimates.estimated_annual_revenue)}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm">Revenue per Subscriber</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {formatCurrency(analytics.revenue_estimates.revenue_per_subscriber)}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm">RPM (Revenue per 1K views)</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      ${analytics.revenue_estimates.estimated_rpm}
                    </div>
                  </CardContent>
                </Card>
              </div>
            ) : (
              <Card>
                <CardContent className="pt-6">
                  <p className="text-muted-foreground text-center">
                    Revenue estimates are disabled. Enable them in the dashboard controls to view detailed revenue projections.
                  </p>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      )}
    </div>
  )
}
