import { DashboardLayout } from "@/components/dashboard/dashboard-layout"
import { ContentPlanningDashboard } from "@/components/dashboard/content-planning-dashboard"

export default function DashboardPage() {
  return (
    <DashboardLayout>
      <ContentPlanningDashboard />
    </DashboardLayout>
  )
}
