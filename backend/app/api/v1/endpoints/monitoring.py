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
from datetime import datetime, timedelta, timezone

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
        unread_alerts = 0
        recent_activity_24h = 0
        last_scan_time = None
        
        # Calculate 24 hours ago timestamp
        twenty_four_hours_ago = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=24)
        
        for competitor in competitors:
            competitor_data = await db.get_monitoring_data_by_competitor(competitor["id"], limit=1000)
            total_monitoring_data += len(competitor_data)
            
            # Count recent activity (last 24 hours)
            for data in competitor_data:
                detected_at = data.get("detected_at")
                if detected_at:
                    try:
                        if isinstance(detected_at, str):
                            detected_dt = datetime.fromisoformat(detected_at.replace('Z', '+00:00'))
                        else:
                            detected_dt = detected_at
                        
                        # Ensure both dates are timezone-aware for comparison
                        if detected_dt.tzinfo is None:
                            detected_dt = detected_dt.replace(tzinfo=timezone.utc)
                        
                        if detected_dt > twenty_four_hours_ago.replace(tzinfo=timezone.utc):
                            recent_activity_24h += 1
                        
                        # Track last scan time
                        if not last_scan_time or detected_dt > last_scan_time:
                            last_scan_time = detected_dt
                    except Exception as e:
                        logger.warning(f"Error parsing date {detected_at}: {e}")
                        continue
            
            # Add platforms from competitor settings
            competitor_platforms = ["youtube", "browser", "website"]  # Core platforms for all competitors
            if isinstance(competitor_platforms, list):
                platforms_monitored.update(competitor_platforms)
        
        # Get unread alerts count
        try:
            # This would need to be implemented in the Supabase client
            # For now, we'll estimate based on recent monitoring data
            unread_alerts = min(recent_activity_24h, 10)  # Estimate based on recent activity
        except Exception as e:
            logger.warning(f"Could not get unread alerts count: {e}")
            unread_alerts = 0
        
        return {
            "success": True,
            "stats": {
                "user_id": user_id,
                "total_competitors": total_competitors,
                "total_monitoring_data": total_monitoring_data,
                "unread_alerts": unread_alerts,
                "recent_activity_24h": recent_activity_24h,
                "last_scan_time": last_scan_time.isoformat() if last_scan_time else None,
                "platforms_monitored": list(platforms_monitored),
                "average_data_per_competitor": total_monitoring_data / total_competitors if total_competitors > 0 else 0
            }
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
        total_active_jobs = 0
        next_scheduled_run = None
        
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
            
            # Core platforms are always the same for all competitors
            platforms_monitored.update(["youtube", "browser", "website"])
        
        # Calculate overall status
        overall_status = "active" if active_competitors > 0 else "inactive"
        if active_competitors > 0 and total_competitors > active_competitors:
            overall_status = "partial"
        
        # Get most recent scan time
        latest_scan = max(last_scan_times) if last_scan_times else None
        
        # Calculate next scheduled run (estimate based on scan frequency)
        if latest_scan:
            try:
                if isinstance(latest_scan, str):
                    latest_scan_dt = datetime.fromisoformat(latest_scan.replace('Z', '+00:00'))
                else:
                    latest_scan_dt = latest_scan
                
                # Ensure the datetime is timezone-aware
                if latest_scan_dt.tzinfo is None:
                    latest_scan_dt = latest_scan_dt.replace(tzinfo=timezone.utc)
                
                # Estimate next run based on average scan frequency (24 hours)
                next_scheduled_run = (latest_scan_dt + timedelta(minutes=1440)).isoformat()
            except Exception as e:
                logger.warning(f"Error calculating next scheduled run: {e}")
        
        # Estimate active jobs based on recent activity
        total_active_jobs = min(active_competitors, 5)  # Estimate based on active competitors
        
        return {
            "success": True,
            "status": {
                "user_id": user_id,
                "running": overall_status == "active",
                "overall_status": overall_status,
                "total_competitors": total_competitors,
                "active_competitors": active_competitors,
                "total_monitoring_data": total_monitoring_data,
                "total_active_jobs": total_active_jobs,
                "platforms_monitored": list(platforms_monitored),
                "latest_scan_time": latest_scan,
                "next_scheduled_run": next_scheduled_run,
                "last_updated": latest_scan
            }
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
        # Get alerts for the user
        params = {"user_id": f"eq.{user_id}", "order": "created_at.desc", "limit": str(limit)}
        if is_read is not None:
            params["is_read"] = f"eq.{str(is_read).lower()}"
        
        response = await db._make_request("GET", "monitoring_alerts", params=params)
        if response.status_code == 200:
            alerts = response.json()
            return [MonitoringAlertResponse.model_validate(alert) for alert in alerts]
        return []
    except Exception as e:
        logger.error(f"Error getting monitoring alerts: {e}")
        # Return empty list instead of raising error to prevent frontend crashes
        return []

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
    """Scan a specific platform for a competitor (legacy endpoint - now redirects to full competitor scan)"""
    try:
        competitor_id = scan_data.get("competitor_id")
        if not competitor_id:
            raise HTTPException(status_code=400, detail="competitor_id is required")
        
        # Verify the competitor belongs to the user
        competitor = await db.get_competitor_by_id(competitor_id)
        if not competitor or competitor.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Validate platform (only allow core platforms)
        valid_platforms = ["youtube", "browser", "website"]
        if platform not in valid_platforms:
            raise HTTPException(status_code=400, detail=f"Invalid platform. Must be one of: {', '.join(valid_platforms)}")
        
        logger.info(f"🚀 Starting {platform} scan for competitor {competitor_id}")
        
        # Run the actual monitoring using the monitoring service with specific platform
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
    """Scan a specific competitor using all three core agents (youtube, browser, website)"""
    try:
        # Verify the competitor belongs to the user
        competitor = await db.get_competitor_by_id(competitor_id)
        if not competitor or competitor.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        logger.info(f"🚀 Starting competitor scan for {competitor_id} with core agents (youtube, browser, website)")
        
        # Run the actual monitoring using the monitoring service (automatically uses core agents)
        result = await monitoring_service.run_monitoring_for_competitor(
            competitor_id=competitor_id
        )
        
        if result.get("status") == "completed":
            return {
                "message": f"Competitor scan completed successfully using core agents (youtube, browser, website)",
                "competitor_id": competitor_id,
                "platforms": ["youtube", "browser", "website"],
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
                "platforms": ["youtube", "browser", "website"],
                "status": "completed_with_warnings",
                "platforms_analyzed": result.get("platforms_analyzed", []),
                "warnings": result.get("errors", [])
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scanning competitor {competitor_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to scan competitor: {str(e)}")

# New endpoint for starting/stopping continuous monitoring
@router.post("/start-continuous-monitoring")
async def start_continuous_monitoring(
    user_id: str = Depends(get_user_id_from_header),
    db: SupabaseClient = Depends(get_db)
):
    """Start continuous monitoring for all user's competitors"""
    try:
        # Get all competitors for the user
        competitors = await db.get_competitors_by_user(user_id)
        
        if not competitors:
            return {
                "success": False,
                "message": "No competitors found for this user"
            }
        
        # Update user monitoring settings to enable continuous monitoring
        settings_data = {
            "user_id": user_id,
            "global_monitoring_enabled": True,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        result = await db.upsert_user_monitoring_settings(settings_data)
        
        if result:
            return {
                "success": True,
                "message": f"Continuous monitoring started for {len(competitors)} competitors",
                "competitors_count": len(competitors)
            }
        else:
            return {
                "success": False,
                "message": "Failed to start continuous monitoring"
            }
            
    except Exception as e:
        logger.error(f"Error starting continuous monitoring: {e}")
        return {
            "success": False,
            "message": f"Failed to start continuous monitoring: {str(e)}"
        }

@router.post("/stop-continuous-monitoring")
async def stop_continuous_monitoring(
    user_id: str = Depends(get_user_id_from_header),
    db: SupabaseClient = Depends(get_db)
):
    """Stop continuous monitoring for all user's competitors"""
    try:
        # Update user monitoring settings to disable continuous monitoring
        settings_data = {
            "user_id": user_id,
            "global_monitoring_enabled": False,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        result = await db.upsert_user_monitoring_settings(settings_data)
        
        if result:
            return {
                "success": True,
                "message": "Continuous monitoring stopped successfully"
            }
        else:
            return {
                "success": False,
                "message": "Failed to stop continuous monitoring"
            }
            
    except Exception as e:
        logger.error(f"Error stopping continuous monitoring: {e}")
        return {
            "success": False,
            "message": f"Failed to stop continuous monitoring: {str(e)}"
        }

@router.post("/run-monitoring-for-all-competitors")
async def run_monitoring_for_all_competitors(
    user_id: str = Depends(get_user_id_from_header),
    db: SupabaseClient = Depends(get_db)
):
    """Run monitoring scan for all user's competitors using core agents (youtube, browser, website)"""
    try:
        # Get all competitors for the user
        competitors = await db.get_competitors_by_user(user_id)
        
        if not competitors:
            return {
                "success": False,
                "message": "No competitors found for this user"
            }
        
        # Start monitoring for each competitor using core agents
        results = []
        for competitor in competitors:
            try:
                # Always use the three core agents: youtube, browser, website
                result = await monitoring_service.run_monitoring_for_competitor(
                    competitor_id=competitor["id"]
                )
                results.append({
                    "competitor_id": competitor["id"],
                    "competitor_name": competitor["name"],
                    "result": result
                })
            except Exception as e:
                logger.error(f"Error monitoring competitor {competitor['id']}: {e}")
                results.append({
                    "competitor_id": competitor["id"],
                    "competitor_name": competitor["name"],
                    "error": str(e)
                })
        
        return {
            "success": True,
            "message": f"Monitoring scan completed for {len(competitors)} competitors using core agents (youtube, browser, website)",
            "results": results
        }
            
    except Exception as e:
        logger.error(f"Error running monitoring for all competitors: {e}")
        return {
            "success": False,
            "message": f"Failed to run monitoring scan: {str(e)}"
        }
