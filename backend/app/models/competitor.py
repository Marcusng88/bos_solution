"""
Competitor model for database
"""

from sqlalchemy import Column, String, Text, DateTime, Integer, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import ModelBase
from app.core.database_types import DatabaseUUID, DatabaseJSON
import uuid


class Competitor(ModelBase):
    """Competitor model"""
    
    __tablename__ = "competitors"
    
    id = Column(DatabaseUUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    website_url = Column(String(500))
    social_media_handles = Column(DatabaseJSON)  # Store platform:handle mappings
    industry = Column(String(100))
    status = Column(Enum('active', 'paused', 'error', name='monitoring_status'), default='active')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_scan_at = Column(DateTime(timezone=True))
    scan_frequency_minutes = Column(Integer, default=60)
    
    def __repr__(self):
        return f"<Competitor(id={self.id}, name='{self.name}', user_id='{self.user_id}')>"
