"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { TrendingUp, TrendingDown, Target, Users, Heart, MessageCircle } from "lucide-react"

interface CompetitorPerformanceProps {
  timeRange: string
  monitoringData?: any[]
}

export function CompetitorPerformance({ timeRange, monitoringData = [] }: CompetitorPerformanceProps) {
  const performanceData = [
    {
      competitor: "Nike",
      metrics: {
        followers: 142000000,
        engagement: 4.8,
        posts: 156,
        avgLikes: 45600,
        avgComments: 2340,
        shareOfVoice: 34.2,
      },
      trends: {
        followers: "+2.3%",
        engagement: "+0.8%",
        posts: "+12%",
        direction: "up",
      },
      strengths: ["Video content", "Athlete partnerships", "Brand storytelling"],
      weaknesses: ["Sustainability messaging", "User-generated content"],
    },
    {
      competitor: "Adidas",
      metrics: {
        followers: 89000000,
        engagement: 3.9,
        posts: 134,
        avgLikes: 28900,
        avgComments: 1560,
        shareOfVoice: 28.7,
      },
      trends: {
        followers: "+1.8%",
        engagement: "-0.3%",
        posts: "+8%",
        direction: "mixed",
      },
      strengths: ["Sustainability focus", "Community building", "Innovation messaging"],
      weaknesses: ["Video engagement", "Influencer partnerships"],
    },
    {
      competitor: "Under Armour",
      metrics: {
        followers: 34000000,
        engagement: 3.2,
        posts: 98,
        avgLikes: 12400,
        avgComments: 890,
        shareOfVoice: 15.3,
      },
      trends: {
        followers: "+3.1%",
        engagement: "+1.2%",
        posts: "+15%",
        direction: "up",
      },
      strengths: ["Tech innovation", "Performance focus", "Athlete training"],
      weaknesses: ["Brand awareness", "Content variety"],
    },
  ]

  const benchmarkMetrics = [
    { metric: "Avg. Engagement Rate", yourValue: 3.5, industry: 3.8, leader: 4.8, unit: "%" },
    { metric: "Posts per Week", yourValue: 8, industry: 12, leader: 18, unit: "" },
    { metric: "Video Content %", yourValue: 35, industry: 45, leader: 60, unit: "%" },
    { metric: "Response Time", yourValue: 4.2, industry: 2.8, leader: 1.5, unit: "hrs" },
  ]

  return (
    <div className="space-y-6">
      {/* Performance Benchmark */}
      <Card>
        <CardHeader>
          <CardTitle>Performance Benchmark</CardTitle>
          <CardDescription>How you compare against competitors and industry averages</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {benchmarkMetrics.map((benchmark, index) => (
              <div key={index} className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-medium">{benchmark.metric}</span>
                  <div className="flex items-center gap-4 text-sm">
                    <span>
                      You:{" "}
                      <strong>
                        {benchmark.yourValue}
                        {benchmark.unit}
                      </strong>
                    </span>
                    <span className="text-muted-foreground">
                      Industry: {benchmark.industry}
                      {benchmark.unit}
                    </span>
                    <span className="text-blue-600">
                      Leader: {benchmark.leader}
                      {benchmark.unit}
                    </span>
                  </div>
                </div>
                <div className="relative">
                  <Progress value={(benchmark.yourValue / benchmark.leader) * 100} className="h-3" />
                  <div className="absolute top-0 left-0 w-full h-3 flex items-center">
                    <div
                      className="w-1 h-4 bg-gray-400 -mt-0.5"
                      style={{ marginLeft: `${(benchmark.industry / benchmark.leader) * 100}%` }}
                    />
                  </div>
                </div>
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>0{benchmark.unit}</span>
                  <span>
                    {benchmark.leader}
                    {benchmark.unit}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Detailed Competitor Analysis */}
      <div className="space-y-6">
        {performanceData.map((competitor, index) => (
          <Card key={index}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gray-100 dark:bg-gray-800 rounded-lg flex items-center justify-center">
                    <span className="font-semibold text-sm">{competitor.competitor.slice(0, 2)}</span>
                  </div>
                  <div>
                    <CardTitle>{competitor.competitor}</CardTitle>
                    <CardDescription>{competitor.metrics.shareOfVoice}% share of voice</CardDescription>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {competitor.trends.direction === "up" && <TrendingUp className="h-5 w-5 text-green-500" />}
                  {competitor.trends.direction === "down" && <TrendingDown className="h-5 w-5 text-red-500" />}
                  {competitor.trends.direction === "mixed" && <Target className="h-5 w-5 text-yellow-500" />}
                  <Badge variant={competitor.trends.direction === "up" ? "default" : "secondary"}>
                    {competitor.trends.direction === "up"
                      ? "Growing"
                      : competitor.trends.direction === "down"
                        ? "Declining"
                        : "Mixed"}
                  </Badge>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Key Metrics */}
                <div className="space-y-4">
                  <h3 className="font-medium">Key Metrics</h3>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Users className="h-4 w-4 text-muted-foreground" />
                        <span className="text-sm">Followers</span>
                      </div>
                      <div className="text-right">
                        <div className="font-medium">{(competitor.metrics.followers / 1000000).toFixed(0)}M</div>
                        <div className="text-xs text-green-600">{competitor.trends.followers}</div>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Heart className="h-4 w-4 text-muted-foreground" />
                        <span className="text-sm">Engagement</span>
                      </div>
                      <div className="text-right">
                        <div className="font-medium">{competitor.metrics.engagement}%</div>
                        <div
                          className={`text-xs ${competitor.trends.engagement.startsWith("+") ? "text-green-600" : "text-red-600"}`}
                        >
                          {competitor.trends.engagement}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <MessageCircle className="h-4 w-4 text-muted-foreground" />
                        <span className="text-sm">Avg. Likes</span>
                      </div>
                      <div className="text-right">
                        <div className="font-medium">{(competitor.metrics.avgLikes / 1000).toFixed(0)}K</div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Strengths */}
                <div className="space-y-4">
                  <h3 className="font-medium">Strengths</h3>
                  <div className="space-y-2">
                    {competitor.strengths.map((strength, strengthIndex) => (
                      <Badge key={strengthIndex} variant="default" className="mr-2 mb-2">
                        {strength}
                      </Badge>
                    ))}
                  </div>
                </div>

                {/* Weaknesses */}
                <div className="space-y-4">
                  <h3 className="font-medium">Opportunities</h3>
                  <div className="space-y-2">
                    {competitor.weaknesses.map((weakness, weaknessIndex) => (
                      <Badge key={weaknessIndex} variant="outline" className="mr-2 mb-2">
                        {weakness}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
