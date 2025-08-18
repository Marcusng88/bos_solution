"""
Authentication utilities for header-based user identification
"""

from fastapi import HTTPException, Header, Depends
from typing import Optional
try:
    from app.services.user.user_service import UserService, get_user_service
except ImportError:
    # If user service import fails, we'll handle it in the functions
    UserService = None
    get_user_service = None
from app.models.user_settings import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
import logging

logger = logging.getLogger(__name__)


def get_user_id_from_header(user_id: Optional[str] = Header(None, alias="X-User-ID")) -> str:
    """
    Extract and validate user ID from request header.
    
    This function is used as a dependency in API endpoints to ensure
    all requests include a valid user ID for data isolation.
    
    Args:
        user_id: User ID from X-User-ID header
        
    Returns:
        The validated user ID
        
    Raises:
        HTTPException: If user ID header is missing or invalid
    """
    if not user_id:
        raise HTTPException(
            status_code=401, 
            detail="X-User-ID header is required for authentication"
        )
    
    if not user_id.strip():
        raise HTTPException(
            status_code=401,
            detail="X-User-ID header cannot be empty"
        )
    
    if not validate_user_id_format(user_id.strip()):
        raise HTTPException(
            status_code=401,
            detail="Invalid user ID format"
        )
    
    return user_id.strip()


def validate_user_id_format(user_id: str) -> bool:
    """
    Validate user ID format (basic validation).
    
    Args:
        user_id: User ID to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Basic validation - adjust based on your Clerk user ID format
    if not user_id:
        return False
    
    # During development, allow test user IDs
    if user_id.startswith('user_test'):
        return True
    
    # Clerk user IDs typically start with 'user_' and contain alphanumeric characters
    if not user_id.startswith('user_'):
        return False
    
    if len(user_id) < 10: # Minimum reasonable length
        return False
    
    return True


async def get_db_user_id(clerk_user_id: str, db: AsyncSession):
    """
    Get the database UUID for a given Clerk user ID.
    
    This function is essential for converting Clerk user IDs to database UUIDs
    when querying other tables that reference users. If the user doesn't exist,
    it will automatically create them.
    
    Args:
        clerk_user_id: Clerk user ID from header
        db: Database session
        
    Returns:
        Database UUID object
        
    Raises:
        HTTPException: If there's a database error
    """
    try:
        logger.info(f"Looking up user with Clerk ID: {clerk_user_id}")
        
        result = await db.execute(
            select(User.id).where(User.clerk_id == clerk_user_id)
        )
        db_user_id = result.scalar_one_or_none()
        
        if not db_user_id:
            # User doesn't exist, create them automatically
            logger.info(f"User not found in database, creating user for Clerk ID: {clerk_user_id}")
            
            # Create new user with minimal information
            new_user = User(
                clerk_id=clerk_user_id,
                email=None,  # Will be updated when user syncs
                first_name=None,
                last_name=None,
                profile_image_url=None
            )
            
            logger.info(f"Adding new user to database: {new_user}")
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            
            logger.info(f"Created new user with database ID: {new_user.id}")
            return new_user.id
        
        logger.info(f"Found existing user with database ID: {db_user_id}")
        # Return the UUID object directly, not as string
        return db_user_id
    except Exception as e:
        await db.rollback()
        logger.error(f"Database error in get_db_user_id: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )


async def get_current_user(
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current authenticated user from database.
    
    This function can be used as a dependency to ensure the user exists
    in the database and is authenticated.
    
    Args:
        user_id: User ID from header
        db: Database session
        
    Returns:
        User object from database
        
    Raises:
        HTTPException: If user not found or not authenticated
    """
    try:
        # Get user directly from database
        result = await db.execute(
            select(User).where(User.clerk_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found in database"
            )
        
        if not user.is_active:
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
