"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Clock, MessageCircle, ThumbsUp, Video, User } from "lucide-react"
import { useYouTubeStore } from '@/hooks/use-youtube'

interface RecentActivity {
  type: string
  video_id: string
  title: string
  description?: string
  thumbnail: string
  published_at: string
  video_url: string
  statistics?: {
    view_count: string
    like_count: string
    comment_count: string
  }
  recent_comments: Array<{
    comment_id: string
    text: string
    author: string
    published_at: string
    like_count: number
  }>
}

export function YouTubeRecentActivity() {
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [hoursBack, setHoursBack] = useState(1)
  
  const { isConnected, getRecentActivity, connect } = useYouTubeStore()

  const fetchRecentActivity = async () => {
    if (!isConnected) {
      setError('Not connected to YouTube')
      return
    }

    setLoading(true)
    setError(null)
    
    try {
      const result = await getRecentActivity(hoursBack)
      
      if (result.success) {
        setRecentActivity(result.recent_activity || [])
      } else {
        setError(result.error || 'Failed to fetch recent activity')
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60))
    
    if (diffInMinutes < 1) return 'Just now'
    if (diffInMinutes < 60) return `${diffInMinutes} minutes ago`
    
    const diffInHours = Math.floor(diffInMinutes / 60)
    if (diffInHours < 24) return `${diffInHours} hours ago`
    
    const diffInDays = Math.floor(diffInHours / 24)
    return `${diffInDays} days ago`
  }

  const getActivityTypeIcon = (type: string) => {
    switch (type) {
      case 'video':
        return <Video className="h-4 w-4" />
      case 'comments_on_existing_video':
        return <MessageCircle className="h-4 w-4" />
      default:
        return <Video className="h-4 w-4" />
    }
  }

  const getActivityTypeBadge = (type: string) => {
    switch (type) {
      case 'video':
        return <Badge variant="default">New Video</Badge>
      case 'comments_on_existing_video':
        return <Badge variant="secondary">New Comments</Badge>
      default:
        return <Badge variant="outline">{type}</Badge>
    }
  }

  if (!isConnected) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Video className="h-5 w-5 text-red-500" />
            YouTube Recent Activity
          </CardTitle>
          <CardDescription>
            View recent activity from your YouTube channel including new videos and comments
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-6">
            <p className="text-muted-foreground mb-4">
              Connect your YouTube account to view recent activity
            </p>
            <Button onClick={connect} className="flex items-center gap-2">
              <Video className="h-4 w-4" />
              Connect YouTube
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Video className="h-5 w-5 text-red-500" />
          YouTube Recent Activity
        </CardTitle>
        <CardDescription>
          Activity from the last {hoursBack} hour{hoursBack > 1 ? 's' : ''}
        </CardDescription>
        <div className="flex items-center gap-2">
          <select 
            value={hoursBack} 
            onChange={(e) => setHoursBack(Number(e.target.value))}
            className="px-3 py-1 border rounded-md text-sm"
          >
            <option value={1}>Last 1 hour</option>
            <option value={3}>Last 3 hours</option>
            <option value={6}>Last 6 hours</option>
            <option value={12}>Last 12 hours</option>
            <option value={24}>Last 24 hours</option>
          </select>
          <Button 
            onClick={fetchRecentActivity} 
            disabled={loading}
            className="flex items-center gap-2"
          >
            <Clock className="h-4 w-4" />
            {loading ? 'Loading...' : 'Refresh'}
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-3 mb-4">
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        )}

        {loading && (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        )}

        {!loading && recentActivity.length === 0 && !error && (
          <div className="text-center py-8 text-muted-foreground">
            <MessageCircle className="h-12 w-12 mx-auto mb-2 opacity-50" />
            <p>No recent activity found in the last {hoursBack} hour{hoursBack > 1 ? 's' : ''}</p>
            <p className="text-sm mt-1">Try expanding the time range or check back later</p>
          </div>
        )}

        {!loading && recentActivity.length > 0 && (
          <div className="space-y-4">
            {recentActivity.map((activity, index) => (
              <div key={`${activity.video_id}-${index}`} className="border rounded-lg p-4">
                <div className="flex items-start gap-3 mb-3">
                  <img 
                    src={activity.thumbnail} 
                    alt={activity.title}
                    className="w-16 h-12 rounded object-cover"
                  />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      {getActivityTypeIcon(activity.type)}
                      {getActivityTypeBadge(activity.type)}
                    </div>
                    <h4 className="font-medium text-sm leading-tight mb-1 line-clamp-2">
                      {activity.title}
                    </h4>
                    <p className="text-xs text-muted-foreground">
                      {activity.published_at && formatTimeAgo(activity.published_at)}
                    </p>
                  </div>
                </div>

                {activity.statistics && (
                  <div className="flex items-center gap-4 text-xs text-muted-foreground mb-3">
                    <span className="flex items-center gap-1">
                      <Video className="h-3 w-3" />
                      {parseInt(activity.statistics.view_count).toLocaleString()} views
                    </span>
                    <span className="flex items-center gap-1">
                      <ThumbsUp className="h-3 w-3" />
                      {parseInt(activity.statistics.like_count).toLocaleString()} likes
                    </span>
                    <span className="flex items-center gap-1">
                      <MessageCircle className="h-3 w-3" />
                      {parseInt(activity.statistics.comment_count).toLocaleString()} comments
                    </span>
                  </div>
                )}

                {activity.recent_comments.length > 0 && (
                  <>
                    <Separator className="my-3" />
                    <div>
                      <h5 className="text-sm font-medium mb-2 flex items-center gap-2">
                        <MessageCircle className="h-4 w-4" />
                        Recent Comments ({activity.recent_comments.length})
                      </h5>
                      <div className="space-y-2">
                        {activity.recent_comments.slice(0, 3).map((comment) => (
                          <div key={comment.comment_id} className="bg-gray-50 rounded-md p-2">
                            <div className="flex items-center gap-2 mb-1">
                              <User className="h-3 w-3" />
                              <span className="text-xs font-medium">{comment.author}</span>
                              <span className="text-xs text-muted-foreground">
                                {formatTimeAgo(comment.published_at)}
                              </span>
                              {comment.like_count > 0 && (
                                <span className="text-xs text-muted-foreground flex items-center gap-1">
                                  <ThumbsUp className="h-3 w-3" />
                                  {comment.like_count}
                                </span>
                              )}
                            </div>
                            <p className="text-xs line-clamp-2">{comment.text}</p>
                          </div>
                        ))}
                        {activity.recent_comments.length > 3 && (
                          <p className="text-xs text-muted-foreground">
                            +{activity.recent_comments.length - 3} more comments
                          </p>
                        )}
                      </div>
                    </div>
                  </>
                )}

                <div className="mt-3 pt-2 border-t">
                  <a 
                    href={activity.video_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-xs text-blue-600 hover:text-blue-800 hover:underline"
                  >
                    View on YouTube →
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
