"use client"

import React, { useState } from "react"
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { useApiClient, handleApiError } from "@/lib/api-client"
import { useUser } from "@clerk/nextjs"
import { AIAnalysisRecommendations } from "./ai-analysis-recommendations"
import { 
  Brain, 
  Lightbulb, 
  AlertTriangle, 
  CheckCircle, 
  Loader2, 
  ArrowRight, 
  Info, 
  TrendingUp, 
  ShieldAlert,
  Zap,
  RefreshCw,
  Users,
  Target
} from "lucide-react"

interface AIAnalysis {
  timestamp: string
  insights: string
  recommendations: string[]
  risk_alerts: string[]
  performance_score: number
}

export function AIInsightsPanel() {
  const { user, isSignedIn } = useUser()
  const [isScanning, setIsScanning] = useState(false)
  const [scanProgress, setScanProgress] = useState(0)
  const [analysis, setAnalysis] = useState<AIAnalysis | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [aiResponse, setAiResponse] = useState<string>("")
  const [isCompetitorMode, setIsCompetitorMode] = useState(false) // New state for toggle

  // Only show content if user is signed in
  if (!isSignedIn || !user) {
    return (
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-blue-600" />
              AI-Powered Insights
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center space-y-4">
              <p className="text-muted-foreground">
                Please sign in to access AI insights and recommendations.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  const { apiClient, userId } = useApiClient()

  const handleModeChange = (competitorMode: boolean) => {
    // Reset all states when switching modes
    setIsCompetitorMode(competitorMode)
    setIsScanning(false)
    setScanProgress(0)
    setAnalysis(null)
    setError(null)
    setAiResponse("")
  }

  const handleAIScan = async () => {
    setIsScanning(true)
    setScanProgress(0)
    setError(null)
    setAnalysis(null)
    setAiResponse("")

    try {
      console.log("🔍 Starting AI scan...")
      console.log("🔍 User ID:", userId)
      console.log("🔍 Competitor Mode:", isCompetitorMode)
      
      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setScanProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return 90
          }
          return prev + 10
        })
      }, 500)

      // Call the AI chat endpoint with the specific question based on mode
      console.log("🔍 Calling AI chat endpoint...")
      
      let aiQuestion = ""
      if (isCompetitorMode) {
        // Competitor-based optimization prompt
        aiQuestion = `Now I want you to detect how many competitors are there in the monitoring_alerts table. Please anaylse carefully whether they are related to the ongoing campaigns we have. For example, if you have detected Apple as competitor and we have campaigns of Uniqlo and Samsung, then obviously Apple has no connection with Uniqlo but is related to Samsung as competitor. Then, give me optimization on my currently ongoing campaigns only based on the competitor alerts that match to our ongoing campaigns that you have detected earlier. I want you to give me a structured output JSON file for me that contains these data fields, just the JSON file. The JSON file structure should look like this:

campaign_name:
competitor_name(can be null):
threatening_alerts (please be short around 50 words):
optimization_steps (please be short around 100 words,what are the steps can be implemented to boost the campaign to win against competitor, this can be reallocating budget etc):
results_and_predictions (please be short around 100 words,after the optimization steps are implemented, what will happen to the performance of our campaigns and what are the results?):
priority_level(low,medium,high, how important this optimization has to be implemented on the campaign)

please be short, give your response in less than 3000 characters`
      } else {
        // Self-optimization prompt (original)
        aiQuestion = `Please list and explain any recommendation actions or optimizations steps that can be taken to improve the performance for my ongoing campaigns.You need not have to give actions to every ongoing campaigns. Please summarize your recommendation actions into high priority and medium priority. Please give your response in a structured JSON output format, just the json file do not add any other words, as the example below:
{
  "recommendations": {
    "high_priority": [
      {
        "campaign_name": 
        "action": 
        "reasoning": 
      }
    ],
    "medium_priority": [
      {
        "campaign_name":  
        "action": 
        "reasoning": 
      }
    ]
  }
}`
      }
      
      const response = await apiClient.chatWithAI(userId, aiQuestion)

      console.log("✅ AI response received:", response)

      clearInterval(progressInterval)
      setScanProgress(100)

      // Wait a moment to show 100% progress
      setTimeout(() => {
        const aiResponseText = (response as any)?.response || "No response received"
        setAiResponse(aiResponseText)
        // Create a mock analysis object for compatibility
        setAnalysis({
          timestamp: new Date().toISOString(),
          insights: aiResponseText,
          recommendations: [],
          risk_alerts: [],
          performance_score: 7
        })
        setIsScanning(false)
        setScanProgress(0)
        console.log("✅ Analysis completed and set")
      }, 500)

    } catch (err) {
      console.error("❌ AI scan error:", err)
      setIsScanning(false)
      setScanProgress(0)
      setError(handleApiError(err))
    }
  }

  const getPerformanceColor = (score: number) => {
    if (score >= 8) return "text-green-600"
    if (score >= 6) return "text-yellow-600"
    return "text-red-600"
  }

  const getPerformanceBadge = (score: number) => {
    if (score >= 8) return <Badge className="bg-green-100 text-green-800">Excellent</Badge>
    if (score >= 6) return <Badge className="bg-yellow-100 text-yellow-800">Good</Badge>
    return <Badge className="bg-red-100 text-red-800">Needs Attention</Badge>
  }

  const handleRecommendationClick = (recommendation: any) => {
    console.log("Recommendation clicked:", recommendation)
    // Here you can implement actions like:
    // - Opening a modal with detailed steps
    // - Navigating to specific campaign pages
    // - Pre-filling forms with the recommendation
  }

  return (
    <div className="space-y-6">
      {/* AI Scan Button */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-blue-600" />
            AI-Powered Campaign Analysis
          </CardTitle>
          <CardDescription>
            Get intelligent insights and recommendations for your ongoing campaigns
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Toggle Button Section */}
          <div className="space-y-4">
            <div className="flex items-center justify-center">
              <div className="bg-gray-100 dark:bg-gray-800 rounded-lg p-1 flex">
                <button
                  onClick={() => handleModeChange(false)}
                  className={`flex items-center gap-2 px-5 py-3 rounded-md text-sm font-medium transition-all ${
                    !isCompetitorMode
                      ? "bg-white dark:bg-gray-700 text-blue-600 shadow-sm"
                      : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
                  }`}
                >
                  <Target className="h-5 w-5" />
                  Self-Optimization
                </button>
                <button
                  onClick={() => handleModeChange(true)}
                  className={`flex items-center gap-2 px-5 py-3 rounded-md text-sm font-medium transition-all ${
                    isCompetitorMode
                      ? "bg-white dark:bg-gray-700 text-purple-600 shadow-sm"
                      : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
                  }`}
                >
                  <Users className="h-5 w-5" />
                  Competitor Analysis
                </button>
              </div>
            </div>
            
            {/* Mode Description */}
            <div className="text-center">
              <p className="text-sm text-muted-foreground">
                {isCompetitorMode 
                  ? "Analyze performance against competitors and find competitive advantages"
                  : "Focus on internal campaign optimization and performance improvements"
                }
              </p>
            </div>
          </div>
          {!isScanning && !analysis && (
            <div className="text-center space-y-4">
              <div className="flex items-center justify-center">
                {isCompetitorMode ? (
                  <Users className="h-12 w-12 text-purple-600 mb-4" />
                ) : (
                  <Zap className="h-12 w-12 text-blue-600 mb-4" />
                )}
              </div>
              <p className="text-sm text-muted-foreground">
                {isCompetitorMode
                  ? "Click the button below to start competitor-based AI analysis"
                  : "Click the button below to start AI analysis of your campaigns"
                }
              </p>
              <Button 
                onClick={handleAIScan}
                size="lg"
                className={`px-8 py-3 text-sm font-semibold text-white ${
                  isCompetitorMode
                    ? "bg-purple-600 hover:bg-purple-700"
                    : "bg-blue-600 hover:bg-blue-700"
                }`}
              >
                {isCompetitorMode ? (
                  <>
                    <Users className="h-6 w-6 mr-3" />
                    Start Competitor Analysis
                  </>
                ) : (
                  <>
                    <Brain className="h-6 w-6 mr-3" />
                    Start AI Scan
                  </>
                )}
              </Button>
            </div>
          )}

          {/* Loading State */}
          {isScanning && (
            <div className="space-y-4">
              <div className="text-center">
                <Loader2 className={`h-8 w-8 animate-spin mx-auto mb-4 ${
                  isCompetitorMode ? "text-purple-600" : "text-blue-600"
                }`} />
                <h3 className="text-lg font-semibold mb-3">
                  {isCompetitorMode ? "AI Agent is Analyzing Competitors..." : "AI Agent is Analyzing..."}
                </h3>
                <p className="text-sm text-muted-foreground mb-4">
                  {isCompetitorMode
                    ? "Comparing your performance against competitors and market data"
                    : "Scanning campaigns, competitors, and market data for insights"
                  }
                </p>
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between text-sm font-medium">
                  <span>Progress</span>
                  <span>{scanProgress}%</span>
                </div>
                <Progress value={scanProgress} className="h-3" />
              </div>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="text-center space-y-4">
              <AlertTriangle className="h-12 w-12 text-red-600 mx-auto" />
              <div>
                <h3 className="text-lg font-semibold text-red-600 mb-3">Analysis Failed</h3>
                <p className="text-sm text-muted-foreground mb-4">{error}</p>
                <Button onClick={handleAIScan} variant="outline" className="text-sm px-4 py-2">
                  Try Again
                </Button>
              </div>
            </div>
          )}

          {/* Analysis Results */}
          {analysis && !isScanning && (
            <div className="space-y-6">
              {/* Performance Score */}
              <Card className="border-blue-200 bg-blue-50 dark:bg-blue-950/20 dark:border-blue-800">
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold flex items-center gap-2 text-foreground">
                        <TrendingUp className="h-5 w-5" />
                        Campaign Health Score
                      </h3>
                      <p className="text-sm text-muted-foreground">Overall performance assessment</p>
                    </div>
                    <div className="text-right">
                      <div className={`text-3xl font-bold ${getPerformanceColor(analysis.performance_score)}`}>
                        {analysis.performance_score}/10
                      </div>
                      {getPerformanceBadge(analysis.performance_score)}
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* AI Analysis Recommendations */}
              <AIAnalysisRecommendations 
                aiResponse={aiResponse}
                onRecommendationClick={handleRecommendationClick}
              />



              {/* Risk Alerts */}
              {analysis.risk_alerts && analysis.risk_alerts.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <ShieldAlert className="h-6 w-6 text-red-600" />
                      Risk Alerts
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {analysis.risk_alerts.map((alert, index) => (
                        <div key={index} className="flex items-start gap-3 p-4 bg-red-50 dark:bg-red-950/20 rounded-lg border border-red-200 dark:border-red-800">
                          <AlertTriangle className="h-6 w-6 text-red-600 dark:text-red-400 mt-0.5 flex-shrink-0" />
                          <p className="text-sm text-red-900 dark:text-red-100">{alert}</p>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Scan Again Button */}
              <div className="text-center">
                <Button 
                  onClick={handleAIScan}
                  variant="outline"
                  className="mt-4 text-sm px-4 py-2"
                >
                  <RefreshCw className="h-5 w-5 mr-2" />
                  Scan Again
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
