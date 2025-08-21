"""
User monitoring settings schemas for API requests and responses
"""

from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class UserMonitoringSettingsBase(BaseModel):
    """Base user monitoring settings schema"""
    global_monitoring_enabled: Optional[bool] = None
    default_scan_frequency_minutes: Optional[int] = None
    alert_preferences: Optional[Dict[str, Any]] = None
    notification_schedule: Optional[Dict[str, Any]] = None


class UserMonitoringSettings(UserMonitoringSettingsBase):
    """Schema for user monitoring settings (matches the database model)"""
    id: UUID
    user_id: str
    user_id_new: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserMonitoringSettingsCreate(UserMonitoringSettingsBase):
    """Schema for creating user monitoring settings"""
    user_id: str


class UserMonitoringSettingsUpdate(UserMonitoringSettingsBase):
    """Schema for updating user monitoring settings"""
    pass


class UserMonitoringSettingsResponse(UserMonitoringSettingsBase):
    """Schema for user monitoring settings response"""
    id: UUID
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
