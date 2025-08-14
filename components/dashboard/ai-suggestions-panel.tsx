"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import { useToast } from "@/hooks/use-toast"
import { Sparkles, ThumbsUp, Edit3, X, RefreshCw, ImageIcon, Target } from "lucide-react"

interface AISuggestionsPanelProps {
  selectedDate: Date
}

const aiSuggestions = [
  {
    id: 1,
    type: "gap-based",
    platform: "Instagram",
    title: "Workout Tutorial - Fill Video Gap",
    content:
      "🏋️‍♀️ Quick 5-minute morning workout to start your day strong! Our gear is designed to move with you. What's your favorite morning exercise? #MorningWorkout #FitnessMotivation #ActiveLifestyle",
    imageUrl: "/summer-fashion-collection.png",
    engagement: "High",
    confidence: 94,
    gapType: "Video Content",
    competitorInsight: "Nike's workout videos get 2x engagement - capitalize on this gap",
  },
  {
    id: 2,
    type: "competitor-response",
    platform: "LinkedIn",
    title: "Sustainability Response to Adidas",
    content:
      "Our commitment to the planet goes beyond products. Here's how we're reducing our carbon footprint by 40% this year through innovative manufacturing processes and renewable energy. #Sustainability #Innovation #ResponsibleBusiness",
    imageUrl: "/design-studio-bts.png",
    engagement: "High",
    confidence: 91,
    gapType: "Sustainability",
    competitorInsight: "Adidas launched major sustainability campaign - respond with your initiatives",
  },
  {
    id: 3,
    type: "trending-topic",
    platform: "TikTok",
    title: "Mental Health Awareness Trend",
    content:
      "Your mental health matters as much as your physical health. Here are 3 simple mindfulness exercises you can do anywhere. Remember: progress over perfection. 🧠💪 #MentalHealthMatters #Mindfulness #WellnessJourney",
    imageUrl: "/fashion-trends-2024.png",
    engagement: "Very High",
    confidence: 96,
    gapType: "Wellness Content",
    competitorInsight: "Mental health content trending across all competitors - join the conversation",
  },
]

export function AISuggestionsPanel({ selectedDate }: AISuggestionsPanelProps) {
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editedContent, setEditedContent] = useState("")
  const { toast } = useToast()

  const handleEdit = (suggestion: (typeof aiSuggestions)[0]) => {
    setEditingId(suggestion.id)
    setEditedContent(suggestion.content)
  }

  const handleSave = (id: number) => {
    setEditingId(null)
    toast({
      title: "Content updated",
      description: "Your AI-generated content has been saved.",
    })
  }

  const handleApprove = (suggestion: (typeof aiSuggestions)[0]) => {
    toast({
      title: "Content approved",
      description: `${suggestion.title} has been scheduled for ${suggestion.platform}.`,
    })
  }

  const handleRegenerate = (id: number) => {
    toast({
      title: "Regenerating content",
      description: "AI is creating a new version based on latest competitor insights...",
    })
  }

  const handleReject = (id: number) => {
    toast({
      title: "Content rejected",
      description: "This suggestion has been removed from your queue.",
    })
  }

  const getSuggestionTypeIcon = (type: string) => {
    switch (type) {
      case "gap-based":
        return <Target className="h-3 w-3" />
      case "competitor-response":
        return <RefreshCw className="h-3 w-3" />
      default:
        return <Sparkles className="h-3 w-3" />
    }
  }

  const getSuggestionTypeBadge = (type: string) => {
    switch (type) {
      case "gap-based":
        return (
          <Badge variant="default" className="text-xs">
            Gap Opportunity
          </Badge>
        )
      case "competitor-response":
        return (
          <Badge variant="destructive" className="text-xs">
            Competitor Response
          </Badge>
        )
      default:
        return (
          <Badge variant="secondary" className="text-xs">
            Trending Topic
          </Badge>
        )
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-blue-600" />
          AI Content Suggestions
        </CardTitle>
        <CardDescription>Competitor-driven content ideas tailored for your audience</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {aiSuggestions.map((suggestion) => (
          <Card key={suggestion.id} className="p-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Badge variant="outline">{suggestion.platform}</Badge>
                  {getSuggestionTypeBadge(suggestion.type)}
                  <Badge variant="secondary" className="text-xs">
                    {suggestion.confidence}% match
                  </Badge>
                </div>
                <Badge
                  variant={
                    suggestion.engagement === "Very High"
                      ? "default"
                      : suggestion.engagement === "High"
                        ? "default"
                        : "secondary"
                  }
                  className="text-xs"
                >
                  {suggestion.engagement} engagement
                </Badge>
              </div>

              <h4 className="font-medium">{suggestion.title}</h4>

              {/* Competitor Insight */}
              <div className="p-2 bg-blue-50 dark:bg-blue-950/20 rounded border-l-2 border-blue-500">
                <div className="flex items-center gap-1 mb-1">
                  {getSuggestionTypeIcon(suggestion.type)}
                  <span className="text-xs font-medium text-blue-900 dark:text-blue-100">
                    {suggestion.gapType} Opportunity
                  </span>
                </div>
                <p className="text-xs text-blue-700 dark:text-blue-300">{suggestion.competitorInsight}</p>
              </div>

              {suggestion.imageUrl && (
                <div className="relative">
                  <img
                    src={suggestion.imageUrl || "/placeholder.svg"}
                    alt={suggestion.title}
                    className="w-full h-32 object-cover rounded-lg"
                  />
                  <div className="absolute top-2 right-2">
                    <Badge variant="secondary" className="text-xs">
                      <ImageIcon className="h-3 w-3 mr-1" />
                      AI Generated
                    </Badge>
                  </div>
                </div>
              )}

              {editingId === suggestion.id ? (
                <div className="space-y-2">
                  <Textarea
                    value={editedContent}
                    onChange={(e) => setEditedContent(e.target.value)}
                    className="min-h-[100px]"
                  />
                  <div className="flex gap-2">
                    <Button size="sm" onClick={() => handleSave(suggestion.id)}>
                      Save
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => setEditingId(null)}>
                      Cancel
                    </Button>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">{suggestion.content}</p>
              )}

              <div className="flex gap-2">
                <Button size="sm" onClick={() => handleApprove(suggestion)} className="flex-1">
                  <ThumbsUp className="mr-2 h-3 w-3" />
                  Approve
                </Button>
                <Button variant="outline" size="sm" onClick={() => handleEdit(suggestion)}>
                  <Edit3 className="h-3 w-3" />
                </Button>
                <Button variant="outline" size="sm" onClick={() => handleRegenerate(suggestion.id)}>
                  <RefreshCw className="h-3 w-3" />
                </Button>
                <Button variant="outline" size="sm" onClick={() => handleReject(suggestion.id)}>
                  <X className="h-3 w-3" />
                </Button>
              </div>
            </div>
          </Card>
        ))}

        <Button variant="outline" className="w-full bg-transparent">
          <RefreshCw className="mr-2 h-4 w-4" />
          Generate More Gap-Based Suggestions
        </Button>
      </CardContent>
    </Card>
  )
}
