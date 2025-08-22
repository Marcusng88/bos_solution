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
  useEffect(() => {
    if (!user) return
    roiApi.costBreakdown(user.id, range).then((res) => setBreakdown(res.rows || [])).catch(() => setBreakdown([]))
    const year = new Date().getUTCFullYear()
    roiApi.monthlySpendTrends(user.id, year).then((res) => setMonthly(res.rows || [])).catch(() => setMonthly([]))
  }, [user, range])

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
                  data={breakdown.map(b => ({ category: b.platform, amount: Number(b.total_spend||0), color: "#3b82f6" }))}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={120}
                  paddingAngle={5}
                  dataKey="amount"
                >
                  {breakdown.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => [`$${value.toLocaleString()}`, ""]} />
              </PieChart>
            </ResponsiveContainer>
            <div className="mt-4 space-y-2">
              {breakdown.map((item, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: "#3b82f6" }}></div>
                    <span className="text-sm">{item.platform}</span>
                  </div>
                  <span className="text-sm font-medium">${Number(item.total_spend||0).toLocaleString()}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Spend Trends</CardTitle>
            <CardDescription>
              {range === "7d" ? "Last 7 days cost evolution" :
               range === "30d" ? "Last 30 days cost evolution" :
               range === "90d" ? "Last 90 days cost evolution" :
               range === "1y" ? "Last year cost evolution" :
               "Cost evolution over time"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={monthly.map(m => ({ month: m.month, adSpend: Number(m.spend||0), revenue: Number(m.revenue||0) }))}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip formatter={(value) => [`$${value.toLocaleString()}`, ""]} />
                <Bar dataKey="adSpend" fill="#3b82f6" name="Ad Spend" />
                <Bar dataKey="revenue" fill="#10b981" name="Revenue" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

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
          <div className="space-y-4">
            {breakdown.map((channel, index) => (
              <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                  <div>
                    <p className="font-medium">{channel.platform}</p>
                    <p className="text-sm text-muted-foreground">Avg CPC: ${Number(channel.avg_cpc||0).toFixed(2)}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className="font-semibold">${Number(channel.total_spend||0).toLocaleString()}</p>
                    <p className="text-sm text-muted-foreground">Total spend</p>
                  </div>
                  <Badge variant={(channel as any).revenue_multiplier >= 4 ? "default" : (channel as any).revenue_multiplier >= 3 ? "secondary" : "destructive"}>
                    {Number((channel as any).revenue_multiplier||0).toFixed(2)}x ROAS
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
