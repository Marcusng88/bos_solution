"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar"
import { Youtube, Users, Video, Eye, CheckCircle, AlertCircle, Loader2 } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { useYouTubeStore } from "@/hooks/use-youtube"

interface YouTubeConnectionProps {
  onConnectionChange?: (connected: boolean) => void
}

export function YouTubeConnection({ onConnectionChange }: YouTubeConnectionProps) {
  const [isConnecting, setIsConnecting] = useState(false)
  const { toast } = useToast()
  const { 
    isConnected, 
    channel, 
    connect, 
    disconnect,
    getUserVideos 
  } = useYouTubeStore()
  
  const [videos, setVideos] = useState<any[]>([])
  const [loadingVideos, setLoadingVideos] = useState(false)

  useEffect(() => {
    onConnectionChange?.(isConnected)
  }, [isConnected, onConnectionChange])

  useEffect(() => {
    if (isConnected && channel) {
      loadUserVideos()
    }
  }, [isConnected, channel])

  const handleConnect = async () => {
    setIsConnecting(true)
    try {
      await connect()
      toast({
        title: "Redirecting to YouTube",
        description: "You'll be redirected to authorize access to your YouTube account.",
      })
    } catch (error) {
      toast({
        title: "Connection Failed",
        description: "Failed to initiate YouTube connection. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsConnecting(false)
    }
  }

  const handleDisconnect = () => {
    disconnect()
    setVideos([])
    toast({
      title: "Disconnected",
      description: "Your YouTube account has been disconnected.",
    })
  }

  const loadUserVideos = async () => {
    if (!isConnected) return
    
    setLoadingVideos(true)
    try {
      const response = await getUserVideos(5)
      setVideos(response.videos || [])
    } catch (error) {
      console.error("Failed to load videos:", error)
      toast({
        title: "Error",
        description: "Failed to load your videos.",
        variant: "destructive",
      })
    } finally {
      setLoadingVideos(false)
    }
  }

  if (!isConnected) {
    return (
      <Card>
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-red-100 dark:bg-red-900/20 rounded-lg">
              <Youtube className="h-6 w-6 text-red-600" />
            </div>
            <div>
              <CardTitle>Connect YouTube</CardTitle>
              <CardDescription>
                Connect your YouTube channel to upload and manage videos through our platform
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-2">
                What you can do:
              </h4>
              <ul className="text-sm text-blue-800 dark:text-blue-200 space-y-1">
                <li>• Upload videos directly from our platform</li>
                <li>• Manage your video metadata and descriptions</li>
                <li>• View your channel analytics</li>
                <li>• Automate content publishing</li>
              </ul>
            </div>
            
            <Button 
              onClick={handleConnect} 
              disabled={isConnecting}
              className="w-full"
            >
              {isConnecting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Connecting...
                </>
              ) : (
                <>
                  <Youtube className="mr-2 h-4 w-4" />
                  Connect YouTube Account
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 dark:bg-green-900/20 rounded-lg">
              <CheckCircle className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <CardTitle className="flex items-center gap-2">
                YouTube Connected
                <Badge variant="secondary" className="bg-green-100 text-green-800">
                  Active
                </Badge>
              </CardTitle>
              <CardDescription>
                Your YouTube channel is successfully connected
              </CardDescription>
            </div>
          </div>
          <Button variant="outline" size="sm" onClick={handleDisconnect}>
            Disconnect
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {channel && (
          <div className="space-y-4">
            <div className="flex items-start gap-4 p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
              <Avatar className="h-16 w-16">
                <AvatarImage src={channel.thumbnail} alt={channel.title} />
                <AvatarFallback>
                  <Youtube className="h-8 w-8" />
                </AvatarFallback>
              </Avatar>
              
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold truncate">{channel.title}</h3>
                <p className="text-sm text-muted-foreground line-clamp-2 mt-1">
                  {channel.description || "No description available"}
                </p>
                
                <div className="flex items-center gap-4 mt-3 text-sm text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <Users className="h-4 w-4" />
                    <span>{parseInt(channel.subscriber_count).toLocaleString()} subscribers</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Video className="h-4 w-4" />
                    <span>{channel.video_count} videos</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Eye className="h-4 w-4" />
                    <span>{parseInt(channel.view_count).toLocaleString()} views</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Recent Videos */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-medium">Recent Videos</h4>
                {loadingVideos && (
                  <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                )}
              </div>
              
              {videos.length > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {videos.slice(0, 4).map((video) => (
                    <div key={video.id} className="flex gap-3 p-3 border rounded-lg">
                      <img
                        src={video.thumbnail}
                        alt={video.title}
                        className="w-16 h-12 rounded object-cover flex-shrink-0"
                      />
                      <div className="min-w-0 flex-1">
                        <h5 className="font-medium text-sm line-clamp-2">{video.title}</h5>
                        <p className="text-xs text-muted-foreground mt-1">
                          {new Date(video.published_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : !loadingVideos ? (
                <div className="text-center py-4 text-muted-foreground">
                  <Video className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">No videos found</p>
                </div>
              ) : null}
            </div>

            <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <p className="text-sm text-green-800 dark:text-green-200">
                ✓ You can now upload videos and manage your YouTube content through our platform
              </p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
