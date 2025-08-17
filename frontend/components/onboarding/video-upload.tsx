"use client"

import { useState, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Upload, Video, X, Loader2, CheckCircle, AlertCircle } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { useYouTubeStore } from "@/hooks/use-youtube"

interface VideoUploadProps {
  onClose?: () => void
}

export function VideoUpload({ onClose }: VideoUploadProps) {
  const { toast } = useToast()
  const { isConnected, uploadVideo } = useYouTubeStore()
  const fileInputRef = useRef<HTMLInputElement>(null)
  
  const [videoFile, setVideoFile] = useState<File | null>(null)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle')
  
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    tags: '',
    privacy_status: 'private'
  })

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      // Check file size (YouTube max is 256GB, but we'll set a reasonable limit)
      const maxSize = 2 * 1024 * 1024 * 1024 // 2GB
      if (file.size > maxSize) {
        toast({
          title: "File too large",
          description: "Please select a video file smaller than 2GB.",
          variant: "destructive",
        })
        return
      }

      // Check file type
      const allowedTypes = ['video/mp4', 'video/avi', 'video/mov', 'video/wmv', 'video/flv', 'video/webm']
      if (!allowedTypes.includes(file.type)) {
        toast({
          title: "Unsupported file type",
          description: "Please select a valid video file (MP4, AVI, MOV, WMV, FLV, WebM).",
          variant: "destructive",
        })
        return
      }

      setVideoFile(file)
      
      // Auto-populate title from filename if empty
      if (!formData.title) {
        const filename = file.name.replace(/\.[^/.]+$/, "") // Remove extension
        setFormData(prev => ({ ...prev, title: filename }))
      }
    }
  }

  const handleUpload = async () => {
    if (!isConnected) {
      toast({
        title: "Not connected",
        description: "Please connect your YouTube account first.",
        variant: "destructive",
      })
      return
    }

    if (!videoFile) {
      toast({
        title: "No file selected",
        description: "Please select a video file to upload.",
        variant: "destructive",
      })
      return
    }

    if (!formData.title.trim()) {
      toast({
        title: "Title required",
        description: "Please enter a title for your video.",
        variant: "destructive",
      })
      return
    }

    setIsUploading(true)
    setUploadStatus('uploading')
    setUploadProgress(0)

    try {
      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return 90
          }
          return prev + Math.random() * 10
        })
      }, 500)

      const tags = formData.tags
        .split(',')
        .map(tag => tag.trim())
        .filter(tag => tag.length > 0)

      const result = await uploadVideo({
        title: formData.title,
        description: formData.description,
        tags,
        privacy_status: formData.privacy_status
      })

      clearInterval(progressInterval)
      setUploadProgress(100)
      setUploadStatus('success')

      toast({
        title: "Upload prepared!",
        description: "Video metadata has been prepared. In a real implementation, the file would be uploaded to YouTube.",
      })

      // Reset form after successful upload
      setTimeout(() => {
        setVideoFile(null)
        setFormData({
          title: '',
          description: '',
          tags: '',
          privacy_status: 'private'
        })
        setUploadProgress(0)
        setUploadStatus('idle')
        if (fileInputRef.current) {
          fileInputRef.current.value = ''
        }
      }, 3000)

    } catch (error: any) {
      setUploadStatus('error')
      toast({
        title: "Upload failed",
        description: error.message || "Failed to upload video. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsUploading(false)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const getStatusIcon = () => {
    switch (uploadStatus) {
      case 'uploading':
        return <Loader2 className="h-5 w-5 animate-spin text-blue-600" />
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-600" />
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-600" />
      default:
        return null
    }
  }

  if (!isConnected) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Video className="h-5 w-5" />
            YouTube Upload
          </CardTitle>
          <CardDescription>
            Connect your YouTube account to upload videos
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <Video className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <p className="text-muted-foreground">
              Please connect your YouTube account in the onboarding process to upload videos.
            </p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="w-full max-w-2xl">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Video className="h-5 w-5" />
              Upload to YouTube
            </CardTitle>
            <CardDescription>
              Upload and manage your video content
            </CardDescription>
          </div>
          {onClose && (
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* File Upload */}
        <div>
          <label className="block text-sm font-medium mb-2">Video File</label>
          {!videoFile ? (
            <div
              className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center hover:border-gray-400 dark:hover:border-gray-500 transition-colors cursor-pointer"
              onClick={() => fileInputRef.current?.click()}
            >
              <Upload className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
              <p className="text-muted-foreground mb-1">Click to select a video file</p>
              <p className="text-xs text-muted-foreground">
                Supports MP4, AVI, MOV, WMV, FLV, WebM (max 2GB)
              </p>
            </div>
          ) : (
            <div className="border rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Video className="h-8 w-8 text-blue-600" />
                  <div>
                    <p className="font-medium">{videoFile.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {formatFileSize(videoFile.size)}
                    </p>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setVideoFile(null)
                    if (fileInputRef.current) {
                      fileInputRef.current.value = ''
                    }
                  }}
                  disabled={isUploading}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
              
              {uploadStatus === 'uploading' && (
                <div className="mt-4">
                  <div className="flex items-center gap-2 mb-2">
                    {getStatusIcon()}
                    <span className="text-sm">Uploading...</span>
                  </div>
                  <Progress value={uploadProgress} className="h-2" />
                  <p className="text-xs text-muted-foreground mt-1">
                    {uploadProgress.toFixed(0)}% complete
                  </p>
                </div>
              )}
              
              {uploadStatus === 'success' && (
                <div className="mt-4 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                  <div className="flex items-center gap-2">
                    {getStatusIcon()}
                    <span className="text-sm text-green-800 dark:text-green-200">
                      Upload successful!
                    </span>
                  </div>
                </div>
              )}
              
              {uploadStatus === 'error' && (
                <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
                  <div className="flex items-center gap-2">
                    {getStatusIcon()}
                    <span className="text-sm text-red-800 dark:text-red-200">
                      Upload failed. Please try again.
                    </span>
                  </div>
                </div>
              )}
            </div>
          )}
          <input
            ref={fileInputRef}
            type="file"
            accept="video/*"
            onChange={handleFileSelect}
            className="hidden"
          />
        </div>

        {/* Video Details */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Title *</label>
            <Input
              value={formData.title}
              onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
              placeholder="Enter video title"
              disabled={isUploading}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Description</label>
            <Textarea
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              placeholder="Enter video description"
              rows={4}
              disabled={isUploading}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Tags</label>
            <Input
              value={formData.tags}
              onChange={(e) => setFormData(prev => ({ ...prev, tags: e.target.value }))}
              placeholder="Enter tags separated by commas"
              disabled={isUploading}
            />
            <p className="text-xs text-muted-foreground mt-1">
              Separate multiple tags with commas
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Privacy</label>
            <Select
              value={formData.privacy_status}
              onValueChange={(value) => setFormData(prev => ({ ...prev, privacy_status: value }))}
              disabled={isUploading}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="private">Private</SelectItem>
                <SelectItem value="unlisted">Unlisted</SelectItem>
                <SelectItem value="public">Public</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Upload Button */}
        <Button
          onClick={handleUpload}
          disabled={!videoFile || !formData.title.trim() || isUploading}
          className="w-full"
        >
          {isUploading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Uploading...
            </>
          ) : (
            <>
              <Upload className="mr-2 h-4 w-4" />
              Upload to YouTube
            </>
          )}
        </Button>

        {/* Note */}
        <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <p className="text-xs text-blue-800 dark:text-blue-200">
            <strong>Note:</strong> This is a demo implementation. In production, this would handle actual file uploads to YouTube using their resumable upload API.
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
