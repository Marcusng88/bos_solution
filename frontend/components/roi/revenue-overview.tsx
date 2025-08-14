"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from "recharts"

const revenueData = [
  { month: "Jan", revenue: 45000, target: 40000 },
  { month: "Feb", revenue: 52000, target: 45000 },
  { month: "Mar", revenue: 48000, target: 50000 },
  { month: "Apr", revenue: 61000, target: 55000 },
  { month: "May", revenue: 55000, target: 60000 },
  { month: "Jun", revenue: 67000, target: 65000 },
]

const revenueBySource = [
  { source: "Google Ads", revenue: 45200, percentage: 35.5 },
  { source: "Facebook Ads", revenue: 38900, percentage: 30.5 },
  { source: "Instagram", revenue: 22100, percentage: 17.3 },
  { source: "LinkedIn", revenue: 12800, percentage: 10.0 },
  { source: "Twitter", revenue: 8450, percentage: 6.7 },
]

export function RevenueOverview() {
  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Revenue Trends</CardTitle>
          <CardDescription>Monthly revenue vs targets</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={revenueData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip formatter={(value) => [`$${value.toLocaleString()}`, ""]} />
              <Line type="monotone" dataKey="revenue" stroke="#3b82f6" strokeWidth={2} name="Actual Revenue" />
              <Line
                type="monotone"
                dataKey="target"
                stroke="#94a3b8"
                strokeWidth={2}
                strokeDasharray="5 5"
                name="Target"
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Revenue by Source</CardTitle>
          <CardDescription>Breakdown of revenue by marketing channel</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={revenueBySource} layout="horizontal">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="source" type="category" width={80} />
              <Tooltip formatter={(value) => [`$${value.toLocaleString()}`, "Revenue"]} />
              <Bar dataKey="revenue" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card className="lg:col-span-2">
        <CardHeader>
          <CardTitle>Revenue Sources Breakdown</CardTitle>
          <CardDescription>Detailed performance by marketing channel</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {revenueBySource.map((source, index) => (
              <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                  <div>
                    <p className="font-medium">{source.source}</p>
                    <p className="text-sm text-muted-foreground">{source.percentage}% of total revenue</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-semibold">${source.revenue.toLocaleString()}</p>
                  <Badge variant="secondary" className="text-xs">
                    {source.percentage > 20 ? "High" : source.percentage > 10 ? "Medium" : "Low"} Impact
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
