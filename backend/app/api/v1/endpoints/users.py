"""
Users endpoints for managing user settings and preferences
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.auth_utils import get_user_id_from_header
from app.models.user_settings import UserMonitoringSettings
from app.schemas.user_settings import UserSettingsResponse, UserSettingsUpdate

router = APIRouter()


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
