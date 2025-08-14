"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from "recharts"
import { TrendingUp, TrendingDown, Target, DollarSign } from "lucide-react"

const profitabilityData = [
  { month: "Jan", profit: 12000, margin: 26.7, revenue: 45000, costs: 33000 },
  { month: "Feb", profit: 16800, margin: 32.3, revenue: 52000, costs: 35200 },
  { month: "Mar", profit: 14400, margin: 30.0, revenue: 48000, costs: 33600 },
  { month: "Apr", profit: 19520, margin: 32.0, revenue: 61000, costs: 41480 },
  { month: "May", profit: 17600, margin: 32.0, revenue: 55000, costs: 37400 },
  { month: "Jun", profit: 23120, margin: 34.5, revenue: 67000, costs: 43880 },
]

const kpiMetrics = [
  {
    title: "Customer Lifetime Value",
    value: "$2,450",
    change: "+15%",
    trend: "up",
    target: "$2,200",
    progress: 111,
    icon: DollarSign,
  },
  {
    title: "Customer Acquisition Cost",
    value: "$48",
    change: "-8%",
    trend: "down",
    target: "$55",
    progress: 87,
    icon: Target,
  },
  {
    title: "Payback Period",
    value: "2.1 months",
    change: "-0.3",
    trend: "down",
    target: "2.5 months",
    progress: 84,
    icon: TrendingUp,
  },
  {
    title: "Monthly Recurring Revenue",
    value: "$89,200",
    change: "+22%",
    trend: "up",
    target: "$85,000",
    progress: 105,
    icon: TrendingUp,
  },
]

export function ProfitabilityMetrics() {
  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {kpiMetrics.map((metric, index) => {
          const Icon = metric.icon
          return (
            <Card key={index}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{metric.title}</CardTitle>
                <Icon className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metric.value}</div>
                <div className="flex items-center justify-between mt-2">
                  <div
                    className={`flex items-center text-xs ${metric.trend === "up" ? "text-green-600" : "text-red-600"}`}
                  >
                    {metric.trend === "up" ? (
                      <TrendingUp className="h-3 w-3 mr-1" />
                    ) : (
                      <TrendingDown className="h-3 w-3 mr-1" />
                    )}
                    {metric.change}
                  </div>
                  <span className="text-xs text-muted-foreground">vs {metric.target}</span>
                </div>
                <Progress value={metric.progress} className="mt-2" />
              </CardContent>
            </Card>
          )
        })}
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Profit Trends</CardTitle>
            <CardDescription>Monthly profit and margin evolution</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={profitabilityData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip
                  formatter={(value, name) => [
                    name === "profit" ? `$${value.toLocaleString()}` : `${value}%`,
                    name === "profit" ? "Profit" : "Margin",
                  ]}
                />
                <Area type="monotone" dataKey="profit" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.3} />
                <Line type="monotone" dataKey="margin" stroke="#10b981" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Revenue vs Costs</CardTitle>
            <CardDescription>Monthly comparison of revenue and costs</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={profitabilityData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip formatter={(value) => [`$${value.toLocaleString()}`, ""]} />
                <Line type="monotone" dataKey="revenue" stroke="#3b82f6" strokeWidth={2} name="Revenue" />
                <Line type="monotone" dataKey="costs" stroke="#ef4444" strokeWidth={2} name="Costs" />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Profitability Analysis</CardTitle>
          <CardDescription>Key insights and recommendations</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-4">
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp className="h-4 w-4 text-green-600" />
                  <span className="font-medium text-green-800">Strong Performance</span>
                </div>
                <p className="text-sm text-green-700">
                  Profit margin has increased by 7.8% over the last 6 months, indicating efficient cost management and
                  strong revenue growth.
                </p>
              </div>

              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Target className="h-4 w-4 text-blue-600" />
                  <span className="font-medium text-blue-800">Optimization Opportunity</span>
                </div>
                <p className="text-sm text-blue-700">
                  Customer acquisition cost has decreased by 8%, creating opportunity to scale profitable channels.
                </p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <DollarSign className="h-4 w-4 text-yellow-600" />
                  <span className="font-medium text-yellow-800">Revenue Growth</span>
                </div>
                <p className="text-sm text-yellow-700">
                  Monthly recurring revenue is 22% above target, suggesting strong customer retention and upselling
                  success.
                </p>
              </div>

              <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp className="h-4 w-4 text-purple-600" />
                  <span className="font-medium text-purple-800">Forecast</span>
                </div>
                <p className="text-sm text-purple-700">
                  Based on current trends, projected profit margin for next quarter is 36-38%.
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
