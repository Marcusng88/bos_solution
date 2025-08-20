"""
Competitor schemas for API requests and responses
"""

from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class CompetitorBase(BaseModel):
    """Base competitor schema"""
    name: str = Field(..., min_length=1, max_length=255, description="Competitor name")
    description: Optional[str] = Field(None, description="Competitor description")
    website_url: Optional[HttpUrl] = Field(None, description="Competitor website URL")
    platforms: Optional[list[str]] = Field(None, description="Array of platforms to monitor")
    social_media_handles: Optional[Dict[str, str]] = Field(
        None, 
        description="Social media handles by platform"
    )
    industry: Optional[str] = Field(None, max_length=100, description="Industry category")
    scan_frequency_minutes: Optional[int] = Field(
        60, 
        ge=15, 
        le=1440, 
        description="Scan frequency in minutes (15 min to 24 hours)"
    )


class CompetitorCreateFrontend(BaseModel):
    """Frontend schema for creating a competitor (accepts frontend field names)"""
    name: str = Field(..., min_length=1, max_length=255, description="Competitor name")
    website: Optional[str] = Field(None, description="Competitor website URL")  # Frontend field name
    platforms: Optional[list[str]] = Field(None, description="Array of platforms to monitor")
    description: Optional[str] = Field(None, description="Competitor description")
    industry: Optional[str] = Field(None, max_length=100, description="Industry category")

class CompetitorCreate(CompetitorBase):
    """Schema for creating a competitor"""
    pass


class CompetitorUpdateFrontend(BaseModel):
    """Frontend schema for updating a competitor (accepts frontend field names)"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    website: Optional[str] = Field(None, description="Competitor website URL")  # Frontend field name
    platforms: Optional[list[str]] = Field(None, description="Array of platforms to monitor")
    description: Optional[str] = None
    industry: Optional[str] = Field(None, max_length=100)

class CompetitorUpdate(BaseModel):
    """Schema for updating a competitor"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    website_url: Optional[HttpUrl] = None
    platforms: Optional[list[str]] = None
    social_media_handles: Optional[Dict[str, str]] = None
    industry: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None, pattern="^(active|paused|error)$")
    scan_frequency_minutes: Optional[int] = Field(None, ge=15, le=1440)


class CompetitorResponse(CompetitorBase):
    """Schema for competitor response"""
    id: UUID
    user_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    last_scan_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str
        }
