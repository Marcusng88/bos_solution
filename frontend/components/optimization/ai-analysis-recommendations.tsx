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
  reasoning?: string // Add reasoning field for structured JSON data
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
    console.log("🔍 Analyzing AI response for JSON structure...")
    
    // Only parse JSON response - no fallback to text parsing
    const jsonRecommendations = parseJSONResponse(response)
    
    if (jsonRecommendations.length > 0) {
      console.log(`✅ Successfully parsed ${jsonRecommendations.length} recommendations from JSON`)
      return jsonRecommendations
    }
    
    console.log("⚠️ No valid JSON recommendations found")
    return []
  }

  // Function to parse JSON response from AI
  const parseJSONResponse = (response: string): Recommendation[] => {
    try {
      console.log("🔍 Attempting to parse JSON response...")
      
      // Look for JSON content in the response (between ```json and ``` or just { and })
      let jsonText = ""
      const jsonBlockMatch = response.match(/```json\s*([\s\S]*?)\s*```/)
      if (jsonBlockMatch) {
        jsonText = jsonBlockMatch[1]
        console.log("✅ Found JSON in code block")
      } else {
        // Try to find JSON object directly
        const jsonMatch = response.match(/(\{[\s\S]*\})/)
        if (jsonMatch) {
          jsonText = jsonMatch[1]
          console.log("✅ Found JSON object directly")
        }
      }

      if (!jsonText) {
        console.log("⚠️ No JSON found in response")
        return []
      }

      const parsed = JSON.parse(jsonText)
      console.log("✅ Successfully parsed JSON:", parsed)

      if (!parsed.recommendations) {
        console.log("⚠️ JSON missing 'recommendations' key")
        return []
      }

      const { recommendations } = parsed
      const extractedRecommendations: Recommendation[] = []

      // Process high priority recommendations
      if (recommendations.high_priority && Array.isArray(recommendations.high_priority)) {
        console.log(`📊 Processing ${recommendations.high_priority.length} high priority recommendations`)
        if (recommendations.high_priority.length === 0) {
          console.log("ℹ️ No high priority recommendations found")
        }
        recommendations.high_priority.forEach((rec: any, index: number) => {
          if (rec.campaign_name && rec.action && rec.reasoning) {
            const { actionType, impact, effort, estimatedTime } = categorizeRecommendation(rec.action)
            
            extractedRecommendations.push({
              id: `high-${index}-${Date.now()}`,
              title: rec.campaign_name, // Use campaign name as title
              description: rec.action, // Main action
              priority: "high",
              category: determineCategory(rec.action),
              impact: impact,
              effort: effort,
              estimatedTime: estimatedTime,
              actionType: actionType,
              campaign: rec.campaign_name,
              reasoning: rec.reasoning // Store reasoning separately
            })
          } else {
            console.log("⚠️ Skipping incomplete high priority recommendation:", rec)
          }
        })
      } else {
        console.log("ℹ️ No high_priority array found or it's not an array")
      }

      // Process medium priority recommendations
      if (recommendations.medium_priority && Array.isArray(recommendations.medium_priority)) {
        console.log(`📊 Processing ${recommendations.medium_priority.length} medium priority recommendations`)
        if (recommendations.medium_priority.length === 0) {
          console.log("ℹ️ No medium priority recommendations found")
        }
        recommendations.medium_priority.forEach((rec: any, index: number) => {
          if (rec.campaign_name && rec.action && rec.reasoning) {
            const { actionType, impact, effort, estimatedTime } = categorizeRecommendation(rec.action)
            
            extractedRecommendations.push({
              id: `medium-${index}-${Date.now()}`,
              title: rec.campaign_name, // Use campaign name as title
              description: rec.action, // Main action
              priority: "medium",
              category: determineCategory(rec.action),
              impact: impact,
              effort: effort,
              estimatedTime: estimatedTime,
              actionType: actionType,
              campaign: rec.campaign_name,
              reasoning: rec.reasoning // Store reasoning separately
            })
          } else {
            console.log("⚠️ Skipping incomplete medium priority recommendation:", rec)
          }
        })
      } else {
        console.log("ℹ️ No medium_priority array found or it's not an array")
      }

      console.log(`✅ Extracted ${extractedRecommendations.length} recommendations from JSON`)
      return extractedRecommendations

    } catch (error) {
      console.log("❌ JSON parsing failed:", error)
      return []
    }
  }

  // Helper function to determine category from action text
  const determineCategory = (action: string): string => {
    const lowerAction = action.toLowerCase()
    if (lowerAction.includes('creative') || lowerAction.includes('ad copy')) return "Creative"
    if (lowerAction.includes('budget') || lowerAction.includes('spend')) return "Budget"
    if (lowerAction.includes('target') || lowerAction.includes('audience')) return "Targeting"
    if (lowerAction.includes('optimization') || lowerAction.includes('optimize')) return "Optimization"
    return "Campaign Optimization"
  }
  
  // Function to check if text is actually a recommendation (not general chat text)
  const isValidRecommendation = (text: string): boolean => {
    const lowerText = text.toLowerCase()
    
    // Exclude general chat messages
    const excludePatterns = [
      'please let me know',
      'feel free to ask',
      'if you have any questions',
      'if you need',
      'let me know if',
      'is there anything else',
      'do you have any other',
      'would you like me to',
      'can i help you',
      'thank you for',
      'hope this helps',
      'let me know if you need',
      'if you would like',
      'please let me know if',
      'feel free to reach out',
      'if you need any clarification',
      'is there anything specific',
      'do you want me to',
      'would you like me to help',
      'if you have other questions'
    ]
    
    // Check if text contains any exclusion patterns
    for (const pattern of excludePatterns) {
      if (lowerText.includes(pattern)) {
        return false
      }
    }
    
    // Must contain action-oriented words to be considered a recommendation
    const actionWords = [
      'optimize', 'improve', 'increase', 'decrease', 'adjust', 'modify',
      'review', 'analyze', 'investigate', 'consider', 'focus on',
      'enhance', 'boost', 'reduce', 'change', 'update', 'refine',
      'target', 'audience', 'budget', 'spend', 'creative', 'copy',
      'landing page', 'conversion', 'ctr', 'cpc', 'roi', 'performance'
    ]
    
    const hasActionWord = actionWords.some(word => lowerText.includes(word))
    
    return hasActionWord && text.length > 20
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
        
        if (recommendationText && recommendationText.length > 10 && isValidRecommendation(recommendationText)) {
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
        if (cleanText.length > 20 && isValidRecommendation(cleanText)) {
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
    if (aiResponse && aiResponse.length > 50) {
      console.log("🔍 AI response received, starting analysis...")
      setIsAnalyzing(true)
      
      // Shorter delay for better user experience
      setTimeout(() => {
        const extractedRecommendations = analyzeAIResponse(aiResponse)
        setRecommendations(extractedRecommendations)
        setIsAnalyzing(false)
        setAnalysisComplete(true)
        
        if (extractedRecommendations.length === 0) {
          console.log("⚠️ No recommendations extracted - check AI response format")
          console.log("Raw AI Response:", aiResponse.substring(0, 500) + "...")
        }
      }, 1000) // Reduced from 2000ms to 1000ms
    } else if (aiResponse) {
      console.log("⚠️ AI response too short or empty:", aiResponse.length)
      setIsAnalyzing(false)
      setAnalysisComplete(true)
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
                    {/* Header with Campaign Name as Main Title */}
                    <div className="flex items-center gap-3">
                      {getPriorityIcon(recommendation.priority)}
                      <h3 className="font-semibold text-lg">{recommendation.title}</h3>
                      <Badge variant={getPriorityBadgeColor(recommendation.priority)}>
                        {recommendation.priority.toUpperCase()} PRIORITY
                      </Badge>
                    </div>
                    
                    {/* Action Type */}
                    <div className="flex items-center gap-2">
                      {getActionTypeIcon(recommendation.actionType)}
                      <span className="text-sm text-muted-foreground capitalize">
                        {recommendation.category}
                      </span>
                    </div>
                    
                    {/* Action Description */}
                    <div className="space-y-2">
                      <div className="text-sm font-medium text-gray-800 dark:text-gray-200">
                        Action:
                      </div>
                      <div className="text-sm leading-relaxed text-gray-700 dark:text-gray-300 pl-4 border-l-2 border-blue-200">
                        {recommendation.description}
                      </div>
                    </div>
                    
                    {/* Reasoning (if available from JSON) */}
                    {recommendation.reasoning && (
                      <div className="space-y-2">
                        <div className="text-sm font-medium text-gray-800 dark:text-gray-200">
                          Reasoning:
                        </div>
                        <div className="text-sm leading-relaxed text-gray-600 dark:text-gray-400 pl-4 border-l-2 border-green-200">
                          {recommendation.reasoning}
                        </div>
                      </div>
                    )}
                    
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
      
      {/* No Recommendations State - Improved */}
      {analysisComplete && recommendations.length === 0 && (
        <Card>
          <CardContent className="p-6 text-center">
            <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Immediate Actions Required</h3>
            <p className="text-muted-foreground mb-4">
              Your AI analysis completed successfully but didn't identify any urgent optimization actions for your ongoing campaigns.
            </p>
            <div className="bg-green-50 dark:bg-green-950/20 p-4 rounded-lg border border-green-200 dark:border-green-800">
              <p className="text-sm text-green-800 dark:text-green-200">
                This could mean:
              </p>
              <ul className="text-sm text-green-700 dark:text-green-300 mt-2 space-y-1 text-left inline-block">
                <li>• Your campaigns are performing well within targets</li>
                <li>• No ongoing campaigns need immediate attention</li>
                <li>• All campaigns are properly optimized</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      )}
      
      {/* Analysis Error State */}
      {analysisComplete && !aiResponse && (
        <Card>
          <CardContent className="p-6 text-center">
            <AlertTriangle className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Analysis Incomplete</h3>
            <p className="text-muted-foreground mb-4">
              The AI analysis couldn't be completed properly. This might be due to:
            </p>
            <div className="bg-yellow-50 dark:bg-yellow-950/20 p-4 rounded-lg border border-yellow-200 dark:border-yellow-800">
              <ul className="text-sm text-yellow-700 dark:text-yellow-300 space-y-1 text-left inline-block">
                <li>• No campaign data available</li>
                <li>• AI service temporarily unavailable</li>
                <li>• Response format not recognized</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
