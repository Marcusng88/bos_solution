"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { useApiClient, handleApiError } from "@/lib/api-client"
import { DollarSign, TrendingUp } from "lucide-react"

interface CampaignData {
  id: number
  name: string
  spend: number
  budget: number
  ongoing: string
  net_profit: number
}

interface CampaignBudgetData {
  name: string
  spend: number
  budget: number
  ongoing: string
  budget_utilization: number
  remaining_budget: number
  net_profit: number
}

export function BudgetDashboard() {
  const [campaigns, setCampaigns] = useState<CampaignBudgetData[]>([])
  const [loading, setLoading] = useState(true)
  const [overallStats, setOverallStats] = useState({
    totalSpend: 0,
    totalBudget: 0,
    overallUtilization: 0,
    ongoingCount: 0
  })
  
  const { apiClient, userId } = useApiClient()

  useEffect(() => {
    fetchBudgetData()
  }, [])

  const fetchBudgetData = async () => {
    try {
      const campaignData = await apiClient.getCampaigns(userId) as CampaignData[]
      
      const budgetData: CampaignBudgetData[] = campaignData.map((campaign: CampaignData) => {
        const spend = campaign.spend || 0
        const budget = campaign.budget || 0
        const budget_utilization = budget > 0 ? (spend / budget) * 100 : 0
        const remaining_budget = budget - spend
        
        return {
          name: campaign.name,
          spend,
          budget,
          ongoing: campaign.ongoing || 'No',
          budget_utilization,
          remaining_budget,
          net_profit: campaign.net_profit || 0
        }
      })
      
      const ongoingCampaigns = budgetData.filter(campaign => campaign.ongoing === 'Yes')
      setCampaigns(ongoingCampaigns)
      
      const totalSpend = ongoingCampaigns.reduce((sum, c) => sum + c.spend, 0)
      const totalBudget = ongoingCampaigns.reduce((sum, c) => sum + c.budget, 0)
      const overallUtilization = totalBudget > 0 ? (totalSpend / totalBudget) * 100 : 0
      
      setOverallStats({
        totalSpend,
        totalBudget,
        overallUtilization,
        ongoingCount: ongoingCampaigns.length
      })
      
    } catch (error) {
      console.error('Failed to fetch budget data:', handleApiError(error))
    } finally {
      setLoading(false)
    }
  }

  const getUtilizationColor = (utilization: number) => {
    if (utilization >= 95) return 'text-red-600'
    if (utilization >= 85) return 'text-orange-600'
    if (utilization >= 75) return 'text-yellow-600'
    return 'text-green-600'
  }

  const getUtilizationBadge = (utilization: number) => {
    if (utilization >= 95) return { label: 'Critical', color: 'bg-red-500 dark:bg-red-600 text-white' }
    if (utilization >= 85) return { label: 'High', color: 'bg-orange-500 dark:bg-orange-600 text-white' }
    if (utilization >= 75) return { label: 'Warning', color: 'bg-yellow-500 dark:bg-yellow-600 text-black' }
    return { label: 'Healthy', color: 'bg-green-500 dark:bg-green-600 text-white' }
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Budget Dashboard</CardTitle>
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
    <div className="space-y-6">
      {/* Overall Budget Utilization */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <DollarSign className="h-5 w-5" />
            Overall Budget Utilization
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm text-muted-foreground mb-2">
                <span>0%</span>
                <span>50%</span>
                <span>100%</span>
              </div>
              <Progress 
                value={overallStats.overallUtilization} 
                className="h-3"
              />
            </div>
            
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-lg font-semibold text-blue-600 dark:text-blue-400">
                  {overallStats.ongoingCount}
                </div>
                <div className="text-xs text-muted-foreground">Ongoing Campaigns</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-semibold text-green-600 dark:text-green-400">
                  {overallStats.overallUtilization.toFixed(1)}%
                </div>
                <div className="text-xs text-muted-foreground">Utilized</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-semibold text-purple-600 dark:text-purple-400">
                  ${(overallStats.totalBudget - overallStats.totalSpend).toLocaleString()}
                </div>
                <div className="text-xs text-muted-foreground">Remaining</div>
              </div>
            </div>
            
            <div className="text-center p-3 bg-muted rounded-lg">
              <div className="text-sm text-muted-foreground">Current Spend / Total Budget</div>
              <div className="text-lg font-semibold text-foreground">
                ${overallStats.totalSpend.toLocaleString()} / ${overallStats.totalBudget.toLocaleString()}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Individual Campaign Budget Status */}
      <Card>
        <CardHeader>
          <CardTitle>Campaign Budget Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {campaigns.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                No ongoing campaigns found.
              </div>
            ) : (
              campaigns.map((campaign) => {
                const utilizationBadge = getUtilizationBadge(campaign.budget_utilization)
                
                return (
                  <div key={campaign.name} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h4 className="font-semibold text-lg">{campaign.name}</h4>
                        <div className="flex items-center gap-2 mt-1">
                          <Badge className={utilizationBadge.color}>
                            {utilizationBadge.label}
                          </Badge>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm text-muted-foreground">Budget Utilization</div>
                        <div className={`text-lg font-semibold ${getUtilizationColor(campaign.budget_utilization)}`}>
                          {campaign.budget_utilization.toFixed(1)}%
                        </div>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                      <div className="text-center p-3 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
                        <div className="text-lg font-bold text-blue-600 dark:text-blue-400">
                          ${campaign.spend.toLocaleString()}
                        </div>
                        <div className="text-xs text-muted-foreground">Spent</div>
                      </div>
                      <div className="text-center p-3 bg-green-50 dark:bg-green-950/20 rounded-lg">
                        <div className="text-lg font-bold text-green-600 dark:text-green-400">
                          ${campaign.budget.toLocaleString()}
                        </div>
                        <div className="text-xs text-muted-foreground">Budget</div>
                      </div>
                      <div className="text-center p-3 bg-purple-50 dark:bg-purple-950/20 rounded-lg">
                        <div className="text-lg font-bold text-purple-600 dark:text-purple-400">
                          ${campaign.remaining_budget.toLocaleString()}
                        </div>
                        <div className="text-xs text-muted-foreground">Remaining</div>
                      </div>
                      <div className="text-center p-3 bg-orange-50 dark:bg-orange-950/20 rounded-lg">
                        <div className={`text-lg font-bold ${campaign.net_profit >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                          ${campaign.net_profit.toLocaleString()}
                        </div>
                        <div className="text-xs text-muted-foreground">Net Profit</div>
                      </div>
                    </div>
                    
                    <div className="mb-3">
                      <div className="flex justify-between text-sm text-muted-foreground mb-1">
                        <span>Budget Utilization</span>
                        <span>{campaign.budget_utilization.toFixed(1)}%</span>
                      </div>
                      <Progress 
                        value={campaign.budget_utilization} 
                        className="h-2"
                      />
                    </div>
                  </div>
                )
              })
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
