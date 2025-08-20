"""
Competitors endpoints for managing competitor intelligence
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.auth_utils import get_user_id_from_header
from app.core.supabase_client import supabase_client
from app.schemas.competitor import (
    CompetitorCreate, CompetitorResponse, CompetitorUpdate, CompetitorCreateFrontend, CompetitorUpdateFrontend
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=list[CompetitorResponse])
async def get_competitors(
    user_id: str = Depends(get_user_id_from_header)
):
    """Get all competitors for a user"""
    try:
        competitors_data = await supabase_client.get_user_competitors(user_id)
        
        # Transform the response to match CompetitorResponse schema
        competitors = []
        for comp_data in competitors_data:
            competitor = CompetitorResponse(
                id=comp_data.get("id"),
                user_id=user_id,
                name=comp_data.get("name"),
                description=comp_data.get("description"),
                website_url=comp_data.get("website_url"),
                platforms=comp_data.get("platforms", []),
                social_media_handles=comp_data.get("social_media_handles", {}),
                industry=comp_data.get("industry"),
                status=comp_data.get("status", "active"),
                scan_frequency_minutes=comp_data.get("scan_frequency_minutes", 60),
                created_at=comp_data.get("created_at"),
                updated_at=comp_data.get("updated_at"),
                last_scan_at=comp_data.get("last_scan_at")
            )
            competitors.append(competitor)
        
        return competitors
    except Exception as e:
        logger.error(f"Error fetching competitors: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch competitors"
        )


@router.post("/", response_model=CompetitorResponse, status_code=status.HTTP_201_CREATED)
async def create_competitor(
    competitor_data: CompetitorCreateFrontend,
    user_id: str = Depends(get_user_id_from_header)
):
    """Create a new competitor"""
    try:
        # Transform frontend data to match database schema
        data_dict = competitor_data.dict()
        
        # Ensure platforms field is handled correctly
        if 'platforms' in data_dict and data_dict['platforms'] is None:
            data_dict['platforms'] = []
        
        # Set default values for all missing columns to match database schema
        data_dict['status'] = 'active'
        data_dict['scan_frequency_minutes'] = 60
        data_dict['description'] = data_dict.get('description')  # Keep if provided, None if not
        data_dict['industry'] = data_dict.get('industry')        # Keep if provided, None if not
        data_dict['last_scan_at'] = None  # Will be set when scanning starts
        
        # Use Supabase client to create competitor
        result = await supabase_client.create_competitor(data_dict, user_id)
        
        if result.get("success"):
            # Prefer returned inserted row; if missing, fetch by (user_id, name)
            created = result.get("data") or await supabase_client.get_competitor_by_user_and_name(user_id, data_dict.get("name"))
            if not created:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Competitor created but could not retrieve created record"
                )
            return CompetitorResponse(
                id=created.get("id"),
                user_id=user_id,
                name=created.get("name"),
                description=created.get("description"),
                website_url=created.get("website_url"),
                platforms=created.get("platforms", []),
                social_media_handles=created.get("social_media_handles", {}),
                industry=created.get("industry"),
                status=created.get("status", "active"),
                scan_frequency_minutes=created.get("scan_frequency_minutes", 60),
                created_at=created.get("created_at"),
                updated_at=created.get("updated_at"),
                last_scan_at=created.get("last_scan_at")
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create competitor in database"
            )
            
    except Exception as e:
        logger.error(f"Error creating competitor: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create competitor"
        )





@router.put("/{competitor_id}", response_model=CompetitorResponse)
async def update_competitor(
    competitor_id: str,
    competitor_data: CompetitorUpdateFrontend,
    user_id: str = Depends(get_user_id_from_header)
):
    """Update a competitor"""
    try:
        # Transform frontend data to match database schema
        update_data = competitor_data.dict(exclude_unset=True)
        
        # Ensure platforms field is handled correctly
        if 'platforms' in update_data and update_data['platforms'] is None:
            update_data['platforms'] = []
        
        # Use Supabase client to update competitor
        result = await supabase_client.update_competitor(competitor_id, update_data, user_id)
        
        if result.get("success"):
            # Get the updated competitor data
            updated_competitor = await supabase_client.get_user_competitors(user_id)
            competitor_data = next((comp for comp in updated_competitor if comp.get("id") == competitor_id), None)
            
            if competitor_data:
                return CompetitorResponse(
                    id=competitor_data.get("id"),
                    user_id=user_id,
                    name=competitor_data.get("name"),
                    description=competitor_data.get("description"),
                    website_url=competitor_data.get("website_url"),
                    platforms=competitor_data.get("platforms", []),
                    social_media_handles=competitor_data.get("social_media_handles", {}),
                    industry=competitor_data.get("industry"),
                    status=competitor_data.get("status", "active"),
                    scan_frequency_minutes=competitor_data.get("scan_frequency_minutes", 60),
                    created_at=competitor_data.get("created_at"),
                    updated_at=competitor_data.get("updated_at"),
                    last_scan_at=competitor_data.get("last_scan_at")
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Competitor not found after update"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update competitor in database"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating competitor: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update competitor"
        )


@router.delete("/{competitor_id}")
async def delete_competitor(
    competitor_id: str,
    user_id: str = Depends(get_user_id_from_header)
):
    """Delete a competitor"""
    try:
        # Use Supabase client to delete competitor
        result = await supabase_client.delete_competitor(competitor_id)
        
        if result.get("success"):
            return {"message": "Competitor deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete competitor from database"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting competitor: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete competitor"
        )


# (Removed competitor analysis endpoints due to missing models/schemas)
