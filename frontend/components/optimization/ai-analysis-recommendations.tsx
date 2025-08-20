"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { AlertTriangle, CheckCircle, Clock, TrendingUp, Target, Zap, AlertCircle } from "lucide-react"

interface Recommendation {
  id: string
  title: string
  description: string
  priority: "high" | "medium" | "low"
  category: string
  impact: string
  effort: string
  estimatedTime: string
  campaign?: string
  actionType: "optimization" | "budget" | "creative" | "targeting" | "pausing" | "analysis"
}

interface AIAnalysisRecommendationsProps {
  aiResponse?: string
  onRecommendationClick?: (recommendation: Recommendation) => void
}

export function AIAnalysisRecommendations({ aiResponse, onRecommendationClick }: AIAnalysisRecommendationsProps) {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisComplete, setAnalysisComplete] = useState(false)

  // Function to analyze AI response and extract recommendations
  const analyzeAIResponse = (response: string): Recommendation[] => {
    const extractedRecommendations: Recommendation[] = []
    
    // Remove any asterisks from the response
    const cleanResponse = response.replace(/\*\*\*/g, '')
    
    // Split response into priority sections
    const highPriorityMatch = cleanResponse.match(/High Priority[^]*?(?=Medium Priority|$)/i)
    const mediumPriorityMatch = cleanResponse.match(/Medium Priority[^]*$/i)
    
    // Process High Priority section
    if (highPriorityMatch) {
      const highPrioritySection = highPriorityMatch[0]
      const highPriorityRecommendations = extractRecommendationsFromSection(highPrioritySection, "high")
      extractedRecommendations.push(...highPriorityRecommendations)
    }
    
    // Process Medium Priority section
    if (mediumPriorityMatch) {
      const mediumPrioritySection = mediumPriorityMatch[0]
      const mediumPriorityRecommendations = extractRecommendationsFromSection(mediumPrioritySection, "medium")
      extractedRecommendations.push(...mediumPriorityRecommendations)
    }
    
    // If no structured recommendations found, try to extract from general text
    if (extractedRecommendations.length === 0) {
      const generalRecommendations = extractGeneralRecommendations(cleanResponse)
      extractedRecommendations.push(...generalRecommendations)
    }
    
    return extractedRecommendations.slice(0, 8) // Limit to top 8 recommendations
  }
  
  const extractRecommendationsFromSection = (section: string, priority: "high" | "medium"): Recommendation[] => {
    const recommendations: Recommendation[] = []
    
    // Split by numbered items (1., 2., 3., etc.)
    const items = section.split(/\d+\.\s+/).filter(item => item.trim().length > 0)
    
    items.forEach((item, index) => {
      const lines = item.trim().split('\n').filter(line => line.trim().length > 0)
      
      if (lines.length > 0) {
        // First line should be campaign name
        const campaignName = lines[0].trim()
        
        // Remaining lines are recommendations
        const recommendationText = lines.slice(1).join('\n').trim()
        
        if (recommendationText && recommendationText.length > 10) {
          // Determine recommendation type and other properties
          const { actionType, impact, effort, estimatedTime } = categorizeRecommendation(recommendationText)
          
          // Create recommendation object
          const recommendation: Recommendation = {
            id: `${priority}-${index}-${Date.now()}`,
            title: generateRecommendationTitle(recommendationText),
            description: recommendationText,
            priority: priority,
            category: "Campaign Optimization",
            impact: impact,
            effort: effort,
            estimatedTime: estimatedTime,
            actionType: actionType,
            campaign: campaignName
          }
          
          recommendations.push(recommendation)
        }
      }
    })
    
    return recommendations
  }
  
  const categorizeRecommendation = (text: string) => {
    const lowerText = text.toLowerCase()
    
    // Determine action type
    let actionType: Recommendation["actionType"] = "optimization"
    if (lowerText.includes("pause") || lowerText.includes("stop")) {
      actionType = "pausing"
    } else if (lowerText.includes("budget") || lowerText.includes("spend")) {
      actionType = "budget"
    } else if (lowerText.includes("creative") || lowerText.includes("ad copy") || lowerText.includes("visual")) {
      actionType = "creative"
    } else if (lowerText.includes("target") || lowerText.includes("audience")) {
      actionType = "targeting"
    } else if (lowerText.includes("analyze") || lowerText.includes("review") || lowerText.includes("investigate")) {
      actionType = "analysis"
    }
    
    // Determine impact
    let impact = "Medium"
    if (lowerText.includes("significant") || lowerText.includes("major") || lowerText.includes("substantial")) {
      impact = "High"
    } else if (lowerText.includes("minor") || lowerText.includes("small")) {
      impact = "Low"
    }
    
    // Determine effort
    let effort = "Medium"
    if (lowerText.includes("quick") || lowerText.includes("simple") || lowerText.includes("easy")) {
      effort = "Low"
    } else if (lowerText.includes("complex") || lowerText.includes("extensive") || lowerText.includes("major")) {
      effort = "High"
    }
    
    // Estimate time
    let estimatedTime = "2-4 hours"
    if (effort === "Low") {
      estimatedTime = "30 min - 2 hours"
    } else if (effort === "High") {
      estimatedTime = "1-3 days"
    }
    
    return { actionType, impact, effort, estimatedTime }
  }
  
  const generateRecommendationTitle = (text: string): string => {
    const lowerText = text.toLowerCase()
    
    if (lowerText.includes("re-evaluate targeting")) {
      return "Optimize Audience Targeting"
    } else if (lowerText.includes("optimize ad creative")) {
      return "Improve Ad Creative & Copy"
    } else if (lowerText.includes("analyze landing page")) {
      return "Optimize Landing Page Experience"
    } else if (lowerText.includes("pause or reallocate")) {
      return "Consider Pausing Campaign"
    } else if (lowerText.includes("investigate low ctr")) {
      return "Address Low Click-Through Rate"
    } else if (lowerText.includes("increase ad spend")) {
      return "Increase Campaign Budget"
    } else if (lowerText.includes("analyze conversion funnel")) {
      return "Optimize Conversion Funnel"
    } else if (lowerText.includes("improve ad relevance")) {
      return "Enhance Ad Relevance"
    } else if (lowerText.includes("enhance conversion rate")) {
      return "Improve Conversion Rate"
    } else if (lowerText.includes("address low ctr")) {
      return "Fix Low Engagement"
    } else if (lowerText.includes("review budget allocation")) {
      return "Review Budget Strategy"
    } else if (lowerText.includes("increase budget")) {
      return "Increase Budget Allocation"
    } else if (lowerText.includes("optimize remaining budget")) {
      return "Optimize Budget Utilization"
    } else if (lowerText.includes("monitor cpc")) {
      return "Monitor Cost Per Click"
    } else if (lowerText.includes("analyze conversion drivers")) {
      return "Analyze Conversion Drivers"
    } else if (lowerText.includes("evaluate cpc for scale")) {
      return "Evaluate CPC for Scaling"
    }
    
    // Default title generation - extract first meaningful phrase
    const lines = text.split('\n')
    const firstLine = lines[0].trim()
    if (firstLine.startsWith('•') || firstLine.startsWith('-')) {
      const cleanLine = firstLine.replace(/^[•\-]\s*/, '').trim()
      return cleanLine.length > 60 ? cleanLine.substring(0, 60) + "..." : cleanLine
    }
    
    return firstLine.length > 60 ? firstLine.substring(0, 60) + "..." : firstLine
  }
  
  const extractGeneralRecommendations = (response: string): Recommendation[] => {
    const recommendations: Recommendation[] = []
    const lines = response.split('\n')
    
    let currentPriority = "medium"
    let currentCampaign = ""
    
    lines.forEach((line, index) => {
      const trimmedLine = line.trim()
      
      // Check for priority sections
      if (trimmedLine.toLowerCase().includes("high priority")) {
        currentPriority = "high"
        return
      } else if (trimmedLine.toLowerCase().includes("medium priority")) {
        currentPriority = "medium"
        return
      }
      
      // Check for numbered campaign items (1., 2., etc.)
      const campaignMatch = trimmedLine.match(/^\d+\.\s+(.+)/)
      if (campaignMatch) {
        currentCampaign = campaignMatch[1].trim()
        return
      }
      
      // Check for bullet points with recommendations
      if (trimmedLine.startsWith('•') || trimmedLine.startsWith('-')) {
        const cleanText = trimmedLine.replace(/^[•\-]\s*/, '').trim()
        if (cleanText.length > 20) {
          const { actionType, impact, effort, estimatedTime } = categorizeRecommendation(cleanText)
          
                     recommendations.push({
             id: `gen-${index}-${Date.now()}`,
             title: generateRecommendationTitle(cleanText),
             description: cleanText,
             priority: currentPriority as "high" | "medium" | "low",
             category: "Campaign Optimization",
             impact: impact,
             effort: effort,
             estimatedTime: estimatedTime,
             actionType: actionType,
             campaign: currentCampaign
           })
        }
      }
    })
    
    return recommendations.slice(0, 8)
  }
  
  // Effect to analyze AI response when it changes
  useEffect(() => {
    if (aiResponse && aiResponse.length > 100) {
      setIsAnalyzing(true)
      
      // Simulate analysis time
      setTimeout(() => {
        const extractedRecommendations = analyzeAIResponse(aiResponse)
        setRecommendations(extractedRecommendations)
        setIsAnalyzing(false)
        setAnalysisComplete(true)
      }, 2000)
    }
  }, [aiResponse])
  
  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case "high":
        return <AlertTriangle className="h-4 w-4 text-red-500" />
      case "medium":
        return <AlertCircle className="h-4 w-4 text-yellow-500" />
      case "low":
        return <Clock className="h-4 w-4 text-blue-500" />
      default:
        return <Target className="h-4 w-4 text-gray-500" />
    }
  }
  
  const getActionTypeIcon = (actionType: string) => {
    switch (actionType) {
      case "optimization":
        return <TrendingUp className="h-4 w-4" />
      case "budget":
        return <Zap className="h-4 w-4" />
      case "creative":
        return <Target className="h-4 w-4" />
      case "targeting":
        return <Target className="h-4 w-4" />
      case "pausing":
        return <AlertTriangle className="h-4 w-4" />
      case "analysis":
        return <CheckCircle className="h-4 w-4" />
      default:
        return <Target className="h-4 w-4" />
    }
  }
  
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high":
        return "border-red-500 bg-red-50 dark:bg-red-950/20 animate-pulse-fast"
      case "medium":
        return "border-yellow-500 bg-yellow-50 dark:bg-yellow-950/20"
      case "low":
        return "border-blue-500 bg-blue-50 dark:bg-blue-950/20"
      default:
        return "border-gray-200 bg-gray-50 dark:bg-gray-950/20"
    }
  }
  
  const getPriorityBadgeColor = (priority: string) => {
    switch (priority) {
      case "high":
        return "destructive"
      case "medium":
        return "secondary"
      case "low":
        return "outline"
      default:
        return "secondary"
    }
  }
  
  const priorityCounts = {
    high: recommendations.filter(r => r.priority === "high").length,
    medium: recommendations.filter(r => r.priority === "medium").length,
    low: recommendations.filter(r => r.priority === "low").length
  }
  
  const totalActions = recommendations.length
  
  return (
    <div className="space-y-6">
      <style jsx>{`
        @keyframes pulse-fast {
          0%, 100% {
            border-color: rgb(239 68 68);
          }
          50% {
            border-color: rgb(185 28 28);
          }
        }
        .animate-pulse-fast {
          animation: pulse-fast 0.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
      `}</style>
      
      {/* Analysis Status */}
      {isAnalyzing && (
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-center space-x-3">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
              <span className="text-lg font-medium">Analyzing AI Response...</span>
            </div>
            <p className="text-center text-muted-foreground mt-2">
              Extracting actionable recommendations from your AI conversation
            </p>
          </CardContent>
        </Card>
      )}
      
      {/* Recommendations Summary */}
      {analysisComplete && totalActions > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Total Actions */}
          <Card className="col-span-1">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Actions</p>
                  <p className="text-2xl font-bold">{totalActions}</p>
                </div>
                <Target className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>
          
          {/* High Priority */}
          <Card className="col-span-1">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">High Priority</p>
                  <p className="text-2xl font-bold text-red-600">{priorityCounts.high}</p>
                </div>
                <AlertTriangle className="h-8 w-8 text-red-600" />
              </div>
            </CardContent>
          </Card>
          
          {/* Medium Priority */}
          <Card className="col-span-1">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Medium Priority</p>
                  <p className="text-2xl font-bold text-yellow-600">{priorityCounts.medium}</p>
                </div>
                <AlertCircle className="h-8 w-8 text-yellow-600" />
              </div>
            </CardContent>
          </Card>
          
          {/* Low Priority */}
          <Card className="col-span-1">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Low Priority</p>
                  <p className="text-2xl font-bold text-blue-600">{priorityCounts.low}</p>
                </div>
                <Clock className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}
      
      {/* Detailed Recommendations */}
      {analysisComplete && recommendations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5 text-blue-600" />
              AI-Generated Recommendations
            </CardTitle>
            <CardDescription>
              Actionable insights extracted from your AI conversation, ranked by priority
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {recommendations.map((recommendation) => (
              <div
                key={recommendation.id}
                className={`p-4 rounded-lg border ${getPriorityColor(recommendation.priority)} hover:shadow-md transition-shadow cursor-pointer`}
                onClick={() => onRecommendationClick?.(recommendation)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 space-y-3">
                    {/* Header */}
                    <div className="flex items-center gap-3">
                      {getPriorityIcon(recommendation.priority)}
                      <h3 className="font-semibold text-lg">{recommendation.title}</h3>
                      <Badge variant={getPriorityBadgeColor(recommendation.priority)}>
                        {recommendation.priority.toUpperCase()} PRIORITY
                      </Badge>
                    </div>
                    
                    {/* Campaign Name - Bold */}
                    {recommendation.campaign && (
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-muted-foreground">Campaign:</span>
                        <span className="font-bold text-base text-gray-900 dark:text-gray-100">
                          {recommendation.campaign}
                        </span>
                      </div>
                    )}
                    
                    {/* Action Type */}
                    <div className="flex items-center gap-2">
                      {getActionTypeIcon(recommendation.actionType)}
                      <span className="text-sm text-muted-foreground capitalize">
                        {recommendation.actionType}
                      </span>
                    </div>
                    
                    {/* Description */}
                    <div className="text-sm leading-relaxed text-gray-700 dark:text-gray-300">
                      {recommendation.description}
                    </div>
                    
                    {/* Metrics */}
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">Impact:</span>
                        <Badge variant="outline" className="ml-2 text-xs">
                          {recommendation.impact}
                        </Badge>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Effort:</span>
                        <Badge variant="outline" className="ml-2 text-xs">
                          {recommendation.effort}
                        </Badge>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Time:</span>
                        <Badge variant="outline" className="ml-2 text-xs">
                          {recommendation.estimatedTime}
                        </Badge>
                      </div>
                    </div>
                  </div>
                  
                  {/* Action Button */}
                  <Button variant="outline" size="sm" className="ml-4">
                    Take Action
                  </Button>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
      
      {/* No Recommendations State */}
      {analysisComplete && recommendations.length === 0 && (
        <Card>
          <CardContent className="p-6 text-center">
            <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Immediate Actions Required</h3>
            <p className="text-muted-foreground">
              Your AI analysis didn't identify any urgent recommendations. Your campaigns appear to be performing well!
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
