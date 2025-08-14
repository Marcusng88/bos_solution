"use client"

import type React from "react"

import { useRef } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { useToast } from "@/hooks/use-toast"
import { Upload, X, ImageIcon, Video, FileText } from "lucide-react"

interface MediaUploadProps {
  onMediaUpload: (files: File[]) => void
  uploadedMedia: File[]
}

export function MediaUpload({ onMediaUpload, uploadedMedia }: MediaUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const { toast } = useToast()

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || [])

    // Validate file types and sizes
    const validFiles = files.filter((file) => {
      const isValidType = file.type.startsWith("image/") || file.type.startsWith("video/")
      const isValidSize = file.size <= 50 * 1024 * 1024 // 50MB limit

      if (!isValidType) {
        toast({
          title: "Invalid file type",
          description: `${file.name} is not a supported image or video file.`,
          variant: "destructive",
        })
        return false
      }

      if (!isValidSize) {
        toast({
          title: "File too large",
          description: `${file.name} exceeds the 50MB size limit.`,
          variant: "destructive",
        })
        return false
      }

      return true
    })

    if (validFiles.length > 0) {
      onMediaUpload([...uploadedMedia, ...validFiles])
      toast({
        title: "Media uploaded",
        description: `${validFiles.length} file(s) added successfully.`,
      })
    }

    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  const removeFile = (index: number) => {
    const newFiles = uploadedMedia.filter((_, i) => i !== index)
    onMediaUpload(newFiles)
  }

  const getFileIcon = (file: File) => {
    if (file.type.startsWith("image/")) return ImageIcon
    if (file.type.startsWith("video/")) return Video
    return FileText
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
  }

  return (
    <div className="space-y-4">
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept="image/*,video/*"
        onChange={handleFileSelect}
        className="hidden"
      />

      <Button variant="outline" onClick={() => fileInputRef.current?.click()} className="w-full h-24 border-dashed">
        <div className="text-center">
          <Upload className="mx-auto h-6 w-6 mb-2" />
          <span>Click to upload images or videos</span>
          <p className="text-xs text-muted-foreground mt-1">Supports JPG, PNG, GIF, MP4, MOV (max 50MB)</p>
        </div>
      </Button>

      {uploadedMedia.length > 0 && (
        <div className="grid grid-cols-2 gap-3">
          {uploadedMedia.map((file, index) => {
            const FileIcon = getFileIcon(file)
            return (
              <Card key={index} className="p-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 flex-1 min-w-0">
                    <FileIcon className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium truncate">{file.name}</p>
                      <p className="text-xs text-muted-foreground">{formatFileSize(file.size)}</p>
                    </div>
                  </div>
                  <Button variant="ghost" size="sm" onClick={() => removeFile(index)} className="flex-shrink-0">
                    <X className="h-4 w-4" />
                  </Button>
                </div>

                {file.type.startsWith("image/") && (
                  <div className="mt-2">
                    <img
                      src={URL.createObjectURL(file) || "/placeholder.svg"}
                      alt={file.name}
                      className="w-full h-20 object-cover rounded"
                    />
                  </div>
                )}
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}
