"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { useApiClient } from "@/lib/api-client"
import { Loader2, Plus } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

interface AddCampaignModalProps {
  isOpen: boolean
  onClose: () => void
  onCampaignCreated?: () => void
}

export function AddCampaignModal({ isOpen, onClose, onCampaignCreated }: AddCampaignModalProps) {
  const [formData, setFormData] = useState({
    name: '',
    budget: '',
    ongoing: 'No' as 'Yes' | 'No'
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { apiClient, userId } = useApiClient()
  const { toast } = useToast()

  const resetForm = () => {
    setFormData({
      name: '',
      budget: '',
      ongoing: 'No'
    })
  }

  const handleClose = () => {
    resetForm()
    onClose()
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.name.trim()) {
      toast({
        title: "Error",
        description: "Campaign name is required",
        variant: "destructive",
      })
      return
    }

    const budget = parseFloat(formData.budget)
    if (!budget || budget <= 0) {
      toast({
        title: "Error",
        description: "Budget must be a positive number",
        variant: "destructive",
      })
      return
    }

    setIsSubmitting(true)
    
    try {
      await apiClient.createCampaign(userId, {
        name: formData.name.trim(),
        budget: budget,
        ongoing: formData.ongoing
      })

      toast({
        title: "Success",
        description: `Campaign "${formData.name}" created successfully!`,
      })

      resetForm()
      onClose()
      onCampaignCreated?.()
    } catch (error: any) {
      console.error('Failed to create campaign:', error)
      toast({
        title: "Error",
        description: error.message || "Failed to create campaign. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Plus className="h-5 w-5" />
            Add New Campaign
          </DialogTitle>
          <DialogDescription>
            Create a new campaign to start tracking its performance and optimize it.
          </DialogDescription>
        </DialogHeader>
        
        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="name" className="text-right">
                Name
              </Label>
              <Input
                id="name"
                placeholder="Enter campaign name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="col-span-3"
                required
                disabled={isSubmitting}
              />
            </div>
            
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="budget" className="text-right">
                Budget
              </Label>
              <Input
                id="budget"
                type="number"
                step="0.01"
                min="0.01"
                placeholder="0.00"
                value={formData.budget}
                onChange={(e) => setFormData({ ...formData, budget: e.target.value })}
                className="col-span-3"
                required
                disabled={isSubmitting}
              />
            </div>
            
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="ongoing" className="text-right">
                Status
              </Label>
              <Select
                value={formData.ongoing}
                onValueChange={(value: 'Yes' | 'No') => setFormData({ ...formData, ongoing: value })}
                disabled={isSubmitting}
              >
                <SelectTrigger className="col-span-3">
                  <SelectValue placeholder="Select status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Yes">Ongoing</SelectItem>
                  <SelectItem value="No">Paused</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating...
                </>
              ) : (
                <>
                  <Plus className="mr-2 h-4 w-4" />
                  Create Campaign
                </>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
