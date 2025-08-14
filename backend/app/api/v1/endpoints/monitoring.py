"""
Monitoring endpoints for continuous monitoring and alerts
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.auth_utils import get_user_id_from_header
from app.models.user_settings import UserMonitoringSettings
from app.models.monitoring import MonitoringAlert
from app.schemas.monitoring import (
    UserMonitoringSettingsCreate, UserMonitoringSettingsResponse, UserMonitoringSettingsUpdate,
    MonitoringAlertCreate, MonitoringAlertResponse
)

router = APIRouter()


@router.get("/settings", response_model=UserMonitoringSettingsResponse)
async def get_user_monitoring_settings(
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
            detail="Failed to fetch monitoring settings"
        )


@router.post("/settings", response_model=UserMonitoringSettingsResponse)
async def create_user_monitoring_settings(
    settings_data: UserMonitoringSettingsCreate,
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Create or update user monitoring settings"""
    try:
        # Check if settings already exist
        result = await db.execute(
            select(UserMonitoringSettings).where(UserMonitoringSettings.user_id == user_id)
        )
        existing_settings = result.scalar_one_or_none()
        
        if existing_settings:
            # Update existing settings
            for field, value in settings_data.dict(exclude_unset=True).items():
                setattr(existing_settings, field, value)
            await db.commit()
            await db.refresh(existing_settings)
            return existing_settings
        else:
            # Create new settings
            settings = UserMonitoringSettings(
                user_id=user_id,
                **settings_data.dict(exclude={'user_id'})
            )
            db.add(settings)
            await db.commit()
            await db.refresh(settings)
            return settings
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create/update monitoring settings"
        )


@router.put("/settings", response_model=UserMonitoringSettingsResponse)
async def update_user_monitoring_settings(
    settings_data: UserMonitoringSettingsUpdate,
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
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Monitoring settings not found"
            )
        
        # Update fields
        for field, value in settings_data.dict(exclude_unset=True).items():
            setattr(settings, field, value)
        
        await db.commit()
        await db.refresh(settings)
        return settings
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update monitoring settings"
        )


# Monitoring Alerts endpoints
@router.get("/alerts", response_model=list[MonitoringAlertResponse])
async def get_monitoring_alerts(
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Get all monitoring alerts for a user"""
    try:
        result = await db.execute(
            select(MonitoringAlert).where(MonitoringAlert.user_id == user_id)
        )
        alerts = result.scalars().all()
        return alerts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch monitoring alerts"
        )


@router.post("/alerts", response_model=MonitoringAlertResponse)
async def create_monitoring_alert(
    alert_data: MonitoringAlertCreate,
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Create a new monitoring alert"""
    try:
        alert = MonitoringAlert(
            user_id=user_id,
            **alert_data.dict()
        )
        db.add(alert)
        await db.commit()
        await db.refresh(alert)
        return alert
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create monitoring alert"
        )


@router.put("/alerts/{alert_id}/read")
async def mark_alert_as_read(
    alert_id: str,
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Mark a monitoring alert as read"""
    try:
        result = await db.execute(
            select(MonitoringAlert).where(
                MonitoringAlert.id == alert_id,
                MonitoringAlert.user_id == user_id
            )
        )
        alert = result.scalar_one_or_none()
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Monitoring alert not found"
            )
        
        alert.is_read = True
        await db.commit()
        return {"message": "Alert marked as read"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark alert as read"
        )
