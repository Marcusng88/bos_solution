"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { TrendingUp, DollarSign, Target, Clock } from "lucide-react"
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from "recharts"

const performanceData = [
  { date: "Week 1", before: 2400, after: 2800, savings: 150 },
  { date: "Week 2", before: 2200, after: 2900, savings: 280 },
  { date: "Week 3", before: 2600, after: 3200, savings: 320 },
  { date: "Week 4", before: 2300, after: 3100, savings: 450 },
]

const optimizationImpacts = [
  {
    category: "Budget Optimization",
    applied: 3,
    avgImprovement: 22,
    totalSavings: 1240,
    icon: DollarSign,
    color: "text-green-600",
  },
  {
    category: "Targeting Refinement",
    applied: 2,
    avgImprovement: 18,
    totalSavings: 890,
    icon: Target,
    color: "text-blue-600",
  },
  {
    category: "Schedule Optimization",
    applied: 2,
    avgImprovement: 15,
    totalSavings: 560,
    icon: Clock,
    color: "text-purple-600",
  },
]

export function PerformanceImpact() {
  return (
    <div className="space-y-6">
      {/* Impact Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Savings</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">$2,690</div>
            <p className="text-xs text-muted-foreground">From applied optimizations</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Performance Boost</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">+24%</div>
            <p className="text-xs text-muted-foreground">Average improvement</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Optimizations Applied</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">7</div>
            <p className="text-xs text-muted-foreground">This month</p>
          </CardContent>
        </Card>
      </div>

      {/* Performance Trend */}
      <Card>
        <CardHeader>
          <CardTitle>Performance Before vs After Optimization</CardTitle>
          <CardDescription>Weekly comparison showing the impact of applied optimizations</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={performanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Area
                  type="monotone"
                  dataKey="before"
                  stackId="1"
                  stroke="#EF4444"
                  fill="#EF4444"
                  fillOpacity={0.1}
                  name="Before Optimization"
                />
                <Area
                  type="monotone"
                  dataKey="after"
                  stackId="2"
                  stroke="#10B981"
                  fill="#10B981"
                  fillOpacity={0.1}
                  name="After Optimization"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Optimization Categories */}
        <Card>
          <CardHeader>
            <CardTitle>Impact by Category</CardTitle>
            <CardDescription>Performance improvements across different optimization types</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {optimizationImpacts.map((impact, index) => {
              const Icon = impact.icon
              return (
                <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-gray-100 dark:bg-gray-800 rounded-lg">
                      <Icon className={`h-5 w-5 ${impact.color}`} />
                    </div>
                    <div>
                      <h4 className="font-medium">{impact.category}</h4>
                      <p className="text-sm text-muted-foreground">{impact.applied} optimizations applied</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="flex items-center gap-2">
                      <Badge variant="secondary">+{impact.avgImprovement}%</Badge>
                      <TrendingUp className="h-4 w-4 text-green-600" />
                    </div>
                    <p className="text-sm text-green-600 font-medium">${impact.totalSavings} saved</p>
                  </div>
                </div>
              )
            })}
          </CardContent>
        </Card>

        {/* Savings Breakdown */}
        <Card>
          <CardHeader>
            <CardTitle>Monthly Savings Breakdown</CardTitle>
            <CardDescription>Cost savings from optimization implementations</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={performanceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="savings" fill="#10B981" name="Savings ($)" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Success Stories */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Success Stories</CardTitle>
          <CardDescription>Highlights from your most impactful optimizations</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="p-4 bg-green-50 dark:bg-green-950/20 rounded-lg border border-green-200">
            <div className="flex items-start gap-3">
              <TrendingUp className="h-5 w-5 text-green-600 mt-1" />
              <div>
                <h4 className="font-semibold text-green-900 dark:text-green-100">Budget Reallocation Success</h4>
                <p className="text-sm text-green-800 dark:text-green-200 mt-1">
                  Shifting budget from underperforming ad sets to high-performers resulted in a 34% increase in
                  conversions while reducing overall spend by $450 per week.
                </p>
                <Badge variant="outline" className="mt-2 text-xs">
                  Applied 5 days ago
                </Badge>
              </div>
            </div>
          </div>

          <div className="p-4 bg-blue-50 dark:bg-blue-950/20 rounded-lg border border-blue-200">
            <div className="flex items-start gap-3">
              <Target className="h-5 w-5 text-blue-600 mt-1" />
              <div>
                <h4 className="font-semibold text-blue-900 dark:text-blue-100">Audience Targeting Refinement</h4>
                <p className="text-sm text-blue-800 dark:text-blue-200 mt-1">
                  Narrowing audience to high-intent segments improved conversion rate by 28% and reduced cost per
                  acquisition from $45 to $32.
                </p>
                <Badge variant="outline" className="mt-2 text-xs">
                  Applied 2 weeks ago
                </Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
