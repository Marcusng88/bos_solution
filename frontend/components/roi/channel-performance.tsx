"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"

const channelData = [
  { channel: "Facebook Ads", roi: 410, spend: 21300, revenue: 87300, efficiency: 91 },
  { channel: "Instagram", roi: 340, spend: 11200, revenue: 38080, efficiency: 80 },
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
