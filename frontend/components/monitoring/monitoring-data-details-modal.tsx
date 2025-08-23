"use client"

import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { ExternalLink, Calendar, User, Globe, Hash, MessageSquare, TrendingUp, Clock, Eye } from "lucide-react"
import { formatDistanceToNow } from "date-fns"

interface MonitoringDataDetails {
  id: string
  competitor_id: string
  platform: string
  post_id?: string
  post_url?: string
  content_text: string
  author_username?: string
  author_display_name?: string
  author_avatar_url?: string
  post_type: string
  engagement_metrics?: any
  media_urls?: any
  content_hash?: string
  language?: string
  sentiment_score?: number
  detected_at: string
  posted_at?: string
  is_new_post?: boolean
  is_content_change?: boolean
  previous_content_hash?: string
}

interface MonitoringDataDetailsModalProps {
  data: MonitoringDataDetails | null
  isOpen: boolean
  onClose: () => void
}

const PlatformIcon = ({ platform }: { platform: string }) => {
  switch (platform.toLowerCase()) {
    case 'instagram':
      return <div className="h-8 w-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center text-white text-sm font-bold">IG</div>
    case 'facebook':
      return <div className="h-8 w-8 bg-blue-600 rounded-lg flex items-center justify-center text-white text-sm font-bold">FB</div>
    case 'twitter':
      return <div className="h-8 w-8 bg-blue-400 rounded-lg flex items-center justify-center text-white text-sm font-bold">TW</div>
    case 'linkedin':
      return <div className="h-8 w-8 bg-blue-700 rounded-lg flex items-center justify-center text-white text-sm font-bold">LI</div>
    case 'tiktok':
      return <div className="h-8 w-8 bg-black rounded-lg flex items-center justify-center text-white text-sm font-bold">TT</div>
    case 'youtube':
      return <div className="h-8 w-8 bg-red-600 rounded-lg flex items-center justify-center text-white text-sm font-bold">YT</div>
    case 'website':
    case 'web':
      return <div className="h-8 w-8 bg-blue-500 rounded-lg flex items-center justify-center text-white text-sm font-bold">WB</div>
    case 'browser':
      return <div className="h-8 w-8 bg-gray-600 rounded-lg flex items-center justify-center text-white text-sm font-bold">BR</div>
    case 'other':
    default:
      return <div className="h-8 w-8 bg-gray-500 rounded-lg flex items-center justify-center text-white text-sm font-bold">OT</div>
  }
}

const SentimentBadge = ({ score }: { score: number }) => {
  let variant: "default" | "secondary" | "destructive" | "outline" = "outline"
  let color = "text-gray-600 dark:text-gray-300"
  
  if (score > 0.3) {
    variant = "default"
    color = "text-green-600 dark:text-green-400"
  } else if (score < -0.3) {
    variant = "destructive"
    color = "text-red-600 dark:text-red-400"
  } else {
    variant = "secondary"
    color = "text-yellow-600 dark:text-yellow-400"
  }

  return (
    <Badge variant={variant} className="text-xs">
      <span className={color}>
        {score > 0 ? '+' : ''}{score.toFixed(2)}
      </span>
    </Badge>
  )
}

export function MonitoringDataDetailsModal({ data, isOpen, onClose }: MonitoringDataDetailsModalProps) {
  if (!data) return null

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString)
      return {
        formatted: date.toLocaleString(),
        relative: formatDistanceToNow(date, { addSuffix: true })
      }
    } catch {
      return { formatted: dateString, relative: 'Unknown' }
    }
  }

  const detectedDate = formatDate(data.detected_at)
  const postedDate = data.posted_at ? formatDate(data.posted_at) : null

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center gap-3">
            <PlatformIcon platform={data.platform} />
            <div>
              <DialogTitle className="text-xl">
                {data.platform.charAt(0).toUpperCase() + data.platform.slice(1)} Content Details
              </DialogTitle>
              <p className="text-sm text-muted-foreground">
                Detected {detectedDate.relative}
              </p>
            </div>
          </div>
        </DialogHeader>

        <div className="space-y-6">
          {/* Content Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5" />
                Content
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-muted/50 dark:bg-muted/30 p-4 rounded-lg border">
                <p className="text-sm whitespace-pre-wrap text-foreground">{data.content_text}</p>
              </div>
              
              {data.post_type && (
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-foreground">Type:</span>
                  <Badge variant="secondary">{data.post_type}</Badge>
                </div>
              )}

              {data.language && (
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-foreground">Language:</span>
                  <Badge variant="outline">{data.language}</Badge>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Author Information */}
          {(data.author_username || data.author_display_name) && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="h-5 w-5" />
                  Author Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center gap-3">
                  {data.author_avatar_url && (
                    <img 
                      src={data.author_avatar_url} 
                      alt="Author avatar" 
                      className="h-12 w-12 rounded-full object-cover"
                      onError={(e) => {
                        const target = e.target as HTMLImageElement
                        target.style.display = 'none'
                      }}
                    />
                  )}
                  <div>
                    <p className="font-medium text-foreground">{data.author_display_name || 'Unknown'}</p>
                    {data.author_username && (
                      <p className="text-sm text-muted-foreground">@{data.author_username}</p>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Timestamps */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5" />
                Timestamps
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex items-center gap-2">
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="text-sm font-medium text-foreground">Detected At</p>
                    <p className="text-sm text-muted-foreground">
                      {detectedDate.formatted}
                    </p>
                  </div>
                </div>
                
                {postedDate && (
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <p className="text-sm font-medium text-foreground">Posted At</p>
                      <p className="text-sm text-muted-foreground">
                        {postedDate.formatted}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Analytics & Metrics */}
          {(data.sentiment_score !== undefined || data.engagement_metrics || data.media_urls) && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  Analytics & Metrics
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {data.sentiment_score !== undefined && (
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-foreground">Sentiment Score:</span>
                    <SentimentBadge score={data.sentiment_score} />
                  </div>
                )}

                {data.engagement_metrics && (
                  <div>
                    <p className="text-sm font-medium mb-2 text-foreground">Engagement Metrics:</p>
                    <div className="bg-muted/50 dark:bg-muted/30 p-3 rounded-lg border">
                      <pre className="text-xs overflow-x-auto text-foreground">
                        {JSON.stringify(data.engagement_metrics, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}

                {data.media_urls && (
                  <div>
                    <p className="text-sm font-medium mb-2 text-foreground">Media URLs:</p>
                    <div className="bg-muted/50 dark:bg-muted/30 p-3 rounded-lg border">
                      <pre className="text-xs overflow-x-auto text-foreground">
                        {JSON.stringify(data.media_urls, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Technical Details */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Hash className="h-5 w-5" />
                Technical Details
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="font-medium text-foreground">Content Hash:</p>
                  <p className="text-muted-foreground font-mono text-xs break-all">
                    {data.content_hash || 'N/A'}
                  </p>
                </div>
                
                {data.previous_content_hash && (
                  <div>
                    <p className="font-medium text-foreground">Previous Hash:</p>
                    <p className="text-muted-foreground font-mono text-xs break-all">
                      {data.previous_content_hash}
                    </p>
                  </div>
                )}

                {data.post_id && (
                  <div>
                    <p className="font-medium text-foreground">Post ID:</p>
                    <p className="text-muted-foreground font-mono text-xs break-all">
                      {data.post_id}
                    </p>
                  </div>
                )}

                <div>
                  <p className="font-medium text-foreground">Competitor ID:</p>
                  <p className="text-muted-foreground font-mono text-xs break-all">
                    {data.competitor_id}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Status Indicators */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Eye className="h-5 w-5" />
                Status Indicators
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex gap-2">
                {data.is_new_post && (
                  <Badge variant="default" className="text-sm">
                    New Post
                  </Badge>
                )}
                {data.is_content_change && (
                  <Badge variant="outline" className="text-sm">
                    Content Changed
                  </Badge>
                )}
                {!data.is_new_post && !data.is_content_change && (
                  <Badge variant="secondary" className="text-sm">
                    Existing Content
                  </Badge>
                )}
              </div>
            </CardContent>
          </Card>

          {/* External Links */}
          {data.post_url && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Globe className="h-5 w-5" />
                  External Links
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Button 
                  variant="outline" 
                  asChild
                  className="w-full"
                >
                  <a
                    href={data.post_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2"
                  >
                    <ExternalLink className="h-4 w-4" />
                    View Original Post
                  </a>
                </Button>
              </CardContent>
            </Card>
          )}
        </div>

        <div className="flex justify-end pt-4">
          <Button onClick={onClose}>Close</Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
