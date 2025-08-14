import { DashboardLayout } from "@/components/dashboard/dashboard-layout"
import { ContentPlanningDashboard } from "@/components/dashboard/content-planning-dashboard"
import { AuthGuard } from "@/components/auth/auth-guard"

export default function DashboardPage() {
  return (
    <AuthGuard>
      <DashboardLayout>
        <ContentPlanningDashboard />
      </DashboardLayout>
    </AuthGuard>
  )
}
