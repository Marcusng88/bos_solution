"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from "recharts"

const costBreakdown = [
  { category: "Ad Spend", amount: 32000, percentage: 81.6, color: "#3b82f6" },
  { category: "Creative Production", amount: 4200, percentage: 10.7, color: "#10b981" },
  { category: "Tools & Software", amount: 2100, percentage: 5.4, color: "#f59e0b" },
  { category: "Agency Fees", amount: 900, percentage: 2.3, color: "#ef4444" },
]

const monthlySpend = [
  { month: "Jan", adSpend: 28000, creative: 3500, tools: 1800, agency: 800 },
  { month: "Feb", adSpend: 31000, creative: 4000, tools: 1900, agency: 850 },
  { month: "Mar", adSpend: 29500, creative: 3800, tools: 2000, agency: 900 },
  { month: "Apr", adSpend: 35000, creative: 4500, tools: 2100, agency: 950 },
  { month: "May", adSpend: 33000, creative: 4200, tools: 2000, agency: 900 },
  { month: "Jun", adSpend: 32000, creative: 4200, tools: 2100, agency: 900 },
]

const costPerChannel = [
  { channel: "Google Ads", cost: 18500, cpa: 45, roas: 4.2 },
  { channel: "Facebook Ads", cost: 12800, cpa: 38, roas: 3.8 },
  { channel: "Instagram", cost: 6200, cpa: 52, roas: 3.1 },
  { channel: "LinkedIn", cost: 4100, cpa: 68, roas: 2.9 },
  { channel: "Twitter", cost: 2400, cpa: 42, roas: 3.5 },
]

export function CostAnalysis() {
  return (
    <div className="space-y-6">
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Cost Breakdown</CardTitle>
            <CardDescription>Distribution of marketing expenses</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={costBreakdown}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={120}
                  paddingAngle={5}
                  dataKey="amount"
                >
                  {costBreakdown.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => [`$${value.toLocaleString()}`, ""]} />
              </PieChart>
            </ResponsiveContainer>
            <div className="mt-4 space-y-2">
              {costBreakdown.map((item, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }}></div>
                    <span className="text-sm">{item.category}</span>
                  </div>
                  <span className="text-sm font-medium">${item.amount.toLocaleString()}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Monthly Spend Trends</CardTitle>
            <CardDescription>Cost evolution over time</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={monthlySpend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip formatter={(value) => [`$${value.toLocaleString()}`, ""]} />
                <Bar dataKey="adSpend" stackId="a" fill="#3b82f6" name="Ad Spend" />
                <Bar dataKey="creative" stackId="a" fill="#10b981" name="Creative" />
                <Bar dataKey="tools" stackId="a" fill="#f59e0b" name="Tools" />
                <Bar dataKey="agency" stackId="a" fill="#ef4444" name="Agency" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Cost Per Channel</CardTitle>
          <CardDescription>Detailed cost analysis by marketing channel</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {costPerChannel.map((channel, index) => (
              <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                  <div>
                    <p className="font-medium">{channel.channel}</p>
                    <p className="text-sm text-muted-foreground">Cost per acquisition: ${channel.cpa}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className="font-semibold">${channel.cost.toLocaleString()}</p>
                    <p className="text-sm text-muted-foreground">Total spend</p>
                  </div>
                  <Badge variant={channel.roas >= 4 ? "default" : channel.roas >= 3 ? "secondary" : "destructive"}>
                    {channel.roas}x ROAS
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
