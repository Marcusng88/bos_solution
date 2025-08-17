"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useApiClient, handleApiError } from "@/lib/api-client"
import { Activity, TrendingUp, AlertTriangle, Shield, Eye } from "lucide-react"

interface RiskPattern {
  id: string
  campaign_name: string
  pattern_type: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  detected_at: string
  pattern_data: any
  resolved: boolean
}

export function RiskPatternsWidget() {
  const [riskPatterns, setRiskPatterns] = useState<RiskPattern[]>([])
  const [loading, setLoading] = useState(true)
  const { apiClient, userId } = useApiClient()

  useEffect(() => {
    fetchRiskPatterns()
  }, [])

  const fetchRiskPatterns = async () => {
    try {
      const patternsData = await apiClient.getRiskPatterns(userId, false, 50)
      
      // Transform backend data to match frontend interface
      const transformedPatterns = patternsData.map((pattern: any) => ({
        ...pattern,
        pattern_data: pattern.pattern_data ? JSON.parse(pattern.pattern_data) : {}
      }))
      
      setRiskPatterns(transformedPatterns)
    } catch (error) {
      console.error('Failed to fetch risk patterns:', handleApiError(error))
    } finally {
      setLoading(false)
    }
  }

  const handleResolvePattern = async (patternId: string) => {
    try {
      // For now, just update UI - you might want to add a resolve API endpoint
      setRiskPatterns(prev => prev.map(pattern => 
        pattern.id === patternId ? { ...pattern, resolved: true } : pattern
      ))
    } catch (error) {
      console.error('Failed to resolve risk pattern:', handleApiError(error))
    }
  }

  const getSeverityColor = (severity: string, resolved: boolean) => {
    if (resolved) return 'text-gray-600 bg-gray-50 border-gray-200'
    
    switch (severity) {
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

  const getPatternIcon = (patternType: string) => {
    switch (patternType) {
      case 'overspend':
        return <AlertTriangle className="h-4 w-4" />
      case 'spending_spike':
        return <TrendingUp className="h-4 w-4" />
      case 'performance_decline':
        return <Activity className="h-4 w-4" />
      default:
        return <Eye className="h-4 w-4" />
    }
  }

  const getPatternDescription = (pattern: RiskPattern) => {
    switch (pattern.pattern_type) {
      case 'overspend':
        return `Budget exceeded by $${pattern.pattern_data.overspend_amount} (${pattern.pattern_data.overspend_percentage}%)`
      case 'spending_spike':
        return `Spending increased by ${pattern.pattern_data.increase_percentage}% from $${pattern.pattern_data.previous_spend} to $${pattern.pattern_data.current_spend}`
      case 'performance_decline':
        return `CTR declined ${pattern.pattern_data.ctr_decline_percentage}% from ${pattern.pattern_data.previous_ctr}% to ${pattern.pattern_data.current_ctr}%`
      case 'low_efficiency':
        return `CPC increased ${pattern.pattern_data.cpc_increase}%, efficiency score: ${pattern.pattern_data.efficiency_score}`
      default:
        return 'Risk pattern detected'
    }
  }

  const unresolvedCount = riskPatterns.filter(pattern => !pattern.resolved).length

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Risk Patterns</CardTitle>
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
            <Activity className="h-5 w-5" />
            Risk Patterns
          </CardTitle>
          {unresolvedCount > 0 && (
            <Badge variant="destructive" className="rounded-full">
              {unresolvedCount}
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent>
        {riskPatterns.length === 0 ? (
          <div className="text-center py-8">
            <Shield className="h-12 w-12 text-green-500 mx-auto mb-3" />
            <p className="text-sm text-muted-foreground">No risk patterns detected</p>
            <p className="text-xs text-muted-foreground">Your campaigns are performing optimally!</p>
          </div>
        ) : (
          <ScrollArea className="h-80">
            <div className="space-y-3">
              {riskPatterns
                .sort((a, b) => {
                  // Sort by resolved status (unresolved first), then by severity
                  if (a.resolved !== b.resolved) {
                    return a.resolved ? 1 : -1
                  }
                  const severityOrder = { critical: 4, high: 3, medium: 2, low: 1 }
                  return severityOrder[b.severity] - severityOrder[a.severity]
                })
                .map((pattern) => (
                <div
                  key={pattern.id}
                  className={`p-3 rounded-lg border transition-all duration-200 ${
                    pattern.resolved ? 'opacity-60' : ''
                  } ${getSeverityColor(pattern.severity, pattern.resolved)}`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-start gap-2 flex-1">
                      {getPatternIcon(pattern.pattern_type)}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-medium text-sm truncate">{pattern.campaign_name}</h4>
                          <Badge variant="outline" className="text-xs">
                            {pattern.severity}
                          </Badge>
                          {pattern.resolved && (
                            <Badge variant="outline" className="text-xs bg-green-50 text-green-700 border-green-200">
                              Resolved
                            </Badge>
                          )}
                        </div>
                        <p className="text-xs mb-2 font-medium capitalize">
                          {pattern.pattern_type.replace('_', ' ')} Pattern
                        </p>
                        <p className="text-xs mb-2 leading-relaxed">
                          {getPatternDescription(pattern)}
                        </p>
                        <div className="flex items-center justify-between mt-2">
                          <span className="text-xs opacity-70">
                            {new Date(pattern.detected_at).toLocaleString()}
                          </span>
                          {!pattern.resolved && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleResolvePattern(pattern.id)}
                              className="h-6 px-2 text-xs"
                            >
                              Mark Resolved
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

        {/* Risk Summary */}
        <div className="mt-4 pt-4 border-t">
          <div className="grid grid-cols-2 gap-4 text-center">
            <div>
              <div className="text-lg font-bold text-red-600">
                {riskPatterns.filter(p => !p.resolved && (p.severity === 'critical' || p.severity === 'high')).length}
              </div>
              <div className="text-xs text-muted-foreground">High Risk</div>
            </div>
            <div>
              <div className="text-lg font-bold text-orange-600">
                {riskPatterns.filter(p => !p.resolved && p.severity === 'medium').length}
              </div>
              <div className="text-xs text-muted-foreground">Medium Risk</div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
