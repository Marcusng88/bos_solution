"use client"

import { useState, useEffect } from "react"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Settings, ArrowLeft, Save } from "lucide-react"
import { IndustryStep } from "@/components/onboarding/steps/industry-step"
import { GoalsStep } from "@/components/onboarding/steps/goals-step"
import { CompetitorStep } from "@/components/onboarding/steps/competitor-step"
import { ConnectionsStep } from "@/components/onboarding/steps/connections-step"
import { useRouter } from "next/navigation"
import { OnboardingData } from "@/components/onboarding/onboarding-wizard"

const steps = [
  { id: 1, title: "Business", description: "Update your company information" },
  { id: 2, title: "Goals", description: "Adjust your marketing goals" },
  { id: 3, title: "Competitors", description: "Manage your competitor list" },
  { id: 4, title: "Connections", description: "Update connected accounts" },
]

export function SettingsWizard() {
  const router = useRouter()
  const [currentStep, setCurrentStep] = useState(1)
  const [hasChanges, setHasChanges] = useState(false)
  const [data, setData] = useState<OnboardingData>({
    industry: "",
    companySize: "",
    goals: [],
    competitors: [],
    connectedAccounts: [],
    budget: "",
  })

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
    
    // Simulate loading existing settings
    const loadSettings = () => {
      // In a real app, you'd fetch this from your backend
      const existingSettings = {
        industry: "Fashion & Apparel",
        companySize: "51-200",
        goals: ["Brand Awareness", "Lead Generation"],
        competitors: [
          {
            name: "Nike",
            website: "nike.com",
            platforms: ["instagram", "facebook", "youtube"]
          }
        ],
        connectedAccounts: ["youtube"],
        budget: "$5,000 - $10,000"
      }
      setData(existingSettings)
    }
    
    loadSettings()
  }, [])

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

  const handleSave = () => {
    // Here you would save the settings to your backend
    console.log("Saving settings:", data)
    setHasChanges(false)
    // Show a success message or redirect
    alert("Settings saved successfully!")
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
      case 4:
        return <ConnectionsStep 
          data={data} 
          updateData={updateData} 
          onNext={nextStep} 
          onPrev={prevStep} 
          isFromSettings={true}
          onSave={handleSave}
          currentStep={currentStep}
        />
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
          {renderStep()}
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
