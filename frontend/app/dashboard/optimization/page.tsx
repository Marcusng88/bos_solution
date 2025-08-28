import { DashboardLayout } from "@/components/dashboard/dashboard-layout"
import { OptimizationDashboard } from "@/components/optimization/optimization-dashboard"

export default function CampaignAndOptimizationPage() {
  return (
    <DashboardLayout>
      <OptimizationDashboard />
    </DashboardLayout>
  )
}
