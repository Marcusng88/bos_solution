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
  post_url?: string
  author_username?: string
  author_display_name?: string
  author_avatar_url?: string
  engagement_metrics?: any
  media_urls?: any
  content_hash?: string
  language?: string
  sentiment_score?: number
  posted_at?: string
  is_new_post?: boolean
  is_content_change?: boolean
  previous_content_hash?: string
}

interface AnalysisResultsProps {
  results: AnalysisResult[]
}

const PlatformIcon = ({ platform }: { platform: string }) => {
  switch (platform.toLowerCase()) {
    case 'instagram':
      return <div className="h-5 w-5 bg-gradient-to-br from-purple-500 to-pink-500 rounded flex items-center justify-center text-white text-xs font-bold">IG</div>
    case 'facebook':
      return <div className="h-5 w-5 bg-blue-600 rounded flex items-center justify-center text-white text-xs font-bold">FB</div>
    case 'twitter':
      return <div className="h-5 w-5 bg-blue-400 rounded flex items-center justify-center text-white text-xs font-bold">TW</div>
    case 'linkedin':
      return <div className="h-5 w-5 bg-blue-700 rounded flex items-center justify-center text-white text-xs font-bold">LI</div>
    case 'tiktok':
      return <div className="h-5 w-5 bg-black rounded flex items-center justify-center text-white text-xs font-bold">TT</div>
    case 'youtube':
      return <div className="h-5 w-5 bg-red-600 rounded flex items-center justify-center text-white text-xs font-bold">YT</div>
    case 'website':
    case 'web':
      return <Globe className="h-5 w-5 text-blue-500" />
    case 'other':
    default:
      return <Rss className="h-5 w-5 text-gray-500" />
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
            {result.post_url && (
              <a
                href={result.post_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-blue-500 hover:underline flex items-center gap-1 mt-2"
              >
                <ExternalLink className="h-3 w-3" />
                View Post
              </a>
            )}
            {result.author_username && (
              <div className="mt-2">
                <p className="text-xs text-muted-foreground">
                  <strong>Author:</strong> {result.author_display_name || result.author_username}
                </p>
              </div>
            )}
            {result.sentiment_score !== undefined && (
              <div className="mt-2">
                <p className="text-xs text-muted-foreground">
                  <strong>Sentiment:</strong> {result.sentiment_score.toFixed(2)}
                </p>
              </div>
            )}
            {result.is_new_post && (
              <div className="mt-2">
                <Badge variant="default" className="text-xs">New Post</Badge>
              </div>
            )}
            {result.is_content_change && (
              <div className="mt-2">
                <Badge variant="outline" className="text-xs">Content Changed</Badge>
              </div>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
