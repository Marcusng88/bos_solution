from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class DraftStatus(str, Enum):
    draft = "draft"
    ready = "ready"
    archived = "archived"

class DraftCreate(BaseModel):
    title: str = Field(..., max_length=200)
    content: str = Field(..., max_length=10000)
    platform: str = Field(..., description="Primary platform")
    content_type: str = Field(..., description="Type of content")
    status: str = Field(default="draft")
    source_id: Optional[str] = Field(None)
    hashtags: List[str] = Field(default_factory=list)
    media_urls: List[str] = Field(default_factory=list)
    scheduling_options: Optional[Dict[str, Any]] = Field(default_factory=dict)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class DraftUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = Field(None, max_length=10000)
    platform: Optional[str] = None
    content_type: Optional[str] = None
    status: Optional[str] = None
    hashtags: Optional[List[str]] = None
    media_urls: Optional[List[str]] = None
    scheduling_options: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class DraftResponse(BaseModel):
    id: str
    user_id: str
    title: str
    content: str
    platform: str
    content_type: str
    status: str
    source_id: Optional[str]
    hashtags: List[str]
    media_urls: List[str]
    scheduling_options: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

class DraftListResponse(BaseModel):
    drafts: List[DraftResponse]
    total: int
    page: int
    per_page: int
