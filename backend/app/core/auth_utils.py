"""
Authentication utilities for header-based user identification
"""

from fastapi import HTTPException, Header
from typing import Optional


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
    
    # Clerk user IDs typically start with 'user_' and contain alphanumeric characters
    if not user_id.startswith('user_'):
        return False
    
    if len(user_id) < 10:  # Minimum reasonable length
        return False
    
    return True
