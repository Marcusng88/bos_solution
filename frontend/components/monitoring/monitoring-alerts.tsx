"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { TrendingUp, MessageSquare, DollarSign, Users } from "lucide-react"

const alerts = [
  {
    id: 1,
    type: "content",
    priority: "high",
    competitor: "Nike",
    title: "New Product Launch Campaign",
    description: "Nike launched a major campaign for their new Air Max series with 500% increase in social mentions",
    timestamp: "5 minutes ago",
    icon: TrendingUp,
    action: "Create Response Campaign",
  },
  {
    id: 2,
    type: "pricing",
    priority: "medium",
    competitor: "Adidas",
    title: "Price Drop Alert",
    description: "Adidas reduced prices on running shoes by 25% - potential threat to our market share",
    timestamp: "1 hour ago",
    icon: DollarSign,
    action: "Review Pricing Strategy",
  },
  {
    id: 3,
    type: "social",
    priority: "high",
    competitor: "Puma",
    title: "Viral Content Alert",
    description: "Puma's latest TikTok video gained 2M views in 24 hours - trending hashtag #PumaChallenge",
    timestamp: "3 hours ago",
    icon: MessageSquare,
    action: "Analyze Content Strategy",
  },
  {
    id: 4,
    type: "audience",
    priority: "low",
    competitor: "Under Armour",
    title: "Audience Shift Detected",
    description: "Under Armour showing increased engagement from 25-34 age group (+15% this week)",
    timestamp: "6 hours ago",
    icon: Users,
    action: "Monitor Trend",
  },
]

export function MonitoringAlerts() {
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high":
        return "bg-red-100 text-red-800 border-red-200"
      case "medium":
        return "bg-orange-100 text-orange-800 border-orange-200"
      case "low":
        return "bg-blue-100 text-blue-800 border-blue-200"
      default:
        return "bg-gray-100 text-gray-800 border-gray-200"
    }
  }

  return (
    <div className="space-y-4">
      {alerts.map((alert) => {
        const Icon = alert.icon
        return (
          <Card key={alert.id} className="border-l-4 border-l-blue-500">
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-blue-50 rounded-lg">
                    <Icon className="h-5 w-5 text-blue-600" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <CardTitle className="text-lg">{alert.title}</CardTitle>
                      <Badge className={getPriorityColor(alert.priority)}>{alert.priority}</Badge>
                    </div>
                    <CardDescription className="text-sm text-muted-foreground">
                      {alert.competitor} • {alert.timestamp}
                    </CardDescription>
                  </div>
                </div>
                <Button size="sm">{alert.action}</Button>
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              <p className="text-sm">{alert.description}</p>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
