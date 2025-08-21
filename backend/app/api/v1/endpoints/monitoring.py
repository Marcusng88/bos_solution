"""
Monitoring endpoints for social media monitoring and alerts
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from app.core.database import get_db
from app.core.auth_utils import get_user_id_from_header
from app.schemas.monitoring import MonitoringDataResponse, MonitoringAlertResponse
from app.core.supabase_client import SupabaseClient
from app.services.monitoring.orchestrator import SimpleMonitoringService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize monitoring service
monitoring_service = SimpleMonitoringService()

@router.get("/data", response_model=List[MonitoringDataResponse])
async def get_all_monitoring_data(
    limit: int = Query(100, ge=1, le=1000),
    user_id: str = Depends(get_user_id_from_header),
    db: SupabaseClient = Depends(get_db)
):
    """Get all monitoring data for the authenticated user"""
    try:
        # Get all competitors for the user
        competitors = await db.get_competitors_by_user(user_id)
        
        # Collect monitoring data from all competitors
        all_monitoring_data = []
        for competitor in competitors:
            competitor_data = await db.get_monitoring_data_by_competitor(competitor["id"], limit=limit)
            all_monitoring_data.extend(competitor_data)
        
        # Sort by detected_at (most recent first) and limit results
        all_monitoring_data.sort(key=lambda x: x.get("detected_at", ""), reverse=True)
        all_monitoring_data = all_monitoring_data[:limit]
        
        return [MonitoringDataResponse.model_validate(data) for data in all_monitoring_data]
    except Exception as e:
        logger.error(f"Error getting all monitoring data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get monitoring data: {str(e)}")

@router.get("/monitoring-data", response_model=List[MonitoringDataResponse])
async def get_all_monitoring_data_alias(
    limit: int = Query(100, ge=1, le=1000),
    user_id: str = Depends(get_user_id_from_header),
    db: SupabaseClient = Depends(get_db)
):
    """Alias endpoint for /data to match frontend expectations"""
    return await get_all_monitoring_data(limit=limit, user_id=user_id, db=db)

@router.get("/data/{competitor_id}", response_model=List[MonitoringDataResponse])
async def get_monitoring_data(
    competitor_id: str,
    limit: int = 100,
    user_id: str = Depends(get_user_id_from_header),
    db: SupabaseClient = Depends(get_db)
):
    """Get monitoring data for a specific competitor"""
    try:
        # Verify the competitor belongs to the user
        competitor = await db.get_competitor_by_id(competitor_id)
        if not competitor or competitor.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        monitoring_data = await db.get_monitoring_data_by_competitor(competitor_id, limit)
        return [MonitoringDataResponse.model_validate(data) for data in monitoring_data]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting monitoring data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get monitoring data: {str(e)}")

@router.get("/monitoring-stats")
async def get_user_monitoring_stats(
    user_id: str = Depends(get_user_id_from_header),
    db: SupabaseClient = Depends(get_db)
):
    """Get overall monitoring statistics for the authenticated user"""
    try:
        # Get all competitors for the user
        competitors = await db.get_competitors_by_user(user_id)
        
        # Calculate overall statistics
        total_competitors = len(competitors)
        total_monitoring_data = 0
        platforms_monitored = set()
        
        for competitor in competitors:
            competitor_data = await db.get_monitoring_data_by_competitor(competitor["id"], limit=1000)
            total_monitoring_data += len(competitor_data)
            
            # Add platforms from competitor settings
            competitor_platforms = competitor.get("platforms", [])
            if isinstance(competitor_platforms, list):
                platforms_monitored.update(competitor_platforms)
        
        return {
            "user_id": user_id,
            "total_competitors": total_competitors,
            "total_monitoring_data": total_monitoring_data,
            "platforms_monitored": list(platforms_monitored),
            "average_data_per_competitor": total_monitoring_data / total_competitors if total_competitors > 0 else 0
        }
        
    except Exception as e:
        logger.error(f"Error getting user monitoring stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get monitoring stats: {str(e)}")

@router.get("/stats")
async def get_user_monitoring_stats_alias(
    user_id: str = Depends(get_user_id_from_header),
    db: SupabaseClient = Depends(get_db)
):
    """Alias endpoint for /monitoring-stats to match frontend expectations"""
    return await get_user_monitoring_stats(user_id=user_id, db=db)

@router.get("/status")
async def get_monitoring_status(
    user_id: str = Depends(get_user_id_from_header),
    db: SupabaseClient = Depends(get_db)
):
    """Get overall monitoring status for the authenticated user"""
    try:
        # Get all competitors for the user
        competitors = await db.get_competitors_by_user(user_id)
        
        # Calculate status information
        total_competitors = len(competitors)
        active_competitors = 0
        total_monitoring_data = 0
        platforms_monitored = set()
        last_scan_times = []
        
        for competitor in competitors:
            # Check if competitor has recent monitoring data (active)
            competitor_data = await db.get_monitoring_data_by_competitor(competitor["id"], limit=1)
            if competitor_data:
                active_competitors += 1
                total_monitoring_data += len(competitor_data)
                
                # Get last scan time
                if competitor_data:
                    last_scan = competitor_data[0].get("detected_at")
                    if last_scan:
                        last_scan_times.append(last_scan)
            
            # Add platforms from competitor settings
            competitor_platforms = competitor.get("platforms", [])
            if isinstance(competitor_platforms, list):
                platforms_monitored.update(competitor_platforms)
        
        # Calculate overall status
        overall_status = "active" if active_competitors > 0 else "inactive"
        if active_competitors > 0 and total_competitors > active_competitors:
            overall_status = "partial"
        
        # Get most recent scan time
        latest_scan = max(last_scan_times) if last_scan_times else None
        
        return {
            "user_id": user_id,
            "overall_status": overall_status,
            "total_competitors": total_competitors,
            "active_competitors": active_competitors,
            "total_monitoring_data": total_monitoring_data,
            "platforms_monitored": list(platforms_monitored),
            "latest_scan_time": latest_scan,
            "last_updated": latest_scan
        }
        
    except Exception as e:
        logger.error(f"Error getting monitoring status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get monitoring status: {str(e)}")

@router.get("/alerts", response_model=List[MonitoringAlertResponse])
async def get_monitoring_alerts(
    user_id: str = Depends(get_user_id_from_header),
    db: SupabaseClient = Depends(get_db),
    is_read: Optional[bool] = None,
    limit: int = 100
):
    """Get monitoring alerts for the authenticated user"""
    try:
        # This would need to be implemented in the Supabase client
        # For now, return empty list
        logger.warning("Getting monitoring alerts not yet implemented")
        return []
    except Exception as e:
        logger.error(f"Error getting monitoring alerts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get monitoring alerts: {str(e)}")

@router.post("/data")
async def create_monitoring_data(
    monitoring_data: dict,
    user_id: str = Depends(get_user_id_from_header),
    db: SupabaseClient = Depends(get_db)
):
    """Create new monitoring data entry"""
    try:
        # Verify the competitor belongs to the user
        competitor_id = monitoring_data.get("competitor_id")
        if competitor_id:
            competitor = await db.get_competitor_by_id(competitor_id)
            if not competitor or competitor.get("user_id") != user_id:
                raise HTTPException(status_code=403, detail="Access denied")
        
        result = await db.save_monitoring_data(monitoring_data)
        
        if result:
            return {"id": result, "message": "Monitoring data created successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to create monitoring data")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating monitoring data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create monitoring data: {str(e)}")

@router.post("/alerts")
async def create_monitoring_alert(
    alert_data: dict,
    user_id: str = Depends(get_user_id_from_header),
    db: SupabaseClient = Depends(get_db)
):
    """Create new monitoring alert"""
    try:
        # Verify the competitor belongs to the user if specified
        competitor_id = alert_data.get("competitor_id")
        if competitor_id:
            competitor = await db.get_competitor_by_id(competitor_id)
            if not competitor or competitor.get("user_id") != user_id:
                raise HTTPException(status_code=403, detail="Access denied")
        
        result = await db.create_monitoring_alert(alert_data)
        
        if result:
            return {"id": result, "message": "Monitoring alert created successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to create monitoring alert")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating monitoring alert: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create monitoring alert: {str(e)}")

@router.get("/stats/{competitor_id}")
async def get_monitoring_stats(
    competitor_id: str,
    user_id: str = Depends(get_user_id_from_header),
    db: SupabaseClient = Depends(get_db)
):
    """Get monitoring statistics for a competitor"""
    try:
        # Verify the competitor belongs to the user
        competitor = await db.get_competitor_by_id(competitor_id)
        if not competitor or competitor.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get monitoring data for statistics
        monitoring_data = await db.get_monitoring_data_by_competitor(competitor_id, limit=1000)
        
        # Calculate basic statistics
        total_posts = len(monitoring_data)
        platforms = set()
        engagement_total = 0
        
        for data in monitoring_data:
            platform = data.get("platform")
            if platform:
                platforms.add(platform)
            
            engagement = data.get("engagement_metrics", {})
            if isinstance(engagement, dict):
                engagement_total += engagement.get("total_engagement", 0)
        
        return {
            "competitor_id": competitor_id,
            "total_posts": total_posts,
            "platforms_monitored": list(platforms),
            "total_engagement": engagement_total,
            "average_engagement": engagement_total / total_posts if total_posts > 0 else 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting monitoring stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get monitoring stats: {str(e)}")

@router.post("/scan-platform/{platform}")
async def scan_platform(
    platform: str,
    scan_data: dict,
    user_id: str = Depends(get_user_id_from_header),
    db: SupabaseClient = Depends(get_db)
):
    """Scan a specific platform for a competitor"""
    try:
        competitor_id = scan_data.get("competitor_id")
        if not competitor_id:
            raise HTTPException(status_code=400, detail="competitor_id is required")
        
        # Verify the competitor belongs to the user
        competitor = await db.get_competitor_by_id(competitor_id)
        if not competitor or competitor.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Validate platform
        valid_platforms = ["youtube", "website", "browser", "instagram", "twitter"]
        if platform not in valid_platforms:
            raise HTTPException(status_code=400, detail=f"Invalid platform. Must be one of: {', '.join(valid_platforms)}")
        
        logger.info(f"🚀 Starting {platform} scan for competitor {competitor_id}")
        
        # Run the actual monitoring using the monitoring service
        result = await monitoring_service.run_monitoring_for_competitor(
            competitor_id=competitor_id,
            platforms=[platform]
        )
        
        if result.get("status") == "completed":
            return {
                "message": f"Platform {platform} scan completed successfully",
                "platform": platform,
                "competitor_id": competitor_id,
                "status": "completed",
                "results": result.get("platform_results", {}).get(platform, {}),
                "monitoring_data_count": result.get("monitoring_data_count", 0)
            }
        else:
            # Check if there were errors
            platform_results = result.get("platform_results", {}).get(platform, {})
            if "error" in platform_results:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Platform scan failed: {platform_results['error']}"
                )
            
            return {
                "message": f"Platform {platform} scan completed with warnings",
                "platform": platform,
                "competitor_id": competitor_id,
                "status": "completed_with_warnings",
                "results": platform_results,
                "warnings": result.get("errors", [])
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scanning platform {platform}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to scan platform: {str(e)}")

@router.post("/scan-competitor/{competitor_id}")
async def scan_competitor(
    competitor_id: str,
    scan_data: dict,
    user_id: str = Depends(get_user_id_from_header),
    db: SupabaseClient = Depends(get_db)
):
    """Scan a specific competitor with optional platforms"""
    try:
        # Verify the competitor belongs to the user
        competitor = await db.get_competitor_by_id(competitor_id)
        if not competitor or competitor.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        platforms = scan_data.get("platforms", [])
        if not platforms:
            # Use competitor's default platforms if none specified
            platforms = competitor.get("platforms", ["youtube"])
        
        logger.info(f"🚀 Starting competitor scan for {competitor_id} with platforms: {platforms}")
        
        # Run the actual monitoring using the monitoring service
        result = await monitoring_service.run_monitoring_for_competitor(
            competitor_id=competitor_id,
            platforms=platforms
        )
        
        if result.get("status") == "completed":
            return {
                "message": f"Competitor scan completed successfully",
                "competitor_id": competitor_id,
                "platforms": platforms,
                "status": "completed",
                "platforms_analyzed": result.get("platforms_analyzed", []),
                "monitoring_data_count": result.get("monitoring_data_count", 0)
            }
        else:
            # Check if there were errors
            if result.get("errors"):
                raise HTTPException(
                    status_code=500, 
                    detail=f"Competitor scan failed: {'; '.join(result['errors'])}"
                )
            
            return {
                "message": f"Competitor scan completed with warnings",
                "competitor_id": competitor_id,
                "platforms": platforms,
                "status": "completed_with_warnings",
                "platforms_analyzed": result.get("platforms_analyzed", []),
                "warnings": result.get("errors", [])
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scanning competitor {competitor_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to scan competitor: {str(e)}")
