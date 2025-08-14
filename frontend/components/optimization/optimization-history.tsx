"use client"

import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { CheckCircle, X, Clock, TrendingUp, TrendingDown, DollarSign, Target, Zap } from "lucide-react"

const optimizationHistory = [
  {
    id: 1,
    title: "Increased Budget for Summer Sale Campaign",
    category: "budget",
    status: "successful",
    appliedDate: "2024-01-10",
    campaign: "Summer Sale 2024",
    platform: "Facebook",
    impact: {
      metric: "Conversions",
      before: 45,
      after: 67,
      improvement: 49,
      savings: 340,
    },
    icon: DollarSign,
  },
  {
    id: 2,
    title: "Optimized Ad Scheduling",
    category: "timing",
    status: "successful",
    appliedDate: "2024-01-08",
    campaign: "Product Launch",
    platform: "Instagram",
    impact: {
      metric: "CTR",
      before: 2.1,
      after: 2.8,
      improvement: 33,
      savings: 280,
    },
    icon: Clock,
  },
  {
    id: 3,
    title: "Refined Audience Targeting",
    category: "targeting",
    status: "in-progress",
    appliedDate: "2024-01-12",
    campaign: "Brand Awareness",
    platform: "Facebook",
    impact: {
      metric: "CPA",
      before: 45,
      after: 32,
      improvement: 29,
      savings: 450,
    },
    icon: Target,
  },
  {
    id: 4,
    title: "Updated Creative Assets",
    category: "creative",
    status: "failed",
    appliedDate: "2024-01-05",
    campaign: "Retargeting",
    platform: "Instagram",
    impact: {
      metric: "Engagement",
      before: 3.2,
      after: 2.8,
      improvement: -12,
      savings: -120,
    },
    icon: Zap,
  },
  {
    id: 5,
    title: "Paused Underperforming Ad Sets",
    category: "budget",
    status: "successful",
    appliedDate: "2024-01-03",
    campaign: "Multiple Campaigns",
    platform: "Facebook",
    impact: {
      metric: "Spend Efficiency",
      before: 78,
      after: 92,
      improvement: 18,
      savings: 890,
    },
    icon: DollarSign,
  },
]

export function OptimizationHistory() {
  const [statusFilter, setStatusFilter] = useState("all")
  const [categoryFilter, setCategoryFilter] = useState("all")

  const filteredHistory = optimizationHistory.filter((item) => {
    const matchesStatus = statusFilter === "all" || item.status === statusFilter
    const matchesCategory = categoryFilter === "all" || item.category === categoryFilter
    return matchesStatus && matchesCategory
  })

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "successful":
        return (
          <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100">
            <CheckCircle className="mr-1 h-3 w-3" />
            Successful
          </Badge>
        )
      case "in-progress":
        return (
          <Badge className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100">
            <Clock className="mr-1 h-3 w-3" />
            In Progress
          </Badge>
        )
      case "failed":
        return (
          <Badge className="bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100">
            <X className="mr-1 h-3 w-3" />
            Failed
          </Badge>
        )
      default:
        return <Badge variant="secondary">Unknown</Badge>
    }
  }

  const getImpactIcon = (improvement: number) => {
    if (improvement > 0) {
      return <TrendingUp className="h-4 w-4 text-green-600" />
    } else {
      return <TrendingDown className="h-4 w-4 text-red-600" />
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    })
  }

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="flex gap-4">
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="successful">Successful</SelectItem>
            <SelectItem value="in-progress">In Progress</SelectItem>
            <SelectItem value="failed">Failed</SelectItem>
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
          </SelectContent>
        </Select>
      </div>

      {/* History List */}
      <div className="space-y-4">
        {filteredHistory.map((item) => {
          const Icon = item.icon
          return (
            <Card key={item.id}>
              <CardContent className="pt-6">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4 flex-1">
                    <div className="p-2 bg-gray-100 dark:bg-gray-800 rounded-lg">
                      <Icon className="h-5 w-5 text-gray-600" />
                    </div>
                    <div className="space-y-2 flex-1">
                      <div className="flex items-center gap-3">
                        <h3 className="font-semibold">{item.title}</h3>
                        {getStatusBadge(item.status)}
                      </div>
                      <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        <span>{item.campaign}</span>
                        <span>•</span>
                        <span>{item.platform}</span>
                        <span>•</span>
                        <span>Applied {formatDate(item.appliedDate)}</span>
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                        <div>
                          <p className="text-xs text-muted-foreground">Metric</p>
                          <p className="font-medium">{item.impact.metric}</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground">Before → After</p>
                          <p className="font-medium">
                            {item.impact.before} → {item.impact.after}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground">Improvement</p>
                          <div className="flex items-center gap-1">
                            {getImpactIcon(item.impact.improvement)}
                            <span
                              className={`font-medium ${item.impact.improvement > 0 ? "text-green-600" : "text-red-600"}`}
                            >
                              {item.impact.improvement > 0 ? "+" : ""}
                              {item.impact.improvement}%
                            </span>
                          </div>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground">Impact</p>
                          <p className={`font-medium ${item.impact.savings > 0 ? "text-green-600" : "text-red-600"}`}>
                            {item.impact.savings > 0 ? "+$" : "-$"}
                            {Math.abs(item.impact.savings)}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                  <Button variant="outline" size="sm">
                    View Details
                  </Button>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {filteredHistory.length === 0 && (
        <Card>
          <CardContent className="flex items-center justify-center py-12">
            <div className="text-center">
              <Clock className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No History Found</h3>
              <p className="text-muted-foreground">No optimization history matches your current filters.</p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
