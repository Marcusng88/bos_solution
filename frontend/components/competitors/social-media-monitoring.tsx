"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Heart, MessageCircle, Share, ExternalLink, Clock, BarChart3, AlertCircle, FileText } from "lucide-react"

interface SocialMediaMonitoringProps {
  monitoringData?: any[]
}

export function SocialMediaMonitoring({ monitoringData = [] }: SocialMediaMonitoringProps) {
  // Calculate real platform metrics from actual monitoring data
  const calculatePlatformMetrics = () => {
    if (!monitoringData || monitoringData.length === 0) {
      return []
    }

    const platformData = monitoringData.reduce((acc: Record<string, any>, post) => {
      const platform = post.platform || 'unknown'
      if (!acc[platform]) {
        acc[platform] = {
          platform,
          posts: 0,
          totalEngagement: 0,
          engagementCount: 0,
          competitors: new Set()
        }
      }
      
      acc[platform].posts += 1
      acc[platform].competitors.add(post.competitor_id)
      
      // Calculate engagement if available
      if (post.engagement_metrics) {
        const engagement = post.engagement_metrics
        if (engagement.like_count) acc[platform].totalEngagement += engagement.like_count
        if (engagement.comment_count) acc[platform].totalEngagement += engagement.comment_count
        if (engagement.share_count) acc[platform].totalEngagement += engagement.share_count
        acc[platform].engagementCount += 1
      }
      
      return acc
    }, {})

    return Object.values(platformData).map((data: any) => ({
      platform: data.platform,
      posts: data.posts,
      avgEngagement: data.engagementCount > 0 ? (data.totalEngagement / data.engagementCount).toFixed(1) : 'N/A',
      topPerformer: `${data.competitors.size} competitors`,
      competitorCount: data.competitors.size
    }))
  }

  // Calculate real recent posts from actual monitoring data
  const calculateRecentPosts = () => {
    if (!monitoringData || monitoringData.length === 0) {
      return []
    }

    // Sort by detected_at and take the most recent posts
    const sortedPosts = [...monitoringData].sort((a, b) => 
      new Date(b.detected_at).getTime() - new Date(a.detected_at).getTime()
    )

    return sortedPosts.slice(0, 5).map(post => {
      const timestamp = new Date(post.detected_at)
      const now = new Date()
      const diffMs = now.getTime() - timestamp.getTime()
      const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
      
      let timeAgo = ''
      if (diffHours < 1) timeAgo = 'Just now'
      else if (diffHours < 24) timeAgo = `${diffHours} hours ago`
      else timeAgo = `${diffDays} days ago`

      // Calculate performance based on available metrics
      let performance = "Low"
      if (post.engagement_metrics) {
        const engagement = post.engagement_metrics
        const totalEngagement = (engagement.like_count || 0) + (engagement.comment_count || 0) + (engagement.share_count || 0)
        if (totalEngagement > 1000) performance = "Very High"
        else if (totalEngagement > 500) performance = "High"
        else if (totalEngagement > 100) performance = "Medium"
      }

      return {
        id: post.id,
        competitor: post.competitor_id || 'Unknown',
        platform: post.platform || 'Unknown',
        content: post.content_text || 'No content available',
        timestamp: timeAgo,
        engagement: post.engagement_metrics || { like_count: 0, comment_count: 0, share_count: 0 },
        performance,
        url: post.post_url || '#',
        postType: post.post_type || 'Unknown'
      }
    })
  }

  // Calculate content themes from actual data
  const calculateContentThemes = () => {
    if (!monitoringData || monitoringData.length === 0) {
      return []
    }

    const themes = monitoringData.reduce((acc: Record<string, any>, post) => {
      if (post.post_type) {
        const theme = post.post_type
        if (!acc[theme]) {
          acc[theme] = { theme, frequency: 0, totalEngagement: 0, engagementCount: 0 }
        }
        acc[theme].frequency += 1
        
        if (post.engagement_metrics) {
          const engagement = post.engagement_metrics
          const totalEngagement = (engagement.like_count || 0) + (engagement.comment_count || 0) + (engagement.share_count || 0)
          acc[theme].totalEngagement += totalEngagement
          acc[theme].engagementCount += 1
        }
      }
      return acc
    }, {})

    return Object.values(themes)
      .sort((a: any, b: any) => b.frequency - a.frequency)
      .slice(0, 6)
      .map((theme: any) => ({
        theme: theme.theme,
        frequency: theme.frequency,
        engagement: theme.engagementCount > 0 
          ? (theme.totalEngagement / theme.engagementCount > 500 ? "High" : 
             theme.totalEngagement / theme.engagementCount > 100 ? "Medium" : "Low")
          : "Unknown"
      }))
  }

  const platformMetrics = calculatePlatformMetrics()
  const recentPosts = calculateRecentPosts()
  const contentThemes = calculateContentThemes()

  const getPerformanceBadge = (performance: string) => {
    switch (performance) {
      case "Very High":
        return <Badge className="bg-green-600">Very High</Badge>
      case "High":
        return <Badge className="bg-green-500">High</Badge>
      case "Medium":
        return <Badge variant="secondary">Medium</Badge>
      case "Low":
        return <Badge variant="outline">Low</Badge>
      default:
        return <Badge variant="outline">Unknown</Badge>
    }
  }

  return (
    <div className="space-y-6">
      {/* Data Overview */}
      <Card>
        <CardHeader>
          <CardTitle>Monitoring Data Overview</CardTitle>
          <CardDescription>Summary of competitor activity across platforms</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 border rounded-lg">
              <FileText className="h-8 w-8 mx-auto mb-2 text-blue-500" />
              <div className="text-2xl font-bold">{monitoringData.length}</div>
              <p className="text-sm text-muted-foreground">Total Posts Monitored</p>
            </div>
            <div className="text-center p-4 border rounded-lg">
              <BarChart3 className="h-8 w-8 mx-auto mb-2 text-green-500" />
              <div className="text-2xl font-bold">
                {new Set(monitoringData.map(post => post.platform)).size}
              </div>
              <p className="text-sm text-muted-foreground">Platforms Monitored</p>
            </div>
            <div className="text-center p-4 border rounded-lg">
              <Clock className="h-8 w-8 mx-auto mb-2 text-purple-500" />
              <div className="text-2xl font-bold">
                {new Set(monitoringData.map(post => post.competitor_id)).size}
              </div>
              <p className="text-sm text-muted-foreground">Competitors Tracked</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Platform Performance Overview - Based on real data */}
      {platformMetrics.length > 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>Platform Performance Overview</CardTitle>
            <CardDescription>Competitor activity and engagement across social platforms</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {platformMetrics.map((platform, index) => (
                <div key={index} className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium">{platform.platform}</h3>
                    <Badge variant="outline">{platform.posts} posts</Badge>
                  </div>
                  <div className="space-y-2">
                    <div>
                      <span className="text-sm text-muted-foreground">Avg. Engagement: </span>
                      <span className="font-medium">{platform.avgEngagement}</span>
                    </div>
                    <div>
                      <span className="text-sm text-muted-foreground">Competitors: </span>
                      <span className="font-medium">{platform.competitorCount}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle>Platform Performance Overview</CardTitle>
            <CardDescription>Competitor activity and engagement across social platforms</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8 text-muted-foreground">
              <BarChart3 className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p className="text-lg font-medium">No platform data available</p>
              <p className="text-sm">Start monitoring competitors to see platform performance</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recent Competitor Posts - Based on real data */}
      {recentPosts.length > 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>Recent Competitor Activity</CardTitle>
            <CardDescription>Latest posts and their performance metrics</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentPosts.map((post, index) => (
                <div key={index} className="border rounded-lg p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <Avatar className="h-8 w-8">
                        <AvatarFallback>{post.competitor.slice(0, 2)}</AvatarFallback>
                      </Avatar>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-medium">Competitor {post.competitor.slice(0, 8)}</span>
                          <Badge variant="outline">{post.platform}</Badge>
                          <Badge variant="secondary">{post.postType}</Badge>
                        </div>
                        <div className="flex items-center gap-1 text-sm text-muted-foreground">
                          <Clock className="h-3 w-3" />
                          {post.timestamp}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {getPerformanceBadge(post.performance)}
                      <Button variant="ghost" size="sm">
                        <ExternalLink className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>

                  <p className="text-sm mb-3 leading-relaxed">
                    {post.content.length > 200 ? `${post.content.substring(0, 200)}...` : post.content}
                  </p>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-6 text-sm text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Heart className="h-4 w-4" />
                        {(post.engagement.like_count || 0).toLocaleString()}
                      </div>
                      <div className="flex items-center gap-1">
                        <MessageCircle className="h-4 w-4" />
                        {(post.engagement.comment_count || 0).toLocaleString()}
                      </div>
                      <div className="flex items-center gap-1">
                        <Share className="h-4 w-4" />
                        {(post.engagement.share_count || 0).toLocaleString()}
                      </div>
                    </div>
                    <Button variant="outline" size="sm">
                      Analyze Post
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle>Recent Competitor Activity</CardTitle>
            <CardDescription>Latest posts and their performance metrics</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8 text-muted-foreground">
              <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p className="text-lg font-medium">No recent posts available</p>
              <p className="text-sm">Start monitoring competitors to see their latest activity</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Content Themes Analysis - Based on real data */}
      {contentThemes.length > 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>Content Themes Analysis</CardTitle>
            <CardDescription>Most popular content themes among competitors</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {contentThemes.map((theme, index) => (
                <div key={index} className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium">{theme.theme}</h3>
                    {getPerformanceBadge(theme.engagement)}
                  </div>
                  <div className="text-sm text-muted-foreground">{theme.frequency} posts monitored</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle>Content Themes Analysis</CardTitle>
            <CardDescription>Most popular content themes among competitors</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8 text-muted-foreground">
              <AlertCircle className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p className="text-lg font-medium">No content themes identified</p>
              <p className="text-sm">
                {monitoringData.length > 0 
                  ? "Content analysis didn't reveal clear themes yet."
                  : "Start monitoring competitors to identify content themes and patterns."
                }
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
