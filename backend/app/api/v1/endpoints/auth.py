"""
Authentication endpoints for user verification and management
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional
from app.core.database import get_db
from app.core.auth_utils import get_user_id_from_header
from app.schemas.user import UserResponse
from app.core.supabase_client import SupabaseClient
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/verify")
async def verify_user(user_id: str = Depends(get_user_id_from_header)):
    """Verify user authentication"""
    return {"user_id": user_id, "authenticated": True}


@router.get("/me")
async def get_current_user(
    user_id: str = Depends(get_user_id_from_header),
    db: SupabaseClient = Depends(get_db)
):
    """Get current user information from database"""
    try:
        user = await db.get_user_by_clerk_id(user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse.model_validate(user)
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/check-user-status")
async def check_user_status(
    user_id: str = Header(..., alias="X-User-ID"),
    db: SupabaseClient = Depends(get_db)
):
    """Check if user exists and determine redirect path with robust validation"""
    try:
        # Check if user exists in Supabase
        user = await db.get_user_by_clerk_id(user_id)
        
        if user:
            # User exists - check if they have completed onboarding
            # Get all required data for comprehensive validation
            logger.info(f"🔍 Checking onboarding status for user {user_id}")
            
            preferences = await db.get_user_preferences(user_id)
            logger.info(f"📋 User preferences: {preferences}")
            
            competitors = await db.get_competitors_by_user(user_id)
            logger.info(f"🏢 User competitors: {competitors}")
            
            # Try to get monitoring settings as well
            try:
                monitoring_settings = await db.get_user_monitoring_settings(user_id)
                has_monitoring_settings = bool(monitoring_settings)
                logger.info(f"📊 User monitoring settings: {monitoring_settings}")
            except Exception as e:
                logger.warning(f"⚠️ Could not get monitoring settings: {e}")
                has_monitoring_settings = False
            
            # More robust validation criteria
            has_valid_preferences = bool(
                preferences and 
                preferences.get("industry") and 
                preferences.get("marketing_goals") and
                len(preferences.get("marketing_goals", [])) > 0 and
                preferences.get("company_size")
            )
            
            has_competitors = bool(competitors and len(competitors) > 0)
            
            logger.info(f"✅ Validation results: has_valid_preferences={has_valid_preferences}, has_competitors={has_competitors}")
            
            # Require BOTH preferences AND at least one competitor for completion
            # This ensures user has gone through the full onboarding flow
            onboarding_complete = has_valid_preferences and has_competitors
            
            logger.info(f"🎯 Final onboarding_complete status: {onboarding_complete}")
            
            # Additional validation: check if user has actually completed the onboarding steps
            # by looking for specific data patterns that indicate completion
            if onboarding_complete:
                # Double-check that the data is meaningful (not just empty records)
                industry = preferences.get("industry", "").strip()
                goals = preferences.get("marketing_goals", [])
                valid_goals = [goal for goal in goals if goal and goal.strip()]
                
                # Ensure we have meaningful data
                if not industry or len(valid_goals) == 0:
                    onboarding_complete = False
                    logger.warning(f"User {user_id} has incomplete preferences data")
                    logger.info(f"📝 Industry: '{industry}', Valid goals: {valid_goals}")
            
            logger.info(f"🏁 Final onboarding status after validation: {onboarding_complete}")
            
            if onboarding_complete:
                # User has completed onboarding - they can go to dashboard
                response_data = {
                    "exists": True,
                    "redirect_to": "dashboard",
                    "user": user,
                    "onboarding_complete": True,
                    "has_preferences": has_valid_preferences,
                    "has_competitors": has_competitors,
                    "has_monitoring_settings": has_monitoring_settings,
                    "preferences": preferences,  # Include actual preferences data
                    "competitors": competitors,  # Include actual competitors data
                    "message": "User found and onboarding completed, redirecting to dashboard"
                }
                logger.info(f"📤 Sending completed response: {response_data}")
                return response_data
            else:
                # User exists but hasn't completed onboarding
                response_data = {
                    "exists": True,
                    "redirect_to": "onboarding",
                    "user": user,
                    "onboarding_complete": False,
                    "has_preferences": has_valid_preferences,
                    "has_competitors": has_competitors,
                    "has_monitoring_settings": has_monitoring_settings,
                    "preferences": preferences,  # Include actual preferences data
                    "competitors": competitors,  # Include actual competitors data
                    "message": "User found but onboarding incomplete, redirecting to onboarding"
                }
                logger.info(f"📤 Sending incomplete response: {response_data}")
                return response_data
        else:
            # User doesn't exist - they need to go through onboarding
            return {
                "exists": False,
                "redirect_to": "onboarding",
                "user": None,
                "onboarding_complete": False,
                "message": "New user, redirecting to onboarding"
            }
            
    except Exception as e:
        logger.error(f"Error checking user status: {e}")
        # Return safe default that won't cause infinite loops
        return {
            "exists": False,
            "redirect_to": "onboarding",
            "user": None,
            "onboarding_complete": False,
            "error": str(e),
            "message": "Error checking user status, defaulting to onboarding"
        }


@router.post("/sync")
async def sync_user_with_clerk(
    db: SupabaseClient = Depends(get_db),
    user_id: str = Header(..., alias="X-User-ID"),
    email: Optional[str] = Header(None, alias="X-User-Email"),
    first_name: Optional[str] = Header(None, alias="X-User-First-Name"),
    last_name: Optional[str] = Header(None, alias="X-User-Last-Name"),
    profile_image_url: Optional[str] = Header(None, alias="X-User-Profile-Image")
):
    """Sync user data from Clerk authentication"""
    try:
        user_data = {
            "clerk_id": user_id,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "profile_image_url": profile_image_url,
            "is_active": True
        }
        
        # Remove None values
        user_data = {k: v for k, v in user_data.items() if v is not None}
        
        result = await db.upsert_user(user_data)
        
        if result:
            return {
                "success": True,
                "message": "User synced successfully",
                "user": result
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to sync user data")
            
    except Exception as e:
        logger.error(f"Error syncing user: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to sync user data: {str(e)}")
