"""
Users endpoints for managing users and user settings
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db
from app.core.auth_utils import get_user_id_from_header
from app.core.supabase_client import supabase_client
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
        result = await db.execute(text("""
            SELECT id, clerk_id, email, first_name, last_name, profile_image_url, 
                   is_active, created_at, updated_at
            FROM users 
            WHERE clerk_id = :user_id
        """), {"user_id": user_id})
        
        user_row = result.first()
        
        if not user_row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "id": str(user_row[0]),
            "clerk_id": user_row[1],
            "email": user_row[2],
            "first_name": user_row[3],
            "last_name": user_row[4],
            "profile_image_url": user_row[5],
            "is_active": user_row[6],
            "created_at": user_row[7].isoformat() if user_row[7] else None,
            "updated_at": user_row[8].isoformat() if user_row[8] else None,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user profile"
        )


@router.get("/settings")
async def get_user_settings(
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Get user monitoring settings"""
    try:
        result = await db.execute(text("""
            SELECT user_id, email_alerts_enabled, sms_alerts_enabled, push_notifications_enabled,
                   alert_frequency_minutes, alert_threshold_percentage, auto_pause_enabled,
                   auto_pause_threshold, daily_budget_alerts, weekly_summary_emails,
                   competitor_alerts_enabled, performance_alerts_enabled,
                   monthly_budget, campaign_objectives, target_audience, preferred_platforms
            FROM user_monitoring_settings 
            WHERE user_id = :user_id
        """), {"user_id": user_id})
        
        settings_row = result.first()
        if not settings_row:
            # Create default settings if none exist
            await db.execute(text("""
                INSERT INTO user_monitoring_settings (user_id)
                VALUES (:user_id)
            """), {"user_id": user_id})
            await db.commit()
            
            # Return default settings
            return {
                "user_id": user_id,
                "email_alerts_enabled": True,
                "sms_alerts_enabled": False,
                "push_notifications_enabled": True,
                "alert_frequency_minutes": 60,
                "alert_threshold_percentage": 80.0,
                "auto_pause_enabled": False,
                "auto_pause_threshold": 95.0,
                "daily_budget_alerts": True,
                "weekly_summary_emails": True,
                "competitor_alerts_enabled": True,
                "performance_alerts_enabled": True,
                "monthly_budget": "$1,000 - $5,000",
                "campaign_objectives": [],
                "target_audience": "",
                "preferred_platforms": []
            }
        
        return {
            "user_id": settings_row[0],
            "email_alerts_enabled": settings_row[1],
            "sms_alerts_enabled": settings_row[2], 
            "push_notifications_enabled": settings_row[3],
            "alert_frequency_minutes": settings_row[4],
            "alert_threshold_percentage": float(settings_row[5]) if settings_row[5] else 80.0,
            "auto_pause_enabled": settings_row[6],
            "auto_pause_threshold": float(settings_row[7]) if settings_row[7] else 95.0,
            "daily_budget_alerts": settings_row[8],
            "weekly_summary_emails": settings_row[9],
            "competitor_alerts_enabled": settings_row[10],
            "performance_alerts_enabled": settings_row[11],
            "monthly_budget": settings_row[12],
            "campaign_objectives": settings_row[13] or [],
            "target_audience": settings_row[14] or "",
            "preferred_platforms": settings_row[15] or []
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user settings: {str(e)}"
        )


@router.put("/settings")
async def update_user_settings(
    settings_data: UserSettingsUpdate,
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Update user monitoring settings"""
    try:
        # Check if settings exist
        result = await db.execute(text("""
            SELECT user_id FROM user_monitoring_settings WHERE user_id = :user_id
        """), {"user_id": user_id})
        
        settings_exist = result.first()
        
        if not settings_exist:
            # Create settings if none exist
            await db.execute(text("""
                INSERT INTO user_monitoring_settings (user_id)
                VALUES (:user_id)
            """), {"user_id": user_id})
        
        # Build update query dynamically based on provided fields
        update_fields = []
        update_params = {"user_id": user_id}
        
        settings_dict = settings_data.dict(exclude_unset=True)
        for field, value in settings_dict.items():
            update_fields.append(f"{field} = :{field}")
            update_params[field] = value
        
        if update_fields:
            update_query = f"""
                UPDATE user_monitoring_settings 
                SET {', '.join(update_fields)}
                WHERE user_id = :user_id
            """
            await db.execute(text(update_query), update_params)
        
        await db.commit()
        
        # Return updated settings
        result = await db.execute(text("""
            SELECT user_id, email_alerts_enabled, sms_alerts_enabled, push_notifications_enabled,
                   alert_frequency_minutes, alert_threshold_percentage, auto_pause_enabled,
                   auto_pause_threshold, daily_budget_alerts, weekly_summary_emails,
                   competitor_alerts_enabled, performance_alerts_enabled,
                   monthly_budget, campaign_objectives, target_audience, preferred_platforms
            FROM user_monitoring_settings 
            WHERE user_id = :user_id
        """), {"user_id": user_id})
        
        settings_row = result.first()
        return {
            "user_id": settings_row[0],
            "email_alerts_enabled": settings_row[1],
            "sms_alerts_enabled": settings_row[2], 
            "push_notifications_enabled": settings_row[3],
            "alert_frequency_minutes": settings_row[4],
            "alert_threshold_percentage": float(settings_row[5]) if settings_row[5] else 80.0,
            "auto_pause_enabled": settings_row[6],
            "auto_pause_threshold": float(settings_row[7]) if settings_row[7] else 95.0,
            "daily_budget_alerts": settings_row[8],
            "weekly_summary_emails": settings_row[9],
            "competitor_alerts_enabled": settings_row[10],
            "performance_alerts_enabled": settings_row[11],
            "monthly_budget": settings_row[12],
            "campaign_objectives": settings_row[13] or [],
            "target_audience": settings_row[14] or "",
            "preferred_platforms": settings_row[15] or []
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user settings: {str(e)}"
        )
