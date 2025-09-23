import { DashboardLayout } from "@/components/dashboard/dashboard-layout"
import { ConnectedAccounts } from "@/components/settings/connected-accounts"
import { SettingsWizard } from "@/components/settings/settings-wizard"
import { Separator } from "@/components/ui/separator"
import GradientText from "@/components/effects/GradientText"
import ShinyText from "@/components/effects/ShinyText"

export default function SettingsPage() {
  return (
    <DashboardLayout>
      <div className="space-y-8 relative">
        {/* Animated Background */}
        <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
          <div className="absolute inset-0">
            <div className="absolute top-0 -left-4 w-72 h-72 bg-violet-500/6 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob"></div>
            <div className="absolute top-0 -right-4 w-72 h-72 bg-purple-500/6 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob animation-delay-2000"></div>
            <div className="absolute -bottom-8 left-20 w-72 h-72 bg-indigo-500/6 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob animation-delay-4000"></div>
          </div>
          </div>

          {/* Main Settings Wizard */}
          <div className="relative z-10 animate-slideUp">
            <SettingsWizard />
          </div>
          
          {/* Separator */}
          <Separator className="my-8 relative z-10 bg-gradient-to-r from-transparent via-gray-300 to-transparent" />
          
          {/* Connected Accounts Section */}
          <div className="space-y-4 relative z-10 animate-slideUp animation-delay-200">
            <div className="p-6 bg-gradient-to-r from-blue-50/50 to-cyan-50/50 dark:from-blue-950/30 dark:to-cyan-950/30 rounded-lg border border-white/20 backdrop-blur-sm">
              <h2 className="text-2xl font-semibold tracking-tight">
                <GradientText colors={['#0ea5e9', '#06b6d4', '#14b8a6']}>
                  Connected Accounts
                </GradientText>
              </h2>
              <p className="text-muted-foreground">
                <ShinyText text="Manage your social media and platform connections" />
              </p>
            </div>
            <ConnectedAccounts />
          </div>
        </div>
      </DashboardLayout>
    )
}
