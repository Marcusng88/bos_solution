"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useToast } from "@/hooks/use-toast"
import {
  TrendingUp,
  DollarSign,
  Target,
  Clock,
  Zap,
  AlertTriangle,
  CheckCircle,
  X,
  ThumbsUp,
  Eye,
  BarChart3,
} from "lucide-react"

interface OptimizationSuggestionsProps {
  priorityFilter: string
  categoryFilter: string
}

const suggestions = [
  {
    id: 1,
    title: "Increase Budget for High-Performing Campaign",
    description:
      "Your 'Summer Sale 2024' campaign is performing 45% above average. Increasing the budget by $500 could generate an additional 120 conversions.",
    category: "budget",
    priority: "high",
    impact: "high",
    potentialSavings: 890,
    expectedImprovement: 23,
    campaign: "Summer Sale 2024",
    platform: "Facebook",
    confidence: 92,
    icon: DollarSign,
    details: {
      currentBudget: "$2,000",
      suggestedBudget: "$2,500",
      expectedConversions: "+120",
      roi: "340%",
    },
  },
  {
    id: 2,
    title: "Optimize Ad Scheduling",
    description:
      "Your ads perform 67% better between 7-9 PM. Shifting 40% of your budget to these peak hours could improve overall performance.",
    category: "timing",
    priority: "high",
    impact: "medium",
    potentialSavings: 450,
    expectedImprovement: 18,
    campaign: "Product Launch",
    platform: "Instagram",
    confidence: 88,
    icon: Clock,
    details: {
      currentSchedule: "All day",
      suggestedSchedule: "Peak hours focus",
      expectedCTR: "+1.2%",
      costReduction: "15%",
    },
  },
  {
    id: 3,
    title: "Refine Audience Targeting",
    description:
      "Users aged 25-34 with interests in 'sustainable living' show 3x higher conversion rates. Expanding this segment could boost performance.",
    category: "targeting",
    priority: "medium",
    impact: "high",
    potentialSavings: 320,
    expectedImprovement: 28,
    campaign: "Brand Awareness",
    platform: "Facebook",
    confidence: 85,
    icon: Target,
    details: {
      currentAudience: "Broad targeting",
      suggestedAudience: "Refined segments",
      expectedConversions: "+85",
      cpaReduction: "22%",
    },
  },
  {
    id: 4,
    title: "Update Creative Assets",
    description:
      "Video ads are outperforming static images by 156%. Creating 3 new video variations could significantly improve engagement.",
    category: "creative",
    priority: "medium",
    impact: "medium",
    potentialSavings: 280,
    expectedImprovement: 15,
    campaign: "Retargeting Campaign",
    platform: "Instagram",
    confidence: 79,
    icon: Zap,
    details: {
      currentFormat: "Static images",
      suggestedFormat: "Video content",
      expectedEngagement: "+45%",
      ctrImprovement: "2.1%",
    },
  },
  {
    id: 5,
    title: "Adjust Bidding Strategy",
    description:
      "Switching to Target CPA bidding could reduce your cost per conversion by 18% while maintaining current volume.",
    category: "bidding",
    priority: "low",
    impact: "medium",
    potentialSavings: 190,
    expectedImprovement: 12,
    campaign: "Lead Generation",
    platform: "LinkedIn",
    confidence: 74,
    icon: BarChart3,
    details: {
      currentBidding: "Manual CPC",
      suggestedBidding: "Target CPA",
      expectedCPA: "-$8.50",
      volumeChange: "Maintained",
    },
  },
  {
    id: 6,
    title: "Pause Underperforming Ad Sets",
    description:
      "3 ad sets are consuming 25% of budget with conversion rates below 1%. Pausing them could save $340 weekly.",
    category: "budget",
    priority: "high",
    impact: "low",
    potentialSavings: 1360,
    expectedImprovement: 8,
    campaign: "Multiple campaigns",
    platform: "Facebook",
    confidence: 96,
    icon: AlertTriangle,
    details: {
      affectedAdSets: "3 ad sets",
      currentSpend: "$340/week",
      expectedSavings: "$1,360/month",
      performanceImpact: "Minimal",
    },
  },
]

export function OptimizationSuggestions({ priorityFilter, categoryFilter }: OptimizationSuggestionsProps) {
  const [appliedSuggestions, setAppliedSuggestions] = useState<number[]>([])
  const [ignoredSuggestions, setIgnoredSuggestions] = useState<number[]>([])
  const { toast } = useToast()

  const filteredSuggestions = suggestions.filter((suggestion) => {
    const matchesPriority = priorityFilter === "all" || suggestion.priority === priorityFilter
    const matchesCategory = categoryFilter === "all" || suggestion.category === categoryFilter
    const notProcessed = !appliedSuggestions.includes(suggestion.id) && !ignoredSuggestions.includes(suggestion.id)
    return matchesPriority && matchesCategory && notProcessed
  })

  const handleApply = (suggestion: (typeof suggestions)[0]) => {
    setAppliedSuggestions((prev) => [...prev, suggestion.id])
    toast({
      title: "Optimization Applied",
      description: `${suggestion.title} has been implemented successfully.`,
    })
  }

  const handleIgnore = (suggestion: (typeof suggestions)[0]) => {
    setIgnoredSuggestions((prev) => [...prev, suggestion.id])
    toast({
      title: "Suggestion Ignored",
      description: `${suggestion.title} has been dismissed.`,
    })
  }

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case "high":
        return <Badge className="bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100">High Priority</Badge>
      case "medium":
        return (
          <Badge className="bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100">
            Medium Priority
          </Badge>
        )
      case "low":
        return <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100">Low Priority</Badge>
      default:
        return <Badge variant="secondary">Unknown</Badge>
    }
  }

  const getImpactBadge = (impact: string) => {
    switch (impact) {
      case "high":
        return <Badge variant="default">High Impact</Badge>
      case "medium":
        return <Badge variant="secondary">Medium Impact</Badge>
      case "low":
        return <Badge variant="outline">Low Impact</Badge>
      default:
        return <Badge variant="secondary">Unknown</Badge>
    }
  }

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case "budget":
        return DollarSign
      case "targeting":
        return Target
      case "creative":
        return Zap
      case "timing":
        return Clock
      case "bidding":
        return BarChart3
      default:
        return TrendingUp
    }
  }

  return (
    <div className="space-y-6">
      {/* Applied/Ignored Summary */}
      {(appliedSuggestions.length > 0 || ignoredSuggestions.length > 0) && (
        <Card className="bg-blue-50 dark:bg-blue-950/20 border-blue-200">
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <CheckCircle className="h-5 w-5 text-blue-600" />
              <div>
                <p className="font-medium text-blue-900 dark:text-blue-100">
                  {appliedSuggestions.length} suggestions applied, {ignoredSuggestions.length} ignored
                </p>
                <p className="text-sm text-blue-700 dark:text-blue-200">
                  Your optimizations are being processed and will take effect within 24 hours.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Suggestions Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredSuggestions.map((suggestion) => {
          const Icon = suggestion.icon
          const CategoryIcon = getCategoryIcon(suggestion.category)

          return (
            <Card key={suggestion.id} className="relative">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    <div className="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
                      <Icon className="h-5 w-5 text-blue-600" />
                    </div>
                    <div className="space-y-1">
                      <CardTitle className="text-lg leading-tight">{suggestion.title}</CardTitle>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="text-xs">
                          <CategoryIcon className="mr-1 h-3 w-3" />
                          {suggestion.category}
                        </Badge>
                        <Badge variant="outline" className="text-xs">
                          {suggestion.platform}
                        </Badge>
                      </div>
                    </div>
                  </div>
                  <div className="flex flex-col gap-1">
                    {getPriorityBadge(suggestion.priority)}
                    {getImpactBadge(suggestion.impact)}
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <CardDescription className="text-sm leading-relaxed">{suggestion.description}</CardDescription>

                {/* Key Metrics */}
                <div className="grid grid-cols-3 gap-4 p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
                  <div className="text-center">
                    <p className="text-xs text-muted-foreground">Potential Savings</p>
                    <p className="font-semibold text-green-600">${suggestion.potentialSavings}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-muted-foreground">Expected Improvement</p>
                    <p className="font-semibold text-blue-600">+{suggestion.expectedImprovement}%</p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-muted-foreground">Confidence</p>
                    <p className="font-semibold">{suggestion.confidence}%</p>
                  </div>
                </div>

                {/* Details */}
                <div className="space-y-2">
                  <h4 className="text-sm font-medium">Implementation Details:</h4>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    {Object.entries(suggestion.details).map(([key, value]) => (
                      <div key={key} className="flex justify-between">
                        <span className="text-muted-foreground capitalize">{key.replace(/([A-Z])/g, " $1")}:</span>
                        <span className="font-medium">{value}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-3 pt-4">
                  <Button onClick={() => handleApply(suggestion)} className="flex-1">
                    <ThumbsUp className="mr-2 h-4 w-4" />
                    Apply
                  </Button>
                  <Button variant="outline" onClick={() => handleIgnore(suggestion)}>
                    <X className="mr-2 h-4 w-4" />
                    Ignore
                  </Button>
                  <Button variant="outline" size="icon">
                    <Eye className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {filteredSuggestions.length === 0 && (
        <Card>
          <CardContent className="flex items-center justify-center py-12">
            <div className="text-center">
              <CheckCircle className="mx-auto h-12 w-12 text-green-500 mb-4" />
              <h3 className="text-lg font-semibold mb-2">All Caught Up!</h3>
              <p className="text-muted-foreground">
                {appliedSuggestions.length > 0 || ignoredSuggestions.length > 0
                  ? "You've processed all current optimization suggestions."
                  : "No optimization suggestions match your current filters."}
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
