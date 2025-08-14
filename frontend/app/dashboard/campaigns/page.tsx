import { DashboardLayout } from "@/components/dashboard/dashboard-layout"
import { CampaignTrackingDashboard } from "@/components/campaigns/campaign-tracking-dashboard"

export default function CampaignsPage() {
  return (
    <DashboardLayout>
      <CampaignTrackingDashboard />
    </DashboardLayout>
  )
}
