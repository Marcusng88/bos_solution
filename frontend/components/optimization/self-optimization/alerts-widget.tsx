"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useApiClient, handleApiError } from "@/lib/api-client"
import { AlertTriangle, Bell, Clock, CheckCircle, X } from "lucide-react"

interface OptimizationAlert {
  id: string
  campaign_name: string
  alert_type: string
  priority: 'low' | 'medium' | 'high' | 'critical'
  title: string
  message: string
  recommendation: string
  created_at: string
  is_read: boolean
}

interface OverspendingPrediction {
  campaign_name: string
  overspend_risk: 'low' | 'medium' | 'high' | 'critical'
  risk_score: number
  current_spend: number
  current_budget: number
  net_profit: number
  budget_utilization: number
}

export function AlertsWidget() {
  const [predictions, setPredictions] = useState<OverspendingPrediction[]>([])
  const [loading, setLoading] = useState(true)
  const { apiClient, userId } = useApiClient()

  useEffect(() => {
    fetchPredictions()
  }, [])

  const fetchPredictions = async () => {
    try {
      const predictionsData = await apiClient.getOverspendingPredictions(userId)
      setPredictions(predictionsData)
    } catch (error) {
      console.error('Failed to fetch predictions:', handleApiError(error))
    } finally {
      setLoading(false)
    }
  }



  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-950/20 border-red-200 dark:border-red-800'
      case 'high':
        return 'text-orange-600 dark:text-orange-400 bg-orange-50 dark:bg-orange-950/20 border-orange-200 dark:border-orange-800'
      case 'medium':
        return 'text-yellow-600 dark:text-yellow-400 bg-yellow-50 dark:bg-yellow-950/20 border-yellow-200 dark:border-yellow-800'
      default:
        return 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/20 border-blue-200 dark:border-blue-800'
    }
  }

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'critical':
      case 'high':
        return <AlertTriangle className="h-4 w-4" />
      case 'medium':
        return <Clock className="h-4 w-4" />
      default:
        return <Bell className="h-4 w-4" />
    }
  }



  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Optimization Alerts</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5" />
            Optimization Alerts
          </CardTitle>
          {predictions.length > 0 && (
            <Badge variant="destructive" className="rounded-full">
              {predictions.length}
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent>
        {predictions.length === 0 ? (
          <div className="text-center py-8">
            <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-3" />
            <p className="text-sm text-muted-foreground">No active alerts</p>
            <p className="text-xs text-muted-foreground">Your campaigns are running smoothly!</p>
          </div>
        ) : (
          <ScrollArea className="h-80">
            <div className="space-y-3">
              {predictions.map((prediction, index) => (
                <div
                  key={index}
                  className={`p-3 rounded-lg border transition-all duration-200 ${getPriorityColor(prediction.overspend_risk)}`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-start gap-2 flex-1">
                      {getPriorityIcon(prediction.overspend_risk)}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-medium text-sm truncate">{prediction.campaign_name}</h4>
                          <Badge variant="outline" className="text-xs capitalize">
                            {prediction.overspend_risk} Risk
                          </Badge>
                        </div>
                        <div className="text-xs mb-2 space-y-1">
                          <div>Budget: ${prediction.current_budget.toLocaleString()} | Spend: ${prediction.current_spend.toLocaleString()}</div>
                          <div>Utilization: {prediction.budget_utilization.toFixed(1)}% | Risk Score: {(prediction.risk_score * 100).toFixed(0)}%</div>
                          <div className={`font-medium ${prediction.net_profit >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                            Net Profit: ${prediction.net_profit.toLocaleString()}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>
        )}
      </CardContent>
    </Card>
  )
}
