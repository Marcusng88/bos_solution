"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { TrendingUp, TrendingDown, AlertTriangle, CheckCircle, Clock, Target } from "lucide-react"

interface CompetitorOverviewProps {
  timeRange: string
  monitoringData?: any[]
}

export function CompetitorOverview({ timeRange, monitoringData = [] }: CompetitorOverviewProps) {
  const insights = [
    {
      type: "opportunity",
      title: "Video Content Gap",
      description: "Competitors are posting 40% more video content. Consider increasing video production.",
      impact: "High",
      confidence: 92,
    },
    {
      type: "threat",
      title: "Nike's New Campaign",
      description: "Nike launched a major social campaign targeting your key demographic.",
      impact: "Medium",
      confidence: 87,
    },
    {
      type: "trend",
      title: "Sustainability Focus",
      description: "All competitors are emphasizing eco-friendly messaging in recent posts.",
      impact: "High",
      confidence: 95,
    },
  ]

  const competitorMetrics = [
    {
      name: "Nike",
      shareOfVoice: 34.2,
      engagement: 4.8,
      postFrequency: 12,
      trend: "up",
    },
    {
      name: "Adidas",
      shareOfVoice: 28.7,
      engagement: 3.9,
      postFrequency: 8,
      trend: "down",
    },
    {
      name: "Under Armour",
      shareOfVoice: 15.3,
      engagement: 3.2,
      postFrequency: 6,
      trend: "up",
    },
  ]

  return (
    <div className="space-y-6">
      {/* AI Insights */}
      <Card>
        <CardHeader>
          <CardTitle>AI Competitive Insights</CardTitle>
          <CardDescription>Key findings from competitor analysis</CardDescription>
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
                    <h3 className="font-medium">{insight.title}</h3>
                    <Badge variant={insight.impact === "High" ? "destructive" : "secondary"}>
                      {insight.impact} Impact
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground mb-2">{insight.description}</p>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-muted-foreground">Confidence:</span>
                    <Progress value={insight.confidence} className="w-20 h-2" />
                    <span className="text-xs font-medium">{insight.confidence}%</span>
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

      {/* Competitor Performance Matrix */}
      <Card>
        <CardHeader>
          <CardTitle>Competitor Performance Matrix</CardTitle>
          <CardDescription>Comparative analysis across key metrics</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {competitorMetrics.map((competitor, index) => (
              <div key={index} className="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 border rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-gray-100 dark:bg-gray-800 rounded-lg flex items-center justify-center">
                    <span className="font-semibold text-xs">{competitor.name.slice(0, 2)}</span>
                  </div>
                  <div>
                    <h3 className="font-medium">{competitor.name}</h3>
                    <div className="flex items-center gap-1">
                      {competitor.trend === "up" ? (
                        <TrendingUp className="h-3 w-3 text-green-500" />
                      ) : (
                        <TrendingDown className="h-3 w-3 text-red-500" />
                      )}
                      <span className="text-xs text-muted-foreground">
                        {competitor.trend === "up" ? "Growing" : "Declining"}
                      </span>
                    </div>
                  </div>
                </div>
                <div>
                  <div className="text-sm font-medium">Share of Voice</div>
                  <div className="text-lg font-bold">{competitor.shareOfVoice}%</div>
                </div>
                <div>
                  <div className="text-sm font-medium">Avg. Engagement</div>
                  <div className="text-lg font-bold">{competitor.engagement}%</div>
                </div>
                <div>
                  <div className="text-sm font-medium">Posts/Week</div>
                  <div className="text-lg font-bold">{competitor.postFrequency}</div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Recommended Actions</CardTitle>
          <CardDescription>Based on competitive intelligence analysis</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 border rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Target className="h-4 w-4 text-blue-500" />
                <h3 className="font-medium">Increase Video Content</h3>
              </div>
              <p className="text-sm text-muted-foreground mb-3">
                Competitors are outperforming with video content. Recommended increase: 60%
              </p>
              <Button size="sm" className="w-full">
                Create Video Strategy
              </Button>
            </div>
            <div className="p-4 border rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Clock className="h-4 w-4 text-green-500" />
                <h3 className="font-medium">Optimize Posting Times</h3>
              </div>
              <p className="text-sm text-muted-foreground mb-3">
                Competitors are posting when your audience is most active. Adjust schedule.
              </p>
              <Button size="sm" variant="outline" className="w-full bg-transparent">
                Update Schedule
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
