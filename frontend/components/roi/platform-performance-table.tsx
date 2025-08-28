"use client"

import { useState, useEffect } from "react"
import { useUser } from "@clerk/nextjs"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { roiApi, type TimeRange } from "@/lib/api-client"
import { TrendingUp, TrendingDown, DollarSign, Target, Eye, ThumbsUp } from "lucide-react"

interface PlatformPerformanceTableProps {
  range?: TimeRange
}

interface PlatformData {
  platform: string
  revenue: number
  spend: number
  roi: number
  views: number
  engagement: number
  posts: number
}

export default function PlatformPerformanceTable({ range = "30d" }: PlatformPerformanceTableProps) {
  const { user } = useUser()
  const [data, setData] = useState<PlatformData[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user) return

    const fetchData = async () => {
      try {
        setLoading(true)
        console.log(`🚀 Fetching platform performance for range: ${range}`)
        
        const response = await roiApi.channelPerformance(range)
        console.log(`📊 Platform performance response:`, response)
        
        if ('all_data' in response) {
          const allData = response.all_data
          console.log(`📊 Total rows received: ${allData.length}`)
          
          // Filter data based on the selected range
          const filteredData = filterDataByRange(allData, range)
          console.log(`📊 Filtered data for ${range}: ${filteredData.length} rows`)
          
          // Group by platform and calculate metrics
          const platformMetrics = calculatePlatformMetrics(filteredData)
          setData(platformMetrics)
        } else {
          console.error('❌ Unexpected response format:', response)
          setData([])
        }
      } catch (error) {
        console.error('Failed to fetch platform performance:', error)
        setData([])
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [user, range])

  // Frontend filtering function
  const filterDataByRange = (allData: any[], selectedRange: TimeRange) => {
    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    
    let startDate: Date
    switch (selectedRange) {
      case '7d':
        startDate = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000)
        break
      case '14d':
        startDate = new Date(today.getTime() - 14 * 24 * 60 * 60 * 1000)
        break
      case '30d':
        startDate = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000)
        break
      case '90d':
        startDate = new Date(today.getTime() - 90 * 24 * 60 * 60 * 1000)
        break
      default:
        startDate = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000)
    }
    
    return allData.filter(row => {
      const rowDate = new Date(row.created_at)
      return rowDate >= startDate && rowDate < today
    })
  }

  // Calculate platform metrics
  const calculatePlatformMetrics = (filteredData: any[]): PlatformData[] => {
    if (!filteredData || filteredData.length === 0) {
      return []
    }
    
    const platformMap = new Map<string, PlatformData>()
    
    filteredData.forEach(row => {
      const platform = row.platform || 'Unknown'
      
      if (!platformMap.has(platform)) {
        platformMap.set(platform, {
          platform,
          revenue: 0,
          spend: 0,
          roi: 0,
          views: 0,
          engagement: 0,
          posts: 0
        })
      }
      
      const current = platformMap.get(platform)!
      current.revenue += parseFloat(row.revenue_generated || 0)
      current.spend += parseFloat(row.ad_spend || 0)
      current.views += parseInt(row.views || 0)
      current.engagement += parseInt(row.likes || 0) + parseInt(row.comments || 0) + parseInt(row.shares || 0)
      current.posts += 1
    })
    
    // Calculate ROI for each platform
    platformMap.forEach(platform => {
      platform.roi = platform.spend > 0 ? ((platform.revenue - platform.spend) / platform.spend) * 100 : 0
    })
    
    // Sort by revenue descending
    return Array.from(platformMap.values()).sort((a, b) => b.revenue - a.revenue)
  }

  const getROIColor = (roi: number) => {
    if (roi >= 20) return "text-green-600"
    if (roi >= 10) return "text-yellow-600"
    if (roi >= 0) return "text-orange-600"
    return "text-red-600"
  }

  const getROIIcon = (roi: number) => {
    if (roi >= 10) return <TrendingUp className="h-4 w-4 text-green-600" />
    if (roi >= 0) return <TrendingUp className="h-4 w-4 text-yellow-600" />
    return <TrendingDown className="h-4 w-4 text-red-600" />
  }

  if (!user) {
    return <div className="text-center py-8">Please sign in to view platform performance</div>
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Target className="h-5 w-5" />
          Platform Performance ({range})
        </CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="text-center py-8">Loading platform performance data...</div>
        ) : data.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            No platform performance data available for the selected period.
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Platform</TableHead>
                <TableHead className="text-right">Revenue</TableHead>
                <TableHead className="text-right">Spend</TableHead>
                <TableHead className="text-right">ROI</TableHead>
                <TableHead className="text-right">Views</TableHead>
                <TableHead className="text-right">Engagement</TableHead>
                <TableHead className="text-right">Posts</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.map((platform) => (
                <TableRow key={platform.platform}>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline">{platform.platform}</Badge>
                    </div>
                  </TableCell>
                  <TableCell className="text-right font-medium">
                    ${platform.revenue.toLocaleString()}
                  </TableCell>
                  <TableCell className="text-right">
                    ${platform.spend.toLocaleString()}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end gap-1">
                      {getROIIcon(platform.roi)}
                      <span className={getROIColor(platform.roi)}>
                        {platform.roi.toFixed(1)}%
                      </span>
                    </div>
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end gap-1">
                      <Eye className="h-4 w-4 text-muted-foreground" />
                      {platform.views.toLocaleString()}
                    </div>
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end gap-1">
                      <ThumbsUp className="h-4 w-4 text-muted-foreground" />
                      {platform.engagement.toLocaleString()}
                    </div>
                  </TableCell>
                  <TableCell className="text-right">
                    {platform.posts}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  )
}
