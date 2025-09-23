"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Skeleton } from "@/components/ui/skeleton"
import { ContentCalendar } from "./content-calendar"
import { AISuggestionsPanel } from "./ai-suggestions-panel"
import { CompetitorGapSuggestions } from "./competitor-gap-suggestions"
import { ContentStrategyInsights } from "./content-strategy-insights"
import { AIContentGenerator } from "./ai-content-generator"
import { Plus, Calendar, Sparkles, Search, Target, AlertTriangle, Settings, RefreshCw, BarChart3 } from "lucide-react"
import { useContentPlanning } from "@/hooks/use-content-planning"
import GradientText from "@/components/effects/GradientText"
import ShinyText from "@/components/effects/ShinyText"
import "../../styles/competitor-animations.css"

export function ContentPlanningDashboard() {
  const [selectedDate, setSelectedDate] = useState<Date>(new Date())
  const [isVisible, setIsVisible] = useState(false)
  
  const {
    dashboardData,
    supportedOptions,
    loading,
    error,
    selectedIndustry,
    changeIndustry,
    refreshData,
    isReady
  } = useContentPlanning({ 
    autoLoad: true // This only loads basic dashboard data, not AI agent
  })

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

      <div className={`relative z-10 space-y-8 overflow-hidden w-full max-w-full content-container transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
      {/* Enhanced Header */}
      <div className={`flex flex-col lg:flex-row lg:items-center justify-between gap-4 transition-all duration-1000 delay-200 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'}`}>
        <div className="space-y-2">
          <h1 className="text-3xl lg:text-4xl font-bold tracking-tight">
            <GradientText>AI Content Planning</GradientText>
          </h1>
          <div className="text-base lg:text-lg text-slate-400 font-medium">
            <ShinyText text="Competitor-driven content strategy with AI assistance" />
          </div>
        </div>
        <div className={`flex flex-col sm:flex-row items-start sm:items-center gap-3 sm:gap-4 transition-all duration-1000 delay-400 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'}`}>
          {/* Industry Selector */}
          {supportedOptions && (
            <div className="glass-card p-1 rounded-xl shadow-soft w-full sm:w-auto">
              <Select value={selectedIndustry} onValueChange={changeIndustry}>
                <SelectTrigger className="w-full sm:w-[180px] border-0 bg-transparent">
                  <SelectValue placeholder="Select Industry" />
                </SelectTrigger>
                <SelectContent className="glass-card border border-white/10">
                  {supportedOptions.industries.map((industry) => (
                    <SelectItem key={industry} value={industry} className="hover:bg-white/10">
                      {industry.charAt(0).toUpperCase() + industry.slice(1)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}
          
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <Button 
              variant="outline" 
              onClick={refreshData} 
              disabled={loading}
              className="hover-lift flex-1 sm:flex-none"
            >
              <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              <span className="hidden sm:inline">Refresh</span>
            </Button>
            
            <Button variant="outline" asChild className="hover-lift flex-1 sm:flex-none">
              <Link href="/dashboard/settings">
                <Settings className="mr-2 h-4 w-4" />
                <span className="hidden sm:inline">Settings</span>
              </Link>
            </Button>
            
            {/* AI Content Generator - Only invokes AI agent when clicked */}
            <AIContentGenerator
              trigger={
                <Button className="hover-lift shadow-soft flex-1 sm:flex-none">
                  <Plus className="mr-2 h-4 w-4" />
                  <span className="hidden sm:inline">Create Content</span>
                  <span className="sm:hidden">Create</span>
                </Button>
              }
            />
          </div>
        </div>
      </div>

      {/* Enhanced Stats Cards */}
      <div className={`grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 transition-all duration-1000 delay-600 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
        {[
          {
            title: "Scheduled Posts",
            value: dashboardData?.summary.scheduled_posts,
            subtitle: "AI-optimized schedule",
            icon: Calendar,
            color: "from-blue-500 to-indigo-600",
            bgColor: "bg-blue-950/20"
          },
          {
            title: "Gap Opportunities",
            value: dashboardData?.summary.gap_opportunities,
            subtitle: "High-impact content gaps",
            icon: Search,
            color: "from-emerald-500 to-teal-600",
            bgColor: "bg-emerald-950/20"
          },
          {
            title: "Competitive Edge",
            value: dashboardData?.summary.competitive_edge,
            subtitle: "vs competitor average",
            icon: Target,
            color: "from-purple-500 to-violet-600",
            bgColor: "bg-purple-950/20"
          },
          {
            title: "Threat Alerts",
            value: dashboardData?.summary.threat_alerts,
            subtitle: "Competitor moves to watch",
            icon: AlertTriangle,
            color: "from-orange-500 to-red-600",
            bgColor: "bg-orange-950/20"
          }
        ].map((card, index) => (
          <Card key={card.title} className={`glass-card transition-all duration-300 hover:scale-105 hover:shadow-xl ${card.bgColor} border-white/10 animate-fade-in-up`} style={{ animationDelay: `${(index + 1) * 100}ms` }}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
              <CardTitle className="text-sm font-semibold text-slate-300">
                {card.title}
              </CardTitle>
              <div className={`relative p-2.5 rounded-xl bg-gradient-to-r ${card.color} shadow-lg overflow-hidden`}>
                <div className="absolute inset-0 bg-white/10 animate-pulse"></div>
                <card.icon className="relative h-4 w-4 text-white" />
              </div>
            </CardHeader>
            <CardContent>
              {loading || !dashboardData ? (
                <div className="space-y-3">
                  <Skeleton className="h-8 w-16 rounded-lg bg-slate-700/50" />
                  <Skeleton className="h-4 w-32 rounded bg-slate-700/30" />
                </div>
              ) : (
                <>
                  <div className="text-3xl font-bold text-white mb-1 bg-gradient-to-r from-white to-slate-200 bg-clip-text text-transparent">
                    {card.value}
                  </div>
                  <p className="text-xs text-slate-400 font-medium leading-relaxed">
                    {card.subtitle}
                  </p>
                </>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Enhanced Competitive Intelligence Alert */}
      {dashboardData?.competitive_intelligence?.new_opportunities && 
       Array.isArray(dashboardData.competitive_intelligence.new_opportunities) &&
       dashboardData.competitive_intelligence.new_opportunities.length > 0 && (
        <Card className={`glass-card border border-blue-200/20 bg-gradient-to-r from-blue-950/20 via-indigo-950/10 to-blue-950/20 transition-all duration-300 hover:scale-105 hover:shadow-xl animate-fade-in-up delay-800 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
          <CardContent className="pt-6">
            <div className="flex items-start gap-4">
              <div className="p-3 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-xl shadow-soft">
                <Sparkles className="h-6 w-6 text-white" />
              </div>
              <div className="flex-1 space-y-3">
                <h3 className="text-lg font-bold text-blue-100">
                  New Content Opportunities Detected
                </h3>
                <p className="text-blue-300 leading-relaxed">
                  Our AI found <span className="font-semibold">{dashboardData?.summary?.gap_opportunities || 0}</span> high-impact content gaps based on competitor analysis. 
                  {dashboardData.competitive_intelligence.new_opportunities.slice(0, 2).map((opp: any, idx: number) => (
                    <span key={idx}> {typeof opp === 'string' ? opp : (opp.description || opp.title || 'New opportunity detected')}.{idx === 0 && ' '}</span>
                  ))}
                </p>
                <Button size="sm" className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 shadow-soft">
                  <Target className="mr-2 h-4 w-4" />
                  View Opportunities
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Enhanced Main Content Tabs */}
      <Tabs defaultValue="calendar" className={`space-y-8 transition-all duration-1000 delay-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
        <TabsList className="glass-card p-1 bg-slate-800/40 border border-white/20 backdrop-blur-md">
          <TabsTrigger value="calendar" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-600 data-[state=active]:to-purple-600 data-[state=active]:text-white data-[state=active]:shadow-lg font-semibold text-slate-300 transition-all duration-300">
            Content Calendar
          </TabsTrigger>
          {/* <TabsTrigger value="gaps">Competitor Gaps</TabsTrigger>
          <TabsTrigger value="strategy">Strategy Insights</TabsTrigger> */}
        </TabsList>

        <TabsContent value="calendar" className="space-y-8">
          <div className="space-y-8 w-full max-w-full overflow-hidden">
            {/* AI Suggestions Panel - Now above the calendar */}
            <div className={`w-full transition-all duration-700 delay-1200 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'}`}>
              <AISuggestionsPanel selectedDate={selectedDate} />
            </div>

            {/* Calendar Section - Now below the suggestions */}
            <div className={`w-full transition-all duration-700 delay-1400 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'}`}>
              <Card className="glass-card w-full max-w-full transition-all duration-300 hover:scale-105 hover:shadow-xl border border-white/20">
                <CardHeader className="border-b border-white/10">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg">
                      <Calendar className="h-5 w-5 text-white" />
                    </div>
                    <div>
                      <CardTitle className="text-xl font-bold text-white">Content Calendar</CardTitle>
                      <CardDescription className="text-slate-400">View and manage your scheduled content across all platforms</CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="overflow-hidden p-6">
                  <ContentCalendar selectedDate={selectedDate} onDateSelect={setSelectedDate} />
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="gaps" className="space-y-6">
          <CompetitorGapSuggestions />
        </TabsContent>

        <TabsContent value="strategy" className="space-y-6">
          <ContentStrategyInsights />
        </TabsContent>
      </Tabs>

      {/* Enhanced Recent Activity */}
      <Card className={`glass-card transition-all duration-300 hover:scale-105 hover:shadow-xl border border-white/20 animate-fade-in-up delay-1600 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
        <CardHeader className="border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-r from-emerald-500 to-teal-600 rounded-lg">
              <BarChart3 className="h-5 w-5 text-white" />
            </div>
            <div>
              <CardTitle className="text-xl font-bold text-white">Recent Activity</CardTitle>
              <CardDescription className="text-slate-400">Latest updates on your content and competitive moves</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-6">
          <div className="space-y-4">
            {loading || !dashboardData ? (
              Array.from({ length: 4 }).map((_, index) => (
                <div key={index} className="flex items-center gap-4 py-3 animate-pulse">
                  <Skeleton className="w-3 h-3 rounded-full" />
                  <div className="flex-1 space-y-2">
                    <Skeleton className="h-4 w-64" />
                    <Skeleton className="h-3 w-24" />
                  </div>
                  <Skeleton className="h-6 w-20 rounded-full" />
                </div>
              ))
            ) : (
              dashboardData.recent_activity?.map((activity, index) => (
                <div key={index} className="flex items-center justify-between py-4 hover:bg-white/5 rounded-xl px-4 transition-all duration-300 hover:scale-[1.02] group animate-fade-in-up" style={{ animationDelay: `${(index + 1) * 100}ms` }}>
                  <div className="flex items-center gap-4">
                    <div
                      className={`w-3 h-3 rounded-full shadow-lg transition-all duration-300 group-hover:scale-110 ${
                        activity.status === "success"
                          ? "bg-gradient-to-r from-emerald-500 to-green-600 animate-pulse"
                          : activity.status === "opportunity"
                            ? "bg-gradient-to-r from-blue-500 to-indigo-600 animate-pulse"
                            : activity.status === "alert"
                              ? "bg-gradient-to-r from-orange-500 to-red-600 animate-pulse"
                              : "bg-gradient-to-r from-slate-400 to-slate-500"
                      }`}
                    />
                    <div>
                      <p className="text-sm font-semibold text-white group-hover:text-blue-200 transition-colors duration-300">
                        {activity.action} <span className="text-slate-400 font-normal group-hover:text-slate-300 transition-colors duration-300">{activity.content}</span>
                      </p>
                      <p className="text-xs text-slate-400 font-medium group-hover:text-slate-300 transition-colors duration-300">{activity.time}</p>
                    </div>
                  </div>
                  <Badge
                    variant={
                      activity.status === "success"
                        ? "default"
                        : activity.status === "opportunity"
                          ? "secondary"
                          : activity.status === "alert"
                            ? "destructive"
                            : "outline"
                    }
                    className="font-semibold transition-all duration-300 group-hover:scale-105 shadow-md"
                  >
                    {activity.status}
                  </Badge>
                </div>
              )) || []
            )}
          </div>
        </CardContent>
      </Card>
    </div>
    </div>
  )
}
