"use client"

import { useState } from "react"
import Link from "next/link"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ContentCalendar } from "./content-calendar"
import { AISuggestionsPanel } from "./ai-suggestions-panel"
import { CompetitorGapSuggestions } from "./competitor-gap-suggestions"
import { ContentStrategyInsights } from "./content-strategy-insights"
import { Plus, Calendar, Sparkles, Search, Target, AlertTriangle, Settings } from "lucide-react"

export function ContentPlanningDashboard() {
  const [selectedDate, setSelectedDate] = useState<Date>(new Date())

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">AI Content Planning</h1>
          <p className="text-muted-foreground">Competitor-driven content strategy with AI assistance</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" asChild>
            <Link href="/dashboard/settings">
              <Settings className="mr-2 h-4 w-4" />
              Settings
            </Link>
          </Button>
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Create Content
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Scheduled Posts</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">24</div>
            <p className="text-xs text-muted-foreground">+3 from last week</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Gap Opportunities</CardTitle>
            <Search className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">8</div>
            <p className="text-xs text-muted-foreground">High-impact content gaps</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Competitive Edge</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">+23%</div>
            <p className="text-xs text-muted-foreground">vs competitor average</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Threat Alerts</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">3</div>
            <p className="text-xs text-muted-foreground">Competitor moves to watch</p>
          </CardContent>
        </Card>
      </div>

      {/* Competitive Intelligence Alert */}
      <Card className="border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-950/20">
        <CardContent className="pt-6">
          <div className="flex items-start gap-3">
            <Sparkles className="h-5 w-5 text-blue-600 mt-0.5" />
            <div className="flex-1">
              <h3 className="font-medium text-blue-900 dark:text-blue-100 mb-1">New Content Opportunities Detected</h3>
              <p className="text-sm text-blue-700 dark:text-blue-300 mb-3">
                Our AI found 3 high-impact content gaps based on competitor analysis. Nike is dominating video content
                while Adidas focuses on sustainability messaging.
              </p>
              <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
                View Opportunities
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Content Tabs */}
      <Tabs defaultValue="calendar" className="space-y-6">
        <TabsList>
          <TabsTrigger value="calendar">Content Calendar</TabsTrigger>
          <TabsTrigger value="gaps">Competitor Gaps</TabsTrigger>
          <TabsTrigger value="strategy">Strategy Insights</TabsTrigger>
        </TabsList>

        <TabsContent value="calendar" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Calendar Section */}
            <div className="lg:col-span-2">
              <Card>
                <CardHeader>
                  <CardTitle>Content Calendar</CardTitle>
                  <CardDescription>View and manage your scheduled content across all platforms</CardDescription>
                </CardHeader>
                <CardContent>
                  <ContentCalendar selectedDate={selectedDate} onDateSelect={setSelectedDate} />
                </CardContent>
              </Card>
            </div>

            {/* AI Suggestions Panel */}
            <div>
              <AISuggestionsPanel selectedDate={selectedDate} />
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

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>Latest updates on your content and competitive moves</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[
              {
                action: "Gap Identified",
                content: "Video content opportunity vs Nike",
                time: "1 hour ago",
                status: "opportunity",
              },
              {
                action: "Published",
                content: "Summer Sale Campaign - Instagram Post",
                time: "2 hours ago",
                status: "success",
              },
              {
                action: "Competitor Alert",
                content: "Adidas launched sustainability campaign",
                time: "3 hours ago",
                status: "alert",
              },
              {
                action: "AI Generated",
                content: "Weekly Newsletter Content",
                time: "6 hours ago",
                status: "draft",
              },
            ].map((activity, index) => (
              <div key={index} className="flex items-center justify-between py-2">
                <div className="flex items-center gap-3">
                  <div
                    className={`w-2 h-2 rounded-full ${
                      activity.status === "success"
                        ? "bg-green-500"
                        : activity.status === "opportunity"
                          ? "bg-blue-500"
                          : activity.status === "alert"
                            ? "bg-orange-500"
                            : "bg-gray-500"
                    }`}
                  />
                  <div>
                    <p className="text-sm font-medium">
                      {activity.action} <span className="text-muted-foreground">{activity.content}</span>
                    </p>
                    <p className="text-xs text-muted-foreground">{activity.time}</p>
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
                >
                  {activity.status}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
