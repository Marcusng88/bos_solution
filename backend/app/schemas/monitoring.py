"""
Monitoring schemas for API requests and responses
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class MonitoringDataBase(BaseModel):
    """Base monitoring data schema"""
    platform: str = Field(..., pattern="^(instagram|facebook|twitter|linkedin|tiktok|youtube|website|browser|other)$")
    post_id: Optional[str] = Field(None, max_length=255)
    post_url: Optional[HttpUrl] = None
    content_text: Optional[str] = None
    media_urls: Optional[List[str]] = None
    engagement_metrics: Optional[Dict[str, Any]] = None
    author_username: Optional[str] = Field(None, max_length=255)
    author_display_name: Optional[str] = Field(None, max_length=255)
    author_avatar_url: Optional[HttpUrl] = None
    post_type: Optional[str] = Field(None, max_length=50)
    language: Optional[str] = Field(None, max_length=10)
    sentiment_score: Optional[Decimal] = Field(None, ge=-1.0, le=1.0)
    posted_at: Optional[datetime] = None


class MonitoringDataCreate(MonitoringDataBase):
    """Schema for creating monitoring data"""
    competitor_id: UUID


class MonitoringDataResponse(MonitoringDataBase):
    """Schema for monitoring data response"""
    id: UUID
    competitor_id: UUID
    content_hash: Optional[str] = None
    detected_at: datetime
    is_new_post: bool
    is_content_change: bool
    previous_content_hash: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str,
            Decimal: float
        }


class MonitoringAlertBase(BaseModel):
    """Base monitoring alert schema"""
    alert_type: str = Field(..., max_length=50)
    priority: str = Field("medium", pattern="^(low|medium|high|critical)$")
    title: str = Field(..., max_length=255)
    message: str
    alert_metadata: Optional[Dict[str, Any]] = None


class MonitoringAlertCreate(MonitoringAlertBase):
    """Schema for creating monitoring alerts"""
    pass


class PlatformScanRequest(BaseModel):
    """Schema for platform-specific scan requests"""
    competitor_id: UUID = Field(..., description="ID of the competitor to scan")
    platforms: Optional[List[str]] = Field(None, description="Specific platforms to scan (optional)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "competitor_id": "123e4567-e89b-12d3-a456-426614174000",
                "platforms": ["youtube", "website"]
            }
        }


class PlatformScanResponse(BaseModel):
    """Schema for platform scan responses"""
    success: bool
    platform: str
    competitor_id: UUID
    result: Dict[str, Any]
    message: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "platform": "youtube",
                "competitor_id": "123e4567-e89b-12d3-a456-426614174000",
                "result": {
                    "status": "completed",
                    "content": []
                },
                "message": "Scan completed successfully"
            }
        }


class MonitoringAlertResponse(MonitoringAlertBase):
    """Schema for monitoring alert response"""
    id: UUID
    user_id: str  # Changed from UUID to str to match Clerk user IDs
    competitor_id: Optional[UUID] = None
    monitoring_data_id: Optional[UUID] = None
    is_read: bool
    is_dismissed: bool
    created_at: datetime
    read_at: Optional[datetime] = None
    dismissed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str
        }


class MonitoringStats(BaseModel):
    """Schema for monitoring statistics"""
    total_competitors: int
    total_monitoring_data: int
    unread_alerts: int
    recent_activity_24h: int
