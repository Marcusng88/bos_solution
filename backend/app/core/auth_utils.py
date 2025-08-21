"""
Authentication utilities for user identification and validation
"""

from fastapi import HTTPException, Header, Depends
from typing import Optional
from app.core.database import get_db
import logging

logger = logging.getLogger(__name__)

async def get_user_id_from_header(
    x_user_id: str = Header(..., alias="X-User-ID")
) -> str:
    """
    Extract user ID from X-User-ID header.
    
    This function validates that the user ID header is present and not empty.
    The actual authentication is handled by Clerk on the frontend.
    
    Args:
        x_user_id: User ID from X-User-ID header
        
    Returns:
        User ID string
        
    Raises:
        HTTPException: If user ID is missing or invalid
    """
    if not x_user_id or x_user_id.strip() == "":
        raise HTTPException(
            status_code=401,
            detail="X-User-ID header is required"
        )
    
    return x_user_id.strip()


async def get_db_user_id(clerk_user_id: str, db) -> str:
    """
    Get database user ID from Clerk user ID.
    
    This function retrieves the database user ID for a given Clerk user ID.
    Since we're now using Supabase directly, this function is simplified.
    
    Args:
        clerk_user_id: Clerk user ID
        db: Database client (Supabase client)
        
    Returns:
        Database user ID string
        
    Raises:
        HTTPException: If user not found or database error
    """
    try:
        user = await db.get_user_by_clerk_id(clerk_user_id)
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found in database"
            )
        
        return str(user.get("id", clerk_user_id))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting database user ID: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )


async def get_current_user(
    user_id: str = Depends(get_user_id_from_header),
    db = Depends(get_db)
) -> dict:
    """
    Get current authenticated user from database.
    
    This function can be used as a dependency to ensure the user exists
    in the database and is authenticated.
    
    Args:
        user_id: User ID from header
        db: Database client (Supabase client)
        
    Returns:
        User object from database
        
    Raises:
        HTTPException: If user not found or not authenticated
    """
    try:
        # Get user directly from database
        user = await db.get_user_by_clerk_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found in database"
            )
        
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=401,
                detail="User account is deactivated"
            )
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get user information"
        )


def validate_user_permission(user_id: str, resource_user_id: str) -> bool:
    """
    Validate that a user has permission to access a resource.
    
    Args:
        user_id: ID of the authenticated user
        resource_user_id: ID of the user who owns the resource
        
    Returns:
        True if user has permission, False otherwise
    """
    return user_id == resource_user_id


async def require_user_permission(
    user_id: str = Depends(get_user_id_from_header),
    resource_user_id: str = None
) -> str:
    """
    Dependency that requires user permission to access a resource.
    
    Args:
        user_id: ID of the authenticated user
        resource_user_id: ID of the user who owns the resource
        
    Returns:
        User ID if permission granted
        
    Raises:
        HTTPException: If permission denied
    """
    if resource_user_id and not validate_user_permission(user_id, resource_user_id):
        raise HTTPException(
            status_code=403,
            detail="Access denied - insufficient permissions"
        )
    
    return user_id
