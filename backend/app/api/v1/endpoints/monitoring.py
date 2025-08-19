"""
Monitoring endpoints for continuous monitoring and alerts
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)
from app.core.database import get_db
from app.core.auth_utils import get_user_id_from_header, get_db_user_id
from app.models.user_settings import UserMonitoringSettings
from app.models.monitoring import MonitoringAlert
from app.schemas.monitoring import (
    UserMonitoringSettingsCreate, UserMonitoringSettingsResponse, UserMonitoringSettingsUpdate,
    MonitoringAlertCreate, MonitoringAlertResponse, PlatformScanRequest, PlatformScanResponse
)
from app.services.monitoring import monitoring_scheduler, MonitoringService, SimpleMonitoringService

router = APIRouter()


@router.get("/settings", response_model=UserMonitoringSettingsResponse)
async def get_user_monitoring_settings(
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Get user monitoring settings"""
    try:
        # Convert Clerk user ID to database UUID
        db_user_id = await get_db_user_id(user_id, db)
        
        result = await db.execute(
            select(UserMonitoringSettings).where(UserMonitoringSettings.user_id == db_user_id)
        )
        settings = result.scalar_one_or_none()
        if not settings:
            # Create default settings if none exist
            settings = UserMonitoringSettings(user_id=db_user_id)
            db.add(settings)
            await db.commit()
            await db.refresh(settings)
        return settings
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch monitoring settings"
        )


@router.post("/settings", response_model=UserMonitoringSettingsResponse)
async def create_user_monitoring_settings(
    settings_data: UserMonitoringSettingsCreate,
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Create or update user monitoring settings"""
    try:
        # Convert Clerk user ID to database UUID
        db_user_id = await get_db_user_id(user_id, db)
        
        # Check if settings already exist
        result = await db.execute(
            select(UserMonitoringSettings).where(UserMonitoringSettings.user_id == db_user_id)
        )
        existing_settings = result.scalar_one_or_none()
        
        if existing_settings:
            # Update existing settings
            for field, value in settings_data.dict(exclude_unset=True).items():
                setattr(existing_settings, field, value)
            await db.commit()
            await db.refresh(existing_settings)
            return existing_settings
        else:
            # Create new settings
            settings = UserMonitoringSettings(
                user_id=db_user_id,
                **settings_data.dict(exclude={'user_id'})
            )
            db.add(settings)
            await db.commit()
            await db.refresh(settings)
            return settings
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create/update monitoring settings"
        )


@router.put("/settings", response_model=UserMonitoringSettingsResponse)
async def update_user_monitoring_settings(
    settings_data: UserMonitoringSettingsUpdate,
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Update user monitoring settings"""
    try:
        # Convert Clerk user ID to database UUID
        db_user_id = await get_db_user_id(user_id, db)
        
        result = await db.execute(
            select(UserMonitoringSettings).where(UserMonitoringSettings.user_id == db_user_id)
        )
        settings = result.scalar_one_or_none()
        if not settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Monitoring settings not found"
            )
        
        # Update fields
        for field, value in settings_data.dict(exclude_unset=True).items():
            setattr(settings, field, value)
        
        await db.commit()
        await db.refresh(settings)
        return settings
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update monitoring settings"
        )


# Monitoring Alerts endpoints
@router.get("/alerts", response_model=list[MonitoringAlertResponse])
async def get_monitoring_alerts(
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Get all monitoring alerts for a user"""
    try:
        # Convert Clerk user ID to database UUID
        db_user_id = await get_db_user_id(user_id, db)
        
        result = await db.execute(
            select(MonitoringAlert).where(MonitoringAlert.user_id == db_user_id)
        )
        alerts = result.scalars().all()
        return alerts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch monitoring alerts"
        )


@router.post("/alerts", response_model=MonitoringAlertResponse)
async def create_monitoring_alert(
    alert_data: MonitoringAlertCreate,
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Create a new monitoring alert"""
    try:
        # Convert Clerk user ID to database UUID
        db_user_id = await get_db_user_id(user_id, db)
        
        alert = MonitoringAlert(
            user_id=db_user_id,
            **alert_data.dict()
        )
        db.add(alert)
        await db.commit()
        await db.refresh(alert)
        return alert
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create monitoring alert"
        )


@router.put("/alerts/{alert_id}/read")
async def mark_alert_as_read(
    alert_id: str,
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Mark a monitoring alert as read"""
    try:
        # Convert Clerk user ID to database UUID
        db_user_id = await get_db_user_id(user_id, db)
        
        result = await db.execute(
            select(MonitoringAlert).where(
                MonitoringAlert.id == alert_id,
                MonitoringAlert.user_id == db_user_id
            )
        )
        alert = result.scalar_one_or_none()
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Monitoring alert not found"
            )
        
        alert.is_read = True
        await db.commit()
        return {"message": "Alert marked as read"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark alert as read"
        )


# Agent monitoring endpoints
@router.post("/start-continuous-monitoring")
async def start_continuous_monitoring(
    user_id: str = Depends(get_user_id_from_header)
) -> Dict[str, Any]:
    """Start continuous monitoring for all user's competitors"""
    try:
        if monitoring_scheduler.running:
            return {
                "success": True,
                "message": "Continuous monitoring is already running",
                "status": monitoring_scheduler.get_status()
            }
        
        # Start the scheduler in background
        import asyncio
        asyncio.create_task(monitoring_scheduler.start())
        
        return {
            "success": True,
            "message": "Continuous monitoring started",
            "status": monitoring_scheduler.get_status()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start continuous monitoring: {str(e)}"
        )


@router.post("/stop-continuous-monitoring")
async def stop_continuous_monitoring(
    user_id: str = Depends(get_user_id_from_header)
) -> Dict[str, Any]:
    """Stop continuous monitoring"""
    try:
        await monitoring_scheduler.stop()
        return {
            "success": True,
            "message": "Continuous monitoring stopped"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop continuous monitoring: {str(e)}"
        )


@router.get("/monitoring-status")
async def get_monitoring_status(
    user_id: str = Depends(get_user_id_from_header)
) -> Dict[str, Any]:
    """Get the current status of the monitoring system"""
    try:
        return {
            "success": True,
            "status": monitoring_scheduler.get_status()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get monitoring status: {str(e)}"
        )


@router.post("/run-monitoring/{competitor_id}")
async def run_monitoring_for_competitor(
    competitor_id: str,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Run monitoring for a specific competitor"""
    try:
        # Convert Clerk user ID to database UUID
        db_user_id = await get_db_user_id(user_id, db)
        
        # Verify competitor belongs to user
        from app.models.competitor import Competitor
        result = await db.execute(
            select(Competitor).where(
                Competitor.id == competitor_id,
                Competitor.user_id == db_user_id
            )
        )
        competitor = result.scalar_one_or_none()
        
        if not competitor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Competitor not found"
            )
        
        # Trigger immediate scan
        scan_result = await monitoring_scheduler.trigger_immediate_scan(competitor_id)
        
        return {
            "success": scan_result["success"],
            "message": scan_result["message"],
            "competitor_id": competitor_id,
            "competitor_name": competitor.name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run monitoring: {str(e)}"
        )


@router.post("/run-monitoring-all")
async def run_monitoring_for_all_competitors(
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Run monitoring for all user's active competitors"""
    try:
        logger.info(f"🚀 Starting monitoring for all competitors for user: {user_id}")
        
        # Convert Clerk user ID to database UUID
        db_user_id = await get_db_user_id(user_id, db)
        
        # Verify user has competitors
        from app.models.competitor import Competitor
        competitors_result = await db.execute(
            select(Competitor).where(
                Competitor.user_id == db_user_id,
                Competitor.status == 'active'
            )
        )
        competitors = competitors_result.scalars().all()
        
        if not competitors:
            return {
                "success": False,
                "message": "No active competitors found for this user",
                "total_competitors": 0
            }
        
        logger.info(f"📊 Found {len(competitors)} active competitors for user {user_id}")
        
        # Initialize the monitoring service
        monitoring_service = SimpleMonitoringService(db)
        
        try:
            # Run monitoring for all competitors
            result = await monitoring_service.run_monitoring_for_all_active_competitors(user_id)
            
            logger.info(f"✅ Monitoring completed for all competitors. Result: {result}")
            
            return {
                "success": True,
                "message": f"Monitoring completed for {result.get('competitors_scanned', 0)} competitors",
                "total_competitors": result.get("total_competitors", 0),
                "competitors_scanned": result.get("competitors_scanned", 0),
                "successful_scans": result.get("successful_scans", 0),
                "failed_scans": result.get("failed_scans", 0),
                "details": result
            }
            
        finally:
            # Always close the service
            await monitoring_service.close()
        
    except Exception as e:
        logger.error(f"❌ Error running monitoring for all competitors: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run monitoring for all competitors: {str(e)}"
        )


@router.post("/test-agent/{competitor_id}")
async def test_agent_workflow(
    competitor_id: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Test the agent workflow for a specific competitor"""
    try:
        from app.services.monitoring import SimpleMonitoringService
        
        monitoring_service = SimpleMonitoringService()
        logger.info(f"Testing simple monitoring service for competitor {competitor_id}")
        
        result = await monitoring_service.run_monitoring_for_competitor(competitor_id)
        
        return {
            "success": True,
            "message": "Simple monitoring service test completed",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error testing simple monitoring service: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test simple monitoring service: {str(e)}"
        )


@router.post("/create-test-competitor")
async def create_test_competitor(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Create a test Nike competitor for testing the agent workflow"""
    try:
        from app.models.competitor import Competitor
        from uuid import uuid4
        
        # Check if Nike already exists
        result = await db.execute(
            select(Competitor).where(Competitor.name == "Nike")
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            return {
                "success": True,
                "message": "Nike competitor already exists",
                "competitor_id": str(existing.id),
                "competitor_name": existing.name
            }
        
        # Create Nike competitor
        nike_competitor = Competitor(
            id=str(uuid4()),
            user_id="test_user_123",  # Test user ID
            name="Nike",
            description="Athletic footwear and apparel company",
            website_url="https://www.nike.com",
            social_media_handles={
                "youtube": "@nike",
                "instagram": "@nike",
                "facebook": "@nike",
                "twitter": "@nike"
            },
            industry="Sports & Athletics",
            status="active",
            scan_frequency_minutes=60
        )
        
        db.add(nike_competitor)
        await db.commit()
        await db.refresh(nike_competitor)
        
        logger.info(f"Created test Nike competitor with ID: {nike_competitor.id}")
        
        return {
            "success": True,
            "message": "Test Nike competitor created successfully",
            "competitor_id": str(nike_competitor.id),
            "competitor_name": nike_competitor.name
        }
        
    except Exception as e:
        logger.error(f"Error creating test competitor: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create test competitor: {str(e)}"
        )



@router.post("/test-youtube-agent")
async def test_youtube_agent(
    competitor_id: str,
    youtube_handle: str = "@nike",
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Test the YouTube agent directly"""
    try:
        from app.services.monitoring.agents.sub_agents.youtube_agent import YouTubeAgent
        
        logger.info(f"Testing YouTube agent for competitor {competitor_id} with handle {youtube_handle}")
        
        youtube_agent = YouTubeAgent()
        result = await youtube_agent.analyze_competitor(competitor_id, youtube_handle)
        
        return {
            "success": True,
            "message": "YouTube agent test completed",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error testing YouTube agent: {e}")
        return {
            "success": False,
            "message": f"YouTube agent test failed: {str(e)}",
            "error": str(e),
            "error_type": type(e).__name__
        }


@router.post("/test-supervisor-agent")
async def test_supervisor_agent(
    competitor_id: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Test the simple monitoring service directly"""
    try:
        from app.services.monitoring import SimpleMonitoringService
        
        logger.info(f"Testing simple monitoring service for competitor {competitor_id}")
        
        monitoring_service = SimpleMonitoringService()
        result = await monitoring_service.run_monitoring_for_competitor(competitor_id)
        
        return {
            "success": True,
            "message": "Simple monitoring service test completed",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error testing simple monitoring service: {e}")
        return {
            "success": False,
            "message": f"Simple monitoring service test failed: {str(e)}",
            "error": str(e),
            "error_type": type(e).__name__
        }


@router.post("/test-agent-workflow")
async def test_agent_workflow(
    competitor_name: str = "Nike",
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Test the complete agent workflow with a competitor by name"""
    try:
        from app.models.competitor import Competitor
        from app.services.monitoring import SimpleMonitoringService
        
        # Find competitor by name
        result = await db.execute(
            select(Competitor).where(Competitor.name == competitor_name)
        )
        competitor = result.scalar_one_or_none()
        
        if not competitor:
            return {
                "success": False,
                "message": f"Competitor '{competitor_name}' not found. Use /create-test-competitor first."
            }
        
        logger.info(f"Testing agent workflow for competitor: {competitor.name} (ID: {competitor.id})")
        
        # Test simple monitoring service instead of supervisor agent
        monitoring_service = SimpleMonitoringService()
        result = await monitoring_service.run_monitoring_for_competitor(str(competitor.id))
        
        return {
            "success": True,
            "message": "Agent workflow test completed",
            "competitor": {
                "id": str(competitor.id),
                "name": competitor.name,
                "industry": competitor.industry
            },
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error testing agent workflow: {e}")
        return {
            "success": False,
            "message": f"Agent workflow test failed: {str(e)}",
            "error": str(e),
            "error_type": type(e).__name__
        }


@router.get("/monitoring-stats")
async def get_monitoring_stats(
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get monitoring statistics for the user"""
    try:
        logger.info(f"Getting monitoring stats for Clerk user ID: {user_id}")
        
        # Convert Clerk user ID to database UUID
        db_user_id = await get_db_user_id(user_id, db)
        logger.info(f"Converted to database user ID: {db_user_id} (type: {type(db_user_id)})")
        
        monitoring_service = MonitoringService(db)
        stats = await monitoring_service.get_monitoring_stats(db_user_id)
        
        return {
            "success": True,
            "stats": stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get monitoring stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get monitoring stats: {str(e)}"
        )


@router.get("/monitoring-data")
async def get_monitoring_data(
    user_id: str = Depends(get_user_id_from_header),
    competitor_id: str = None,
    platform: str = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get monitoring data for the user's competitors"""
    try:
        from app.models.monitoring import MonitoringData
        from app.models.competitor import Competitor
        
        logger.info(f"Getting monitoring data for Clerk user ID: {user_id}")
        
        # Convert Clerk user ID to database UUID
        db_user_id = await get_db_user_id(user_id, db)
        logger.info(f"Converted to database user ID: {db_user_id}")
        
        # Build query
        query = select(MonitoringData).join(
            Competitor, MonitoringData.competitor_id == Competitor.id
        ).where(Competitor.user_id == db_user_id)
        
        # Add optional filters
        if competitor_id:
            query = query.where(MonitoringData.competitor_id == competitor_id)
        if platform:
            query = query.where(MonitoringData.platform == platform)
        
        # Order by detection time and limit
        query = query.order_by(MonitoringData.detected_at.desc()).limit(limit)
        
        result = await db.execute(query)
        monitoring_data = result.scalars().all()
        
        # Convert to serializable format
        data_list = []
        for data in monitoring_data:
            data_dict = {
                "id": str(data.id),
                "competitor_id": str(data.competitor_id),
                "platform": data.platform,
                "post_id": data.post_id,
                "post_url": data.post_url,
                "content_text": data.content_text,
                "content_hash": data.content_hash,
                "media_urls": data.media_urls,
                "engagement_metrics": data.engagement_metrics,
                "author_username": data.author_username,
                "author_display_name": data.author_display_name,
                "author_avatar_url": data.author_avatar_url,
                "post_type": data.post_type,
                "language": data.language,
                "sentiment_score": float(data.sentiment_score) if data.sentiment_score else None,
                "detected_at": data.detected_at.isoformat() if data.detected_at else None,
                "posted_at": data.posted_at.isoformat() if data.posted_at else None,
                "is_new_post": data.is_new_post,
                "is_content_change": data.is_content_change,
                "previous_content_hash": data.previous_content_hash
            }
            data_list.append(data_dict)
        
        logger.info(f"Found {len(data_list)} monitoring data records")
        
        return {
            "success": True,
            "data": data_list,
            "total_records": len(data_list),
            "filters": {
                "competitor_id": competitor_id,
                "platform": platform,
                "limit": limit
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get monitoring data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get monitoring data: {str(e)}"
        )


@router.post("/scan-platform/{platform}", response_model=PlatformScanResponse)
async def scan_specific_platform(
    platform: str,
    request: PlatformScanRequest,
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Run monitoring for a specific platform and competitor"""
    try:
        competitor_id = request.competitor_id
        logger.info(f"Starting {platform} scan for competitor {competitor_id}")
        
        # Convert Clerk user ID to database UUID
        db_user_id = await get_db_user_id(user_id, db)
        
        # Initialize the simple monitoring service
        monitoring_service = SimpleMonitoringService()
        
        try:
            # Run platform-specific monitoring
            result = await monitoring_service.run_platform_specific_monitoring(competitor_id, platform)
            
            logger.info(f"✅ {platform} scan completed for competitor {competitor_id}")
            
            return PlatformScanResponse(
                success=True,
                platform=platform,
                competitor_id=competitor_id,
                result=result,
                message=f"{platform} scan completed successfully"
            )
            
        finally:
            # Always close the service
            await monitoring_service.close()
            
    except Exception as e:
        logger.error(f"❌ Error in {platform} scan for competitor {competitor_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run {platform} scan: {str(e)}"
        )


@router.get("/scanning-progress")
async def get_scanning_progress(
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get real-time scanning progress for all user's competitors"""
    try:
        # Convert Clerk user ID to database UUID
        db_user_id = await get_db_user_id(user_id, db)
        
        # Get all competitors and their scanning status
        from app.models.competitor import Competitor
        from app.models.monitoring import CompetitorMonitoringStatus
        
        # Get competitors with their monitoring status
        query = select(Competitor, CompetitorMonitoringStatus).outerjoin(
            CompetitorMonitoringStatus, 
            Competitor.id == CompetitorMonitoringStatus.competitor_id
        ).where(Competitor.user_id == db_user_id)
        
        result = await db.execute(query)
        rows = result.all()
        
        scanning_progress = []
        total_competitors = len(rows)
        currently_scanning = 0
        completed_scans = 0
        failed_scans = 0
        
        for competitor, status in rows:
            if status and status.is_scanning:
                currently_scanning += 1
                scan_status = "scanning"
            elif status and status.last_successful_scan:
                if status.last_failed_scan and status.last_failed_scan > status.last_successful_scan:
                    failed_scans += 1
                    scan_status = "failed"
                else:
                    completed_scans += 1
                    scan_status = "completed"
            else:
                scan_status = "not_started"
            
            scanning_progress.append({
                "competitor_id": str(competitor.id),
                "competitor_name": competitor.name,
                "status": scan_status,
                "last_scan": status.last_successful_scan.isoformat() if status and status.last_successful_scan else None,
                "last_failed_scan": status.last_failed_scan.isoformat() if status and status.last_failed_scan else None,
                "error_message": status.scan_error_message if status else None,
                "scan_started_at": status.scan_started_at.isoformat() if status and status.scan_started_at else None
            })
        
        return {
            "success": True,
            "total_competitors": total_competitors,
            "currently_scanning": currently_scanning,
            "completed_scans": completed_scans,
            "failed_scans": failed_scans,
            "not_started": total_competitors - currently_scanning - completed_scans - failed_scans,
            "progress_percentage": (completed_scans / total_competitors * 100) if total_competitors > 0 else 0,
            "competitors": scanning_progress
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting scanning progress: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get scanning progress: {str(e)}"
        )


@router.post("/scan-competitor/{competitor_id}")
async def scan_specific_competitor(
    competitor_id: str,
    platforms: List[str] = None,
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Run monitoring for a specific competitor with optional platform selection"""
    try:
        logger.info(f"Starting scan for competitor {competitor_id} with platforms: {platforms or 'all'}")
        
        # Convert Clerk user ID to database UUID
        db_user_id = await get_db_user_id(user_id, db)
        
        # Initialize the simple monitoring service
        monitoring_service = SimpleMonitoringService(db)
        
        try:
            # Run competitor monitoring
            result = await monitoring_service.run_monitoring_for_competitor(competitor_id, platforms)
            
            logger.info(f"✅ Scan completed for competitor {competitor_id}")
            
            return {
                "success": True,
                "competitor_id": competitor_id,
                "result": result
            }
            
        finally:
            # Always close the service
            await monitoring_service.close()
            
    except Exception as e:
        logger.error(f"❌ Error in scan for competitor {competitor_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run competitor scan: {str(e)}"
        )
