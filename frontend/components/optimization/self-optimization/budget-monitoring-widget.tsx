"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { useApiClient, handleApiError } from "@/lib/api-client"
import { DollarSign, AlertTriangle, CheckCircle, Clock } from "lucide-react"

interface BudgetData {
  campaign_name: string
  date: string
  spend: number
  budget: number
  utilization_pct: number
  status: 'normal' | 'warning' | 'critical'
}

interface BudgetMonitoringWidgetProps {
  detailed?: boolean
}

export function BudgetMonitoringWidget({ detailed = false }: BudgetMonitoringWidgetProps) {
  const [budgetData, setBudgetData] = useState<BudgetData[]>([])
  const [loading, setLoading] = useState(true)
  const { apiClient, userId } = useApiClient()

  useEffect(() => {
    fetchBudgetData()
  }, [])

  const fetchBudgetData = async () => {
    try {
      const monitoringData = await apiClient.getBudgetMonitoring(userId, 7)
      
      // Transform backend data to match frontend interface
      const transformedData = monitoringData.map((item: any) => ({
        campaign_name: item.campaign_name,
        date: item.date,
        spend: parseFloat(item.spend),
        budget: parseFloat(item.budget),
        utilization_pct: parseFloat(item.utilization_pct),
        status: item.status as 'normal' | 'warning' | 'critical'
      }))
      
      setBudgetData(transformedData)
    } catch (error) {
      console.error('Failed to fetch budget data:', handleApiError(error))
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'critical':
        return <AlertTriangle className="h-4 w-4 text-red-500" />
      case 'warning':
        return <Clock className="h-4 w-4 text-orange-500" />
      default:
        return <CheckCircle className="h-4 w-4 text-green-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'critical':
        return 'bg-red-500'
      case 'warning':
        return 'bg-orange-500'
      default:
        return 'bg-green-500'
    }
  }

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'critical':
        return 'destructive'
      case 'warning':
        return 'secondary'
      default:
        return 'default'
    }
  }

  const totalSpend = budgetData.reduce((sum, item) => sum + item.spend, 0)
  const totalBudget = budgetData.reduce((sum, item) => sum + item.budget, 0)
  const overallUtilization = totalBudget > 0 ? (totalSpend / totalBudget) * 100 : 0

  const criticalCount = budgetData.filter(item => item.status === 'critical').length
  const warningCount = budgetData.filter(item => item.status === 'warning').length
  const normalCount = budgetData.filter(item => item.status === 'normal').length

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Budget Monitoring</CardTitle>
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
            <DollarSign className="h-5 w-5" />
            Budget Monitoring
          </CardTitle>
          <Badge variant={overallUtilization > 100 ? 'destructive' : overallUtilization > 80 ? 'secondary' : 'default'}>
            {overallUtilization.toFixed(1)}% Utilized
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Overall Summary */}
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium">Overall Budget Utilization</span>
            <span className="text-sm text-muted-foreground">
              ${totalSpend.toFixed(2)} / ${totalBudget.toFixed(2)}
            </span>
          </div>
          <Progress 
            value={Math.min(overallUtilization, 100)} 
            className="h-2"
          />
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>0%</span>
            <span>50%</span>
            <span>100%</span>
          </div>
        </div>

        {/* Status Summary */}
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-lg font-bold text-green-600">{normalCount}</div>
            <div className="text-xs text-muted-foreground">Healthy</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-orange-600">{warningCount}</div>
            <div className="text-xs text-muted-foreground">Warning</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-red-600">{criticalCount}</div>
            <div className="text-xs text-muted-foreground">Critical</div>
          </div>
        </div>

        {/* Campaign Budget Details */}
        <div className="space-y-3">
          <h4 className="font-medium">Campaign Budget Status</h4>
          <div className="space-y-3">
            {budgetData
              .sort((a, b) => b.utilization_pct - a.utilization_pct)
              .slice(0, detailed ? budgetData.length : 5)
              .map((campaign) => (
              <div key={`${campaign.campaign_name}-${campaign.date}`} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(campaign.status)}
                    <span className="text-sm font-medium">{campaign.campaign_name}</span>
                  </div>
                  <Badge variant={getStatusBadgeVariant(campaign.status)} className="text-xs">
                    {campaign.utilization_pct.toFixed(1)}%
                  </Badge>
                </div>
                <div className="flex items-center space-x-2">
                  <Progress 
                    value={Math.min(campaign.utilization_pct, 100)} 
                    className="flex-1 h-2"
                  />
                  <span className="text-xs text-muted-foreground min-w-[80px]">
                    ${campaign.spend.toFixed(0)}/${campaign.budget.toFixed(0)}
                  </span>
                </div>
                {campaign.status === 'critical' && (
                  <div className="text-xs text-red-600 bg-red-50 p-2 rounded">
                    ⚠️ Budget exceeded by ${(campaign.spend - campaign.budget).toFixed(2)}
                  </div>
                )}
                {campaign.status === 'warning' && campaign.utilization_pct > 80 && (
                  <div className="text-xs text-orange-600 bg-orange-50 p-2 rounded">
                    ⚡ Approaching budget limit
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Real-time Insights */}
        {detailed && (
          <div className="space-y-3">
            <h4 className="font-medium">Real-time Insights</h4>
            <div className="space-y-2">
              <div className="p-3 rounded-lg bg-blue-50 border border-blue-200">
                <div className="text-sm font-medium text-blue-900">Spending Velocity</div>
                <div className="text-xs text-blue-700">
                  Current pace suggests {overallUtilization > 90 ? 'budget exhaustion by end of day' : 'healthy budget utilization'}
                </div>
              </div>
              {criticalCount > 0 && (
                <div className="p-3 rounded-lg bg-red-50 border border-red-200">
                  <div className="text-sm font-medium text-red-900">Action Required</div>
                  <div className="text-xs text-red-700">
                    {criticalCount} campaign{criticalCount > 1 ? 's' : ''} exceeded budget. Consider pausing or reallocating.
                  </div>
                </div>
              )}
              {warningCount > 0 && (
                <div className="p-3 rounded-lg bg-orange-50 border border-orange-200">
                  <div className="text-sm font-medium text-orange-900">Monitor Closely</div>
                  <div className="text-xs text-orange-700">
                    {warningCount} campaign{warningCount > 1 ? 's' : ''} approaching budget limit.
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
