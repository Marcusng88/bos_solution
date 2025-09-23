"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { CreatePostForm } from "./create-post-form"
import { ScheduledPosts } from "./scheduled-posts"
import { PostTemplates } from "./post-templates"
import { YouTubeUpload } from "./youtube-upload"
import { SocialMediaTab } from "./social-media-tab"
import { DraftTab } from "./draft-tab"
import { Plus, Calendar, FileText, Clock, Share2, Youtube } from "lucide-react"
import { useUser } from "@clerk/nextjs"
import { ComingSoonDialog } from "@/components/ui/coming-soon-dialog"
import GradientText from "@/components/effects/GradientText"
import ShinyText from "@/components/effects/ShinyText"
import "../../styles/competitor-animations.css"

export function PublishingInterface() {
  const [activeTab, setActiveTab] = useState("create")
  const [isVisible, setIsVisible] = useState(false)
  const { user } = useUser()

  useEffect(() => {
    setIsVisible(true)
  }, [])

  return (
    <div className="relative">
      {/* Subtle background overlay for depth */}
      <div className="absolute inset-0 bg-gradient-to-br from-transparent via-blue-950/3 to-purple-950/3 pointer-events-none"></div>
      
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-500/4 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-500/4 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }}></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-r from-blue-500/2 to-purple-500/2 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
      </div>

      <div className={`relative z-10 space-y-6 transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
      {/* Header */}
      <div className={`flex items-center justify-between transition-all duration-1000 delay-200 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'}`}>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            <GradientText>Publishing & Scheduling</GradientText>
          </h1>
          <div className="text-muted-foreground">
            <ShinyText text="Create and schedule content across all your platforms" />
          </div>
        </div>
        <div className={`flex gap-2 transition-all duration-1000 delay-400 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'}`}>
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
      <div className={`grid grid-cols-1 md:grid-cols-4 gap-4 transition-all duration-1000 delay-600 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'}`}>
        <Card className="glass-card transition-all duration-300 hover:scale-105 hover:shadow-xl border-white/20 animate-fade-in-up" style={{ animationDelay: '100ms' }}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-300">Posts Today</CardTitle>
            <div className="relative p-2.5 rounded-xl bg-gradient-to-r from-blue-500 to-indigo-600 shadow-lg overflow-hidden">
              <div className="absolute inset-0 bg-white/10 animate-pulse"></div>
              <Calendar className="relative h-4 w-4 text-white" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white bg-gradient-to-r from-white to-slate-200 bg-clip-text text-transparent">8</div>
            <p className="text-xs text-slate-400 font-medium leading-relaxed">+2 from yesterday</p>
          </CardContent>
        </Card>
        <Card className="glass-card transition-all duration-300 hover:scale-105 hover:shadow-xl border-white/20 animate-fade-in-up" style={{ animationDelay: '200ms' }}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-300">Scheduled</CardTitle>
            <div className="relative p-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 shadow-lg overflow-hidden">
              <div className="absolute inset-0 bg-white/10 animate-pulse"></div>
              <Clock className="relative h-4 w-4 text-white" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white bg-gradient-to-r from-white to-slate-200 bg-clip-text text-transparent">24</div>
            <p className="text-xs text-slate-400 font-medium leading-relaxed">Next 7 days</p>
          </CardContent>
        </Card>
        <Card className="glass-card transition-all duration-300 hover:scale-105 hover:shadow-xl border-white/20 animate-fade-in-up" style={{ animationDelay: '300ms' }}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-300">Drafts</CardTitle>
            <div className="relative p-2.5 rounded-xl bg-gradient-to-r from-purple-500 to-violet-600 shadow-lg overflow-hidden">
              <div className="absolute inset-0 bg-white/10 animate-pulse"></div>
              <FileText className="relative h-4 w-4 text-white" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white bg-gradient-to-r from-white to-slate-200 bg-clip-text text-transparent">6</div>
            <p className="text-xs text-slate-400 font-medium leading-relaxed">Ready to publish</p>
          </CardContent>
        </Card>
        <Card className="glass-card transition-all duration-300 hover:scale-105 hover:shadow-xl border-white/20 animate-fade-in-up" style={{ animationDelay: '400ms' }}>
           <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
             <CardTitle className="text-sm font-medium text-slate-300">Platforms</CardTitle>
             <div className="relative p-2.5 rounded-xl bg-gradient-to-r from-orange-500 to-red-600 shadow-lg overflow-hidden">
               <div className="absolute inset-0 bg-white/10 animate-pulse"></div>
               <Plus className="relative h-4 w-4 text-white" />
             </div>
           </CardHeader>
           <CardContent>
             <div className="text-2xl font-bold text-white bg-gradient-to-r from-white to-slate-200 bg-clip-text text-transparent">0</div>
             <p className="text-xs text-slate-400 font-medium leading-relaxed">Connected accounts</p>
           </CardContent>
         </Card>
      </div>

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className={`transition-all duration-1000 delay-800 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
        <TabsList className="glass-card grid w-full grid-cols-6 p-1 bg-slate-800/40 border border-white/20 backdrop-blur-md">
          <TabsTrigger value="create" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-600 data-[state=active]:to-purple-600 data-[state=active]:text-white data-[state=active]:shadow-lg font-semibold text-slate-300 transition-all duration-300">Create Post</TabsTrigger>
          <TabsTrigger value="drafts" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-600 data-[state=active]:to-purple-600 data-[state=active]:text-white data-[state=active]:shadow-lg font-semibold text-slate-300 transition-all duration-300">Drafts</TabsTrigger>
          <TabsTrigger value="youtube" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-600 data-[state=active]:to-purple-600 data-[state=active]:text-white data-[state=active]:shadow-lg font-semibold text-slate-300 transition-all duration-300">YouTube Upload</TabsTrigger>
          <TabsTrigger value="scheduled" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-600 data-[state=active]:to-purple-600 data-[state=active]:text-white data-[state=active]:shadow-lg font-semibold text-slate-300 transition-all duration-300">Scheduled Posts</TabsTrigger>
          <TabsTrigger value="templates" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-600 data-[state=active]:to-purple-600 data-[state=active]:text-white data-[state=active]:shadow-lg font-semibold text-slate-300 transition-all duration-300">Templates</TabsTrigger>
          <TabsTrigger value="social-media" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-600 data-[state=active]:to-purple-600 data-[state=active]:text-white data-[state=active]:shadow-lg font-semibold text-slate-300 transition-all duration-300">Social Media</TabsTrigger>
        </TabsList>

        <TabsContent value="create" className={`space-y-6 transition-all duration-700 delay-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'}`}>
          <CreatePostForm />
        </TabsContent>

        <TabsContent value="drafts" className="space-y-6">
          <DraftTab />
        </TabsContent>

        <TabsContent value="youtube" className={`space-y-6 transition-all duration-700 delay-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'}`}>
          <YouTubeUpload />
        </TabsContent>

        <TabsContent value="scheduled" className={`space-y-6 transition-all duration-700 delay-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'}`}>
          <ScheduledPosts />
        </TabsContent>

        <TabsContent value="templates" className={`space-y-6 transition-all duration-700 delay-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'}`}>
          <PostTemplates />
        </TabsContent>
        <TabsContent value="social-media" className={`space-y-6 transition-all duration-700 delay-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'}`}>
          <SocialMediaTab />
        </TabsContent>
      </Tabs>
    </div>
    </div>
  )
}
