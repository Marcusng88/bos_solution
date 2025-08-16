import { DashboardLayout } from "@/components/dashboard/dashboard-layout"
import { ConnectedAccounts } from "@/components/settings/connected-accounts"
import { AuthGuard } from "@/components/auth/auth-guard"

export default function SettingsPage() {
  return (
    <AuthGuard>
      <DashboardLayout>
        <ConnectedAccounts />
      </DashboardLayout>
    </AuthGuard>
  )
}
