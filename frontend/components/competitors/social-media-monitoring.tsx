"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Heart, MessageCircle, Share, ExternalLink, Clock } from "lucide-react"

interface SocialMediaMonitoringProps {
  monitoringData?: any[]
}

export function SocialMediaMonitoring({ monitoringData = [] }: SocialMediaMonitoringProps) {
  const recentPosts = [
    {
      competitor: "Nike",
      platform: "Instagram",
      content: "Just Do It. New Air Max collection drops tomorrow. Get ready to elevate your game. #JustDoIt #AirMax",
      timestamp: "2 hours ago",
      engagement: { likes: 15420, comments: 892, shares: 234 },
      performance: "High",
      url: "#",
    },
    {
      competitor: "Adidas",
      platform: "Facebook",
      content: "Impossible is Nothing. Our sustainable future starts now with 100% recycled materials in our new line.",
      timestamp: "4 hours ago",
      engagement: { likes: 8930, comments: 445, shares: 567 },
      performance: "Medium",
      url: "#",
    },
    {
      competitor: "Nike",
      platform: "TikTok",
      content: "POV: You're training with the best. Watch our athletes push their limits every single day.",
      timestamp: "8 hours ago",
      engagement: { likes: 45600, comments: 2340, shares: 1200 },
      performance: "Very High",
      url: "#",
    },
  ]

  const platformMetrics = [
    { platform: "Instagram", posts: 156, avgEngagement: 4.2, topPerformer: "Nike" },
    { platform: "Facebook", posts: 198, avgEngagement: 3.1, topPerformer: "Adidas" },
    { platform: "TikTok", posts: 89, avgEngagement: 8.7, topPerformer: "Nike" },
    { platform: "YouTube", posts: 45, avgEngagement: 6.2, topPerformer: "Under Armour" },
  ]

  const getPerformanceBadge = (performance: string) => {
    switch (performance) {
      case "Very High":
        return <Badge className="bg-green-600">Very High</Badge>
      case "High":
        return <Badge className="bg-green-500">High</Badge>
      case "Medium":
        return <Badge variant="secondary">Medium</Badge>
      case "Low":
        return <Badge variant="outline">Low</Badge>
      default:
        return <Badge variant="outline">Unknown</Badge>
    }
  }

  return (
    <div className="space-y-6">
      {/* Platform Performance Overview */}
      <Card>
        <CardHeader>
          <CardTitle>Platform Performance Overview</CardTitle>
          <CardDescription>Competitor activity and engagement across social platforms</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {platformMetrics.map((platform, index) => (
              <div key={index} className="p-4 border rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium">{platform.platform}</h3>
                  <Badge variant="outline">{platform.posts} posts</Badge>
                </div>
                <div className="space-y-2">
                  <div>
                    <span className="text-sm text-muted-foreground">Avg. Engagement: </span>
                    <span className="font-medium">{platform.avgEngagement}%</span>
                  </div>
                  <div>
                    <span className="text-sm text-muted-foreground">Top Performer: </span>
                    <span className="font-medium">{platform.topPerformer}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Recent Competitor Posts */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Competitor Activity</CardTitle>
          <CardDescription>Latest posts and their performance metrics</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recentPosts.map((post, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <Avatar className="h-8 w-8">
                      <AvatarFallback>{post.competitor.slice(0, 2)}</AvatarFallback>
                    </Avatar>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{post.competitor}</span>
                        <Badge variant="outline">{post.platform}</Badge>
                      </div>
                      <div className="flex items-center gap-1 text-sm text-muted-foreground">
                        <Clock className="h-3 w-3" />
                        {post.timestamp}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {getPerformanceBadge(post.performance)}
                    <Button variant="ghost" size="sm">
                      <ExternalLink className="h-4 w-4" />
                    </Button>
                  </div>
                </div>

                <p className="text-sm mb-3 leading-relaxed">{post.content}</p>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-6 text-sm text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <Heart className="h-4 w-4" />
                      {post.engagement.likes.toLocaleString()}
                    </div>
                    <div className="flex items-center gap-1">
                      <MessageCircle className="h-4 w-4" />
                      {post.engagement.comments.toLocaleString()}
                    </div>
                    <div className="flex items-center gap-1">
                      <Share className="h-4 w-4" />
                      {post.engagement.shares.toLocaleString()}
                    </div>
                  </div>
                  <Button variant="outline" size="sm">
                    Analyze Post
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Content Themes Analysis */}
      <Card>
        <CardHeader>
          <CardTitle>Content Themes Analysis</CardTitle>
          <CardDescription>Most popular content themes among competitors</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[
              { theme: "Product Launches", frequency: 28, engagement: "High" },
              { theme: "Athlete Partnerships", frequency: 22, engagement: "Very High" },
              { theme: "Sustainability", frequency: 19, engagement: "Medium" },
              { theme: "User Generated Content", frequency: 16, engagement: "High" },
              { theme: "Behind the Scenes", frequency: 14, engagement: "Medium" },
              { theme: "Training Tips", frequency: 12, engagement: "Low" },
            ].map((theme, index) => (
              <div key={index} className="p-4 border rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium">{theme.theme}</h3>
                  {getPerformanceBadge(theme.engagement)}
                </div>
                <div className="text-sm text-muted-foreground">{theme.frequency} posts this month</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
