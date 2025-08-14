import { DashboardLayout } from "@/components/dashboard/dashboard-layout"
import { CompetitorInvestigationDashboard } from "@/components/competitors/competitor-investigation-dashboard"
import { AuthGuard } from "@/components/auth/auth-guard"

export default function CompetitorsPage() {
  return (
    <AuthGuard>
      <DashboardLayout>
        <CompetitorInvestigationDashboard />
      </DashboardLayout>
    </AuthGuard>
  )
}
