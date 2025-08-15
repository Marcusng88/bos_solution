"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import { useToast } from "@/hooks/use-toast"
import { Sparkles, ThumbsUp, Edit3, X, RefreshCw, ImageIcon, Target, Loader2 } from "lucide-react"
import { apiClient } from "@/lib/api-client"

interface AISuggestionsPanelProps {
  selectedDate: Date
  userId: string
}

interface AISuggestion {
  id: number
  type: string
  platform: string
  title: string
  content: string
  engagement: string
  confidence: number
  gap_type: string
  competitor_insight: string
}

export function AISuggestionsPanel({ selectedDate, userId }: AISuggestionsPanelProps) {
  const [aiSuggestions, setAiSuggestions] = useState<AISuggestion[]>([])
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editedContent, setEditedContent] = useState("")
  const [isLoading, setIsLoading] = useState(true)
  const [isRegenerating, setIsRegenerating] = useState(false)
  const { toast } = useToast()

  useEffect(() => {
    loadAISuggestions()
  }, [userId])

  const loadAISuggestions = async () => {
    try {
      setIsLoading(true)
      const suggestions = await apiClient.getAISuggestions(userId) as AISuggestion[]
      setAiSuggestions(suggestions)
    } catch (error) {
      console.error('Error loading AI suggestions:', error)
      toast({
        title: "Error loading suggestions",
        description: "Failed to load AI suggestions. Please try again.",
        variant: "destructive"
      })
      
      // Fallback suggestions
      setAiSuggestions([
        {
          id: 1,
          type: "gap-based",
          platform: "Instagram",
          title: "Fitness Content - Fill Video Gap",
          content: "💪 Transform your morning routine with these 5-minute energizing exercises! Perfect for busy schedules. What's your go-to morning motivation? #MorningWorkout #FitnessMotivation #ActiveLifestyle",
          engagement: "High",
          confidence: 94,
          gap_type: "Fitness",
          competitor_insight: "Competitors are 46% ahead in fitness content"
        }
      ])
    } finally {
      setIsLoading(false)
    }
  }

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

  const handleRegenerate = async (id: number) => {
    try {
      setIsRegenerating(true)
      toast({
        title: "Regenerating content",
        description: "AI is creating a new version based on latest competitor insights...",
      })
      
      // Trigger AI analysis and reload suggestions
      await apiClient.getAIAnalysis(userId, "content_generation")
      await loadAISuggestions()
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to regenerate content. Please try again.",
        variant: "destructive"
      })
    } finally {
      setIsRegenerating(false)
    }
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
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-8 w-8 animate-spin" />
          </div>
        ) : (
          aiSuggestions.map((suggestion) => (
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
                    {suggestion.gap_type} Opportunity
                  </span>
                </div>
                <p className="text-xs text-blue-700 dark:text-blue-300">{suggestion.competitor_insight}</p>
              </div>

              <div className="relative">
                <img
                  src="/placeholder.svg"
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
        ))
        )}

        <Button 
          variant="outline" 
          className="w-full bg-transparent" 
          onClick={() => handleRegenerate(0)}
          disabled={isRegenerating}
        >
          {isRegenerating ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <RefreshCw className="mr-2 h-4 w-4" />
          )}
          Generate More Gap-Based Suggestions
        </Button>
      </CardContent>
    </Card>
  )
}
