"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { useApiClient, handleApiError } from "@/lib/api-client"
import { TrendingUp, AlertTriangle, Clock, Target, DollarSign } from "lucide-react"

interface OverspendingPrediction {
  campaign_name: string
  current_spend: number
  current_budget: number
  predicted_spend: number
  overspend_risk: 'low' | 'medium' | 'high' | 'critical'
  days_until_overspend: number
  confidence_score: number
  risk_factors: string[]
}

export function OverspendingPredictionWidget() {
  const [predictions, setPredictions] = useState<OverspendingPrediction[]>([])
  const [loading, setLoading] = useState(true)
  const { apiClient, userId } = useApiClient()

  useEffect(() => {
    fetchPredictions()
  }, [])

  const fetchPredictions = async () => {
    try {
      // For now, we'll simulate predictions based on campaign data
      // In a real implementation, this would call a prediction API
      const campaigns = await apiClient.getCampaigns(userId)
      
      // Generate predictions based on current spend vs budget
      const predictionsData: OverspendingPrediction[] = campaigns
        .filter((campaign: any) => campaign.ongoing === 'Yes')
        .map((campaign: any) => {
          const currentSpend = campaign.spend || 0
          const currentBudget = campaign.budget || 0
          const utilization = currentBudget > 0 ? (currentSpend / currentBudget) * 100 : 0
          
          // Calculate risk based on utilization and spending patterns
          let overspendRisk: 'low' | 'medium' | 'high' | 'critical' = 'low'
          let daysUntilOverspend = 30
          let confidenceScore = 0.5
          let riskFactors: string[] = []
          
          if (utilization > 90) {
            overspendRisk = 'critical'
            daysUntilOverspend = Math.max(1, Math.floor((100 - utilization) / 3))
            confidenceScore = 0.95
            riskFactors.push('High budget utilization')
          } else if (utilization > 75) {
            overspendRisk = 'high'
            daysUntilOverspend = Math.max(3, Math.floor((100 - utilization) / 2))
            confidenceScore = 0.8
            riskFactors.push('Above 75% budget utilization')
          } else if (utilization > 50) {
            overspendRisk = 'medium'
            daysUntilOverspend = Math.max(7, Math.floor((100 - utilization) / 1.5))
            confidenceScore = 0.6
            riskFactors.push('Moderate budget utilization')
          }
          
          // Add additional risk factors
          if (currentSpend > 0 && currentBudget > 0) {
            const dailySpend = currentSpend / 30 // Assume 30-day month
            const remainingBudget = currentBudget - currentSpend
            const daysLeft = remainingBudget / dailySpend
            
            if (daysLeft < 10) {
              riskFactors.push('Rapid spending rate')
              overspendRisk = overspendRisk === 'low' ? 'medium' : overspendRisk
              confidenceScore = Math.min(0.9, confidenceScore + 0.2)
            }
          }
          
          return {
            campaign_name: campaign.name,
            current_spend: currentSpend,
            current_budget: currentBudget,
            predicted_spend: currentBudget * 1.1, // Simple prediction
            overspend_risk: overspendRisk,
            days_until_overspend: daysUntilOverspend,
            confidence_score: confidenceScore,
            risk_factors: riskFactors
          }
        })
        .filter(prediction => prediction.overspend_risk !== 'low')
        .sort((a, b) => {
          const riskOrder = { 'critical': 4, 'high': 3, 'medium': 2, 'low': 1 }
          return riskOrder[b.overspend_risk] - riskOrder[a.overspend_risk]
        })
      
      setPredictions(predictionsData)
    } catch (error) {
      console.error('Failed to fetch predictions:', handleApiError(error))
      setPredictions([])
    } finally {
      setLoading(false)
    }
  }

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'critical':
        return 'bg-red-500 text-white'
      case 'high':
        return 'bg-orange-500 text-white'
      case 'medium':
        return 'bg-yellow-500 text-black'
      default:
        return 'bg-green-500 text-white'
    }
  }

  const getRiskIcon = (risk: string) => {
    switch (risk) {
      case 'critical':
        return <AlertTriangle className="h-4 w-4" />
      case 'high':
        return <TrendingUp className="h-4 w-4" />
      case 'medium':
        return <Clock className="h-4 w-4" />
      default:
        return <Target className="h-4 w-4" />
    }
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Overspending Predictions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (predictions.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Overspending Predictions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <Target className="h-12 w-12 text-green-500 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Overspending Risks Detected</h3>
            <p className="text-gray-500">All campaigns are currently within budget limits.</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-orange-500" />
            Overspending Predictions
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {predictions.map((prediction, index) => (
              <div key={index} className="p-4 rounded-lg border border-gray-200 hover:border-gray-300 transition-colors">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h4 className="font-medium text-gray-900">{prediction.campaign_name}</h4>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge className={getRiskColor(prediction.overspend_risk)}>
                        {getRiskIcon(prediction.overspend_risk)}
                        <span className="ml-1 capitalize">{prediction.overspend_risk} Risk</span>
                      </Badge>
                      <span className="text-sm text-gray-500">
                        {prediction.days_until_overspend} days until overspend
                      </span>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-gray-500">Confidence</div>
                    <div className="text-lg font-semibold text-blue-600">
                      {(prediction.confidence_score * 100).toFixed(0)}%
                    </div>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4 mb-3">
                  <div>
                    <div className="text-sm text-gray-500">Current Spend</div>
                    <div className="text-lg font-semibold text-gray-900">
                      ${prediction.current_spend.toLocaleString()}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-500">Budget</div>
                    <div className="text-lg font-semibold text-gray-900">
                      ${prediction.current_budget.toLocaleString()}
                    </div>
                  </div>
                </div>
                
                <div className="mb-3">
                  <div className="flex justify-between text-sm text-gray-500 mb-1">
                    <span>Budget Utilization</span>
                    <span>{((prediction.current_spend / prediction.current_budget) * 100).toFixed(1)}%</span>
                  </div>
                  <Progress 
                    value={(prediction.current_spend / prediction.current_budget) * 100} 
                    className="h-2"
                  />
                </div>
                
                {prediction.risk_factors.length > 0 && (
                  <div>
                    <div className="text-sm text-gray-500 mb-2">Risk Factors:</div>
                    <div className="flex flex-wrap gap-2">
                      {prediction.risk_factors.map((factor, factorIndex) => (
                        <Badge key={factorIndex} variant="outline" className="text-xs">
                          {factor}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
