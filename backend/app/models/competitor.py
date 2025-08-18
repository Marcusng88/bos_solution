"""
Competitor model for database
"""

from sqlalchemy import Column, String, Text, DateTime, Integer, Enum, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import ModelBase
import uuid


class Competitor(ModelBase):
    """Competitor model"""
    
    __tablename__ = "competitors"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    website_url = Column(String(500))
    social_media_handles = Column(JSONB)  # Store platform:handle mappings
    platforms = Column(ARRAY(String), default=[])  # Array of platforms to monitor
    industry = Column(String(100))
    status = Column(Enum('active', 'paused', 'error', name='monitoring_status'), default='active')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_scan_at = Column(DateTime(timezone=True))
    scan_frequency_minutes = Column(Integer, default=60)
    
    # Relationships
    user = relationship("User", back_populates="competitors")
    monitoring_data = relationship("MonitoringData", back_populates="competitor", cascade="all, delete-orphan")
    alerts = relationship("MonitoringAlert", back_populates="competitor", cascade="all, delete-orphan")
    monitoring_status = relationship("CompetitorMonitoringStatus", back_populates="competitor", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Competitor(id={self.id}, name='{self.name}', user_id='{self.user_id}')>"
