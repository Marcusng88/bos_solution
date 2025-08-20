"""
User monitoring settings model for database
"""

from sqlalchemy import Column, String, Boolean, Integer, DateTime
from sqlalchemy.sql import func
from app.core.database import Base
from app.core.database_types import DatabaseUUID, DatabaseJSON
import uuid


class UserMonitoringSettings(Base):
    """User monitoring settings model"""
    
    __tablename__ = "user_monitoring_settings"
    
    id = Column(DatabaseUUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=False, unique=True, index=True)
    global_monitoring_enabled = Column(Boolean, default=True)
    default_scan_frequency_minutes = Column(Integer, default=60)
    alert_preferences = Column(DatabaseJSON, default={
        "email_alerts": True,
        "push_notifications": True,
        "new_posts": True,
        "content_changes": True,
        "engagement_spikes": True,
        "sentiment_changes": True
    })
    notification_schedule = Column(DatabaseJSON, default={
        "quiet_hours_start": "22:00",
        "quiet_hours_end": "08:00",
        "timezone": "UTC"
    })
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<UserMonitoringSettings(id={self.id}, user_id='{self.user_id}')>"
