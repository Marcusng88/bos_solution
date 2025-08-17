"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useApiClient, handleApiClient } from "@/lib/api-client"
import { TrendingUp, AlertTriangle, Clock, Target, DollarSign, TrendingDown, Pause, DollarSign as DollarSignIcon } from "lucide-react"

interface OverspendingPrediction {
  campaign_name: string
  current_spend: number
  current_budget: number
  net_profit: number
  overspend_risk: 'low' | 'medium' | 'high' | 'critical'
  days_until_overspend: number
  risk_factors: string[]
  budget_utilization: number
  profit_margin: number
  ctr?: number
  cpc?: number
  conversions?: number
  impressions?: number
  risk_score: number
  performance_score?: number
  performance_category?: string
}

export function OverspendingPredictionWidget() {
  const [predictions, setPredictions] = useState<OverspendingPrediction[]>([])
  const [loading, setLoading] = useState(true)
  const [reallocatingCampaign, setReallocatingCampaign] = useState<string | null>(null)
  const [newBudget, setNewBudget] = useState<string>('')
  const { apiClient, userId } = useApiClient()

  useEffect(() => {
    fetchPredictions()
  }, [])

  const fetchPredictions = async () => {
    try {
      const predictionsData = await apiClient.getOverspendingPredictions(userId)
      setPredictions(predictionsData)
    } catch (error) {
      console.error('Failed to fetch predictions:', handleApiClient(error))
      setPredictions([])
    } finally {
      setLoading(false)
    }
  }

  const handlePauseCampaign = async (campaignName: string) => {
    try {
      // Update the ongoing field from 'Yes' to 'No' in the database
      await apiClient.updateCampaignStatus(userId, campaignName, 'No')
      // Refresh predictions
      await fetchPredictions()
    } catch (error) {
      console.error('Failed to pause campaign:', error)
    }
  }

  const handleReallocateBudget = async (campaignName: string) => {
    if (!newBudget || parseFloat(newBudget) <= 0) return
    
    try {
      // Update the budget field in the database
      await apiClient.updateCampaignBudget(userId, campaignName, parseFloat(newBudget))
      // Reset form and refresh predictions
      setReallocatingCampaign(null)
      setNewBudget('')
      await fetchPredictions()
    } catch (error) {
      console.error('Failed to reallocate budget:', error)
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

  const getGlowClass = (risk: string) => {
    switch (risk) {
      case 'critical':
        return 'shadow-lg shadow-red-500/50 border-red-500/30'
      case 'high':
        return 'shadow-lg shadow-orange-500/50 border-orange-500/30'
      case 'medium':
        return 'shadow-lg shadow-yellow-500/50 border-yellow-500/30'
      default:
        return 'shadow-md border-gray-200'
    }
  }

  const getCriticalGlowClass = (risk: string) => {
    if (risk === 'critical') {
      return 'animate-pulse animate-duration-1000'
    }
    return ''
  }

  const getProfitColor = (profitMargin: number) => {
    if (profitMargin > 20) return 'text-green-600'
    if (profitMargin > 10) return 'text-green-500'
    if (profitMargin > 0) return 'text-yellow-600'
    if (profitMargin > -10) return 'text-orange-500'
    return 'text-red-600'
  }

  const getProfitIcon = (profitMargin: number) => {
    if (profitMargin > 0) return <TrendingUp className="h-4 w-4" />
    return <TrendingDown className="h-4 w-4" />
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
            <p className="text-gray-500">All campaigns are currently within budget limits and performing well.</p>
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
            Enhanced Overspending Predictions
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {predictions.map((prediction, index) => (
                                            <div 
                 key={index} 
                 className={`p-4 rounded-lg border transition-all duration-300 hover:scale-[1.02] ${getGlowClass(prediction.overspend_risk)}`}
               >
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
                    <div className="text-sm text-gray-500">Risk Score</div>
                    <div className="text-lg font-semibold text-red-600">
                      {(prediction.risk_score * 100).toFixed(0)}%
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

                {/* Net Profit Section */}
                <div className="grid grid-cols-2 gap-4 mb-3">
                  <div>
                    <div className="text-sm text-gray-500">Net Profit</div>
                    <div className={`text-lg font-semibold flex items-center gap-1 ${getProfitColor(prediction.profit_margin)}`}>
                      {getProfitIcon(prediction.profit_margin)}
                      ${prediction.net_profit.toLocaleString()}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-500">Profit Margin</div>
                    <div className={`text-lg font-semibold ${getProfitColor(prediction.profit_margin)}`}>
                      {prediction.profit_margin.toFixed(1)}%
                    </div>
                  </div>
                </div>
                
                <div className="mb-3">
                  <div className="flex justify-between text-sm text-gray-500 mb-1">
                    <span>Budget Utilization</span>
                    <span>{prediction.budget_utilization.toFixed(1)}%</span>
                  </div>
                  <Progress 
                    value={prediction.budget_utilization} 
                    className="h-2"
                  />
                </div>

                {/* Performance Metrics */}
                <div className="grid grid-cols-3 gap-4 mb-3 p-3 bg-gray-50 rounded-lg">
                  <div className="text-center">
                    <div className="text-xs text-gray-500">CTR</div>
                    <div className="text-sm font-semibold">{prediction.ctr?.toFixed(2) || 'N/A'}%</div>
                  </div>
                  <div className="text-center">
                    <div className="text-xs text-gray-500">CPC</div>
                    <div className="text-sm font-semibold">${prediction.cpc?.toFixed(2) || 'N/A'}</div>
                  </div>
                  <div className="text-center">
                    <div className="text-xs text-gray-500">Conv. Rate</div>
                    <div className="text-sm font-semibold">{prediction.conversions && prediction.impressions ? ((prediction.conversions / prediction.impressions) * 100).toFixed(2) : 'N/A'}%</div>
                  </div>
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

                {/* Action Buttons */}
                <div className="flex gap-3 mt-4 pt-4 border-t border-gray-200">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handlePauseCampaign(prediction.campaign_name)}
                    className="flex items-center gap-2 text-red-600 border-red-200 hover:bg-red-50"
                  >
                    <Pause className="h-4 w-4" />
                    Pause Campaign
                  </Button>
                  
                  {reallocatingCampaign === prediction.campaign_name ? (
                    <div className="flex gap-2">
                      <Input
                        type="number"
                        placeholder="New budget amount"
                        value={newBudget}
                        onChange={(e) => setNewBudget(e.target.value)}
                        className="w-32"
                      />
                      <Button
                        size="sm"
                        onClick={() => handleReallocateBudget(prediction.campaign_name)}
                        className="flex items-center gap-2"
                      >
                        <DollarSignIcon className="h-4 w-4" />
                        Update
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          setReallocatingCampaign(null)
                          setNewBudget('')
                        }}
                      >
                        Cancel
                      </Button>
                    </div>
                  ) : (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setReallocatingCampaign(prediction.campaign_name)}
                      className="flex items-center gap-2 text-blue-600 border-blue-200 hover:bg-blue-50"
                    >
                      <DollarSignIcon className="h-4 w-4" />
                      Reallocate Budget
                    </Button>
                                       )}
                 </div>
               </div>
             ))}
           </div>
        </CardContent>
      </Card>
    </div>
  )
}
