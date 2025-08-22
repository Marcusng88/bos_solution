"""
Competitors endpoints for managing competitor monitoring
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.core.database import get_db
from app.core.auth_utils import get_user_id_from_header
from app.schemas.competitor import CompetitorCreate, CompetitorUpdate, CompetitorResponse
from app.core.supabase_client import SupabaseClient
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[CompetitorResponse])
async def get_competitors(
    user_id: str = Depends(get_user_id_from_header),
    db: SupabaseClient = Depends(get_db)
):
    """Get all competitors for the authenticated user"""
    try:
        competitors = await db.get_competitors_by_user(user_id)
        return [CompetitorResponse.model_validate(comp) for comp in competitors]
    except Exception as e:
        logger.error(f"Error getting competitors: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get competitors: {str(e)}")


@router.get("/{competitor_id}", response_model=CompetitorResponse)
async def get_competitor(
    competitor_id: str,
    user_id: str = Depends(get_user_id_from_header),
    db: SupabaseClient = Depends(get_db)
):
    """Get a specific competitor by ID"""
    try:
        competitor = await db.get_competitor_by_id(competitor_id)
        
        if not competitor:
            raise HTTPException(status_code=404, detail="Competitor not found")
        
        # Verify the competitor belongs to the authenticated user
        if competitor.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return CompetitorResponse.model_validate(competitor)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting competitor: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get competitor: {str(e)}")


@router.post("/", response_model=CompetitorResponse)
async def create_competitor(
    competitor_data: CompetitorCreate,
    user_id: str = Depends(get_user_id_from_header),
    db: SupabaseClient = Depends(get_db)
):
    """Create a new competitor"""
    try:
        # Add user_id to competitor data
        competitor_dict = competitor_data.model_dump()
        competitor_dict["user_id"] = user_id
        
        result = await db.create_competitor(competitor_dict)
        
        if result:
            return CompetitorResponse.model_validate(result)
        else:
            raise HTTPException(status_code=500, detail="Failed to create competitor")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating competitor: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create competitor: {str(e)}")


@router.put("/{competitor_id}", response_model=CompetitorResponse)
async def update_competitor(
    competitor_id: str,
    competitor_data: CompetitorUpdate,
    user_id: str = Depends(get_user_id_from_header),
    db: SupabaseClient = Depends(get_db)
):
    """Update an existing competitor"""
    try:
        # Verify the competitor exists and belongs to the user
        existing_competitor = await db.get_competitor_by_id(competitor_id)
        
        if not existing_competitor:
            raise HTTPException(status_code=404, detail="Competitor not found")
        
        if existing_competitor.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update competitor data
        update_data = competitor_data.model_dump(exclude_unset=True)
        result = await db.update_competitor(competitor_id, update_data)
        
        if result:
            return CompetitorResponse.model_validate(result)
        else:
            raise HTTPException(status_code=500, detail="Failed to update competitor")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating competitor: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update competitor: {str(e)}")


@router.delete("/{competitor_id}")
async def delete_competitor(
    competitor_id: str,
    user_id: str = Depends(get_user_id_from_header),
    db: SupabaseClient = Depends(get_db)
):
    """Delete a competitor"""
    try:
        # Verify the competitor exists and belongs to the user
        existing_competitor = await db.get_competitor_by_id(competitor_id)
        
        if not existing_competitor:
            raise HTTPException(status_code=404, detail="Competitor not found")
        
        if existing_competitor.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Delete competitor
        success = await db.delete_competitor(competitor_id)
        
        if success:
            return {"message": "Competitor deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete competitor")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting competitor: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete competitor: {str(e)}")


@router.post("/{competitor_id}/scan")
async def trigger_competitor_scan(
    competitor_id: str,
    user_id: str = Depends(get_user_id_from_header),
    db: SupabaseClient = Depends(get_db)
):
    """Trigger a manual scan for a competitor"""
    try:
        # Verify the competitor exists and belongs to the user
        existing_competitor = await db.get_competitor_by_id(competitor_id)
        
        if not existing_competitor:
            raise HTTPException(status_code=404, detail="Competitor not found")
        
        if existing_competitor.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update scan time
        success = await db.update_competitor_scan_time(competitor_id)
        
        if success:
            return {"message": "Competitor scan triggered successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to trigger competitor scan")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering competitor scan: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to trigger competitor scan: {str(e)}")

@router.post("/{competitor_id}/toggle-status")
async def toggle_competitor_status(
    competitor_id: str,
    user_id: str = Depends(get_user_id_from_header),
    db: SupabaseClient = Depends(get_db)
):
    """Toggle competitor status between active and paused"""
    try:
        # Verify the competitor exists and belongs to the user
        existing_competitor = await db.get_competitor_by_id(competitor_id)
        
        if not existing_competitor:
            raise HTTPException(status_code=404, detail="Competitor not found")
        
        if existing_competitor.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Toggle status
        current_status = existing_competitor.get("status", "active")
        new_status = "paused" if current_status == "active" else "active"
        
        # Update competitor status
        result = await db.update_competitor(competitor_id, {"status": new_status})
        
        if result:
            return {"message": f"Competitor status updated to {new_status}", "status": new_status}
        else:
            raise HTTPException(status_code=500, detail="Failed to update competitor status")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling competitor status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to toggle competitor status: {str(e)}")

@router.put("/{competitor_id}/scan-frequency")
async def update_scan_frequency(
    competitor_id: str,
    frequency_data: dict,
    user_id: str = Depends(get_user_id_from_header),
    db: SupabaseClient = Depends(get_db)
):
    """Update scan frequency for a competitor"""
    try:
        # Verify the competitor exists and belongs to the user
        existing_competitor = await db.get_competitor_by_id(competitor_id)
        
        if not existing_competitor:
            raise HTTPException(status_code=404, detail="Competitor not found")
        
        if existing_competitor.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        frequency_minutes = frequency_data.get("frequency_minutes")
        if not frequency_minutes or frequency_minutes < 15 or frequency_minutes > 1440:
            raise HTTPException(status_code=400, detail="frequency_minutes must be between 15 and 1440")
        
        # Update scan frequency
        result = await db.update_competitor(competitor_id, {"scan_frequency_minutes": frequency_minutes})
        
        if result:
            return {"message": "Scan frequency updated successfully", "scan_frequency_minutes": frequency_minutes}
        else:
            raise HTTPException(status_code=500, detail="Failed to update scan frequency")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating scan frequency: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update scan frequency: {str(e)}")

@router.post("/scan-all")
async def scan_all_competitors(
    user_id: str = Depends(get_user_id_from_header),
    db: SupabaseClient = Depends(get_db)
):
    """Scan all competitors for the authenticated user"""
    try:
        # Get all competitors for the user
        competitors = await db.get_competitors_by_user(user_id)
        
        if not competitors:
            return {"message": "No competitors found to scan", "scanned_count": 0}
        
        # Update scan time for all competitors
        scanned_count = 0
        for competitor in competitors:
            success = await db.update_competitor_scan_time(competitor["id"])
            if success:
                scanned_count += 1
        
        return {
            "message": f"Scan initiated for {scanned_count} competitors",
            "scanned_count": scanned_count,
            "total_competitors": len(competitors)
        }
        
    except Exception as e:
        logger.error(f"Error scanning all competitors: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to scan all competitors: {str(e)}")

@router.get("/stats/summary")
async def get_competitor_stats_summary(
    user_id: str = Depends(get_user_id_from_header),
    db: SupabaseClient = Depends(get_db)
):
    """Get competitor statistics summary for the authenticated user"""
    try:
        # Get all competitors for the user
        competitors = await db.get_competitors_by_user(user_id)
        
        # Calculate summary statistics
        total_competitors = len(competitors)
        active_competitors = sum(1 for c in competitors if c.get("status") == "active")
        paused_competitors = sum(1 for c in competitors if c.get("status") == "paused")
        error_competitors = sum(1 for c in competitors if c.get("status") == "error")
        
        # Calculate average scan frequency
        scan_frequencies = [c.get("scan_frequency_minutes", 60) for c in competitors]
        avg_scan_frequency = sum(scan_frequencies) / len(scan_frequencies) if scan_frequencies else 60
        
        # Get platforms being monitored
        all_platforms = set()
        for competitor in competitors:
            platforms = competitor.get("platforms", [])
            if isinstance(platforms, list):
                all_platforms.update(platforms)
        
        # Get recent activity (competitors scanned in last 24 hours)
        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone.utc)
        yesterday = now - timedelta(days=1)
        
        recent_activity = 0
        for competitor in competitors:
            last_scan = competitor.get("last_scan_at")
            if last_scan:
                try:
                    # Parse ISO format datetime
                    if isinstance(last_scan, str):
                        last_scan_dt = datetime.fromisoformat(last_scan.replace('Z', '+00:00'))
                    else:
                        last_scan_dt = last_scan
                    
                    if last_scan_dt.tzinfo is None:
                        last_scan_dt = last_scan_dt.replace(tzinfo=timezone.utc)
                    
                    if last_scan_dt >= yesterday:
                        recent_activity += 1
                except (ValueError, TypeError):
                    # Skip if date parsing fails
                    continue
        
        summary = {
            "user_id": user_id,
            "total_competitors": total_competitors,
            "active_competitors": active_competitors,
            "paused_competitors": paused_competitors,
            "error_competitors": error_competitors,
            "average_scan_frequency_minutes": round(avg_scan_frequency, 1),
            "platforms_monitored": list(all_platforms),
            "recent_activity_24h": recent_activity,
            "last_updated": now.isoformat()
        }
        
        logger.info(f"✅ Competitor stats summary retrieved for user {user_id}")
        return summary
        
    except Exception as e:
        logger.error(f"Error getting competitor stats summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get competitor stats: {str(e)}")
