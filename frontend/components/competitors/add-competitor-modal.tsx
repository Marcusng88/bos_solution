"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Plus } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { competitorAPI } from "@/lib/api-client"
import { CompetitorCreate } from "@/lib/types"
import { useUser } from "@clerk/nextjs"

interface AddCompetitorModalProps {
  onCompetitorAdded: () => void
  isOpen: boolean
  onClose: () => void
}

export function AddCompetitorModal({ onCompetitorAdded, isOpen, onClose }: AddCompetitorModalProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [formData, setFormData] = useState<CompetitorCreate>({
    name: "",
    description: "",
    website_url: "",
    industry: "",
    scan_frequency_minutes: 1440
  })
  const { toast } = useToast()
  const { user } = useUser()

  const handleInputChange = (field: keyof CompetitorCreate, value: string | number) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
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
        title: "Invalid Scan Frequency",
        description: "Scan frequency must be between 15 minutes and 24 hours.",
        variant: "destructive"
      })
      return
    }

    setIsLoading(true)
    try {
      const competitorData = {
        name: formData.name.trim(),
        description: formData.description?.trim() || undefined,
        website_url: formData.website_url?.trim() || undefined,
        industry: formData.industry?.trim() || undefined,
        scan_frequency_minutes: formData.scan_frequency_minutes || 1440
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
        scan_frequency_minutes: 1440
      })
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

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Add New Competitor</DialogTitle>
          <DialogDescription>
            Add a new competitor to monitor their activities across YouTube, web content, and website changes.
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
            
            {/* Hidden scan frequency - fixed at 24 hours */}
            <input 
              type="hidden" 
              name="scan_frequency_minutes" 
              value="1440" 
            />
            
            <div className="text-sm text-muted-foreground bg-muted p-3 rounded-lg">
              <strong>Note:</strong> Competitor scanning is automatically set to run every 24 hours for optimal performance and resource management.
            </div>
          </div>
          
          {/* Monitoring Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Monitoring Coverage</h3>
            <div className="text-sm text-muted-foreground bg-blue-50 p-4 rounded-lg border border-blue-200">
              <p className="font-medium mb-2">🎯 Automatic Monitoring Includes:</p>
              <ul className="space-y-1 ml-4">
                <li>• <strong>YouTube:</strong> Video content, channel activity, and engagement metrics</li>
                <li>• <strong>Web Content:</strong> Online mentions, news articles, and social media posts</li>
                <li>• <strong>Website Changes:</strong> Updates to competitor websites and landing pages</li>
              </ul>
              <p className="mt-2 text-xs">No platform selection needed - all three monitoring agents run automatically!</p>
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
