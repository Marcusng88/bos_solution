"use client"

import { useState, useEffect } from "react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Progress } from "@/components/ui/progress"
import { 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Target, 
  FileText, 
  Globe, 
  BarChart3,
  Eye,
  Brain,
  Lightbulb,
  AlertCircle,
  Info
} from "lucide-react"
import { useUser } from "@clerk/nextjs"

interface AIInsight {
  type: "opportunity" | "threat" | "trend"
  title: string
  description: string
  impact: "Low" | "Medium" | "High"
  confidence: number
  data?: any
}

interface AIInsightsDetailsDialogProps {
  insight: AIInsight
  trigger: React.ReactNode
}

interface MonitoringData {
  id: string
  platform: string
  post_type: string
  sentiment_score: number
  detected_at: string
  content_text: string
  competitor_name: string
}

interface MonitoringAlert {
  id: string
  alert_type: string
  priority: "low" | "medium" | "high" | "critical"
  title: string
  message: string
  created_at: string
  competitor_name: string
}

export function AIInsightsDetailsDialog({ insight, trigger }: AIInsightsDetailsDialogProps) {
  const { user } = useUser()
  const [open, setOpen] = useState(false)
  const [monitoringData, setMonitoringData] = useState<MonitoringData[]>([])
  const [alerts, setAlerts] = useState<MonitoringAlert[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (open && user?.id) {
      fetchInsightData()
    }
  }, [open, user?.id])

  const fetchInsightData = async () => {
    if (!user?.id) return
    
    setLoading(true)
    try {
      // Fetch monitoring data
      const monitoringResponse = await fetch('/api/v1/monitoring/data', {
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': user.id,
        },
      })
      
      if (monitoringResponse.ok) {
        const monitoringData = await monitoringResponse.json()
        setMonitoringData(monitoringData)
      }

      // Fetch monitoring alerts
      const alertsResponse = await fetch('/api/v1/monitoring/alerts', {
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': user.id,
        },
      })
      
      if (alertsResponse.ok) {
        const alertsData = await alertsResponse.json()
        setAlerts(alertsData)
      }
    } catch (error) {
      console.error('Error fetching insight data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getInsightIcon = (type: string) => {
    switch (type) {
      case "opportunity":
        return <CheckCircle className="h-6 w-6 text-green-500" />
      case "threat":
        return <AlertTriangle className="h-6 w-6 text-orange-500" />
      case "trend":
        return <TrendingUp className="h-6 w-6 text-blue-500" />
      default:
        return <Info className="h-6 w-6 text-gray-500" />
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "critical":
        return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
      case "high":
        return "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200"
      case "medium":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200"
      case "low":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200"
    }
  }

  const getPlatformIcon = (platform: string) => {
    switch (platform.toLowerCase()) {
      case "youtube":
        return <Globe className="h-4 w-4 text-red-500" />
      case "instagram":
        return <Globe className="h-4 w-4 text-pink-500" />
      case "facebook":
        return <Globe className="h-4 w-4 text-blue-500" />
      case "twitter":
        return <Globe className="h-4 w-4 text-blue-400" />
      case "linkedin":
        return <Globe className="h-4 w-4 text-blue-600" />
      case "browser":
        return <Globe className="h-4 w-4 text-gray-500" />
      default:
        return <Globe className="h-4 w-4 text-gray-400" />
    }
  }

  const getSentimentColor = (score: number) => {
    if (score > 0.3) return "text-green-600"
    if (score < -0.3) return "text-red-600"
    return "text-yellow-600"
  }

  const getSentimentLabel = (score: number) => {
    if (score > 0.3) return "Positive"
    if (score < -0.3) return "Negative"
    return "Neutral"
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger}
      </DialogTrigger>
      <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center gap-3">
            {getInsightIcon(insight.type)}
            <div>
              <DialogTitle className="text-xl">{insight.title}</DialogTitle>
              <DialogDescription className="text-base">
                {insight.description}
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <div className="space-y-6">
          {/* Insight Summary */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-5 w-5 text-blue-600" />
                Insight Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-foreground">{insight.impact}</div>
                  <p className="text-sm text-muted-foreground">Impact Level</p>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-foreground">{insight.confidence}%</div>
                  <p className="text-sm text-muted-foreground">Confidence Score</p>
                  <Progress value={insight.confidence} className="w-full mt-2" />
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-foreground capitalize">{insight.type}</div>
                  <p className="text-sm text-muted-foreground">Insight Type</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Detailed Analysis Tabs */}
          <Tabs defaultValue="data" className="w-full">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="data">Raw Data</TabsTrigger>
              <TabsTrigger value="alerts">Alerts</TabsTrigger>
              <TabsTrigger value="trends">Trends</TabsTrigger>
              <TabsTrigger value="actions">Actions</TabsTrigger>
            </TabsList>

            <TabsContent value="data" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="h-5 w-5 text-blue-600" />
                    Monitoring Data Analysis
                  </CardTitle>
                  <CardDescription>
                    Raw data that contributed to this insight
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {loading ? (
                    <div className="text-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                      <p className="mt-2 text-muted-foreground">Loading data...</p>
                    </div>
                  ) : monitoringData.length > 0 ? (
                    <div className="space-y-4">
                      {monitoringData.slice(0, 10).map((data, index) => (
                        <div key={index} className="border rounded-lg p-4">
                          <div className="flex items-start justify-between mb-3">
                            <div className="flex items-center gap-2">
                              {getPlatformIcon(data.platform)}
                              <Badge variant="outline">{data.platform}</Badge>
                              <Badge variant="outline">{data.post_type}</Badge>
                            </div>
                            <div className="text-right">
                              <div className="text-sm text-muted-foreground">
                                {new Date(data.detected_at).toLocaleDateString()}
                              </div>
                              <div className={`text-sm font-medium ${getSentimentColor(data.sentiment_score)}`}>
                                {getSentimentLabel(data.sentiment_score)} ({data.sentiment_score.toFixed(2)})
                              </div>
                            </div>
                          </div>
                          <p className="text-sm text-muted-foreground line-clamp-3">
                            {data.content_text}
                          </p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-muted-foreground">
                      <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>No monitoring data available</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="alerts" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <AlertCircle className="h-5 w-5 text-orange-600" />
                    Related Alerts
                  </CardTitle>
                  <CardDescription>
                    Monitoring alerts that support this insight
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {alerts.length > 0 ? (
                    <div className="space-y-4">
                      {alerts.slice(0, 10).map((alert, index) => (
                        <div key={index} className="border rounded-lg p-4">
                          <div className="flex items-start justify-between mb-2">
                            <div className="flex items-center gap-2">
                              <Badge className={getPriorityColor(alert.priority)}>
                                {alert.priority}
                              </Badge>
                              <Badge variant="outline">{alert.alert_type}</Badge>
                            </div>
                            <div className="text-sm text-muted-foreground">
                              {new Date(alert.created_at).toLocaleDateString()}
                            </div>
                          </div>
                          <h4 className="font-medium mb-2">{alert.title}</h4>
                          <p className="text-sm text-muted-foreground">{alert.message}</p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-muted-foreground">
                      <AlertCircle className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>No alerts available</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="trends" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-green-600" />
                    Trend Analysis
                  </CardTitle>
                  <CardDescription>
                    Patterns and trends identified from the data
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <h4 className="font-medium">Platform Distribution</h4>
                      {monitoringData.length > 0 && (
                        <div className="space-y-2">
                          {Object.entries(
                            monitoringData.reduce((acc: Record<string, number>, data) => {
                              acc[data.platform] = (acc[data.platform] || 0) + 1
                              return acc
                            }, {})
                          ).map(([platform, count]) => (
                            <div key={platform} className="flex items-center justify-between">
                              <span className="text-sm">{platform}</span>
                              <Badge variant="secondary">{count}</Badge>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                    <div className="space-y-4">
                      <h4 className="font-medium">Sentiment Trends</h4>
                      {monitoringData.length > 0 && (
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-sm">Positive</span>
                            <Badge variant="secondary">
                              {monitoringData.filter(d => d.sentiment_score > 0.3).length}
                            </Badge>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-sm">Neutral</span>
                            <Badge variant="secondary">
                              {monitoringData.filter(d => d.sentiment_score >= -0.3 && d.sentiment_score <= 0.3).length}
                            </Badge>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-sm">Negative</span>
                            <Badge variant="secondary">
                              {monitoringData.filter(d => d.sentiment_score < -0.3).length}
                            </Badge>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="actions" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Lightbulb className="h-5 w-5 text-yellow-600" />
                    Recommended Actions
                  </CardTitle>
                  <CardDescription>
                    Strategic actions based on this competitive insight
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {insight.type === "opportunity" && (
                      <div className="p-4 border border-green-200 bg-green-50 dark:bg-green-950/20 rounded-lg">
                        <h4 className="font-medium text-green-800 dark:text-green-200 mb-2">
                          🎯 Seize the Opportunity
                        </h4>
                        <ul className="text-sm text-green-700 dark:text-green-300 space-y-1">
                          <li>• Analyze competitor content gaps in this area</li>
                          <li>• Develop content strategy to capitalize on the trend</li>
                          <li>• Monitor competitor response to your actions</li>
                        </ul>
                      </div>
                    )}
                    
                    {insight.type === "threat" && (
                      <div className="p-4 border border-red-200 bg-red-50 dark:bg-red-950/20 rounded-lg">
                        <h4 className="font-medium text-red-800 dark:text-red-200 mb-2">
                          ⚠️ Mitigate the Threat
                        </h4>
                        <ul className="text-sm text-red-700 dark:text-red-300 space-y-1">
                          <li>• Assess your current competitive position</li>
                          <li>• Develop defensive strategies</li>
                          <li>• Strengthen your unique value propositions</li>
                        </ul>
                      </div>
                    )}
                    
                    {insight.type === "trend" && (
                      <div className="p-4 border border-blue-200 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
                        <h4 className="font-medium text-blue-800 dark:text-blue-200 mb-2">
                          📈 Follow the Trend
                        </h4>
                        <ul className="text-sm text-blue-700 dark:text-blue-300 space-y-1">
                          <li>• Adapt your strategy to align with the trend</li>
                          <li>• Identify early adoption opportunities</li>
                          <li>• Monitor trend evolution and competitor responses</li>
                        </ul>
                      </div>
                    )}

                    <div className="p-4 border rounded-lg">
                      <h4 className="font-medium mb-2">Immediate Actions</h4>
                      <div className="space-y-2">
                        <Button size="sm" className="w-full">
                          <Target className="h-4 w-4 mr-2" />
                          Set Up Enhanced Monitoring
                        </Button>
                        <Button size="sm" variant="outline" className="w-full">
                          <BarChart3 className="h-4 w-4 mr-2" />
                          Generate Detailed Report
                        </Button>
                        <Button size="sm" variant="outline" className="w-full">
                          <Clock className="h-4 w-4 mr-2" />
                          Schedule Follow-up Analysis
                        </Button>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </DialogContent>
    </Dialog>
  )
}
