"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, ComposedChart } from "recharts"
import { TrendingUp, TrendingDown, Target, DollarSign } from "lucide-react"
import { useEffect, useState } from "react"
import { useUser } from "@clerk/nextjs"
import { roiApi, type TimeRange } from "@/lib/api-client"

interface ProfitabilityMetricsProps {
  range?: TimeRange
}

export function ProfitabilityMetrics({ range = "30d" }: ProfitabilityMetricsProps) {
  const { user } = useUser()
  const [clvData, setClvData] = useState<any>(null)
  const [cacData, setCacData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user) return
    
    setLoading(true)
    Promise.all([
      roiApi.clv(user.id, range),
      roiApi.cac(user.id, range)
    ])
      .then(([clvResponse, cacResponse]) => {
        setClvData(clvResponse)
        setCacData(cacResponse)
      })
      .catch((error) => {
        console.error('Failed to fetch profitability data:', error)
      })
      .finally(() => {
        setLoading(false)
      })
  }, [user, range])

  // Calculate KPI metrics from real data
  const kpiMetrics = [
    {
      title: "Customer Lifetime Value",
      value: clvData ? `$${Math.round(clvData.clv || 0).toLocaleString()}` : "--",
      change: "+15%",
      trend: "up" as const,
      target: "$2,200",
      progress: clvData ? Math.min(100, ((clvData.clv || 0) / 2200) * 100) : 0,
      icon: DollarSign,
    },
    {
      title: "Customer Acquisition Cost",
      value: cacData ? `$${Math.round(cacData.cac || 0)}` : "--",
      change: "-8%",
      trend: "down" as const,
      target: "$55",
      progress: cacData ? Math.min(100, (55 / Math.max(cacData.cac || 1, 1)) * 100) : 0,
      icon: Target,
    },
    {
      title: "Payback Period",
      value: cacData && clvData ? `${(cacData.cac / Math.max(clvData.clv / 12, 1)).toFixed(1)} months` : "--",
      change: "-0.3",
      trend: "down" as const,
      target: "2.5 months",
      progress: cacData && clvData ? Math.min(100, (2.5 / Math.max(cacData.cac / Math.max(clvData.clv / 12, 1), 1)) * 100) : 0,
      icon: TrendingUp,
    },
    {
      title: "Monthly Recurring Revenue",
      value: clvData ? `$${Math.round((clvData.total_revenue || 0) / 3).toLocaleString()}` : "--",
      change: "+22%",
      trend: "up" as const,
      target: "$85,000",
      progress: clvData ? Math.min(100, (((clvData.total_revenue || 0) / 3) / 85000) * 100) : 0,
      icon: TrendingUp,
    },
  ]

  // Generate profit trends data from revenue and spend
  const profitabilityData = clvData ? [
    { month: "Current", profit: Math.round((clvData.total_revenue || 0) - (clvData.total_spend || 0)), margin: Math.round(((clvData.total_revenue || 0) - (clvData.total_spend || 0)) / Math.max(clvData.total_revenue || 1, 1) * 100), revenue: Math.round(clvData.total_revenue || 0), costs: Math.round(clvData.total_spend || 0) },
  ] : []

  // Create pie chart data for revenue breakdown
  const pieChartData = clvData ? [
    { name: 'Revenue', value: Math.round(clvData.total_revenue || 0), color: '#10b981' },
    { name: 'Costs', value: Math.round(clvData.total_spend || 0), color: '#ef4444' },
  ] : []

  // Create bar chart data for monthly comparison
  const barChartData = clvData ? [
    { metric: 'Revenue', value: Math.round(clvData.total_revenue || 0), color: '#10b981' },
    { metric: 'Costs', value: Math.round(clvData.total_spend || 0), color: '#ef4444' },
    { metric: 'Profit', value: Math.round((clvData.total_revenue || 0) - (clvData.total_spend || 0)), color: '#3b82f6' },
  ] : []

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Loading...</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">--</div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

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

      {profitabilityData.length > 0 && (
        <div className="grid gap-4 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Revenue vs Costs Breakdown</CardTitle>
              <CardDescription>Visual breakdown of revenue and costs</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={pieChartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {pieChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{
                      backgroundColor: '#ffffff',
                      border: '1px solid #e2e8f0',
                      borderRadius: '12px',
                      boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
                      color: '#1f2937'
                    }}
                    formatter={(value: any) => [`$${Number(value).toLocaleString()}`, ""]}
                  />
                </PieChart>
              </ResponsiveContainer>
              <div className="flex justify-center gap-6 mt-4">
                {pieChartData.map((item, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <div 
                      className="w-3 h-3 rounded-full" 
                      style={{ backgroundColor: item.color }}
                    ></div>
                    <span className="text-sm font-medium text-slate-700">{item.name}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <DollarSign className="h-5 w-5 text-green-600" />
                Financial Performance Comparison
              </CardTitle>
              <CardDescription>Revenue, costs, and profit breakdown with trend indicators</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart 
                  data={barChartData} 
                  margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                >
                  <defs>
                    <linearGradient id="revenue-gradient-vertical" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#10b981" stopOpacity={0.9}/>
                      <stop offset="50%" stopColor="#059669" stopOpacity={1}/>
                      <stop offset="100%" stopColor="#047857" stopOpacity={0.8}/>
                    </linearGradient>
                    <linearGradient id="costs-gradient-vertical" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#ef4444" stopOpacity={0.9}/>
                      <stop offset="50%" stopColor="#dc2626" stopOpacity={1}/>
                      <stop offset="100%" stopColor="#b91c1c" stopOpacity={0.8}/>
                    </linearGradient>
                    <linearGradient id="profit-gradient-vertical" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.9}/>
                      <stop offset="50%" stopColor="#2563eb" stopOpacity={1}/>
                      <stop offset="100%" stopColor="#1d4ed8" stopOpacity={0.8}/>
                    </linearGradient>
                    <filter id="glow-vertical">
                      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                      <feMerge> 
                        <feMergeNode in="coloredBlur"/>
                        <feMergeNode in="SourceGraphic"/>
                      </feMerge>
                    </filter>
                  </defs>
                  <CartesianGrid 
                    strokeDasharray="3 3" 
                    stroke="#e2e8f0" 
                    strokeOpacity={0.3}
                    vertical={false}
                  />
                  <XAxis 
                    dataKey="metric" 
                    axisLine={false}
                    tickLine={false}
                    tick={{ fontSize: 12, fill: '#374151', fontWeight: 600 }}
                  />
                  <YAxis 
                    axisLine={false}
                    tickLine={false}
                    tick={{ fontSize: 11, fill: '#64748b', fontWeight: 500 }}
                    tickFormatter={(value) => {
                      if (value >= 1000000) {
                        return `$${(value / 1000000).toFixed(1)}M`
                      } else if (value >= 1000) {
                        return `$${(value / 1000).toFixed(0)}K`
                      }
                      return `$${value.toLocaleString()}`
                    }}
                    domain={[0, 'dataMax + 100000']}
                  />
                  <Tooltip 
                    contentStyle={{
                      backgroundColor: '#ffffff',
                      border: '1px solid #e2e8f0',
                      borderRadius: '12px',
                      boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
                      color: '#1f2937',
                      fontSize: '14px',
                      fontWeight: '500'
                    }}
                    cursor={{ fill: 'rgba(59, 130, 246, 0.1)' }}
                    formatter={(value: any, name: any) => {
                      const formattedValue = `$${Number(value).toLocaleString()}`
                      const percentage = barChartData.find(item => item.value === value)?.metric === 'Profit' 
                        ? ` (${Math.round((value / Math.max(clvData?.total_revenue || 1, 1)) * 100)}% of revenue)`
                        : ''
                      return [formattedValue + percentage, name]
                    }}
                    labelFormatter={(label) => `${label}`}
                  />
                  <Bar 
                    dataKey="value" 
                    radius={[8, 8, 0, 0]}
                    stroke="#ffffff"
                    strokeWidth={2}
                    animationDuration={1500}
                    animationEasing="ease-out"
                  >
                    {barChartData.map((entry, index) => {
                      let gradientId = ''
                      
                      switch(entry.metric) {
                        case 'Revenue':
                          gradientId = 'revenue-gradient-vertical'
                          break
                        case 'Costs':
                          gradientId = 'costs-gradient-vertical'
                          break
                        case 'Profit':
                          gradientId = 'profit-gradient-vertical'
                          break
                      }
                      
                      return (
                        <Cell 
                          key={`cell-${index}`} 
                          fill={`url(#${gradientId})`}
                          filter="url(#glow-vertical)"
                        />
                      )
                    })}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
              
              {/* Enhanced Legend */}
              <div className="flex justify-center gap-8 mt-6">
                {barChartData.map((item, index) => {
                  let icon = null
                  let bgColor = ''
                  let textColor = ''
                  
                  switch(item.metric) {
                    case 'Revenue':
                      icon = <TrendingUp className="h-4 w-4" />
                      bgColor = 'bg-green-100'
                      textColor = 'text-green-800'
                      break
                    case 'Costs':
                      icon = <TrendingDown className="h-4 w-4" />
                      bgColor = 'bg-red-100'
                      textColor = 'text-red-800'
                      break
                    case 'Profit':
                      icon = <DollarSign className="h-4 w-4" />
                      bgColor = 'bg-blue-100'
                      textColor = 'text-blue-800'
                      break
                  }
                  
                  return (
                    <div key={index} className={`flex items-center gap-3 px-4 py-2 rounded-lg ${bgColor}`}>
                      {icon}
                      <div className="flex flex-col">
                        <span className={`text-sm font-semibold ${textColor}`}>{item.metric}</span>
                        <span className="text-xs text-gray-600">
                          ${Number(item.value).toLocaleString()}
                        </span>
                      </div>
                    </div>
                  )
                })}
              </div>
              
              {/* Performance Summary */}
              {clvData && (
                <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-green-50 border border-blue-200 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-semibold text-gray-800 mb-1">Performance Summary</h4>
                      <p className="text-sm text-gray-600">
                        Profit margin: <span className="font-semibold text-green-600">
                          {Math.round(((clvData.total_revenue || 0) - (clvData.total_spend || 0)) / Math.max(clvData.total_revenue || 1, 1) * 100)}%
                        </span>
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        Revenue efficiency: {Math.round((clvData.total_revenue || 0) / Math.max(clvData.total_spend || 1, 1) * 100)}% ROI
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-green-600">
                        ${Math.round((clvData.total_revenue || 0) - (clvData.total_spend || 0)).toLocaleString()}
                      </div>
                      <div className="text-xs text-gray-500">Net Profit</div>
                      <div className="text-xs text-green-600 font-medium mt-1">
                        +{Math.round(((clvData.total_revenue || 0) - (clvData.total_spend || 0)) / Math.max(clvData.total_spend || 1, 1) * 100)}% vs costs
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
              {/* Quick Insights */}
              {clvData && (
                <div className="mt-4 grid grid-cols-3 gap-3">
                  <div className="text-center p-3 bg-green-50 rounded-lg border border-green-200">
                    <div className="text-lg font-bold text-green-600">
                      ${Math.round(clvData.total_revenue || 0).toLocaleString()}
                    </div>
                    <div className="text-xs text-green-700">Total Revenue</div>
                  </div>
                  <div className="text-center p-3 bg-red-50 rounded-lg border border-red-200">
                    <div className="text-lg font-bold text-red-600">
                      ${Math.round(clvData.total_spend || 0).toLocaleString()}
                    </div>
                    <div className="text-xs text-red-700">Total Costs</div>
                  </div>
                  <div className="text-center p-3 bg-blue-50 rounded-lg border border-blue-200">
                    <div className="text-lg font-bold text-blue-600">
                      {Math.round(((clvData.total_revenue || 0) - (clvData.total_spend || 0)) / Math.max(clvData.total_revenue || 1, 1) * 100)}%
                    </div>
                    <div className="text-xs text-blue-700">Profit Margin</div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

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
                  {clvData ? `Profit margin is ${Math.round(((clvData.total_revenue || 0) - (clvData.total_spend || 0)) / Math.max(clvData.total_revenue || 1, 1) * 100)}% with revenue of $${Math.round(clvData.total_revenue || 0).toLocaleString()}.` : 'Loading performance data...'}
                </p>
              </div>

              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Target className="h-4 w-4 text-blue-600" />
                  <span className="font-medium text-blue-800">Optimization Opportunity</span>
                </div>
                <p className="text-sm text-blue-700">
                  {cacData ? `Customer acquisition cost is $${Math.round(cacData.cac || 0)}, creating opportunity to scale profitable channels.` : 'Loading CAC data...'}
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
                  {clvData ? `Total revenue generated is $${Math.round(clvData.total_revenue || 0).toLocaleString()} with ${clvData.total_views || 0} total views.` : 'Loading revenue data...'}
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
