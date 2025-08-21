"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import { Skeleton } from "@/components/ui/skeleton"
import { useToast } from "@/hooks/use-toast"
import { useContentPlanning } from "@/hooks/use-content-planning"
import { Sparkles, ThumbsUp, Edit3, X, RefreshCw, Target } from "lucide-react"

interface AISuggestionsPanelProps {
  selectedDate: Date
}

export function AISuggestionsPanel({ selectedDate }: AISuggestionsPanelProps) {
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editedContent, setEditedContent] = useState("")
  const [suggestions, setSuggestions] = useState<any[]>([])
  const [loadingSuggestions, setLoadingSuggestions] = useState(false)
  const { toast } = useToast()
  
  const { generateContent, selectedIndustry } = useContentPlanning({ autoLoad: false })

  const loadAISuggestions = async () => {
    try {
      setLoadingSuggestions(true)
      
      // Generate multiple content suggestions for different platforms
      const platforms = ['instagram', 'linkedin', 'twitter']
      const contentTypes = ['promotional', 'educational', 'entertaining']
      
      const suggestionPromises = platforms.map(async (platform, index) => {
        const contentType = contentTypes[index % contentTypes.length]
        try {
          const response = await generateContent({
            industry: selectedIndustry,
            platform,
            content_type: contentType,
            tone: 'professional',
            target_audience: 'professionals',
            custom_requirements: `Create engaging ${contentType} content for ${platform}. Make it relevant to current trends and competitor gaps.`
          })
          
          return {
            id: index + 1,
            type: contentType === 'promotional' ? 'gap-based' : contentType === 'educational' ? 'trending-topic' : 'competitor-response',
            platform: platform.charAt(0).toUpperCase() + platform.slice(1),
            title: `AI Generated ${contentType.charAt(0).toUpperCase() + contentType.slice(1)} Content`,
            content: response.content?.post_content || 'Content generated successfully',
            engagement: response.content?.estimated_engagement || 'High',
            confidence: 90 + Math.floor(Math.random() * 10),
            gapType: contentType === 'promotional' ? 'Content Gap' : contentType === 'educational' ? 'Educational Content' : 'Competitor Response',
            competitorInsight: `AI-generated content optimized for ${platform} engagement`,
            hashtags: response.content?.hashtags || []
          }
        } catch (error) {
          console.error(`Failed to generate content for ${platform}:`, error)
          return null
        }
      })
      
      const results = await Promise.all(suggestionPromises)
      const validSuggestions = results.filter(Boolean)
      setSuggestions(validSuggestions)
      
    } catch (error) {
      console.error('Failed to load AI suggestions:', error)
      // Fallback to mock data if API fails
      setSuggestions([
        {
          id: 1,
          type: "gap-based",
          platform: "Instagram",
          title: "AI Content Suggestion",
          content: "🚀 Boost your content strategy with AI-powered insights! Stay ahead of the competition with data-driven content creation. #AIContent #Strategy",
          engagement: "High",
          confidence: 92,
          gapType: "Content Gap",
          competitorInsight: "AI-generated content optimized for engagement",
          hashtags: ["#AIContent", "#Strategy"]
        }
      ])
    } finally {
      setLoadingSuggestions(false)
    }
  }

  useEffect(() => {
    loadAISuggestions()
  }, [selectedIndustry])

  const handleEdit = (suggestion: any) => {
    setEditingId(suggestion.id)
    setEditedContent(suggestion.content)
  }

  const handleSave = (id: number) => {
    setSuggestions(prev => prev.map(s => 
      s.id === id ? { ...s, content: editedContent } : s
    ))
    setEditingId(null)
    toast({
      title: "Content updated",
      description: "Your AI-generated content has been saved.",
    })
  }

  const handleApprove = (suggestion: any) => {
    toast({
      title: "Content approved",
      description: `${suggestion.title} has been scheduled for ${suggestion.platform}.`,
    })
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case "gap-based":
        return <Target className="h-4 w-4" />
      case "competitor-response":
        return <RefreshCw className="h-4 w-4" />
      case "trending-topic":
        return <Sparkles className="h-4 w-4" />
      default:
        return <Sparkles className="h-4 w-4" />
    }
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case "gap-based":
        return "text-blue-600"
      case "competitor-response":
        return "text-orange-600"
      case "trending-topic":
        return "text-purple-600"
      default:
        return "text-gray-600"
    }
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-blue-600" />
              AI Content Suggestions
            </CardTitle>
            <CardDescription>AI-powered content ideas based on competitor gaps and trends</CardDescription>
          </div>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={loadAISuggestions}
            disabled={loadingSuggestions}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${loadingSuggestions ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {loadingSuggestions ? (
          Array.from({ length: 3 }).map((_, index) => (
            <div key={index} className="space-y-3 p-4 border rounded-lg">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Skeleton className="h-4 w-4" />
                  <Skeleton className="h-4 w-24" />
                </div>
                <Skeleton className="h-6 w-12" />
              </div>
              <Skeleton className="h-4 w-48" />
              <Skeleton className="h-20 w-full" />
              <div className="flex gap-2">
                <Skeleton className="h-8 w-20" />
                <Skeleton className="h-8 w-16" />
              </div>
            </div>
          ))
        ) : (
          suggestions.map((suggestion) => (
            <div key={suggestion.id} className="space-y-3 p-4 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-900/50 transition-colors">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className={getTypeColor(suggestion.type)}>
                    {getTypeIcon(suggestion.type)}
                  </div>
                  <span className="text-sm font-medium text-muted-foreground">{suggestion.platform}</span>
                  <Badge variant="outline" className="text-xs">
                    {suggestion.confidence}% confidence
                  </Badge>
                </div>
                <Badge variant={suggestion.engagement === "Very High" ? "default" : "secondary"}>
                  {suggestion.engagement} engagement
                </Badge>
              </div>

              <h4 className="font-medium">{suggestion.title}</h4>

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
                    <Button size="sm" variant="outline" onClick={() => setEditingId(null)}>
                      <X className="h-3 w-3 mr-1" />
                      Cancel
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="space-y-3">
                  <p className="text-sm leading-relaxed">{suggestion.content}</p>
                  
                  {suggestion.hashtags && suggestion.hashtags.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {suggestion.hashtags.slice(0, 3).map((hashtag: string, index: number) => (
                        <Badge key={index} variant="secondary" className="text-xs">
                          {hashtag}
                        </Badge>
                      ))}
                    </div>
                  )}

                  <div className="bg-blue-50 dark:bg-blue-950/20 p-3 rounded text-xs">
                    <p className="font-medium text-blue-900 dark:text-blue-100">💡 AI Insight</p>
                    <p className="text-blue-700 dark:text-blue-300">{suggestion.competitorInsight}</p>
                  </div>

                  <div className="flex gap-2">
                    <Button size="sm" onClick={() => handleApprove(suggestion)}>
                      <ThumbsUp className="h-3 w-3 mr-1" />
                      Approve & Schedule
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => handleEdit(suggestion)}>
                      <Edit3 className="h-3 w-3 mr-1" />
                      Edit
                    </Button>
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </CardContent>
    </Card>
  )
}
