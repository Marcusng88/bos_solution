"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Youtube, Upload, Video, Users, Eye, Settings } from "lucide-react"
import { AuthGuard } from "@/components/auth/auth-guard"
import { YouTubeConnection } from "@/components/onboarding/youtube-connection"
import { VideoUpload } from "@/components/onboarding/video-upload"
import { useYouTubeStore } from "@/hooks/use-youtube"

export default function YouTubePage() {
  const [showUpload, setShowUpload] = useState(false)
  const { isConnected, channel } = useYouTubeStore()

  return (
    <AuthGuard>
      <div className="container mx-auto p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-3">
              <Youtube className="h-8 w-8 text-red-600" />
              YouTube Management
            </h1>
            <p className="text-muted-foreground mt-1">
              Connect your YouTube account and manage your video content
            </p>
          </div>
          
          {isConnected && (
            <Dialog open={showUpload} onOpenChange={setShowUpload}>
              <DialogTrigger asChild>
                <Button>
                  <Upload className="mr-2 h-4 w-4" />
                  Upload Video
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-2xl">
                <DialogHeader>
                  <DialogTitle>Upload Video to YouTube</DialogTitle>
                </DialogHeader>
                <VideoUpload onClose={() => setShowUpload(false)} />
              </DialogContent>
            </Dialog>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Connection Status */}
          <div className="lg:col-span-2">
            <YouTubeConnection />
          </div>

          {/* Quick Stats */}
          {isConnected && channel && (
            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Channel Stats</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Users className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm">Subscribers</span>
                    </div>
                    <Badge variant="secondary">
                      {parseInt(channel.subscriber_count).toLocaleString()}
                    </Badge>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Video className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm">Videos</span>
                    </div>
                    <Badge variant="secondary">
                      {channel.video_count}
                    </Badge>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Eye className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm">Total Views</span>
                    </div>
                    <Badge variant="secondary">
                      {parseInt(channel.view_count).toLocaleString()}
                    </Badge>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Quick Actions</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <Button 
                    variant="outline" 
                    className="w-full justify-start"
                    onClick={() => setShowUpload(true)}
                  >
                    <Upload className="mr-2 h-4 w-4" />
                    Upload Video
                  </Button>
                  
                  <Button variant="outline" className="w-full justify-start" disabled>
                    <Settings className="mr-2 h-4 w-4" />
                    Channel Settings
                  </Button>
                  
                  <Button variant="outline" className="w-full justify-start" disabled>
                    <Video className="mr-2 h-4 w-4" />
                    Video Analytics
                  </Button>
                </CardContent>
              </Card>
            </div>
          )}
        </div>

        {/* Features Overview */}
        {!isConnected && (
          <Card>
            <CardHeader>
              <CardTitle>Why Connect YouTube?</CardTitle>
              <CardDescription>
                Unlock powerful features by connecting your YouTube account
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div className="p-4 border rounded-lg">
                  <Upload className="h-8 w-8 text-blue-600 mb-3" />
                  <h3 className="font-semibold mb-2">Direct Upload</h3>
                  <p className="text-sm text-muted-foreground">
                    Upload videos directly to YouTube without leaving our platform
                  </p>
                </div>
                
                <div className="p-4 border rounded-lg">
                  <Video className="h-8 w-8 text-green-600 mb-3" />
                  <h3 className="font-semibold mb-2">Content Management</h3>
                  <p className="text-sm text-muted-foreground">
                    Manage video metadata, thumbnails, and descriptions in one place
                  </p>
                </div>
                
                <div className="p-4 border rounded-lg">
                  <Eye className="h-8 w-8 text-purple-600 mb-3" />
                  <h3 className="font-semibold mb-2">Analytics</h3>
                  <p className="text-sm text-muted-foreground">
                    View detailed analytics and performance metrics for your videos
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </AuthGuard>
  )
}
