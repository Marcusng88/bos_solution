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
    """Check if user exists and determine redirect path"""
    try:
        # Check if user exists in Supabase
        user = await db.get_user_by_clerk_id(user_id)
        
        if user:
            # User exists - check if they have completed onboarding
            # You can add additional checks here for onboarding completion
            # For now, if user exists, they can go to dashboard
            return {
                "exists": True,
                "redirect_to": "dashboard",
                "user": user,
                "message": "User found, redirecting to dashboard"
            }
        else:
            # User doesn't exist - they need to go through onboarding
            return {
                "exists": False,
                "redirect_to": "onboarding",
                "user": None,
                "message": "New user, redirecting to onboarding"
            }
            
    except Exception as e:
        logger.error(f"Error checking user status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to check user status: {str(e)}")


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
