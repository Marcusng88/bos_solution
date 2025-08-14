"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { AlertTriangle, TrendingUp, Target, Clock, X } from "lucide-react"

export function CompetitorMoveAlerts() {
  const alerts = [
    {
      id: 1,
      competitor: "Nike",
      action: "Launched major video campaign",
      impact: "High",
      urgency: "Immediate",
      description: "Nike increased video ad spend by 150% targeting your key demographics",
      timeDetected: "2 hours ago",
      recommendedAction: "Launch counter-campaign within 48 hours",
      threat: "High",
    },
    {
      id: 2,
      competitor: "Adidas",
      action: "Reduced sustainability messaging",
      impact: "Medium",
      urgency: "This Week",
      description: "30% decrease in eco-friendly content creates market opportunity",
      timeDetected: "1 day ago",
      recommendedAction: "Increase sustainability content by 40%",
      threat: "Low",
    },
    {
      id: 3,
      competitor: "Under Armour",
      action: "Paused major campaigns",
      impact: "Medium",
      urgency: "Next 10 Days",
      description: "Budget reallocation creates keyword bidding opportunity",
      timeDetected: "3 days ago",
      recommendedAction: "Increase bids on shared keywords",
      threat: "Low",
    },
  ]

  return (
    <Card className="border-orange-200 bg-orange-50 dark:border-orange-800 dark:bg-orange-950/20">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-orange-900 dark:text-orange-100">
          <AlertTriangle className="h-5 w-5" />
          Competitor Move Alerts
        </CardTitle>
        <CardDescription className="text-orange-700 dark:text-orange-300">
          Real-time alerts about competitor strategy changes requiring immediate attention
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {alerts.map((alert) => (
            <div
              key={alert.id}
              className="flex items-center justify-between p-3 bg-white dark:bg-gray-800 rounded-lg border"
            >
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2">
                  {alert.threat === "High" ? (
                    <AlertTriangle className="h-4 w-4 text-red-500" />
                  ) : alert.impact === "Medium" ? (
                    <TrendingUp className="h-4 w-4 text-yellow-500" />
                  ) : (
                    <Target className="h-4 w-4 text-green-500" />
                  )}
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium">{alert.competitor}</span>
                      <span className="text-sm text-muted-foreground">{alert.action}</span>
                      <Badge
                        variant={
                          alert.urgency === "Immediate"
                            ? "destructive"
                            : alert.urgency === "This Week"
                              ? "secondary"
                              : "outline"
                        }
                      >
                        {alert.urgency}
                      </Badge>
                    </div>
                    <div className="text-sm text-muted-foreground">{alert.description}</div>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <div className="text-right mr-3">
                  <div className="text-sm font-medium">{alert.recommendedAction}</div>
                  <div className="text-xs text-muted-foreground flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {alert.timeDetected}
                  </div>
                </div>
                <Button size="sm">Act Now</Button>
                <Button variant="ghost" size="sm">
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
