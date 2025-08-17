"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { CampaignPerformanceDashboard } from "./campaign-performance-dashboard"
import { BudgetMonitoringWidget } from "./budget-monitoring-widget"
import { RiskPatternsWidget } from "./risk-patterns-widget"
import { RecommendationsWidget } from "./recommendations-widget"
import { AlertsWidget } from "./alerts-widget"
import { OverspendingPredictionWidget } from "./overspending-prediction-widget"
import { useApiClient, handleApiError } from "@/lib/api-client"
import { DollarSign, TrendingUp, AlertTriangle, Target, Activity, BarChart3 } from "lucide-react"

interface DashboardMetrics {
  spend_today: number  // Backend returns Decimal but converts to float via json_encoders
  budget_today: number  // Backend returns Decimal but converts to float via json_encoders
  alerts_count: number
  risk_patterns_count: number
  recommendations_count: number
  budget_utilization_pct: number  // Backend returns Decimal but converts to float via json_encoders
}

interface DetailedMetrics {
  basic_metrics: DashboardMetrics
  risk_breakdown: {
    critical: number
    high: number
    medium: number
    low: number
  }
  alert_breakdown: {
    critical: number
    high: number
    medium: number
    low: number
  }
}

interface OverspendingPrediction {
  campaign_name: string
  overspend_risk: 'low' | 'medium' | 'high' | 'critical'
  risk_score: number
}

export function SelfOptimizationDashboard() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null)
  const [detailedMetrics, setDetailedMetrics] = useState<DetailedMetrics | null>(null)
  const [overspendingPredictions, setOverspendingPredictions] = useState<OverspendingPrediction[]>([])
  const [loading, setLoading] = useState(true)
  const { apiClient, userId } = useApiClient()

  useEffect(() => {
    fetchDashboardMetrics()
  }, [])

  const fetchDashboardMetrics = async () => {
    try {
      setLoading(true)
      
      console.log('Fetching dashboard metrics for user:', userId)
      
      // Fetch basic metrics, detailed metrics, and overspending predictions
      const [basicMetrics, detailedMetricsData, predictionsData] = await Promise.all([
        apiClient.getDashboardMetrics(userId),
        apiClient.getDetailedDashboardMetrics(userId),
        apiClient.getOverspendingPredictions(userId)
      ])
      
      console.log('Basic metrics received:', basicMetrics)
      console.log('Detailed metrics received:', detailedMetricsData)
      console.log('Overspending predictions received:', predictionsData)
      
      setMetrics(basicMetrics)
      setDetailedMetrics(detailedMetricsData)
      setOverspendingPredictions(predictionsData)
    } catch (error) {
      console.error('Failed to fetch dashboard metrics:', handleApiError(error))
      // Fall back to mock data if API fails
      const mockMetrics: DashboardMetrics = {
        spend_today: 0,
        budget_today: 0,
        alerts_count: 0,
        risk_patterns_count: 0,
        recommendations_count: 0,
        budget_utilization_pct: 0
      }
      setMetrics(mockMetrics)
      setDetailedMetrics({
        basic_metrics: mockMetrics,
        risk_breakdown: { critical: 0, high: 0, medium: 0, low: 0 },
        alert_breakdown: { critical: 0, high: 0, medium: 0, low: 0 }
      })
      setOverspendingPredictions([])
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-in fade-in-50 duration-500">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Self Optimization Dashboard</h2>
        <p className="text-muted-foreground">Monitor and optimize your campaign performance</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card className="transition-all duration-200 hover:shadow-lg">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Spend</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${metrics?.spend_today.toFixed(2) || '0.00'}</div>
            <p className="text-xs text-muted-foreground">
              of ${metrics?.budget_today.toFixed(2) || '0.00'} budget
            </p>
          </CardContent>
        </Card>

        <Card className="transition-all duration-200 hover:shadow-lg">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Budget Utilization</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">
              {metrics?.budget_utilization_pct.toFixed(1) || '0.0'}%
            </div>
            <p className="text-xs text-muted-foreground">Active campaigns utilization</p>
          </CardContent>
        </Card>

        <Card className="transition-all duration-200 hover:shadow-lg">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Alerts</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              {overspendingPredictions.length || 0}
            </div>
            <p className="text-xs text-muted-foreground">Risky campaigns detected</p>
          </CardContent>
        </Card>

        <Card className="transition-all duration-200 hover:shadow-lg">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Risk Patterns</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {overspendingPredictions.filter(p => p.overspend_risk === 'critical').length || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              {overspendingPredictions.filter(p => p.overspend_risk === 'critical').length || 0} Critical, {' '}
              {overspendingPredictions.filter(p => p.overspend_risk === 'high').length || 0} High, {' '}
              {overspendingPredictions.filter(p => p.overspend_risk === 'medium').length || 0} Medium
            </p>
          </CardContent>
        </Card>

        <Card className="transition-all duration-200 hover:shadow-lg">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Recommendations</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {metrics?.recommendations_count || 0}
            </div>
            <p className="text-xs text-muted-foreground">Available actions</p>
          </CardContent>
        </Card>


      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <AlertsWidget />
        <RiskPatternsWidget />
        <RecommendationsWidget />
      </div>

      {/* Main Dashboard Content */}
      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="campaigns">Campaign Performance</TabsTrigger>
          <TabsTrigger value="budget">Budget Monitoring</TabsTrigger>
          <TabsTrigger value="insights">AI Insights</TabsTrigger>
          <TabsTrigger value="predictions">Predictions</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid gap-6 lg:grid-cols-2">
            <CampaignPerformanceDashboard />
            <BudgetMonitoringWidget />
          </div>
        </TabsContent>

        <TabsContent value="campaigns" className="space-y-6">
          <CampaignPerformanceDashboard detailed={true} />
        </TabsContent>

        <TabsContent value="budget" className="space-y-6">
          <BudgetMonitoringWidget detailed={true} />
        </TabsContent>

        <TabsContent value="insights" className="space-y-6">
          <div className="grid gap-6">
            <Card>
              <CardHeader>
                <CardTitle>AI-Powered Insights</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="p-4 rounded-lg bg-blue-50 border border-blue-200">
                    <h4 className="font-medium text-blue-900">Spending Pattern Analysis</h4>
                    <p className="text-sm text-blue-700 mt-1">
                      Your weekend campaigns show 35% better performance. Consider increasing weekend budgets.
                    </p>
                  </div>
                  <div className="p-4 rounded-lg bg-green-50 border border-green-200">
                    <h4 className="font-medium text-green-900">Optimization Opportunity</h4>
                    <p className="text-sm text-green-700 mt-1">
                      "Summer Sale" campaign has the highest ROI. Scaling budget by 40% could increase conversions by 60%.
                    </p>
                  </div>
                  <div className="p-4 rounded-lg bg-orange-50 border border-orange-200">
                    <h4 className="font-medium text-orange-900">Risk Assessment</h4>
                    <p className="text-sm text-orange-700 mt-1">
                      "Brand Awareness" campaign spending increased 80% yesterday. Monitor closely to prevent overspend.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
        
        <TabsContent value="predictions" className="space-y-6">
          <OverspendingPredictionWidget />
        </TabsContent>
      </Tabs>
    </div>
  )
}
