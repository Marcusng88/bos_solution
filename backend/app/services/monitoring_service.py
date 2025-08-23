"""
Monitoring service for business logic
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.schemas.monitoring import MonitoringDataCreate, MonitoringAlertCreate
import hashlib
import logging

logger = logging.getLogger(__name__)


class MonitoringService:
    """Service for monitoring operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def process_social_media_post(
        self, 
        competitor_id: str, 
        platform: str, 
        post_data: Dict[str, Any]
    ) -> Optional[MonitoringData]:
        """Process a new social media post and detect changes"""
        try:
            # Generate content hash
            content_text = post_data.get("content_text", "")
            content_hash = hashlib.md5(content_text.encode()).hexdigest()
            
            # Check if this post already exists
            existing_post = await self.db.execute(
                select(MonitoringData).where(
                    and_(
                        MonitoringData.competitor_id == competitor_id,
                        MonitoringData.platform == platform,
                        MonitoringData.post_id == post_data.get("post_id")
                    )
                )
            )
            
            existing = existing_post.scalar_one_or_none()
            
            if existing:
                # Check if content has changed
                if existing.content_hash != content_hash:
                    # Content has changed
                    existing.is_content_change = True
                    existing.previous_content_hash = existing.content_hash
                    existing.content_hash = content_hash
                    existing.content_text = content_text
                    existing.updated_at = datetime.utcnow()
                    
                    # Create alert for content change
                    await self._create_content_change_alert(existing)
                    
                    await self.db.commit()
                    await self.db.refresh(existing)
                    return existing
                else:
                    # No changes, return existing
                    return existing
            else:
                # New post
                new_post = MonitoringData(
                    competitor_id=competitor_id,
                    platform=platform,
                    content_hash=content_hash,
                    **post_data
                )
                
                self.db.add(new_post)
                await self.db.commit()
                await self.db.refresh(new_post)
                
                # Create alert for new post
                await self._create_new_post_alert(new_post)
                
                return new_post
                
        except Exception as e:
            logger.error(f"Error processing social media post: {e}")
            await self.db.rollback()
            raise
    
    async def _create_content_change_alert(self, monitoring_data: MonitoringData):
        """Create alert for content change"""
        try:
            alert = MonitoringAlert(
                user_id=monitoring_data.competitor.user_id,
                competitor_id=monitoring_data.competitor_id,
                monitoring_data_id=monitoring_data.id,
                alert_type="content_change",
                priority="medium",
                title=f"Content Change Detected - {monitoring_data.platform}",
                message=f"Content has been modified for {monitoring_data.competitor.name} on {monitoring_data.platform}",
                alert_metadata={
                    "platform": monitoring_data.platform,
                    "post_id": monitoring_data.post_id,
                    "change_type": "content_modification"
                }
            )
            
            self.db.add(alert)
            
        except Exception as e:
            logger.error(f"Error creating content change alert: {e}")
    
    async def _create_new_post_alert(self, monitoring_data: MonitoringData):
        """Create alert for new post"""
        try:
            alert = MonitoringAlert(
                user_id=monitoring_data.competitor.user_id,
                competitor_id=monitoring_data.competitor_id,
                monitoring_data_id=monitoring_data.id,
                alert_type="new_post",
                priority="low",
                title=f"New Post Detected - {monitoring_data.platform}",
                message=f"New post detected for {monitoring_data.competitor.name} on {monitoring_data.platform}",
                alert_metadata={
                    "platform": monitoring_data.platform,
                    "post_id": monitoring_data.post_id,
                    "content_preview": monitoring_data.content_text[:100] if monitoring_data.content_text else None
                }
            )
            
            self.db.add(alert)
            
        except Exception as e:
            logger.error(f"Error creating new post alert: {e}")
    
    async def get_monitoring_stats(self, user_id: str) -> Dict[str, int]:
        """Get monitoring statistics for a user"""
        try:
            # Get total competitors
            competitors_result = await self.db.execute(
                select(Competitor).where(Competitor.user_id == user_id)
            )
            total_competitors = len(competitors_result.scalars().all())
            
            # Get total monitoring data
            data_result = await self.db.execute(
                select(MonitoringData).join(
                    Competitor, MonitoringData.competitor_id == Competitor.id
                ).where(Competitor.user_id == user_id)
            )
            total_data = len(data_result.scalars().all())
            
            # Get unread alerts
            alerts_result = await self.db.execute(
                select(MonitoringAlert).where(
                    MonitoringAlert.user_id == user_id,
                    MonitoringAlert.is_read == False
                )
            )
            unread_alerts = len(alerts_result.scalars().all())
            
            # Get recent activity (last 24 hours)
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_data_result = await self.db.execute(
                select(MonitoringData).join(
                    Competitor, MonitoringData.competitor_id == Competitor.id
                ).where(
                    Competitor.user_id == user_id,
                    MonitoringData.detected_at >= yesterday
                )
            )
            recent_activity = len(recent_data_result.scalars().all())
            
            return {
                "total_competitors": total_competitors,
                "total_monitoring_data": total_data,
                "unread_alerts": unread_alerts,
                "recent_activity_24h": recent_activity
            }
            
        except Exception as e:
            logger.error(f"Error getting monitoring stats: {e}")
            raise
