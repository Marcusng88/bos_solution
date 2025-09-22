"use client"

import React, { useState } from "react"
import { useUser } from '@clerk/nextjs'
import { draftService, CreateDraftData } from '@/lib/draft-service'
import { useToast } from '@/hooks/use-toast'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Checkbox } from "@/components/ui/checkbox"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { MediaUpload } from "./media-upload"
import { PostPreview } from "./post-preview"
import { ComingSoonDialog } from "@/components/ui/coming-soon-dialog"
import { Facebook, Instagram, Calendar, Send, Save, Sparkles } from "lucide-react"

const platforms = [
  { id: "facebook", name: "Facebook", icon: Facebook, color: "bg-blue-600", connected: true },
  { id: "instagram", name: "Instagram", icon: Instagram, color: "bg-pink-600", connected: true },
]

export function CreatePostForm() {
  const { user } = useUser()
  const { toast } = useToast()
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>(["facebook", "instagram"])
  const [postData, setPostData] = useState({
    title: "",
    caption: "",
    hashtags: [] as string[],
    scheduledDate: "",
    scheduledTime: "",
    postType: "now",
  })
  const [hashtagsInput, setHashtagsInput] = useState("") // Raw input string
  const [uploadedMedia, setUploadedMedia] = useState<File[]>([])
  const [isPublishing, setIsPublishing] = useState(false)

  const handlePublish = async () => {
    if (!postData.caption.trim()) {
      alert("Please enter a caption for your post")
      return
    }

    setIsPublishing(true)
    try {
      // Use FormData for media file support
      const formData = new FormData()
      
      // Send caption and hashtags separately (don't combine them here)
      formData.append('content_text', postData.caption)
      
      // Send hashtags as separate field if backend supports it
      if (postData.hashtags.length > 0) {
        formData.append('hashtags', JSON.stringify(postData.hashtags))
      }
      
      formData.append('platform', 'facebook')
      
      // Add media files if any
      uploadedMedia.forEach((file) => {
        formData.append('media_files', file)
      })

      const response = await fetch('http://localhost:8000/api/v1/social-media/publish-direct', {
        method: 'POST',
        headers: {
          'X-User-ID': 'user_31KT7lnRSm5G57HC4gfDUb2F9Ci'
          // Don't set Content-Type header - let the browser set it automatically for FormData
        },
        body: formData
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const result = await response.json()
      
      if (result.success) {
        let message = `✅ Published successfully!`
        if (result.media_type === 'video') {
          message += `\n📹 Video uploaded to Facebook`
        } else if (result.media_type === 'photo') {
          message += `\n📷 Photo uploaded to Facebook`
        } else if (result.media_type === 'album') {
          message += `\n📸 Album with ${result.media_count || uploadedMedia.length} photos uploaded`
        } else if (result.media_type === 'text') {
          message += `\n📝 Text post published`
        }
        message += `\n🔗 Post ID: ${result.post_id}`
        
        alert(message)
        
        // Reset form
        setPostData({ title: "", caption: "", hashtags: [], scheduledDate: "", scheduledTime: "", postType: "now" })
        setHashtagsInput("")
        setUploadedMedia([])
      } else {
        // Handle different error types
        if (result.error_type === 'expired_token') {
          const instructions = result.instructions?.join('\n') || ''
          alert(`❌ ${result.message}\n\n${result.error}\n\nTo fix this:\n${instructions}`)
        } else {
          alert(result.message || 'Publish failed')
        }
      }

    } catch (error) {
      console.error('Publish error:', error)
      
      // Try to parse error from response
      try {
        const errorText = error instanceof Error ? error.message : String(error)
        if (errorText.includes('Session has expired') || errorText.includes('access token')) {
          alert('❌ Facebook Access Token Expired\n\nYour Facebook access token has expired.\n\nTo fix this:\n1. Go to Facebook Developer Console\n2. Generate a new Page Access Token\n3. Update your backend configuration\n4. Restart the server')
        } else {
          alert(`Failed to publish: ${errorText}`)
        }
      } catch {
        alert(`Failed to publish: ${error instanceof Error ? error.message : String(error)}`)
      }
    } finally {
      setIsPublishing(false)
    }
  }

  const handleSaveDraft = async () => {
    if (!user?.id) {
      toast({
        title: 'Error',
        description: 'Please sign in to save drafts',
        variant: 'destructive'
      })
      return
    }

    if (!postData.title.trim()) {
      toast({
        title: 'Error', 
        description: 'Please enter a title for your draft',
        variant: 'destructive'
      })
      return
    }

    if (!postData.caption.trim()) {
      toast({
        title: 'Error',
        description: 'Please enter content for your draft',
        variant: 'destructive'
      })
      return
    }

    try {
      // Convert uploaded media files to URLs for storage
      const mediaUrls = uploadedMedia.map(file => {
        return URL.createObjectURL(file)
      })

      // Ensure hashtags are processed from input
      const processedHashtags = hashtagsInput
        .split(',')
        .map(tag => tag.trim().replace(/^#+/, ''))
        .filter(tag => tag.length > 0)

      const draftData: CreateDraftData = {
        title: postData.title,
        content: postData.caption,
        platform: selectedPlatforms[0] || 'facebook', // Use first selected platform
        content_type: 'post',
        status: 'draft',
        hashtags: processedHashtags,
        media_urls: mediaUrls,
        scheduling_options: {
          postType: postData.postType,
          scheduledDate: postData.scheduledDate,
          scheduledTime: postData.scheduledTime
        },
        metadata: {
          platforms: selectedPlatforms
        }
      }

      await draftService.createDraft(draftData, user.id)
      
      toast({
        title: 'Success',
        description: 'Draft saved successfully!',
      })

      // Reset form after successful save
      setPostData({ title: "", caption: "", hashtags: [], scheduledDate: "", scheduledTime: "", postType: "now" })
      setHashtagsInput("")
      setUploadedMedia([])
      
    } catch (error) {
      console.error('Error saving draft:', error)
      toast({
        title: 'Error',
        description: 'Failed to save draft',
        variant: 'destructive'
      })
    }
  }
  // Use platforms directly since YouTube is handled separately
  const dynamicPlatforms = platforms

  const togglePlatform = (platformId: string) => {
    setSelectedPlatforms((prev) =>
      prev.includes(platformId) ? prev.filter((id) => id !== platformId) : [...prev, platformId],
    )
  }

  // Note: AI assistance functionality is coming soon - currently shows coming soon dialog

  // Note: Publishing functionality is coming soon - currently shows coming soon dialog

  // Note: Draft saving functionality is coming soon - currently shows coming soon dialog

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Form Section */}
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Create New Post</CardTitle>
            <CardDescription>Compose your content and select platforms to publish</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Platform Selection */}
            <div className="space-y-3">
              <Label className="text-base font-medium">Select Platforms</Label>
              <div className="grid grid-cols-2 gap-3">
                {dynamicPlatforms.map((platform) => {
                  const Icon = platform.icon
                  const isSelected = selectedPlatforms.includes(platform.id)
                  const isConnected = platform.connected
                  return (
                    <div
                      key={platform.id}
                      className={`flex items-center space-x-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                        !isConnected
                          ? "opacity-50 cursor-not-allowed"
                          : isSelected
                            ? "border-blue-500 bg-blue-50 dark:bg-blue-950/20"
                            : "border-gray-200 hover:border-gray-300 dark:border-gray-700"
                      }`}
                      onClick={() => isConnected && togglePlatform(platform.id)}
                    >
                      <Checkbox checked={isSelected && isConnected} disabled={!isConnected} />
                      <div className={`p-1.5 rounded ${platform.color}`}>
                        <Icon className="h-4 w-4 text-white" />
                      </div>
                      <div className="flex-1">
                        <span className="text-sm font-medium">{platform.name}</span>
                        {!isConnected && (
                          <Badge variant="outline" className="ml-2 text-xs">
                            Not connected
                          </Badge>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>

            {/* Title */}
            <div className="space-y-3">
              <Label htmlFor="title" className="text-base font-medium">
                Draft Title
              </Label>
              <Input
                id="title"
                placeholder="Enter a title for your post/draft"
                value={postData.title}
                onChange={(e) => setPostData(prev => ({ ...prev, title: e.target.value }))}
              />
            </div>

            {/* Caption */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label htmlFor="caption" className="text-base font-medium">
                  Caption
                </Label>
                <ComingSoonDialog
                  trigger={
                    <Button variant="outline" size="sm">
                      <Sparkles className="mr-2 h-3 w-3" />
                      AI Assist
                    </Button>
                  }
                  title="AI Content Assistant"
                  description="AI-powered content creation and optimization tools are coming soon!"
                  features={[
                    "Smart caption generation",
                    "Content optimization suggestions",
                    "Hashtag recommendations",
                    "Engagement predictions",
                    "Brand voice consistency"
                  ]}
                  estimatedRelease="Q1 2025"
                />
              </div>
              <Textarea
                id="caption"
                placeholder="What's on your mind? Share your story..."
                value={postData.caption}
                onChange={(e) => setPostData((prev) => ({ ...prev, caption: e.target.value }))}
                className="min-h-[120px] resize-none"
              />
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>{postData.caption.length} characters</span>
                <span>Recommended: 125-150 characters for optimal engagement</span>
              </div>
            </div>

            {/* Media Upload */}
            <div className="space-y-3">
              <Label className="text-base font-medium">Media</Label>
              <MediaUpload onMediaUpload={setUploadedMedia} uploadedMedia={uploadedMedia} />
            </div>

            {/* Hashtags */}
            <div className="space-y-3">
              <Label className="text-base font-medium">Hashtags (comma separated)</Label>
              <Input
                placeholder="#example, #content, #marketing"
                value={hashtagsInput}
                onChange={(e) => setHashtagsInput(e.target.value)}
                onBlur={() => {
                  const hashtags = hashtagsInput
                    .split(',')
                    .map(tag => tag.trim().replace(/^#+/, '')) // Remove # prefix if present
                    .filter(tag => tag.length > 0)
                  setPostData((prev) => ({ ...prev, hashtags }))
                }}
              />
            </div>

            {/* Scheduling */}
            <div className="space-y-3">
              <Label className="text-base font-medium">Publishing Options</Label>
              <Select
                value={postData.postType}
                onValueChange={(value) => setPostData((prev) => ({ ...prev, postType: value }))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Choose when to publish" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="now">Publish Now</SelectItem>
                  <SelectItem value="schedule">Schedule for Later</SelectItem>
                  <SelectItem value="optimal">Publish at Optimal Time</SelectItem>
                </SelectContent>
              </Select>

              {postData.postType === "schedule" && (
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <Label htmlFor="date">Date</Label>
                    <Input
                      id="date"
                      type="date"
                      value={postData.scheduledDate}
                      onChange={(e) => setPostData((prev) => ({ ...prev, scheduledDate: e.target.value }))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="time">Time</Label>
                    <Input
                      id="time"
                      type="time"
                      value={postData.scheduledTime}
                      onChange={(e) => setPostData((prev) => ({ ...prev, scheduledTime: e.target.value }))}
                    />
                  </div>
                </div>
              )}

              {postData.postType === "optimal" && (
                <div className="p-3 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
                  <p className="text-sm text-blue-800 dark:text-blue-200">
                    AI will analyze your audience activity and schedule this post for maximum engagement.
                  </p>
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3 pt-4">
              <Button 
                className="flex-1"
                onClick={handlePublish}
                disabled={isPublishing}
              >
                {isPublishing ? (
                  <>
                    <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-background border-t-foreground" />
                    Publishing...
                  </>
                ) : postData.postType === "now" ? (
                  <>
                    <Send className="mr-2 h-4 w-4" />
                    Publish Now
                  </>
                ) : (
                  <>
                    <Calendar className="mr-2 h-4 w-4" />
                    Schedule Post
                  </>
                )}
              </Button>
              <Button 
                variant="outline"
                className="flex-1"
                onClick={handleSaveDraft}
              >
                <Save className="mr-2 h-4 w-4" />
                Save Draft
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Preview Section */}
      <div>
        <PostPreview
          caption={postData.caption}
          hashtags={postData.hashtags}
          media={uploadedMedia}
          platforms={selectedPlatforms}
          scheduledDate={postData.scheduledDate}
          scheduledTime={postData.scheduledTime}
          postType={postData.postType}
        />
      </div>
    </div>
  )
}
