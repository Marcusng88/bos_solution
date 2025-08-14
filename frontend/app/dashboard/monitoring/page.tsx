import { DashboardLayout } from "@/components/dashboard/dashboard-layout"
import ContinuousMonitoringDashboard from "./ContinuousMonitoringDashboard"

export default function MonitoringPage() {
  return (
    <DashboardLayout>
      <ContinuousMonitoringDashboard />
    </DashboardLayout>
  )
}
