from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class SocialMediaPlatform(str, Enum):
    instagram = "instagram"
    facebook = "facebook"
    twitter = "twitter"
    linkedin = "linkedin"
    tiktok = "tiktok"
    youtube = "youtube"
    other = "other"

class ContentStatus(str, Enum):
    draft = "draft"
    scheduled = "scheduled"
    posted = "posted"
    failed = "failed"
    cancelled = "cancelled"

class MediaFile(BaseModel):
    url: str
    type: str = Field(..., description="Type of media: image, video, gif, etc.")
    size: Optional[int] = Field(None, description="File size in bytes")
    filename: Optional[str] = Field(None, description="Original filename")
    mime_type: Optional[str] = Field(None, description="MIME type of the file")

class SocialMediaAccountBase(BaseModel):
    platform: SocialMediaPlatform
    account_name: str = Field(..., min_length=1, max_length=255)
    is_test_account: bool = Field(False, description="Mark as test account for safe testing")

class SocialMediaAccountCreate(SocialMediaAccountBase):
    pass

class SocialMediaAccountUpdate(BaseModel):
    account_name: Optional[str] = Field(None, min_length=1, max_length=255)
    is_active: Optional[bool] = None
    is_test_account: Optional[bool] = None

class SocialMediaAccountResponse(SocialMediaAccountBase):
    id: str
    user_id: str
    account_id: Optional[str] = None
    is_active: bool
    permissions: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SocialMediaAccount(SocialMediaAccountBase):
    """Schema for social media account data (matches database model)"""
    id: str
    user_id: str
    account_id: Optional[str] = None
    is_active: bool
    permissions: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ContentUploadBase(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    content_text: str = Field(..., min_length=1)
    media_files: Optional[List[MediaFile]] = None
    scheduled_at: Optional[datetime] = None
    platform: SocialMediaPlatform
    account_id: str
    is_test_post: bool = Field(False, description="Mark as test post for safe testing")

    @validator('scheduled_at')
    def validate_scheduled_at(cls, v):
        if v and v <= datetime.now():
            raise ValueError('Scheduled time must be in the future')
        return v

class ContentUploadCreate(ContentUploadBase):
    pass

class ContentUploadUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    content_text: Optional[str] = Field(None, min_length=1)
    media_files: Optional[List[MediaFile]] = None
    scheduled_at: Optional[datetime] = None
    status: Optional[ContentStatus] = None
    is_test_post: Optional[bool] = None

class ContentUploadResponse(ContentUploadBase):
    id: str
    user_id: str
    status: ContentStatus
    post_id: Optional[str] = None
    post_url: Optional[str] = None
    error_message: Optional[str] = None
    upload_attempts: int
    last_attempt_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ContentTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    content_text: str = Field(..., min_length=1)
    media_files: Optional[List[MediaFile]] = None
    platforms: List[SocialMediaPlatform] = Field(..., min_items=1)
    tags: Optional[List[str]] = None
    is_active: bool = True

class ContentTemplateCreate(ContentTemplateBase):
    pass

class ContentTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    content_text: Optional[str] = Field(None, min_length=1)
    media_files: Optional[List[MediaFile]] = None
    platforms: Optional[List[SocialMediaPlatform]] = Field(None, min_items=1)
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None

class ContentTemplateResponse(ContentTemplateBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UploadPreview(BaseModel):
    """Preview of how content will look on different platforms"""
    platform: SocialMediaPlatform
    preview_text: str
    character_count: int
    media_count: int
    estimated_engagement: Optional[Dict[str, Any]] = None
    warnings: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)

class BulkUploadRequest(BaseModel):
    """Request to upload the same content to multiple platforms"""
    content: ContentUploadBase
    platforms: List[SocialMediaPlatform] = Field(..., min_items=1)
    schedule_strategy: str = Field("simultaneous", description="simultaneous, staggered, or custom")
    custom_schedule: Optional[Dict[str, datetime]] = None

class UploadAnalytics(BaseModel):
    """Analytics for uploaded content"""
    post_id: str
    platform: SocialMediaPlatform
    impressions: Optional[int] = None
    reach: Optional[int] = None
    engagement: Optional[int] = None
    clicks: Optional[int] = None
    shares: Optional[int] = None
    comments: Optional[int] = None
    likes: Optional[int] = None
    collected_at: datetime
