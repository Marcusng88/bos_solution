"""
Campaign schemas for self-optimization API requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal


class CampaignDataBase(BaseModel):
    """Base campaign data schema"""
    name: str = Field(..., max_length=255)
    date: date
    impressions: int = Field(0, ge=0)
    clicks: int = Field(0, ge=0)
    ctr: Decimal = Field(0.0, ge=0.0, le=1.0)
    cpc: Decimal = Field(0.0, ge=0.0)
    spend: Decimal = Field(0.0, ge=0.0)
    budget: Decimal = Field(0.0, ge=0.0)
    conversions: int = Field(0, ge=0)
    ongoing: str = Field("No", pattern="^(Yes|No)$")


class CampaignDataCreate(CampaignDataBase):
    """Schema for creating campaign data"""
    user_id: str


class CampaignDataUpdate(BaseModel):
    """Schema for updating campaign data"""
    name: Optional[str] = Field(None, max_length=255)
    date: Optional[date] = None
    impressions: Optional[int] = Field(None, ge=0)
    clicks: Optional[int] = Field(None, ge=0)
    ctr: Optional[Decimal] = Field(None, ge=0.0, le=1.0)
    cpc: Optional[Decimal] = Field(None, ge=0.0)
    spend: Optional[Decimal] = Field(None, ge=0.0)
    budget: Optional[Decimal] = Field(None, ge=0.0)
    conversions: Optional[int] = Field(None, ge=0)
    ongoing: Optional[str] = Field(None, pattern="^(Yes|No)$")


class CampaignDataResponse(CampaignDataBase):
    """Schema for campaign data response"""
    id: UUID
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str,
            Decimal: float,
            date: lambda v: v.isoformat()
        }


class OptimizationAlertBase(BaseModel):
    """Base optimization alert schema"""
    campaign_name: Optional[str] = Field(None, max_length=255)
    alert_type: str = Field(..., max_length=50)
    priority: str = Field("medium", pattern="^(low|medium|high|critical)$")
    title: str = Field(..., max_length=255)
    message: str
    recommendation: Optional[str] = None
    alert_data: Optional[str] = None


class OptimizationAlertCreate(OptimizationAlertBase):
    """Schema for creating optimization alert"""
    user_id: str


class OptimizationAlertResponse(OptimizationAlertBase):
    """Schema for optimization alert response"""
    id: UUID
    user_id: str
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


class RiskPatternBase(BaseModel):
    """Base risk pattern schema"""
    campaign_name: str = Field(..., max_length=255)
    pattern_type: str = Field(..., max_length=50)
    severity: str = Field("medium", pattern="^(low|medium|high|critical)$")
    pattern_data: Optional[str] = None


class RiskPatternCreate(RiskPatternBase):
    """Schema for creating risk pattern"""
    user_id: str


class RiskPatternResponse(RiskPatternBase):
    """Schema for risk pattern response"""
    id: UUID
    user_id: str
    detected_at: datetime
    resolved: bool
    resolved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str
        }


class OptimizationRecommendationBase(BaseModel):
    """Base optimization recommendation schema"""
    campaign_name: Optional[str] = Field(None, max_length=255)
    recommendation_type: str = Field(..., max_length=50)
    priority: str = Field("medium", pattern="^(low|medium|high|critical)$")
    title: str = Field(..., max_length=255)
    description: str
    action_items: Optional[str] = None
    potential_impact: Optional[str] = None
    confidence_score: Decimal = Field(0.0, ge=0.0, le=1.0)


class OptimizationRecommendationCreate(OptimizationRecommendationBase):
    """Schema for creating optimization recommendation"""
    user_id: str


class OptimizationRecommendationResponse(OptimizationRecommendationBase):
    """Schema for optimization recommendation response"""
    id: UUID
    user_id: str
    is_applied: bool
    applied_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str,
            Decimal: float
        }


class CampaignStatsResponse(BaseModel):
    """Schema for campaign statistics response"""
    total_campaigns: int
    active_campaigns: int
    total_spend: Decimal
    total_budget: Decimal
    avg_ctr: Decimal
    avg_cpc: Decimal
    total_conversions: int
    budget_utilization: Decimal
    
    class Config:
        json_encoders = {
            Decimal: float
        }


class DashboardMetrics(BaseModel):
    """Schema for dashboard metrics"""
    spend_today: Decimal
    budget_today: Decimal
    alerts_count: int
    risk_patterns_count: int
    recommendations_count: int
    budget_utilization_pct: Decimal
    
    class Config:
        json_encoders = {
            Decimal: float
        }


class BudgetMonitoringResponse(BaseModel):
    """Schema for budget monitoring response"""
    campaign_name: str
    date: date
    spend: Decimal
    budget: Decimal
    utilization_pct: Decimal
    status: str  # normal, warning, critical
    
    class Config:
        json_encoders = {
            Decimal: float,
            date: lambda v: v.isoformat()
        }


class CampaignPerformanceResponse(BaseModel):
    """Schema for campaign performance trends"""
    campaign_name: str
    dates: List[str]
    spend_trend: List[Decimal]
    ctr_trend: List[Decimal]
    cpc_trend: List[Decimal]
    conversions_trend: List[int]
    
    class Config:
        json_encoders = {
            Decimal: float
        }
