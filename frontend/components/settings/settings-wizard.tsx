"use client"

import { useState, useEffect } from "react"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Settings, ArrowLeft, Save, Edit, X, Check } from "lucide-react"
import { IndustryStep } from "@/components/onboarding/steps/industry-step"
import { GoalsStep } from "@/components/onboarding/steps/goals-step"
import { CompetitorStep } from "@/components/onboarding/steps/competitor-step"
import { useRouter } from "next/navigation"
import { OnboardingData } from "@/components/onboarding/onboarding-wizard"
import { useUser } from "@clerk/nextjs"
import { ApiClient } from "@/lib/api-client"
import { useToast } from "@/hooks/use-toast"

const steps = [
  { id: 1, title: "Business", description: "Update your company information" },
  { id: 2, title: "Goals", description: "Adjust your marketing goals" },
  { id: 3, title: "Competitors", description: "Manage your competitor list" },
]

export function SettingsWizard() {
  const router = useRouter()
  const { user } = useUser()
  const { toast } = useToast()
  const [currentStep, setCurrentStep] = useState(1)
  const [hasChanges, setHasChanges] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [data, setData] = useState<OnboardingData>({
    industry: "",
    companySize: "",
    goals: [],
    competitors: [],
    connectedAccounts: [],
    budget: "",
  })
  const [initialData, setInitialData] = useState<OnboardingData | null>(null)
  const [editingSections, setEditingSections] = useState<Set<number>>(new Set())
  const [sectionChanges, setSectionChanges] = useState<Set<number>>(new Set())

  // Simple URL validator for http/https only
  const isValidHttpUrl = (value?: string) => {
    if (!value || typeof value !== "string") return false
    try {
      const url = new URL(value)
      return url.protocol === "http:" || url.protocol === "https:"
    } catch {
      return false
    }
  }

  // Load existing settings
  useEffect(() => {
    const loadSettings = async () => {
      if (!user?.id) return
      
      try {
        setIsLoading(true)
        const apiClient = new ApiClient()
        
        // Load user preferences and competitors in parallel
        const clerkId = user.externalId || user.id
        const [preferences, competitors] = await Promise.all([
          apiClient.getUserPreferences(clerkId).catch(() => null),
          apiClient.getUserCompetitors(clerkId).catch(() => [])
        ])
        
        // Transform database data to match OnboardingData interface
        const transformCompanySizeFromDB = (dbSize: string) => {
          const sizeMapping = {
            "1-10": "solo",
            "11-50": "medium", 
            "51-200": "large",
            "201-500": "large",
            "500+": "enterprise"
          }
          return sizeMapping[dbSize as keyof typeof sizeMapping] || "medium"
        }
        
        const transformBudgetFromDB = (dbBudget: string) => {
          const budgetMapping = {
            "$0 - $1,000": "0-1000",
            "$1,000 - $5,000": "1000-5000",
            "$5,000 - $10,000": "5000-10000",
            "$10,000 - $25,000": "10000-25000",
            "$25,000+": "25000+"
          }
          return budgetMapping[dbBudget as keyof typeof budgetMapping] || "5000-10000"
        }
        
        const transformedData: OnboardingData = {
          industry: (preferences as any)?.industry || "Fashion & Apparel",
          companySize: transformCompanySizeFromDB((preferences as any)?.company_size) || "medium",
          goals: (preferences as any)?.marketing_goals || ["Brand Awareness", "Lead Generation"],
          competitors: (competitors as any[]).map((comp: any) => ({
            id: comp.id, // Include the database ID for updates
            name: comp.name || comp.competitor_name,
            website: comp.website_url || "",
            description: comp.description || "",
            platforms: comp.platforms || comp.active_platforms || []
          })),
          connectedAccounts: [], // Keep existing connected accounts
          budget: transformBudgetFromDB((preferences as any)?.monthly_budget) || "5000-10000"
        }
        
        setData(transformedData)
        setInitialData(transformedData)
      } catch (error) {
        console.error('Failed to load user settings:', error)
        toast({
          title: "Load Failed",
          description: "Failed to load your settings. Using default values.",
          variant: "destructive",
        })
      } finally {
        setIsLoading(false)
      }
    }
    
    loadSettings()
  }, [user?.id])

  const updateData = (updates: Partial<OnboardingData>) => {
    setData((prev) => ({ ...prev, ...updates }))
    setHasChanges(true)
  }

  const nextStep = () => {
    if (currentStep < steps.length) {
      setCurrentStep(currentStep + 1)
    }
  }

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  // Toggle edit mode for a specific section
  const toggleEditSection = (stepId: number) => {
    const newEditingSections = new Set(editingSections)
    if (newEditingSections.has(stepId)) {
      newEditingSections.delete(stepId)
      // Cancel changes for this section
      if (initialData) {
        setData(prev => ({
          ...prev,
          ...(stepId === 1 ? {
            industry: initialData.industry,
            companySize: initialData.companySize
          } : stepId === 2 ? {
            goals: initialData.goals,
            budget: initialData.budget
          } : stepId === 3 ? {
            competitors: initialData.competitors
          } : {})
        }))
      }
    } else {
      newEditingSections.add(stepId)
    }
    setEditingSections(newEditingSections)
    
    // Clear section changes when entering edit mode
    const newSectionChanges = new Set(sectionChanges)
    newSectionChanges.delete(stepId)
    setSectionChanges(newSectionChanges)
  }

  // Save changes for a specific section
  const saveSection = async (stepId: number) => {
    if (!user?.id) {
      toast({
        title: "Error",
        description: "User not authenticated. Please log in again.",
        variant: "destructive",
      })
      return
    }

    try {
      const apiClient = new ApiClient()
      const clerkId = user.externalId || user.id
      
      if (stepId === 1) {
        // Save business information
        await apiClient.saveUserPreferences(clerkId, {
          industry: data.industry,
          companySize: data.companySize,
          goals: data.goals,
          budget: data.budget
        })
      } else if (stepId === 2) {
        // Save goals and budget
        await apiClient.saveUserPreferences(clerkId, {
          industry: data.industry,
          companySize: data.companySize,
          goals: data.goals,
          budget: data.budget
        })
      } else if (stepId === 3) {
        // Handle competitors - this is more complex
        // First, get current competitors from database to compare
        const currentCompetitors = await apiClient.getUserCompetitors(clerkId)
        const currentIds = new Set((currentCompetitors as any[]).map((c: any) => c.id).filter(Boolean))
        
        // Determine which competitors to delete, update, or create
        for (const competitor of data.competitors) {
          if (competitor.website && !isValidHttpUrl(competitor.website)) {
            toast({
              title: "Invalid URL",
              description: `Please use a valid URL for ${competitor.name}. Use http(s)://...`,
              variant: "destructive",
            })
            return
          }
          
          if (competitor.id && currentIds.has(competitor.id)) {
            // Update existing competitor
            await apiClient.updateCompetitor(clerkId, competitor.id, {
              name: competitor.name,
              website: competitor.website,
              description: competitor.description,
              platforms: competitor.platforms
            })
          } else if (!competitor.id) {
            // Create new competitor
            await apiClient.saveCompetitor(clerkId, {
              name: competitor.name,
              website: competitor.website,
              description: competitor.description,
              platforms: competitor.platforms
            })
          }
        }
        
        // Delete competitors that are no longer in the list
        for (const currentId of currentIds) {
          if (!data.competitors.some(c => c.id === currentId)) {
            await apiClient.deleteCompetitor(currentId, clerkId)
          }
        }
        
        // Refresh competitors from database to get updated IDs
        const refreshed = await apiClient.getUserCompetitors(clerkId)
        const refreshedCompetitors = (refreshed as any[]).map((comp: any) => ({
          id: comp.id,
          name: comp.name || comp.competitor_name,
          website: comp.website_url || "",
          description: comp.description || "",
          platforms: comp.platforms || comp.active_platforms || []
        }))
        
        setData(prev => ({ ...prev, competitors: refreshedCompetitors }))
        if (initialData) {
          setInitialData(prev => prev ? { ...prev, competitors: refreshedCompetitors } : null)
        }
      }

      // Exit edit mode and mark section as saved
      const newEditingSections = new Set(editingSections)
      newEditingSections.delete(stepId)
      setEditingSections(newEditingSections)
      
      // Update initial data to reflect saved state
      if (initialData) {
        setInitialData(prev => prev ? { ...prev, ...data } : null)
      }
      
      // Check if there are any remaining changes
      const hasRemainingChanges = JSON.stringify(data) !== JSON.stringify(initialData)
      setHasChanges(hasRemainingChanges)
      
      toast({
        title: "Section Saved!",
        description: "Your changes have been saved successfully.",
      })
    } catch (error) {
      console.error('Failed to save section:', error)
      toast({
        title: "Save Failed",
        description: "Failed to save your changes. Please try again.",
        variant: "destructive",
      })
    }
  }

  const handleBackToDashboard = () => {
    if (hasChanges) {
      const confirmLeave = window.confirm("You have unsaved changes. Are you sure you want to leave?")
      if (!confirmLeave) return
    }
    router.push("/dashboard")
  }

  const progress = ((currentStep - 1) / (steps.length - 1)) * 100

  const renderStep = () => {
    const isEditing = editingSections.has(currentStep)
    
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">Business Information</h3>
              <Button
                variant={isEditing ? "outline" : "default"}
                size="sm"
                onClick={() => toggleEditSection(1)}
              >
                {isEditing ? (
                  <>
                    <X className="h-4 w-4 mr-2" />
                    Cancel
                  </>
                ) : (
                  <>
                    <Edit className="h-4 w-4 mr-2" />
                    Edit
                  </>
                )}
              </Button>
            </div>
            
            <IndustryStep 
              data={data} 
              updateData={updateData} 
              onNext={nextStep} 
              onPrev={prevStep} 
              isFromSettings={true}
              readOnly={!isEditing}
            />
            
            {isEditing && (
              <div className="flex justify-end pt-4">
                <Button onClick={() => saveSection(1)}>
                  <Save className="h-4 w-4 mr-2" />
                  Save Changes
                </Button>
              </div>
            )}
          </div>
        )
      case 2:
        return (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">Goals & Budget</h3>
              <Button
                variant={isEditing ? "outline" : "default"}
                size="sm"
                onClick={() => toggleEditSection(2)}
              >
                {isEditing ? (
                  <>
                    <X className="h-4 w-4 mr-2" />
                    Cancel
                  </>
                ) : (
                  <>
                    <Edit className="h-4 w-4 mr-2" />
                    Edit
                  </>
                )}
              </Button>
            </div>
            
            <GoalsStep 
              data={data} 
              updateData={updateData} 
              onNext={nextStep} 
              onPrev={prevStep} 
              isFromSettings={true}
              readOnly={!isEditing}
            />
            
            {isEditing && (
              <div className="flex justify-end pt-4">
                <Button onClick={() => saveSection(2)}>
                  <Save className="h-4 w-4 mr-2" />
                  Save Changes
                </Button>
              </div>
            )}
          </div>
        )
      case 3:
        return (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">Competitor Management</h3>
              <Button
                variant={isEditing ? "outline" : "default"}
                size="sm"
                onClick={() => toggleEditSection(3)}
              >
                {isEditing ? (
                  <>
                    <X className="h-4 w-4 mr-2" />
                    Cancel
                  </>
                ) : (
                  <>
                    <Edit className="h-4 w-4 mr-2" />
                    Edit
                  </>
                )}
              </Button>
            </div>
            
            <CompetitorStep 
              data={data} 
              updateData={updateData} 
              onNext={nextStep} 
              onPrev={prevStep} 
              isFromSettings={true}
              readOnly={!isEditing}
            />
            
            {isEditing && (
              <div className="flex justify-end pt-4">
                <Button onClick={() => saveSection(3)}>
                  <Save className="h-4 w-4 mr-2" />
                  Save Changes
                </Button>
              </div>
            )}
          </div>
        )
      default:
        return null
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-blue-600 rounded-lg">
                <Settings className="h-6 w-6 text-white" />
              </div>
              <h1 className="text-3xl font-bold tracking-tight">Account Settings</h1>
            </div>
            <p className="text-muted-foreground">Update your onboarding preferences and configuration</p>
          </div>
        </div>
      </div>

      {/* Progress */}
      <Card>
        <CardHeader>
          <CardTitle>Settings Navigation</CardTitle>
          <CardDescription>Navigate through different sections to update your preferences</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              {steps.map((step, index) => (
                <div key={step.id} className="flex items-center">
                  <button
                    onClick={() => setCurrentStep(step.id)}
                    className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-colors ${
                      currentStep >= step.id
                        ? "bg-blue-600 text-white hover:bg-blue-700"
                        : "bg-gray-200 text-gray-600 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-400 dark:hover:bg-gray-600"
                    }`}
                  >
                    {step.id}
                  </button>
                  {index < steps.length - 1 && (
                    <div
                      className={`w-12 h-0.5 mx-2 ${
                        currentStep > step.id ? "bg-blue-600" : "bg-gray-200 dark:bg-gray-700"
                      }`}
                    />
                  )}
                </div>
              ))}
            </div>
            <Progress value={progress} className="h-2" />
            <div className="flex justify-between text-sm text-muted-foreground">
              <span>{steps[currentStep - 1]?.title}</span>
              <span>
                {currentStep} of {steps.length}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Step Content */}
      <Card>
        <CardContent className="pt-6">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-muted-foreground">Loading your settings...</p>
              </div>
            </div>
          ) : (
            renderStep()
          )}
        </CardContent>
      </Card>

      {/* Save Notice */}
      {hasChanges && (
        <Card className="border-orange-200 bg-orange-50 dark:border-orange-800 dark:bg-orange-950/20">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium text-orange-900 dark:text-orange-100">Unsaved Changes</h3>
                <p className="text-sm text-orange-700 dark:text-orange-300">
                  You have unsaved changes in some sections. Click the Edit button for each section to make changes, then save them individually.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
