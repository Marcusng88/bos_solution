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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Campaign & Optimization Dashboard</h1>
          <p className="text-muted-foreground">
            Manage campaigns and get AI-powered optimization insights to maximize performance
          </p>
        </div>
      </div>

      {/* Self Optimization Dashboard */}
      <SelfOptimizationDashboard />
    </div>
  )
}
