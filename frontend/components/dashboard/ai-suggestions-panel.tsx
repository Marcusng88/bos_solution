"use client"

import React, { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import { Skeleton } from "@/components/ui/skeleton"
import { Input } from "@/components/ui/input"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { useToast } from "@/hooks/use-toast"
import { useContentPlanning } from "@/hooks/use-content-planning"
import { useUser } from "@clerk/nextjs"
import { Sparkles, ThumbsUp, Edit3, X, RefreshCw, Target, Upload, Image as ImageIcon, Video, Trash2, Plus } from "lucide-react"

interface AISuggestionsPanelProps {
  selectedDate: Date
}

export function AISuggestionsPanel({ selectedDate }: AISuggestionsPanelProps) {
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editedContent, setEditedContent] = useState("")
  const [uploadedMedia, setUploadedMedia] = useState<{ [key: string]: { file: File; preview: string; type: 'image' | 'video' } | null }>({})
  const [suggestions, setSuggestions] = useState<any[]>([])
  const [loadingSuggestions, setLoadingSuggestions] = useState(false)
  const [loadingCreate, setLoadingCreate] = useState(false)
  const [loadingSave, setLoadingSave] = useState<string | null>(null) // Track which suggestion is being saved
  const [showPromotionDialog, setShowPromotionDialog] = useState(false)
  const [promotionDescription, setPromotionDescription] = useState("")
  const { toast } = useToast()
  const { user } = useUser()
  
  const { 
    generateContent, 
    saveContentSuggestion, 
    getContentSuggestions, 
    updateContentSuggestion,
    selectedIndustry 
  } = useContentPlanning({ autoLoad: false })

  // Load content suggestions from database
  const loadContentSuggestions = async () => {
    if (!user?.id) return
    
    try {
      setLoadingSuggestions(true)
      const response = await getContentSuggestions(user.id, 4) // Changed from 3 to 4
      
      if (response.success && response.suggestions) {
        // Transform database data to match component structure
        const transformedSuggestions = response.suggestions.map((suggestion, index) => ({
          id: suggestion.id,
          type: suggestion.competitor_analysis?.content_type === 'promotional' ? 'gap-based' : 
                suggestion.competitor_analysis?.content_type === 'educational' ? 'trending-topic' : 'competitor-response',
          platform: suggestion.competitor_analysis?.platform?.charAt(0).toUpperCase() + suggestion.competitor_analysis?.platform?.slice(1) || 'LinkedIn',
          title: `AI Generated ${suggestion.competitor_analysis?.content_type?.charAt(0).toUpperCase() + suggestion.competitor_analysis?.content_type?.slice(1) || 'Content'}`,
          content: suggestion.suggested_content,
          engagement: suggestion.predicted_engagement?.estimated_engagement_rate === 'high' ? 'High' : 'Medium',
          confidence: suggestion.predicted_engagement?.confidence_score || 85,
          gapType: suggestion.competitor_analysis?.content_type === 'promotional' ? 'Content Gap' : 
                   suggestion.competitor_analysis?.content_type === 'educational' ? 'Educational Content' : 'Competitor Response',
          competitorInsight: `AI-generated content optimized for ${suggestion.competitor_analysis?.platform || 'social media'} engagement`,
          hashtags: suggestion.suggested_hashtags || [],
          created_at: suggestion.created_at,
          // Store original data for saving
          originalData: suggestion
        }))
        setSuggestions(transformedSuggestions)
      } else {
        setSuggestions([])
      }
    } catch (error) {
      console.error('Failed to load content suggestions:', error)
      setSuggestions([])
      toast({
        title: "Error",
        description: "Failed to load content suggestions from database.",
        variant: "destructive"
      })
    } finally {
      setLoadingSuggestions(false)
    }
  }

  // Handle create content button click - show dialog first
  const handleCreateContentClick = () => {
    setShowPromotionDialog(true)
  }

  // Create new content using AI agent after user provides promotion details
  const handleCreateContent = async () => {
    if (!user?.id) {
      toast({
        title: "Error",
        description: "User not authenticated. Please log in again.",
        variant: "destructive"
      })
      return
    }

    if (!promotionDescription.trim()) {
      toast({
        title: "Error",
        description: "Please describe what you're trying to promote.",
        variant: "destructive"
      })
      return
    }

    try {
      setLoadingCreate(true)
      setShowPromotionDialog(false)
      
      // First, get user's industry from preferences
      let userIndustry = selectedIndustry
      if (!userIndustry) {
        try {
          const response = await fetch(`/api/v1/user-preferences?user_id=${user.id}`)
          if (response.ok) {
            const preferences = await response.json()
            userIndustry = preferences.industry
          }
        } catch (error) {
          console.warn('Could not fetch user industry, using default:', error)
          userIndustry = 'Technology & Software' // Default fallback
        }
      }
      
      // Generate content for the four major platforms
      const platforms = ['twitter', 'instagram', 'facebook', 'linkedin']
      const contentTypes = ['promotional', 'educational', 'entertaining', 'promotional'] // Mix of content types
      
      const createdSuggestions = []
      
      for (let i = 0; i < 4; i++) {
        const platform = platforms[i]
        const contentType = contentTypes[i]
        
        try {
          // Generate content using AI agent with user's promotion description
          const response = await generateContent({
            clerk_id: user.id,
            platform,
            content_type: contentType,
            tone: 'professional',
            target_audience: 'professionals',
            industry: userIndustry,
            custom_requirements: `🎯 Create concise, impactful ${contentType} content for ${platform} to promote: ${promotionDescription}. Keep it short and engaging. Focus on trends and competitor gaps. Max 2-3 sentences with relevant hashtags.`
          })

          console.log('🔧 Content generation response:', response)

          if (response.success && response.content) {
            toast({
              title: "Content Generated! 🎉",
              description: `AI has created ${contentType} content for ${platform}`,
            })
          } else {
            console.error('❌ Content generation failed:', response)
            toast({
              title: "Content Generation Failed",
              description: response.error || "Failed to generate content. Please try again.",
              variant: "destructive"
            })
          }
          
          if (response.success && response.content) {
            // Save to database
            const saveResponse = await saveContentSuggestion({
              user_id: user.id,
              suggested_content: response.content.post_content || 'Content generated successfully',
              platform,
              industry: userIndustry,
              content_type: contentType,
              tone: 'professional',
              target_audience: 'professionals',
              hashtags: response.content.hashtags || [],
              custom_requirements: `Generate ${contentType} content for ${platform} in ${userIndustry} industry to promote: ${promotionDescription}`
            })
            
            if (saveResponse.success) {
              createdSuggestions.push({
                platform,
                contentType,
                content: response.content.post_content || 'Content generated successfully',
                hashtags: response.content.hashtags || []
              })
            }
          }
        } catch (error) {
          console.error(`Failed to generate content for ${platform}:`, error)
        }
      }
      
      // Reload suggestions from database
      await loadContentSuggestions()
      
      if (createdSuggestions.length > 0) {
        toast({
          title: "Success",
          description: `Generated ${createdSuggestions.length} new content suggestions for all platforms!`,
        })
      } else {
        toast({
          title: "Warning",
          description: "Failed to generate any content suggestions. Please try again.",
          variant: "destructive"
        })
      }
      
      // Reset promotion description
      setPromotionDescription("")
      
    } catch (error) {
      console.error('Failed to create content:', error)
      toast({
        title: "Error",
        description: "Failed to create content. Please try again.",
        variant: "destructive"
      })
    } finally {
      setLoadingCreate(false)
    }
  }

  useEffect(() => {
    loadContentSuggestions()
  }, [user?.id, selectedIndustry])

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

  const handleSave = async (id: string) => {
    if (!user?.id) {
      toast({
        title: "Error",
        description: "User not authenticated. Please log in again.",
        variant: "destructive"
      })
      return
    }

    try {
      setLoadingSave(id)
      // Save to database
      const response = await updateContentSuggestion(id, {
        suggested_content: editedContent,
        user_modifications: "User edited the AI-generated content"
      })

      if (response.success) {
        // Update local state
        setSuggestions(prev => prev.map(s => 
          s.id === id ? { ...s, content: editedContent } : s
        ))
        setEditingId(null)
        toast({
          title: "Content updated",
          description: "Your AI-generated content has been saved to the database.",
        })
      } else {
        throw new Error(response.error || "Failed to update content")
      }
    } catch (error) {
      console.error('Failed to update content:', error)
      toast({
        title: "Error",
        description: "Failed to save content changes. Please try again.",
        variant: "destructive"
      })
    } finally {
      setLoadingSave(null)
    }
  }

  const handleApprove = (suggestion: any) => {
    toast({
      title: "Content approved",
      description: `${suggestion.title} has been scheduled for ${suggestion.platform}.`,
    })
  }

  const handleMediaUpload = (suggestionId: string, event: React.ChangeEvent<HTMLInputElement>) => {
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

  const handleRemoveMedia = (suggestionId: string) => {
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
          <div className="flex gap-2 flex-shrink-0">
            <Button 
              onClick={handleCreateContentClick}
              disabled={loadingCreate || !user?.id}
              className="flex items-center gap-2"
            >
              <Plus className="h-3 w-3" />
              <span className="hidden sm:inline">Create Content</span>
            </Button>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={loadContentSuggestions}
              disabled={loadingSuggestions}
              className="flex-shrink-0"
            >
              <RefreshCw className={`h-3 w-3 mr-1 ${loadingSuggestions ? 'animate-spin' : ''}`} />
              <span className="hidden sm:inline">Refresh</span>
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-3 pt-0">
        {loadingSuggestions ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {Array.from({ length: 4 }).map((_, index) => (
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
            ))}
          </div>
        ) : suggestions.length === 0 ? (
          <div className="text-center py-8">
            <Sparkles className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
              No Content Suggestions Yet
            </h3>
            <p className="text-gray-500 dark:text-gray-400 mb-4">
              Click "Create Content" to generate AI-powered content suggestions based on competitor analysis.
            </p>
            <Button 
              onClick={handleCreateContentClick}
              disabled={loadingCreate || !user?.id}
              className="flex items-center gap-2 mx-auto"
            >
              <Plus className="h-4 w-4" />
              {loadingCreate ? 'Generating...' : 'Create Content'}
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {suggestions.map((suggestion) => (
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
                      <Button size="sm" onClick={() => handleSave(suggestion.id)} className="text-xs px-2 py-1 h-7" disabled={loadingSave === suggestion.id}>
                        {loadingSave === suggestion.id ? 'Saving...' : 'Save'}
                      </Button>
                      <Button size="sm" variant="outline" onClick={() => setEditingId(null)} className="text-xs px-2 py-1 h-7" disabled={loadingSave === suggestion.id}>
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
            ))}
          </div>
        )}
      </CardContent>

      <Dialog open={showPromotionDialog} onOpenChange={setShowPromotionDialog}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>What are you trying to promote?</DialogTitle>
            <DialogDescription>
              Describe your product, service, or message. This will help AI generate more relevant and effective content for Twitter, Instagram, Facebook, and LinkedIn.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="promotion-description">Promotion Description</Label>
              <Textarea
                id="promotion-description"
                value={promotionDescription}
                onChange={(e) => setPromotionDescription(e.target.value)}
                placeholder="e.g., Our new AI-powered marketing tool that helps businesses increase their social media engagement by 300%..."
                className="min-h-[100px]"
              />
            </div>
            <div className="text-sm text-muted-foreground">
              <p>AI will create optimized content for:</p>
              <ul className="list-disc list-inside mt-1 space-y-1">
                <li><strong>Twitter:</strong> Concise, trending content with relevant hashtags</li>
                <li><strong>Instagram:</strong> Visual-friendly content with engaging captions</li>
                <li><strong>Facebook:</strong> Community-focused content for broader audience</li>
                <li><strong>LinkedIn:</strong> Professional content for business audience</li>
              </ul>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowPromotionDialog(false)}>Cancel</Button>
            <Button onClick={handleCreateContent} disabled={!promotionDescription.trim() || loadingCreate}>
              {loadingCreate ? 'Generating...' : 'Generate Content'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Card>
  )
}
