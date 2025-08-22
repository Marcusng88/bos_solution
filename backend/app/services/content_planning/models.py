"""
Pydantic models for Content Planning service
Follows the same pattern as other services in the app
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


# Request Models
class ContentGenerationRequest(BaseModel):
    """Request model for content generation"""
    industry: str = Field(..., description="Target industry sector")
    platform: str = Field(..., description="Social media platform")
    content_type: str = Field(..., description="Type of content to generate")
    tone: str = Field(default="professional", description="Tone of voice")
    target_audience: str = Field(..., description="Target audience description")
    custom_requirements: Optional[str] = Field(None, description="Custom requirements")
    generate_variations: bool = Field(default=False, description="Generate multiple variations")


class CompetitorAnalysisRequest(BaseModel):
    """Request model for competitor analysis"""
    industry: str = Field(..., description="Industry to analyze")
    competitor_ids: Optional[List[str]] = Field(None, description="Specific competitor IDs")
    analysis_type: str = Field(default="comprehensive_analysis", description="Type of analysis")
    time_period: str = Field(default="last_30_days", description="Analysis time period")


class HashtagResearchRequest(BaseModel):
    """Request model for hashtag research"""
    industry: str = Field(..., description="Target industry")
    content_type: str = Field(..., description="Content type")
    platform: str = Field(..., description="Social media platform")
    target_audience: str = Field(..., description="Target audience")
    custom_keywords: Optional[List[str]] = Field(None, description="Custom keywords")


class ContentStrategyRequest(BaseModel):
    """Request model for content strategy generation"""
    industry: str = Field(..., description="Target industry")
    platforms: List[str] = Field(..., description="Target platforms")
    content_goals: List[str] = Field(..., description="Content goals")
    target_audience: str = Field(..., description="Target audience")


class ContentCalendarRequest(BaseModel):
    """Request model for content calendar generation"""
    industry: str = Field(..., description="Target industry")
    platforms: List[str] = Field(..., description="Target platforms")
    duration_days: int = Field(default=30, description="Calendar duration in days")
    posts_per_day: int = Field(default=2, description="Posts per day")


class ContentGapsRequest(BaseModel):
    """Request model for content gap identification"""
    industry: str = Field(..., description="Target industry")
    user_content_summary: str = Field(..., description="Summary of user's current content")


class ScheduleOptimizationRequest(BaseModel):
    """Request model for posting schedule optimization"""
    industry: str = Field(..., description="Target industry")
    platforms: List[str] = Field(..., description="Target platforms")


# Response Models
class ContentGenerationResponse(BaseModel):
    """Response model for generated content"""
    success: bool
    content: Optional[Dict[str, Any]] = None
    variations: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None


class CompetitorAnalysisResponse(BaseModel):
    """Response model for competitor analysis"""
    success: bool
    analysis: Optional[Dict[str, Any]] = None
    insights: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[str]] = None
    error: Optional[str] = None


class HashtagResearchResponse(BaseModel):
    """Response model for hashtag research"""
    success: bool
    recommended_hashtags: Optional[Dict[str, Any]] = None
    hashtag_analysis: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ContentStrategyResponse(BaseModel):
    """Response model for content strategy"""
    success: bool
    strategy: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ContentCalendarResponse(BaseModel):
    """Response model for content calendar"""
    success: bool
    calendar: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ContentGapsResponse(BaseModel):
    """Response model for content gap analysis"""
    success: bool
    gaps_identified: Optional[Dict[str, Any]] = None
    content_suggestions: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None


class ScheduleOptimizationResponse(BaseModel):
    """Response model for schedule optimization"""
    success: bool
    optimized_schedule: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class DashboardDataResponse(BaseModel):
    """Response model for dashboard data"""
    success: bool
    summary: Optional[Dict[str, Any]] = None
    competitive_intelligence: Optional[Dict[str, Any]] = None
    content_gaps: Optional[List[Dict[str, Any]]] = None
    recent_activity: Optional[List[Dict[str, Any]]] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class IndustryInsightsResponse(BaseModel):
    """Response model for industry insights"""
    success: bool
    insights: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class SupportedOptionsResponse(BaseModel):
    """Response model for supported options"""
    industries: List[str]
    platforms: List[str]
    content_types: List[str]
    tones: List[str]
