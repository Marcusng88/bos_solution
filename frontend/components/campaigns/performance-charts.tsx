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

  // Convert time range to number of days for data calculation
  const getDaysFromTimeRange = (range: string): number => {
    switch (range) {
      case "24h":
        return 1
      case "7d":
        return 7
      case "14d":
        return 14
      case "30d":
        return 30
      case "1m":
        return 30
      case "3m":
        return 90
      case "6m":
        return 180
      case "ytd":
        // Calculate days from January 1st of current year
        const now = new Date()
        const startOfYear = new Date(now.getFullYear(), 0, 1)
        return Math.ceil((now.getTime() - startOfYear.getTime()) / (1000 * 60 * 60 * 24))
      default:
        return 7
    }
  }

  const getMetricData = () => {
    // Get the number of days for the selected time range
    const days = getDaysFromTimeRange(timeRange)
    
    // Generate performance data based on the selected time period
    // This simulates how daily data would be calculated for conversions and spend over the graph:
    // 1. We create data points for each day in the selected period
    // 2. Each metric (clicks, conversions, spend) gets realistic daily values
    // 3. The data shows trends over time while maintaining realistic campaign performance patterns
    
    const data = []
    const today = new Date()
    
    for (let i = days - 1; i >= 0; i--) {
      const date = new Date(today)
      date.setDate(today.getDate() - i)
      
      // Generate realistic daily values with some variation
      const baseClicks = 1200 + Math.random() * 800
      const baseConversions = 45 + Math.random() * 30
      const baseSpend = 340 + Math.random() * 120
      
      data.push({
        date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        clicks: Math.round(baseClicks),
        conversions: Math.round(baseConversions),
        spend: Math.round(baseSpend)
      })
    }
    
    return data
  }

  const metricData = getMetricData()

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
              <AreaChart data={metricData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Area
                  type="monotone"
                  dataKey={selectedMetric}
                  stroke="#8884d8"
                  fill="#8884d8"
                  fillOpacity={0.3}
                />
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
