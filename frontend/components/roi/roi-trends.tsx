"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { AreaChart, Area, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, defs, linearGradient, stop } from "recharts"
import { useEffect, useState } from "react"
import { useUser } from "@clerk/nextjs"
import { roiApi, type TimeRange } from "@/lib/api-client"

interface ROITrendsProps {
  range?: TimeRange
}

export function ROITrends({ range = "30d" }: ROITrendsProps) {
  const { user } = useUser()
  const [trendsData, setTrendsData] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user) return
    
    setLoading(true)
    roiApi.roiTrends(user.id, range)
      .then((response) => {
        const formattedData = response.rows?.map((item: any) => ({
          date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
          roi: parseFloat(item.roi) || 0,
          benchmark: parseFloat(item.roi) * 0.85 || 0 // Simulated benchmark
        })) || []
        setTrendsData(formattedData)
      })
      .catch((error) => {
        console.error('Failed to fetch ROI trends:', error)
        setTrendsData([])
      })
      .finally(() => {
        setLoading(false)
      })
  }, [user, range])

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>ROI Trends</CardTitle>
          <CardDescription>Return on investment over time vs industry benchmark</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-[300px] flex items-center justify-center">
            <div className="text-muted-foreground">Loading...</div>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>ROI Trends</CardTitle>
        <CardDescription>Return on investment over time vs industry benchmark</CardDescription>
      </CardHeader>
      <CardContent>
        {trendsData.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={trendsData} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="roiGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.1}/>
                </linearGradient>
                <linearGradient id="benchmarkGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#64748b" stopOpacity={0.6}/>
                  <stop offset="95%" stopColor="#64748b" stopOpacity={0.1}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" strokeOpacity={0.5} />
              <XAxis 
                dataKey="date" 
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 12, fill: '#64748b' }}
              />
              <YAxis 
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 12, fill: '#64748b' }}
                tickFormatter={(value) => `${value}%`}
              />
              <Tooltip 
                contentStyle={{
                  backgroundColor: '#1e293b',
                  border: 'none',
                  borderRadius: '12px',
                  boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
                  color: '#ffffff'
                }}
                formatter={(value: any, name: string) => [
                  `${Number(value).toFixed(1)}%`, 
                  name === 'roi' ? 'Your ROI' : 'Industry Benchmark'
                ]}
                labelStyle={{ color: '#94a3b8' }}
              />
              <Area 
                type="monotone" 
                dataKey="benchmark" 
                stroke="#64748b" 
                strokeWidth={2}
                strokeDasharray="8 4"
                fill="url(#benchmarkGradient)"
                name="benchmark"
                dot={false}
              />
              <Area 
                type="monotone" 
                dataKey="roi" 
                stroke="#8b5cf6" 
                strokeWidth={3}
                fill="url(#roiGradient)"
                name="roi"
                dot={{ fill: '#8b5cf6', strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, fill: '#8b5cf6', stroke: '#ffffff', strokeWidth: 2 }}
              />
            </AreaChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-[300px] flex items-center justify-center">
            <div className="text-muted-foreground">No data available</div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
