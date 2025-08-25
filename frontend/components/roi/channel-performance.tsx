"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts"
import { useEffect, useState } from "react"
import { useUser } from "@clerk/nextjs"
import { roiApi, type TimeRange } from "@/lib/api-client"

interface ChannelPerformanceProps {
  range?: TimeRange
}

export function ChannelPerformance({ range = "30d" }: ChannelPerformanceProps) {
  const { user } = useUser()
  const [rows, setRows] = useState<any[]>([])
  
  // Professional color palette for different platforms
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
    roiApi.channelPerformance(user.id, range).then((res) => {
      // More flexible platform matching
      const filteredRows = (res.rows || []).filter((row: any) => {
        const platform = row.platform?.toLowerCase();
        return ['facebook', 'instagram', 'youtube'].includes(platform);
      });

      // Add debug logging
      console.log("🔍 Raw channel performance data:", res.rows);
      console.log("🔍 Filtered rows:", filteredRows);
      setRows(filteredRows);
    }).catch(() => setRows([]))
  }, [user, range])
  return (
    <Card>
      <CardHeader>
        <CardTitle>Channel Performance</CardTitle>
        <CardDescription>
          {range === "7d" ? "Last 7 days ROI by channel" :
           range === "30d" ? "Last 30 days ROI by channel" :
           range === "90d" ? "Last 90 days ROI by channel" :
           range === "1y" ? "Last year ROI by channel" :
           "ROI and efficiency by marketing channel"}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart 
            data={rows.map(r => ({ channel: r.platform, roi: Number(r.avg_roi||0) }))}
            margin={{ top: 20, right: 30, left: 0, bottom: 5 }}
          >
            <defs>
              {rows.map((r, index) => (
                <linearGradient key={r.platform} id={`gradient-${index}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={getColor(r.platform, index)} stopOpacity={0.9}/>
                  <stop offset="95%" stopColor={getColor(r.platform, index)} stopOpacity={0.4}/>
                </linearGradient>
              ))}
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" strokeOpacity={0.5} />
            <XAxis 
              dataKey="channel" 
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
                backgroundColor: '#ffffff',
                border: '1px solid #e2e8f0',
                borderRadius: '12px',
                boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
                color: '#1f2937'
              }}
              formatter={(value: any) => [`${Number(value).toFixed(1)}%`, "ROI"]}
            />
            <Bar 
              dataKey="roi" 
              radius={[8, 8, 0, 0]}
              stroke="#ffffff"
              strokeWidth={2}
            >
              {rows.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={`url(#gradient-${index})`} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>

        <div className="mt-6 space-y-3">
          {rows.map((channel, index) => (
            <div key={index} className="flex items-center justify-between p-4 bg-gradient-to-r from-slate-50 to-slate-100 border border-slate-200 rounded-xl hover:shadow-md transition-all duration-200">
              <div className="flex items-center gap-4">
                <div 
                  className="w-4 h-4 rounded-full shadow-sm"
                  style={{ backgroundColor: getColor(channel.platform, index) }}
                ></div>
                <div>
                  <p className="font-semibold text-slate-900">{channel.platform}</p>
                  <p className="text-sm text-slate-600">${Number(channel.spend||channel.revenue||0).toLocaleString()} metrics</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="text-right">
                  <Badge 
                    variant={Number(channel.avg_roi||0) >= 400 ? "default" : Number(channel.avg_roi||0) >= 300 ? "secondary" : "outline"}
                    className="font-semibold px-3 py-1"
                  >
                    {Number(channel.avg_roi||0).toFixed(0)}% ROI
                  </Badge>
                  <div className="flex items-center gap-2 mt-2">
                    <div className="w-20 bg-slate-200 rounded-full h-2 overflow-hidden">
                      <div 
                        className="h-full rounded-full transition-all duration-500"
                        style={{ 
                          width: `${Math.min(100, Number(channel.efficiency_score||0))}%`,
                          backgroundColor: getColor(channel.platform, index)
                        }}
                      ></div>
                    </div>
                    <span className="text-xs text-slate-600 font-medium">{Number(channel.efficiency_score||0).toFixed(0)}%</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
