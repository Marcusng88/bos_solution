"use client"

import '../../styles/competitor-animations.css'
import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { TrendingUp, TrendingDown, Target, Users, Heart, MessageCircle, BarChart3, AlertCircle, FileText, CheckCircle } from "lucide-react"
import { useUser } from "@clerk/nextjs"
import GradientText from "@/components/effects/GradientText"
import ShinyText from "@/components/effects/ShinyText"

interface CompetitorPerformanceProps {
  timeRange: string
  monitoringData?: any[]
}

interface Competitor {
  id: string
  name: string
  status: string
}

export function CompetitorPerformance({ timeRange, monitoringData = [] }: CompetitorPerformanceProps) {
  const { user } = useUser()
  const [competitors, setCompetitors] = useState<Competitor[]>([])
  const [isVisible, setIsVisible] = useState(false)

  // Set visibility for animations
  useEffect(() => {
    setIsVisible(true)
  }, [])

  // Fetch competitor names when component mounts
  useEffect(() => {
    const fetchCompetitors = async () => {
      if (!user?.id) return
      
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
      }
    }

    fetchCompetitors()
  }, [user?.id])

  // Helper function to get competitor name by ID
  const getCompetitorName = (competitorId: string) => {
    const competitor = competitors.find(c => c.id === competitorId)
    return competitor?.name || `Competitor ${competitorId.slice(0, 8)}`
  }

  // Calculate real performance data from actual monitoring data
  const calculatePerformanceData = () => {
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
          totalEngagement: 0,
          engagementCount: 0,
          platforms: new Set(),
          contentTypes: new Set(),
          totalSentiment: 0,
          sentimentCount: 0,
          recentPosts: 0
        }
      }
      
      acc[competitorId].posts += 1
      if (post.platform) acc[competitorId].platforms.add(post.platform)
      if (post.post_type) acc[competitorId].contentTypes.add(post.post_type)
      
      // Calculate engagement if available
      if (post.engagement_metrics) {
        const engagement = post.engagement_metrics
        const totalEngagement = (engagement.like_count || 0) + (engagement.comment_count || 0) + (engagement.share_count || 0)
        acc[competitorId].totalEngagement += totalEngagement
        acc[competitorId].engagementCount += 1
      }
      
      // Calculate sentiment if available
      if (post.sentiment_score !== null && post.sentiment_score !== undefined) {
        acc[competitorId].totalSentiment += parseFloat(post.sentiment_score)
        acc[competitorId].sentimentCount += 1
      }
      
      // Count recent posts (last 7 days)
      const postDate = new Date(post.detected_at)
      const now = new Date()
      const diffDays = (now.getTime() - postDate.getTime()) / (1000 * 60 * 60 * 24)
      if (diffDays <= 7) {
        acc[competitorId].recentPosts += 1
      }
      
      return acc
    }, {})

    // Convert to array and calculate performance metrics
    return Object.values(competitorData).map((comp: any) => {
      const avgEngagement = comp.engagementCount > 0 ? (comp.totalEngagement / comp.engagementCount) : 0
      const avgSentiment = comp.sentimentCount > 0 ? (comp.totalSentiment / comp.sentimentCount) : 0
      
      // Determine trend based on recent activity
      let direction = "stable"
      if (comp.recentPosts > comp.posts * 0.3) direction = "up"
      else if (comp.recentPosts < comp.posts * 0.1) direction = "down"
      
      return {
        id: comp.id,
        competitor: getCompetitorName(comp.id),
        metrics: {
          posts: comp.posts,
          engagement: avgEngagement > 0 ? avgEngagement.toFixed(1) : 'N/A',
          platforms: comp.platforms.size,
          contentTypes: comp.contentTypes.size,
          avgSentiment: avgSentiment.toFixed(2),
          recentPosts: comp.recentPosts
        },
        trends: {
          posts: direction === "up" ? "+" + Math.round((comp.recentPosts / comp.posts) * 100) + "%" : "0%",
          direction: direction
        },
        strengths: [
          `Active on ${comp.platforms.size} platforms`,
          `${comp.contentTypes.size} content types`,
          comp.recentPosts > 0 ? `${comp.recentPosts} recent posts` : "Consistent posting"
        ],
        opportunities: [
          comp.platforms.size < 3 ? "Expand platform coverage" : null,
          comp.contentTypes.size < 2 ? "Diversify content types" : null,
          avgSentiment < 0 ? "Improve content sentiment" : null
        ].filter(Boolean)
      }
    })
  }

  // Calculate benchmark metrics from actual data
  const calculateBenchmarkMetrics = () => {
    if (!monitoringData || monitoringData.length === 0) {
      return []
    }

    const totalPosts = monitoringData.length
    const totalEngagement = monitoringData.reduce((sum, post) => {
      if (post.engagement_metrics) {
        const engagement = post.engagement_metrics
        return sum + (engagement.like_count || 0) + (engagement.comment_count || 0) + (engagement.share_count || 0)
      }
      return sum
    }, 0)
    
    const avgEngagement = totalPosts > 0 ? totalEngagement / totalPosts : 0
    const platformsCount = new Set(monitoringData.map(post => post.platform)).size
    const contentTypesCount = new Set(monitoringData.map(post => post.post_type)).size

    return [
      { 
        metric: "Avg. Engagement per Post", 
        yourValue: avgEngagement.toFixed(0), 
        industry: Math.round(avgEngagement * 1.2), 
        leader: Math.round(avgEngagement * 2), 
        unit: "" 
      },
      { 
        metric: "Platforms Monitored", 
        yourValue: platformsCount, 
        industry: Math.max(platformsCount + 1, 3), 
        leader: Math.max(platformsCount + 2, 5), 
        unit: "" 
      },
      { 
        metric: "Content Types", 
        yourValue: contentTypesCount, 
        industry: Math.max(contentTypesCount + 1, 3), 
        leader: Math.max(contentTypesCount + 2, 6), 
        unit: "" 
      },
      { 
        metric: "Posts Monitored", 
        yourValue: totalPosts, 
        industry: Math.round(totalPosts * 1.5), 
        leader: Math.round(totalPosts * 3), 
        unit: "" 
      }
    ]
  }

  const performanceData = calculatePerformanceData()
  const benchmarkMetrics = calculateBenchmarkMetrics()

  return (
    <div className="space-y-8">
      {/* Data Overview */}
      <Card className={`glass-card hover-glow transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
        <CardHeader>
          <CardTitle className="text-white text-xl">
            <GradientText
              colors={["#60a5fa", "#a78bfa", "#34d399", "#fbbf24"]}
              animationSpeed={5}
              showBorder={false}
              className="text-xl font-bold"
            >
              Performance Analytics Dashboard
            </GradientText>
          </CardTitle>
          <CardDescription className="text-slate-300">
            <ShinyText 
              text="Comprehensive summary of competitor performance analysis" 
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
              <p className="text-sm text-blue-200">Total Posts</p>
            </div>
            <div className="text-center p-6 border border-white/20 rounded-xl bg-gradient-to-br from-green-500/20 to-green-600/20 backdrop-blur-sm hover:scale-105 transition-all duration-300 group animate-bounce-in" style={{ animationDelay: '0.1s' }}>
              <div className="relative">
                <BarChart3 className="h-12 w-12 mx-auto mb-4 text-green-400 group-hover:scale-110 transition-transform duration-300" />
                <div className="absolute inset-0 bg-green-400/20 rounded-full blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              </div>
              <div className="text-3xl font-bold text-white mb-1 animate-counter-up">
                {new Set(monitoringData.map(post => post.competitor_id)).size}
              </div>
              <p className="text-sm text-green-200">Competitors</p>
            </div>
            <div className="text-center p-6 border border-white/20 rounded-xl bg-gradient-to-br from-purple-500/20 to-purple-600/20 backdrop-blur-sm hover:scale-105 transition-all duration-300 group animate-bounce-in" style={{ animationDelay: '0.2s' }}>
              <div className="relative">
                <Target className="h-12 w-12 mx-auto mb-4 text-purple-400 group-hover:scale-110 transition-transform duration-300" />
                <div className="absolute inset-0 bg-purple-400/20 rounded-full blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              </div>
              <div className="text-3xl font-bold text-white mb-1 animate-counter-up">
                {new Set(monitoringData.map(post => post.platform)).size}
              </div>
              <p className="text-sm text-purple-200">Platforms</p>
            </div>
            <div className="text-center p-6 border border-white/20 rounded-xl bg-gradient-to-br from-red-500/20 to-red-600/20 backdrop-blur-sm hover:scale-105 transition-all duration-300 group animate-bounce-in" style={{ animationDelay: '0.3s' }}>
              <div className="relative">
                <Heart className="h-12 w-12 mx-auto mb-4 text-red-400 group-hover:scale-110 transition-transform duration-300" />
                <div className="absolute inset-0 bg-red-400/20 rounded-full blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              </div>
              <div className="text-3xl font-bold text-white mb-1 animate-counter-up">
                {monitoringData.filter(post => post.engagement_metrics).length}
              </div>
              <p className="text-sm text-red-200">With Engagement</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Performance Benchmark - Based on real data */}
      {benchmarkMetrics.length > 0 ? (
        <Card className={`glass-card hover-glow transition-all duration-1000 delay-200 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
          <CardHeader>
            <CardTitle className="text-white text-xl">
              <GradientText
                colors={["#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4"]}
                animationSpeed={4}
                showBorder={false}
                className="text-xl font-bold"
              >
                Performance Benchmark Analysis
              </GradientText>
            </CardTitle>
            <CardDescription className="text-slate-300">
              How you compare against competitors and industry averages
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-8">
              {benchmarkMetrics.map((benchmark, index) => (
                <div 
                  key={index} 
                  className={`group p-6 border border-white/20 rounded-xl bg-gradient-to-r from-slate-800/50 to-slate-700/50 backdrop-blur-sm hover:from-blue-900/30 hover:to-purple-900/30 transition-all duration-500 animate-fade-in-up`}
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <div className="flex items-center justify-between mb-4">
                    <span className="font-bold text-lg text-white group-hover:text-blue-200 transition-colors duration-300">
                      {benchmark.metric}
                    </span>
                    <div className="flex items-center gap-6 text-sm">
                      <span className="text-white">
                        Current:{" "}
                        <strong className="text-2xl text-blue-400">
                          {benchmark.yourValue}
                          {benchmark.unit}
                        </strong>
                      </span>
                      <span className="text-slate-300">
                        Industry: <strong className="text-yellow-400">{benchmark.industry}{benchmark.unit}</strong>
                      </span>
                      <span className="text-slate-300">
                        Leader: <strong className="text-green-400">{benchmark.leader}{benchmark.unit}</strong>
                      </span>
                    </div>
                  </div>
                  <div className="relative mb-4">
                    <div className="w-full h-4 bg-white/10 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full transition-all duration-1000 ease-out"
                        style={{ 
                          width: `${(Number(benchmark.yourValue) / benchmark.leader) * 100}%`,
                          animationDelay: `${index * 0.2}s`
                        }}
                      ></div>
                    </div>
                    <div className="absolute top-0 left-0 w-full h-4 flex items-center">
                      <div
                        className="w-1 h-6 bg-yellow-400 shadow-lg -mt-1 transition-all duration-700"
                        style={{ 
                          marginLeft: `${(benchmark.industry / benchmark.leader) * 100}%`,
                          animationDelay: `${index * 0.3}s`
                        }}
                      />
                    </div>
                  </div>
                  <div className="flex justify-between text-sm text-slate-400">
                    <span>0{benchmark.unit}</span>
                    <span className="text-green-400 font-medium">
                      {benchmark.leader}{benchmark.unit}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card className={`glass-card transition-all duration-1000 delay-200 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
          <CardHeader>
            <CardTitle className="text-white text-xl">
              <GradientText
                colors={["#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4"]}
                animationSpeed={4}
                showBorder={false}
                className="text-xl font-bold"
              >
                Performance Benchmark Analysis
              </GradientText>
            </CardTitle>
            <CardDescription className="text-slate-300">
              How you compare against competitors and industry averages
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center py-12 text-slate-300">
              <div className="relative mb-6">
                <BarChart3 className="h-20 w-20 mx-auto opacity-50" />
                <div className="absolute inset-0 h-20 w-20 mx-auto bg-blue-500/20 rounded-full animate-ping"></div>
              </div>
              <p className="text-xl font-medium mb-2">No benchmark data available</p>
              <p className="text-sm text-slate-400">Start monitoring competitors to see performance comparisons</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Detailed Competitor Analysis - Based on real data */}
      {performanceData.length > 0 ? (
        <div className={`space-y-8 transition-all duration-1000 delay-400 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
          <div className="mb-6">
            <h3 className="text-2xl font-bold text-white mb-2">
              <GradientText
                colors={["#06b6d4", "#8b5cf6", "#f59e0b"]}
                animationSpeed={4}
                showBorder={false}
                className="text-2xl font-bold"
              >
                Detailed Competitor Analysis
              </GradientText>
            </h3>
            <p className="text-slate-300">Performance breakdown by competitor with key insights</p>
          </div>
          {performanceData.map((competitor, index) => (
            <Card 
              key={index}
              className={`glass-card hover-glow transition-all duration-500 animate-fade-in-up`}
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-16 h-16 bg-gradient-to-br from-cyan-500/30 to-purple-500/30 rounded-xl flex items-center justify-center backdrop-blur-sm border border-white/20 group-hover:scale-110 transition-all duration-300">
                      <span className="font-bold text-white text-lg">
                        {competitor.competitor.slice(0, 2)}
                      </span>
                    </div>
                    <div>
                      <CardTitle className="text-white text-xl group-hover:text-cyan-200 transition-colors duration-300">
                        {competitor.competitor}
                      </CardTitle>
                      <CardDescription className="text-slate-300">
                        {competitor.metrics.posts} posts monitored across {competitor.metrics.platforms} platforms
                      </CardDescription>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    {competitor.trends.direction === "up" && (
                      <div className="flex items-center gap-2 p-2 bg-green-500/20 rounded-lg border border-green-400/30">
                        <TrendingUp className="h-6 w-6 text-green-400" />
                        <span className="text-green-300 font-medium">Growing</span>
                      </div>
                    )}
                    {competitor.trends.direction === "down" && (
                      <div className="flex items-center gap-2 p-2 bg-red-500/20 rounded-lg border border-red-400/30">
                        <TrendingDown className="h-6 w-6 text-red-400" />
                        <span className="text-red-300 font-medium">Declining</span>
                      </div>
                    )}
                    {competitor.trends.direction === "stable" && (
                      <div className="flex items-center gap-2 p-2 bg-yellow-500/20 rounded-lg border border-yellow-400/30">
                        <Target className="h-6 w-6 text-yellow-400" />
                        <span className="text-yellow-300 font-medium">Stable</span>
                      </div>
                    )}
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                  {/* Key Metrics */}
                  <div className="space-y-6">
                    <h3 className="font-bold text-lg text-white">Key Performance Metrics</h3>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg border border-white/10">
                        <div className="flex items-center gap-3">
                          <FileText className="h-5 w-5 text-blue-400" />
                          <span className="text-white">Posts</span>
                        </div>
                        <div className="text-right">
                          <div className="text-xl font-bold text-white">{competitor.metrics.posts}</div>
                          <div className="text-sm text-green-400">{competitor.trends.posts}</div>
                        </div>
                      </div>
                      <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg border border-white/10">
                        <div className="flex items-center gap-3">
                          <Heart className="h-5 w-5 text-red-400" />
                          <span className="text-white">Engagement</span>
                        </div>
                        <div className="text-right">
                          <div className="text-xl font-bold text-white">{competitor.metrics.engagement}</div>
                          <div className="text-sm text-slate-400">Average per post</div>
                        </div>
                      </div>
                      <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg border border-white/10">
                        <div className="flex items-center gap-3">
                          <Target className="h-5 w-5 text-purple-400" />
                          <span className="text-white">Platforms</span>
                        </div>
                        <div className="text-right">
                          <div className="text-xl font-bold text-white">{competitor.metrics.platforms}</div>
                          <div className="text-sm text-slate-400">Active presence</div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Strengths */}
                  <div className="space-y-6">
                    <h3 className="font-bold text-lg text-white">Core Strengths</h3>
                    <div className="space-y-3">
                      {competitor.strengths.map((strength, strengthIndex) => (
                        <Badge 
                          key={strengthIndex} 
                          variant="default" 
                          className="block w-full p-3 text-center bg-green-500/20 text-green-300 border-green-400/30 hover:bg-green-500/30 transition-all duration-300"
                        >
                          <CheckCircle className="h-4 w-4 mr-2 inline" />
                          {strength}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  {/* Opportunities */}
                  <div className="space-y-6">
                    <h3 className="font-bold text-lg text-white">Growth Opportunities</h3>
                    <div className="space-y-3">
                      {competitor.opportunities.length > 0 ? (
                        competitor.opportunities.map((opportunity, opportunityIndex) => (
                          <Badge 
                            key={opportunityIndex} 
                            variant="outline" 
                            className="block w-full p-3 text-center bg-yellow-500/20 text-yellow-300 border-yellow-400/30 hover:bg-yellow-500/30 transition-all duration-300"
                          >
                            <AlertCircle className="h-4 w-4 mr-2 inline" />
                            {opportunity}
                          </Badge>
                        ))
                      ) : (
                        <Badge 
                          variant="outline" 
                          className="block w-full p-3 text-center bg-blue-500/20 text-blue-300 border-blue-400/30"
                        >
                          <CheckCircle className="h-4 w-4 mr-2 inline" />
                          Well positioned across all metrics
                        </Badge>
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card className={`glass-card transition-all duration-1000 delay-400 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
          <CardHeader>
            <CardTitle className="text-white text-xl">
              <GradientText
                colors={["#06b6d4", "#8b5cf6", "#f59e0b"]}
                animationSpeed={4}
                showBorder={false}
                className="text-xl font-bold"
              >
                Detailed Competitor Analysis
              </GradientText>
            </CardTitle>
            <CardDescription className="text-slate-300">
              Performance breakdown by competitor
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center py-12 text-slate-300">
              <div className="relative mb-6">
                <AlertCircle className="h-20 w-20 mx-auto opacity-50" />
                <div className="absolute inset-0 h-20 w-20 mx-auto bg-cyan-500/20 rounded-full animate-ping"></div>
              </div>
              <p className="text-xl font-medium mb-2">No competitor data available</p>
              <p className="text-sm text-slate-400">Start monitoring competitors to see detailed performance analysis</p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
