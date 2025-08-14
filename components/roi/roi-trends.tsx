"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"

const roiData = [
  { month: "Jan", roi: 245, benchmark: 220 },
  { month: "Feb", roi: 278, benchmark: 225 },
  { month: "Mar", roi: 265, benchmark: 230 },
  { month: "Apr", roi: 312, benchmark: 235 },
  { month: "May", roi: 298, benchmark: 240 },
  { month: "Jun", roi: 324, benchmark: 245 },
]

export function ROITrends() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>ROI Trends</CardTitle>
        <CardDescription>Return on investment over time vs industry benchmark</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={roiData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip formatter={(value) => [`${value}%`, ""]} />
            <Line type="monotone" dataKey="roi" stroke="#3b82f6" strokeWidth={3} name="Your ROI" />
            <Line
              type="monotone"
              dataKey="benchmark"
              stroke="#94a3b8"
              strokeWidth={2}
              strokeDasharray="5 5"
              name="Industry Benchmark"
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
