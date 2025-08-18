"""
User schemas for API requests and responses
"""

from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    """Base user schema"""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    profile_image_url: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new user"""
    clerk_id: str


class UserUpdate(UserBase):
    """Schema for updating user information"""
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response"""
    id: UUID
    clerk_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserMonitoringSettingsBase(BaseModel):
    """Base user monitoring settings schema"""
    global_monitoring_enabled: Optional[bool] = None


class UserMonitoringSettingsCreate(UserMonitoringSettingsBase):
    """Schema for creating user monitoring settings"""
    user_id: UUID


class UserMonitoringSettingsUpdate(UserMonitoringSettingsBase):
    """Schema for updating user monitoring settings"""
    pass


class UserMonitoringSettingsResponse(UserMonitoringSettingsBase):
    """Schema for user monitoring settings response"""
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
