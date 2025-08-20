import { Suspense } from "react"
import { OnboardingWizard } from "@/components/onboarding/onboarding-wizard"
import { AuthGuard } from "@/components/auth/auth-guard"

function OnboardingContent() {
  return (
    <AuthGuard>
      <OnboardingWizard />
    </AuthGuard>
  )
}

export default function OnboardingPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    }>
      <OnboardingContent />
    </Suspense>
  )
}
