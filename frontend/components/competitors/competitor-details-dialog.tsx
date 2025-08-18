"use client"

import { useState, useEffect } from "react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { Badge } from "@/components/ui/badge"
import { Youtube, Instagram, Twitter, Facebook, Linkedin, Globe, Edit3, Save, X } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { competitorAPI } from "@/lib/api-client"
import { Competitor, CompetitorUpdate, Platform } from "@/lib/types"
import { useUser } from "@clerk/nextjs"

interface CompetitorDetailsDialogProps {
  competitor: Competitor
  onCompetitorUpdated: () => void
  trigger?: React.ReactNode
}

const AVAILABLE_PLATFORMS: Platform[] = [
  {
    id: "youtube",
    name: "YouTube",
    icon: "🎥",
    description: "Video content and channel monitoring"
  },
  {
    id: "instagram",
    name: "Instagram",
    icon: "📸",
    description: "Photo and story content monitoring"
  },
  {
    id: "twitter",
    name: "Twitter/X",
    icon: "🐦",
    description: "Tweet and thread monitoring"
  },
  {
    id: "facebook",
    name: "Facebook",
    icon: "📘",
    description: "Page and post monitoring"
  },
  {
    id: "linkedin",
    name: "LinkedIn",
    icon: "💼",
    description: "Company page and content monitoring"
  },
  {
    id: "website",
    name: "Website",
    icon: "🌐",
    description: "Website changes and updates monitoring"
  }
]

export function CompetitorDetailsDialog({ competitor, onCompetitorUpdated, trigger }: CompetitorDetailsDialogProps) {
  const [open, setOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [formData, setFormData] = useState<CompetitorUpdate>({
    name: competitor.name,
    description: competitor.description || "",
    website_url: competitor.website_url || "",
    industry: competitor.industry || "",
    platforms: competitor.platforms || ["youtube"],
    scan_frequency_minutes: competitor.scan_frequency_minutes
  })
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>(competitor.platforms || ["youtube"])
  const [socialHandles, setSocialHandles] = useState<Record<string, string>>(competitor.social_media_handles || {})
  const { toast } = useToast()
  const { user } = useUser()

  // Reset form data when competitor changes
  useEffect(() => {
    setFormData({
      name: competitor.name,
      description: competitor.description || "",
      website_url: competitor.website_url || "",
      industry: competitor.industry || "",
      platforms: competitor.platforms || ["youtube"],
      scan_frequency_minutes: competitor.scan_frequency_minutes
    })
    setSelectedPlatforms(competitor.platforms || ["youtube"])
    setSocialHandles(competitor.social_media_handles || {})
  }, [competitor])

  const handleInputChange = (field: keyof CompetitorUpdate, value: string | number) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handlePlatformToggle = (platformId: string, checked: boolean) => {
    if (checked) {
      setSelectedPlatforms(prev => [...prev, platformId])
    } else {
      setSelectedPlatforms(prev => prev.filter(id => id !== platformId))
      // Remove social handle for deselected platform
      setSocialHandles(prev => {
        const newHandles = { ...prev }
        delete newHandles[platformId]
        return newHandles
      })
    }
  }

  const handleSocialHandleChange = (platformId: string, handle: string) => {
    setSocialHandles(prev => ({
      ...prev,
      [platformId]: handle
    }))
  }

  const handleSave = async () => {
    if (!user) {
      toast({
        title: "Error",
        description: "User not authenticated. Please log in again.",
        variant: "destructive"
      })
      return
    }

    // Validate required fields
    if (!formData.name?.trim()) {
      toast({
        title: "Error",
        description: "Competitor name is required.",
        variant: "destructive"
      })
      return
    }

    setIsLoading(true)
    try {
      const updateData: CompetitorUpdate = {
        name: formData.name.trim(),
        description: formData.description?.trim() || undefined,
        website_url: formData.website_url?.trim() || undefined,
        industry: formData.industry?.trim() || undefined,
        platforms: selectedPlatforms,
        social_media_handles: Object.keys(socialHandles).length > 0 ? socialHandles : undefined,
        scan_frequency_minutes: formData.scan_frequency_minutes
      }

      await competitorAPI.updateCompetitor(competitor.id, updateData, user.id)
      
      toast({
        title: "Success",
        description: `Competitor "${formData.name}" updated successfully!`
      })
      
      setIsEditing(false)
      onCompetitorUpdated()
      
    } catch (error) {
      console.error("Error updating competitor:", error)
      
      let errorMessage = "Failed to update competitor. Please try again.";
      if (error instanceof Error) {
        errorMessage = error.message;
      }
      
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive"
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleCancel = () => {
    // Reset form data to original values
    setFormData({
      name: competitor.name,
      description: competitor.description || "",
      website_url: competitor.website_url || "",
      industry: competitor.industry || "",
      platforms: competitor.platforms || ["youtube"],
      scan_frequency_minutes: competitor.scan_frequency_minutes
    })
    setSelectedPlatforms(competitor.platforms || ["youtube"])
    setSocialHandles(competitor.social_media_handles || {})
    setIsEditing(false)
  }

  const getPlatformIcon = (platformId: string) => {
    switch (platformId) {
      case "youtube": return <Youtube className="h-4 w-4" />
      case "instagram": return <Instagram className="h-4 w-4" />
      case "twitter": return <Twitter className="h-4 w-4" />
      case "facebook": return <Facebook className="h-4 w-4" />
      case "linkedin": return <Linkedin className="h-4 w-4" />
      case "website": return <Globe className="h-4 w-4" />
      default: return <Globe className="h-4 w-4" />
    }
  }

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'active': return 'default'
      case 'paused': return 'secondary'
      case 'error': return 'destructive'
      default: return 'outline'
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || <Button variant="ghost" size="sm">View Details</Button>}
      </DialogTrigger>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <div>
              <DialogTitle>Competitor Details</DialogTitle>
              <DialogDescription>
                {isEditing ? "Edit competitor information and monitoring settings" : "View and manage competitor details"}
              </DialogDescription>
            </div>
            <div className="flex items-center gap-2">
              {!isEditing ? (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setIsEditing(true)}
                >
                  <Edit3 className="mr-2 h-4 w-4" />
                  Edit
                </Button>
              ) : (
                <>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleCancel}
                    disabled={isLoading}
                  >
                    <X className="mr-2 h-4 w-4" />
                    Cancel
                  </Button>
                  <Button
                    size="sm"
                    onClick={handleSave}
                    disabled={isLoading}
                  >
                    <Save className="mr-2 h-4 w-4" />
                    {isLoading ? "Saving..." : "Save"}
                  </Button>
                </>
              )}
            </div>
          </div>
        </DialogHeader>
        
        <div className="space-y-6">
          {/* Basic Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Basic Information</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="name">Competitor Name *</Label>
                {isEditing ? (
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => handleInputChange("name", e.target.value)}
                    placeholder="Enter competitor name"
                    required
                  />
                ) : (
                  <div className="p-3 bg-muted rounded-md">
                    <span className="font-medium">{competitor.name}</span>
                  </div>
                )}
              </div>
              
              <div className="space-y-2">
                <Label>Status</Label>
                <div className="p-3 bg-muted rounded-md">
                  <Badge variant={getStatusBadgeVariant(competitor.status)}>
                    {competitor.status}
                  </Badge>
                </div>
              </div>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              {isEditing ? (
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => handleInputChange("description", e.target.value)}
                  placeholder="Brief description of the competitor"
                  rows={3}
                />
              ) : (
                <div className="p-3 bg-muted rounded-md">
                  <span>{competitor.description || "No description provided"}</span>
                </div>
              )}
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="website_url">Website URL</Label>
                {isEditing ? (
                  <Input
                    id="website_url"
                    type="url"
                    value={formData.website_url}
                    onChange={(e) => handleInputChange("website_url", e.target.value)}
                    placeholder="https://example.com"
                  />
                ) : (
                  <div className="p-3 bg-muted rounded-md">
                    <span>{competitor.website_url || "No website provided"}</span>
                  </div>
                )}
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="industry">Industry</Label>
                {isEditing ? (
                  <Input
                    id="industry"
                    value={formData.industry}
                    onChange={(e) => handleInputChange("industry", e.target.value)}
                    placeholder="e.g., Fashion, Technology, Food"
                  />
                ) : (
                  <div className="p-3 bg-muted rounded-md">
                    <span>{competitor.industry || "No industry specified"}</span>
                  </div>
                )}
              </div>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="scan_frequency">Scan Frequency</Label>
              {isEditing ? (
                <Select
                  value={formData.scan_frequency_minutes?.toString()}
                  onValueChange={(value) => handleInputChange("scan_frequency_minutes", parseInt(value))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select scan frequency" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="15">Every 15 minutes</SelectItem>
                    <SelectItem value="30">Every 30 minutes</SelectItem>
                    <SelectItem value="60">Every hour</SelectItem>
                    <SelectItem value="240">Every 4 hours</SelectItem>
                    <SelectItem value="480">Every 8 hours</SelectItem>
                    <SelectItem value="1440">Daily</SelectItem>
                  </SelectContent>
                </Select>
              ) : (
                <div className="p-3 bg-muted rounded-md">
                  <span>Every {competitor.scan_frequency_minutes} minutes</span>
                </div>
              )}
            </div>
          </div>
          
          {/* Platform Selection */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Platforms to Monitor</h3>
            <p className="text-sm text-muted-foreground">
              {isEditing ? "Select the platforms you want to monitor for this competitor" : "Currently monitored platforms"}
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {AVAILABLE_PLATFORMS.map((platform) => (
                <div key={platform.id} className="flex items-start space-x-3 p-3 border rounded-lg">
                  {isEditing ? (
                    <Checkbox
                      id={platform.id}
                      checked={selectedPlatforms.includes(platform.id)}
                      onCheckedChange={(checked) => handlePlatformToggle(platform.id, checked as boolean)}
                    />
                  ) : (
                    <div className="w-4 h-4 flex items-center justify-center">
                      {selectedPlatforms.includes(platform.id) && (
                        <div className="w-3 h-3 bg-primary rounded-full" />
                      )}
                    </div>
                  )}
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center space-x-2">
                      <span className="text-lg">{platform.icon}</span>
                      <Label htmlFor={platform.id} className="font-medium cursor-pointer">
                        {platform.name}
                      </Label>
                    </div>
                    <p className="text-xs text-muted-foreground">{platform.description}</p>
                    
                    {selectedPlatforms.includes(platform.id) && platform.id !== "website" && (
                      <div className="pt-2">
                        {isEditing ? (
                          <Input
                            placeholder={`${platform.name} handle or username`}
                            value={socialHandles[platform.id] || ""}
                            onChange={(e) => handleSocialHandleChange(platform.id, e.target.value)}
                            className="text-sm"
                          />
                        ) : (
                          <div className="text-sm text-muted-foreground">
                            Handle: {socialHandles[platform.id] || "Not specified"}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          {/* Monitoring Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Monitoring Information</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Last Scan</Label>
                <div className="p-3 bg-muted rounded-md">
                  <span>
                    {competitor.last_scan_at 
                      ? new Date(competitor.last_scan_at).toLocaleString()
                      : "Never scanned"
                    }
                  </span>
                </div>
              </div>
              
              <div className="space-y-2">
                <Label>Created</Label>
                <div className="p-3 bg-muted rounded-md">
                  <span>{new Date(competitor.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
