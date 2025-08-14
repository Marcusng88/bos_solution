"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Facebook, Instagram, Twitter, Linkedin, Heart, MessageCircle, Share, Clock } from "lucide-react"

interface PostPreviewProps {
  caption: string
  media: File[]
  platforms: string[]
  scheduledDate: string
  scheduledTime: string
  postType: string
}

const platformData = {
  facebook: { name: "Facebook", icon: Facebook, color: "bg-blue-600" },
  instagram: { name: "Instagram", icon: Instagram, color: "bg-pink-600" },
  twitter: { name: "Twitter/X", icon: Twitter, color: "bg-black" },
  linkedin: { name: "LinkedIn", icon: Linkedin, color: "bg-blue-700" },
}

export function PostPreview({ caption, media, platforms, scheduledDate, scheduledTime, postType }: PostPreviewProps) {
  const formatScheduleTime = () => {
    if (postType === "now") return "Publishing immediately"
    if (postType === "optimal") return "AI will choose optimal time"
    if (scheduledDate && scheduledTime) {
      const date = new Date(`${scheduledDate}T${scheduledTime}`)
      return `Scheduled for ${date.toLocaleDateString()} at ${date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`
    }
    return "Schedule not set"
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Post Preview</CardTitle>
        <CardDescription>See how your post will appear on different platforms</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Schedule Info */}
        <div className="flex items-center gap-2 p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
          <Clock className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm">{formatScheduleTime()}</span>
        </div>

        {/* Platform Badges */}
        <div className="flex flex-wrap gap-2">
          {platforms.map((platformId) => {
            const platform = platformData[platformId as keyof typeof platformData]
            if (!platform) return null
            const Icon = platform.icon
            return (
              <Badge key={platformId} variant="secondary" className="flex items-center gap-1">
                <div className={`w-3 h-3 rounded-sm ${platform.color}`}>
                  <Icon className="w-2 h-2 text-white m-0.5" />
                </div>
                {platform.name}
              </Badge>
            )
          })}
        </div>

        {/* Preview Content */}
        <div className="space-y-4">
          {platforms.includes("instagram") && (
            <Card className="p-4">
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <Avatar className="h-8 w-8">
                    <AvatarImage src="/placeholder.svg?height=32&width=32" />
                    <AvatarFallback>YB</AvatarFallback>
                  </Avatar>
                  <div>
                    <p className="font-semibold text-sm">your_business</p>
                    <p className="text-xs text-muted-foreground">Sponsored</p>
                  </div>
                </div>

                {media.length > 0 && media[0].type.startsWith("image/") && (
                  <div className="aspect-square bg-gray-100 dark:bg-gray-800 rounded-lg overflow-hidden">
                    <img
                      src={URL.createObjectURL(media[0]) || "/placeholder.svg"}
                      alt="Post media"
                      className="w-full h-full object-cover"
                    />
                  </div>
                )}

                <div className="flex items-center gap-4">
                  <Heart className="h-6 w-6" />
                  <MessageCircle className="h-6 w-6" />
                  <Share className="h-6 w-6" />
                </div>

                <div className="space-y-1">
                  <p className="font-semibold text-sm">1,234 likes</p>
                  <p className="text-sm">
                    <span className="font-semibold">your_business</span> {caption || "Your caption will appear here..."}
                  </p>
                </div>
              </div>
            </Card>
          )}

          {platforms.includes("facebook") && (
            <Card className="p-4">
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <Avatar className="h-10 w-10">
                    <AvatarImage src="/placeholder.svg?height=40&width=40" />
                    <AvatarFallback>YB</AvatarFallback>
                  </Avatar>
                  <div>
                    <p className="font-semibold">Your Business</p>
                    <p className="text-xs text-muted-foreground">2 hours ago • 🌍</p>
                  </div>
                </div>

                <p className="text-sm">{caption || "Your caption will appear here..."}</p>

                {media.length > 0 && media[0].type.startsWith("image/") && (
                  <div className="aspect-video bg-gray-100 dark:bg-gray-800 rounded-lg overflow-hidden">
                    <img
                      src={URL.createObjectURL(media[0]) || "/placeholder.svg"}
                      alt="Post media"
                      className="w-full h-full object-cover"
                    />
                  </div>
                )}

                <div className="flex items-center justify-between pt-2 border-t">
                  <div className="flex items-center gap-4">
                    <span className="text-sm text-muted-foreground">👍 ❤️ 42</span>
                  </div>
                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <span>8 comments</span>
                    <span>3 shares</span>
                  </div>
                </div>
              </div>
            </Card>
          )}

          {platforms.includes("linkedin") && (
            <Card className="p-4">
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <Avatar className="h-12 w-12">
                    <AvatarImage src="/placeholder.svg?height=48&width=48" />
                    <AvatarFallback>YB</AvatarFallback>
                  </Avatar>
                  <div>
                    <p className="font-semibold">Your Business</p>
                    <p className="text-xs text-muted-foreground">Company • 1st</p>
                    <p className="text-xs text-muted-foreground">2h • 🌍</p>
                  </div>
                </div>

                <p className="text-sm">{caption || "Your caption will appear here..."}</p>

                {media.length > 0 && media[0].type.startsWith("image/") && (
                  <div className="aspect-video bg-gray-100 dark:bg-gray-800 rounded-lg overflow-hidden">
                    <img
                      src={URL.createObjectURL(media[0]) || "/placeholder.svg"}
                      alt="Post media"
                      className="w-full h-full object-cover"
                    />
                  </div>
                )}

                <div className="flex items-center gap-6 pt-2 border-t text-sm text-muted-foreground">
                  <span>👍 15</span>
                  <span>💬 3 comments</span>
                  <span>🔄 2 reposts</span>
                </div>
              </div>
            </Card>
          )}
        </div>

        {!caption && platforms.length === 0 && (
          <div className="text-center py-8 text-muted-foreground">
            <p>Select platforms and add content to see preview</p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
