"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { Plus, Youtube, Instagram, Twitter, Facebook, Linkedin, Globe } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { competitorAPI } from "@/lib/api-client"
import { CompetitorCreate, Platform } from "@/lib/types"
import { useUser } from "@clerk/nextjs"

interface AddCompetitorModalProps {
  onCompetitorAdded: () => void
  isOpen: boolean
  onClose: () => void
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

export function AddCompetitorModal({ onCompetitorAdded, isOpen, onClose }: AddCompetitorModalProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [formData, setFormData] = useState<CompetitorCreate>({
    name: "",
    description: "",
    website_url: "",
    industry: "",
    scan_frequency_minutes: 60
  })
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>(["youtube"])
  const [socialHandles, setSocialHandles] = useState<Record<string, string>>({})
  const { toast } = useToast()
  const { user } = useUser()

  const handleInputChange = (field: keyof CompetitorCreate, value: string | number) => {
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!user) {
      toast({
        title: "Error",
        description: "User not authenticated. Please log in again.",
        variant: "destructive"
      })
      return
    }

    // Validate required fields
    if (!formData.name.trim()) {
      toast({
        title: "Error",
        description: "Competitor name is required.",
        variant: "destructive"
      })
      return
    }

    // Validate scan frequency
    if (formData.scan_frequency_minutes && (formData.scan_frequency_minutes < 15 || formData.scan_frequency_minutes > 1440)) {
      toast({
        title: "Error",
        description: "Scan frequency must be between 15 minutes and 24 hours.",
        variant: "destructive"
      })
      return
    }

    setIsLoading(true)
    try {
      const competitorData: CompetitorCreate = {
        name: formData.name.trim(), // Ensure name is trimmed
        description: formData.description?.trim() || undefined,
        website_url: formData.website_url?.trim() || undefined,
        industry: formData.industry?.trim() || undefined,
        platforms: selectedPlatforms, // Include selected platforms
        social_media_handles: Object.keys(socialHandles).length > 0 ? socialHandles : undefined,
        scan_frequency_minutes: formData.scan_frequency_minutes || 60
      }

      console.log('Submitting competitor data:', competitorData);
      console.log('User ID:', user.id);

      await competitorAPI.createCompetitor(competitorData, user.id)
      
      toast({
        title: "Success",
        description: `Competitor "${formData.name}" added successfully!`
      })
      
      // Reset form and close modal
      setFormData({
        name: "",
        description: "",
        website_url: "",
        industry: "",
        scan_frequency_minutes: 60
      })
      setSelectedPlatforms(["youtube"])
      setSocialHandles({})
      onClose()
      
      // Notify parent component
      onCompetitorAdded()
      
    } catch (error) {
      console.error("Error creating competitor:", error)
      
      let errorMessage = "Failed to create competitor. Please try again.";
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

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Add New Competitor</DialogTitle>
          <DialogDescription>
            Add a new competitor to monitor their activities across selected platforms.
          </DialogDescription>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Basic Information</h3>
            
            <div className="space-y-2">
              <Label htmlFor="name">Competitor Name *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => handleInputChange("name", e.target.value)}
                placeholder="Enter competitor name"
                required
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => handleInputChange("description", e.target.value)}
                placeholder="Brief description of the competitor"
                rows={3}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="website_url">Website URL</Label>
              <Input
                id="website_url"
                type="url"
                value={formData.website_url}
                onChange={(e) => handleInputChange("website_url", e.target.value)}
                placeholder="https://example.com"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="industry">Industry</Label>
              <Input
                id="industry"
                value={formData.industry}
                onChange={(e) => handleInputChange("industry", e.target.value)}
                placeholder="e.g., Fashion, Technology, Food"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="scan_frequency">Scan Frequency</Label>
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
            </div>
          </div>
          
          {/* Platform Selection */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Platforms to Monitor</h3>
            <p className="text-sm text-muted-foreground">
              Select the platforms you want to monitor for this competitor
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {AVAILABLE_PLATFORMS.map((platform) => (
                <div key={platform.id} className="flex items-start space-x-3 p-3 border rounded-lg">
                  <Checkbox
                    id={platform.id}
                    checked={selectedPlatforms.includes(platform.id)}
                    onCheckedChange={(checked) => handlePlatformToggle(platform.id, checked as boolean)}
                  />
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
                        <Input
                          placeholder={`${platform.name} handle or username`}
                          value={socialHandles[platform.id] || ""}
                          onChange={(e) => handleSocialHandleChange(platform.id, e.target.value)}
                          className="text-sm"
                        />
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          {/* Form Actions */}
          <div className="flex justify-end space-x-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? "Adding..." : "Add Competitor"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}
