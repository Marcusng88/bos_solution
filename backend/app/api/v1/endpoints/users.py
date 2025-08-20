"""
Users endpoints for managing users and user settings
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.auth_utils import get_user_id_from_header
from app.models.user import User
from app.models.user_settings import UserMonitoringSettings
from app.schemas.user import UserCreate, UserResponse, ClerkUserData
from app.schemas.user_settings import UserSettingsResponse, UserSettingsUpdate

"""
Users endpoints for managing users and user settings
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.auth_utils import get_user_id_from_header
from app.core.supabase_client import supabase_client
from app.models.user import User
from app.models.user_settings import UserMonitoringSettings
from app.schemas.user import UserCreate, UserResponse, ClerkUserData
from app.schemas.user_settings import UserSettingsResponse, UserSettingsUpdate
import uuid

router = APIRouter()


@router.post("/sync", response_model=dict)
async def sync_user_from_clerk(
    clerk_data: ClerkUserData,
    db: AsyncSession = Depends(get_db)
):
    """
    Create or update user from Clerk authentication data
    This endpoint should be called after successful Clerk authentication
    """
    try:
        primary_email = clerk_data.get_primary_email()
        
        # Prepare user data for Supabase
        user_data = {
            "clerk_id": clerk_data.id,
            "email": primary_email,
            "first_name": clerk_data.first_name,
            "last_name": clerk_data.last_name,
            "profile_image_url": clerk_data.image_url,
            "is_active": True
        }
        
        # Use Supabase REST API to create/update user
        result = await supabase_client.upsert_user(user_data)
        
        if result:
            return {
                "success": True,
                "message": "User synced successfully",
                "user": result
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to sync user data to Supabase"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync user data: {str(e)}"
        )


@router.get("/profile")
async def get_user_profile(
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Get current user profile"""
    try:
        # Try to get user from Supabase first
        user_data = await supabase_client.get_user_by_clerk_id(user_id)
        
        if user_data:
            return user_data
        
        # Fallback to local database if Supabase fails
        result = await db.execute(
            select(User).where(User.clerk_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "id": str(user.id),
            "clerk_id": user.clerk_id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "profile_image_url": user.profile_image_url,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user profile"
        )


@router.get("/settings", response_model=UserSettingsResponse)
async def get_user_settings(
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Get user monitoring settings"""
    try:
        result = await db.execute(
            select(UserMonitoringSettings).where(UserMonitoringSettings.user_id == user_id)
        )
        
        settings = result.scalar_one_or_none()
        if not settings:
            # Create default settings if none exist
            settings = UserMonitoringSettings(user_id=user_id)
            db.add(settings)
            await db.commit()
            await db.refresh(settings)
        
        return settings
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user settings"
        )


@router.put("/settings", response_model=UserSettingsResponse)
async def update_user_settings(
    settings_data: UserSettingsUpdate,
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Update user monitoring settings"""
    try:
        result = await db.execute(
            select(UserMonitoringSettings).where(UserMonitoringSettings.user_id == user_id)
        )
        
        settings = result.scalar_one_or_none()
        if not settings:
            # Create settings if none exist
            settings = UserMonitoringSettings(user_id=user_id)
            db.add(settings)
        
        # Update fields
        for field, value in settings_data.dict(exclude_unset=True).items():
            setattr(settings, field, value)
        
        await db.commit()
        await db.refresh(settings)
        return settings
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user settings"
        )
