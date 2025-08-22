"use client"

import { useState, useEffect } from "react"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Settings, ArrowLeft, Save } from "lucide-react"
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
  const [initialCompetitorIds, setInitialCompetitorIds] = useState<string[]>([])

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

  // Load existing settings and handle YouTube OAuth return
  useEffect(() => {
    // Check if returning from YouTube OAuth
    const returnStep = sessionStorage.getItem('youtube_return_step')
    if (returnStep) {
      const step = parseInt(returnStep, 10)
      if (step >= 1 && step <= steps.length) {
        setCurrentStep(step)
      }
      // Clear the return step from session storage
      sessionStorage.removeItem('youtube_return_step')
    }
    
    // Load real settings from database
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
          connectedAccounts: data.connectedAccounts, // Keep existing connected accounts
          budget: transformBudgetFromDB((preferences as any)?.monthly_budget) || "5000-10000"
        }
        
        setData(transformedData)
        setInitialCompetitorIds((competitors as any[]).map((c: any) => c.id).filter(Boolean))
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

  const handleSave = async () => {
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
      
      // Save user preferences to database
      await apiClient.saveUserPreferences(clerkId, {
        industry: data.industry,
        companySize: data.companySize,
        goals: data.goals,
        budget: data.budget
      })
      
      // Determine deletions (IDs that were initially loaded but are no longer present)
      const currentIds = data.competitors.map((c) => c.id).filter(Boolean) as string[]
      const idsToDelete = initialCompetitorIds.filter((id) => !currentIds.includes(id))
      for (const id of idsToDelete) {
        try {
          await apiClient.deleteCompetitor(clerkId, id)
        } catch (e) {
          console.warn('Failed to delete competitor', id, e)
        }
      }

      // Save competitors to database (one by one)
      for (const competitor of data.competitors) {
        // Frontend validation for website URL
        if (competitor.website && !isValidHttpUrl(competitor.website)) {
          console.warn("Please add valid URL", { name: competitor.name, website: competitor.website })
          toast({
            title: "Please add valid URL",
            description: `Invalid website for ${competitor.name}. Use http(s)://...`,
            variant: "destructive",
          })
          return
        }
        if (competitor.id) {
          // Update existing competitor
          await apiClient.updateCompetitor(clerkId, competitor.id, {
            name: competitor.name,
            website: competitor.website,
            description: competitor.description,
            platforms: competitor.platforms
          })
        } else {
          // Create new competitor
          await apiClient.saveCompetitor(clerkId, {
            name: competitor.name,
            website: competitor.website,
            description: competitor.description,
            platforms: competitor.platforms
          })
        }
      }
      // Refresh from database so UI reflects DB and captures new IDs
      try {
        const refreshed = await apiClient.getUserCompetitors(clerkId)
        const refreshedMapped: OnboardingData = {
          industry: data.industry,
          companySize: data.companySize,
          goals: data.goals,
          competitors: (refreshed as any[]).map((comp: any) => ({
            id: comp.id,
            name: comp.name || comp.competitor_name,
            website: comp.website_url || "",
            description: comp.description || "",
            platforms: comp.platforms || comp.active_platforms || []
          })),
          connectedAccounts: data.connectedAccounts,
          budget: data.budget,
        }
        setData(refreshedMapped)
        setInitialCompetitorIds((refreshed as any[]).map((c: any) => c.id).filter(Boolean))
      } catch (e) {
        console.warn('Failed to refresh competitors after save', e)
      }

      setHasChanges(false)
      toast({
        title: "Settings Saved!",
        description: "Your preferences have been updated successfully.",
      })
    } catch (error) {
      console.error('Failed to save settings:', error)
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
    switch (currentStep) {
      case 1:
        return <IndustryStep data={data} updateData={updateData} onNext={nextStep} onPrev={prevStep} isFromSettings={true} />
      case 2:
        return <GoalsStep data={data} updateData={updateData} onNext={nextStep} onPrev={prevStep} isFromSettings={true} />
      case 3:
        return <CompetitorStep data={data} updateData={updateData} onNext={nextStep} onPrev={prevStep} isFromSettings={true} />
      default:
        return <IndustryStep data={data} updateData={updateData} onNext={nextStep} onPrev={prevStep} isFromSettings={true} />
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            variant="outline"
            size="sm"
            onClick={handleBackToDashboard}
            className="flex items-center gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Dashboard
          </Button>
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
        <Button
          onClick={handleSave}
          disabled={!hasChanges}
          className="flex items-center gap-2"
        >
          <Save className="h-4 w-4" />
          Save Changes
        </Button>
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
                  You have unsaved changes. Don't forget to save your updates.
                </p>
              </div>
              <Button
                onClick={handleSave}
                className="bg-orange-600 hover:bg-orange-700 text-white"
              >
                Save Now
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
