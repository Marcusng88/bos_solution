"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { ComingSoonDialog } from "@/components/ui/coming-soon-dialog"
import { 
  Plus, 
  Calendar, 
  Clock, 
  Image, 
  Video, 
  Share2, 
  Instagram, 
  Facebook, 
  Twitter, 
  Linkedin,
  Youtube,
  Sparkles,
  FileText,
  BarChart3
} from "lucide-react"

export function SocialMediaTab() {
  const [activeTab, setActiveTab] = useState("create")
  const [selectedPlatform, setSelectedPlatform] = useState("")
  const [content, setContent] = useState("")
  const [scheduledDate, setScheduledDate] = useState("")

  const platforms = [
    { id: "instagram", name: "Instagram", icon: Instagram, color: "from-purple-400 to-pink-500" },
    { id: "facebook", name: "Facebook", icon: Facebook, color: "from-blue-500 to-blue-600" },
    { id: "twitter", name: "Twitter", icon: Twitter, color: "from-blue-400 to-blue-500" },
    { id: "linkedin", name: "LinkedIn", icon: Linkedin, color: "from-blue-600 to-blue-700" },
    { id: "youtube", name: "YouTube", icon: Youtube, color: "from-red-500 to-red-600" },
  ]

  const socialMediaFeatures = [
    "Multi-platform content scheduling",
    "AI-powered content optimization",
    "Advanced analytics and insights",
    "Content calendar management",
    "Team collaboration tools",
    "Automated posting workflows"
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold text-gray-900">Social Media Management</h2>
        <p className="text-gray-600">Create, schedule, and manage your social media content</p>
        <Badge variant="secondary" className="text-xs">
          <Sparkles className="w-3 h-3 mr-1" />
          Coming Soon
        </Badge>
      </div>

      {/* Platform Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {platforms.map((platform) => {
          const IconComponent = platform.icon
          return (
            <Card key={platform.id} className="hover:shadow-md transition-shadow cursor-pointer">
              <CardHeader className="pb-3">
                <div className="flex items-center gap-3">
                  <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${platform.color} flex items-center justify-center`}>
                    <IconComponent className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <CardTitle className="text-lg">{platform.name}</CardTitle>
                    <Badge variant="outline" className="text-xs">
                      Not Connected
                    </Badge>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <ComingSoonDialog
                  trigger={
                    <Button className="w-full" variant="outline">
                      <Plus className="w-4 h-4 mr-2" />
                      Connect Account
                    </Button>
                  }
                  title={`Connect ${platform.name} Account`}
                  description={`Connect your ${platform.name} account to start publishing content directly from our platform.`}
                  features={[
                    "Secure OAuth authentication",
                    "Multi-account support",
                    "Content scheduling",
                    "Analytics integration"
                  ]}
                  estimatedRelease="Q1 2025"
                />
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="create">Create Post</TabsTrigger>
          <TabsTrigger value="schedule">Schedule</TabsTrigger>
          <TabsTrigger value="templates">Templates</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="create" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Create New Post</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="platform">Platform</Label>
                  <Select value={selectedPlatform} onValueChange={setSelectedPlatform}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select platform" />
                    </SelectTrigger>
                    <SelectContent>
                      {platforms.map((platform) => (
                        <SelectItem key={platform.id} value={platform.id}>
                          <div className="flex items-center gap-2">
                            <platform.icon className="w-4 h-4" />
                            {platform.name}
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="scheduledDate">Schedule Date</Label>
                  <Input
                    id="scheduledDate"
                    type="datetime-local"
                    value={scheduledDate}
                    onChange={(e) => setScheduledDate(e.target.value)}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="content">Content</Label>
                <Textarea
                  id="content"
                  placeholder="Write your post content here..."
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  rows={4}
                />
              </div>

              <div className="space-y-2">
                <Label>Media</Label>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm">
                    <Image className="w-4 h-4 mr-2" />
                    Add Image
                  </Button>
                  <Button variant="outline" size="sm">
                    <Video className="w-4 h-4 mr-2" />
                    Add Video
                  </Button>
                </div>
              </div>

              <div className="flex gap-2 pt-4">
                <ComingSoonDialog
                  trigger={
                    <Button className="flex-1">
                      <Share2 className="w-4 h-4 mr-2" />
                      Publish Now
                    </Button>
                  }
                  title="Publish to Social Media"
                  description="Direct publishing to social media platforms is coming soon! You'll be able to post directly to Instagram, Facebook, Twitter, LinkedIn, and YouTube."
                  features={socialMediaFeatures}
                  estimatedRelease="Q1 2025"
                />
                
                <ComingSoonDialog
                  trigger={
                    <Button variant="outline" className="flex-1">
                      <Clock className="w-4 h-4 mr-2" />
                      Schedule Post
                    </Button>
                  }
                  title="Schedule Social Media Posts"
                  description="Advanced scheduling with optimal posting times, content calendar, and automated workflows will be available soon."
                  features={[
                    "Smart scheduling algorithms",
                    "Content calendar view",
                    "Bulk scheduling",
                    "Time zone management"
                  ]}
                  estimatedRelease="Q1 2025"
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="schedule" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Scheduled Posts</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-gray-500">
                <Calendar className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                <p className="text-lg font-medium">No scheduled posts yet</p>
                <p className="text-sm">Schedule your first post to see it here</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="templates" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Content Templates</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-gray-500">
                <FileText className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                <p className="text-lg font-medium">Templates coming soon</p>
                <p className="text-sm">Pre-designed content templates will be available here</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Social Media Analytics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-gray-500">
                <BarChart3 className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                <p className="text-lg font-medium">Analytics dashboard coming soon</p>
                <p className="text-sm">Track your social media performance with detailed insights</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Coming Soon Banner */}
      <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
        <CardContent className="pt-6">
          <div className="text-center space-y-3">
            <div className="flex justify-center">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
                <Sparkles className="w-8 h-8 text-white" />
              </div>
            </div>
            <h3 className="text-xl font-bold text-gray-900">Social Media Integration Coming Soon!</h3>
            <p className="text-gray-600 max-w-2xl mx-auto">
              We're building powerful social media management tools that will help you create, schedule, 
              and analyze content across all major platforms. Get ready for seamless social media workflow!
            </p>
            <ComingSoonDialog
              trigger={
                <Button variant="outline" className="mt-2">
                  Learn More
                </Button>
              }
              title="Social Media Management Suite"
              description="Our comprehensive social media management platform is designed to streamline your content creation and publishing workflow."
              features={socialMediaFeatures}
              estimatedRelease="Q1 2025"
            />
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
