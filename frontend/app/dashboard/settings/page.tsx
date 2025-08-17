import { AuthGuard } from "@/components/auth/auth-guard"
import { DashboardLayout } from "@/components/dashboard/dashboard-layout"
import { ConnectedAccounts } from "@/components/settings/connected-accounts"
import { SettingsWizard } from "@/components/settings/settings-wizard"
import { Separator } from "@/components/ui/separator"

export default function SettingsPage() {
  return (
    <AuthGuard>
      <DashboardLayout>
        <div className="space-y-8">
          {/* Main Settings Wizard */}
          <SettingsWizard />
          
          {/* Separator */}
          <Separator className="my-8" />
          
          {/* Connected Accounts Section */}
          <div className="space-y-4">
            <div>
              <h2 className="text-2xl font-semibold tracking-tight">Connected Accounts</h2>
              <p className="text-muted-foreground">
                Manage your social media and platform connections
              </p>
            </div>
            <ConnectedAccounts />
          </div>
        </div>
      </DashboardLayout>
    </AuthGuard>
  )
}
