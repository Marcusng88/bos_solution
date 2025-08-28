"""
AI Insights schemas for request/response models
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime


class AIAnalysisRequest(BaseModel):
    """Request model for AI analysis"""
    include_competitors: bool = Field(default=True, description="Include competitor analysis")
    include_monitoring: bool = Field(default=True, description="Include monitoring data")
    analysis_type: str = Field(default="comprehensive", description="Type of analysis to perform")


class AIAnalysisResponse(BaseModel):
    """Response model for AI analysis"""
    success: bool
    analysis: Dict[str, Any]
    message: str


class AIChatRequest(BaseModel):
    """Request model for AI chat"""
    message: str = Field(..., description="User message to AI")


class AIChatResponse(BaseModel):
    """Response model for AI chat"""
    success: bool
    response: str
    message: str


class AIInsightsResponse(BaseModel):
    """Response model for AI insights"""
    success: bool
    insights: Dict[str, Any]
    message: str


class AIRecommendation(BaseModel):
    """AI recommendation model"""
    id: str
    type: str
    title: str
    description: str
    priority: str
    impact: str
    action_items: List[str]
    confidence_score: float
    created_at: datetime


class AIRiskAlert(BaseModel):
    """AI risk alert model"""
    id: str
    type: str
    title: str
    description: str
    severity: str
    affected_campaigns: List[str]
    mitigation_strategy: str
    created_at: datetime


class AIPerformanceInsight(BaseModel):
    """AI performance insight model"""
    id: str
    type: str
    title: str
    description: str
    metrics: Dict[str, Any]
    trend: str
    recommendation: str
    created_at: datetime
