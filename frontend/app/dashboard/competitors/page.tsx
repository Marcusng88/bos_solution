import { DashboardLayout } from "@/components/dashboard/dashboard-layout"
import { CompetitorInvestigationDashboard } from "@/components/competitors/competitor-investigation-dashboard"

export default function CompetitorsPage() {
  return (
    <DashboardLayout>
      <CompetitorInvestigationDashboard />
    </DashboardLayout>
  )
}
