"use client"

import { useState, useEffect } from "react"
import { useSearchParams } from "next/navigation"
import { Progress } from "@/components/ui/progress"
import { Brain } from "lucide-react"
import { WelcomeStep } from "./steps/welcome-step"
import { IndustryStep } from "./steps/industry-step"
import { GoalsStep } from "./steps/goals-step"
import { CompetitorStep } from "./steps/competitor-step"
import { ConnectionsStep } from "./steps/connections-step"
import { CompletionStep } from "./steps/completion-step"
import { ThemeToggle } from "@/components/optimization/theme-toggle"

export interface OnboardingData {
  industry: string
  companySize: string
  goals: string[]
  competitors: Array<{
    id?: string // Optional ID for saved competitors
    name: string
    website: string
    description?: string
    platforms: string[]
  }>
  connectedAccounts: Array<{
    platform: string
    username: string
    displayName?: string
    isConnected: boolean
    permissions: string[]
    connectedAt?: Date
  }>
  budget: string
}

const steps = [
  { id: 1, title: "Welcome", description: "Let's get started" },
  { id: 2, title: "Business", description: "Tell us about your company" },
  { id: 3, title: "Goals", description: "What do you want to achieve?" },
  { id: 4, title: "Competitors", description: "Who are you competing against?" },
  { id: 5, title: "Connections", description: "Connect your social media accounts" },
  { id: 6, title: "Complete", description: "Setup complete!" },
]

const ONBOARDING_STEP_KEY = 'onboarding_current_step'
const ONBOARDING_DATA_KEY = 'onboarding_data'

export function OnboardingWizard() {
  const searchParams = useSearchParams()
  const [currentStep, setCurrentStep] = useState(1)
  const [data, setData] = useState<OnboardingData>({
    industry: "",
    companySize: "",
    goals: [],
    competitors: [],
    connectedAccounts: [],
    budget: "",
  })

  // Restore current step and data from localStorage on component mount
  useEffect(() => {
    // Check URL parameters first (from YouTube callback)
    const urlStep = searchParams.get('step')
    const savedStep = localStorage.getItem(ONBOARDING_STEP_KEY)
    const returnStep = sessionStorage.getItem('youtube_return_step')
    const savedData = localStorage.getItem(ONBOARDING_DATA_KEY)

    // Load saved data if it exists
    if (savedData) {
      try {
        const parsedData = JSON.parse(savedData)
        setData(parsedData)
      } catch (error) {
        console.error('Failed to parse saved onboarding data:', error)
      }
    }

    // Priority: URL step > Session storage > Local storage
    if (urlStep) {
      const step = parseInt(urlStep, 10)
      if (step >= 1 && step <= steps.length) {
        setCurrentStep(step)
        // Clean up session storage since we got it from URL
        sessionStorage.removeItem('youtube_return_step')
        return
      }
    }

    if (returnStep) {
      const step = parseInt(returnStep, 10)
      if (step >= 1 && step <= steps.length) {
        setCurrentStep(step)
      }
      // Clear the return step from session storage
      sessionStorage.removeItem('youtube_return_step')
      return
    }

    // Otherwise use saved step
    if (savedStep) {
      const step = parseInt(savedStep, 10)
      if (step >= 1 && step <= steps.length) {
        // Since user preferences are now saved before reaching social media step,
        // we don't need to validate completion here
        setCurrentStep(step)
      }
    }
  }, [searchParams])

  // Save current step to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem(ONBOARDING_STEP_KEY, currentStep.toString())
  }, [currentStep])

  // Save onboarding data to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem(ONBOARDING_DATA_KEY, JSON.stringify(data))
  }, [data])

  const updateData = (updates: Partial<OnboardingData>) => {
    setData((prev) => ({ ...prev, ...updates }))
  }

  const nextStep = () => {
    if (currentStep < steps.length) {
      // Validate current step before allowing next
      let canProceed = true
      
      switch (currentStep) {
        case 1: // Welcome step - always can proceed
          canProceed = true
          break
        case 2: // Industry step
          canProceed = Boolean(data.industry && data.companySize)
          break
        case 3: // Goals step
          canProceed = Boolean(data.goals.length > 0 && data.budget)
          break
        case 4: // Competitors step
          canProceed = Boolean(data.competitors.length > 0)
          break
        case 5: // Connections step
          canProceed = Boolean(data.connectedAccounts.length > 0)
          break
        case 6: // Completion step - can't go next
          canProceed = false
          break
      }
      
      if (canProceed) {
        setCurrentStep(currentStep + 1)
      }
    }
  }

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }
  
  const goToStep = (step: number) => {
    if (step >= 1 && step <= steps.length) {
      setCurrentStep(step)
    }
  }

  const progress = ((currentStep - 1) / (steps.length - 1)) * 100

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return <WelcomeStep onNext={nextStep} />
      case 2:
        return <IndustryStep data={data} updateData={updateData} onNext={nextStep} onPrev={prevStep} />
      case 3:
        return <GoalsStep data={data} updateData={updateData} onNext={nextStep} onPrev={prevStep} />
      case 4:
        return <CompetitorStep data={data} updateData={updateData} onNext={nextStep} onPrev={prevStep} />
      case 5:
        return <ConnectionsStep data={data} updateData={updateData} onNext={nextStep} onPrev={prevStep} currentStep={currentStep} />
      case 6:
        return <CompletionStep data={data} goToStep={goToStep} />
      default:
        return <WelcomeStep onNext={nextStep} />
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="absolute top-6 right-6">
        <ThemeToggle />
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="p-3 bg-blue-600 rounded-xl">
              <Brain className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-3xl font-bold">BOSSolution</h1>
          </div>
          <p className="text-muted-foreground">AI-powered competitive intelligence for your marketing</p>
        </div>

        {/* Progress */}
        <div className="max-w-2xl mx-auto mb-8">
          <div className="flex items-center justify-between mb-4">
            {steps.map((step, index) => (
              <div key={step.id} className="flex items-center">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                    currentStep >= step.id
                      ? "bg-blue-600 text-white"
                      : "bg-gray-200 text-gray-600 dark:bg-gray-700 dark:text-gray-400"
                  }`}
                >
                  {step.id}
                </div>
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
          <div className="flex justify-between mt-2 text-sm text-muted-foreground">
            <span>{steps[currentStep - 1]?.title}</span>
            <span>
              {currentStep} of {steps.length}
            </span>
          </div>
        </div>

        {/* Step Content */}
        <div className="max-w-2xl mx-auto">{renderStep()}</div>
      </div>
    </div>
  )
}
