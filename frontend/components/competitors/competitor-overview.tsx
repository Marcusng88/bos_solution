"use client"

import '../../styles/competitor-animations.css'
import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { TrendingUp, TrendingDown, AlertTriangle, CheckCircle, Clock, Target, FileText, Globe, BarChart3, Brain, AlertCircle } from "lucide-react"
import { useUser } from "@clerk/nextjs"
import { AIInsightsDetailsDialog } from "./ai-insights-details-dialog"
import GradientText from "@/components/effects/GradientText"
import ShinyText from "@/components/effects/ShinyText"

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
  const [isVisible, setIsVisible] = useState(false)

  // Set visibility for animations
  useEffect(() => {
    setIsVisible(true)
  }, [])

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
    <div className="space-y-8">
      {/* Real Data Summary */}
      <Card className={`glass-card hover-glow transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
        <CardHeader>
          <CardTitle className="text-white text-xl">
            <GradientText
              colors={["#60a5fa", "#a78bfa", "#34d399"]}
              animationSpeed={4}
              showBorder={false}
              className="text-xl font-bold"
            >
              Intelligence Data Overview
            </GradientText>
          </CardTitle>
          <CardDescription className="text-slate-300">
            <ShinyText 
              text="Real-time summary of monitored competitor activity" 
              disabled={false} 
              speed={3} 
              className="text-slate-300"
            />
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center p-6 border border-white/20 rounded-xl bg-gradient-to-br from-blue-500/20 to-blue-600/20 backdrop-blur-sm hover:scale-105 transition-all duration-300 group animate-bounce-in">
              <div className="relative">
                <FileText className="h-12 w-12 mx-auto mb-4 text-blue-400 group-hover:scale-110 transition-transform duration-300" />
                <div className="absolute inset-0 bg-blue-400/20 rounded-full blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              </div>
              <div className="text-3xl font-bold text-white mb-1 animate-counter-up">
                {monitoringData.length}
              </div>
              <p className="text-sm text-blue-200">Total Posts Monitored</p>
            </div>
            <div className="text-center p-6 border border-white/20 rounded-xl bg-gradient-to-br from-green-500/20 to-green-600/20 backdrop-blur-sm hover:scale-105 transition-all duration-300 group animate-bounce-in" style={{ animationDelay: '0.1s' }}>
              <div className="relative">
                <Globe className="h-12 w-12 mx-auto mb-4 text-green-400 group-hover:scale-110 transition-transform duration-300" />
                <div className="absolute inset-0 bg-green-400/20 rounded-full blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              </div>
              <div className="text-3xl font-bold text-white mb-1 animate-counter-up">
                {new Set(monitoringData.map(post => post.platform)).size}
              </div>
              <p className="text-sm text-green-200">Platforms Monitored</p>
            </div>
            <div className="text-center p-6 border border-white/20 rounded-xl bg-gradient-to-br from-purple-500/20 to-purple-600/20 backdrop-blur-sm hover:scale-105 transition-all duration-300 group animate-bounce-in" style={{ animationDelay: '0.2s' }}>
              <div className="relative">
                <BarChart3 className="h-12 w-12 mx-auto mb-4 text-purple-400 group-hover:scale-110 transition-transform duration-300" />
                <div className="absolute inset-0 bg-purple-400/20 rounded-full blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              </div>
              <div className="text-3xl font-bold text-white mb-1 animate-counter-up">
                {new Set(monitoringData.map(post => post.competitor_id)).size}
              </div>
              <p className="text-sm text-purple-200">Competitors Tracked</p>
            </div>
            <div className="text-center p-6 border border-white/20 rounded-xl bg-gradient-to-br from-orange-500/20 to-orange-600/20 backdrop-blur-sm hover:scale-105 transition-all duration-300 group animate-bounce-in" style={{ animationDelay: '0.3s' }}>
              <div className="relative">
                <Brain className="h-12 w-12 mx-auto mb-4 text-orange-400 group-hover:scale-110 transition-transform duration-300" />
                <div className="absolute inset-0 bg-orange-400/20 rounded-full blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              </div>
              <div className="text-3xl font-bold text-white mb-1 animate-counter-up">
                {insights.length}
              </div>
              <p className="text-sm text-orange-200">AI Insights Generated</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* AI Insights - Based on real data */}
      {insights.length > 0 ? (
        <Card className={`glass-card hover-glow transition-all duration-1000 delay-200 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-white">
              <Brain className="h-6 w-6 text-blue-400 animate-pulse" />
              <GradientText
                colors={["#3b82f6", "#8b5cf6", "#06b6d4"]}
                animationSpeed={5}
                showBorder={false}
                className="text-xl font-bold"
              >
                AI Competitive Intelligence
              </GradientText>
            </CardTitle>
            <CardDescription className="text-slate-300">
              Key findings from actual competitor analysis powered by advanced AI
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {insights.map((insight, index) => (
                <div 
                  key={index} 
                  className={`group relative overflow-hidden p-6 border border-white/20 rounded-xl bg-gradient-to-r from-slate-800/50 to-slate-700/50 backdrop-blur-sm hover:from-blue-900/30 hover:to-purple-900/30 transition-all duration-500 hover:scale-105 animate-fade-in-up`}
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  {/* Animated background glow */}
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-pink-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 rounded-xl"></div>
                  
                  <div className="relative z-10 flex items-start gap-4">
                    <div className="mt-1 p-2 rounded-lg bg-white/10 backdrop-blur-sm">
                      {insight.type === "opportunity" && <CheckCircle className="h-6 w-6 text-green-400" />}
                      {insight.type === "threat" && <AlertTriangle className="h-6 w-6 text-orange-400" />}
                      {insight.type === "trend" && <TrendingUp className="h-6 w-6 text-blue-400" />}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="font-bold text-lg text-white group-hover:text-blue-200 transition-colors duration-300">
                          {insight.title}
                        </h3>
                        <Badge 
                          variant={insight.impact === "High" ? "destructive" : "secondary"}
                          className={
                            insight.impact === "High" 
                              ? "bg-red-500/20 text-red-300 border-red-400/30" 
                              : insight.impact === "Medium"
                                ? "bg-yellow-500/20 text-yellow-300 border-yellow-400/30"
                                : "bg-green-500/20 text-green-300 border-green-400/30"
                          }
                        >
                          {insight.impact} Impact
                        </Badge>
                      </div>
                      <p className="text-slate-300 mb-4 group-hover:text-white transition-colors duration-300">
                        {insight.description}
                      </p>
                      <div className="flex items-center gap-3">
                        <span className="text-sm text-slate-400">Confidence:</span>
                        <div className="flex-1 max-w-32 relative">
                          <Progress 
                            value={insight.confidence} 
                            className="h-3 bg-white/10 border border-white/20" 
                          />
                          <div 
                            className="absolute top-0 left-0 h-3 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full transition-all duration-1000 ease-out"
                            style={{ width: `${insight.confidence}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-bold text-white">{insight.confidence}%</span>
                      </div>
                    </div>
                    <AIInsightsDetailsDialog 
                      insight={insight}
                      trigger={
                        <Button 
                          variant="outline" 
                          size="sm"
                          className="bg-white/10 border-white/20 text-white hover:bg-white/20 hover:border-white/30 hover:scale-105 transition-all duration-300 backdrop-blur-sm"
                        >
                          <AlertCircle className="h-4 w-4 mr-2" />
                          View Details
                        </Button>
                      }
                    />
                  </div>
                  
                  {/* Animated border on hover */}
                  <div className="absolute inset-0 rounded-xl border-2 border-transparent group-hover:border-blue-400/30 transition-all duration-500"></div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card className={`glass-card transition-all duration-1000 delay-200 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-white">
              <Brain className="h-6 w-6 text-blue-400 animate-pulse" />
              <GradientText
                colors={["#3b82f6", "#8b5cf6", "#06b6d4"]}
                animationSpeed={5}
                showBorder={false}
                className="text-xl font-bold"
              >
                AI Competitive Intelligence
              </GradientText>
            </CardTitle>
            <CardDescription className="text-slate-300">
              Key findings from competitor analysis
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center py-12 text-slate-300">
              <div className="relative mb-6">
                <BarChart3 className="h-20 w-20 mx-auto opacity-50" />
                <div className="absolute inset-0 h-20 w-20 mx-auto bg-blue-500/20 rounded-full animate-ping"></div>
              </div>
              <p className="text-xl font-medium mb-2">No insights available yet</p>
              <p className="text-sm text-slate-400">Start monitoring competitors to generate AI-powered insights</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Competitor Performance Matrix - Based on real data */}
      {competitorMetrics.length > 0 ? (
        <Card className={`glass-card hover-glow transition-all duration-1000 delay-400 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
          <CardHeader>
            <CardTitle className="text-white text-xl">
              <GradientText
                colors={["#f59e0b", "#ef4444", "#8b5cf6"]}
                animationSpeed={4}
                showBorder={false}
                className="text-xl font-bold"
              >
                Competitor Performance Matrix
              </GradientText>
            </CardTitle>
            <CardDescription className="text-slate-300">
              Comparative analysis based on monitored data
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {competitorMetrics.map((competitor, index) => (
                <div 
                  key={index} 
                  className={`group relative overflow-hidden grid grid-cols-1 md:grid-cols-6 gap-6 p-6 border border-white/20 rounded-xl bg-gradient-to-r from-slate-800/50 to-slate-700/50 backdrop-blur-sm hover:from-indigo-900/30 hover:to-purple-900/30 transition-all duration-500 hover:scale-105 animate-fade-in-up`}
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  {/* Animated background glow */}
                  <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/10 via-purple-500/10 to-pink-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 rounded-xl"></div>
                  
                  <div className="relative z-10 flex items-center gap-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-indigo-500/30 to-purple-500/30 rounded-xl flex items-center justify-center backdrop-blur-sm border border-white/20 group-hover:scale-110 transition-all duration-300">
                      <span className="font-bold text-white text-sm">
                        {competitor.name.charAt(0).toUpperCase()}
                      </span>
                    </div>
                    <div>
                      <h3 className="font-bold text-white text-lg group-hover:text-blue-200 transition-colors duration-300">
                        {competitor.name}
                      </h3>
                      <div className="flex items-center gap-2 mt-1">
                        {competitor.trend === "up" ? (
                          <TrendingUp className="h-4 w-4 text-green-400" />
                        ) : (
                          <TrendingDown className="h-4 w-4 text-red-400" />
                        )}
                        <span className="text-sm text-slate-300">
                          {competitor.trend === "up" ? "Active Growth" : "Stable Activity"}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="relative z-10 text-center">
                    <div className="text-sm font-medium text-slate-300 mb-1">Posts</div>
                    <div className="text-2xl font-bold text-white animate-counter-up">
                      {competitor.posts}
                    </div>
                  </div>
                  
                  <div className="relative z-10 text-center">
                    <div className="text-sm font-medium text-slate-300 mb-1">Platforms</div>
                    <div className="text-2xl font-bold text-blue-400 animate-counter-up">
                      {competitor.platforms}
                    </div>
                  </div>
                  
                  <div className="relative z-10 text-center">
                    <div className="text-sm font-medium text-slate-300 mb-1">Content Types</div>
                    <div className="text-2xl font-bold text-purple-400 animate-counter-up">
                      {competitor.contentTypes}
                    </div>
                  </div>
                  
                  <div className="relative z-10 text-center">
                    <div className="text-sm font-medium text-slate-300 mb-1">Avg. Sentiment</div>
                    <div className="text-2xl font-bold text-green-400 animate-counter-up">
                      {competitor.avgSentiment}
                    </div>
                  </div>
                  
                  <div className="relative z-10 text-center">
                    <div className="text-sm font-medium text-slate-300 mb-1">New Posts</div>
                    <div className="text-2xl font-bold text-orange-400 animate-counter-up">
                      {competitor.newPosts}
                    </div>
                  </div>
                  
                  {/* Animated border on hover */}
                  <div className="absolute inset-0 rounded-xl border-2 border-transparent group-hover:border-indigo-400/30 transition-all duration-500"></div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card className={`glass-card transition-all duration-1000 delay-400 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
          <CardHeader>
            <CardTitle className="text-white text-xl">
              <GradientText
                colors={["#f59e0b", "#ef4444", "#8b5cf6"]}
                animationSpeed={4}
                showBorder={false}
                className="text-xl font-bold"
              >
                Competitor Performance Matrix
              </GradientText>
            </CardTitle>
            <CardDescription className="text-slate-300">
              Comparative analysis across key metrics
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center py-12 text-slate-300">
              <div className="relative mb-6">
                <BarChart3 className="h-20 w-20 mx-auto opacity-50" />
                <div className="absolute inset-0 h-20 w-20 mx-auto bg-purple-500/20 rounded-full animate-ping"></div>
              </div>
              <p className="text-xl font-medium mb-2">No performance data available</p>
              <p className="text-sm text-slate-400">Start monitoring competitors to see performance comparisons</p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
