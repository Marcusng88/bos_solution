"""
Authentication endpoints for user management
"""

from fastapi import APIRouter, Depends
from app.core.auth_utils import get_user_id_from_header

router = APIRouter()


@router.get("/verify")
async def verify_user(user_id: str = Depends(get_user_id_from_header)):
    """Verify user ID from header"""
    return {"user_id": user_id, "authenticated": True}


@router.get("/me")
async def get_current_user(user_id: str = Depends(get_user_id_from_header)):
    """Get current user information from database"""
    # This will be implemented to fetch user data from Supabase
    # For now, return basic user info
    return {
        "id": user_id,
        "authenticated": True
    }
