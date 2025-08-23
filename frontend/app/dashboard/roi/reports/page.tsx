import { DashboardLayout } from "@/components/dashboard/dashboard-layout"
import { ReportGenerator } from "@/components/roi/report-generator"

export default function ROIReportsPage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">ROI Reports</h1>
          <p className="text-muted-foreground">
            Generate comprehensive AI-powered ROI reports with insights and recommendations
          </p>
        </div>
        <ReportGenerator />
      </div>
    </DashboardLayout>
  )
}
