"use client"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useToast } from "@/hooks/use-toast"
import { Target, TrendingUp, AlertTriangle, CheckCircle, Clock, DollarSign, Users, Zap } from "lucide-react"

export function CompetitorBasedOptimizations() {
  const { toast } = useToast()

  const competitorOptimizations = [
    {
      id: 1,
      type: "competitive-response",
      title: "Counter Nike's Video Campaign",
      competitor: "Nike",
      trigger: "Nike increased video ad spend by 150% targeting fitness enthusiasts",
      recommendation: "Launch competing video campaign with 20% higher budget allocation to fitness keywords",
      impact: "High",
      urgency: "High",
      estimatedGain: "+$4,200 revenue",
      confidence: 94,
      timeframe: "Launch within 48 hours",
      details: {
        currentSpend: "$2,400",
        recommendedSpend: "$3,600",
        targetAudience: "Fitness enthusiasts 25-45",
        expectedCTR: "+0.8%",
        expectedCVR: "+1.2%",
      },
    },
    {
      id: 2,
      type: "gap-exploitation",
      title: "Exploit Adidas' Sustainability Gap",
      competitor: "Adidas",
      trigger: "Adidas reduced sustainability messaging by 30% this quarter",
      recommendation: "Increase eco-friendly product promotion to capture abandoned market share",
      impact: "High",
      urgency: "Medium",
      estimatedGain: "+$3,800 revenue",
      confidence: 89,
      timeframe: "2-week campaign",
      details: {
        currentSpend: "$1,800",
        recommendedSpend: "$2,700",
        targetAudience: "Eco-conscious consumers",
        expectedCTR: "+1.1%",
        expectedCVR: "+0.9%",
      },
    },
    {
      id: 3,
      type: "timing-advantage",
      title: "Capitalize on Under Armour's Quiet Period",
      competitor: "Under Armour",
      trigger: "Under Armour paused major campaigns for budget reallocation",
      recommendation: "Increase bid aggressiveness on shared keywords while competition is low",
      impact: "Medium",
      urgency: "High",
      estimatedGain: "+$2,100 revenue",
      confidence: 87,
      timeframe: "Next 10 days",
      details: {
        currentSpend: "$3,200",
        recommendedSpend: "$4,100",
        targetAudience: "Athletic performance seekers",
        expectedCTR: "+0.6%",
        expectedCVR: "+0.7%",
      },
    },
    {
      id: 4,
      type: "defensive-strategy",
      title: "Defend Against Nike's Influencer Push",
      competitor: "Nike",
      trigger: "Nike partnered with 15 new fitness influencers this month",
      recommendation: "Launch counter-influencer campaign with micro-influencers for better ROI",
      impact: "Medium",
      urgency: "Medium",
      estimatedGain: "+$1,900 revenue",
      confidence: 82,
      timeframe: "3-week rollout",
      details: {
        currentSpend: "$0",
        recommendedSpend: "$2,200",
        targetAudience: "Fitness community followers",
        expectedCTR: "+0.9%",
        expectedCVR: "+0.8%",
      },
    },
    {
      id: 5,
      type: "market-expansion",
      title: "Enter Nike's Abandoned Demographics",
      competitor: "Nike",
      trigger: "Nike reduced targeting of 45+ age group by 40%",
      recommendation: "Expand targeting to mature fitness market with tailored messaging",
      impact: "High",
      urgency: "Low",
      estimatedGain: "+$5,600 revenue",
      confidence: 91,
      timeframe: "4-week campaign",
      details: {
        currentSpend: "$800",
        recommendedSpend: "$2,400",
        targetAudience: "Active adults 45-65",
        expectedCTR: "+1.3%",
        expectedCVR: "+1.1%",
      },
    },
  ]

  const handleApply = (optimization: (typeof competitorOptimizations)[0]) => {
    toast({
      title: "Optimization Applied",
      description: `${optimization.title} has been implemented in your campaigns.`,
    })
  }

  const handleDismiss = (id: number) => {
    toast({
      title: "Optimization Dismissed",
      description: "This recommendation has been removed from your queue.",
    })
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case "competitive-response":
        return <Target className="h-4 w-4" />
      case "gap-exploitation":
        return <TrendingUp className="h-4 w-4" />
      case "timing-advantage":
        return <Clock className="h-4 w-4" />
      case "defensive-strategy":
        return <AlertTriangle className="h-4 w-4" />
      case "market-expansion":
        return <Users className="h-4 w-4" />
      default:
        return <Zap className="h-4 w-4" />
    }
  }

  const getTypeBadge = (type: string) => {
    switch (type) {
      case "competitive-response":
        return <Badge variant="destructive">Competitive Response</Badge>
      case "gap-exploitation":
        return <Badge variant="default">Gap Exploitation</Badge>
      case "timing-advantage":
        return <Badge className="bg-green-600">Timing Advantage</Badge>
      case "defensive-strategy":
        return <Badge variant="secondary">Defensive Strategy</Badge>
      case "market-expansion":
        return <Badge className="bg-purple-600">Market Expansion</Badge>
      default:
        return <Badge variant="outline">Strategy</Badge>
    }
  }

  return (
    <div className="space-y-6">
      {/* Strategy Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Competitive Opportunities</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">5</div>
            <p className="text-xs text-muted-foreground">Based on competitor moves</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Revenue Potential</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">+$17.6K</div>
            <p className="text-xs text-muted-foreground">If all optimizations applied</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Confidence</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">89%</div>
            <p className="text-xs text-muted-foreground">AI recommendation accuracy</p>
          </CardContent>
        </Card>
      </div>

      {/* Competitor-Based Optimizations */}
      <Card>
        <CardHeader>
          <CardTitle>Competitor Intelligence Optimizations</CardTitle>
          <CardDescription>AI recommendations based on real-time competitor analysis</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {competitorOptimizations.map((optimization) => (
              <Card key={optimization.id} className="p-6 border-l-4 border-l-blue-500">
                <div className="space-y-4">
                  {/* Header */}
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        {getTypeIcon(optimization.type)}
                        <h3 className="text-lg font-semibold">{optimization.title}</h3>
                        {getTypeBadge(optimization.type)}
                      </div>
                      <div className="flex items-center gap-4 text-sm text-muted-foreground mb-3">
                        <span>
                          vs <strong>{optimization.competitor}</strong>
                        </span>
                        <Badge
                          variant={
                            optimization.impact === "High"
                              ? "destructive"
                              : optimization.impact === "Medium"
                                ? "secondary"
                                : "outline"
                          }
                        >
                          {optimization.impact} Impact
                        </Badge>
                        <Badge
                          variant={
                            optimization.urgency === "High"
                              ? "destructive"
                              : optimization.urgency === "Medium"
                                ? "secondary"
                                : "outline"
                          }
                        >
                          {optimization.urgency} Urgency
                        </Badge>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-muted-foreground mb-1">Confidence</div>
                      <Badge variant="outline">{optimization.confidence}%</Badge>
                    </div>
                  </div>

                  {/* Trigger & Recommendation */}
                  <div className="space-y-3">
                    <div className="p-3 bg-orange-50 dark:bg-orange-950/20 rounded-lg border-l-2 border-orange-500">
                      <div className="text-sm font-medium text-orange-900 dark:text-orange-100 mb-1">
                        Competitor Trigger
                      </div>
                      <p className="text-sm text-orange-700 dark:text-orange-300">{optimization.trigger}</p>
                    </div>
                    <div className="p-3 bg-blue-50 dark:bg-blue-950/20 rounded-lg border-l-2 border-blue-500">
                      <div className="text-sm font-medium text-blue-900 dark:text-blue-100 mb-1">AI Recommendation</div>
                      <p className="text-sm text-blue-700 dark:text-blue-300">{optimization.recommendation}</p>
                    </div>
                  </div>

                  {/* Details */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-muted/30 rounded-lg">
                    <div>
                      <div className="text-sm text-muted-foreground">Budget Change</div>
                      <div className="font-medium">
                        {optimization.details.currentSpend} → {optimization.details.recommendedSpend}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-muted-foreground">Expected Gain</div>
                      <div className="font-medium text-green-600">{optimization.estimatedGain}</div>
                    </div>
                    <div>
                      <div className="text-sm text-muted-foreground">Timeline</div>
                      <div className="font-medium">{optimization.timeframe}</div>
                    </div>
                  </div>

                  {/* Performance Projections */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <div className="text-center p-2 bg-muted/50 rounded">
                      <div className="text-xs text-muted-foreground">Target Audience</div>
                      <div className="text-sm font-medium">{optimization.details.targetAudience}</div>
                    </div>
                    <div className="text-center p-2 bg-muted/50 rounded">
                      <div className="text-xs text-muted-foreground">CTR Boost</div>
                      <div className="text-sm font-medium text-green-600">{optimization.details.expectedCTR}</div>
                    </div>
                    <div className="text-center p-2 bg-muted/50 rounded">
                      <div className="text-xs text-muted-foreground">CVR Boost</div>
                      <div className="text-sm font-medium text-green-600">{optimization.details.expectedCVR}</div>
                    </div>
                    <div className="text-center p-2 bg-muted/50 rounded">
                      <div className="text-xs text-muted-foreground">Confidence</div>
                      <div className="text-sm font-medium">{optimization.confidence}%</div>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-3">
                    <Button onClick={() => handleApply(optimization)} className="flex-1">
                      <CheckCircle className="mr-2 h-4 w-4" />
                      Apply Optimization
                    </Button>
                    <Button variant="outline">View Details</Button>
                    <Button variant="outline" onClick={() => handleDismiss(optimization.id)}>
                      Dismiss
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
