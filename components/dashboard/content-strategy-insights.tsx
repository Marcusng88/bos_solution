"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { TrendingUp, TrendingDown, AlertTriangle, CheckCircle, Clock } from "lucide-react"

export function ContentStrategyInsights() {
  const strategicInsights = [
    {
      type: "opportunity",
      title: "Video Content Dominance",
      description: "Competitors are posting 3x more video content. Video posts get 65% higher engagement.",
      recommendation: "Increase video content production by 200% over next 30 days",
      impact: "High",
      urgency: "High",
      metrics: { current: 15, target: 45, unit: "videos/month" },
    },
    {
      type: "threat",
      title: "Nike's Athlete Partnership Surge",
      description: "Nike increased athlete collaborations by 40% this quarter, driving massive engagement.",
      recommendation: "Identify and partner with 3-5 micro-influencers in your niche",
      impact: "Medium",
      urgency: "Medium",
      metrics: { current: 2, target: 7, unit: "partnerships" },
    },
    {
      type: "trend",
      title: "Sustainability Messaging Rising",
      description: "All competitors emphasizing eco-friendly practices. 85% increase in sustainability content.",
      recommendation: "Develop comprehensive sustainability content series",
      impact: "High",
      urgency: "Low",
      metrics: { current: 5, target: 20, unit: "% of content" },
    },
  ]

  const contentPerformanceGaps = [
    { category: "Video Content", yourPerformance: 35, competitorAvg: 58, leader: 72, gap: -23 },
    { category: "User Generated Content", yourPerformance: 42, competitorAvg: 51, leader: 68, gap: -9 },
    { category: "Educational Posts", yourPerformance: 28, competitorAvg: 45, leader: 61, gap: -17 },
    { category: "Behind the Scenes", yourPerformance: 38, competitorAvg: 41, leader: 55, gap: -3 },
    { category: "Product Features", yourPerformance: 52, competitorAvg: 48, leader: 59, gap: +4 },
  ]

  const competitivePositioning = [
    { metric: "Content Volume", position: "3rd", trend: "stable", score: 72 },
    { metric: "Engagement Rate", position: "2nd", trend: "up", score: 85 },
    { metric: "Video Performance", position: "4th", trend: "down", score: 58 },
    { metric: "Brand Mentions", position: "3rd", trend: "up", score: 68 },
  ]

  return (
    <div className="space-y-6">
      {/* Strategic Insights */}
      <Card>
        <CardHeader>
          <CardTitle>Strategic Insights</CardTitle>
          <CardDescription>AI-powered competitive intelligence for your content strategy</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {strategicInsights.map((insight, index) => (
              <div key={index} className="flex items-start gap-4 p-4 border rounded-lg">
                <div className="mt-1">
                  {insight.type === "opportunity" && <CheckCircle className="h-5 w-5 text-green-500" />}
                  {insight.type === "threat" && <AlertTriangle className="h-5 w-5 text-orange-500" />}
                  {insight.type === "trend" && <TrendingUp className="h-5 w-5 text-blue-500" />}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="font-medium">{insight.title}</h3>
                    <Badge variant={insight.impact === "High" ? "destructive" : "secondary"}>
                      {insight.impact} Impact
                    </Badge>
                    <Badge variant={insight.urgency === "High" ? "destructive" : "outline"}>
                      {insight.urgency} Urgency
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground mb-3">{insight.description}</p>
                  <div className="p-3 bg-blue-50 dark:bg-blue-950/20 rounded-lg mb-3">
                    <p className="text-sm font-medium text-blue-900 dark:text-blue-100">
                      Recommendation: {insight.recommendation}
                    </p>
                  </div>
                  <div className="flex items-center gap-4 text-sm">
                    <span>
                      Current:{" "}
                      <strong>
                        {insight.metrics.current} {insight.metrics.unit}
                      </strong>
                    </span>
                    <span>
                      Target:{" "}
                      <strong>
                        {insight.metrics.target} {insight.metrics.unit}
                      </strong>
                    </span>
                    <Progress value={(insight.metrics.current / insight.metrics.target) * 100} className="w-24 h-2" />
                  </div>
                </div>
                <Button variant="outline" size="sm">
                  Act on This
                </Button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Content Performance Gaps */}
      <Card>
        <CardHeader>
          <CardTitle>Content Performance Analysis</CardTitle>
          <CardDescription>How your content performs vs competitors across categories</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {contentPerformanceGaps.map((gap, index) => (
              <div key={index} className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-medium">{gap.category}</span>
                  <div className="flex items-center gap-4 text-sm">
                    <span>
                      You: <strong>{gap.yourPerformance}%</strong>
                    </span>
                    <span className="text-muted-foreground">Avg: {gap.competitorAvg}%</span>
                    <span className="text-blue-600">Leader: {gap.leader}%</span>
                    <Badge variant={gap.gap > 0 ? "default" : "destructive"}>
                      {gap.gap > 0 ? "+" : ""}
                      {gap.gap}%
                    </Badge>
                  </div>
                </div>
                <div className="relative">
                  <Progress value={(gap.yourPerformance / gap.leader) * 100} className="h-3" />
                  <div className="absolute top-0 left-0 w-full h-3 flex items-center">
                    <div
                      className="w-1 h-4 bg-gray-400 -mt-0.5"
                      style={{ marginLeft: `${(gap.competitorAvg / gap.leader) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Competitive Positioning */}
      <Card>
        <CardHeader>
          <CardTitle>Competitive Positioning</CardTitle>
          <CardDescription>Your current market position across key content metrics</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {competitivePositioning.map((position, index) => (
              <div key={index} className="p-4 border rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium">{position.metric}</h3>
                  <div className="flex items-center gap-2">
                    {position.trend === "up" && <TrendingUp className="h-4 w-4 text-green-500" />}
                    {position.trend === "down" && <TrendingDown className="h-4 w-4 text-red-500" />}
                    {position.trend === "stable" && <Clock className="h-4 w-4 text-gray-500" />}
                    <Badge variant="outline">{position.position}</Badge>
                  </div>
                </div>
                <div className="space-y-2">
                  <Progress value={position.score} className="h-2" />
                  <div className="flex justify-between text-sm text-muted-foreground">
                    <span>Score: {position.score}/100</span>
                    <span
                      className={
                        position.trend === "up"
                          ? "text-green-600"
                          : position.trend === "down"
                            ? "text-red-600"
                            : "text-gray-600"
                      }
                    >
                      {position.trend === "up" ? "Improving" : position.trend === "down" ? "Declining" : "Stable"}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
