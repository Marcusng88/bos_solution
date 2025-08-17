from sqlalchemy import Column, String, Text, DateTime, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base

class MyCompetitor(Base):
    __tablename__ = "my_competitors"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    user_id = Column(String(255), nullable=False)
    competitor_name = Column(String(255), nullable=False)
    website_url = Column(String(500))
    active_platforms = Column(ARRAY(Text), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
