"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useApiClient, handleApiError } from "@/lib/api-client"
import { AlertTriangle, Bell, Clock, CheckCircle, X } from "lucide-react"

interface OptimizationAlert {
  id: string
  campaign_name: string
  alert_type: string
  priority: 'low' | 'medium' | 'high' | 'critical'
  title: string
  message: string
  recommendation: string
  created_at: string
  is_read: boolean
}

export function AlertsWidget() {
  const [alerts, setAlerts] = useState<OptimizationAlert[]>([])
  const [loading, setLoading] = useState(true)
  const { apiClient, userId } = useApiClient()

  useEffect(() => {
    fetchAlerts()
  }, [])

  const fetchAlerts = async () => {
    try {
      const alertsData = await apiClient.getOptimizationAlerts(userId, false, 50)
      setAlerts(alertsData)
    } catch (error) {
      console.error('Failed to fetch alerts:', handleApiError(error))
    } finally {
      setLoading(false)
    }
  }

  const handleMarkAsRead = async (alertId: string) => {
    try {
      await apiClient.markOptimizationAlertAsRead(userId, alertId)
      setAlerts(prev => prev.map(alert => 
        alert.id === alertId ? { ...alert, is_read: true } : alert
      ))
    } catch (error) {
      console.error('Failed to mark alert as read:', handleApiError(error))
    }
  }

  const handleDismissAlert = async (alertId: string) => {
    try {
      // For now, just remove from UI - you might want to add a dismiss API endpoint
      setAlerts(prev => prev.filter(alert => alert.id !== alertId))
    } catch (error) {
      console.error('Failed to dismiss alert:', handleApiError(error))
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'text-red-600 bg-red-50 border-red-200'
      case 'high':
        return 'text-orange-600 bg-orange-50 border-orange-200'
      case 'medium':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      default:
        return 'text-blue-600 bg-blue-50 border-blue-200'
    }
  }

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'critical':
      case 'high':
        return <AlertTriangle className="h-4 w-4" />
      case 'medium':
        return <Clock className="h-4 w-4" />
      default:
        return <Bell className="h-4 w-4" />
    }
  }

  const unreadCount = alerts.filter(alert => !alert.is_read).length

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Optimization Alerts</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5" />
            Optimization Alerts
          </CardTitle>
          {unreadCount > 0 && (
            <Badge variant="destructive" className="rounded-full">
              {unreadCount}
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent>
        {alerts.length === 0 ? (
          <div className="text-center py-8">
            <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-3" />
            <p className="text-sm text-muted-foreground">No active alerts</p>
            <p className="text-xs text-muted-foreground">Your campaigns are running smoothly!</p>
          </div>
        ) : (
          <ScrollArea className="h-80">
            <div className="space-y-3">
              {alerts.map((alert) => (
                <div
                  key={alert.id}
                  className={`p-3 rounded-lg border transition-all duration-200 ${
                    alert.is_read ? 'opacity-60' : ''
                  } ${getPriorityColor(alert.priority)}`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-start gap-2 flex-1">
                      {getPriorityIcon(alert.priority)}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-medium text-sm truncate">{alert.title}</h4>
                          <Badge variant="outline" className="text-xs">
                            {alert.priority}
                          </Badge>
                        </div>
                        <p className="text-xs mb-2 leading-relaxed">{alert.message}</p>
                        {alert.recommendation && (
                          <div className="text-xs p-2 rounded bg-white/50 border border-current/20">
                            <span className="font-medium">Recommendation: </span>
                            {alert.recommendation}
                          </div>
                        )}
                        <div className="flex items-center justify-between mt-2">
                          <span className="text-xs opacity-70">
                            {new Date(alert.created_at).toLocaleString()}
                          </span>
                          <div className="flex items-center gap-1">
                            {!alert.is_read && (
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleMarkAsRead(alert.id)}
                                className="h-6 px-2 text-xs"
                              >
                                Mark Read
                              </Button>
                            )}
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleDismissAlert(alert.id)}
                              className="h-6 w-6 p-0"
                            >
                              <X className="h-3 w-3" />
                            </Button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>
        )}
      </CardContent>
    </Card>
  )
}
