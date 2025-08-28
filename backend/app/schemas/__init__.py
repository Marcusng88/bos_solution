# Pydantic schemas package

from .user import UserCreate, UserUpdate, UserResponse, ClerkUserData
from .user_preferences import UserPreferences, UserPreferencesCreate, UserPreferencesUpdate
from .user_settings import UserMonitoringSettings, UserMonitoringSettingsResponse, UserMonitoringSettingsUpdate
from .competitor import Competitor, CompetitorCreate, CompetitorUpdate
from .monitoring import MonitoringDataResponse, MonitoringAlertResponse
from .social_media import SocialMediaAccount, SocialMediaAccountCreate, SocialMediaAccountUpdate
from .youtube import (
    # Video schemas
    VideoBase, VideoCreate, VideoUpdate, VideoResponse, VideoListResponse, VideoStats,
    # Channel schemas
    ChannelBase, ChannelCreate, ChannelUpdate, ChannelResponse, ChannelListResponse, ChannelStats,
    # ROI Analytics schemas
    ROIAnalyticsBase, ROIAnalyticsCreate, ROIAnalyticsUpdate, ROIAnalyticsResponse, ROIAnalyticsListResponse,
    # Utility schemas
    VideoInfoResponse, ChannelInfoResponse, ROIAnalyticsInfoResponse, ROIAnalyticsSummary
)
