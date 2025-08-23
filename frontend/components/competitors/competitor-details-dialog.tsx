"use client"

import { useState, useEffect } from "react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Edit3, Save, X, Trash2, Loader2 } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { competitorAPI } from "@/lib/api-client"
import { Competitor, CompetitorUpdate } from "@/lib/types"
import { useUser } from "@clerk/nextjs"

interface CompetitorDetailsDialogProps {
  competitor: Competitor
  onCompetitorUpdated: () => void
  onCompetitorDeleted: () => void
  trigger?: React.ReactNode
}

export function CompetitorDetailsDialog({ competitor, onCompetitorUpdated, onCompetitorDeleted, trigger }: CompetitorDetailsDialogProps) {
  const [open, setOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [formData, setFormData] = useState<CompetitorUpdate>({
    name: competitor.name,
    description: competitor.description || "",
    website_url: competitor.website_url || "",
    industry: competitor.industry || ""
  })
  const { toast } = useToast()
  const { user } = useUser()

  // Reset form data when competitor changes
  useEffect(() => {
    setFormData({
      name: competitor.name,
      description: competitor.description || "",
      website_url: competitor.website_url || "",
      industry: competitor.industry || ""
    })
  }, [competitor])

  const handleInputChange = (field: keyof CompetitorUpdate, value: string | number) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
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
        industry: formData.industry?.trim() || undefined
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
      industry: competitor.industry || ""
    })
    setIsEditing(false)
  }

  const handleDelete = async () => {
    if (!user) {
      toast({
        title: "Error",
        description: "User not authenticated. Please log in again.",
        variant: "destructive"
      })
      return
    }

    // Show confirmation dialog
    setShowDeleteConfirm(true)
  }

  const confirmDelete = async () => {
    if (!user) return

    setIsLoading(true)
    try {
      await competitorAPI.deleteCompetitor(competitor.id, user.id)
      
      toast({
        title: "Success",
        description: `Competitor "${competitor.name}" deleted successfully!`
      })
      
      setOpen(false)
      setShowDeleteConfirm(false)
      onCompetitorDeleted()
      
    } catch (error) {
      console.error("Error deleting competitor:", error)
      
      let errorMessage = "Failed to delete competitor. Please try again.";
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
                {isEditing ? "Edit competitor information" : "View and manage competitor details"}
              </DialogDescription>
            </div>
            <div className="flex items-center gap-2">
              {!isEditing ? (
                <>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setIsEditing(true)}
                  >
                    <Edit3 className="mr-2 h-4 w-4" />
                    Edit
                  </Button>
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={handleDelete}
                    disabled={isLoading}
                  >
                    <Trash2 className="mr-2 h-4 w-4" />
                    Delete
                  </Button>
                </>
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
              <div className="p-3 bg-muted rounded-md">
                <span>Every 24 hours (1440 minutes)</span>
                <div className="text-xs text-muted-foreground mt-1">
                  Scan frequency is fixed at 24 hours for optimal performance
                </div>
              </div>
            </div>
          </div>
          
          {/* Monitoring Coverage */}
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

       {/* Delete Confirmation Dialog */}
       <Dialog open={showDeleteConfirm} onOpenChange={setShowDeleteConfirm}>
         <DialogContent className="max-w-md">
           <DialogHeader>
             <DialogTitle className="flex items-center gap-2 text-destructive">
               <Trash2 className="h-5 w-5" />
               Delete Competitor
             </DialogTitle>
             <DialogDescription>
               Are you sure you want to delete <strong>"{competitor.name}"</strong>? 
               This action cannot be undone and will remove all monitoring data for this competitor.
             </DialogDescription>
           </DialogHeader>
           <div className="flex items-center justify-end gap-3 pt-4">
             <Button
               variant="outline"
               onClick={() => setShowDeleteConfirm(false)}
               disabled={isLoading}
             >
               Cancel
             </Button>
             <Button
               variant="destructive"
               onClick={confirmDelete}
               disabled={isLoading}
             >
               {isLoading ? (
                 <>
                   <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                   Deleting...
                 </>
               ) : (
                 <>
                   <Trash2 className="mr-2 h-4 w-4" />
                   Delete
                 </>
               )}
             </Button>
           </div>
         </DialogContent>
       </Dialog>
     </Dialog>
   )
 }
