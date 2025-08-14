"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"

const channelData = [
  { channel: "Google Ads", roi: 420, spend: 18500, revenue: 77700, efficiency: 92 },
  { channel: "Facebook Ads", roi: 380, spend: 12800, revenue: 48640, efficiency: 88 },
  { channel: "Instagram", roi: 310, spend: 6200, revenue: 19220, efficiency: 75 },
  { channel: "LinkedIn", roi: 290, spend: 4100, revenue: 11890, efficiency: 71 },
  { channel: "Twitter", roi: 350, spend: 2400, revenue: 8400, efficiency: 82 },
]

export function ChannelPerformance() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Channel Performance</CardTitle>
        <CardDescription>ROI and efficiency by marketing channel</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={channelData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="channel" />
            <YAxis />
            <Tooltip formatter={(value) => [`${value}%`, "ROI"]} />
            <Bar dataKey="roi" fill="#3b82f6" />
          </BarChart>
        </ResponsiveContainer>

        <div className="mt-6 space-y-4">
          {channelData.map((channel, index) => (
            <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                <div>
                  <p className="font-medium">{channel.channel}</p>
                  <p className="text-sm text-muted-foreground">
                    ${channel.spend.toLocaleString()} spend → ${channel.revenue.toLocaleString()} revenue
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="text-right">
                  <Badge variant={channel.roi >= 400 ? "default" : channel.roi >= 300 ? "secondary" : "outline"}>
                    {channel.roi}% ROI
                  </Badge>
                  <div className="flex items-center gap-2 mt-1">
                    <Progress value={channel.efficiency} className="w-16 h-2" />
                    <span className="text-xs text-muted-foreground">{channel.efficiency}%</span>
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
