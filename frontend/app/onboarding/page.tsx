import { OnboardingWizard } from "@/components/onboarding/onboarding-wizard"
import { AuthGuard } from "@/components/auth/auth-guard"

export default function OnboardingPage() {
  return (
    <AuthGuard>
      <OnboardingWizard />
    </AuthGuard>
  )
}
