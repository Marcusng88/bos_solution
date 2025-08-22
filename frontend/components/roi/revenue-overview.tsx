"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, AreaChart, Area, Cell, ComposedChart } from "recharts"
import { useEffect, useMemo, useState } from "react"
import { useUser } from "@clerk/nextjs"
import { roiApi, type TimeRange } from "@/lib/api-client"

interface RevenueOverviewProps {
  range?: TimeRange
}

export function RevenueOverview({ range = "30d" }: RevenueOverviewProps) {
  const { user } = useUser()
  const [trends, setTrends] = useState<any[]>([])
  const [bySource, setBySource] = useState<any[]>([])

  // Professional color palette for platforms
  const platformColors = {
    'YouTube': '#FF0000',
    'Instagram': '#E4405F', 
    'Facebook': '#1877F2',
    'Twitter': '#1DA1F2',
    'LinkedIn': '#0A66C2',
    'TikTok': '#000000'
  }
  
  const getColor = (platform: string, index: number) => {
    return platformColors[platform as keyof typeof platformColors] || 
           ['#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#84cc16'][index % 6]
  }

  useEffect(() => {
    if (!user) return
    roiApi.revenueTrends(user.id, range).then((res) => setTrends(res.rows || [])).catch(() => setTrends([]))
    roiApi.revenueBySource(user.id, range).then((res) => {
      // Filter out duplicate platforms, keeping only capitalized versions
      const filteredBySource = (res.rows || []).filter((row: any) => {
        const platform = row.platform;
        // Keep only capitalized versions (Facebook, Instagram, YouTube)
        return platform === 'Facebook' || platform === 'Instagram' || platform === 'YouTube';
      });
      setBySource(filteredBySource);
    }).catch(() => setBySource([]))
  }, [user, range])

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Revenue Trends</CardTitle>
          <CardDescription>
            {range === "7d" ? "Last 7 days revenue trends" :
             range === "30d" ? "Last 30 days revenue trends" :
             range === "90d" ? "Last 90 days revenue trends" :
             range === "1y" ? "Last year revenue trends" :
             "Revenue trends over time"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <ComposedChart 
              data={trends.map(t => ({ 
                period: t.time_period?.slice(0,10) || '', 
                revenue: Number(t.revenue||0),
                target: Number(t.revenue||0) * 1.1, // Simulated target
                growth: Number(t.revenue||0) * 0.05 // Simulated growth rate
              }))}
              margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
            >
              <defs>
                <linearGradient id="revenueGradientEnhanced" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#10b981" stopOpacity={0.9}/>
                  <stop offset="50%" stopColor="#059669" stopOpacity={0.6}/>
                  <stop offset="100%" stopColor="#047857" stopOpacity={0.2}/>
                </linearGradient>
                <linearGradient id="targetGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#f59e0b" stopOpacity={0.3}/>
                  <stop offset="100%" stopColor="#f59e0b" stopOpacity={0.1}/>
                </linearGradient>
                <filter id="glow">
                  <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
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
                dataKey="period" 
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 11, fill: '#64748b', fontWeight: 500 }}
                padding={{ left: 10, right: 10 }}
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
                cursor={{ fill: 'rgba(16, 185, 129, 0.1)' }}
                formatter={(value: any, name: any) => {
                  const formattedValue = `$${Number(value).toLocaleString()}`
                  return [formattedValue, name === 'revenue' ? 'Revenue' : name === 'target' ? 'Target' : 'Growth']
                }}
                labelFormatter={(label) => `Period: ${label}`}
              />
              
              {/* Target Area (Background) */}
              <Area 
                type="monotone" 
                dataKey="target" 
                stroke="none"
                fill="url(#targetGradient)"
                strokeWidth={0}
              />
              
              {/* Main Revenue Area */}
              <Area 
                type="monotone" 
                dataKey="revenue" 
                stroke="#10b981" 
                strokeWidth={3}
                fill="url(#revenueGradientEnhanced)"
                dot={{ 
                  fill: '#10b981', 
                  strokeWidth: 2, 
                  r: 5,
                  filter: "url(#glow)"
                }}
                activeDot={{ 
                  r: 8, 
                  fill: '#10b981', 
                  stroke: '#ffffff', 
                  strokeWidth: 3,
                  filter: "url(#glow)"
                }}
              />
              
              {/* Growth Line */}
              <Line 
                type="monotone" 
                dataKey="growth" 
                stroke="#3b82f6" 
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={{ fill: '#3b82f6', strokeWidth: 1, r: 3 }}
                activeDot={{ r: 5, fill: '#3b82f6', stroke: '#ffffff', strokeWidth: 2 }}
              />
            </ComposedChart>
          </ResponsiveContainer>
          
          {/* Enhanced Legend */}
          <div className="flex justify-center gap-6 mt-4">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
              <span className="text-sm font-medium text-gray-700">Revenue</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-blue-500"></div>
              <span className="text-sm font-medium text-gray-700">Growth Trend</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-yellow-400 opacity-50"></div>
              <span className="text-sm font-medium text-gray-700">Target Zone</span>
            </div>
          </div>
          
          {/* Performance Summary */}
          {trends.length > 0 && (
            <div className="mt-4 p-3 bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-semibold text-gray-800 text-sm">Performance Summary</h4>
                  <p className="text-xs text-gray-600 mt-1">
                    Total Revenue: <span className="font-semibold text-green-600">
                      ${trends.reduce((sum, t) => sum + Number(t.revenue || 0), 0).toLocaleString()}
                    </span>
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold text-green-600">
                    {trends.length > 1 ? 
                      `${((trends[trends.length - 1].revenue - trends[0].revenue) / Math.max(trends[0].revenue, 1) * 100).toFixed(1)}%`
                      : '0%'
                    }
                  </div>
                  <div className="text-xs text-gray-500">Growth</div>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Revenue by Source</CardTitle>
          <CardDescription>
            {range === "7d" ? "Last 7 days revenue by channel" :
             range === "30d" ? "Last 30 days revenue by channel" :
             range === "90d" ? "Last 90 days revenue by channel" :
             range === "1y" ? "Last year revenue by channel" :
             "Revenue breakdown by marketing channel"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart 
              data={bySource.map(s => ({ source: s.platform, revenue: Number(s.total_revenue||0) }))} 
              layout="horizontal"
              margin={{ top: 20, right: 30, left: 0, bottom: 5 }}
            >
              <defs>
                {bySource.map((s, index) => (
                  <linearGradient key={s.platform} id={`revenue-gradient-${index}`} x1="0" y1="0" x2="1" y2="0">
                    <stop offset="5%" stopColor={getColor(s.platform, index)} stopOpacity={0.9}/>
                    <stop offset="95%" stopColor={getColor(s.platform, index)} stopOpacity={0.4}/>
                  </linearGradient>
                ))}
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" strokeOpacity={0.5} />
              <XAxis 
                type="number" 
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 12, fill: '#64748b' }}
                tickFormatter={(value) => `$${Number(value / 1000).toFixed(0)}k`}
              />
              <YAxis 
                dataKey="source" 
                type="category" 
                width={80}
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 12, fill: '#64748b' }}
              />
              <Tooltip 
                contentStyle={{
                  backgroundColor: '#ffffff',
                  border: '1px solid #e2e8f0',
                  borderRadius: '12px',
                  boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
                  color: '#1f2937'
                }}
                formatter={(value: any) => [`$${Number(value).toLocaleString()}`, "Revenue"]}
              />
              <Bar 
                dataKey="revenue" 
                radius={[0, 8, 8, 0]}
                stroke="#ffffff"
                strokeWidth={1}
              >
                {bySource.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={`url(#revenue-gradient-${index})`} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card className="lg:col-span-2">
        <CardHeader>
          <CardTitle>Revenue Sources Breakdown</CardTitle>
          <CardDescription>
            {range === "7d" ? "Last 7 days detailed channel performance" :
             range === "30d" ? "Last 30 days detailed channel performance" :
             range === "90d" ? "Last 90 days detailed channel performance" :
             range === "1y" ? "Last year detailed channel performance" :
             "Detailed performance by marketing channel"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {bySource.map((source, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-gradient-to-r from-slate-50 to-slate-100 border border-slate-200 rounded-xl hover:shadow-md transition-all duration-200">
                <div className="flex items-center gap-4">
                  <div 
                    className="w-4 h-4 rounded-full shadow-sm"
                    style={{ backgroundColor: getColor(source.platform, index) }}
                  ></div>
                  <div>
                    <p className="font-semibold text-slate-900">{source.platform}</p>
                    <p className="text-sm text-slate-600">${Number(source.total_revenue||0).toLocaleString()}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-bold text-lg text-slate-900">{Number(source.revenue||source.total_revenue||0) ? `$${Number(source.revenue||source.total_revenue||0).toLocaleString()}`: ''}</p>
                  <Badge 
                    variant="secondary" 
                    className="text-xs font-semibold px-2 py-1 mt-1"
                    style={{ backgroundColor: `${getColor(source.platform, index)}20`, color: getColor(source.platform, index) }}
                  >
                    {Number(source.revenue_multiplier||0).toFixed(2)}x
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
