"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from "recharts"
import { useEffect, useState } from "react"
import { useUser } from "@clerk/nextjs"
import { roiApi, type TimeRange } from "@/lib/api-client"

interface CostAnalysisProps {
  range?: TimeRange
}

export function CostAnalysis({ range = "30d" }: CostAnalysisProps) {
  const { user } = useUser()
  const [breakdown, setBreakdown] = useState<any[]>([])
  const [monthly, setMonthly] = useState<any[]>([])

  // Helper: filter ALL data by selected range, excluding today
  const filterDataByRange = (allData: any[], selectedRange: TimeRange) => {
    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    let startDate: Date
    switch (selectedRange) {
      case '7d':
        startDate = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000)
        break
      case '14d':
        startDate = new Date(today.getTime() - 14 * 24 * 60 * 60 * 1000)
        break
      case '30d':
        startDate = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000)
        break
      case '90d':
        startDate = new Date(today.getTime() - 90 * 24 * 60 * 60 * 1000)
        break
      default:
        startDate = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000)
    }
    return (allData || []).filter(row => {
      const d = new Date(row.created_at)
      return d >= startDate && d < today
    })
  }

  // Helper: aggregate platform costs and compute metrics
  const aggregatePlatformCosts = (rows: any[]) => {
    const totals: Record<string, { total_spend: number, total_revenue: number, cpc_sum: number, cpc_count: number }> = {}
    for (const row of rows) {
      const platform = (row.platform || '').toLowerCase()
      if (!platform) continue
      const spend = Number(row.ad_spend || 0)
      const revenue = Number(row.revenue_generated || 0)
      const cpc = row.cost_per_click != null ? Number(row.cost_per_click) : NaN
      if (!totals[platform]) totals[platform] = { total_spend: 0, total_revenue: 0, cpc_sum: 0, cpc_count: 0 }
      totals[platform].total_spend += spend
      totals[platform].total_revenue += revenue
      if (!Number.isNaN(cpc)) {
        totals[platform].cpc_sum += cpc
        totals[platform].cpc_count += 1
      }
    }
    const palette = ['#3b82f6', '#10b981', '#ef4444', '#f59e0b', '#8b5cf6', '#06b6d4']
    const result = Object.keys(totals)
      .filter(p => ['facebook','instagram','youtube'].includes(p))
      .map((p, idx) => {
        const t = totals[p]
        const avg_cpc = t.cpc_count > 0 ? t.cpc_sum / t.cpc_count : 0
        const roas = t.total_spend > 0 ? t.total_revenue / t.total_spend : 0
        return {
          platform: p.charAt(0).toUpperCase() + p.slice(1),
          total_spend: t.total_spend,
          avg_cpc,
          revenue_multiplier: roas,
          color: palette[idx % palette.length],
        }
      })
    return result
  }

  useEffect(() => {
    if (!user) return
    ;(async () => {
      try {
        // Cost breakdown: fetch ALL rows then filter/aggregate on client
        const cb = await roiApi.costBreakdown(range)
        if ('all_data' in cb) {
          const filtered = filterDataByRange(cb.all_data, range)
          setBreakdown(aggregatePlatformCosts(filtered))
        } else {
          setBreakdown([])
        }
      } catch (_) {
        setBreakdown([])
      }
      try {
        const year = new Date().getUTCFullYear()
        const mt = await roiApi.monthlySpendTrends(year)
        setMonthly((mt as any).rows || [])
      } catch (_) {
        setMonthly([])
      }
    })()
  }, [user, range])

  const pieColors = ['#3b82f6', '#10b981', '#ef4444', '#f59e0b', '#8b5cf6', '#06b6d4']

  return (
    <div className="space-y-6">
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Cost Breakdown</CardTitle>
            <CardDescription>
              {range === "7d" ? "Last 7 days marketing expenses" :
               range === "30d" ? "Last 30 days marketing expenses" :
               range === "90d" ? "Last 90 days marketing expenses" :
               range === "1y" ? "Last year marketing expenses" :
               "Distribution of marketing expenses"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={breakdown.map(b => ({ platform: b.platform, amount: Number(b.total_spend || 0) }))}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={120}
                  paddingAngle={5}
                  dataKey="amount"
                >
                  {breakdown.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={breakdown[index]?.color || pieColors[index % pieColors.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value: any, _name: any, payload: any) => [`$${Number(value).toLocaleString()}`, payload?.payload?.platform || ""]} />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Cost Per Channel</CardTitle>
            <CardDescription>
              {range === "7d" ? "Last 7 days cost analysis by channel" :
               range === "30d" ? "Last 30 days cost analysis by channel" :
               range === "90d" ? "Last 90 days cost analysis by channel" :
               range === "1y" ? "Last year cost analysis by channel" :
               "Detailed cost analysis by marketing channel"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-5">
              {breakdown.map((channel, index) => (
                <div key={index} className="flex items-center justify-between p-6 rounded-xl border">
                  <div className="flex items-center gap-4">
                    <div className="w-4 h-4 rounded-full" style={{ backgroundColor: channel.color || pieColors[index % pieColors.length] }}></div>
                    <p className="font-semibold text-lg">{channel.platform}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-extrabold text-2xl">${Number(channel.total_spend || 0).toLocaleString()}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Removed bottom full-width Cost Per Channel card */}
    </div>
  )
}
