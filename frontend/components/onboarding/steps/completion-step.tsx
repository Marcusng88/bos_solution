"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { CheckCircle, Sparkles, ArrowRight } from "lucide-react"
import type { OnboardingData } from "../onboarding-wizard"
import { useUser } from "@clerk/nextjs"
import { useRouter } from "next/navigation"

interface CompletionStepProps {
  data: OnboardingData
}

export function CompletionStep({ data }: CompletionStepProps) {
  const { user } = useUser()
  const router = useRouter()
  const handleGetStarted = async () => {
    try {
      await user?.update({ unsafeMetadata: { onboardingComplete: true } as any })
    } catch (e) {
      // ignore
    } finally {
      try {
        if (typeof window !== "undefined") {
          // Clear onboarding step from localStorage since onboarding is complete
          localStorage.removeItem("onboarding_current_step")
          sessionStorage.setItem("skipOnboardingGuard", "true")
        }
      } catch {}
      router.replace("/dashboard")
    }
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
          <Button onClick={handleGetStarted} size="lg" className="px-8">
            Go to Dashboard
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
          <p className="text-sm text-muted-foreground mt-3">
            You can always update these settings later in your account preferences.
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
