"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useToast } from "@/hooks/use-toast"
import { Search, Eye, Edit, Pause, Play, Trash2, MoreHorizontal } from "lucide-react"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"

const allCampaigns = [
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
    conversionRate: 5.4,
    startDate: "2024-01-01",
    endDate: "2024-01-31",
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
    conversionRate: 2.6,
    startDate: "2024-01-05",
    endDate: "2024-01-25",
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
    conversionRate: 5.7,
    startDate: "2023-12-01",
    endDate: "2023-12-31",
  },
  {
    id: 6,
    name: "Retargeting Campaign",
    platform: "Instagram",
    status: "active",
    budget: 1500,
    spent: 890,
    clicks: 2345,
    conversions: 156,
    ctr: 6.2,
    conversionRate: 6.6,
    startDate: "2024-01-15",
    endDate: "2024-02-15",
  },
]

export function CampaignList() {
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")
  const [platformFilter, setPlatformFilter] = useState("all")
  const { toast } = useToast()

  const filteredCampaigns = allCampaigns.filter((campaign) => {
    const matchesSearch = campaign.name.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === "all" || campaign.status === statusFilter
    const matchesPlatform = platformFilter === "all" || campaign.platform === platformFilter
    return matchesSearch && matchesStatus && matchesPlatform
  })

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

  const handleAction = (action: string, campaignName: string) => {
    toast({
      title: `Campaign ${action}`,
      description: `${campaignName} has been ${action.toLowerCase()}.`,
    })
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>All Campaigns</CardTitle>
        <CardDescription>Manage and monitor all your marketing campaigns</CardDescription>
      </CardHeader>
      <CardContent>
        {/* Filters */}
        <div className="flex gap-4 mb-6">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search campaigns..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-32">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="active">Active</SelectItem>
              <SelectItem value="paused">Paused</SelectItem>
              <SelectItem value="completed">Completed</SelectItem>
            </SelectContent>
          </Select>
          <Select value={platformFilter} onValueChange={setPlatformFilter}>
            <SelectTrigger className="w-32">
              <SelectValue placeholder="Platform" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Platforms</SelectItem>
              <SelectItem value="Facebook">Facebook</SelectItem>
              <SelectItem value="Instagram">Instagram</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Campaigns Table */}
        <div className="space-y-4">
          {filteredCampaigns.map((campaign) => (
            <Card key={campaign.id} className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex-1 space-y-2">
                  <div className="flex items-center gap-3">
                    <h3 className="font-semibold">{campaign.name}</h3>
                    {getStatusBadge(campaign.status)}
                    <Badge variant="outline" className="text-xs">
                      {campaign.platform}
                    </Badge>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-6 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Budget</p>
                      <p className="font-medium">${campaign.budget.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Spent</p>
                      <p className="font-medium">${campaign.spent.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Clicks</p>
                      <p className="font-medium">{campaign.clicks.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Conversions</p>
                      <p className="font-medium">{campaign.conversions.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">CTR</p>
                      <p className="font-medium">{campaign.ctr}%</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Conv. Rate</p>
                      <p className="font-medium">{campaign.conversionRate}%</p>
                    </div>
                  </div>
                </div>

                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="sm">
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem onClick={() => handleAction("viewed", campaign.name)}>
                      <Eye className="mr-2 h-4 w-4" />
                      View Details
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => handleAction("edited", campaign.name)}>
                      <Edit className="mr-2 h-4 w-4" />
                      Edit Campaign
                    </DropdownMenuItem>
                    <DropdownMenuItem
                      onClick={() => handleAction(campaign.status === "active" ? "paused" : "resumed", campaign.name)}
                    >
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
                    <DropdownMenuItem onClick={() => handleAction("deleted", campaign.name)}>
                      <Trash2 className="mr-2 h-4 w-4" />
                      Delete Campaign
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </Card>
          ))}
        </div>

        {filteredCampaigns.length === 0 && (
          <div className="text-center py-8 text-muted-foreground">
            <p>No campaigns found matching your criteria</p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
