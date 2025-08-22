"""
User Pydantic schemas for request/response validation
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class UserBase(BaseModel):
    """Base user schema"""
    clerk_id: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    profile_image_url: Optional[str] = None
    is_active: Optional[bool] = True


class UserCreate(UserBase):
    """Schema for creating a new user from Clerk data"""
    pass


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    profile_image_url: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response"""
    id: uuid.UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ClerkUserData(BaseModel):
    """Schema for Clerk user data payload"""
    id: str  # Clerk user ID
    email_addresses: List[Dict[str, Any]]
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    image_url: Optional[str] = None
    primary_email_address_id: Optional[str] = None
    
    def get_primary_email(self) -> Optional[str]:
        """Extract primary email from email addresses"""
        if not self.email_addresses:
            return None
        
        # Find primary email
        if self.primary_email_address_id:
            for email_obj in self.email_addresses:
                if email_obj.get("id") == self.primary_email_address_id:
                    return email_obj.get("email_address")
        
        # Fallback to first email
        if self.email_addresses and len(self.email_addresses) > 0:
            return self.email_addresses[0].get("email_address")
        
        return None
