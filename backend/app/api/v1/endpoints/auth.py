"""
Authentication endpoints for user management
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional
from app.core.auth_utils import get_user_id_from_header
from app.core.database import get_db
from app.models.user_settings import User
from app.schemas.user_settings import UserCreate, UserUpdate, UserResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("/verify")
async def verify_user(user_id: str = Depends(get_user_id_from_header)):
    """Verify user ID from header"""
    return {"user_id": user_id, "authenticated": True}


@router.get("/me")
async def get_current_user(
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Get current user information from database"""
    try:
        result = await db.execute(
            select(User).where(User.clerk_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse.model_validate(user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/sync")
async def sync_user_with_clerk(
    db: AsyncSession = Depends(get_db),
    user_id: str = Header(..., alias="X-User-ID"),
    email: Optional[str] = Header(None, alias="X-User-Email"),
    first_name: Optional[str] = Header(None, alias="X-User-First-Name"),
    last_name: Optional[str] = Header(None, alias="X-User-Last-Name"),
    profile_image_url: Optional[str] = Header(None, alias="X-User-Profile-Image")
):
    """
    Synchronize user data from Clerk with local database.
    This endpoint should be called after successful Clerk authentication.
    """
    try:
        # Check if user already exists
        result = await db.execute(
            select(User).where(User.clerk_id == user_id)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            # Update existing user
            if email and email != existing_user.email:
                existing_user.email = email
            if first_name and first_name != existing_user.first_name:
                existing_user.first_name = first_name
            if last_name and last_name != existing_user.last_name:
                existing_user.last_name = last_name
            if profile_image_url and profile_image_url != existing_user.profile_image_url:
                existing_user.profile_image_url = profile_image_url
            
            await db.commit()
            await db.refresh(existing_user)
            user = existing_user
        else:
            # Create new user
            new_user = User(
                clerk_id=user_id,
                email=email,
                first_name=first_name,
                last_name=last_name,
                profile_image_url=profile_image_url
            )
            
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            user = new_user
        
        return {
            "message": "User synchronized successfully",
            "user": UserResponse.model_validate(user)
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error synchronizing user: {str(e)}")


@router.put("/profile")
async def update_user_profile(
    user_data: UserUpdate,
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Update user profile information"""
    try:
        result = await db.execute(
            select(User).where(User.clerk_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update only provided fields
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await db.commit()
        await db.refresh(user)
        
        return UserResponse.model_validate(user)
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")


@router.delete("/deactivate")
async def deactivate_user(
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Deactivate user account"""
    try:
        result = await db.execute(
            select(User).where(User.clerk_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.is_active = False
        await db.commit()
        
        return {"message": "User deactivated successfully"}
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deactivating user: {str(e)}")
