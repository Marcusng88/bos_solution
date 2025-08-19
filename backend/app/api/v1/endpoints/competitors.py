"""
Competitors endpoints for managing competitor intelligence
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.auth_utils import get_user_id_from_header, get_db_user_id
from app.services.competitor.competitor_service import CompetitorService
from app.schemas.competitor import (
    CompetitorCreate, CompetitorResponse, CompetitorUpdate
)
import logging
import asyncio
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Supervisor agent removed - using simplified monitoring service instead

router = APIRouter()


@router.get("/", response_model=list[CompetitorResponse])
async def get_competitors(
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Get all competitors for a user"""
    try:
        # Convert Clerk user ID to database UUID
        db_user_id = await get_db_user_id(user_id, db)
        
        competitor_service = CompetitorService(db)
        competitors = await competitor_service.get_competitors(db_user_id)
        
        # Convert UUID fields to strings for proper serialization
        serialized_competitors = []
        for competitor in competitors:
            competitor_dict = {
                "id": str(competitor.id),
                "name": competitor.name,
                "description": competitor.description,
                "website_url": competitor.website_url,
                "social_media_handles": competitor.social_media_handles,
                "platforms": competitor.platforms or [],
                "industry": competitor.industry,
                "status": competitor.status,
                "created_at": competitor.created_at,
                "updated_at": competitor.updated_at,
                "last_scan_at": competitor.last_scan_at,
                "scan_frequency_minutes": competitor.scan_frequency_minutes,
                "user_id": str(competitor.user_id)
            }
            serialized_competitors.append(competitor_dict)
        
        return serialized_competitors
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch competitors"
        )


@router.post("/", response_model=CompetitorResponse)
async def create_competitor(
    competitor_data: CompetitorCreate,
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Create a new competitor"""
    try:
        logger.info(f"Creating competitor for user: {user_id}")
        logger.info(f"Competitor data: {competitor_data}")
        
        # Convert Clerk user ID to database UUID
        db_user_id = await get_db_user_id(user_id, db)
        logger.info(f"Converted user ID to database UUID: {db_user_id}")
        
        competitor_service = CompetitorService(db)
        competitor = await competitor_service.create_competitor(competitor_data, db_user_id)
        
        # Ensure the competitor object is properly serializable
        await db.refresh(competitor)
        
        # Convert UUID fields to strings for proper serialization
        competitor_dict = {
            "id": str(competitor.id),
            "name": competitor.name,
            "description": competitor.description,
            "website_url": competitor.website_url,
            "social_media_handles": competitor.social_media_handles,
            "platforms": competitor.platforms or [],
            "industry": competitor.industry,
            "status": competitor.status,
            "created_at": competitor.created_at,
            "updated_at": competitor.updated_at,
            "last_scan_at": competitor.last_scan_at,
            "scan_frequency_minutes": competitor.scan_frequency_minutes,
            "user_id": str(competitor.user_id)
        }
        
        return competitor_dict
    except Exception as e:
        import traceback
        logger.error(f"Error creating competitor: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Provide more specific error messages
        if "duplicate key" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Competitor with this name already exists"
            )
        elif "foreign key" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID or user not found"
            )
        elif "not null" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Required field is missing"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create competitor: {str(e)}"
            )


@router.get("/{competitor_id}", response_model=CompetitorResponse)
async def get_competitor(
    competitor_id: str,
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific competitor"""
    try:
        # Convert Clerk user ID to database UUID
        db_user_id = await get_db_user_id(user_id, db)
        
        competitor_service = CompetitorService(db)
        competitor = await competitor_service.get_competitor(competitor_id, db_user_id)
        
        if not competitor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Competitor not found"
            )
        return competitor
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch competitor"
        )


@router.put("/{competitor_id}", response_model=CompetitorResponse)
async def update_competitor(
    competitor_id: str,
    competitor_data: CompetitorUpdate,
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Update a competitor"""
    try:
        # Convert Clerk user ID to database UUID
        db_user_id = await get_db_user_id(user_id, db)
        
        competitor_service = CompetitorService(db)
        competitor = await competitor_service.update_competitor(competitor_id, competitor_data, db_user_id)
        
        if not competitor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Competitor not found"
            )
        return competitor
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update competitor"
        )


@router.delete("/{competitor_id}")
async def delete_competitor(
    competitor_id: str,
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Delete a competitor"""
    try:
        # Convert Clerk user ID to database UUID
        db_user_id = await get_db_user_id(user_id, db)
        
        competitor_service = CompetitorService(db)
        success = await competitor_service.delete_competitor(competitor_id, db_user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Competitor not found"
            )
        
        return {"message": "Competitor deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete competitor"
        )


@router.get("/stats/summary")
async def get_competitor_stats(
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Get competitor statistics summary"""
    try:
        # Convert Clerk user ID to database UUID
        db_user_id = await get_db_user_id(user_id, db)
        
        competitor_service = CompetitorService(db)
        stats = await competitor_service.get_competitor_stats(db_user_id)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch competitor statistics"
        )


@router.post("/{competitor_id}/toggle-status", response_model=CompetitorResponse)
async def toggle_competitor_status(
    competitor_id: str,
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Toggle competitor status between active and paused"""
    try:
        # Convert Clerk user ID to database UUID
        db_user_id = await get_db_user_id(user_id, db)
        
        competitor_service = CompetitorService(db)
        competitor = await competitor_service.toggle_competitor_status(competitor_id, db_user_id)
        
        if not competitor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Competitor not found"
            )
        return competitor
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to toggle competitor status"
        )


@router.put("/{competitor_id}/scan-frequency")
async def update_scan_frequency(
    competitor_id: str,
    frequency_minutes: int,
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Update scan frequency for a competitor"""
    try:
        # Convert Clerk user ID to database UUID
        db_user_id = await get_db_user_id(user_id, db)
        
        competitor_service = CompetitorService(db)
        competitor = await competitor_service.update_scan_frequency(competitor_id, frequency_minutes, db_user_id)
        
        if not competitor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Competitor not found"
            )
        return {"message": "Scan frequency updated successfully", "competitor": competitor}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update scan frequency"
        )


@router.post("/scan-all")
async def scan_all_competitors(
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Trigger a scan for all active competitors of a user"""
    try:
        logger.info(f"🚀 POST /scan-all endpoint called for user: {user_id}")
        logger.info(f"📊 Request method: POST")
        logger.info(f"🔑 User authentication successful for: {user_id}")
        logger.info(f"Starting scan-all request for user: {user_id}")
        
        # Convert Clerk user ID to database UUID
        db_user_id = await get_db_user_id(user_id, db)
        logger.info(f"Converted user ID {user_id} to database UUID: {db_user_id}")
        
        competitor_service = CompetitorService(db)
        competitors = await competitor_service.get_competitors(db_user_id)
        logger.info(f"Found {len(competitors)} total competitors for user {user_id}")
        
        if not competitors:
            logger.info(f"No competitors found for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No competitors found for this user"
            )
        
        # Filter active competitors
        active_competitors = [c for c in competitors if c.status == 'active']
        active_count = len(active_competitors)
        logger.info(f"Found {active_count} active competitors out of {len(competitors)} total for user {user_id}")
        
        if not active_competitors:
            logger.info(f"No active competitors found for user {user_id}")
            return {
                "message": "No active competitors found to scan",
                "competitors_scanned": 0,
                "total_competitors": len(competitors),
                "active_competitors": 0,
                "scan_started_at": datetime.now(timezone.utc).isoformat(),
                "user_id": user_id
            }
        
        # Initialize simple monitoring service
        from app.services.monitoring import SimpleMonitoringService
        monitoring_service = SimpleMonitoringService()
        logger.info(f"Initialized simple monitoring service for user {user_id}")
        
        # Trigger monitoring for all active competitors sequentially
        current_time = datetime.now(timezone.utc)
        
        # Start scanning all active competitors sequentially
        scan_results = []
        for competitor in active_competitors:
            logger.info(f"🔍 Starting scan for competitor {competitor.name} (ID: {competitor.id}) for user {user_id}")
            logger.info(f"   📊 Social media handles: {competitor.social_media_handles}")
            logger.info(f"   📱 Platforms: {competitor.platforms}")
            try:
                # Ensure we're in the right async context
                # Pass competitor name since orchestrator no longer queries database
                result = await monitoring_service.run_monitoring_for_competitor(
                    str(competitor.id), 
                    competitor.name
                )
                scan_results.append(result)
                logger.info(f"✅ Scan completed for {competitor.name}")
            except Exception as e:
                logger.error(f"❌ Scan failed for {competitor.name}: {e}")
                scan_results.append({"error": str(e)})
        
        logger.info(f"Completed {len(scan_results)} scan tasks for user {user_id}")
        
        # Process results
        successful_scans = 0
        failed_scans = 0
        scan_details = []
        
        for i, result in enumerate(scan_results):
            competitor = active_competitors[i]
            if isinstance(result, Exception):
                failed_scans += 1
                logger.error(f"❌ Scan failed for competitor {competitor.name} (ID: {competitor.id}) for user {user_id}: {result}")
                scan_details.append({
                    "competitor_id": str(competitor.id),
                    "competitor_name": competitor.name,
                    "status": "failed",
                    "error": str(result)
                })
            else:
                logger.info(f"📊 Scan result for {competitor.name}: {result}")
                if result.get("status") in ["completed", "completed_with_errors"]:
                    successful_scans += 1
                    logger.info(f"✅ Scan completed for competitor {competitor.name} (ID: {competitor.id}) for user {user_id}")
                    logger.info(f"   📈 Posts found: {result.get('posts_found', 0)}")
                    logger.info(f"   📱 Platforms analyzed: {result.get('platforms_analyzed', [])}")
                else:
                    failed_scans += 1
                    logger.warning(f"⚠️  Scan failed for competitor {competitor.name} (ID: {competitor.id}) for user {user_id}: {result.get('status')}")
                scan_details.append({
                    "competitor_id": str(competitor.id),
                    "competitor_name": competitor.name,
                    "status": result.get("status", "unknown"),
                    "posts_found": result.get("posts_found", 0),
                    "platforms_analyzed": result.get("platforms_analyzed", []),
                    "error": result.get("error")
                })
        
        # Close the monitoring service properly
        try:
            await monitoring_service.close()
            logger.info("✅ Monitoring service closed successfully")
        except Exception as e:
            logger.warning(f"⚠️  Warning: Could not close monitoring service: {e}")
        
        # Return comprehensive scan results
        return {
            "message": f"Scan completed for {len(active_competitors)} active competitors",
            "competitors_scanned": len(active_competitors),
            "total_competitors": len(competitors),
            "active_competitors": active_count,
            "successful_scans": successful_scans,
            "failed_scans": failed_scans,
            "scan_started_at": current_time.isoformat(),
            "scan_completed_at": datetime.now(timezone.utc).isoformat(),
            "scan_details": scan_details,
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"❌ Error scanning all competitors for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete competitor scans"
        )


@router.post("/{competitor_id}/scan")
async def scan_competitor(
    competitor_id: str,
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Trigger a manual scan for a specific competitor"""
    try:
        # Convert Clerk user ID to database UUID
        db_user_id = await get_db_user_id(user_id, db)
        
        competitor_service = CompetitorService(db)
        competitor = await competitor_service.get_competitor(competitor_id, db_user_id)
        
        if not competitor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Competitor not found"
            )
        
        current_time = datetime.now(timezone.utc)
        
        # Initialize simple monitoring service and trigger analysis
        from app.services.monitoring import SimpleMonitoringService
        monitoring_service = SimpleMonitoringService()
        
        # Start the competitor analysis
        scan_result = await monitoring_service.run_monitoring_for_competitor(competitor_id)
        
        # Update last scan time
        competitor.last_scan_at = current_time
        await db.commit()
        
        return {
            "message": "Competitor scan completed successfully",
            "competitor_id": competitor_id,
            "competitor_name": competitor.name,
            "scan_status": scan_result.get("status", "unknown"),
            "scan_started_at": current_time.isoformat(),
            "posts_found": scan_result.get("posts_found", 0),
            "platforms_analyzed": scan_result.get("platforms_analyzed", []),
            "error": scan_result.get("error")
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scanning competitor {competitor_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete competitor scan"
        )
