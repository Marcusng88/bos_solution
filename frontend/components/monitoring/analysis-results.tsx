"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ExternalLink, Rss, Globe, Youtube, Eye } from "lucide-react"
import { MonitoringDataDetailsModal } from "./monitoring-data-details-modal"

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
    case 'browser':
      return <div className="h-5 w-5 bg-gray-600 rounded flex items-center justify-center text-white text-xs font-bold">BR</div>
    case 'other':
    default:
      return <Rss className="h-5 w-5 text-gray-500" />
  }
}

export function AnalysisResults({ results }: AnalysisResultsProps) {
  const [selectedData, setSelectedData] = useState<AnalysisResult | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)

  const handleViewDetails = (data: AnalysisResult) => {
    setSelectedData(data)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setSelectedData(null)
  }

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
    <>
      <div className="space-y-4">
        {results.map((result) => (
          <Card key={result.id}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <div className="flex items-center gap-2">
                <PlatformIcon platform={result.platform} />
                <CardTitle className="text-sm font-medium capitalize">{result.platform} Analysis</CardTitle>
              </div>
              <div className="flex items-center gap-2">
                <div className="text-xs text-muted-foreground">
                  {new Date(result.detected_at).toLocaleString()}
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleViewDetails(result)}
                  className="h-8 px-2"
                >
                  <Eye className="h-3 w-3 mr-1" />
                  Details
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {/* Content Preview */}
                <div>
                  <p className="text-sm text-muted-foreground line-clamp-3">
                    {result.content_text && result.content_text.length > 200 
                      ? `${result.content_text.substring(0, 200)}...` 
                      : result.content_text}
                  </p>
                </div>
                
                {/* Post Type */}
                {result.post_type && (
                  <div>
                    <Badge variant="secondary" className="text-xs">
                      {result.post_type}
                    </Badge>
                  </div>
                )}
                
                {/* External Link */}
                {result.post_url && (
                  <a
                    href={result.post_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-blue-500 hover:underline flex items-center gap-1"
                  >
                    <ExternalLink className="h-3 w-3" />
                    View Source
                  </a>
                )}
                
                {/* Author Info */}
                {result.author_username && (
                  <div>
                    <p className="text-xs text-muted-foreground">
                      <strong>Author:</strong> {result.author_display_name || result.author_username}
                    </p>
                  </div>
                )}
                
                {/* Sentiment Score */}
                {result.sentiment_score !== undefined && (
                  <div>
                    <p className="text-xs text-muted-foreground">
                      <strong>Sentiment:</strong> 
                      <span className={`ml-1 ${
                        result.sentiment_score > 0.3 ? 'text-green-600' : 
                        result.sentiment_score < -0.3 ? 'text-red-600' : 'text-yellow-600'
                      }`}>
                        {result.sentiment_score.toFixed(2)}
                      </span>
                    </p>
                  </div>
                )}
                
                {/* Status Badges */}
                <div className="flex gap-2">
                  {result.is_new_post && (
                    <Badge variant="default" className="text-xs">New Post</Badge>
                  )}
                  {result.is_content_change && (
                    <Badge variant="outline" className="text-xs">Content Changed</Badge>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Details Modal */}
      <MonitoringDataDetailsModal
        data={selectedData}
        isOpen={isModalOpen}
        onClose={handleCloseModal}
      />
    </>
  )
}
