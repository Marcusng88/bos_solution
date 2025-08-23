"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useApiClient, handleApiError } from "@/lib/api-client"
import { Target, CheckCircle, Clock, TrendingUp, Pause, Play, DollarSign } from "lucide-react"

interface OptimizationRecommendation {
  id: string
  campaign_name: string
  recommendation_type: string
  priority: 'low' | 'medium' | 'high' | 'critical'
  title: string
  description: string
  action_items: string[]
  potential_impact: string
  confidence_score: number
  is_applied: boolean
  created_at: string
}

export function RecommendationsWidget() {
  const [recommendations, setRecommendations] = useState<OptimizationRecommendation[]>([])
  const [loading, setLoading] = useState(true)
  const { apiClient, userId } = useApiClient()

  useEffect(() => {
    fetchRecommendations()
  }, [])

  const fetchRecommendations = async () => {
    try {
      const recsData = await apiClient.getOptimizationRecommendations(userId, false, 50)
      
      // Transform backend data to match frontend interface
      const transformedRecs = recsData.map((rec: any) => ({
        ...rec,
        action_items: rec.action_items ? JSON.parse(rec.action_items) : [],
        confidence_score: parseFloat(rec.confidence_score)
      }))
      
      setRecommendations(transformedRecs)
    } catch (error) {
      console.error('Failed to fetch recommendations:', handleApiError(error))
    } finally {
      setLoading(false)
    }
  }

  const handleApplyRecommendation = async (recommendationId: string) => {
    try {
      await apiClient.applyRecommendation(userId, recommendationId)
      setRecommendations(prev => prev.map(rec => 
        rec.id === recommendationId ? { ...rec, is_applied: true } : rec
      ))
    } catch (error) {
      console.error('Failed to apply recommendation:', handleApiError(error))
    }
  }

  const getPriorityColor = (priority: string, isApplied: boolean) => {
    if (isApplied) return 'text-gray-600 bg-gray-50 border-gray-200'
    
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

  const getRecommendationIcon = (type: string) => {
    switch (type) {
      case 'pause_low_performance':
        return <Pause className="h-4 w-4" />
      case 'scale_budget':
        return <TrendingUp className="h-4 w-4" />
      case 'optimize_creative':
        return <Target className="h-4 w-4" />
      case 'adjust_bidding':
        return <DollarSign className="h-4 w-4" />
      case 'reallocate_budget':
        return <Play className="h-4 w-4" />
      default:
        return <Target className="h-4 w-4" />
    }
  }

  const unappliedCount = recommendations.filter(rec => !rec.is_applied).length

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Recommendations</CardTitle>
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
            <Target className="h-5 w-5" />
            Recommendations
          </CardTitle>
          {unappliedCount > 0 && (
            <Badge variant="secondary" className="rounded-full">
              {unappliedCount} New
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent>
        {recommendations.length === 0 ? (
          <div className="text-center py-8">
            <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-3" />
            <p className="text-sm text-muted-foreground">No recommendations available</p>
            <p className="text-xs text-muted-foreground">Your campaigns are optimally configured!</p>
          </div>
        ) : (
          <ScrollArea className="h-80">
            <div className="space-y-3">
              {recommendations
                .sort((a, b) => {
                  // Sort by applied status (unapplied first), then by priority
                  if (a.is_applied !== b.is_applied) {
                    return a.is_applied ? 1 : -1
                  }
                  const priorityOrder = { critical: 4, high: 3, medium: 2, low: 1 }
                  return priorityOrder[b.priority] - priorityOrder[a.priority]
                })
                .map((recommendation) => (
                <div
                  key={recommendation.id}
                  className={`p-3 rounded-lg border transition-all duration-200 ${
                    recommendation.is_applied ? 'opacity-60' : ''
                  } ${getPriorityColor(recommendation.priority, recommendation.is_applied)}`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-start gap-2 flex-1">
                      {getRecommendationIcon(recommendation.recommendation_type)}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-medium text-sm truncate">{recommendation.title}</h4>
                          <Badge variant="outline" className="text-xs">
                            {recommendation.priority}
                          </Badge>
                          {recommendation.is_applied && (
                            <Badge variant="outline" className="text-xs bg-green-50 text-green-700 border-green-200">
                              Applied
                            </Badge>
                          )}
                        </div>
                        <p className="text-xs mb-2 leading-relaxed">{recommendation.description}</p>
                        
                        {/* Confidence Score */}
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-xs text-muted-foreground">Confidence:</span>
                          <div className="flex items-center gap-1">
                            <div className="w-16 h-1 bg-gray-200 rounded-full overflow-hidden">
                              <div 
                                className="h-full bg-current rounded-full transition-all duration-300"
                                style={{ width: `${recommendation.confidence_score * 100}%` }}
                              />
                            </div>
                            <span className="text-xs font-medium">
                              {Math.round(recommendation.confidence_score * 100)}%
                            </span>
                          </div>
                        </div>

                        {/* Action Items */}
                        <div className="text-xs p-2 rounded bg-white/50 border border-current/20 mb-2">
                          <span className="font-medium">Actions: </span>
                          <ul className="mt-1 space-y-1">
                            {recommendation.action_items.slice(0, 2).map((item, index) => (
                              <li key={index} className="flex items-start gap-1">
                                <span className="text-current/70">•</span>
                                <span>{item}</span>
                              </li>
                            ))}
                            {recommendation.action_items.length > 2 && (
                              <li className="text-current/70">
                                +{recommendation.action_items.length - 2} more actions
                              </li>
                            )}
                          </ul>
                        </div>

                        {/* Expected Impact */}
                        <div className="text-xs p-2 rounded bg-current/10 border border-current/20 mb-2">
                          <span className="font-medium">Expected Impact: </span>
                          {recommendation.potential_impact}
                        </div>

                        <div className="flex items-center justify-between mt-2">
                          <span className="text-xs opacity-70">
                            {new Date(recommendation.created_at).toLocaleString()}
                          </span>
                          {!recommendation.is_applied && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleApplyRecommendation(recommendation.id)}
                              className="h-6 px-2 text-xs"
                            >
                              Apply
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>
        )}

        {/* Recommendation Summary */}
        <div className="mt-4 pt-4 border-t">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-lg font-bold text-red-600">
                {recommendations.filter(r => !r.is_applied && (r.priority === 'critical' || r.priority === 'high')).length}
              </div>
              <div className="text-xs text-muted-foreground">High Priority</div>
            </div>
            <div>
              <div className="text-lg font-bold text-orange-600">
                {recommendations.filter(r => !r.is_applied && r.priority === 'medium').length}
              </div>
              <div className="text-xs text-muted-foreground">Medium Priority</div>
            </div>
            <div>
              <div className="text-lg font-bold text-green-600">
                {recommendations.filter(r => r.is_applied).length}
              </div>
              <div className="text-xs text-muted-foreground">Applied</div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
