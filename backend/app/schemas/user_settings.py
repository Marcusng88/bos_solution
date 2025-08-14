"""
User settings schemas for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class UserSettingsBase(BaseModel):
    """Base user settings schema"""
    global_monitoring_enabled: bool = True
    default_scan_frequency_minutes: int = Field(60, ge=15, le=1440)
    alert_preferences: Dict[str, bool] = Field(
        default={
            "email_alerts": True,
            "push_notifications": True,
            "new_posts": True,
            "content_changes": True,
            "engagement_spikes": True,
            "sentiment_changes": True
        }
    )
    notification_schedule: Dict[str, str] = Field(
        default={
            "quiet_hours_start": "22:00",
            "quiet_hours_end": "08:00",
            "timezone": "UTC"
        }
    )


class UserSettingsUpdate(BaseModel):
    """Schema for updating user settings"""
    global_monitoring_enabled: Optional[bool] = None
    default_scan_frequency_minutes: Optional[int] = Field(None, ge=15, le=1440)
    alert_preferences: Optional[Dict[str, bool]] = None
    notification_schedule: Optional[Dict[str, str]] = None


class UserSettingsResponse(UserSettingsBase):
    """Schema for user settings response"""
    id: UUID
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str
        }
