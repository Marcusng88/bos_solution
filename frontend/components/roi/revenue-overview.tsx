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
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

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
    
    const fetchRevenueData = async () => {
      try {
        setLoading(true)
        setError(null)
        
        // Fetch revenue trends
        const trendsResponse = await roiApi.revenueTrends(range)
        if ('all_data' in trendsResponse) {
          const allTrendsData = trendsResponse.all_data
          const filteredTrendsData = filterDataByRange(allTrendsData, range)
          const processedTrendsData = processRevenueTrendsData(filteredTrendsData)
          setTrends(processedTrendsData)
        } else {
          setTrends([])
        }
        
        // Fetch revenue by source
        const sourceResponse = await roiApi.revenueBySource(range)
        console.log('📊 Revenue by source response:', sourceResponse)
        
        if ('all_data' in sourceResponse) {
          const allSourceData = sourceResponse.all_data
          console.log('📊 All source data received:', allSourceData.length, 'rows')
          console.log('📊 Sample source data:', allSourceData.slice(0, 3))
          
          const filteredSourceData = filterDataByRange(allSourceData, range)
          console.log('📊 Filtered source data:', filteredSourceData.length, 'rows')
          
          const processedSourceData = processRevenueBySourceData(filteredSourceData)
          console.log('📊 Processed source data:', processedSourceData)
          
          setBySource(processedSourceData)
        } else {
          console.log('❌ No all_data in source response:', sourceResponse)
          setBySource([])
        }
      } catch (error) {
        console.error('Error fetching revenue data:', error)
        setError('Failed to fetch revenue data')
        setTrends([])
        setBySource([])
      } finally {
        setLoading(false)
      }
    }
    
    fetchRevenueData()
  }, [user, range])

  // Frontend filtering function - handles 7d, 14d, 30d, 90d logic
  const filterDataByRange = (allData: any[], selectedRange: TimeRange) => {
    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate()) // Start of today
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
        startDate = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000) // Default to 7 days
    }
    
    console.log(`📅 Revenue filtering: ${startDate.toISOString()} to ${today.toISOString()}`)
    
    // Filter data within the range
    return allData.filter(row => {
      const rowDate = new Date(row.created_at)
      return rowDate >= startDate && rowDate < today // Exclude today
    })
  }

  // Process revenue trends data
  const processRevenueTrendsData = (filteredData: any[]) => {
    // Group by date and sum revenue
    const dailyRevenue: { [key: string]: number } = {}
    
    filteredData.forEach(row => {
      const dateKey = row.created_at.split('T')[0] // YYYY-MM-DD
      const revenue = parseFloat(row.revenue_generated || 0)
      dailyRevenue[dateKey] = (dailyRevenue[dateKey] || 0) + revenue
    })
    
    // Convert to chart format
    return Object.keys(dailyRevenue)
      .sort()
      .map(dateKey => ({
        time_period: dateKey,
        revenue: dailyRevenue[dateKey]
      }))
  }

  // Process revenue by source data
  const processRevenueBySourceData = (filteredData: any[]) => {
    console.log('🔍 Processing revenue by source data:', filteredData.length, 'rows')
    
    // Group by platform and sum revenue
    const platformRevenue: { [key: string]: number } = {}
    
    filteredData.forEach(row => {
      const platform = row.platform || 'unknown'
      const revenue = parseFloat(row.revenue_generated || 0)
      platformRevenue[platform] = (platformRevenue[platform] || 0) + revenue
      console.log(`📊 Platform: ${platform}, Revenue: ${revenue}, Running Total: ${platformRevenue[platform]}`)
    })
    
    console.log('📊 Platform revenue totals:', platformRevenue)
    
    // Convert to chart format and filter platforms
    const result = Object.keys(platformRevenue)
      .filter(platform => ['facebook', 'youtube', 'instagram'].includes(platform))
      .map(platform => ({
        platform: platform.charAt(0).toUpperCase() + platform.slice(1), // Capitalize first letter
        revenue: platformRevenue[platform]
      }))
    
    console.log('🎯 Final revenue by source data:', result)
    return result
  }

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      {loading && (
        <div className="lg:col-span-2 text-center py-8">
          <div className="text-muted-foreground">Loading revenue data...</div>
        </div>
      )}
      
      {error && (
        <div className="lg:col-span-2 text-center py-8">
          <div className="text-red-500">Error: {error}</div>
        </div>
      )}
      
      {!loading && !error && trends.length === 0 && bySource.length === 0 && (
        <div className="lg:col-span-2 text-center py-8">
          <div className="text-muted-foreground">No revenue data available for the selected range</div>
        </div>
      )}
      
      {!loading && !error && trends.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Revenue Trends</CardTitle>
            <CardDescription>
              {range === "7d" ? "Last 7 days revenue trends" :
               range === "14d" ? "Last 14 days revenue trends" :
               range === "30d" ? "Last 30 days revenue trends" :
               range === "90d" ? "Last 90 days revenue trends" :
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
      )}

      {!loading && !error && bySource.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Revenue by Source</CardTitle>
            <CardDescription>
              {range === "7d" ? "Last 7 days revenue by platform" :
               range === "14d" ? "Last 14 days revenue by platform" :
               range === "30d" ? "Last 30 days revenue by platform" :
               range === "90d" ? "Last 90 days revenue by platform" :
               "Revenue breakdown by marketing platform"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart 
                data={bySource} 
                margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" strokeOpacity={0.5} />
                <XAxis 
                  dataKey="platform" 
                  axisLine={false}
                  tickLine={false}
                  tick={{ fontSize: 12, fill: '#64748b' }}
                />
                <YAxis 
                  axisLine={false}
                  tickLine={false}
                  tick={{ fontSize: 12, fill: '#64748b' }}
                  tickFormatter={(value) => `$${Number(value / 1000).toFixed(0)}k`}
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
                  fill="#10b981"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {!loading && !error && bySource.length > 0 && (
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Revenue Sources Breakdown</CardTitle>
            <CardDescription>
              {range === "7d" ? "Last 7 days detailed channel performance" :
               range === "14d" ? "Last 14 days detailed channel performance" :
               range === "30d" ? "Last 30 days detailed channel performance" :
               range === "90d" ? "Last 90 days detailed channel performance" :
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
                      <p className="text-sm text-slate-600">${Number(source.revenue||0).toLocaleString()}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-lg text-slate-900">${Number(source.revenue||0).toLocaleString()}</p>
                    <Badge 
                      variant="secondary" 
                      className="text-xs font-semibold px-2 py-1 mt-1"
                      style={{ backgroundColor: `${getColor(source.platform, index)}20`, color: getColor(source.platform, index) }}
                    >
                      Revenue
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
