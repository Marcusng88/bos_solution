"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Separator } from "@/components/ui/separator"
import { 
  FileText, 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Target, 
  Lightbulb, 
  CheckCircle, 
  AlertCircle,
  Download,
  Loader2,
  Sparkles
} from "lucide-react"
import { useUser } from "@clerk/nextjs"
import { roiApi } from "@/lib/api-client"
import { useToast } from "@/hooks/use-toast"

interface ReportData {
  executive_summary: string
  performance_overview: string
  platform_analysis: string
  key_insights: string
  recommendations: string
  action_items: string
}

interface ReportResponse {
  success: boolean
  message?: string
  files?: {
    text: string
    html: string
    pdf: string
    json: string
  }
  report?: ReportData
  raw_data?: any
  generated_at: string
}

export function ReportGenerator() {
  const { user } = useUser()
  const { toast } = useToast()
  const [report, setReport] = useState<ReportResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const generateReport = async () => {
    if (!user) {
      toast({
        title: "Error",
        description: "Please log in to generate reports",
        variant: "destructive",
      })
      return
    }

    setLoading(true)
    setError(null)
    setReport(null)

    try {
      const response = await roiApi.generateReport(user.id)
      
      // Check if the response is successful
      if (response.success) {
        setReport(response)
        
        // Check if the new format response has files
        if (response.files) {
          toast({
            title: "Report Generated",
            description: "Your AI-powered ROI report is ready in multiple formats!",
          })
        } else {
          toast({
            title: "Report Generated",
            description: "Report generated successfully.",
            variant: "default",
          })
        }
      } else {
        throw new Error("Report generation failed")
      }
    } catch (err: any) {
      console.error("Report generation error:", err)
      
      // Extract error message from response if available
      let errorMessage = "Failed to generate report"
      if (err.message) {
        errorMessage = err.message
      } else if (err.detail) {
        errorMessage = err.detail
      } else if (typeof err === 'string') {
        errorMessage = err
      }
      
      setError(errorMessage)
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const downloadReport = (format: 'text' | 'html' | 'pdf' | 'json' = 'text') => {
    if (!report || !report.files) return

    const fileName = report.files[format]
    if (!fileName) {
      toast({
        title: "Error",
        description: `${format.toUpperCase()} format not available`,
        variant: "destructive",
      })
      return
    }

    // Create download link for the generated file
    const a = document.createElement('a')
    a.href = `/api/download-report?file=${encodeURIComponent(fileName)}`
    a.download = fileName
    a.target = '_blank'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)

    toast({
      title: "Report Downloaded",
      description: `Your ${format.toUpperCase()} report has been downloaded successfully.`,
    })
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const renderSection = (title: string, content: string, icon: React.ReactNode) => (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          {icon}
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="whitespace-pre-wrap text-sm leading-relaxed">
          {content}
        </div>
      </CardContent>
    </Card>
  )

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">AI Report Generator</h2>
          <p className="text-muted-foreground">
            Generate comprehensive ROI reports with AI-powered insights and recommendations
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button 
            onClick={generateReport} 
            disabled={loading}
            className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4 mr-2" />
                Generate Report
              </>
            )}
          </Button>
          {report && report.files && (
            <div className="flex items-center gap-2">
              <Button onClick={() => downloadReport('text')} variant="outline" size="sm">
                <FileText className="h-4 w-4 mr-2" />
                TXT
              </Button>
              <Button onClick={() => downloadReport('html')} variant="outline" size="sm">
                <Download className="h-4 w-4 mr-2" />
                HTML
              </Button>
              <Button onClick={() => downloadReport('pdf')} variant="outline" size="sm">
                <Download className="h-4 w-4 mr-2" />
                PDF
              </Button>
              <Button onClick={() => downloadReport('json')} variant="outline" size="sm">
                <Download className="h-4 w-4 mr-2" />
                JSON
              </Button>
            </div>
          )}
        </div>
      </div>

      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-red-700">
              <AlertCircle className="h-4 w-4" />
              <span className="font-medium">Error:</span>
              <span>{error}</span>
            </div>
          </CardContent>
        </Card>
      )}

      {report && (
        <div className="space-y-6">
          <Card className="bg-gradient-to-r from-green-50 to-blue-50 border-green-200">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <span className="font-medium text-green-800">
                    {report.message || "Report Generated Successfully"}
                  </span>
                </div>
                <Badge variant="secondary">
                  {formatDate(report.generated_at)}
                </Badge>
              </div>
            </CardContent>
          </Card>

          {report.files && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Download Options</CardTitle>
                <CardDescription>
                  Choose your preferred format to download the report
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <Button onClick={() => downloadReport('text')} variant="outline" className="flex flex-col items-center gap-2 h-auto py-4">
                    <FileText className="h-6 w-6" />
                    <span>Text Report</span>
                    <span className="text-xs text-muted-foreground">Simple format</span>
                  </Button>
                  <Button onClick={() => downloadReport('html')} variant="outline" className="flex flex-col items-center gap-2 h-auto py-4">
                    <Download className="h-6 w-6" />
                    <span>HTML Report</span>
                    <span className="text-xs text-muted-foreground">Professional design</span>
                  </Button>
                  <Button onClick={() => downloadReport('pdf')} variant="outline" className="flex flex-col items-center gap-2 h-auto py-4">
                    <Download className="h-6 w-6" />
                    <span>PDF Report</span>
                    <span className="text-xs text-muted-foreground">Print ready</span>
                  </Button>
                  <Button onClick={() => downloadReport('json')} variant="outline" className="flex flex-col items-center gap-2 h-auto py-4">
                    <Download className="h-6 w-6" />
                    <span>JSON Data</span>
                    <span className="text-xs text-muted-foreground">Raw data</span>
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {report.report && (
            <Tabs defaultValue="summary" className="space-y-4">
              <TabsList className="grid w-full grid-cols-6">
                <TabsTrigger value="summary">Summary</TabsTrigger>
                <TabsTrigger value="performance">Performance</TabsTrigger>
                <TabsTrigger value="platforms">Platforms</TabsTrigger>
                <TabsTrigger value="insights">Insights</TabsTrigger>
                <TabsTrigger value="recommendations">Recommendations</TabsTrigger>
                <TabsTrigger value="actions">Actions</TabsTrigger>
              </TabsList>

              <TabsContent value="summary" className="space-y-4">
                {renderSection(
                  "Executive Summary",
                  report.report.executive_summary,
                  <FileText className="h-4 w-4" />
                )}
              </TabsContent>

              <TabsContent value="performance" className="space-y-4">
                {renderSection(
                  "Performance Overview",
                  report.report.performance_overview,
                  <TrendingUp className="h-4 w-4" />
                )}
              </TabsContent>

              <TabsContent value="platforms" className="space-y-4">
                {renderSection(
                  "Platform Performance Analysis",
                  report.report.platform_analysis,
                  <Target className="h-4 w-4" />
                )}
              </TabsContent>

              <TabsContent value="insights" className="space-y-4">
                {renderSection(
                  "Key Insights",
                  report.report.key_insights,
                  <Lightbulb className="h-4 w-4" />
                )}
              </TabsContent>

              <TabsContent value="recommendations" className="space-y-4">
                {renderSection(
                  "Strategic Recommendations",
                  report.report.recommendations,
                  <TrendingUp className="h-4 w-4" />
                )}
              </TabsContent>

              <TabsContent value="actions" className="space-y-4">
                {renderSection(
                  "Action Items",
                  report.report.action_items,
                  <CheckCircle className="h-4 w-4" />
                )}
              </TabsContent>
            </Tabs>
          )}

          <Separator />

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Report Metadata</CardTitle>
              <CardDescription>
                Technical details about this report generation
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium">Generated:</span>
                  <span className="ml-2">{formatDate(report.generated_at)}</span>
                </div>
                <div>
                  <span className="font-medium">Data Period:</span>
                  <span className="ml-2">Previous & Current Month</span>
                </div>
                <div>
                  <span className="font-medium">AI Model:</span>
                  <span className="ml-2">Google Gemini Pro</span>
                </div>
                <div>
                  <span className="font-medium">Report Type:</span>
                  <span className="ml-2">Comprehensive ROI Analysis</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

             {!report && !loading && !error && (
         <Card className="border-dashed">
           <CardContent className="pt-6">
             <div className="text-center space-y-4">
               <div className="mx-auto w-16 h-16 bg-gradient-to-r from-purple-100 to-blue-100 rounded-full flex items-center justify-center">
                 <Sparkles className="h-8 w-8 text-purple-600" />
               </div>
               <div>
                 <h3 className="text-lg font-medium">Generate Your First AI Report</h3>
                 <p className="text-muted-foreground">
                   Click the button above to generate a comprehensive ROI report with AI-powered insights, 
                   recommendations, and actionable strategies based on your current and previous month's data.
                 </p>
               </div>
             </div>
           </CardContent>
         </Card>
       )}

       {report && report.raw_data && Object.keys(report.raw_data.current_month?.platforms || {}).length === 0 && (
         <Card className="border-yellow-200 bg-yellow-50">
           <CardContent className="pt-6">
             <div className="text-center space-y-4">
               <div className="mx-auto w-16 h-16 bg-gradient-to-r from-yellow-100 to-orange-100 rounded-full flex items-center justify-center">
                 <AlertCircle className="h-8 w-8 text-yellow-600" />
               </div>
               <div>
                 <h3 className="text-lg font-medium text-yellow-800">No ROI Data Available</h3>
                 <p className="text-yellow-700">
                   The report was generated successfully, but no ROI metrics data was found for the current and previous month. 
                   This could mean:
                 </p>
                 <ul className="text-yellow-700 text-sm mt-2 space-y-1">
                   <li>• No data has been added to the roi_metrics table yet</li>
                   <li>• Data exists but is outside the current/previous month range</li>
                   <li>• The database connection needs to be verified</li>
                 </ul>
               </div>
             </div>
           </CardContent>
         </Card>
       )}
    </div>
  )
}
