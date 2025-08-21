"""
User service for managing user operations
Updated for Supabase integration without SQLAlchemy
"""

from typing import Optional, Dict, Any
from app.schemas.user import UserCreate, UserUpdate, UserResponse
import logging

logger = logging.getLogger(__name__)

class UserService:
    """Service class for user operations using Supabase"""
    
    def __init__(self, supabase_client):
        self.db = supabase_client
    
    async def create_user(self, user_data: UserCreate) -> Optional[Dict[str, Any]]:
        """Create a new user in the database"""
        try:
            # Check if user already exists
            existing_user = await self.get_user_by_clerk_id(user_data.clerk_id)
            if existing_user:
                return existing_user
            
            # Create new user using Supabase client
            user_dict = user_data.model_dump()
            result = await self.db.upsert_user(user_dict)
            
            if result:
                logger.info(f"✅ User created successfully: {result.get('clerk_id')}")
                return result
            else:
                logger.error("❌ Failed to create user")
                return None
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None
    
    async def get_user_by_clerk_id(self, clerk_id: str) -> Optional[Dict[str, Any]]:
        """Get user by Clerk ID"""
        try:
            user = await self.db.get_user_by_clerk_id(clerk_id)
            return user
        except Exception as e:
            logger.error(f"Error getting user by clerk_id: {e}")
            return None
    
    async def update_user(self, clerk_id: str, user_data: UserUpdate) -> Optional[Dict[str, Any]]:
        """Update user information"""
        try:
            # Get existing user first
            existing_user = await self.get_user_by_clerk_id(clerk_id)
            if not existing_user:
                logger.warning(f"User not found for update: {clerk_id}")
                return None
            
            # Update user data
            update_data = user_data.model_dump(exclude_unset=True)
            result = await self.db.upsert_user(update_data)
            
            if result:
                logger.info(f"✅ User updated successfully: {clerk_id}")
                return result
            else:
                logger.error("❌ Failed to update user")
                return None
                
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return None
    
    async def delete_user(self, clerk_id: str) -> bool:
        """Delete user (soft delete by setting is_active to False)"""
        try:
            update_data = {"is_active": False}
            result = await self.db.upsert_user({"clerk_id": clerk_id, **update_data})
            
            if result:
                logger.info(f"✅ User deactivated successfully: {clerk_id}")
                return True
            else:
                logger.error("❌ Failed to deactivate user")
                return False
                
        except Exception as e:
            logger.error(f"Error deactivating user: {e}")
            return False
    
    async def get_user_profile(self, clerk_id: str) -> Optional[Dict[str, Any]]:
        """Get complete user profile"""
        try:
            user = await self.get_user_by_clerk_id(clerk_id)
            if user and user.get("is_active", True):
                return user
            return None
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return None
    
    async def sync_user_from_clerk(self, clerk_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Sync user data from Clerk authentication"""
        try:
            # Prepare user data for Supabase
            user_data = {
                "clerk_id": clerk_data.get("id"),
                "email": clerk_data.get("email"),
                "first_name": clerk_data.get("first_name"),
                "last_name": clerk_data.get("last_name"),
                "profile_image_url": clerk_data.get("image_url"),
                "is_active": True
            }
            
            # Remove None values
            user_data = {k: v for k, v in user_data.items() if v is not None}
            
            # Use Supabase client to upsert user
            result = await self.db.upsert_user(user_data)
            
            if result:
                logger.info(f"✅ User synced successfully: {user_data.get('clerk_id')}")
                return result
            else:
                logger.error("❌ Failed to sync user data")
                return None
                
        except Exception as e:
            logger.error(f"Error syncing user from Clerk: {e}")
            return None
