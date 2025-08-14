"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { TrendingUp, TrendingDown, Target, Users, BarChart3 } from "lucide-react"

interface CompetitorBenchmarkingProps {
  timeRange: string
}

export function CompetitorBenchmarking({ timeRange }: CompetitorBenchmarkingProps) {
  const benchmarkData = [
    {
      metric: "Cost Per Click",
      yourValue: 2.45,
      competitors: [
        { name: "Nike", value: 3.2, trend: "up" },
        { name: "Adidas", value: 2.8, trend: "down" },
        { name: "Under Armour", value: 2.15, trend: "up" },
      ],
      industryAvg: 2.65,
      unit: "$",
      position: "2nd",
      insight: "You're performing 8% better than industry average",
    },
    {
      metric: "Click-Through Rate",
      yourValue: 4.2,
      competitors: [
        { name: "Nike", value: 5.1, trend: "up" },
        { name: "Adidas", value: 3.8, trend: "stable" },
        { name: "Under Armour", value: 3.2, trend: "down" },
      ],
      industryAvg: 3.9,
      unit: "%",
      position: "2nd",
      insight: "Strong performance, but Nike leads by 0.9%",
    },
    {
      metric: "Conversion Rate",
      yourValue: 3.8,
      competitors: [
        { name: "Nike", value: 4.2, trend: "up" },
        { name: "Adidas", value: 3.1, trend: "up" },
        { name: "Under Armour", value: 2.9, trend: "stable" },
      ],
      industryAvg: 3.4,
      unit: "%",
      position: "2nd",
      insight: "Above industry average, closing gap with Nike",
    },
    {
      metric: "Return on Ad Spend",
      yourValue: 4.8,
      competitors: [
        { name: "Nike", value: 5.2, trend: "up" },
        { name: "Adidas", value: 4.1, trend: "down" },
        { name: "Under Armour", value: 3.9, trend: "stable" },
      ],
      industryAvg: 4.3,
      unit: "x",
      position: "2nd",
      insight: "Strong ROAS, outperforming 2 of 3 competitors",
    },
  ]

  const competitorCampaigns = [
    {
      competitor: "Nike",
      campaign: "Just Do It - Summer 2024",
      status: "Active",
      spend: "$2.4M",
      performance: "High",
      threat: "High",
      description: "Major push targeting fitness enthusiasts with video-heavy creative",
      metrics: { ctr: 5.1, cvr: 4.2, cpc: 3.2 },
    },
    {
      competitor: "Adidas",
      campaign: "Impossible is Nothing - Sustainability",
      status: "Active",
      spend: "$1.8M",
      performance: "Medium",
      threat: "Medium",
      description: "Eco-focused campaign emphasizing sustainable manufacturing",
      metrics: { ctr: 3.8, cvr: 3.1, cpc: 2.8 },
    },
    {
      competitor: "Under Armour",
      campaign: "Will Finds a Way - Tech Innovation",
      status: "Ending Soon",
      spend: "$950K",
      performance: "Low",
      threat: "Low",
      description: "Technology-focused campaign highlighting smart fabric innovations",
      metrics: { ctr: 3.2, cvr: 2.9, cpc: 2.15 },
    },
  ]

  return (
    <div className="space-y-6">
      {/* Benchmark Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Metrics Leading</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">1</div>
            <p className="text-xs text-muted-foreground">Out of 4 key metrics</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Position</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">2nd</div>
            <p className="text-xs text-muted-foreground">Across all competitors</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Performance Gap</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">-8.2%</div>
            <p className="text-xs text-muted-foreground">Behind market leader</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Competitive Threats</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">2</div>
            <p className="text-xs text-muted-foreground">High-threat campaigns</p>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Benchmarking */}
      <Card>
        <CardHeader>
          <CardTitle>Performance Benchmarking</CardTitle>
          <CardDescription>How you compare against competitors across key metrics</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {benchmarkData.map((benchmark, index) => (
              <div key={index} className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium">{benchmark.metric}</h3>
                    <p className="text-sm text-muted-foreground">{benchmark.insight}</p>
                  </div>
                  <Badge variant="outline">#{benchmark.position}</Badge>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  {/* Your Performance */}
                  <div className="p-3 border rounded-lg bg-blue-50 dark:bg-blue-950/20">
                    <div className="text-sm font-medium text-blue-900 dark:text-blue-100">You</div>
                    <div className="text-lg font-bold">
                      {benchmark.unit === "$" ? "$" : ""}
                      {benchmark.yourValue}
                      {benchmark.unit !== "$" ? benchmark.unit : ""}
                    </div>
                  </div>

                  {/* Competitors */}
                  {benchmark.competitors.map((competitor, compIndex) => (
                    <div key={compIndex} className="p-3 border rounded-lg">
                      <div className="flex items-center justify-between mb-1">
                        <div className="text-sm font-medium">{competitor.name}</div>
                        {competitor.trend === "up" && <TrendingUp className="h-3 w-3 text-green-500" />}
                        {competitor.trend === "down" && <TrendingDown className="h-3 w-3 text-red-500" />}
                      </div>
                      <div className="text-lg font-bold">
                        {benchmark.unit === "$" ? "$" : ""}
                        {competitor.value}
                        {benchmark.unit !== "$" ? benchmark.unit : ""}
                      </div>
                    </div>
                  ))}
                </div>

                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  <span>
                    Industry Average:{" "}
                    <strong>
                      {benchmark.unit === "$" ? "$" : ""}
                      {benchmark.industryAvg}
                      {benchmark.unit !== "$" ? benchmark.unit : ""}
                    </strong>
                  </span>
                  <div className="flex-1">
                    <Progress
                      value={
                        (benchmark.yourValue /
                          Math.max(...benchmark.competitors.map((c) => c.value), benchmark.yourValue)) *
                        100
                      }
                      className="h-2"
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Active Competitor Campaigns */}
      <Card>
        <CardHeader>
          <CardTitle>Active Competitor Campaigns</CardTitle>
          <CardDescription>Monitor competitor campaign activity and performance</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {competitorCampaigns.map((campaign, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-medium">{campaign.campaign}</h3>
                      <Badge variant="outline">{campaign.competitor}</Badge>
                      <Badge
                        variant={
                          campaign.status === "Active"
                            ? "default"
                            : campaign.status === "Ending Soon"
                              ? "secondary"
                              : "outline"
                        }
                      >
                        {campaign.status}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">{campaign.description}</p>
                    <div className="text-sm">
                      <strong>Spend:</strong> {campaign.spend}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge
                      variant={
                        campaign.threat === "High"
                          ? "destructive"
                          : campaign.threat === "Medium"
                            ? "secondary"
                            : "outline"
                      }
                    >
                      {campaign.threat} Threat
                    </Badge>
                    <Badge
                      variant={
                        campaign.performance === "High"
                          ? "default"
                          : campaign.performance === "Medium"
                            ? "secondary"
                            : "outline"
                      }
                    >
                      {campaign.performance} Performance
                    </Badge>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4 mb-3">
                  <div className="text-center p-2 bg-muted/50 rounded">
                    <div className="text-sm text-muted-foreground">CTR</div>
                    <div className="font-medium">{campaign.metrics.ctr}%</div>
                  </div>
                  <div className="text-center p-2 bg-muted/50 rounded">
                    <div className="text-sm text-muted-foreground">CVR</div>
                    <div className="font-medium">{campaign.metrics.cvr}%</div>
                  </div>
                  <div className="text-center p-2 bg-muted/50 rounded">
                    <div className="text-sm text-muted-foreground">CPC</div>
                    <div className="font-medium">${campaign.metrics.cpc}</div>
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button variant="outline" size="sm">
                    View Details
                  </Button>
                  <Button variant="outline" size="sm">
                    Counter Strategy
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
