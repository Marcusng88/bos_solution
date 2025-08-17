"""
Campaign models for self-optimization database
"""

from sqlalchemy import Column, String, Text, DateTime, Boolean, Numeric, Integer, Date, Float
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.sql import func
from app.core.database import ModelBase
import uuid


class CampaignData(ModelBase):
    """Campaign data model for self-optimization analysis"""
    
    __tablename__ = "campaign_data"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=True)
    date = Column(Date, nullable=True)
    impressions = Column(Integer, nullable=True)
    clicks = Column(Integer, nullable=True)
    ctr = Column(Float, nullable=True)  # Changed to FLOAT to match your SQL script
    cpc = Column(Float, nullable=True)  # Changed to FLOAT to match your SQL script
    spend = Column(Float, nullable=True)  # Changed to FLOAT to match your SQL script
    budget = Column(Float, nullable=True)  # Changed to FLOAT to match your SQL script
    conversions = Column(Integer, nullable=True)
    net_profit = Column(Float, nullable=True)  # Changed to FLOAT to match your SQL script
    ongoing = Column(String(10), nullable=True)  # Changed to VARCHAR(10) to match your schema
    
    def __repr__(self):
        return f"<CampaignData(id={self.id}, name='{self.name}', date='{self.date}')>"


class OptimizationAlert(ModelBase):
    """Optimization alerts model for self-optimization"""
    
    __tablename__ = "optimization_alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_name = Column(String(255), index=True)
    alert_type = Column(String(50), nullable=False)  # overspend, low_roi, spike, etc.
    priority = Column(ENUM('low', 'medium', 'high', 'critical', name='alert_priority'), default='medium')
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    recommendation = Column(Text)
    alert_data = Column(Text)  # JSON string for additional data
    is_read = Column(Boolean, default=False, index=True)
    is_dismissed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    read_at = Column(DateTime(timezone=True))
    dismissed_at = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<OptimizationAlert(id={self.id}, type='{self.alert_type}', campaign='{self.campaign_name}')>"


class RiskPattern(ModelBase):
    """Risk patterns model for tracking spending and performance anomalies"""
    
    __tablename__ = "risk_patterns"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_name = Column(String(255), nullable=False, index=True)
    pattern_type = Column(String(50), nullable=False)  # spending_spike, low_ctr, high_cpc, etc.
    severity = Column(ENUM('low', 'medium', 'high', 'critical', name='risk_severity'), default='medium')
    detected_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    pattern_data = Column(Text)  # JSON string for pattern details
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<RiskPattern(id={self.id}, type='{self.pattern_type}', campaign='{self.campaign_name}')>"


class OptimizationRecommendation(ModelBase):
    """Optimization recommendations model"""
    
    __tablename__ = "optimization_recommendations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_name = Column(String(255), index=True)
    recommendation_type = Column(String(50), nullable=False)  # pause, reallocate, optimize_creative, etc.
    priority = Column(ENUM('low', 'medium', 'high', 'critical', name='recommendation_priority'), default='medium')
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    action_items = Column(Text)  # JSON string for specific actions
    potential_impact = Column(Text)  # Expected impact description
    confidence_score = Column(Numeric(3, 2), default=0.0)  # 0.00 to 1.00
    is_applied = Column(Boolean, default=False)
    applied_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    def __repr__(self):
        return f"<OptimizationRecommendation(id={self.id}, type='{self.recommendation_type}', campaign='{self.campaign_name}')>"
