from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from app.schemas.draft import DraftCreate, DraftUpdate, DraftResponse, DraftListResponse
from app.core.supabase_client import SupabaseClient
from app.core.auth_utils import get_user_id_from_header
from datetime import datetime
import uuid
import logging

router = APIRouter()
supabase_client = SupabaseClient()
logger = logging.getLogger(__name__)

@router.post("/", response_model=DraftResponse)
async def create_draft(
    draft: DraftCreate,
    user_id: str = Depends(get_user_id_from_header)
):
    """Create a new draft"""
    try:
        draft_data = draft.dict()
        draft_data["id"] = str(uuid.uuid4())
        draft_data["user_id"] = user_id
        draft_data["created_at"] = datetime.utcnow().isoformat()
        draft_data["updated_at"] = datetime.utcnow().isoformat()
        
        created_draft = await supabase_client.create_draft(draft_data)
        
        if not created_draft:
            raise HTTPException(status_code=500, detail="Failed to create draft")
        
        return DraftResponse(**created_draft)
    except Exception as e:
        logger.error(f"Error creating draft: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create draft: {str(e)}")

@router.get("/", response_model=DraftListResponse)
async def get_user_drafts(
    user_id: str = Depends(get_user_id_from_header),
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page")
):
    """Get all drafts for a user with pagination"""
    try:
        result = await supabase_client.get_user_drafts(user_id, status, page, per_page)
        drafts = [DraftResponse(**draft) for draft in result.get("drafts", [])]
        return DraftListResponse(
            drafts=drafts,
            total=result.get("total", 0),
            page=page,
            per_page=per_page
        )
    except Exception as e:
        logger.error(f"Error getting drafts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get drafts: {str(e)}")

@router.get("/{draft_id}", response_model=DraftResponse)
async def get_draft_by_id(
    draft_id: str,
    user_id: str = Depends(get_user_id_from_header)
):
    """Get a specific draft by ID"""
    try:
        draft = await supabase_client.get_draft_by_id(draft_id, user_id)
        if not draft:
            raise HTTPException(status_code=404, detail="Draft not found")
        return DraftResponse(**draft)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting draft by ID: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get draft: {str(e)}")

@router.put("/{draft_id}", response_model=DraftResponse)
async def update_draft(
    draft_id: str,
    draft_update: DraftUpdate,
    user_id: str = Depends(get_user_id_from_header)
):
    """Update a draft"""
    try:
        update_data = draft_update.dict(exclude_unset=True)
        updated_draft = await supabase_client.update_draft(draft_id, user_id, update_data)
        if not updated_draft:
            raise HTTPException(status_code=404, detail="Draft not found or update failed")
        return DraftResponse(**updated_draft)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating draft: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update draft: {str(e)}")

@router.delete("/{draft_id}")
async def delete_draft(
    draft_id: str,
    user_id: str = Depends(get_user_id_from_header)
):
    """Delete a draft"""
    try:
        success = await supabase_client.delete_draft(draft_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Draft not found or delete failed")
        return {"message": "Draft deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting draft: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete draft: {str(e)}")
