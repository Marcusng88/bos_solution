"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { CampaignPerformanceDashboard } from "./campaign-performance-dashboard"
import { BudgetMonitoringWidget } from "./budget-monitoring-widget"
import { BudgetDashboard } from "./budget-dashboard"
import { RiskPatternsWidget } from "./risk-patterns-widget"
import { RecommendationsWidget } from "./recommendations-widget"
import { AlertsWidget } from "./alerts-widget"
import { OverspendingPredictionWidget } from "./overspending-prediction-widget"
import { AIInsightsPanel } from "../ai-insights-panel"
import { AddCampaignModal } from "../add-campaign-modal"
import { useApiClient, handleApiError } from "@/lib/api-client"
import { DollarSign, TrendingUp, AlertTriangle, Target, Activity, BarChart3, Plus, RefreshCw } from "lucide-react"
import GradientText from "@/components/effects/GradientText"
import ShinyText from "@/components/effects/ShinyText"
import "../../../styles/competitor-animations.css"

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
  const [isAddCampaignModalOpen, setIsAddCampaignModalOpen] = useState(false)
  const [isVisible, setIsVisible] = useState(false)
  const { apiClient, userId } = useApiClient()

  useEffect(() => {
    fetchDashboardMetrics()
    setIsVisible(true)
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
      
      setMetrics(basicMetrics as DashboardMetrics)
      setDetailedMetrics(detailedMetricsData as DetailedMetrics)
      setOverspendingPredictions(predictionsData as OverspendingPrediction[])
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
      <div className={`flex items-center justify-between transition-all duration-1000 delay-200 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'}`}>
        <div>
          <h2 className="text-2xl font-bold tracking-tight">
            <GradientText>Self Optimization Dashboard</GradientText>
          </h2>
          <div className="text-muted-foreground">
            <ShinyText text="Monitor and optimize your campaign performance" />
          </div>
        </div>
        <div className={`flex items-center gap-3 transition-all duration-1000 delay-400 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'}`}>
          <Button
            onClick={() => setIsAddCampaignModalOpen(true)}
            size="sm"
            className="bg-blue-600 hover:bg-blue-700"
          >
            <Plus className="mr-2 h-4 w-4" />
            Add Campaign
          </Button>
          <Button
            onClick={fetchDashboardMetrics}
            size="sm"
            variant="outline"
            disabled={loading}
          >
            <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh Data
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className={`grid grid-cols-1 md:grid-cols-4 gap-4 transition-all duration-1000 delay-600 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'}`}>
        <Card className="glass-card transition-all duration-300 hover:scale-105 hover:shadow-xl border-white/20 animate-fade-in-up" style={{ animationDelay: '100ms' }}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-300">Active Spend</CardTitle>
            <div className="relative p-2.5 rounded-xl bg-gradient-to-r from-blue-500 to-indigo-600 shadow-lg overflow-hidden">
              <div className="absolute inset-0 bg-white/10 animate-pulse"></div>
              <DollarSign className="relative h-4 w-4 text-white" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white bg-gradient-to-r from-white to-slate-200 bg-clip-text text-transparent">${metrics?.spend_today.toFixed(2) || '0.00'}</div>
            <p className="text-xs text-slate-400 font-medium leading-relaxed">
              of ${metrics?.budget_today.toFixed(2) || '0.00'} budget
            </p>
          </CardContent>
        </Card>

        <Card className="glass-card transition-all duration-300 hover:scale-105 hover:shadow-xl border-white/20 animate-fade-in-up" style={{ animationDelay: '200ms' }}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-300">Budget Utilization</CardTitle>
            <div className="relative p-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 shadow-lg overflow-hidden">
              <div className="absolute inset-0 bg-white/10 animate-pulse"></div>
              <TrendingUp className="relative h-4 w-4 text-white" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600 bg-gradient-to-r from-blue-400 to-blue-600 bg-clip-text text-transparent">
              {metrics?.budget_utilization_pct.toFixed(1) || '0.0'}%
            </div>
            <p className="text-xs text-slate-400 font-medium leading-relaxed">Active campaigns utilization</p>
          </CardContent>
        </Card>

        <Card className="glass-card transition-all duration-300 hover:scale-105 hover:shadow-xl border-white/20 animate-fade-in-up" style={{ animationDelay: '300ms' }}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-300">Active Alerts</CardTitle>
            <div className="relative p-2.5 rounded-xl bg-gradient-to-r from-orange-500 to-red-600 shadow-lg overflow-hidden">
              <div className="absolute inset-0 bg-white/10 animate-pulse"></div>
              <AlertTriangle className="relative h-4 w-4 text-white" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600 bg-gradient-to-r from-orange-400 to-orange-600 bg-clip-text text-transparent">
              {overspendingPredictions.length || 0}
            </div>
            <p className="text-xs text-slate-400 font-medium leading-relaxed">Risky campaigns detected</p>
          </CardContent>
        </Card>

        <Card className="glass-card transition-all duration-300 hover:scale-105 hover:shadow-xl border-white/20 animate-fade-in-up" style={{ animationDelay: '400ms' }}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-300">Risk Patterns</CardTitle>
            <div className="relative p-2.5 rounded-xl bg-gradient-to-r from-purple-500 to-violet-600 shadow-lg overflow-hidden">
              <div className="absolute inset-0 bg-white/10 animate-pulse"></div>
              <Activity className="relative h-4 w-4 text-white" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600 bg-gradient-to-r from-red-400 to-red-600 bg-clip-text text-transparent">
              {overspendingPredictions.filter(p => p.overspend_risk === 'critical').length || 0}
            </div>
            <p className="text-xs text-slate-400 font-medium leading-relaxed">
              {overspendingPredictions.filter(p => p.overspend_risk === 'critical').length || 0} Critical, {' '}
              {overspendingPredictions.filter(p => p.overspend_risk === 'high').length || 0} High, {' '}
              {overspendingPredictions.filter(p => p.overspend_risk === 'medium').length || 0} Medium
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <div className={`grid grid-cols-1 lg:grid-cols-2 gap-6 transition-all duration-1000 delay-800 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'}`}>
        <AlertsWidget />
        <RiskPatternsWidget />
      </div>

      {/* Main Dashboard Content */}
      <Tabs defaultValue="overview" className={`space-y-6 transition-all duration-1000 delay-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
        <TabsList className="glass-card grid w-full grid-cols-5 p-1 bg-slate-800/40 border border-white/20 backdrop-blur-md">
          <TabsTrigger value="overview" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-600 data-[state=active]:to-purple-600 data-[state=active]:text-white data-[state=active]:shadow-lg font-semibold text-slate-300 transition-all duration-300">Overview</TabsTrigger>
          <TabsTrigger value="campaigns" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-600 data-[state=active]:to-purple-600 data-[state=active]:text-white data-[state=active]:shadow-lg font-semibold text-slate-300 transition-all duration-300">Campaign Performance</TabsTrigger>
          <TabsTrigger value="budget" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-600 data-[state=active]:to-purple-600 data-[state=active]:text-white data-[state=active]:shadow-lg font-semibold text-slate-300 transition-all duration-300">Budget Monitoring</TabsTrigger>
          <TabsTrigger value="insights" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-600 data-[state=active]:to-purple-600 data-[state=active]:text-white data-[state=active]:shadow-lg font-semibold text-slate-300 transition-all duration-300">AI Insights</TabsTrigger>
          <TabsTrigger value="predictions" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-600 data-[state=active]:to-purple-600 data-[state=active]:text-white data-[state=active]:shadow-lg font-semibold text-slate-300 transition-all duration-300">Risk Detection</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className={`space-y-6 transition-all duration-700 delay-1200 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'}`}>
          <div className="grid gap-6 lg:grid-cols-2">
            <CampaignPerformanceDashboard />
            <BudgetDashboard />
          </div>
        </TabsContent>

        <TabsContent value="campaigns" className={`space-y-6 transition-all duration-700 delay-1200 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'}`}>
          <CampaignPerformanceDashboard detailed={true} />
        </TabsContent>

        <TabsContent value="budget" className={`space-y-6 transition-all duration-700 delay-1200 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'}`}>
          <BudgetDashboard />
        </TabsContent>

        <TabsContent value="insights" className={`space-y-6 transition-all duration-700 delay-1200 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'}`}>
          <AIInsightsPanel />
        </TabsContent>
        
        <TabsContent value="predictions" className={`space-y-6 transition-all duration-700 delay-1200 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'}`}>
          <OverspendingPredictionWidget />
        </TabsContent>
      </Tabs>

      {/* Add Campaign Modal */}
      <AddCampaignModal
        isOpen={isAddCampaignModalOpen}
        onClose={() => setIsAddCampaignModalOpen(false)}
        onCampaignCreated={fetchDashboardMetrics}
      />
    </div>
  )
}
