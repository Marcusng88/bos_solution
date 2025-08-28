"""
Users endpoints for managing users and user settings
"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.core.database import get_db
from app.core.auth_utils import get_user_id_from_header
from app.schemas.user import UserResponse, ClerkUserData
from app.schemas.user_settings import UserMonitoringSettingsResponse, UserMonitoringSettingsUpdate
from app.core.supabase_client import SupabaseClient
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/sync", response_model=dict)
async def sync_user_from_clerk(
    clerk_data: ClerkUserData,
    db: SupabaseClient = Depends(get_db)
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
        result = await db.upsert_user(user_data)
        
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
        logger.error(f"Error syncing user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync user data: {str(e)}"
        )


@router.get("/profile")
async def get_user_profile(
    user_id: str = Depends(get_user_id_from_header),
    db: SupabaseClient = Depends(get_db)
):
    """Get user profile information"""
    try:
        user = await db.get_user_by_clerk_id(user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse.model_validate(user)
        
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get user profile: {str(e)}")


@router.get("/settings")
async def get_user_monitoring_settings(
    user_id: str = Depends(get_user_id_from_header),
    db: SupabaseClient = Depends(get_db)
):
    """Get user monitoring settings"""
    try:
        settings = await db.get_user_monitoring_settings(user_id)
        
        if not settings:
            # Return default settings if none exist
            return UserMonitoringSettingsResponse(
                user_id=user_id,
                global_monitoring_enabled=True,
                default_scan_frequency_minutes=1440,
                alert_preferences={
                    "email_alerts": True,
                    "push_notifications": True,
                    "new_posts": True,
                    "content_changes": True,
                    "engagement_spikes": True,
                    "sentiment_changes": True
                },
                notification_schedule={
                    "quiet_hours_start": "22:00",
                    "quiet_hours_end": "08:00",
                    "timezone": "UTC"
                }
            )
        
        return UserMonitoringSettingsResponse.model_validate(settings)
        
    except Exception as e:
        logger.error(f"Error getting user settings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get user settings: {str(e)}")


@router.put("/settings")
async def update_user_monitoring_settings(
    settings_update: UserMonitoringSettingsUpdate,
    user_id: str = Depends(get_user_id_from_header),
    db: SupabaseClient = Depends(get_db)
):
    """Update user monitoring settings"""
    try:
        settings_data = settings_update.model_dump()
        settings_data["user_id"] = user_id
        
        result = await db.upsert_user_monitoring_settings(settings_data)
        
        if result:
            return UserMonitoringSettingsResponse.model_validate(result)
        else:
            raise HTTPException(status_code=500, detail="Failed to update user settings")
            
    except Exception as e:
        logger.error(f"Error updating user settings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update user settings: {str(e)}")


@router.get("/preferences")
async def get_user_preferences(
    user_id: str = Depends(get_user_id_from_header),
    db: SupabaseClient = Depends(get_db)
):
    """Get user preferences"""
    try:
        preferences = await db.get_user_preferences(user_id)
        
        if not preferences:
            raise HTTPException(status_code=404, detail="User preferences not found")
        
        return preferences
        
    except Exception as e:
        logger.error(f"Error getting user preferences: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get user preferences: {str(e)}")


@router.put("/preferences")
async def update_user_preferences(
    preferences_data: dict,
    user_id: str = Depends(get_user_id_from_header),
    db: SupabaseClient = Depends(get_db)
):
    """Update user preferences"""
    try:
        preferences_data["user_id"] = user_id
        
        result = await db.upsert_user_preferences(preferences_data)
        
        if result:
            return result
        else:
            raise HTTPException(status_code=500, detail="Failed to update user preferences")
            
    except Exception as e:
        logger.error(f"Error updating user preferences: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update user preferences: {str(e)}")


@router.get("/{user_id}/onboarding-status")
async def get_user_onboarding_status(
    user_id: str,
    db: SupabaseClient = Depends(get_db)
):
    """Get user onboarding completion status"""
    try:
        # Check if user exists
        user = await db.get_user_by_clerk_id(user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if user has completed onboarding by looking for user preferences
        preferences = await db.get_user_preferences(user_id)
        
        # Check if user has competitors (another indicator of onboarding completion)
        competitors = await db.get_competitors_by_user(user_id)
        
        # Consider onboarding complete if user has:
        # 1. User preferences (industry, goals, etc.)
        # 2. OR has set up competitors
        # 3. OR has monitoring settings
        has_preferences = bool(preferences and preferences.get("industry") and preferences.get("marketing_goals"))
        has_competitors = bool(competitors and len(competitors) > 0)
        
        # Try to get monitoring settings as well
        try:
            monitoring_settings = await db.get_user_monitoring_settings(user_id)
            has_monitoring_settings = bool(monitoring_settings)
        except:
            has_monitoring_settings = False
        
        onboarding_complete = has_preferences or has_competitors or has_monitoring_settings
        
        return {
            "user_id": user_id,
            "onboarding_complete": onboarding_complete,
            "has_preferences": has_preferences,
            "has_competitors": has_competitors,
            "has_monitoring_settings": has_monitoring_settings,
            "preferences": preferences,
            "competitor_count": len(competitors) if competitors else 0
        }
        
    except Exception as e:
        logger.error(f"Error getting user onboarding status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get user onboarding status: {str(e)}")
