"use client"

import { useState } from "react"
import { Progress } from "@/components/ui/progress"
import { Brain } from "lucide-react"
import { WelcomeStep } from "./steps/welcome-step"
import { IndustryStep } from "./steps/industry-step"
import { GoalsStep } from "./steps/goals-step"
import { CompetitorStep } from "./steps/competitor-step"
import { ConnectionsStep } from "./steps/connections-step"
import { CompletionStep } from "./steps/completion-step"
import { ThemeToggle } from "@/components/theme-toggle"

export interface OnboardingData {
  industry: string
  companySize: string
  goals: string[]
  competitors: Array<{
    name: string
    website: string
    platforms: string[]
  }>
  connectedAccounts: string[]
  budget: string
}

const steps = [
  { id: 1, title: "Welcome", description: "Let's get started" },
  { id: 2, title: "Business", description: "Tell us about your company" },
  { id: 3, title: "Goals", description: "What do you want to achieve?" },
  { id: 4, title: "Competitors", description: "Who are you competing against?" },
  { id: 5, title: "Connections", description: "Connect your accounts" },
  { id: 6, title: "Complete", description: "AI analysis starting!" },
]

export function OnboardingWizard() {
  const [currentStep, setCurrentStep] = useState(1)
  const [data, setData] = useState<OnboardingData>({
    industry: "",
    companySize: "",
    goals: [],
    competitors: [],
    connectedAccounts: [],
    budget: "",
  })

  const updateData = (updates: Partial<OnboardingData>) => {
    setData((prev) => ({ ...prev, ...updates }))
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
        return <ConnectionsStep data={data} updateData={updateData} onNext={nextStep} onPrev={prevStep} />
      case 6:
        return <CompletionStep data={data} />
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
            <h1 className="text-3xl font-bold">CompetitorAI Pro</h1>
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
