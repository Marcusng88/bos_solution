import { AuthGuard } from "@/components/auth/auth-guard"
import { DashboardLayout } from "@/components/dashboard/dashboard-layout"
import { SettingsWizard } from "@/components/settings/settings-wizard"

export default function SettingsPage() {
  return (
    <AuthGuard>
      <DashboardLayout>
        <SettingsWizard />
      </DashboardLayout>
    </AuthGuard>
  )
}
