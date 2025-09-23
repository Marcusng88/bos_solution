'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { useUser } from '@clerk/nextjs'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import { Trash2, Edit, Save, Plus, FileText, Clock, Check, Archive, Send, Facebook, Instagram, Upload, X, ImageIcon, Video } from 'lucide-react'
import { MediaUpload } from './media-upload'
import { PostPreview } from './post-preview'
import { draftService, Draft, CreateDraftData, UpdateDraftData } from '@/lib/draft-service'
import { toast } from '@/hooks/use-toast'

interface DraftTabProps {
  onSelectDraft?: (draft: Draft) => void
  onLoadDraft?: (draft: Draft) => void
}

export function DraftTab({ onSelectDraft, onLoadDraft }: DraftTabProps) {
  const { user } = useUser()
  const [drafts, setDrafts] = useState<Draft[]>([])
  const [selectedDraft, setSelectedDraft] = useState<Draft | null>(null)
  const [isCreating, setIsCreating] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [uploadedMedia, setUploadedMedia] = useState<File[]>([])
  const [isPublishing, setIsPublishing] = useState(false)
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>(['facebook'])

  // Form states
  const [formData, setFormData] = useState<CreateDraftData>({
    title: '',
    content: '',
    platform: 'facebook',
    content_type: 'post',
    status: 'draft',
    hashtags: [],
    media_urls: [],
    scheduling_options: { postType: 'now', scheduledDate: '', scheduledTime: '' },
    metadata: {},
  })

  const loadDrafts = useCallback(async () => {
    if (!user?.id) return

    try {
      setLoading(true)
      const response = await draftService.getDrafts(
        user.id,
        statusFilter === 'all' ? undefined : statusFilter
      )
      setDrafts(response.drafts)
    } catch (error) {
      console.error('Error loading drafts:', error)
      toast({
        title: 'Error',
        description: 'Failed to load drafts',
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }, [user?.id, statusFilter])

  useEffect(() => {
    loadDrafts()
  }, [loadDrafts])

  const handleCreateDraft = async () => {
    if (!user?.id) return

    try {
      // For media, store the files as base64 or upload to backend
      // For now, keep the original approach but ensure media is properly handled
      const mediaUrls = uploadedMedia.map(file => {
        // For demo purposes, use object URLs. In production, upload to cloud storage first
        return URL.createObjectURL(file)
      })

      const draftData = {
        ...formData,
        media_urls: mediaUrls,
        scheduling_options: formData.scheduling_options || { postType: 'now' }
      }

      const draft = await draftService.createDraft(draftData, user.id)
      setDrafts(prev => [draft, ...prev])
      setIsCreating(false)
      resetForm()
      toast({
        title: 'Success',
        description: 'Draft created successfully',
      })
    } catch (error) {
      console.error('Error creating draft:', error)
      toast({
        title: 'Error',
        description: 'Failed to create draft',
        variant: 'destructive',
      })
    }
  }

  const handleUpdateDraft = async () => {
    if (!user?.id || !selectedDraft) return

    try {
      // Convert uploaded media files to URLs for storage
      const mediaUrls = uploadedMedia.length > 0 
        ? uploadedMedia.map(file => URL.createObjectURL(file))
        : formData.media_urls // Keep existing URLs if no new files

      const updateData: UpdateDraftData = {
        title: formData.title,
        content: formData.content,
        platform: formData.platform,
        content_type: formData.content_type,
        status: formData.status,
        hashtags: formData.hashtags,
        media_urls: mediaUrls,
        scheduling_options: formData.scheduling_options || { postType: 'now' },
        metadata: formData.metadata,
      }

      const updatedDraft = await draftService.updateDraft(selectedDraft.id, updateData, user.id)
      
      setDrafts(prev => prev.map(d => d.id === updatedDraft.id ? updatedDraft : d))
      setSelectedDraft(updatedDraft)
      setIsEditing(false)
      
      toast({
        title: 'Success',
        description: 'Draft updated successfully',
      })
    } catch (error) {
      console.error('Error updating draft:', error)
      toast({
        title: 'Error',
        description: 'Failed to update draft',
        variant: 'destructive',
      })
    }
  }

  const handleDeleteDraft = async (draftId: string) => {
    if (!user?.id) return

    if (!confirm('Are you sure you want to delete this draft?')) return

    try {
      await draftService.deleteDraft(draftId, user.id)
      setDrafts(prev => prev.filter(d => d.id !== draftId))
      if (selectedDraft?.id === draftId) {
        setSelectedDraft(null)
      }
      
      toast({
        title: 'Success',
        description: 'Draft deleted successfully',
      })
    } catch (error) {
      console.error('Error deleting draft:', error)
      toast({
        title: 'Error',
        description: 'Failed to delete draft',
        variant: 'destructive',
      })
    }
  }

  const handlePublishDraft = async (draft?: Draft) => {
    if (!user?.id) return
    
    const draftToPublish = draft || selectedDraft
    if (!draftToPublish) return

    setIsPublishing(true)
    try {
      // Use FormData for media file support
      const formData = new FormData()
      
      // Send caption and hashtags separately (don't combine them here)
      formData.append('content_text', draftToPublish.content)
      
      // Send hashtags as separate field if backend supports it
      if (draftToPublish.hashtags && draftToPublish.hashtags.length > 0) {
        formData.append('hashtags', JSON.stringify(draftToPublish.hashtags))
      }
      
      formData.append('platform', draftToPublish.platform)
      
      // Add media files if any
      uploadedMedia.forEach((file) => {
        formData.append('media_files', file)
      })

      const response = await fetch('http://localhost:8000/api/v1/social-media/publish-direct', {
        method: 'POST',
        headers: {
          'X-User-ID': user.id
        },
        body: formData
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const result = await response.json()
      
      if (result.success) {
        let message = `✅ Published successfully!`
        if (result.media_type === 'video') {
          message += `\n📹 Video uploaded to ${draftToPublish.platform}`
        } else if (result.media_type === 'photo') {
          message += `\n📷 Photo uploaded to ${draftToPublish.platform}`
        } else if (result.media_type === 'album') {
          message += `\n📸 Album with ${result.media_count || uploadedMedia.length} photos uploaded`
        } else if (result.media_type === 'text') {
          message += `\n📝 Text post published`
        }
        message += `\n🔗 Post ID: ${result.post_id}`
        
        toast({
          title: 'Success',
          description: message,
        })
        
        // Update draft status to published/archived
        await draftService.updateDraft(draftToPublish.id, { status: 'archived' }, user.id)
        loadDrafts() // Refresh drafts list
        setIsEditing(false)
        setUploadedMedia([])
      } else {
        throw new Error(result.message || 'Publish failed')
      }

    } catch (error) {
      console.error('Publish error:', error)
      toast({
        title: 'Error',
        description: 'Failed to publish draft',
        variant: 'destructive',
      })
    } finally {
      setIsPublishing(false)
    }
  }

  const handleLoadDraft = (draft: Draft) => {
    if (onLoadDraft) {
      onLoadDraft(draft)
      toast({
        title: 'Success',
        description: 'Draft loaded to editor',
      })
    }
  }

  const resetForm = () => {
    setFormData({
      title: '',
      content: '',
      platform: 'facebook',
      content_type: 'post',
      status: 'draft',
      hashtags: [],
      media_urls: [],
      scheduling_options: { postType: 'now', scheduledDate: '', scheduledTime: '' },
      metadata: {},
    })
    setUploadedMedia([])
    setSelectedPlatforms(['facebook'])
  }

  const openEditDialog = (draft: Draft) => {
    setSelectedDraft(draft)
    setFormData({
      title: draft.title,
      content: draft.content,
      platform: draft.platform,
      content_type: draft.content_type,
      status: draft.status,
      hashtags: draft.hashtags,
      media_urls: draft.media_urls,
      scheduling_options: draft.scheduling_options,
      metadata: draft.metadata,
    })
    // Keep existing media - don't clear it when editing
    // setUploadedMedia([]) // This was clearing the media!
    setSelectedPlatforms([draft.platform])
    setIsEditing(true)
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'draft': return <FileText className="w-4 h-4" />
      case 'ready': return <Check className="w-4 h-4" />
      case 'archived': return <Archive className="w-4 h-4" />
      default: return <Clock className="w-4 h-4" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300'
      case 'ready': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
      case 'archived': return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300'
      default: return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300'
    }
  }

  const filteredDrafts = drafts.filter(draft => 
    draft.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    draft.content.toLowerCase().includes(searchQuery.toLowerCase())
  )

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Content Drafts</h2>
          <p className="text-muted-foreground">Manage your content drafts</p>
        </div>
        <Dialog open={isCreating} onOpenChange={setIsCreating}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              New Draft
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[1200px]">
            <DialogHeader>
              <DialogTitle>Create New Draft</DialogTitle>
              <DialogDescription>Create a new content draft with media and publishing options.</DialogDescription>
            </DialogHeader>
            <DraftForm
              formData={formData}
              setFormData={setFormData}
              onSubmit={handleCreateDraft}
              onCancel={() => {
                setIsCreating(false)
                resetForm()
              }}
              isSubmitting={false}
              uploadedMedia={uploadedMedia}
              setUploadedMedia={setUploadedMedia}
              selectedPlatforms={selectedPlatforms}
              setSelectedPlatforms={setSelectedPlatforms}
            />
          </DialogContent>
        </Dialog>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <Input
          placeholder="Search drafts..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="max-w-sm"
        />
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="draft">Draft</SelectItem>
            <SelectItem value="ready">Ready</SelectItem>
            <SelectItem value="archived">Archived</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Drafts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredDrafts.map((draft) => (
          <Card key={draft.id} className="hover:shadow-md transition-shadow">
            <CardHeader className="pb-2">
              <div className="flex items-start justify-between">
                <div className="space-y-1 flex-1 mr-2">
                  <CardTitle className="text-sm font-medium line-clamp-2">
                    {draft.title}
                  </CardTitle>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-xs">
                      <Facebook className="w-3 h-3 mr-1" />
                      {draft.platform}
                    </Badge>
                    <Badge className={`text-xs ${getStatusColor(draft.status)}`}>
                      <div className="flex items-center gap-1">
                        {getStatusIcon(draft.status)}
                        {draft.status}
                      </div>
                    </Badge>
                  </div>
                </div>
                <div className="flex gap-1">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handlePublishDraft(draft)}
                    disabled={isPublishing}
                    className="text-green-600 hover:text-green-700"
                  >
                    <Send className="w-3 h-3" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => openEditDialog(draft)}
                  >
                    <Edit className="w-3 h-3" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDeleteDraft(draft.id)}
                  >
                    <Trash2 className="w-3 h-3" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground line-clamp-3 mb-3">
                {draft.content}
              </p>
              
              {/* Media Preview */}
              {draft.media_urls && draft.media_urls.length > 0 && (
                <div className="flex gap-2 mb-3">
                  {draft.media_urls.slice(0, 3).map((url, index) => (
                    <div key={index} className="w-12 h-12 rounded border overflow-hidden bg-gray-100">
                      <img 
                        src={url} 
                        alt={`Media ${index + 1}`} 
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          (e.target as HTMLImageElement).style.display = 'none'
                        }}
                      />
                    </div>
                  ))}
                  {draft.media_urls.length > 3 && (
                    <div className="w-12 h-12 rounded border flex items-center justify-center bg-gray-100 text-xs">
                      +{draft.media_urls.length - 3}
                    </div>
                  )}
                </div>
              )}
              
              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <span>Updated {new Date(draft.updated_at).toLocaleDateString()}</span>
                <div className="flex gap-1">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleLoadDraft(draft)}
                    className="h-7 text-xs"
                  >
                    Load to Editor
                  </Button>
                  <Button
                    variant="default"
                    size="sm"
                    onClick={() => handlePublishDraft(draft)}
                    disabled={isPublishing}
                    className="h-7 text-xs bg-blue-600 hover:bg-blue-700"
                  >
                    {isPublishing ? (
                      <div className="w-3 h-3 animate-spin rounded-full border-2 border-background border-t-foreground" />
                    ) : (
                      <>
                        <Send className="w-3 h-3 mr-1" />
                        Publish
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredDrafts.length === 0 && (
        <div className="text-center py-12">
          <FileText className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <h3 className="mt-2 text-sm font-semibold text-gray-900 dark:text-gray-100">No drafts found</h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchQuery || statusFilter !== 'all' 
              ? "Try adjusting your filters or search terms." 
              : "Get started by creating your first draft."}
          </p>
        </div>
      )}

      {/* Edit Dialog */}
      <Dialog open={isEditing} onOpenChange={setIsEditing}>
        <DialogContent className="sm:max-w-[1200px]">
          <DialogHeader>
            <DialogTitle>Edit Draft</DialogTitle>
            <DialogDescription>Make changes to your draft content and publish directly to social media.</DialogDescription>
          </DialogHeader>
          <DraftForm
            formData={formData}
            setFormData={setFormData}
            onSubmit={handleUpdateDraft}
            onCancel={() => {
              setIsEditing(false)
              setSelectedDraft(null)
              resetForm()
            }}
            isSubmitting={false}
            isEditing={true}
            uploadedMedia={uploadedMedia}
            setUploadedMedia={setUploadedMedia}
            onPublish={() => selectedDraft && handlePublishDraft(selectedDraft)}
            isPublishing={isPublishing}
            selectedPlatforms={selectedPlatforms}
            setSelectedPlatforms={setSelectedPlatforms}
          />
        </DialogContent>
      </Dialog>
    </div>
  )
}

interface DraftFormProps {
  formData: CreateDraftData
  setFormData: (data: CreateDraftData) => void
  onSubmit: () => void
  onCancel: () => void
  isSubmitting: boolean
  isEditing?: boolean
  uploadedMedia: File[]
  setUploadedMedia: (files: File[]) => void
  onPublish?: () => void
  isPublishing?: boolean
  selectedPlatforms: string[]
  setSelectedPlatforms: (platforms: string[]) => void
}

const platforms = [
  { id: "facebook", name: "Facebook", icon: Facebook, color: "bg-blue-600", connected: true },
  { id: "instagram", name: "Instagram", icon: Instagram, color: "bg-pink-600", connected: true },
]

function DraftForm({ 
  formData, 
  setFormData, 
  onSubmit, 
  onCancel, 
  isSubmitting, 
  isEditing = false,
  uploadedMedia,
  setUploadedMedia,
  onPublish,
  isPublishing = false,
  selectedPlatforms,
  setSelectedPlatforms
}: DraftFormProps) {
  const [hashtagsInput, setHashtagsInput] = useState(formData.hashtags?.join(', ') || '')
  
  // Sync hashtagsInput when formData.hashtags changes (for editing existing drafts)
  useEffect(() => {
    setHashtagsInput(formData.hashtags?.join(', ') || '')
  }, [formData.hashtags])
  
  const handleHashtagsChange = (value: string) => {
    setHashtagsInput(value)
  }

  const handleHashtagsBlur = () => {
    const hashtags = hashtagsInput
      .split(',')
      .map(tag => tag.trim().replace(/^#+/, '')) // Remove # prefix if present
      .filter(tag => tag.length > 0)
    setFormData({ ...formData, hashtags })
  }

  // Process hashtags from input and update formData
  const processHashtagsFromInput = () => {
    const hashtags = hashtagsInput
      .split(',')
      .map(tag => tag.trim().replace(/^#+/, '')) // Remove # prefix if present
      .filter(tag => tag.length > 0)
    setFormData({ ...formData, hashtags })
    return hashtags
  }

  // Handle publish with hashtags processing
  const handlePublishWithHashtags = () => {
    // Process current hashtags input before publishing
    processHashtagsFromInput()
    // Call the original onPublish
    if (onPublish) {
      // Use setTimeout to ensure state update completes first
      setTimeout(() => {
        onPublish()
      }, 0)
    }
  }

  const handlePlatformToggle = (platformId: string) => {
    setSelectedPlatforms(
      selectedPlatforms.includes(platformId)
        ? selectedPlatforms.filter(id => id !== platformId)
        : [...selectedPlatforms, platformId]
    )
    // Update primary platform in form data
    if (selectedPlatforms.length === 0 || !selectedPlatforms.includes(formData.platform)) {
      setFormData({ ...formData, platform: platformId })
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 max-h-[80vh] overflow-y-auto">
      {/* Left Column - Form */}
      <div className="space-y-6">
        {/* Platform Selection */}
        <div className="space-y-3">
          <Label className="text-base font-medium">Select Platforms</Label>
          <div className="grid grid-cols-2 gap-3">
            {platforms.map((platform) => {
              const Icon = platform.icon
              const isSelected = selectedPlatforms.includes(platform.id)
              return (
                <div
                  key={platform.id}
                  className={`relative rounded-lg border-2 transition-all cursor-pointer ${
                    isSelected
                      ? 'border-primary bg-primary/5'
                      : 'border-border hover:border-primary/50'
                  }`}
                  onClick={() => handlePlatformToggle(platform.id)}
                >
                  <div className="p-4 flex items-center space-x-3">
                    <Checkbox checked={isSelected} />
                    <Icon className={`h-5 w-5 ${isSelected ? 'text-primary' : 'text-muted-foreground'}`} />
                    <span className={`font-medium ${isSelected ? 'text-primary' : 'text-muted-foreground'}`}>
                      {platform.name}
                    </span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Basic Info */}
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="title">Title</Label>
            <Input
              id="title"
              placeholder="Enter draft title..."
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="content_type">Content Type</Label>
            <Select value={formData.content_type} onValueChange={(value) => setFormData({ ...formData, content_type: value })}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="post">Post</SelectItem>
                <SelectItem value="story">Story</SelectItem>
                <SelectItem value="reel">Reel</SelectItem>
                <SelectItem value="video">Video</SelectItem>
                <SelectItem value="article">Article</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Content */}
        <div className="space-y-3">
          <Label className="text-base font-medium">Caption</Label>
          <Textarea
            id="content"
            placeholder="What's on your mind? Share your story..."
            value={formData.content}
            onChange={(e) => setFormData({ ...formData, content: e.target.value })}
            className="min-h-[120px] resize-none"
          />
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>{formData.content.length} characters</span>
            <span>Recommended: 125-150 characters for optimal engagement</span>
          </div>
        </div>

        {/* Media Upload */}
        <div className="space-y-3">
          <Label className="text-base font-medium">Media</Label>
          <MediaUpload onMediaUpload={setUploadedMedia} uploadedMedia={uploadedMedia} />
        </div>

        {/* Hashtags */}
        <div className="space-y-2">
          <Label htmlFor="hashtags">Hashtags (comma separated)</Label>
          <Input
            id="hashtags"
            placeholder="#example, #content, #marketing"
            value={hashtagsInput}
            onChange={(e) => handleHashtagsChange(e.target.value)}
            onBlur={handleHashtagsBlur}
          />
        </div>

        {/* Publishing Options */}
        <div className="space-y-3">
          <Label className="text-base font-medium">Publishing Options</Label>
          <Select
            value={formData.scheduling_options?.postType || 'now'}
            onValueChange={(value) => setFormData({ 
              ...formData, 
              scheduling_options: { ...formData.scheduling_options, postType: value } 
            })}
          >
            <SelectTrigger>
              <SelectValue placeholder="Choose when to publish" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="now">Publish Now</SelectItem>
              <SelectItem value="schedule">Schedule for Later</SelectItem>
              <SelectItem value="optimal">Publish at Optimal Time</SelectItem>
            </SelectContent>
          </Select>

          {formData.scheduling_options?.postType === "schedule" && (
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label htmlFor="date">Date</Label>
                <Input
                  id="date"
                  type="date"
                  value={formData.scheduling_options?.scheduledDate || ''}
                  onChange={(e) => setFormData({ 
                    ...formData, 
                    scheduling_options: { ...formData.scheduling_options, scheduledDate: e.target.value } 
                  })}
                />
              </div>
              <div>
                <Label htmlFor="time">Time</Label>
                <Input
                  id="time"
                  type="time"
                  value={formData.scheduling_options?.scheduledTime || ''}
                  onChange={(e) => setFormData({ 
                    ...formData, 
                    scheduling_options: { ...formData.scheduling_options, scheduledTime: e.target.value } 
                  })}
                />
              </div>
            </div>
          )}

          {formData.scheduling_options?.postType === "optimal" && (
            <div className="p-3 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
              <p className="text-sm text-blue-800 dark:text-blue-200">
                AI will analyze your audience activity and schedule this post for maximum engagement.
              </p>
            </div>
          )}
        </div>

        {/* Status */}
        <div className="space-y-2">
          <Label htmlFor="status">Draft Status</Label>
          <Select value={formData.status || 'draft'} onValueChange={(value) => setFormData({ ...formData, status: value })}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="draft">Draft</SelectItem>
              <SelectItem value="ready">Ready</SelectItem>
              <SelectItem value="archived">Archived</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Right Column - Preview */}
      <div className="space-y-4">
        <Label className="text-base font-medium">Post Preview</Label>
        <PostPreview
          caption={formData.content}
          hashtags={formData.hashtags || []}
          media={uploadedMedia}
          platforms={selectedPlatforms}
          scheduledDate={formData.scheduling_options?.scheduledDate || ''}
          scheduledTime={formData.scheduling_options?.scheduledTime || ''}
          postType={formData.scheduling_options?.postType || 'now'}
        />
      </div>

      {/* Action Buttons */}
      <div className="lg:col-span-2 flex gap-3 pt-6 border-t">
        <Button variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button 
          onClick={() => {
            // Process hashtags before saving
            handleHashtagsBlur()
            onSubmit()
          }} 
          disabled={isSubmitting || !formData.title.trim() || !formData.content.trim()}
          variant="outline"
        >
          <Save className="w-4 h-4 mr-2" />
          {isEditing ? 'Update' : 'Save'} Draft
        </Button>
        {onPublish && (
          <Button 
            onClick={handlePublishWithHashtags}
            disabled={isPublishing || !formData.content.trim()}
            className="flex-1"
          >
            {isPublishing ? (
              <>
                <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-background border-t-foreground" />
                Publishing...
              </>
            ) : formData.scheduling_options?.postType === "now" ? (
              <>
                <Send className="mr-2 h-4 w-4" />
                Publish Now
              </>
            ) : (
              <>
                <Send className="mr-2 h-4 w-4" />
                Publish
              </>
            )}
          </Button>
        )}
      </div>
    </div>
  )
}