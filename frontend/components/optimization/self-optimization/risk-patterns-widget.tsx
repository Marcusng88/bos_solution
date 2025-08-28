"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useApiClient, handleApiError } from "@/lib/api-client"
import { Activity, TrendingUp, AlertTriangle, Shield, Eye } from "lucide-react"

interface OverspendingPrediction {
  campaign_name: string
  overspend_risk: 'low' | 'medium' | 'high' | 'critical'
  risk_score: number
  current_spend: number
  current_budget: number
  net_profit: number
  budget_utilization: number
}

export function RiskPatternsWidget() {
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



  const getSeverityColor = (severity: string, resolved: boolean) => {
    if (resolved) return 'text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700'
    
    switch (severity) {
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

  const getPatternIcon = (patternType: string) => {
    switch (patternType) {
      case 'overspend':
        return <AlertTriangle className="h-4 w-4" />
      case 'spending_spike':
        return <TrendingUp className="h-4 w-4" />
      case 'performance_decline':
        return <Activity className="h-4 w-4" />
      default:
        return <Eye className="h-4 w-4" />
    }
  }



  const criticalCount = predictions.filter(p => p.overspend_risk === 'critical').length
  const highCount = predictions.filter(p => p.overspend_risk === 'high').length
  const mediumCount = predictions.filter(p => p.overspend_risk === 'medium').length
  const totalRisks = predictions.length

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Risk Patterns</CardTitle>
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
            <Activity className="h-5 w-5" />
            Risk Patterns
          </CardTitle>
          {totalRisks > 0 && (
            <Badge variant="destructive" className="rounded-full">
              {totalRisks}
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent>
        {predictions.length === 0 ? (
          <div className="text-center py-8">
            <Shield className="h-12 w-12 text-green-500 mx-auto mb-3" />
            <p className="text-sm text-muted-foreground">No risk patterns detected</p>
            <p className="text-xs text-muted-foreground">Your campaigns are performing optimally!</p>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Risk Summary */}
            <div className="grid grid-cols-3 gap-3 mb-4">
              <div className="text-center p-3 rounded-lg bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-800">
                <div className="text-2xl font-bold text-red-600 dark:text-red-400">{criticalCount}</div>
                <div className="text-xs text-red-700 dark:text-red-300">Critical</div>
              </div>
              <div className="text-center p-3 rounded-lg bg-orange-50 dark:bg-orange-950/20 border border-orange-200 dark:border-orange-800">
                <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">{highCount}</div>
                <div className="text-xs text-orange-700 dark:text-orange-300">High</div>
              </div>
              <div className="text-center p-3 rounded-lg bg-yellow-50 dark:bg-yellow-950/20 border border-yellow-200 dark:border-yellow-800">
                <div className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">{mediumCount}</div>
                <div className="text-xs text-yellow-700 dark:text-yellow-300">Medium</div>
              </div>
            </div>
            
            {/* Campaign List */}
            <ScrollArea className="h-60">
              <div className="space-y-3">
                {predictions
                  .sort((a, b) => {
                    const severityOrder = { critical: 4, high: 3, medium: 2, low: 1 }
                    return severityOrder[b.overspend_risk] - severityOrder[a.overspend_risk]
                  })
                  .map((prediction, index) => (
                  <div
                    key={index}
                    className={`p-3 rounded-lg border transition-all duration-200 ${getSeverityColor(prediction.overspend_risk, false)}`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-start gap-2 flex-1">
                        {getPatternIcon('overspend')}
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
          </div>
        )}
      </CardContent>
    </Card>
  )
}
