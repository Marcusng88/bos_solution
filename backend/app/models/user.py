"""
User model for database - matches Supabase users table structure
"""

from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import ModelBase
from app.core.database_types import DatabaseUUID
import uuid


class User(ModelBase):
    """User model matching Supabase users table structure"""
    
    __tablename__ = "users"
    
    id = Column(DatabaseUUID(), primary_key=True, default=uuid.uuid4)
    clerk_id = Column(String(255), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    profile_image_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, nullable=True, default=True)
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<User(id={self.id}, clerk_id='{self.clerk_id}', email='{self.email}')>"
