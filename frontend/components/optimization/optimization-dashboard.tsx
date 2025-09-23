"use client"

import { useState, useEffect } from "react"
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
import GradientText from "@/components/effects/GradientText"
import ShinyText from "@/components/effects/ShinyText"
import "../../styles/competitor-animations.css"

export function OptimizationDashboard() {
  const [priorityFilter, setPriorityFilter] = useState("all")
  const [categoryFilter, setCategoryFilter] = useState("all")
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    setIsVisible(true)
  }, [])

  return (
    <div className="relative">
      {/* Subtle background overlay for depth */}
      <div className="absolute inset-0 bg-gradient-to-br from-transparent via-blue-950/3 to-purple-950/3 pointer-events-none"></div>
      
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-500/4 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-500/4 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }}></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-r from-blue-500/2 to-purple-500/2 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
      </div>

      <div className={`relative z-10 space-y-6 transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
        {/* Header */}
        <div className={`flex items-center justify-between transition-all duration-1000 delay-200 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'}`}>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">
              <GradientText>Campaign & Optimization Dashboard</GradientText>
            </h1>
            <div className="text-muted-foreground">
              <ShinyText text="Manage campaigns and get AI-powered optimization insights to maximize performance" />
            </div>
          </div>
        </div>

        {/* Self Optimization Dashboard */}
        <div className={`transition-all duration-1000 delay-400 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'}`}>
          <SelfOptimizationDashboard />
        </div>
      </div>
    </div>
  )
}
