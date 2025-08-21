"use client"

import { useState, useRef, useEffect } from "react"
import { useUser } from "@clerk/nextjs"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { useToast } from "@/hooks/use-toast"
import { useYouTubeStore } from "@/hooks/use-youtube"
import { 
  Youtube, 
  Upload, 
  Video, 
  Play, 
  X, 
  CheckCircle, 
  AlertCircle, 
  Clock,
  Eye,
  EyeOff,
  Globe,
  Lock,
  Trash2,
  ExternalLink
} from "lucide-react"

interface UploadedVideo {
  id: string
  title: string
  description: string
  thumbnail: string
  video_url: string
  upload_status: string
  privacy_status: string
  upload_date: string
  file_name: string
}

export function YouTubeUpload() {
  const { user } = useUser()
  const { isConnected, connectionStatus, uploadVideoFile, connect, getUserVideos } = useYouTubeStore()
  const [videoFile, setVideoFile] = useState<File | null>(null)
  const [videoPreview, setVideoPreview] = useState<string | null>(null)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadedVideos, setUploadedVideos] = useState<UploadedVideo[]>([])
  const [videoData, setVideoData] = useState({
    title: "",
    description: "",
    tags: "",
    privacy_status: "private"
  })
  const fileInputRef = useRef<HTMLInputElement>(null)
  const { toast } = useToast()

  // Load real uploaded videos from YouTube API
  useEffect(() => {
    const loadUserVideos = async () => {
      if (isConnected) {
        try {
          const response = await getUserVideos(10) // Get latest 10 videos
          if (response && response.videos) {
            const formattedVideos: UploadedVideo[] = response.videos.map((video: any) => ({
              id: video.id,
              title: video.title,
              description: video.description || "",
              thumbnail: video.thumbnail,
              video_url: `https://www.youtube.com/watch?v=${video.id}`,
              upload_status: "processed", // Assume processed if it's in the list
              privacy_status: "public", // Default for fetched videos
              upload_date: video.published_at,
              file_name: `${video.title}.mp4`
            }))
            setUploadedVideos(formattedVideos)
          }
        } catch (error) {
          console.error('Failed to load user videos:', error)
          // Don't show error toast for this, just log it
        }
      }
    }

    loadUserVideos()
  }, [isConnected, getUserVideos])

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      // Validate file type
      if (!file.type.startsWith("video/")) {
        toast({
          title: "Invalid file type",
          description: "Please select a valid video file.",
          variant: "destructive",
        })
        return
      }

      // Validate file size (500MB limit)
      const maxSize = 500 * 1024 * 1024 // 500MB
      if (file.size > maxSize) {
        toast({
          title: "File too large",
          description: "Please select a video file smaller than 500MB.",
          variant: "destructive",
        })
        return
      }

      setVideoFile(file)
      
      // Set default title from filename
      const fileName = file.name.replace(/\.[^/.]+$/, "")
      setVideoData(prev => ({ ...prev, title: fileName }))
      
      // Create video preview
      const url = URL.createObjectURL(file)
      setVideoPreview(url)
    }
  }

  const handleUpload = async () => {
    if (!videoFile) {
      toast({
        title: "No video selected",
        description: "Please select a video file to upload.",
        variant: "destructive",
      })
      return
    }

    if (!videoData.title.trim()) {
      toast({
        title: "Title required",
        description: "Please enter a title for your video.",
        variant: "destructive",
      })
      return
    }

    if (!isConnected) {
      toast({
        title: "YouTube not connected",
        description: "Please connect your YouTube account first.",
        variant: "destructive",
      })
      return
    }

    if (!user?.id) {
      toast({
        title: "User not authenticated",
        description: "Please log in to upload videos.",
        variant: "destructive",
      })
      return
    }

    setIsUploading(true)
    setUploadProgress(0)

    try {
      // Parse tags
      const tagsArray = videoData.tags
        .split(",")
        .map(tag => tag.trim())
        .filter(tag => tag.length > 0)

      const uploadData = {
        videoFile: videoFile,
        title: videoData.title,
        description: videoData.description,
        tags: tagsArray,
        privacy_status: videoData.privacy_status
      }

      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return 90
          }
          return prev + 10
        })
      }, 500)

      const result = await uploadVideoFile(uploadData, user.id)
      
      clearInterval(progressInterval)
      setUploadProgress(100)

      // Add to uploaded videos list
      const newVideo: UploadedVideo = {
        id: result.video_id || `temp_${Date.now()}`,
        title: videoData.title,
        description: videoData.description,
        thumbnail: `https://img.youtube.com/vi/${result.video_id}/maxresdefault.jpg`,
        video_url: result.video_url || "#",
        upload_status: result.upload_status || "processing",
        privacy_status: videoData.privacy_status,
        upload_date: new Date().toISOString(),
        file_name: videoFile.name
      }

      setUploadedVideos(prev => [newVideo, ...prev])

      toast({
        title: "Upload successful!",
        description: `"${videoData.title}" has been uploaded to YouTube.`,
      })

      // Refresh the videos list to show the new upload
      try {
        const response = await getUserVideos(10)
        if (response && response.videos) {
          const formattedVideos: UploadedVideo[] = response.videos.map((video: any) => ({
            id: video.id,
            title: video.title,
            description: video.description || "",
            thumbnail: video.thumbnail,
            video_url: `https://www.youtube.com/watch?v=${video.id}`,
            upload_status: "processed",
            privacy_status: "public",
            upload_date: video.published_at,
            file_name: `${video.title}.mp4`
          }))
          setUploadedVideos(formattedVideos)
        }
      } catch (error) {
        console.error('Failed to refresh videos list:', error)
      }

      // Reset form
      setVideoFile(null)
      setVideoPreview(null)
      setVideoData({ title: "", description: "", tags: "", privacy_status: "private" })
      setUploadProgress(0)
      
      if (fileInputRef.current) {
        fileInputRef.current.value = ""
      }

    } catch (error: any) {
      console.error('Upload error:', error)
      toast({
        title: "Upload failed",
        description: error.message || "Failed to upload video. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsUploading(false)
    }
  }

  const removeVideo = () => {
    setVideoFile(null)
    setVideoPreview(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  const getPrivacyIcon = (privacy: string) => {
    switch (privacy) {
      case "public": return <Globe className="h-4 w-4" />
      case "unlisted": return <EyeOff className="h-4 w-4" />
      case "private": return <Lock className="h-4 w-4" />
      default: return <Eye className="h-4 w-4" />
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "processed": return <CheckCircle className="h-4 w-4 text-green-500" />
      case "processing": return <Clock className="h-4 w-4 text-yellow-500" />
      case "failed": return <AlertCircle className="h-4 w-4 text-red-500" />
      default: return <Clock className="h-4 w-4 text-gray-500" />
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (!isConnected) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Youtube className="h-5 w-5 text-red-600" />
            YouTube Upload
          </CardTitle>
          <CardDescription>Connect your YouTube account to upload videos</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <Youtube className="h-16 w-16 text-red-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">YouTube Not Connected</h3>
            <p className="text-muted-foreground mb-4">
              Connect your YouTube account to start uploading videos directly from here.
            </p>
            <Button onClick={() => {
              // Set return context so we come back to publishing after connection
              sessionStorage.setItem('youtube_return_context', 'publishing')
              connect()
            }}>
              <Youtube className="mr-2 h-4 w-4" />
              Connect YouTube Account
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Upload Form */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Youtube className="h-5 w-5 text-red-600" />
            Upload Video to YouTube
          </CardTitle>
          <CardDescription>
            Upload videos directly to your connected YouTube channel
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* File Upload */}
          <div className="space-y-3">
            <Label className="text-base font-medium">Video File</Label>
            {!videoFile ? (
              <div
                className="border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-lg p-8 text-center cursor-pointer hover:border-gray-400 transition-colors"
                onClick={() => fileInputRef.current?.click()}
              >
                <Video className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-lg font-medium mb-2">Choose a video file</p>
                <p className="text-sm text-muted-foreground mb-4">
                  Drag and drop your video here, or click to browse
                </p>
                <p className="text-xs text-muted-foreground">
                  Supported formats: MP4, MOV, AVI • Max size: 500MB
                </p>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="video/*"
                  onChange={handleFileSelect}
                  className="hidden"
                />
              </div>
            ) : (
              <div className="relative">
                <div className="border rounded-lg p-4 flex items-center gap-4">
                  <div className="relative">
                    {videoPreview && (
                      <video
                        src={videoPreview}
                        className="w-24 h-16 object-cover rounded"
                        controls={false}
                      />
                    )}
                    <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50 rounded">
                      <Play className="h-6 w-6 text-white" />
                    </div>
                  </div>
                  <div className="flex-1">
                    <p className="font-medium">{videoFile.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {(videoFile.size / (1024 * 1024)).toFixed(2)} MB
                    </p>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={removeVideo}
                    className="text-red-600 hover:text-red-700"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            )}
          </div>

          {/* Video Details */}
          {videoFile && (
            <>
              <div className="space-y-3">
                <Label htmlFor="video-title" className="text-base font-medium">
                  Title *
                </Label>
                <Input
                  id="video-title"
                  placeholder="Enter video title"
                  value={videoData.title}
                  onChange={(e) => setVideoData(prev => ({ ...prev, title: e.target.value }))}
                  maxLength={100}
                />
                <p className="text-xs text-muted-foreground">
                  {videoData.title.length}/100 characters
                </p>
              </div>

              <div className="space-y-3">
                <Label htmlFor="video-description" className="text-base font-medium">
                  Description
                </Label>
                <Textarea
                  id="video-description"
                  placeholder="Tell viewers about your video..."
                  value={videoData.description}
                  onChange={(e) => setVideoData(prev => ({ ...prev, description: e.target.value }))}
                  className="min-h-[100px] resize-none"
                  maxLength={5000}
                />
                <p className="text-xs text-muted-foreground">
                  {videoData.description.length}/5000 characters
                </p>
              </div>

              <div className="space-y-3">
                <Label htmlFor="video-tags" className="text-base font-medium">
                  Tags
                </Label>
                <Input
                  id="video-tags"
                  placeholder="gaming, tutorial, entertainment (comma separated)"
                  value={videoData.tags}
                  onChange={(e) => setVideoData(prev => ({ ...prev, tags: e.target.value }))}
                />
                <p className="text-xs text-muted-foreground">
                  Separate tags with commas. Tags help people find your video.
                </p>
              </div>

              <div className="space-y-3">
                <Label className="text-base font-medium">Privacy</Label>
                <Select
                  value={videoData.privacy_status}
                  onValueChange={(value) => setVideoData(prev => ({ ...prev, privacy_status: value }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="private">
                      <div className="flex items-center gap-2">
                        <Lock className="h-4 w-4" />
                        Private
                      </div>
                    </SelectItem>
                    <SelectItem value="unlisted">
                      <div className="flex items-center gap-2">
                        <EyeOff className="h-4 w-4" />
                        Unlisted
                      </div>
                    </SelectItem>
                    <SelectItem value="public">
                      <div className="flex items-center gap-2">
                        <Globe className="h-4 w-4" />
                        Public
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Upload Progress */}
              {isUploading && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <Label>Upload Progress</Label>
                    <span className="text-sm text-muted-foreground">{uploadProgress}%</span>
                  </div>
                  <Progress value={uploadProgress} className="w-full" />
                  <p className="text-sm text-muted-foreground">
                    {uploadProgress < 100 ? "Uploading video..." : "Processing video..."}
                  </p>
                </div>
              )}

              {/* Upload Button */}
              <Button 
                onClick={handleUpload} 
                disabled={isUploading || !videoData.title.trim()}
                className="w-full"
              >
                <Upload className="mr-2 h-4 w-4" />
                {isUploading ? "Uploading..." : "Upload to YouTube"}
              </Button>
            </>
          )}
        </CardContent>
      </Card>

      {/* Uploaded Videos */}
      {uploadedVideos.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Your YouTube Videos</CardTitle>
            <CardDescription>Recently uploaded videos to your channel</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {uploadedVideos.map((video) => (
                <div
                  key={video.id}
                  className="flex items-start gap-4 p-4 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-900 transition-colors"
                >
                  {/* Thumbnail */}
                  <div className="relative flex-shrink-0">
                    <img
                      src={video.thumbnail}
                      alt={video.title}
                      className="w-24 h-16 object-cover rounded"
                      onError={(e) => {
                        e.currentTarget.src = "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjI0IiBoZWlnaHQ9IjI0IiBmaWxsPSIjRjFGNUY5Ii8+CjxwYXRoIGQ9Ik0xMiAxNkM4LjY4NjI5IDE2IDYgMTMuMzEzNyA2IDEwQzYgNi42ODYyOSA4LjY4NjI5IDQgMTIgNEMxNS4zMTM3IDQgMTggNi42ODYyOSAxOCAxMEMxOCAxMy4zMTM3IDE1LjMxMzcgMTYgMTIgMTZaIiBmaWxsPSIjRDFENU5CIi8+CjwvcmVnPgo="
                      }}
                    />
                    <div className="absolute bottom-1 right-1 bg-black bg-opacity-75 px-1 rounded text-xs text-white">
                      <Play className="h-3 w-3" />
                    </div>
                  </div>

                  {/* Video Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <h3 className="font-medium truncate">{video.title}</h3>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        {getStatusIcon(video.upload_status)}
                        {getPrivacyIcon(video.privacy_status)}
                      </div>
                    </div>
                    
                    {video.description && (
                      <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                        {video.description}
                      </p>
                    )}
                    
                    <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                      <span>Uploaded {formatDate(video.upload_date)}</span>
                      <Badge variant={video.upload_status === "processed" ? "default" : "secondary"}>
                        {video.upload_status}
                      </Badge>
                      <Badge variant="outline">
                        {video.privacy_status}
                      </Badge>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 flex-shrink-0">
                    {video.video_url !== "#" && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => window.open(video.video_url, "_blank")}
                      >
                        <ExternalLink className="h-4 w-4" />
                      </Button>
                    )}
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setUploadedVideos(prev => prev.filter(v => v.id !== video.id))
                        toast({
                          title: "Video removed",
                          description: "Video has been removed from the list.",
                        })
                      }}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
