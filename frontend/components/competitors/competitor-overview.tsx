"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { TrendingUp, TrendingDown, AlertTriangle, CheckCircle, Clock, Target, FileText, Globe, BarChart3, Brain, AlertCircle } from "lucide-react"
import { useUser } from "@clerk/nextjs"
import { AIInsightsDetailsDialog } from "./ai-insights-details-dialog"

interface CompetitorOverviewProps {
  timeRange: string
  monitoringData?: any[]
}

interface Competitor {
  id: string
  name: string
  status: string
}

interface AIInsight {
  type: "opportunity" | "threat" | "trend"
  title: string
  description: string
  impact: "Low" | "Medium" | "High"
  confidence: number
  data?: any
}

export function CompetitorOverview({ timeRange, monitoringData = [] }: CompetitorOverviewProps) {
  const { user } = useUser()
  const [competitors, setCompetitors] = useState<Competitor[]>([])
  const [loading, setLoading] = useState(false)

  // Fetch competitor names when component mounts
  useEffect(() => {
    const fetchCompetitors = async () => {
      if (!user?.id) return
      
      setLoading(true)
      try {
        const response = await fetch('/api/v1/competitors', {
          headers: {
            'Content-Type': 'application/json',
            'X-User-ID': user.id,
          },
        })
        
        if (response.ok) {
          const data = await response.json()
          setCompetitors(data)
        } else {
          console.error('Failed to fetch competitors:', response.status)
        }
      } catch (error) {
        console.error('Error fetching competitors:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchCompetitors()
  }, [user?.id])

  // Helper function to get competitor name by ID
  const getCompetitorName = (competitorId: string) => {
    const competitor = competitors.find(c => c.id === competitorId)
    return competitor?.name || `Competitor ${competitorId.slice(0, 8)}`
  }

  // Calculate real insights from actual monitoring data
  const calculateInsights = (): AIInsight[] => {
    if (!monitoringData || monitoringData.length === 0) {
      return []
    }

    const insights: AIInsight[] = []
    
    // Platform distribution insight
    const platformCounts = monitoringData.reduce((acc: Record<string, number>, post) => {
      const platform = post.platform || 'unknown'
      acc[platform] = (acc[platform] || 0) + 1
      return acc
    }, {})
    
    const dominantPlatform = Object.entries(platformCounts).sort(([,a], [,b]) => b - a)[0]
    if (dominantPlatform) {
      insights.push({
        type: "trend",
        title: "Platform Activity Concentration",
        description: `Most content is being monitored on ${dominantPlatform[0]} (${dominantPlatform[1]} posts). Consider focusing your monitoring efforts here for maximum competitive intelligence coverage.`,
        impact: "Medium",
        confidence: 85,
        data: { platform: dominantPlatform[0], count: dominantPlatform[1] }
      })
    }

    // Content type insight
    const contentTypes = monitoringData.reduce((acc: Record<string, number>, post) => {
      const postType = post.post_type || 'unknown'
      acc[postType] = (acc[postType] || 0) + 1
      return acc
    }, {})
    
    if (Object.keys(contentTypes).length > 1) {
      insights.push({
        type: "opportunity",
        title: "Content Strategy Diversity",
        description: `Competitors are using multiple content types: ${Object.keys(contentTypes).join(', ')}. This shows content strategy variety and presents opportunities to identify gaps in your content mix.`,
        impact: "Medium",
        confidence: 78,
        data: { contentTypes: Object.keys(contentTypes) }
      })
    }

    // Sentiment insight
    const sentimentScores = monitoringData
      .filter(post => post.sentiment_score !== null && post.sentiment_score !== undefined)
      .map(post => parseFloat(post.sentiment_score))
    
    if (sentimentScores.length > 0) {
      const avgSentiment = sentimentScores.reduce((a, b) => a + b, 0) / sentimentScores.length
      const sentimentInsight = avgSentiment > 0.3 ? "positive" : avgSentiment < -0.3 ? "negative" : "neutral"
      
      insights.push({
        type: "trend",
        title: "Content Sentiment Analysis",
        description: `Overall content sentiment is ${sentimentInsight} (average: ${avgSentiment.toFixed(2)}). This reflects the tone of competitor content and can inform your messaging strategy.`,
        impact: "Low",
        confidence: 72,
        data: { avgSentiment, sentimentInsight }
      })
    }

    // Engagement pattern insight
    const engagementData = monitoringData.filter(post => post.engagement_metrics)
    if (engagementData.length > 0) {
      insights.push({
        type: "opportunity",
        title: "Engagement Pattern Analysis",
        description: `Found ${engagementData.length} posts with engagement metrics. Analyzing these patterns can reveal what content resonates with your target audience.`,
        impact: "High",
        confidence: 68,
        data: { engagementPosts: engagementData.length }
      })
    }

    // New content detection
    const newPosts = monitoringData.filter(post => post.is_new_post === true)
    if (newPosts.length > 0) {
      insights.push({
        type: "trend",
        title: "Fresh Content Detection",
        description: `Detected ${newPosts.length} new posts in the last monitoring cycle. This indicates active competitor activity and content strategy evolution.`,
        impact: "Medium",
        confidence: 75,
        data: { newPosts: newPosts.length }
      })
    }

    return insights
  }

  // Calculate real competitor metrics from monitoring data
  const calculateCompetitorMetrics = () => {
    if (!monitoringData || monitoringData.length === 0) {
      return []
    }

    // Group by competitor and calculate metrics
    const competitorData = monitoringData.reduce((acc: Record<string, any>, post) => {
      const competitorId = post.competitor_id
      if (!acc[competitorId]) {
        acc[competitorId] = {
          id: competitorId,
          posts: 0,
          platforms: new Set(),
          contentTypes: new Set(),
          totalSentiment: 0,
          sentimentCount: 0,
          newPosts: 0,
          contentChanges: 0
        }
      }
      
      acc[competitorId].posts += 1
      if (post.platform) acc[competitorId].platforms.add(post.platform)
      if (post.post_type) acc[competitorId].contentTypes.add(post.post_type)
      
      if (post.sentiment_score !== null && post.sentiment_score !== undefined) {
        acc[competitorId].totalSentiment += parseFloat(post.sentiment_score)
        acc[competitorId].sentimentCount += 1
      }

      if (post.is_new_post) acc[competitorId].newPosts += 1
      if (post.is_content_change) acc[competitorId].contentChanges += 1
      
      return acc
    }, {})

    // Convert to array and calculate averages
    return Object.values(competitorData).map((comp: any) => ({
      id: comp.id,
      name: getCompetitorName(comp.id),
      posts: comp.posts,
      platforms: comp.platforms.size,
      contentTypes: comp.contentTypes.size,
      avgSentiment: comp.sentimentCount > 0 ? (comp.totalSentiment / comp.sentimentCount).toFixed(2) : 'N/A',
      newPosts: comp.newPosts,
      contentChanges: comp.contentChanges,
      trend: comp.posts > 5 ? "up" : "stable"
    }))
  }

  const insights = calculateInsights()
  const competitorMetrics = calculateCompetitorMetrics()

  return (
    <div className="space-y-6">
      {/* Real Data Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Data Overview</CardTitle>
          <CardDescription>Summary of monitored competitor activity</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center p-4 border rounded-lg">
              <FileText className="h-8 w-8 mx-auto mb-2 text-blue-500" />
              <div className="text-2xl font-bold text-foreground">{monitoringData.length}</div>
              <p className="text-sm text-muted-foreground">Total Posts Monitored</p>
            </div>
            <div className="text-center p-4 border rounded-lg">
              <Globe className="h-8 w-8 mx-auto mb-2 text-green-500" />
              <div className="text-2xl font-bold text-foreground">
                {new Set(monitoringData.map(post => post.platform)).size}
              </div>
              <p className="text-sm text-muted-foreground">Platforms Monitored</p>
            </div>
            <div className="text-center p-4 border rounded-lg">
              <BarChart3 className="h-8 w-8 mx-auto mb-2 text-purple-500" />
              <div className="text-2xl font-bold text-foreground">
                {new Set(monitoringData.map(post => post.competitor_id)).size}
              </div>
              <p className="text-sm text-muted-foreground">Competitors Tracked</p>
            </div>
            <div className="text-center p-4 border rounded-lg">
              <Brain className="h-8 w-8 mx-auto mb-2 text-orange-500" />
              <div className="text-2xl font-bold text-foreground">{insights.length}</div>
              <p className="text-sm text-muted-foreground">AI Insights Generated</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* AI Insights - Based on real data */}
      {insights.length > 0 ? (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-blue-600" />
              AI Competitive Insights
            </CardTitle>
            <CardDescription>Key findings from actual competitor analysis</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {insights.map((insight, index) => (
                <div key={index} className="flex items-start gap-4 p-4 border rounded-lg">
                  <div className="mt-1">
                    {insight.type === "opportunity" && <CheckCircle className="h-5 w-5 text-green-500" />}
                    {insight.type === "threat" && <AlertTriangle className="h-5 w-5 text-orange-500" />}
                    {insight.type === "trend" && <TrendingUp className="h-5 w-5 text-blue-500" />}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-medium text-foreground">{insight.title}</h3>
                      <Badge variant={insight.impact === "High" ? "destructive" : "secondary"}>
                        {insight.impact} Impact
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">{insight.description}</p>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-muted-foreground">Confidence:</span>
                      <Progress value={insight.confidence} className="w-20 h-2" />
                      <span className="text-xs font-medium text-foreground">{insight.confidence}%</span>
                    </div>
                  </div>
                  <AIInsightsDetailsDialog 
                    insight={insight}
                    trigger={
                      <Button variant="outline" size="sm">
                        <AlertCircle className="h-4 w-4 mr-1" />
                        View Details
                      </Button>
                    }
                  />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-blue-600" />
              AI Competitive Insights
            </CardTitle>
            <CardDescription>Key findings from competitor analysis</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8 text-muted-foreground">
              <BarChart3 className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p className="text-lg font-medium">No insights available yet</p>
              <p className="text-sm">Start monitoring competitors to generate AI-powered insights</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Competitor Performance Matrix - Based on real data */}
      {competitorMetrics.length > 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>Competitor Performance Matrix</CardTitle>
            <CardDescription>Comparative analysis based on monitored data</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {competitorMetrics.map((competitor, index) => (
                <div key={index} className="grid grid-cols-1 md:grid-cols-6 gap-4 p-4 border rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-gray-100 dark:bg-gray-800 rounded-lg flex items-center justify-center">
                      <span className="font-semibold text-xs text-foreground">{competitor.name.charAt(0).toUpperCase()}</span>
                    </div>
                    <div>
                      <h3 className="font-medium text-foreground">{competitor.name}</h3>
                      <div className="flex items-center gap-1">
                        {competitor.trend === "up" ? (
                          <TrendingUp className="h-3 w-3 text-green-500" />
                        ) : (
                          <TrendingDown className="h-3 w-3 text-red-500" />
                        )}
                        <span className="text-xs text-muted-foreground">
                          {competitor.trend === "up" ? "Active" : "Stable"}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-foreground">Posts</div>
                    <div className="text-lg font-bold text-foreground">{competitor.posts}</div>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-foreground">Platforms</div>
                    <div className="text-lg font-bold text-foreground">{competitor.platforms}</div>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-foreground">Content Types</div>
                    <div className="text-lg font-bold text-foreground">{competitor.contentTypes}</div>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-foreground">Avg. Sentiment</div>
                    <div className="text-lg font-bold text-foreground">{competitor.avgSentiment}</div>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-foreground">New Posts</div>
                    <div className="text-lg font-bold text-foreground">{competitor.newPosts}</div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle>Competitor Performance Matrix</CardTitle>
            <CardDescription>Comparative analysis across key metrics</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8 text-muted-foreground">
              <BarChart3 className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p className="text-lg font-medium">No performance data available</p>
              <p className="text-sm">Start monitoring competitors to see performance comparisons</p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
