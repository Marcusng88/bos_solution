"""
YouTube Data Service - Handles database operations for videos, channels, and ROI analytics
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.core.supabase_client import supabase_client
from app.schemas.youtube import (
    VideoCreate, VideoUpdate, VideoResponse, VideoListResponse, VideoStats,
    ChannelCreate, ChannelUpdate, ChannelResponse, ChannelListResponse, ChannelStats,
    ROIAnalyticsCreate, ROIAnalyticsUpdate, ROIAnalyticsResponse, ROIAnalyticsListResponse,
    VideoInfoResponse, ChannelInfoResponse, ROIAnalyticsInfoResponse, ROIAnalyticsSummary
)

logger = logging.getLogger(__name__)

class YouTubeDataService:
    """Service for YouTube data operations"""
    
    def __init__(self):
        self.supabase = supabase_client

    # Video Operations
    async def create_video(self, video_data: VideoCreate) -> Optional[VideoResponse]:
        """Create a new video record"""
        try:
            data = video_data.dict()
            response = await self.supabase._make_request("POST", "videos", data=data)
            
            if response.status_code == 201:
                result = response.json()
                return VideoResponse(**result[0]) if result else None
            else:
                logger.error(f"Failed to create video: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error creating video: {e}")
            return None

    async def get_video(self, video_id: str) -> Optional[VideoResponse]:
        """Get video by YouTube video ID"""
        try:
            response = await self.supabase._make_request(
                "GET", 
                "videos", 
                params={"video_id": f"eq.{video_id}"}
            )
            
            if response.status_code == 200:
                result = response.json()
                return VideoResponse(**result[0]) if result else None
            return None
        except Exception as e:
            logger.error(f"Error getting video: {e}")
            return None

    async def get_user_videos(
        self, 
        user_id: str, 
        page: int = 1, 
        per_page: int = 10
    ) -> Optional[VideoListResponse]:
        """Get videos for a user with pagination"""
        try:
            offset = (page - 1) * per_page
            response = await self.supabase._make_request(
                "GET", 
                "videos", 
                params={
                    "user_id": f"eq.{user_id}",
                    "order": "published_at.desc",
                    "limit": per_page,
                    "offset": offset
                }
            )
            
            if response.status_code == 200:
                videos = [VideoResponse(**video) for video in response.json()]
                
                # Get total count
                count_response = await self.supabase._make_request(
                    "GET", 
                    "videos", 
                    params={
                        "user_id": f"eq.{user_id}",
                        "select": "count"
                    }
                )
                total = count_response.json()[0]["count"] if count_response.status_code == 200 else len(videos)
                
                return VideoListResponse(
                    videos=videos,
                    total=total,
                    page=page,
                    per_page=per_page
                )
            return None
        except Exception as e:
            logger.error(f"Error getting user videos: {e}")
            return None

    async def get_video_info(self, video_id: str) -> Optional[VideoInfoResponse]:
        """Get comprehensive video information including stats and channel info"""
        try:
            # Get video data
            video = await self.get_video(video_id)
            if not video:
                return None
            
            # Get channel info
            channel = await self.get_channel(video.channel_id)
            if not channel:
                return None
            
            # Create video stats
            video_stats = VideoStats(
                views=video.views or 0,
                likes=video.likes or 0,
                comments=video.comments or 0,
                engagement_rate=video.engagement_rate or 0.0,
                watch_time_hours=video.watch_time_hours or 0.0,
                roi_score=video.roi_score
            )
            
            # Create performance trend (placeholder for now)
            performance_trend = []
            
            return VideoInfoResponse(
                video=video,
                stats=video_stats,
                channel_info=channel,
                performance_trend=performance_trend
            )
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return None

    async def update_video(self, video_id: str, video_data: VideoUpdate) -> Optional[VideoResponse]:
        """Update video data"""
        try:
            data = {k: v for k, v in video_data.dict().items() if v is not None}
            response = await self.supabase._make_request(
                "PATCH", 
                f"videos?video_id=eq.{video_id}", 
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                return VideoResponse(**result[0]) if result else None
            return None
        except Exception as e:
            logger.error(f"Error updating video: {e}")
            return None

    async def delete_video(self, video_id: str) -> bool:
        """Delete video record"""
        try:
            response = await self.supabase._make_request(
                "DELETE", 
                f"videos?video_id=eq.{video_id}"
            )
            return response.status_code == 204
        except Exception as e:
            logger.error(f"Error deleting video: {e}")
            return False

    # Channel Operations
    async def create_channel(self, channel_data: ChannelCreate) -> Optional[ChannelResponse]:
        """Create a new channel record"""
        try:
            data = channel_data.dict()
            response = await self.supabase._make_request("POST", "channels", data=data)
            
            if response.status_code == 201:
                result = response.json()
                return ChannelResponse(**result[0]) if result else None
            else:
                logger.error(f"Failed to create channel: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error creating channel: {e}")
            return None

    async def get_channel(self, channel_id: str) -> Optional[ChannelResponse]:
        """Get channel by YouTube channel ID"""
        try:
            response = await self.supabase._make_request(
                "GET", 
                "channels", 
                params={"channel_id": f"eq.{channel_id}"}
            )
            
            if response.status_code == 200:
                result = response.json()
                return ChannelResponse(**result[0]) if result else None
            return None
        except Exception as e:
            logger.error(f"Error getting channel: {e}")
            return None

    async def get_user_channels(
        self, 
        user_id: str, 
        page: int = 1, 
        per_page: int = 10
    ) -> Optional[ChannelListResponse]:
        """Get channels for a user with pagination"""
        try:
            offset = (page - 1) * per_page
            response = await self.supabase._make_request(
                "GET", 
                "channels", 
                params={
                    "user_id": f"eq.{user_id}",
                    "order": "created_at.desc",
                    "limit": per_page,
                    "offset": offset
                }
            )
            
            if response.status_code == 200:
                channels = [ChannelResponse(**channel) for channel in response.json()]
                
                # Get total count
                count_response = await self.supabase._make_request(
                    "GET", 
                    "channels", 
                    params={
                        "user_id": f"eq.{user_id}",
                        "select": "count"
                    }
                )
                total = count_response.json()[0]["count"] if count_response.status_code == 200 else len(channels)
                
                return ChannelListResponse(
                    channels=channels,
                    total=total,
                    page=page,
                    per_page=per_page
                )
            return None
        except Exception as e:
            logger.error(f"Error getting user channels: {e}")
            return None

    async def get_channel_info(self, channel_id: str) -> Optional[ChannelInfoResponse]:
        """Get comprehensive channel information including stats and recent videos"""
        try:
            # Get channel data
            channel = await self.get_channel(channel_id)
            if not channel:
                return None
            
            # Get recent videos for this channel
            recent_videos_response = await self.supabase._make_request(
                "GET", 
                "videos", 
                params={
                    "channel_id": f"eq.{channel_id}",
                    "order": "published_at.desc",
                    "limit": 5
                }
            )
            
            recent_videos = []
            if recent_videos_response.status_code == 200:
                recent_videos = [VideoResponse(**video) for video in recent_videos_response.json()]
            
            # Get latest analytics
            latest_analytics_response = await self.supabase._make_request(
                "GET", 
                "roi_analytics", 
                params={
                    "channel_id": f"eq.{channel_id}",
                    "order": "generated_at.desc",
                    "limit": 1
                }
            )
            
            latest_analytics = None
            if latest_analytics_response.status_code == 200 and latest_analytics_response.json():
                latest_analytics = ROIAnalyticsResponse(**latest_analytics_response.json()[0])
            
            # Create channel stats
            channel_stats = ChannelStats(
                total_subscribers=channel.total_subscribers,
                total_videos=channel.total_videos,
                total_views=channel.total_views,
                estimated_monthly_revenue=channel.estimated_monthly_revenue,
                estimated_annual_revenue=channel.estimated_annual_revenue,
                revenue_per_subscriber=channel.revenue_per_subscriber
            )
            
            return ChannelInfoResponse(
                channel=channel,
                stats=channel_stats,
                recent_videos=recent_videos,
                latest_analytics=latest_analytics
            )
        except Exception as e:
            logger.error(f"Error getting channel info: {e}")
            return None

    async def update_channel(self, channel_id: str, channel_data: ChannelUpdate) -> Optional[ChannelResponse]:
        """Update channel data"""
        try:
            data = {k: v for k, v in channel_data.dict().items() if v is not None}
            response = await self.supabase._make_request(
                "PATCH", 
                f"channels?channel_id=eq.{channel_id}", 
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                return ChannelResponse(**result[0]) if result else None
            return None
        except Exception as e:
            logger.error(f"Error updating channel: {e}")
            return None

    # ROI Analytics Operations
    async def create_roi_analytics(self, roi_data: ROIAnalyticsCreate) -> Optional[ROIAnalyticsResponse]:
        """Create a new ROI analytics record"""
        try:
            data = roi_data.dict()
            response = await self.supabase._make_request("POST", "roi_analytics", data=data)
            
            if response.status_code == 201:
                result = response.json()
                return ROIAnalyticsResponse(**result[0]) if result else None
            else:
                logger.error(f"Failed to create ROI analytics: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error creating ROI analytics: {e}")
            return None

    async def get_roi_analytics(self, analytics_id: str) -> Optional[ROIAnalyticsResponse]:
        """Get ROI analytics by ID"""
        try:
            response = await self.supabase._make_request(
                "GET", 
                f"roi_analytics?id=eq.{analytics_id}"
            )
            
            if response.status_code == 200:
                result = response.json()
                return ROIAnalyticsResponse(**result[0]) if result else None
            return None
        except Exception as e:
            logger.error(f"Error getting ROI analytics: {e}")
            return None

    async def get_channel_roi_analytics(
        self, 
        channel_id: str, 
        analysis_period: Optional[str] = None,
        limit: int = 10
    ) -> List[ROIAnalyticsResponse]:
        """Get ROI analytics for a channel"""
        try:
            params = {
                "channel_id": f"eq.{channel_id}",
                "order": "generated_at.desc",
                "limit": limit
            }
            
            if analysis_period:
                params["analysis_period"] = f"eq.{analysis_period}"
            
            response = await self.supabase._make_request("GET", "roi_analytics", params=params)
            
            if response.status_code == 200:
                return [ROIAnalyticsResponse(**analytics) for analytics in response.json()]
            return []
        except Exception as e:
            logger.error(f"Error getting channel ROI analytics: {e}")
            return []

    async def get_roi_analytics_info(self, analytics_id: str) -> Optional[ROIAnalyticsInfoResponse]:
        """Get comprehensive ROI analytics information"""
        try:
            # Get analytics data
            analytics = await self.get_roi_analytics(analytics_id)
            if not analytics:
                return None
            
            # Get channel info
            channel = await self.get_channel(analytics.channel_id)
            if not channel:
                return None
            
            # Get top performing videos for this channel
            top_videos_response = await self.supabase._make_request(
                "GET", 
                "videos", 
                params={
                    "channel_id": f"eq.{analytics.channel_id}",
                    "order": "roi_score.desc",
                    "limit": 5
                }
            )
            
            top_performing_videos = []
            if top_videos_response.status_code == 200:
                top_performing_videos = [VideoResponse(**video) for video in top_videos_response.json()]
            
            # Create analytics summary
            recommendations_count = len(analytics.recommendations.get("recommendations", [])) if analytics.recommendations else 0
            
            summary = ROIAnalyticsSummary(
                analysis_period=analytics.analysis_period,
                total_views=analytics.total_views_period or 0,
                total_likes=analytics.total_likes_period or 0,
                total_comments=analytics.total_comments_period or 0,
                avg_engagement_rate=analytics.avg_engagement_rate or 0.0,
                optimal_video_length=analytics.optimal_video_length,
                recommendations_count=recommendations_count
            )
            
            return ROIAnalyticsInfoResponse(
                analytics=analytics,
                summary=summary,
                channel_info=channel,
                top_performing_videos=top_performing_videos
            )
        except Exception as e:
            logger.error(f"Error getting ROI analytics info: {e}")
            return None

    async def update_roi_analytics(self, analytics_id: str, roi_data: ROIAnalyticsUpdate) -> Optional[ROIAnalyticsResponse]:
        """Update ROI analytics data"""
        try:
            data = {k: v for k, v in roi_data.dict().items() if v is not None}
            response = await self.supabase._make_request(
                "PATCH", 
                f"roi_analytics?id=eq.{analytics_id}", 
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                return ROIAnalyticsResponse(**result[0]) if result else None
            return None
        except Exception as e:
            logger.error(f"Error updating ROI analytics: {e}")
            return None

    # Utility Methods
    async def sync_video_stats_from_youtube(self, video_id: str, youtube_stats: Dict[str, Any]) -> bool:
        """Sync video statistics from YouTube API"""
        try:
            stats_data = {
                "views": youtube_stats.get("viewCount", 0),
                "likes": youtube_stats.get("likeCount", 0),
                "comments": youtube_stats.get("commentCount", 0),
                "watch_time_hours": youtube_stats.get("watchTimeHours", 0.0),
                "engagement_rate": youtube_stats.get("engagementRate", 0.0)
            }
            
            response = await self.supabase._make_request(
                "PATCH", 
                f"videos?video_id=eq.{video_id}", 
                data=stats_data
            )
            
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error syncing video stats: {e}")
            return False

    async def sync_channel_stats_from_youtube(self, channel_id: str, youtube_stats: Dict[str, Any]) -> bool:
        """Sync channel statistics from YouTube API"""
        try:
            stats_data = {
                "total_subscribers": youtube_stats.get("subscriberCount", 0),
                "total_videos": youtube_stats.get("videoCount", 0),
                "total_views": youtube_stats.get("viewCount", 0),
                "last_synced_at": datetime.now().isoformat()
            }
            
            response = await self.supabase._make_request(
                "PATCH", 
                f"channels?channel_id=eq.{channel_id}", 
                data=stats_data
            )
            
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error syncing channel stats: {e}")
            return False

    async def get_user_youtube_overview(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive YouTube overview for a user"""
        try:
            # Get user's channels
            channels_response = await self.supabase._make_request(
                "GET", 
                "channels", 
                params={"user_id": f"eq.{user_id}"}
            )
            
            channels = []
            if channels_response.status_code == 200:
                channels = [ChannelResponse(**channel) for channel in channels_response.json()]
            
            # Get total videos count
            videos_count_response = await self.supabase._make_request(
                "GET", 
                "videos", 
                params={
                    "user_id": f"eq.{user_id}",
                    "select": "count"
                }
            )
            
            total_videos = 0
            if videos_count_response.status_code == 200:
                total_videos = videos_count_response.json()[0]["count"]
            
            # Get latest analytics
            latest_analytics_response = await self.supabase._make_request(
                "GET", 
                "roi_analytics", 
                params={
                    "user_id": f"eq.{user_id}",
                    "order": "generated_at.desc",
                    "limit": 1
                }
            )
            
            latest_analytics = None
            if latest_analytics_response.status_code == 200 and latest_analytics_response.json():
                latest_analytics = ROIAnalyticsResponse(**latest_analytics_response.json()[0])
            
            return {
                "channels": channels,
                "total_videos": total_videos,
                "latest_analytics": latest_analytics,
                "total_channels": len(channels)
            }
        except Exception as e:
            logger.error(f"Error getting user YouTube overview: {e}")
            return {
                "channels": [],
                "total_videos": 0,
                "latest_analytics": None,
                "total_channels": 0
            }

    async def record_video_upload(
        self,
        user_id: str,
        video_id: str,
        title: str,
        description: str,
        tags: Optional[List[str]] = None,
        privacy_status: str = "private",
        channel_id: Optional[str] = None,
        upload_status: str = "uploaded",
        video_url: Optional[str] = None
    ) -> Optional[VideoResponse]:
        """
        Record a video upload in the database after successful YouTube upload
        
        Args:
            user_id: User ID who uploaded the video
            video_id: YouTube video ID
            title: Video title
            description: Video description
            tags: List of video tags
            privacy_status: Privacy status of the video
            channel_id: YouTube channel ID (optional, will be fetched if not provided)
            upload_status: Upload status from YouTube
            video_url: Video URL
            
        Returns:
            VideoResponse object if successful, None otherwise
        """
        try:
            # If channel_id is not provided, try to get it from user's channels
            if not channel_id:
                channels_response = await self.supabase._make_request(
                    "GET", 
                    "channels", 
                    params={"user_id": f"eq.{user_id}"}
                )
                
                if channels_response.status_code == 200 and channels_response.json():
                    # Use the first channel found for this user
                    channel_id = channels_response.json()[0]["channel_id"]
                else:
                    logger.warning(f"No channel found for user {user_id}, cannot record video upload")
                    return None
            
            # Create video data
            video_data = VideoCreate(
                video_id=video_id,
                user_id=user_id,
                title=title,
                description=description,
                tags=tags or [],
                channel_id=channel_id,
                published_at=datetime.now(),
                views=0,  # New upload, no views yet
                likes=0,
                comments=0,
                engagement_rate=0.0,
                watch_time_hours=0.0,
                duration_seconds=None,  # Will be updated when stats are synced
                roi_score=None  # Will be calculated later
            )
            
            # Create the video record
            video_record = await self.create_video(video_data)
            
            if video_record:
                logger.info(f"Successfully recorded video upload: {video_id} for user {user_id}")
                return video_record
            else:
                logger.error(f"Failed to create video record for upload: {video_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error recording video upload: {e}")
            return None

    async def get_or_create_channel_for_user(
        self,
        user_id: str,
        channel_info: Dict[str, Any]
    ) -> Optional[str]:
        """
        Get or create a channel record for a user based on YouTube channel info
        
        Args:
            user_id: User ID
            channel_info: Channel information from YouTube API
            
        Returns:
            Channel ID if successful, None otherwise
        """
        try:
            channel_id = channel_info.get("id")
            if not channel_id:
                return None
            
            # Check if channel already exists
            existing_channel = await self.get_channel(channel_id)
            if existing_channel:
                return channel_id
            
            # Create new channel record
            channel_data = ChannelCreate(
                channel_id=channel_id,
                user_id=user_id,
                channel_title=channel_info.get("title", "Unknown Channel"),
                total_subscribers=int(channel_info.get("subscriber_count", 0)),
                total_videos=int(channel_info.get("video_count", 0)),
                total_views=int(channel_info.get("view_count", 0)),
                channel_created=None,  # Not provided by YouTube API
                estimated_monthly_revenue=None,
                estimated_annual_revenue=None,
                revenue_per_subscriber=None,
                last_synced_at=datetime.now()
            )
            
            channel_record = await self.create_channel(channel_data)
            if channel_record:
                logger.info(f"Created new channel record: {channel_id} for user {user_id}")
                return channel_id
            else:
                logger.error(f"Failed to create channel record: {channel_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting or creating channel: {e}")
            return None

# Create a singleton instance
youtube_data_service = YouTubeDataService()
