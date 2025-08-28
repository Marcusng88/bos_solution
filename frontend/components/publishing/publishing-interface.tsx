"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { CreatePostForm } from "./create-post-form"
import { ScheduledPosts } from "./scheduled-posts"
import { PostTemplates } from "./post-templates"
import { YouTubeUpload } from "./youtube-upload"
import { SocialMediaTab } from "./social-media-tab"
import { Plus, Calendar, FileText, Clock, Share2, Youtube } from "lucide-react"
import { useUser } from "@clerk/nextjs"
import { ComingSoonDialog } from "@/components/ui/coming-soon-dialog"

export function PublishingInterface() {
  const [activeTab, setActiveTab] = useState("create")
  const { user } = useUser()

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Publishing & Scheduling</h1>
          <p className="text-muted-foreground">Create and schedule content across all your platforms</p>
        </div>
        <div className="flex gap-2">
          <ComingSoonDialog
            trigger={
              <Button variant="outline">
                <Youtube className="mr-2 h-4 w-4" />
                Upload to YouTube
              </Button>
            }
            title="YouTube Integration"
            description="Direct YouTube video uploads and management are coming soon! You'll be able to upload, schedule, and manage your YouTube content directly from our platform."
            features={[
              "Video upload and optimization",
              "Thumbnail generation",
              "SEO optimization",
              "Scheduling and publishing",
              "Analytics and insights"
            ]}
            estimatedRelease="Q1 2025"
          />
          <ComingSoonDialog
            trigger={
              <Button>
                <Share2 className="mr-2 h-4 w-4" />
                Create Social Media Post
              </Button>
            }
            title="Social Media Publishing"
            description="Direct social media publishing is coming soon! You'll be able to create and schedule posts across Instagram, Facebook, Twitter, LinkedIn, and YouTube."
            features={[
              "Multi-platform content creation",
              "Smart scheduling algorithms",
              "Content templates and optimization",
              "Analytics and performance tracking",
              "Team collaboration tools"
            ]}
            estimatedRelease="Q1 2025"
          />
        </div>
      </div>

                   

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Posts Today</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">8</div>
            <p className="text-xs text-muted-foreground">+2 from yesterday</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Scheduled</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">24</div>
            <p className="text-xs text-muted-foreground">Next 7 days</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Drafts</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">6</div>
            <p className="text-xs text-muted-foreground">Ready to publish</p>
          </CardContent>
        </Card>
                 <Card>
           <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
             <CardTitle className="text-sm font-medium">Platforms</CardTitle>
             <Plus className="h-4 w-4 text-muted-foreground" />
           </CardHeader>
           <CardContent>
             <div className="text-2xl font-bold">0</div>
             <p className="text-xs text-muted-foreground">Connected accounts</p>
           </CardContent>
         </Card>
      </div>

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="create">Create Post</TabsTrigger>
          <TabsTrigger value="youtube">YouTube Upload</TabsTrigger>
          <TabsTrigger value="scheduled">Scheduled Posts</TabsTrigger>
          <TabsTrigger value="templates">Templates</TabsTrigger>
          <TabsTrigger value="social-media">Social Media</TabsTrigger>
        </TabsList>

        <TabsContent value="create" className="space-y-6">
          <CreatePostForm />
        </TabsContent>

        <TabsContent value="youtube" className="space-y-6">
          <YouTubeUpload />
        </TabsContent>

        <TabsContent value="scheduled" className="space-y-6">
          <ScheduledPosts />
        </TabsContent>

        <TabsContent value="templates" className="space-y-6">
          <PostTemplates />
        </TabsContent>
        <TabsContent value="social-media" className="space-y-6">
          <SocialMediaTab />
        </TabsContent>
      </Tabs>
    </div>
  )
}
