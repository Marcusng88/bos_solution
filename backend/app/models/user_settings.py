"""
User models for database
"""

from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import ModelBase
import uuid


class User(ModelBase):
    """User model for Clerk integration"""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clerk_id = Column(String(255), nullable=False, unique=True, index=True)
    email = Column(String(255), index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    profile_image_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    monitoring_settings = relationship("UserMonitoringSettings", back_populates="user", uselist=False)
    competitors = relationship("Competitor", back_populates="user")
    monitoring_alerts = relationship("MonitoringAlert", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, clerk_id='{self.clerk_id}', email='{self.email}')>"


class UserMonitoringSettings(ModelBase):
    """User monitoring settings model"""
    
    __tablename__ = "user_monitoring_settings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    global_monitoring_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="monitoring_settings")
    
    def __repr__(self):
        return f"<UserMonitoringSettings(id={self.id}, user_id='{self.user_id}')>"
