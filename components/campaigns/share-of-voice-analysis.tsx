"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { TrendingUp, TrendingDown, Target, Users, Volume2, BarChart3 } from "lucide-react"

interface ShareOfVoiceAnalysisProps {
  timeRange: string
}

export function ShareOfVoiceAnalysis({ timeRange }: ShareOfVoiceAnalysisProps) {
  const shareOfVoiceData = [
    {
      brand: "Nike",
      share: 34.2,
      change: +2.1,
      mentions: 45600,
      sentiment: 78,
      trend: "up",
      color: "bg-blue-500",
    },
    {
      brand: "Adidas",
      share: 28.7,
      change: -1.3,
      mentions: 38200,
      sentiment: 72,
      trend: "down",
      color: "bg-green-500",
    },
    {
      brand: "You",
      share: 18.4,
      change: +3.2,
      mentions: 24500,
      sentiment: 81,
      trend: "up",
      color: "bg-purple-500",
    },
    {
      brand: "Under Armour",
      share: 12.1,
      change: -0.8,
      mentions: 16100,
      sentiment: 69,
      trend: "down",
      color: "bg-orange-500",
    },
    {
      brand: "Others",
      share: 6.6,
      change: -3.2,
      mentions: 8800,
      sentiment: 65,
      trend: "down",
      color: "bg-gray-400",
    },
  ]

  const platformBreakdown = [
    { platform: "Instagram", yourShare: 22.1, leader: "Nike (38.4%)", gap: -16.3 },
    { platform: "Twitter", yourShare: 19.8, leader: "Adidas (31.2%)", gap: -11.4 },
    { platform: "TikTok", yourShare: 15.2, leader: "Nike (42.1%)", gap: -26.9 },
    { platform: "YouTube", yourShare: 16.7, leader: "Nike (35.8%)", gap: -19.1 },
    { platform: "LinkedIn", yourShare: 24.3, leader: "You (24.3%)", gap: 0 },
  ]

  const topicAnalysis = [
    { topic: "Sustainability", yourShare: 12.4, marketShare: 28.7, opportunity: "High" },
    { topic: "Fitness Training", yourShare: 31.2, marketShare: 35.1, opportunity: "Medium" },
    { topic: "Product Innovation", yourShare: 18.9, marketShare: 22.3, opportunity: "Medium" },
    { topic: "Athlete Partnerships", yourShare: 8.1, marketShare: 41.2, opportunity: "High" },
    { topic: "Lifestyle Content", yourShare: 29.4, marketShare: 26.8, opportunity: "Low" },
  ]

  return (
    <div className="space-y-6">
      {/* Share of Voice Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Your Share of Voice</CardTitle>
            <Volume2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">18.4%</div>
            <p className="text-xs text-green-600">+3.2% from last period</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Market Position</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">3rd</div>
            <p className="text-xs text-muted-foreground">Out of major competitors</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Mentions</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">24.5K</div>
            <p className="text-xs text-green-600">+15.8% from last period</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Sentiment Score</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">81%</div>
            <p className="text-xs text-muted-foreground">Highest among competitors</p>
          </CardContent>
        </Card>
      </div>

      {/* Share of Voice Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle>Share of Voice Breakdown</CardTitle>
          <CardDescription>Market share of brand mentions and conversations</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {shareOfVoiceData.map((brand, index) => (
              <div key={index} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`w-4 h-4 rounded ${brand.color}`} />
                    <span className="font-medium">{brand.brand}</span>
                    {brand.trend === "up" ? (
                      <TrendingUp className="h-4 w-4 text-green-500" />
                    ) : (
                      <TrendingDown className="h-4 w-4 text-red-500" />
                    )}
                  </div>
                  <div className="flex items-center gap-4 text-sm">
                    <span>{brand.mentions.toLocaleString()} mentions</span>
                    <span>Sentiment: {brand.sentiment}%</span>
                    <Badge variant={brand.change > 0 ? "default" : "destructive"}>
                      {brand.change > 0 ? "+" : ""}
                      {brand.change}%
                    </Badge>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Progress value={brand.share} className="flex-1 h-3" />
                  <span className="text-sm font-medium w-12">{brand.share}%</span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Platform Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle>Platform Share of Voice</CardTitle>
          <CardDescription>Your market share across different social media platforms</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {platformBreakdown.map((platform, index) => (
              <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium">{platform.platform}</h3>
                    <div className="flex items-center gap-2">
                      <Badge variant={platform.gap === 0 ? "default" : "outline"}>
                        {platform.gap === 0 ? "Leading" : `${platform.gap}% behind`}
                      </Badge>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <span>Your Share: {platform.yourShare}%</span>
                    <span>Leader: {platform.leader}</span>
                  </div>
                  <Progress value={platform.yourShare} className="mt-2 h-2" />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Topic Analysis */}
      <Card>
        <CardHeader>
          <CardTitle>Topic Share of Voice</CardTitle>
          <CardDescription>Your share of conversation across key topics</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {topicAnalysis.map((topic, index) => (
              <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium">{topic.topic}</h3>
                    <Badge
                      variant={
                        topic.opportunity === "High"
                          ? "destructive"
                          : topic.opportunity === "Medium"
                            ? "secondary"
                            : "outline"
                      }
                    >
                      {topic.opportunity} Opportunity
                    </Badge>
                  </div>
                  <div className="grid grid-cols-2 gap-4 mb-2">
                    <div>
                      <div className="text-sm text-muted-foreground">Your Share</div>
                      <div className="font-medium">{topic.yourShare}%</div>
                    </div>
                    <div>
                      <div className="text-sm text-muted-foreground">Market Share Available</div>
                      <div className="font-medium">{topic.marketShare}%</div>
                    </div>
                  </div>
                  <Progress value={(topic.yourShare / topic.marketShare) * 100} className="h-2" />
                </div>
                <Button variant="outline" size="sm" className="ml-4 bg-transparent">
                  Expand
                </Button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
