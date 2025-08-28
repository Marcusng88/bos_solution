from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

# Video Schema - Updated to match database structure
class VideoBase(BaseModel):
    """Base video schema matching database structure"""
    video_id: str = Field(..., description="YouTube video ID")
    user_id: str = Field(..., description="User ID who owns the video")
    title: Optional[str] = Field(None, description="Video title")
    published_at: Optional[datetime] = Field(None, description="Video publication date")
    views: Optional[int] = Field(None, description="Total view count")
    likes: Optional[int] = Field(None, description="Total like count")
    comments: Optional[int] = Field(None, description="Total comment count")
    engagement_rate: Optional[float] = Field(None, ge=0, le=1, description="Engagement rate (0-1)")
    watch_time_hours: Optional[float] = Field(None, description="Total watch time in hours")
    duration_seconds: Optional[int] = Field(None, description="Video duration in seconds")
    roi_score: Optional[float] = Field(None, description="ROI performance score")
    tags: Optional[List[str]] = Field(None, description="Video tags")
    channel_id: str = Field(..., description="YouTube channel ID")

class VideoCreate(VideoBase):
    """Schema for creating a new video record"""
    pass

class VideoUpdate(BaseModel):
    """Schema for updating video data"""
    title: Optional[str] = None
    views: Optional[int] = None
    likes: Optional[int] = None
    comments: Optional[int] = None
    engagement_rate: Optional[float] = Field(None, ge=0, le=1)
    watch_time_hours: Optional[float] = None
    duration_seconds: Optional[int] = None
    roi_score: Optional[float] = None
    tags: Optional[List[str]] = None

class VideoResponse(VideoBase):
    """Schema for video response"""
    id: str = Field(..., description="Database record ID")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Record last update timestamp")
    
    class Config:
        from_attributes = True

# Channel Schema - Updated to match database structure
class ChannelBase(BaseModel):
    """Base channel schema matching database structure"""
    channel_id: str = Field(..., description="YouTube channel ID")
    user_id: str = Field(..., description="User ID who owns the channel")
    channel_title: str = Field(..., description="Channel title")
    total_subscribers: int = Field(0, description="Total subscriber count")
    total_videos: int = Field(0, description="Total video count")
    total_views: int = Field(0, description="Total view count")
    channel_created: Optional[datetime] = Field(None, description="Channel creation date")
    estimated_monthly_revenue: Optional[float] = Field(None, description="Estimated monthly revenue")
    estimated_annual_revenue: Optional[float] = Field(None, description="Estimated annual revenue")
    revenue_per_subscriber: Optional[float] = Field(None, description="Revenue per subscriber")
    last_synced_at: Optional[datetime] = Field(None, description="Last sync timestamp")

class ChannelCreate(ChannelBase):
    """Schema for creating a new channel record"""
    pass

class ChannelUpdate(BaseModel):
    """Schema for updating channel data"""
    channel_title: Optional[str] = None
    total_subscribers: Optional[int] = None
    total_videos: Optional[int] = None
    total_views: Optional[int] = None
    estimated_monthly_revenue: Optional[float] = None
    estimated_annual_revenue: Optional[float] = None
    revenue_per_subscriber: Optional[float] = None
    last_synced_at: Optional[datetime] = None

class ChannelResponse(ChannelBase):
    """Schema for channel response"""
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Record last update timestamp")
    
    class Config:
        from_attributes = True

# ROI Analytics Schema - Updated to match database structure
class ROIAnalyticsBase(BaseModel):
    """Base ROI analytics schema matching database structure"""
    user_id: str = Field(..., description="User ID")
    channel_id: str = Field(..., description="Channel ID for analysis")
    analysis_period: str = Field(..., description="Analysis period (e.g., '7d', '30d', '90d')")
    cutoff_time: Optional[datetime] = Field(None, description="Cutoff time for analysis")
    total_views_period: Optional[int] = Field(None, description="Total views in period")
    total_likes_period: Optional[int] = Field(None, description="Total likes in period")
    total_comments_period: Optional[int] = Field(None, description="Total comments in period")
    avg_engagement_rate: Optional[float] = Field(None, ge=0, le=1, description="Average engagement rate")
    optimal_video_length: Optional[float] = Field(None, description="Optimal video length in minutes")
    best_performing_tags: Optional[Dict[str, Any]] = Field(None, description="Best performing tags JSONB")
    recommendations: Optional[Dict[str, Any]] = Field(None, description="Recommendations JSONB")

class ROIAnalyticsCreate(ROIAnalyticsBase):
    """Schema for creating a new ROI analytics record"""
    pass

class ROIAnalyticsUpdate(BaseModel):
    """Schema for updating ROI analytics data"""
    total_views_period: Optional[int] = None
    total_likes_period: Optional[int] = None
    total_comments_period: Optional[int] = None
    avg_engagement_rate: Optional[float] = Field(None, ge=0, le=1)
    optimal_video_length: Optional[float] = None
    best_performing_tags: Optional[Dict[str, Any]] = None
    recommendations: Optional[Dict[str, Any]] = None

class ROIAnalyticsResponse(ROIAnalyticsBase):
    """Schema for ROI analytics response"""
    id: str = Field(..., description="Database record ID")
    generated_at: datetime = Field(..., description="Analysis generation timestamp")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Record last update timestamp")
    
    class Config:
        from_attributes = True

# Bulk response schemas
class VideoListResponse(BaseModel):
    """Schema for list of videos response"""
    videos: List[VideoResponse]
    total: int
    page: int
    per_page: int

class ChannelListResponse(BaseModel):
    """Schema for list of channels response"""
    channels: List[ChannelResponse]
    total: int
    page: int
    per_page: int

class ROIAnalyticsListResponse(BaseModel):
    """Schema for list of ROI analytics response"""
    analytics: List[ROIAnalyticsResponse]
    total: int
    page: int
    per_page: int

# Additional utility schemas for API responses
class ChannelStats(BaseModel):
    """Channel statistics summary"""
    total_subscribers: int
    total_videos: int
    total_views: int
    estimated_monthly_revenue: Optional[float]
    estimated_annual_revenue: Optional[float]
    revenue_per_subscriber: Optional[float]

class VideoStats(BaseModel):
    """Video statistics summary"""
    views: int
    likes: int
    comments: int
    engagement_rate: float
    watch_time_hours: float
    roi_score: Optional[float]

class ROIAnalyticsSummary(BaseModel):
    """ROI analytics summary"""
    analysis_period: str
    total_views: int
    total_likes: int
    total_comments: int
    avg_engagement_rate: float
    optimal_video_length: Optional[float]
    recommendations_count: int

# API Response schemas for specific endpoints
class ChannelInfoResponse(BaseModel):
    """Channel information response"""
    channel: ChannelResponse
    stats: ChannelStats
    recent_videos: List[VideoResponse]
    latest_analytics: Optional[ROIAnalyticsResponse]

class VideoInfoResponse(BaseModel):
    """Video information response"""
    video: VideoResponse
    stats: VideoStats
    channel_info: ChannelResponse
    performance_trend: List[Dict[str, Any]]

class ROIAnalyticsInfoResponse(BaseModel):
    """ROI analytics information response"""
    analytics: ROIAnalyticsResponse
    summary: ROIAnalyticsSummary
    channel_info: ChannelResponse
    top_performing_videos: List[VideoResponse]
