import { DashboardLayout } from "@/components/dashboard/dashboard-layout"
import { PlatformPerformanceTable } from "@/components/roi/platform-performance-table"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useState } from "react"
import { type TimeRange } from "@/lib/api-client"

export default function PlatformPerformancePage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Platform Performance Summary</h1>
            <p className="text-muted-foreground">
              Comprehensive performance metrics across all marketing platforms
            </p>
          </div>
        </div>
        
        <PlatformPerformanceTable range="30d" />
      </div>
    </DashboardLayout>
  )
}
