"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useToast } from "@/hooks/use-toast"
import { Facebook, Instagram, Twitter, Linkedin, Clock, Edit, Trash2, Search, Filter } from "lucide-react"

const scheduledPosts = [
  {
    id: 1,
    title: "Summer Sale Announcement",
    caption: "🌟 Exciting news! Our summer sale is here with up to 50% off selected items...",
    platforms: ["facebook", "instagram"],
    scheduledDate: "2024-01-15",
    scheduledTime: "10:00",
    status: "scheduled",
    engagement: "High",
  },
  {
    id: 2,
    title: "Product Feature Highlight",
    caption: "Discover the amazing features of our latest product that will transform your workflow...",
    platforms: ["linkedin", "twitter"],
    scheduledDate: "2024-01-15",
    scheduledTime: "14:00",
    status: "scheduled",
    engagement: "Medium",
  },
  {
    id: 3,
    title: "Behind the Scenes Content",
    caption: "Take a peek behind the scenes at our creative process. Our team is working hard...",
    platforms: ["instagram"],
    scheduledDate: "2024-01-16",
    scheduledTime: "09:00",
    status: "draft",
    engagement: "High",
  },
  {
    id: 4,
    title: "Customer Success Story",
    caption: "We love hearing from our customers! Here's how Sarah transformed her business...",
    platforms: ["facebook", "linkedin"],
    scheduledDate: "2024-01-16",
    scheduledTime: "16:00",
    status: "scheduled",
    engagement: "High",
  },
]

const platformData = {
  facebook: { name: "Facebook", icon: Facebook, color: "bg-blue-600" },
  instagram: { name: "Instagram", icon: Instagram, color: "bg-pink-600" },
  twitter: { name: "Twitter/X", icon: Twitter, color: "bg-black" },
  linkedin: { name: "LinkedIn", icon: Linkedin, color: "bg-blue-700" },
}

export function ScheduledPosts() {
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")
  const { toast } = useToast()

  const filteredPosts = scheduledPosts.filter((post) => {
    const matchesSearch =
      post.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      post.caption.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === "all" || post.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const handleEdit = (postId: number) => {
    toast({
      title: "Edit post",
      description: "Opening post editor...",
    })
  }

  const handleDelete = (postId: number) => {
    toast({
      title: "Post deleted",
      description: "The scheduled post has been removed.",
    })
  }

  const formatDateTime = (date: string, time: string) => {
    const dateObj = new Date(`${date}T${time}`)
    return dateObj.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Scheduled Posts</CardTitle>
          <CardDescription>Manage your upcoming and draft posts</CardDescription>
        </CardHeader>
        <CardContent>
          {/* Filters */}
          <div className="flex gap-4 mb-6">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search posts..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-40">
                <Filter className="mr-2 h-4 w-4" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Posts</SelectItem>
                <SelectItem value="scheduled">Scheduled</SelectItem>
                <SelectItem value="draft">Drafts</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Posts List */}
          <div className="space-y-4">
            {filteredPosts.map((post) => (
              <Card key={post.id} className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1 space-y-3">
                    <div className="flex items-center gap-3">
                      <h3 className="font-semibold">{post.title}</h3>
                      <Badge variant={post.status === "scheduled" ? "default" : "secondary"}>{post.status}</Badge>
                      <Badge variant={post.engagement === "High" ? "default" : "secondary"} className="text-xs">
                        {post.engagement} engagement
                      </Badge>
                    </div>

                    <p className="text-sm text-muted-foreground line-clamp-2">{post.caption}</p>

                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-2">
                        <Clock className="h-4 w-4 text-muted-foreground" />
                        <span className="text-sm text-muted-foreground">
                          {formatDateTime(post.scheduledDate, post.scheduledTime)}
                        </span>
                      </div>

                      <div className="flex items-center gap-1">
                        {post.platforms.map((platformId) => {
                          const platform = platformData[platformId as keyof typeof platformData]
                          if (!platform) return null
                          const Icon = platform.icon
                          return (
                            <div key={platformId} className={`p-1 rounded ${platform.color}`}>
                              <Icon className="h-3 w-3 text-white" />
                            </div>
                          )
                        })}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" onClick={() => handleEdit(post.id)}>
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => handleDelete(post.id)}>
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>

          {filteredPosts.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              <p>No posts found matching your criteria</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
