from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.core.supabase_client import supabase_client
from app.schemas.user_preferences import UserPreferencesCreate, UserPreferencesUpdate, UserPreferences as UserPreferencesSchema
from app.core.auth_utils import get_user_id_from_header
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

async def check_and_update_onboarding_completion(user_id: str):
    """Check if user has completed onboarding and update the database flag"""
    try:
        # Get user preferences and competitors
        preferences = await supabase_client.get_user_preferences(user_id)
        competitors = await supabase_client.get_competitors_by_user(user_id)
        
        # Check if onboarding is complete
        has_valid_preferences = bool(
            preferences and 
            preferences.get("industry") and 
            preferences.get("marketing_goals") and
            len(preferences.get("marketing_goals", [])) > 0 and
            preferences.get("company_size")
        )
        
        has_competitors = bool(competitors and len(competitors) > 0)
        onboarding_complete = has_valid_preferences and has_competitors
        
        # Update the user's onboarding_complete status in database
        if onboarding_complete:
            logger.info(f"Marking onboarding as complete for user {user_id}")
            await supabase_client.upsert_user({
                "clerk_id": user_id,
                "onboarding_complete": True
            })
        
    except Exception as e:
        logger.error(f"Error checking onboarding completion for {user_id}: {e}")
        # Don't raise exception as this is a secondary operation

@router.post("/", response_model=UserPreferencesSchema)
async def create_user_preferences(
    preferences: UserPreferencesCreate,
    user_id: str = Depends(get_user_id_from_header)
):
    """Create or update user preferences"""
    try:
        # First, ensure the user exists in the users table
        user = await supabase_client.get_user_by_clerk_id(user_id)
        if not user:
            # User doesn't exist, this shouldn't happen if user sync was called properly
            # But we'll create a minimal user record to prevent foreign key violations
            minimal_user_data = {
                "clerk_id": user_id,
                "email": f"user_{user_id}@temp.com",  # Temporary email
                "is_active": True
            }
            user_result = await supabase_client.upsert_user(minimal_user_data)
            if not user_result or not user_result.get("success"):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create user record before saving preferences"
                )
        
        # Transform frontend values to match database constraints
        def transform_budget(budget: str) -> str:
            """Transform frontend budget values to database constraint values and ensure validity"""
            allowed_budgets = {
                "$0 - $1,000",
                "$1,000 - $5,000",
                "$5,000 - $10,000",
                "$10,000 - $25,000",
                "$25,000+",
            }
            budget_mapping = {
                # Frontend values from goals-step.tsx
                "under-500": "$0 - $1,000",
                "500-1000": "$0 - $1,000",  # Map to closest valid constraint
                "1000-5000": "$1,000 - $5,000", 
                "5000-10000": "$5,000 - $10,000",
                "10000-25000": "$10,000 - $25,000",
                "over-25000": "$25,000+",
                
                # Alternative formats (for backward compatibility)
                "0-1000": "$0 - $1,000",
                "25000+": "$25,000+",
                "25000-plus": "$25,000+",
                "": "$0 - $1,000",  # Safeguard for empty string
                None: "$0 - $1,000",  # type: ignore
            }
            # Normalize and map
            normalized = (budget or "").strip()
            transformed = budget_mapping.get(normalized, normalized)
            # Final safeguard: default to lowest tier if still invalid
            if transformed not in allowed_budgets:
                print(f"Budget transformed (fallback): '{budget}' -> '$0 - $1,000'")
                transformed = "$0 - $1,000"
            # Log transformation for debugging
            if budget != transformed:
                print(f"Budget transformed: '{budget}' -> '{transformed}'")
            return transformed
        
        def transform_company_size(size: str) -> str:
            """Transform frontend company size values to database constraint values"""
            size_mapping = {
                "solo": "1-10",
                "small": "1-10", 
                "medium": "11-50",
                "large": "51-200",
                "enterprise": "500+"
            }
            return size_mapping.get(size, size)
        
        # Prepare data for Supabase with transformed values and all required fields
        preference_data = {
            "user_id": user_id,
            "industry": preferences.industry,
            "company_size": transform_company_size(preferences.company_size),
            "marketing_goals": preferences.marketing_goals,
            "monthly_budget": transform_budget(preferences.monthly_budget),
            # id, created_at, updated_at will be auto-generated by Supabase
        }
        
        # Use Supabase REST API instead of direct database connection
        result = await supabase_client.upsert_user_preferences(preference_data)
        
        if result:
            # Check if onboarding should be marked as complete
            await check_and_update_onboarding_completion(user_id)
            # Return the created/updated preferences data
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save user preferences via Supabase API"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save user preferences: {str(e)}"
        )

@router.get("/", response_model=UserPreferencesSchema)
async def get_user_preferences(
    user_id: str = Depends(get_user_id_from_header)
):
    """Get user preferences"""
    try:
        # Use Supabase REST API instead of direct database connection
        result = await supabase_client.get_user_preferences(user_id)
        
        if result:
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User preferences not found"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user preferences: {str(e)}"
        )

@router.put("/", response_model=UserPreferencesSchema)
async def update_user_preferences(
    preferences: UserPreferencesUpdate,
    user_id: str = Depends(get_user_id_from_header)
):
    """Update user preferences"""
    try:
        # Transform frontend values to match database constraints
        def transform_budget(budget: str) -> str:
            """Transform frontend budget values to database constraint values and ensure validity"""
            allowed_budgets = {
                "$0 - $1,000",
                "$1,000 - $5,000",
                "$5,000 - $10,000",
                "$10,000 - $25,000",
                "$25,000+",
            }
            budget_mapping = {
                # Frontend values from goals-step.tsx
                "under-500": "$0 - $1,000",
                "500-1000": "$0 - $1,000",
                "1000-5000": "$1,000 - $5,000", 
                "5000-10000": "$5,000 - $10,000",
                "10000-25000": "$10,000 - $25,000",
                "over-25000": "$25,000+",
                
                # Alternative formats (for backward compatibility)
                "0-1000": "$0 - $1,000",
                "25000+": "$25,000+",
                "25000-plus": "$25,000+",
                "": "$0 - $1,000",
                None: "$0 - $1,000",  # type: ignore
            }
            normalized = (budget or "").strip()
            transformed = budget_mapping.get(normalized, normalized)
            if transformed not in allowed_budgets:
                print(f"Budget transformed (fallback): '{budget}' -> '$0 - $1,000'")
                transformed = "$0 - $1,000"
            if budget != transformed:
                print(f"Budget transformed: '{budget}' -> '{transformed}'")
            return transformed
        
        def transform_company_size(size: str) -> str:
            """Transform frontend company size values to database constraint values"""
            size_mapping = {
                "solo": "1-10",
                "small": "1-10", 
                "medium": "11-50",
                "large": "51-200",
                "enterprise": "500+"
            }
            return size_mapping.get(size, size)
        
        # Prepare data for Supabase with transformed values and all required fields
        preference_data = {
            "user_id": user_id,
            "industry": preferences.industry,
            "company_size": transform_company_size(preferences.company_size),
            "marketing_goals": preferences.marketing_goals,
            "monthly_budget": transform_budget(preferences.monthly_budget),
            # id, created_at, updated_at will be auto-generated by Supabase
        }
        
        # Use Supabase REST API instead of direct database connection
        result = await supabase_client.upsert_user_preferences(preference_data)
        
        if result:
            # Check if onboarding should be marked as complete
            await check_and_update_onboarding_completion(user_id)
            # Return the updated preferences data
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user preferences"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user preferences: {str(e)}"
        )
