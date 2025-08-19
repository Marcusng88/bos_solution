"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Checkbox } from "@/components/ui/checkbox"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { useToast } from "@/hooks/use-toast"
import { MediaUpload } from "./media-upload"
import { PostPreview } from "./post-preview"
import { Facebook, Instagram, Calendar, Send, Save, Sparkles } from "lucide-react"

const platforms = [
  { id: "facebook", name: "Facebook", icon: Facebook, color: "bg-blue-600", connected: true },
  { id: "instagram", name: "Instagram", icon: Instagram, color: "bg-pink-600", connected: true },
]

export function CreatePostForm() {
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>(["facebook", "instagram"])
  const [postData, setPostData] = useState({
    caption: "",
    scheduledDate: "",
    scheduledTime: "",
    postType: "now",
  })
  const [uploadedMedia, setUploadedMedia] = useState<File[]>([])
  const { toast } = useToast()

  // Use platforms directly since YouTube is handled separately
  const dynamicPlatforms = platforms

  const togglePlatform = (platformId: string) => {
    setSelectedPlatforms((prev) =>
      prev.includes(platformId) ? prev.filter((id) => id !== platformId) : [...prev, platformId],
    )
  }

  const handleAIAssist = () => {
    const aiSuggestion =
      "🌟 Exciting news! We're thrilled to announce our latest product launch. This innovative solution will transform how you approach your daily challenges. What do you think? Share your thoughts below! #Innovation #ProductLaunch #Excited"
    setPostData((prev) => ({ ...prev, caption: aiSuggestion }))
    toast({
      title: "AI suggestion added",
      description: "Your caption has been enhanced with AI-generated content.",
    })
  }

  const handlePublish = async () => {
    if (!postData.caption.trim()) {
      toast({
        title: "Caption required",
        description: "Please add a caption for your post.",
        variant: "destructive",
      })
      return
    }

    if (selectedPlatforms.length === 0) {
      toast({
        title: "Platform required",
        description: "Please select at least one platform to publish to.",
        variant: "destructive",
      })
      return
    }

    try {
      const action = postData.postType === "now" ? "published" : "scheduled"
      toast({
        title: `Post ${action}!`,
        description: `Your content has been ${action} to ${selectedPlatforms.length} platform(s).`,
      })

      // Reset form
      setPostData({ caption: "", scheduledDate: "", scheduledTime: "", postType: "now" })
      setSelectedPlatforms(["facebook", "instagram"])
      setUploadedMedia([])
      
    } catch (error: any) {
      console.error('Publishing error:', error)
      toast({
        title: "Publishing Failed",
        description: error.message || "Failed to publish content. Please try again.",
        variant: "destructive",
      })
    }
  }

  const handleSaveDraft = () => {
    toast({
      title: "Draft saved",
      description: "Your post has been saved as a draft.",
    })
  }

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

            {/* Caption */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label htmlFor="caption" className="text-base font-medium">
                  Caption
                </Label>
                <Button variant="outline" size="sm" onClick={handleAIAssist}>
                  <Sparkles className="mr-2 h-3 w-3" />
                  AI Assist
                </Button>
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
              <Button onClick={handlePublish} className="flex-1">
                {postData.postType === "now" ? (
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
              <Button variant="outline" onClick={handleSaveDraft}>
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
