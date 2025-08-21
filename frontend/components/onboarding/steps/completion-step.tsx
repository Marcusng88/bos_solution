"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { CheckCircle, Sparkles, ArrowRight, Loader2 } from "lucide-react"
import type { OnboardingData } from "../onboarding-wizard"
import { useUser } from "@clerk/nextjs"
import { useRouter } from "next/navigation"
import { useToast } from "@/hooks/use-toast"
import { ApiClient } from "@/lib/api-client"

interface CompletionStepProps {
  data: OnboardingData
  goToStep: (step: number) => void
}

export function CompletionStep({ data, goToStep }: CompletionStepProps) {
  const { user } = useUser()
  const router = useRouter()
  const { toast } = useToast()
  const [isSaving, setIsSaving] = useState(false)
  
  // Check if required fields are missing and determine which step to go back to
  const getMissingFields = () => {
    const missing = []
    if (!data.industry || !data.companySize) missing.push('business')
    if (!data.goals?.length || !data.budget) missing.push('goals')
    if (!data.competitors?.length) missing.push('competitors')
    if (!data.connectedAccounts?.length) missing.push('connections')
    return missing
  }
  
  const getStepNumber = (stepName: string) => {
    const stepMap: Record<string, number> = {
      'business': 2,
      'goals': 3,
      'competitors': 4,
      'connections': 5
    }
    return stepMap[stepName] || 1
  }
  
  const goToIncompleteStep = () => {
    const missingFields = getMissingFields()
    if (missingFields.length > 0) {
      const stepToGo = getStepNumber(missingFields[0])
      goToStep(stepToGo)
    }
  }
  
  const handleGetStarted = async () => {
    console.log('🎯 Go to Dashboard button clicked')
    console.log('📊 Onboarding data:', data)
    console.log('👤 User:', user)

    // Validate required fields before save
    if (!data.budget || (data.goals?.length ?? 0) === 0 || !data.industry || !data.companySize) {
      console.error('❌ Validation failed - missing required fields:', {
        budget: data.budget,
        goalsCount: data.goals?.length ?? 0,
        industry: data.industry,
        companySize: data.companySize
      })
      toast({
        title: "Incomplete",
        description: "Please complete all steps (industry, company size, goals, and budget) before continuing.",
        variant: "destructive",
      })
      return
    }

    if (!user?.id) {
      console.error('❌ User not authenticated:', user)
      toast({
        title: "Error",
        description: "User not authenticated. Please log in again.",
        variant: "destructive",
      })
      return
    }

    console.log('✅ Validation passed, starting save process')
    setIsSaving(true)
    try {
      const apiClient = new ApiClient()
      console.log('🔗 API Client created')

      // First, sync user to ensure they exist in the users table
      console.log('👤 Syncing user to database...')
      await apiClient.syncUserFromClerk(user.id, {
        id: user.id,
        email_addresses: user.emailAddresses.map(email => ({
          id: email.id,
          email_address: email.emailAddress,
        })),
        first_name: user.firstName,
        last_name: user.lastName,
        image_url: user.imageUrl,
        primary_email_address_id: user.primaryEmailAddressId,
      })
      console.log('✅ User synced to database')

      // Save user preferences to database
      console.log('💾 Saving user preferences...')
      await apiClient.saveUserPreferences(user.id, {
        industry: data.industry,
        companySize: data.companySize,
        goals: data.goals,
        budget: data.budget
      })
      console.log('✅ User preferences saved')

      // Save competitors to database (one by one)
      console.log(`👥 Saving ${data.competitors.length} competitors...`)
      for (const competitor of data.competitors) {
        console.log('💾 Saving competitor:', competitor)
        await apiClient.saveCompetitor(user.id, {
          name: competitor.name,
          website: competitor.website,
          platforms: competitor.platforms
        })
      }
      console.log('✅ Competitors saved')

      // Update Clerk metadata
      console.log('🔐 Updating Clerk metadata...')
      await user?.update({ unsafeMetadata: { onboardingComplete: true } as any })
      console.log('✅ Clerk metadata updated')

      // Also update the database to mark onboarding as complete
      console.log('💾 Updating database onboarding status...')
      try {
        await apiClient.updateUserOnboardingStatus(user.id, true)
        console.log('✅ Database onboarding status updated')
      } catch (dbError) {
        console.warn('⚠️ Failed to update database onboarding status:', dbError)
        // Don't fail the whole process if this fails
      }

      // Show success message
      toast({
        title: "Onboarding Complete!",
        description: "Your preferences have been saved successfully.",
      })

      // Clear localStorage and redirect
      console.log('🧹 Clearing localStorage and redirecting...')
      if (typeof window !== "undefined") {
        localStorage.removeItem("onboarding_current_step")
        localStorage.removeItem("onboarding_data")
        sessionStorage.setItem("skipOnboardingGuard", "true")
        // Also set a more permanent flag
        localStorage.setItem("onboardingComplete", "true")
      }

      console.log('🚀 Redirecting to dashboard...')
      router.replace("/dashboard")
      console.log('✅ Redirect completed')

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error'
      const errorDetails = error instanceof Error ? {
        message: error.message,
        stack: error.stack,
        name: error.name
      } : { message: 'Unknown error', stack: undefined, name: 'Unknown' }

      console.error('❌ Failed to save onboarding data:', error)
      console.error('❌ Error details:', errorDetails)

      toast({
        title: "Save Failed",
        description: `Failed to save your preferences: ${errorMessage}. Please try again.`,
        variant: "destructive",
      })
    } finally {
      setIsSaving(false)
      console.log('🏁 Save process completed')
    }
  }

  // Check if all required fields are completed
  const missingFields = getMissingFields()
  const isComplete = missingFields.length === 0
  
  if (!isComplete) {
    return (
      <Card>
        <CardHeader className="text-center">
          <div className="mx-auto w-16 h-16 bg-yellow-100 dark:bg-yellow-900/20 rounded-full flex items-center justify-center mb-4">
            <div className="h-8 w-8 text-yellow-600 text-2xl font-bold">!</div>
          </div>
          <CardTitle className="text-2xl">Almost there!</CardTitle>
          <CardDescription>
            Please complete the following steps before continuing:
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-4">
            {!data.industry || !data.companySize ? (
              <div className="flex items-center justify-between p-3 bg-yellow-50 dark:bg-yellow-950/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
                <span className="font-medium">Business Information</span>
                <Badge variant="outline" className="text-yellow-700 bg-yellow-100">Incomplete</Badge>
              </div>
            ) : null}
            {!data.goals?.length || !data.budget ? (
              <div className="flex items-center justify-between p-3 bg-yellow-50 dark:bg-yellow-950/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
                <span className="font-medium">Goals & Budget</span>
                <Badge variant="outline" className="text-yellow-700 bg-yellow-100">Incomplete</Badge>
              </div>
            ) : null}
            {!data.competitors?.length ? (
              <div className="flex items-center justify-between p-3 bg-yellow-50 dark:bg-yellow-950/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
                <span className="font-medium">Competitor Analysis</span>
                <Badge variant="outline" className="text-yellow-700 bg-yellow-100">Incomplete</Badge>
              </div>
            ) : null}
            {!data.connectedAccounts?.length ? (
              <div className="flex items-center justify-between p-3 bg-yellow-50 dark:bg-yellow-950/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
                <span className="font-medium">Account Connections</span>
                <Badge variant="outline" className="text-yellow-700 bg-yellow-100">Incomplete</Badge>
              </div>
            ) : null}
          </div>
          
          <div className="text-center">
            <Button onClick={goToIncompleteStep} className="w-full">
              Complete Missing Steps
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader className="text-center">
        <div className="mx-auto w-16 h-16 bg-green-100 dark:bg-green-900/20 rounded-full flex items-center justify-center mb-4">
          <CheckCircle className="h-8 w-8 text-green-600" />
        </div>
        <CardTitle className="text-2xl">You're all set!</CardTitle>
        <CardDescription>
          Your MarketingAI Pro workspace is ready. Here's what we've configured for you:
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-4">
          <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
            <span className="font-medium">Industry</span>
            <Badge variant="secondary">{data.industry}</Badge>
          </div>
          <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
            <span className="font-medium">Company Size</span>
            <Badge variant="secondary">{data.companySize}</Badge>
          </div>
          <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
            <span className="font-medium">Marketing Goals</span>
            <div className="flex flex-wrap gap-1">
              {data.goals.slice(0, 2).map((goal) => (
                <Badge key={goal} variant="outline" className="text-xs">
                  {goal.replace("-", " ")}
                </Badge>
              ))}
              {data.goals.length > 2 && (
                <Badge variant="outline" className="text-xs">
                  +{data.goals.length - 2} more
                </Badge>
              )}
            </div>
          </div>
          <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
            <span className="font-medium">Connected Accounts</span>
            <Badge variant="secondary">{data.connectedAccounts.length} connected</Badge>
          </div>
        </div>

        <div className="p-4 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
          <div className="flex items-start gap-3">
            <Sparkles className="h-6 w-6 text-blue-600 mt-1" />
            <div>
              <h4 className="font-semibold text-blue-900 dark:text-blue-100">AI is learning about your business</h4>
              <p className="text-sm text-blue-700 dark:text-blue-200 mt-1">
                Based on your preferences, we're customizing content suggestions, campaign strategies, and optimization
                recommendations specifically for your {data.industry.toLowerCase()} business.
              </p>
            </div>
          </div>
        </div>

        <div className="text-center pt-4">
          <Button onClick={handleGetStarted} size="lg" className="px-8" disabled={isSaving}>
            {isSaving ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                Go to Dashboard
                <ArrowRight className="ml-2 h-4 w-4" />
              </>
            )}
          </Button>
          <p className="text-sm text-muted-foreground mt-3">
            You can always update these settings later in your account preferences.
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
