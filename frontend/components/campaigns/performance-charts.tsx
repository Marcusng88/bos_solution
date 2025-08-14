"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { useState } from "react"
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts"

interface PerformanceChartsProps {
  timeRange: string
}

const performanceData = [
  { date: "Jan 1", clicks: 1200, conversions: 45, spend: 340 },
  { date: "Jan 2", clicks: 1450, conversions: 52, spend: 380 },
  { date: "Jan 3", clicks: 1100, conversions: 38, spend: 320 },
  { date: "Jan 4", clicks: 1680, conversions: 67, spend: 420 },
  { date: "Jan 5", clicks: 1890, conversions: 78, spend: 450 },
  { date: "Jan 6", clicks: 1560, conversions: 61, spend: 390 },
  { date: "Jan 7", clicks: 1720, conversions: 69, spend: 410 },
]

const platformData = [
  { name: "Facebook", value: 45, color: "#1877F2" },
  { name: "Instagram", value: 30, color: "#E4405F" },
  { name: "LinkedIn", value: 15, color: "#0A66C2" },
  { name: "Twitter", value: 10, color: "#1DA1F2" },
]

const conversionFunnelData = [
  { stage: "Impressions", value: 125000, percentage: 100 },
  { stage: "Clicks", value: 3750, percentage: 3.0 },
  { stage: "Landing Page", value: 2850, percentage: 2.3 },
  { stage: "Sign-ups", value: 890, percentage: 0.7 },
  { stage: "Conversions", value: 234, percentage: 0.2 },
]

export function PerformanceCharts({ timeRange }: PerformanceChartsProps) {
  const [selectedMetric, setSelectedMetric] = useState("clicks")

  const getMetricData = () => {
    switch (selectedMetric) {
      case "clicks":
        return performanceData.map((d) => ({ ...d, value: d.clicks }))
      case "conversions":
        return performanceData.map((d) => ({ ...d, value: d.conversions }))
      case "spend":
        return performanceData.map((d) => ({ ...d, value: d.spend }))
      default:
        return performanceData.map((d) => ({ ...d, value: d.clicks }))
    }
  }

  return (
    <div className="space-y-6">
      {/* Performance Trend */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Performance Trends</CardTitle>
              <CardDescription>Track key metrics over time</CardDescription>
            </div>
            <Select value={selectedMetric} onValueChange={setSelectedMetric}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="clicks">Clicks</SelectItem>
                <SelectItem value="conversions">Conversions</SelectItem>
                <SelectItem value="spend">Spend</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={getMetricData()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Area type="monotone" dataKey="value" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.1} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Platform Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Platform Performance</CardTitle>
            <CardDescription>Conversion distribution by platform</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={platformData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {platformData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex flex-wrap gap-2 mt-4">
              {platformData.map((platform) => (
                <div key={platform.name} className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: platform.color }} />
                  <span className="text-sm">{platform.name}</span>
                  <Badge variant="secondary" className="text-xs">
                    {platform.value}%
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Conversion Funnel */}
        <Card>
          <CardHeader>
            <CardTitle>Conversion Funnel</CardTitle>
            <CardDescription>User journey from impression to conversion</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {conversionFunnelData.map((stage, index) => (
                <div key={stage.stage} className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">{stage.stage}</span>
                    <div className="text-right">
                      <span className="text-sm font-semibold">{stage.value.toLocaleString()}</span>
                      <span className="text-xs text-muted-foreground ml-2">({stage.percentage}%)</span>
                    </div>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2 dark:bg-gray-700">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${stage.percentage * 10}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Metrics */}
      <Card>
        <CardHeader>
          <CardTitle>Daily Performance Breakdown</CardTitle>
          <CardDescription>Detailed view of clicks, conversions, and spend</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={performanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="clicks" fill="#3B82F6" name="Clicks" />
                <Bar dataKey="conversions" fill="#10B981" name="Conversions" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
