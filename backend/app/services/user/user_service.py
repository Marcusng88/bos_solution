"""
User service for managing user operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from typing import Optional
from app.models.user_settings import User, UserMonitoringSettings
from app.schemas.user_settings import UserCreate, UserUpdate, UserResponse
from app.core.database import get_db


class UserService:
    """Service class for user operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_user(self, user_data: UserCreate) -> Optional[User]:
        """Create a new user in the database"""
        try:
            # Check if user already exists
            existing_user = await self.get_user_by_clerk_id(user_data.clerk_id)
            if existing_user:
                return existing_user
            
            # Create new user
            db_user = User(
                clerk_id=user_data.clerk_id,
                email=user_data.email,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                profile_image_url=user_data.profile_image_url
            )
            
            self.db.add(db_user)
            await self.db.commit()
            await self.db.refresh(db_user)
            
            return db_user
            
        except IntegrityError as e:
            await self.db.rollback()
            # Log the error (you might want to add proper logging)
            print(f"Error creating user: {e}")
            return None
        except Exception as e:
            await self.db.rollback()
            print(f"Unexpected error creating user: {e}")
            return None
    
    async def get_user_by_clerk_id(self, clerk_id: str) -> Optional[User]:
        """Get user by Clerk ID"""
        result = await self.db.execute(
            select(User).where(User.clerk_id == clerk_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by database ID"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def update_user(self, clerk_id: str, user_data: UserUpdate) -> Optional[User]:
        """Update user information"""
        try:
            user = await self.get_user_by_clerk_id(clerk_id)
            if not user:
                return None
            
            # Update only provided fields
            update_data = user_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(user, field, value)
            
            await self.db.commit()
            await self.db.refresh(user)
            return user
            
        except Exception as e:
            await self.db.rollback()
            print(f"Error updating user: {e}")
            return None
    
    async def deactivate_user(self, clerk_id: str) -> bool:
        """Deactivate a user"""
        try:
            user = await self.get_user_by_clerk_id(clerk_id)
            if not user:
                return False
            
            user.is_active = False
            await self.db.commit()
            return True
            
        except Exception as e:
            await self.db.rollback()
            print(f"Error deactivating user: {e}")
            return None
    
    async def get_or_create_user(self, clerk_id: str, email: str = None, 
                          first_name: str = None, last_name: str = None,
                          profile_image_url: str = None) -> Optional[User]:
        """Get existing user or create new one if doesn't exist"""
        user = await self.get_user_by_clerk_id(clerk_id)
        
        if user:
            # Update user info if new data is provided
            update_data = {}
            if email and email != user.email:
                update_data['email'] = email
            if first_name and first_name != user.first_name:
                update_data['first_name'] = first_name
            if last_name and last_name != user.last_name:
                update_data['last_name'] = last_name
            if profile_image_url and profile_image_url != user.profile_image_url:
                update_data['profile_image_url'] = profile_image_url
            
            if update_data:
                user = await self.update_user(clerk_id, UserUpdate(**update_data))
        else:
            # Create new user
            user_data = UserCreate(
                clerk_id=clerk_id,
                email=email,
                first_name=first_name,
                last_name=last_name,
                profile_image_url=profile_image_url
            )
            user = await self.create_user(user_data)
        
        return user


async def get_user_service() -> UserService:
    """Dependency to get user service"""
    async for db in get_db():
        return UserService(db)
