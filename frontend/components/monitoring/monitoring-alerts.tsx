"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { TrendingUp, MessageSquare, DollarSign, Users, Loader2, AlertCircle, Eye } from "lucide-react"
import { apiClient, handleApiError } from "@/lib/api-client"
import { useToast } from "@/hooks/use-toast"

interface MonitoringAlert {
  id: string
  alert_type: string
  priority: 'low' | 'medium' | 'high' | 'critical'
  title: string
  message: string
  is_read: boolean
  is_dismissed: boolean
  created_at: string
  competitor_id?: string
  alert_metadata?: any
}

interface MonitoringAlertsProps {
  userId: string
}

// Icon mapping for different alert types
const getAlertIcon = (alertType: string) => {
  switch (alertType.toLowerCase()) {
    case 'content':
    case 'new_post':
      return TrendingUp
    case 'pricing':
    case 'price_change':
      return DollarSign
    case 'social':
    case 'engagement':
      return MessageSquare
    case 'audience':
      return Users
    default:
      return AlertCircle
  }
}

export function MonitoringAlerts({ userId }: MonitoringAlertsProps) {
  const [alerts, setAlerts] = useState<MonitoringAlert[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [markingAsRead, setMarkingAsRead] = useState<string | null>(null)
  const { toast } = useToast()

  // Fetch alerts on component mount
  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        setIsLoading(true)
        const response = await apiClient.getMonitoringAlerts(userId)
        
        if (Array.isArray(response)) {
          // Sort by created_at descending (newest first)
          const sortedAlerts = response.sort((a: MonitoringAlert, b: MonitoringAlert) => 
            new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
          )
          setAlerts(sortedAlerts)
        }
      } catch (error) {
        console.error('Error fetching alerts:', error)
        toast({
          title: "Error",
          description: handleApiError(error),
          variant: "destructive",
        })
      } finally {
        setIsLoading(false)
      }
    }

    fetchAlerts()
  }, [userId]) // Remove toast from dependencies

  // Mark alert as read
  const markAsRead = async (alertId: string) => {
    try {
      setMarkingAsRead(alertId)
      await apiClient.markAlertAsRead(userId, alertId)
      
      // Update local state
      setAlerts(prev => prev.map(alert => 
        alert.id === alertId ? { ...alert, is_read: true } : alert
      ))
      
      toast({
        title: "Success",
        description: "Alert marked as read",
      })
    } catch (error) {
      console.error('Error marking alert as read:', error)
      toast({
        title: "Error",
        description: handleApiError(error),
        variant: "destructive",
      })
    } finally {
      setMarkingAsRead(null)
    }
  }

  // Format timestamp
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    
    if (diffMins < 1) return "Just now"
    if (diffMins < 60) return `${diffMins} minutes ago`
    const diffHours = Math.floor(diffMins / 60)
    if (diffHours < 24) return `${diffHours} hours ago`
    const diffDays = Math.floor(diffHours / 24)
    return `${diffDays} days ago`
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "critical":
        return "bg-red-200 text-red-900 border-red-300"
      case "high":
        return "bg-red-100 text-red-800 border-red-200"
      case "medium":
        return "bg-orange-100 text-orange-800 border-orange-200"
      case "low":
        return "bg-blue-100 text-blue-800 border-blue-200"
      default:
        return "bg-gray-100 text-gray-800 border-gray-200"
    }
  }

  const getBorderColor = (priority: string) => {
    switch (priority) {
      case "critical":
        return "border-l-red-600"
      case "high":
        return "border-l-red-500"
      case "medium":
        return "border-l-orange-500"
      case "low":
        return "border-l-blue-500"
      default:
        return "border-l-gray-500"
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-32">
        <Loader2 className="h-6 w-6 animate-spin" />
      </div>
    )
  }

  if (alerts.length === 0) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-8">
          <AlertCircle className="h-12 w-12 text-muted-foreground mb-4" />
          <h3 className="text-lg font-medium mb-2">No alerts yet</h3>
          <p className="text-muted-foreground text-center">
            When competitors are detected making changes, alerts will appear here.
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      {alerts.map((alert) => {
        const Icon = getAlertIcon(alert.alert_type)
        return (
          <Card 
            key={alert.id} 
            className={`border-l-4 ${getBorderColor(alert.priority)} ${
              !alert.is_read ? 'bg-blue-50/30' : ''
            }`}
          >
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-blue-50 rounded-lg">
                    <Icon className="h-5 w-5 text-blue-600" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <CardTitle className="text-lg">{alert.title}</CardTitle>
                      <Badge className={getPriorityColor(alert.priority)}>
                        {alert.priority}
                      </Badge>
                      {!alert.is_read && (
                        <Badge variant="secondary" className="text-xs">New</Badge>
                      )}
                    </div>
                    <CardDescription className="text-sm text-muted-foreground">
                      {alert.alert_metadata?.competitor_name || 'Unknown Competitor'} • {formatTimestamp(alert.created_at)}
                    </CardDescription>
                  </div>
                </div>
                <div className="flex gap-2">
                  {!alert.is_read && (
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={() => markAsRead(alert.id)}
                      disabled={markingAsRead === alert.id}
                    >
                      {markingAsRead === alert.id ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <>
                          <Eye className="h-4 w-4 mr-1" />
                          Mark Read
                        </>
                      )}
                    </Button>
                  )}
                </div>
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              <p className="text-sm">{alert.message}</p>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
