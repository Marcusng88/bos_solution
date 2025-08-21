"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Eye, Edit, Pause, Play, MoreHorizontal } from "lucide-react"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"

interface CampaignOverviewProps {
  timeRange: string
}

const campaigns = [
  {
    id: 1,
    name: "Summer Sale 2024",
    platform: "Facebook",
    status: "active",
    budget: 5000,
    spent: 3247,
    clicks: 12456,
    conversions: 678,
    ctr: 3.2,
    cpc: 0.26,
    conversionRate: 5.4,
    performance: "excellent",
  },
  {
    id: 2,
    name: "Product Launch Campaign",
    platform: "Instagram",
    status: "active",
    budget: 3000,
    spent: 2890,
    clicks: 8934,
    conversions: 234,
    ctr: 2.8,
    cpc: 0.32,
    conversionRate: 2.6,
    performance: "good",
  },
  {
    id: 5,
    name: "Holiday Promotion",
    platform: "Facebook",
    status: "completed",
    budget: 6000,
    spent: 5890,
    clicks: 15678,
    conversions: 890,
    ctr: 4.1,
    cpc: 0.38,
    conversionRate: 5.7,
    performance: "excellent",
  },
]

export function CampaignOverview({ timeRange }: CampaignOverviewProps) {
  const getPerformanceBadge = (performance: string) => {
    switch (performance) {
      case "excellent":
        return <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100">Excellent</Badge>
      case "good":
        return <Badge className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100">Good</Badge>
      case "average":
        return <Badge className="bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100">Average</Badge>
      default:
        return <Badge variant="secondary">Unknown</Badge>
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "active":
        return <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100">Active</Badge>
      case "paused":
        return <Badge className="bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-100">Paused</Badge>
      case "completed":
        return <Badge className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100">Completed</Badge>
      default:
        return <Badge variant="secondary">Unknown</Badge>
    }
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {campaigns.map((campaign) => (
          <Card key={campaign.id}>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <CardTitle className="text-lg">{campaign.name}</CardTitle>
                  <CardDescription>{campaign.platform} Campaign</CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  {getStatusBadge(campaign.status)}
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="sm">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem>
                        <Eye className="mr-2 h-4 w-4" />
                        View Details
                      </DropdownMenuItem>
                      <DropdownMenuItem>
                        <Edit className="mr-2 h-4 w-4" />
                        Edit Campaign
                      </DropdownMenuItem>
                      <DropdownMenuItem>
                        {campaign.status === "active" ? (
                          <>
                            <Pause className="mr-2 h-4 w-4" />
                            Pause Campaign
                          </>
                        ) : (
                          <>
                            <Play className="mr-2 h-4 w-4" />
                            Resume Campaign
                          </>
                        )}
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Budget Progress */}
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Budget Used</span>
                  <span>
                    ${campaign.spent.toLocaleString()} / ${campaign.budget.toLocaleString()}
                  </span>
                </div>
                <Progress value={(campaign.spent / campaign.budget) * 100} className="h-2" />
              </div>

              {/* Key Metrics */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">Clicks</p>
                  <p className="text-lg font-semibold">{campaign.clicks.toLocaleString()}</p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">Conversions</p>
                  <p className="text-lg font-semibold">{campaign.conversions.toLocaleString()}</p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">CTR</p>
                  <p className="text-lg font-semibold">{campaign.ctr}%</p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">Conv. Rate</p>
                  <p className="text-lg font-semibold">{campaign.conversionRate}%</p>
                </div>
              </div>

              {/* Performance & CPC */}
              <div className="flex items-center justify-between pt-2 border-t">
                <div className="flex items-center gap-2">
                  <span className="text-sm text-muted-foreground">Performance:</span>
                  {getPerformanceBadge(campaign.performance)}
                </div>
                <div className="text-right">
                  <p className="text-sm text-muted-foreground">Avg. CPC</p>
                  <p className="font-semibold">${campaign.cpc}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
