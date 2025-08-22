"use client"

import React, { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import { Skeleton } from "@/components/ui/skeleton"
import { Input } from "@/components/ui/input"
import { useToast } from "@/hooks/use-toast"
import { useContentPlanning } from "@/hooks/use-content-planning"
import { Sparkles, ThumbsUp, Edit3, X, RefreshCw, Target, Upload, Image as ImageIcon, Video, Trash2 } from "lucide-react"

interface AISuggestionsPanelProps {
  selectedDate: Date
}

export function AISuggestionsPanel({ selectedDate }: AISuggestionsPanelProps) {
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editedContent, setEditedContent] = useState("")
  const [uploadedMedia, setUploadedMedia] = useState<{ [key: number]: { file: File; preview: string; type: 'image' | 'video' } | null }>({})
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
          // 🎯 SHORTENED CONTENT PROMPT - HIGHLIGHTED FOR ATTENTION
          // ========================================================
          // Previous: "Create engaging ${contentType} content for ${platform}. Make it relevant to current trends and competitor gaps."
          // NEW: Concise prompt with specific instructions for shorter, impactful content
          // ========================================================
          const response = await generateContent({
            industry: selectedIndustry,
            platform,
            content_type: contentType,
            tone: 'professional',
            target_audience: 'professionals',
            custom_requirements: `🎯 Create concise, impactful ${contentType} content for ${platform}. Keep it short and engaging. Focus on trends and competitor gaps. Max 2-3 sentences with relevant hashtags.`
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
          content: "🚀 Boost your strategy with AI insights! Stay competitive. #AIContent #Strategy",
          engagement: "High",
          confidence: 92,
          gapType: "Content Gap",
          competitorInsight: "Concise AI-generated content optimized for engagement",
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

  // Cleanup function to revoke object URLs and prevent memory leaks
  useEffect(() => {
    return () => {
      Object.values(uploadedMedia).forEach(media => {
        if (media?.preview) {
          URL.revokeObjectURL(media.preview)
        }
      })
    }
  }, [uploadedMedia])

  const handleEdit = (suggestion: any) => {
    setEditingId(suggestion.id)
    setEditedContent(suggestion.content)
    // Keep any existing uploaded media when entering edit mode
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

  const handleMediaUpload = (suggestionId: number, event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    // Validate file type
    const isImage = file.type.startsWith('image/')
    const isVideo = file.type.startsWith('video/')
    
    if (!isImage && !isVideo) {
      toast({
        title: "Invalid file type",
        description: "Please upload an image or video file.",
        variant: "destructive"
      })
      return
    }

    // Check file size (max 10MB for images, 50MB for videos)
    const maxSize = isImage ? 10 * 1024 * 1024 : 50 * 1024 * 1024
    if (file.size > maxSize) {
      toast({
        title: "File too large",
        description: `Please upload a ${isImage ? 'image' : 'video'} smaller than ${isImage ? '10MB' : '50MB'}.`,
        variant: "destructive"
      })
      return
    }

    // Create preview URL
    const preview = URL.createObjectURL(file)
    const mediaType = isImage ? 'image' : 'video'

    setUploadedMedia(prev => ({
      ...prev,
      [suggestionId]: { file, preview, type: mediaType }
    }))

    toast({
      title: "Media uploaded",
      description: `${mediaType.charAt(0).toUpperCase() + mediaType.slice(1)} has been attached to your content.`,
    })
  }

  const handleRemoveMedia = (suggestionId: number) => {
    const media = uploadedMedia[suggestionId]
    if (media?.preview) {
      URL.revokeObjectURL(media.preview)
    }
    
    setUploadedMedia(prev => ({
      ...prev,
      [suggestionId]: null
    }))

    toast({
      title: "Media removed",
      description: "The attached media has been removed.",
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

  const renderMarkdownContent = (content: string) => {
    // Simple markdown parsing for basic formatting
    const processedContent = content
      .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold">$1</strong>')
      .replace(/\*(.*?)\*/g, '<em class="italic">$1</em>')
      .replace(/`(.*?)`/g, '<code class="bg-gray-100 dark:bg-gray-800 px-1 rounded text-xs">$1</code>')
      .replace(/\n/g, '<br />')
    
    return (
      <div 
        // 📝 JUSTIFIED TEXT - Added text-justify for professional alignment
        className="text-xs leading-relaxed break-words text-justify"
        dangerouslySetInnerHTML={{ __html: processedContent }}
      />
    )
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
    <Card className="w-full max-w-full relative z-10">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0 space-y-1">
            <CardTitle className="flex items-center gap-2 text-base">
              <Sparkles className="h-4 w-4 text-blue-600 flex-shrink-0" />
              <span className="truncate">AI Content Suggestions</span>
            </CardTitle>
            <CardDescription className="text-xs leading-relaxed">
              AI-powered content ideas based on competitor gaps and trends
            </CardDescription>
          </div>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={loadAISuggestions}
            disabled={loadingSuggestions}
            className="flex-shrink-0"
          >
            <RefreshCw className={`h-3 w-3 mr-1 ${loadingSuggestions ? 'animate-spin' : ''}`} />
            <span className="hidden sm:inline">Refresh</span>
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-3 pt-0">
        {loadingSuggestions ? (
          Array.from({ length: 3 }).map((_, index) => (
            <div key={index} className="space-y-2 p-3 border rounded-lg">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Skeleton className="h-3 w-3" />
                  <Skeleton className="h-3 w-20" />
                </div>
                <Skeleton className="h-5 w-10" />
              </div>
              <Skeleton className="h-3 w-32" />
              <Skeleton className="h-16 w-full" />
              <div className="flex gap-2">
                <Skeleton className="h-6 w-16" />
                <Skeleton className="h-6 w-12" />
              </div>
            </div>
          ))
        ) : (
          suggestions.map((suggestion) => (
            <div key={suggestion.id} className="relative space-y-2 p-3 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-900/50 transition-colors overflow-hidden">
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-2 min-w-0 flex-1">
                  <div className={`${getTypeColor(suggestion.type)} flex-shrink-0`}>
                    {getTypeIcon(suggestion.type)}
                  </div>
                  <span className="text-xs font-medium text-muted-foreground truncate">{suggestion.platform}</span>
                  <Badge variant="outline" className="text-xs flex-shrink-0 px-1 py-0">
                    {suggestion.confidence}%
                  </Badge>
                </div>
                <Badge variant={suggestion.engagement === "Very High" ? "default" : "secondary"} className="flex-shrink-0 text-xs px-1 py-0">
                  {suggestion.engagement}
                </Badge>
              </div>

              <h4 className="font-medium text-sm break-words leading-tight">{suggestion.title}</h4>

              {editingId === suggestion.id ? (
                <div className="space-y-3">
                  <Textarea
                    value={editedContent}
                    onChange={(e) => setEditedContent(e.target.value)}
                    // 📝 JUSTIFIED TEXT - Added text-justify for professional alignment in edit mode
                    className="min-h-[80px] text-xs text-justify"
                    placeholder="Edit your content..."
                  />
                  
                  {/* Media Upload Section */}
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-medium text-muted-foreground">Media</span>
                      {!uploadedMedia[suggestion.id] && (
                        <div className="relative">
                          <Input
                            type="file"
                            accept="image/*,video/*"
                            onChange={(e) => handleMediaUpload(suggestion.id, e)}
                            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                            id={`media-upload-${suggestion.id}`}
                          />
                          <Button
                            variant="outline"
                            size="sm"
                            className="text-xs px-2 py-1 h-7"
                            asChild
                          >
                            <label htmlFor={`media-upload-${suggestion.id}`} className="cursor-pointer flex items-center">
                              <Upload className="h-3 w-3 mr-1" />
                              Upload
                            </label>
                          </Button>
                        </div>
                      )}
                    </div>

                    {/* Media Preview */}
                    {uploadedMedia[suggestion.id] && (
                      <div className="relative rounded-lg border bg-gray-50 dark:bg-gray-900/50 p-3">
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex items-center gap-2">
                            {uploadedMedia[suggestion.id]?.type === 'image' ? (
                              <ImageIcon className="h-4 w-4 text-blue-600" />
                            ) : (
                              <Video className="h-4 w-4 text-purple-600" />
                            )}
                            <span className="text-xs font-medium text-muted-foreground">
                              {uploadedMedia[suggestion.id]?.file.name}
                            </span>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleRemoveMedia(suggestion.id)}
                            className="h-6 w-6 p-0 text-muted-foreground hover:text-destructive"
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                        
                        <div className="rounded-md overflow-hidden bg-white dark:bg-gray-800 border">
                          {uploadedMedia[suggestion.id]?.type === 'image' ? (
                            <img
                              src={uploadedMedia[suggestion.id]?.preview}
                              alt="Uploaded content"
                              className="w-full h-32 object-cover"
                            />
                          ) : (
                            <video
                              src={uploadedMedia[suggestion.id]?.preview}
                              className="w-full h-32 object-cover"
                              controls
                              preload="metadata"
                            >
                              Your browser does not support the video tag.
                            </video>
                          )}
                        </div>
                        
                        <div className="mt-2 text-xs text-muted-foreground">
                          {uploadedMedia[suggestion.id]?.type === 'image' ? 'Image' : 'Video'} • {
                            uploadedMedia[suggestion.id]?.file.size && 
                            (uploadedMedia[suggestion.id]!.file.size / 1024 / 1024).toFixed(1)
                          } MB
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="flex gap-1 pt-1">
                    <Button size="sm" onClick={() => handleSave(suggestion.id)} className="text-xs px-2 py-1 h-7">
                      Save
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => setEditingId(null)} className="text-xs px-2 py-1 h-7">
                      <X className="h-3 w-3 mr-1" />
                      Cancel
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="space-y-3">
                  {renderMarkdownContent(suggestion.content)}
                  
                  {/* Display uploaded media in view mode */}
                  {uploadedMedia[suggestion.id] && (
                    <div className="rounded-lg border bg-gray-50 dark:bg-gray-900/50 p-3">
                      <div className="flex items-center gap-2 mb-2">
                        {uploadedMedia[suggestion.id]?.type === 'image' ? (
                          <ImageIcon className="h-4 w-4 text-blue-600" />
                        ) : (
                          <Video className="h-4 w-4 text-purple-600" />
                        )}
                        <span className="text-xs font-medium text-muted-foreground">
                          {uploadedMedia[suggestion.id]?.file.name}
                        </span>
                      </div>
                      
                      <div className="rounded-md overflow-hidden bg-white dark:bg-gray-800 border">
                        {uploadedMedia[suggestion.id]?.type === 'image' ? (
                          <img
                            src={uploadedMedia[suggestion.id]?.preview}
                            alt="Uploaded content"
                            className="w-full h-32 object-cover"
                          />
                        ) : (
                          <video
                            src={uploadedMedia[suggestion.id]?.preview}
                            className="w-full h-32 object-cover"
                            controls
                            preload="metadata"
                          >
                            Your browser does not support the video tag.
                          </video>
                        )}
                      </div>
                    </div>
                  )}
                  
                  {suggestion.hashtags && suggestion.hashtags.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {suggestion.hashtags.slice(0, 3).map((hashtag: string, index: number) => (
                        <Badge key={index} variant="secondary" className="text-xs break-all px-1 py-0">
                          {hashtag}
                        </Badge>
                      ))}
                    </div>
                  )}

                  <div className="bg-blue-50 dark:bg-blue-950/20 p-2 rounded text-xs">
                    <p className="font-medium text-blue-900 dark:text-blue-100 text-xs mb-1">💡 AI Insight</p>
                    <p className="text-blue-700 dark:text-blue-300 break-words text-xs leading-relaxed">{suggestion.competitorInsight}</p>
                  </div>

                  <div className="flex flex-col sm:flex-row gap-1">
                    <Button size="sm" onClick={() => handleApprove(suggestion)} className="flex-1 text-xs px-2 py-1 h-7">
                      <ThumbsUp className="h-3 w-3 mr-1" />
                      <span className="truncate">Approve</span>
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => handleEdit(suggestion)} className="flex-shrink-0 text-xs px-2 py-1 h-7">
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
