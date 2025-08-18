"""
Monitoring models for database
"""

from sqlalchemy import Column, String, Text, DateTime, Boolean, Numeric, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB, ENUM
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import ModelBase
import uuid





class MonitoringData(ModelBase):
    """Monitoring data model for social media posts"""
    
    __tablename__ = "monitoring_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competitor_id = Column(UUID(as_uuid=True), ForeignKey("competitors.id"), nullable=False, index=True)
    platform = Column(ENUM('instagram', 'facebook', 'twitter', 'linkedin', 'tiktok', 'youtube', 'other', name='social_media_platform'), nullable=False)
    post_id = Column(String(255))
    post_url = Column(String(500))
    content_text = Column(Text)
    content_hash = Column(String(64), index=True)
    media_urls = Column(JSONB)
    engagement_metrics = Column(JSONB)
    author_username = Column(String(255))
    author_display_name = Column(String(255))
    author_avatar_url = Column(String(500))
    post_type = Column(String(50))
    language = Column(String(10))
    sentiment_score = Column(Numeric(3, 2))
    detected_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    posted_at = Column(DateTime(timezone=True), index=True)
    is_new_post = Column(Boolean, default=True)
    is_content_change = Column(Boolean, default=False)
    previous_content_hash = Column(String(64))
    
    # Relationships
    competitor = relationship("Competitor", back_populates="monitoring_data")
    alerts = relationship("MonitoringAlert", back_populates="monitoring_data")
    
    def __repr__(self):
        return f"<MonitoringData(id={self.id}, platform='{self.platform}', competitor_id='{self.competitor_id}')>"


class MonitoringAlert(ModelBase):
    """Monitoring alerts model"""
    
    __tablename__ = "monitoring_alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    competitor_id = Column(UUID(as_uuid=True), ForeignKey("competitors.id"), index=True)
    monitoring_data_id = Column(UUID(as_uuid=True), ForeignKey("monitoring_data.id"), index=True)
    alert_type = Column(String(50), nullable=False)
    priority = Column(ENUM('low', 'medium', 'high', 'critical', name='alert_priority'), default='medium')
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    alert_metadata = Column(JSONB)
    is_read = Column(Boolean, default=False, index=True)
    is_dismissed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    read_at = Column(DateTime(timezone=True))
    dismissed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="monitoring_alerts")
    competitor = relationship("Competitor", back_populates="alerts")
    monitoring_data = relationship("MonitoringData", back_populates="alerts")
    
    def __repr__(self):
        return f"<MonitoringAlert(id={self.id}, type='{self.alert_type}', user_id='{self.user_id}')>"


class CompetitorMonitoringStatus(ModelBase):
    """Competitor monitoring status model"""
    
    __tablename__ = "competitor_monitoring_status"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competitor_id = Column(UUID(as_uuid=True), ForeignKey("competitors.id"), nullable=False, index=True)
    last_successful_scan = Column(DateTime(timezone=True))
    last_failed_scan = Column(DateTime(timezone=True))
    scan_error_message = Column(Text)
    consecutive_failures = Column(Integer, default=0)
    is_scanning = Column(Boolean, default=False)
    scan_started_at = Column(DateTime(timezone=True))
    next_scheduled_scan = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    competitor = relationship("Competitor", back_populates="monitoring_status")
    
    def __repr__(self):
        return f"<CompetitorMonitoringStatus(id={self.id}, competitor_id='{self.competitor_id}')>"
