"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { OptimizationSuggestions } from "./optimization-suggestions"
import { OptimizationHistory } from "./optimization-history"
import { PerformanceImpact } from "./performance-impact"
import { CompetitorBasedOptimizations } from "./competitor-based-optimizations"
import { CompetitorMoveAlerts } from "./competitor-move-alerts"
import { SelfOptimizationDashboard } from "./self-optimization/self-optimization-dashboard"
import { AIAssistant } from "./self-optimization/ai-assistant"
import { AIInsightsPanel } from "./ai-insights-panel"
import { Lightbulb, Target, DollarSign, RefreshCw, AlertTriangle, Search, BarChart3, Brain } from "lucide-react"

export function OptimizationDashboard() {
  const [priorityFilter, setPriorityFilter] = useState("all")
  const [categoryFilter, setCategoryFilter] = useState("all")
  const [optimizationMode, setOptimizationMode] = useState<"competitor" | "self">("competitor")

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">AI Optimization Engine</h1>
          <p className="text-muted-foreground">
            {optimizationMode === "competitor" 
              ? "Competitor-driven AI recommendations to outperform your rivals"
              : "Self-optimization insights to maximize your campaign performance"
            }
          </p>
        </div>
        <div className="flex items-center gap-4">
          {/* Mode Toggle */}
          <div className="flex items-center rounded-lg border bg-background p-1">
            <Button
              variant={optimizationMode === "competitor" ? "default" : "ghost"}
              size="sm"
              onClick={() => setOptimizationMode("competitor")}
              className="transition-all duration-200"
            >
              <Target className="mr-2 h-4 w-4" />
              Competitor-based
            </Button>
            <Button
              variant={optimizationMode === "self" ? "default" : "ghost"}
              size="sm"
              onClick={() => setOptimizationMode("self")}
              className="transition-all duration-200"
            >
              <Brain className="mr-2 h-4 w-4" />
              Self Optimization
            </Button>
          </div>
          <Button>
            <RefreshCw className="mr-2 h-4 w-4" />
            {optimizationMode === "competitor" ? "Scan for New Opportunities" : "Refresh Data"}
          </Button>
        </div>
      </div>

      {/* Summary Cards - Only show in competitor mode */}
      {optimizationMode === "competitor" && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Suggestions</CardTitle>
            <Lightbulb className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">18</div>
            <p className="text-xs text-muted-foreground">8 competitor-based</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Competitor Alerts</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">5</div>
            <p className="text-xs text-muted-foreground">Require immediate action</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Potential Advantage</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">+24%</div>
            <p className="text-xs text-muted-foreground">vs competitor average</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Cost Savings</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">$3,240</div>
            <p className="text-xs text-muted-foreground">Monthly estimate</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Market Position</CardTitle>
            <Search className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">3rd</div>
            <p className="text-xs text-green-600">+1 position this month</p>
          </CardContent>
        </Card>
      </div>
      )}

      {/* Mode-specific Content */}
      <div className="transition-all duration-300 ease-in-out">
        {optimizationMode === "competitor" ? (
          <>
            {/* Competitor Move Alerts */}
            <CompetitorMoveAlerts />

            {/* Main Content */}
            <Tabs defaultValue="competitor-based" className="space-y-6">
              <TabsList>
                <TabsTrigger value="competitor-based">Competitor Intelligence</TabsTrigger>
                <TabsTrigger value="suggestions">All Suggestions</TabsTrigger>
                <TabsTrigger value="impact">Performance Impact</TabsTrigger>
                <TabsTrigger value="history">Optimization History</TabsTrigger>
                <TabsTrigger value="ai-insights">AI Insights</TabsTrigger>
              </TabsList>

              <TabsContent value="competitor-based" className="space-y-6">
                <CompetitorBasedOptimizations />
              </TabsContent>

              <TabsContent value="suggestions" className="space-y-6">
                {/* Filters */}
                <div className="flex gap-4">
                  <Select value={priorityFilter} onValueChange={setPriorityFilter}>
                    <SelectTrigger className="w-40">
                      <SelectValue placeholder="Priority" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Priorities</SelectItem>
                      <SelectItem value="high">High Priority</SelectItem>
                      <SelectItem value="medium">Medium Priority</SelectItem>
                      <SelectItem value="low">Low Priority</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                    <SelectTrigger className="w-40">
                      <SelectValue placeholder="Category" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Categories</SelectItem>
                      <SelectItem value="budget">Budget</SelectItem>
                      <SelectItem value="targeting">Targeting</SelectItem>
                      <SelectItem value="creative">Creative</SelectItem>
                      <SelectItem value="timing">Timing</SelectItem>
                      <SelectItem value="bidding">Bidding</SelectItem>
                      <SelectItem value="competitor-response">Competitor Response</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <OptimizationSuggestions priorityFilter={priorityFilter} categoryFilter={categoryFilter} />
              </TabsContent>

              <TabsContent value="impact" className="space-y-6">
                <PerformanceImpact />
              </TabsContent>

              <TabsContent value="history" className="space-y-6">
                <OptimizationHistory />
              </TabsContent>

              <TabsContent value="ai-insights" className="space-y-6">
                <AIInsightsPanel />
              </TabsContent>
            </Tabs>
          </>
        ) : (
          <SelfOptimizationDashboard />
        )}
      </div>

      {/* AI Assistant - Only shown in self-optimization mode */}
      {optimizationMode === "self" && <AIAssistant />}
    </div>
  )
}
