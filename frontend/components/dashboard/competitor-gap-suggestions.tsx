"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import { useToast } from "@/hooks/use-toast"
import { Lightbulb, Target, TrendingUp, Calendar, Sparkles, ThumbsUp, Edit3, X } from "lucide-react"

export function CompetitorGapSuggestions() {
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editedContent, setEditedContent] = useState("")
  const { toast } = useToast()

  const gapSuggestions = [
    {
      id: 1,
      gapType: "Video Content",
      competitor: "Nike",
      opportunity: "Behind by 40%",
      title: "Workout Tutorial Series",
      content:
        "Create a 5-part workout tutorial series featuring your products. Nike's fitness videos get 2x engagement. Focus on beginner-friendly exercises with product integration.",
      platform: "Instagram Reels",
      impact: "High",
      difficulty: "Medium",
      estimatedReach: "45K",
      confidence: 92,
      competitorExample: "Nike's daily workout videos average 50K views",
    },
    {
      id: 2,
      gapType: "Sustainability",
      competitor: "Adidas",
      opportunity: "Behind by 60%",
      title: "Eco-Friendly Manufacturing Story",
      content:
        "Share behind-the-scenes content about your sustainable practices. Adidas' eco-content performs 3x better. Highlight recycled materials and carbon reduction efforts.",
      platform: "LinkedIn + Instagram",
      impact: "High",
      difficulty: "Low",
      estimatedReach: "32K",
      confidence: 88,
      competitorExample: "Adidas' #MyAdidas sustainability posts get 40K+ engagements",
    },
    {
      id: 3,
      gapType: "User Generated Content",
      competitor: "Under Armour",
      opportunity: "Behind by 25%",
      title: "Customer Transformation Stories",
      content:
        "Launch a campaign featuring customer fitness journeys. Under Armour's UGC campaigns drive 4x engagement. Create a branded hashtag and incentivize sharing.",
      platform: "TikTok + Instagram",
      impact: "Medium",
      difficulty: "Low",
      estimatedReach: "28K",
      confidence: 85,
      competitorExample: "Under Armour's #WillFindAWay campaign generated 100K posts",
    },
    {
      id: 4,
      gapType: "Educational Content",
      competitor: "All Competitors",
      opportunity: "Behind by 30%",
      title: "Nutrition & Training Guide Series",
      content:
        "Create educational content about fitness nutrition and training tips. All competitors are positioning as fitness experts. Partner with trainers and nutritionists.",
      platform: "YouTube + Blog",
      impact: "Medium",
      difficulty: "High",
      estimatedReach: "22K",
      confidence: 90,
      competitorExample: "Industry average: 15 educational posts/month vs your 5",
    },
  ]

  const handleEdit = (suggestion: (typeof gapSuggestions)[0]) => {
    setEditingId(suggestion.id)
    setEditedContent(suggestion.content)
  }

  const handleSave = (id: number) => {
    setEditingId(null)
    toast({
      title: "Content updated",
      description: "Your gap-based content has been saved.",
    })
  }

  const handleApprove = (suggestion: (typeof gapSuggestions)[0]) => {
    toast({
      title: "Content approved",
      description: `${suggestion.title} has been added to your content strategy.`,
    })
  }

  const handleReject = (id: number) => {
    toast({
      title: "Opportunity dismissed",
      description: "This gap suggestion has been removed from your queue.",
    })
  }

  return (
    <div className="space-y-6">
      {/* Gap Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">High-Impact Gaps</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">4</div>
            <p className="text-xs text-muted-foreground">Ready to capitalize on</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Potential Reach</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">127K</div>
            <p className="text-xs text-muted-foreground">Additional audience</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Quick Wins</CardTitle>
            <Lightbulb className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">2</div>
            <p className="text-xs text-muted-foreground">Low-effort opportunities</p>
          </CardContent>
        </Card>
      </div>

      {/* Gap-Based Content Suggestions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-blue-600" />
            Competitor Gap Opportunities
          </CardTitle>
          <CardDescription>AI-generated content ideas based on competitor analysis</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {gapSuggestions.map((suggestion) => (
            <Card key={suggestion.id} className="p-6 border-l-4 border-l-blue-500">
              <div className="space-y-4">
                {/* Header */}
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold">{suggestion.title}</h3>
                      <Badge variant="destructive">{suggestion.opportunity}</Badge>
                      <Badge variant={suggestion.impact === "High" ? "default" : "secondary"}>
                        {suggestion.impact} Impact
                      </Badge>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-muted-foreground mb-3">
                      <span>
                        Gap Type: <strong>{suggestion.gapType}</strong>
                      </span>
                      <span>
                        vs <strong>{suggestion.competitor}</strong>
                      </span>
                      <span>
                        Platform: <strong>{suggestion.platform}</strong>
                      </span>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-muted-foreground mb-1">Confidence</div>
                    <Badge variant="outline">{suggestion.confidence}%</Badge>
                  </div>
                </div>

                {/* Content */}
                {editingId === suggestion.id ? (
                  <div className="space-y-3">
                    <Textarea
                      value={editedContent}
                      onChange={(e) => setEditedContent(e.target.value)}
                      className="min-h-[100px]"
                    />
                    <div className="flex gap-2">
                      <Button size="sm" onClick={() => handleSave(suggestion.id)}>
                        Save Changes
                      </Button>
                      <Button variant="outline" size="sm" onClick={() => setEditingId(null)}>
                        Cancel
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <p className="text-sm leading-relaxed">{suggestion.content}</p>
                    <div className="p-3 bg-muted/50 rounded-lg">
                      <div className="text-sm">
                        <strong className="text-blue-600">Competitor Insight:</strong> {suggestion.competitorExample}
                      </div>
                    </div>
                  </div>
                )}

                {/* Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-3 bg-muted/30 rounded-lg">
                  <div>
                    <div className="text-sm text-muted-foreground">Estimated Reach</div>
                    <div className="font-medium">{suggestion.estimatedReach}</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">Implementation</div>
                    <div className="font-medium">{suggestion.difficulty} Difficulty</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">Expected Impact</div>
                    <div className="font-medium">+{Math.floor(Math.random() * 30 + 15)}% engagement</div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  <Button size="sm" onClick={() => handleApprove(suggestion)} className="flex-1">
                    <ThumbsUp className="mr-2 h-3 w-3" />
                    Add to Strategy
                  </Button>
                  <Button variant="outline" size="sm" onClick={() => handleEdit(suggestion)}>
                    <Edit3 className="h-3 w-3" />
                  </Button>
                  <Button variant="outline" size="sm">
                    <Calendar className="h-3 w-3" />
                  </Button>
                  <Button variant="outline" size="sm" onClick={() => handleReject(suggestion.id)}>
                    <X className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}
