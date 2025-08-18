"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Lightbulb, TrendingUp, Users, Calendar, Sparkles } from "lucide-react"

interface ContentGapAnalysisProps {
  monitoringData?: any[]
}

export function ContentGapAnalysis({ monitoringData = [] }: ContentGapAnalysisProps) {
  const contentGaps = [
    {
      category: "Video Content",
      opportunity: "Behind by 40%",
      description: "Competitors are producing significantly more video content, especially short-form videos",
      potential: "High",
      difficulty: "Medium",
      topics: ["Product demos", "Behind-the-scenes", "User testimonials"],
      competitorExample: "Nike's daily workout videos get 2x engagement",
    },
    {
      category: "User-Generated Content",
      opportunity: "Behind by 25%",
      description: "Competitors are leveraging customer content more effectively",
      potential: "High",
      difficulty: "Low",
      topics: ["Customer reviews", "Unboxing videos", "Style challenges"],
      competitorExample: "Adidas' #MyAdidas campaign generated 50K posts",
    },
    {
      category: "Educational Content",
      opportunity: "Behind by 30%",
      description: "Competitors are positioning themselves as industry experts with how-to content",
      potential: "Medium",
      difficulty: "Medium",
      topics: ["Training tips", "Nutrition guides", "Injury prevention"],
      competitorExample: "Under Armour's fitness education series",
    },
    {
      category: "Sustainability Focus",
      opportunity: "Behind by 60%",
      description: "All competitors are heavily emphasizing eco-friendly initiatives",
      potential: "High",
      difficulty: "High",
      topics: ["Eco-friendly materials", "Recycling programs", "Carbon footprint"],
      competitorExample: "Nike's Move to Zero campaign",
    },
  ]

  const trendingTopics = [
    { topic: "Sustainable fashion", volume: 85, growth: "+23%" },
    { topic: "Home workouts", volume: 72, growth: "+18%" },
    { topic: "Mental health", volume: 68, growth: "+31%" },
    { topic: "Inclusive sizing", volume: 61, growth: "+15%" },
    { topic: "Tech integration", volume: 54, growth: "+27%" },
  ]

  return (
    <div className="space-y-6">
      {/* Content Gap Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Gaps Identified</CardTitle>
            <Lightbulb className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">12</div>
            <p className="text-xs text-muted-foreground">4 high-priority opportunities</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Potential Reach</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">2.4M</div>
            <p className="text-xs text-muted-foreground">Additional audience potential</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Quick Wins</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">5</div>
            <p className="text-xs text-muted-foreground">Low-effort, high-impact gaps</p>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Gap Analysis */}
      <Card>
        <CardHeader>
          <CardTitle>Content Gap Analysis</CardTitle>
          <CardDescription>Opportunities identified through competitor content analysis</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {contentGaps.map((gap, index) => (
              <div key={index} className="border rounded-lg p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold">{gap.category}</h3>
                      <Badge variant="destructive">{gap.opportunity}</Badge>
                      <Badge variant={gap.potential === "High" ? "default" : "secondary"}>
                        {gap.potential} Potential
                      </Badge>
                    </div>
                    <p className="text-muted-foreground mb-3">{gap.description}</p>
                    <div className="text-sm text-blue-600 dark:text-blue-400 mb-4">
                      <strong>Competitor Example:</strong> {gap.competitorExample}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-muted-foreground mb-1">Implementation</div>
                    <Badge variant="outline">{gap.difficulty} Difficulty</Badge>
                  </div>
                </div>

                <div className="mb-4">
                  <h4 className="text-sm font-medium mb-2">Suggested Topics:</h4>
                  <div className="flex flex-wrap gap-2">
                    {gap.topics.map((topic, topicIndex) => (
                      <Badge key={topicIndex} variant="secondary">
                        {topic}
                      </Badge>
                    ))}
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="text-sm">
                      <span className="text-muted-foreground">Estimated Impact: </span>
                      <span className="font-medium">+{Math.floor(Math.random() * 30 + 10)}% engagement</span>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm">
                      <Sparkles className="h-4 w-4 mr-2" />
                      Generate Ideas
                    </Button>
                    <Button size="sm">
                      <Calendar className="h-4 w-4 mr-2" />
                      Plan Content
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Trending Topics */}
      <Card>
        <CardHeader>
          <CardTitle>Trending Topics in Your Industry</CardTitle>
          <CardDescription>Topics your competitors are capitalizing on</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {trendingTopics.map((trend, index) => (
              <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-1">
                    <h3 className="font-medium">{trend.topic}</h3>
                    <Badge variant="outline" className="text-green-600 border-green-600">
                      {trend.growth}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-2">
                    <Progress value={trend.volume} className="w-32 h-2" />
                    <span className="text-sm text-muted-foreground">{trend.volume}% competitor coverage</span>
                  </div>
                </div>
                <Button variant="ghost" size="sm">
                  Explore
                </Button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
