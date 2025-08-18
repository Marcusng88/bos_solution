"""
Users endpoints for managing user settings and preferences
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.auth_utils import get_user_id_from_header, get_db_user_id
from app.models.user_settings import UserMonitoringSettings
from app.schemas.user_settings import UserMonitoringSettingsResponse, UserMonitoringSettingsUpdate

router = APIRouter()


@router.get("/settings", response_model=UserMonitoringSettingsResponse)
async def get_user_settings(
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Get user monitoring settings"""
    try:
        # Convert Clerk user ID to database UUID
        db_user_id = await get_db_user_id(user_id, db)
        
        result = await db.execute(
            select(UserMonitoringSettings).where(UserMonitoringSettings.user_id == db_user_id)
        )
        
        settings = result.scalar_one_or_none()
        if not settings:
            # Create default settings if none exist
            settings = UserMonitoringSettings(user_id=db_user_id)
            db.add(settings)
            await db.commit()
            await db.refresh(settings)
        
        return UserMonitoringSettingsResponse.model_validate(settings)
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user settings"
        )


@router.put("/settings", response_model=UserMonitoringSettingsResponse)
async def update_user_settings(
    settings_data: UserMonitoringSettingsUpdate,
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Update user monitoring settings"""
    try:
        # Convert Clerk user ID to database UUID
        db_user_id = await get_db_user_id(user_id, db)
        
        result = await db.execute(
            select(UserMonitoringSettings).where(UserMonitoringSettings.user_id == db_user_id)
        )
        
        settings = result.scalar_one_or_none()
        if not settings:
            # Create settings if none exist
            settings = UserMonitoringSettings(user_id=db_user_id)
            db.add(settings)
        
        # Update fields
        update_data = settings_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(settings, field, value)
        
        await db.commit()
        await db.refresh(settings)
        return UserMonitoringSettingsResponse.model_validate(settings)
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user settings"
        )
