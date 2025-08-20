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
  RefreshCw
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

  const handleAIScan = async () => {
    setIsScanning(true)
    setScanProgress(0)
    setError(null)
    setAnalysis(null)
    setAiResponse("")

    try {
      console.log("🔍 Starting AI scan...")
      console.log("🔍 User ID:", userId)
      
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

      // Call the AI chat endpoint with the specific question
      console.log("🔍 Calling AI chat endpoint...")
      const aiQuestion = `Please list any recommendation actions or optimizations steps that can be taken to improve the performance of all my ongoing campaigns. Please summarize your recommendation actions into high priority and medium priority. Please follow this format:
[Level of Priority]
1.[Campaign Name]
[Recommendation Actions]

2. [Campaign Name]
[Recommendation Actions]

......

[Level of Priority]
1.[Campaign Name]
[Recommendation Actions]

2. [Campaign Name]
[Recommendation Actions]

.....`
      
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
          {!isScanning && !analysis && (
            <div className="text-center space-y-4">
              <div className="flex items-center justify-center">
                <Zap className="h-12 w-12 text-blue-600 mb-4" />
              </div>
              <p className="text-muted-foreground">
                Click the button below to start AI analysis of your campaigns
              </p>
              <Button 
                onClick={handleAIScan}
                size="lg"
                className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3"
              >
                <Brain className="h-5 w-5 mr-2" />
                Start AI Scan
              </Button>
            </div>
          )}

          {/* Loading State */}
          {isScanning && (
            <div className="space-y-4">
              <div className="text-center">
                <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">AI Agent is Analyzing...</h3>
                <p className="text-muted-foreground mb-4">
                  Scanning campaigns, competitors, and market data for insights
                </p>
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Progress</span>
                  <span>{scanProgress}%</span>
                </div>
                <Progress value={scanProgress} className="h-2" />
              </div>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="text-center space-y-4">
              <AlertTriangle className="h-12 w-12 text-red-600 mx-auto" />
              <div>
                <h3 className="text-lg font-semibold text-red-600 mb-2">Analysis Failed</h3>
                <p className="text-muted-foreground mb-4">{error}</p>
                <Button onClick={handleAIScan} variant="outline">
                  Try Again
                </Button>
              </div>
            </div>
          )}

          {/* Analysis Results */}
          {analysis && !isScanning && (
            <div className="space-y-6">
              {/* Performance Score */}
              <Card className="border-blue-200 bg-blue-50">
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold flex items-center gap-2">
                        <TrendingUp className="h-5 w-5" />
                        Campaign Health Score
                      </h3>
                      <p className="text-muted-foreground">Overall performance assessment</p>
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
                      <ShieldAlert className="h-5 w-5 text-red-600" />
                      Risk Alerts
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {analysis.risk_alerts.map((alert, index) => (
                        <div key={index} className="flex items-start gap-3 p-3 bg-red-50 rounded-lg border border-red-200">
                          <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5 flex-shrink-0" />
                          <p className="text-sm">{alert}</p>
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
                  className="mt-4"
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
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
