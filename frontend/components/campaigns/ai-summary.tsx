"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Sparkles, TrendingUp, AlertTriangle, CheckCircle, RefreshCw } from "lucide-react"

interface AISummaryProps {
  timeRange: string
}

const getTimeRangeText = (range: string) => {
  switch (range) {
    case "24h":
      return "the last 24 hours"
    case "7d":
      return "the last 7 days"
    case "30d":
      return "the last 30 days"
    case "90d":
      return "the last 90 days"
    default:
      return "the selected period"
  }
}

export function AISummary({ timeRange }: AISummaryProps) {
  const timeText = getTimeRangeText(timeRange)

  const insights = [
    {
      type: "positive",
      icon: TrendingUp,
      title: "Strong Performance",
      description: "Your Facebook campaign 'Summer Sale 2024' is performing 23% above expectations with a CTR of 3.2%.",
    },
    {
      type: "warning",
      icon: AlertTriangle,
      title: "Attention Needed",
      description:
        "Instagram campaign 'Product Launch' has a high cost per conversion ($45). Consider adjusting targeting.",
    },
    {
      type: "success",
      icon: CheckCircle,
      title: "Goal Achieved",
      description:
        "LinkedIn campaign 'B2B Outreach' has exceeded its conversion goal by 15% while staying under budget.",
    },
  ]

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-blue-600" />
            <CardTitle>AI Performance Summary</CardTitle>
          </div>
          <Button variant="outline" size="sm">
            <RefreshCw className="mr-2 h-3 w-3" />
            Refresh Analysis
          </Button>
        </div>
        <CardDescription>AI-powered insights and recommendations for {timeText}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Main Summary */}
        <div className="p-4 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
          <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">Overall Performance</h3>
          <p className="text-blue-800 dark:text-blue-200 text-sm leading-relaxed">
            Your campaigns performed well during {timeText}, generating <strong>1,234 conversions</strong> from{" "}
            <strong>24,567 clicks</strong> with a total spend of <strong>$12,847</strong>. The average cost per
            conversion decreased by <strong>8%</strong> compared to the previous period, indicating improved efficiency.
            Your top-performing campaign was "Summer Sale 2024" with a conversion rate of <strong>5.8%</strong>.
          </p>
        </div>

        {/* Key Insights */}
        <div className="space-y-4">
          <h4 className="font-medium">Key Insights & Recommendations</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {insights.map((insight, index) => {
              const Icon = insight.icon
              const colorClasses = {
                positive: "border-green-200 bg-green-50 dark:bg-green-950/20",
                warning: "border-yellow-200 bg-yellow-50 dark:bg-yellow-950/20",
                success: "border-blue-200 bg-blue-50 dark:bg-blue-950/20",
              }
              const iconColors = {
                positive: "text-green-600",
                warning: "text-yellow-600",
                success: "text-blue-600",
              }
              return (
                <div key={index} className={`p-4 rounded-lg border ${colorClasses[insight.type]}`}>
                  <div className="flex items-start gap-3">
                    <Icon className={`h-5 w-5 mt-0.5 ${iconColors[insight.type]}`} />
                    <div className="space-y-1">
                      <h5 className="font-medium text-sm">{insight.title}</h5>
                      <p className="text-xs text-muted-foreground leading-relaxed">{insight.description}</p>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="flex items-center gap-2 pt-4 border-t">
          <span className="text-sm text-muted-foreground">Recommended actions:</span>
          <Badge variant="outline" className="text-xs">
            Increase budget for Summer Sale
          </Badge>
          <Badge variant="outline" className="text-xs">
            Pause underperforming ads
          </Badge>
          <Badge variant="outline" className="text-xs">
            A/B test new creatives
          </Badge>
        </div>
      </CardContent>
    </Card>
  )
}
