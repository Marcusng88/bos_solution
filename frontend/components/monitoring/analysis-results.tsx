"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ExternalLink, Rss, Globe, Youtube } from "lucide-react"

interface AnalysisResult {
  id: string
  competitor_id: string
  platform: string
  content_text: string
  post_type: string
  detected_at: string
  source_url?: string
  key_insights?: string[]
  alert_type?: string
  engagement_metrics?: any
}

interface AnalysisResultsProps {
  results: AnalysisResult[]
}

const PlatformIcon = ({ platform }: { platform: string }) => {
  switch (platform) {
    case 'website':
      return <Globe className="h-5 w-5 text-blue-500" />
    case 'web':
      return <Rss className="h-5 w-5 text-green-500" />
    case 'youtube':
      return <Youtube className="h-5 w-5 text-red-500" />
    default:
      return <Globe className="h-5 w-5" />
  }
}

export function AnalysisResults({ results }: AnalysisResultsProps) {
  if (!results || results.length === 0) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-center text-muted-foreground">No analysis results found.</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      {results.map((result) => (
        <Card key={result.id}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <div className="flex items-center gap-2">
              <PlatformIcon platform={result.platform} />
              <CardTitle className="text-sm font-medium capitalize">{result.platform} Analysis</CardTitle>
            </div>
            <div className="text-xs text-muted-foreground">
              {new Date(result.detected_at).toLocaleString()}
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">{result.content_text}</p>
            {result.source_url && (
              <a
                href={result.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-blue-500 hover:underline flex items-center gap-1 mt-2"
              >
                <ExternalLink className="h-3 w-3" />
                View Source
              </a>
            )}
            {result.key_insights && result.key_insights.length > 0 && (
              <div className="mt-2">
                <h4 className="text-xs font-semibold">Key Insights:</h4>
                <ul className="list-disc list-inside text-xs text-muted-foreground">
                  {result.key_insights.map((insight, index) => (
                    <li key={index}>{insight}</li>
                  ))}
                </ul>
              </div>
            )}
            {result.alert_type && (
                <div className="mt-2">
                    <Badge variant="outline">{result.alert_type}</Badge>
                </div>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
