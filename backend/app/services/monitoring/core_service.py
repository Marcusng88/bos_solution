"""
Core Monitoring service for business logic
"""

import sys
import asyncio
import platform
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.monitoring import MonitoringData, MonitoringAlert, CompetitorMonitoringStatus
from app.models.competitor import Competitor
from app.schemas.monitoring import MonitoringDataCreate, MonitoringAlertCreate
import hashlib
import logging
import sys

# Import and setup Windows compatibility early
from app.core.windows_compatibility import setup_windows_compatibility
setup_windows_compatibility()

# Configure logging to output to terminal with colors and formatting
logger = logging.getLogger(__name__)

# Create a custom formatter for terminal output
class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for terminal output"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Add color to level name
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        # Add timestamp and format
        timestamp = datetime.now().strftime("%H:%M:%S")
        return f"[{timestamp}] {record.levelname}: {record.getMessage()}"

# Configure terminal logging
def setup_terminal_logging():
    """Setup terminal logging with colors and formatting"""
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Set formatter
    formatter = ColoredFormatter()
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)
    
    # Prevent duplicate logs
    logger.propagate = False

# Setup terminal logging
setup_terminal_logging()

class MonitoringService:
    """Service for monitoring operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        logger.info("🔧 MonitoringService initialized")
    
    async def process_social_media_post(
        self, 
        competitor_id: str, 
        platform: str, 
        post_data: Dict[str, Any]
    ) -> Optional[MonitoringData]:
        """Process a new social media post and detect changes"""
        try:
            logger.info(f"📝 Processing {platform} post for competitor {competitor_id}")
            logger.info(f"   📊 Post data: {post_data.get('post_type', 'unknown')} | {post_data.get('author_username', 'unknown')}")
            
            # Generate content hash
            content_text = post_data.get("content_text", "")
            content_hash = hashlib.md5(content_text.encode()).hexdigest()
            logger.debug(f"   🔐 Content hash generated: {content_hash[:8]}...")
            
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
                logger.info(f"   🔍 Existing post found, checking for changes...")
                # Check if content has changed
                if existing.content_hash != content_hash:
                    logger.info(f"   ✏️  Content change detected!")
                    # Content has changed - update the record but don't create alerts
                    # Website change alerts will be handled by website agent when implemented
                    existing.is_content_change = True
                    existing.previous_content_hash = existing.content_hash
                    existing.content_hash = content_hash
                    existing.content_text = content_text
                    existing.updated_at = datetime.now(timezone.utc)
                    
                    await self.db.commit()
                    await self.db.refresh(existing)
                    logger.info(f"   ✅ Content change processed and stored (no alert created)")
                    return existing
                else:
                    logger.info(f"   ✅ No changes detected, returning existing post")
                    # No changes, return existing
                    return existing
            else:
                logger.info(f"   🆕 New post detected, creating record...")
                # New post - remove platform from post_data to avoid duplicate
                post_data_clean = {k: v for k, v in post_data.items() if k != 'platform'}
                new_post = MonitoringData(
                    competitor_id=competitor_id,
                    platform=platform,
                    content_hash=content_hash,
                    **post_data_clean
                )
                
                self.db.add(new_post)
                await self.db.commit()
                await self.db.refresh(new_post)
                
                # Create alert for new post
                await self._create_new_post_alert(new_post)
                
                logger.info(f"   ✅ New post created with ID: {new_post.id}")
                return new_post
                
        except Exception as e:
            logger.error(f"❌ Error processing social media post: {e}")
            await self.db.rollback()
            raise
    
    async def _create_website_change_alert(self, monitoring_data: MonitoringData):
        """Create alert for website layout/design changes (not implemented yet)"""
        try:
            logger.info(f"   🚨 Creating website change alert...")
            alert = MonitoringAlert(
                user_id=monitoring_data.competitor.user_id,
                competitor_id=monitoring_data.competitor_id,
                monitoring_data_id=monitoring_data.id,
                alert_type="website_change",
                priority="medium",
                title=f"Website Change Detected - {monitoring_data.platform}",
                message=f"Website layout or design has been modified for {monitoring_data.competitor.name}",
                alert_metadata={
                    "platform": monitoring_data.platform,
                    "post_id": monitoring_data.post_id,
                    "change_type": "website_layout_modification"
                }
            )
            
            self.db.add(alert)
            logger.info(f"   ✅ Website change alert created")
            
        except Exception as e:
            logger.error(f"❌ Error creating website change alert: {e}")
    
    async def _create_new_post_alert(self, monitoring_data: MonitoringData):
        """Create alert for new post"""
        try:
            logger.info(f"   🚨 Creating new post alert...")
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
            logger.info(f"   ✅ New post alert created")
            
        except Exception as e:
            logger.error(f"❌ Error creating new post alert: {e}")
    
    async def get_monitoring_stats(self, user_id) -> Dict[str, int]:
        """Get monitoring statistics for a user"""
        try:
            logger.info(f"📊 Getting monitoring stats for user: {user_id}")
            
            # Log the type and value of user_id for debugging
            logger.debug(f"   🔍 User ID type: {type(user_id)}, value: {user_id}")
            
            # Ensure user_id is provided
            if not user_id:
                raise ValueError("user_id is required")
            
            # Convert to string if it's a UUID object
            from uuid import UUID
            if isinstance(user_id, UUID):
                user_id_param = user_id
            elif isinstance(user_id, str):
                try:
                    # Try to parse as UUID to validate format
                    user_id_param = UUID(user_id)
                except ValueError:
                    raise ValueError(f"Invalid UUID format: {user_id}")
            else:
                raise ValueError(f"Invalid user_id type: {type(user_id)}")
            
            logger.info(f"   🔍 Querying database for user {user_id_param}")
            
            # Get total competitors
            competitors_result = await self.db.execute(
                select(Competitor).where(Competitor.user_id == user_id_param)
            )
            total_competitors = len(competitors_result.scalars().all())
            logger.info(f"   👥 Found {total_competitors} competitors")
            
            # Get total monitoring data
            data_result = await self.db.execute(
                select(MonitoringData).join(
                    Competitor, MonitoringData.competitor_id == Competitor.id
                ).where(Competitor.user_id == user_id_param)
            )
            total_data = len(data_result.scalars().all())
            logger.info(f"   📝 Found {total_data} monitoring data records")
            
            # Get unread alerts
            alerts_result = await self.db.execute(
                select(MonitoringAlert).where(
                    MonitoringAlert.user_id == user_id_param,
                    MonitoringAlert.is_read == False
                )
            )
            unread_alerts = len(alerts_result.scalars().all())
            logger.info(f"   🚨 Found {unread_alerts} unread alerts")
            
            # Get recent activity (last 24 hours)
            yesterday = datetime.now(timezone.utc) - timedelta(days=1)
            recent_data_result = await self.db.execute(
                select(MonitoringData).join(
                    Competitor, MonitoringData.competitor_id == Competitor.id
                ).where(
                    Competitor.user_id == user_id_param,
                    MonitoringData.detected_at >= yesterday
                )
            )
            recent_activity = len(recent_data_result.scalars().all())
            logger.info(f"   ⏰ Found {recent_activity} recent activities (24h)")
            
            stats = {
                "total_competitors": total_competitors,
                "total_monitoring_data": total_data,
                "unread_alerts": unread_alerts,
                "recent_activity_24h": recent_activity
            }
            
            logger.info(f"✅ Monitoring stats retrieved successfully")
            logger.info(f"   📊 Summary: {total_competitors} competitors, {total_data} data points, {unread_alerts} alerts, {recent_activity} recent")
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error getting monitoring stats for user_id {user_id}: {e}")
            raise

    async def create_alert(
        self,
        user_id: str,
        competitor_id: str,
        alert_type: str,
        title: str,
        message: str,
        priority: str = "medium",
        monitoring_data_id: Optional[str] = None,
        alert_metadata: Optional[Dict[str, Any]] = None
    ) -> MonitoringAlert:
        """Create a web alert for monitoring events"""
        try:
            logger.info(f"🚨 Creating web alert: {alert_type} - {title}")
            
            # Convert user_id to UUID if it's a string
            from uuid import UUID
            if isinstance(user_id, str):
                try:
                    user_id_param = UUID(user_id)
                except ValueError:
                    raise ValueError(f"Invalid UUID format for user_id: {user_id}")
            else:
                user_id_param = user_id
            
            # Convert competitor_id to UUID if it's a string
            if isinstance(competitor_id, str):
                try:
                    competitor_id_param = UUID(competitor_id)
                except ValueError:
                    raise ValueError(f"Invalid UUID format for competitor_id: {competitor_id}")
            else:
                competitor_id_param = competitor_id
            
            # Convert monitoring_data_id to UUID if provided and it's a string
            monitoring_data_id_param = None
            if monitoring_data_id:
                if isinstance(monitoring_data_id, str):
                    try:
                        monitoring_data_id_param = UUID(monitoring_data_id)
                    except ValueError:
                        raise ValueError(f"Invalid UUID format for monitoring_data_id: {monitoring_data_id}")
                else:
                    monitoring_data_id_param = monitoring_data_id
            
            # Create the alert
            alert = MonitoringAlert(
                user_id=user_id_param,
                competitor_id=competitor_id_param,
                monitoring_data_id=monitoring_data_id_param,
                alert_type=alert_type,
                priority=priority,
                title=title,
                message=message,
                alert_metadata=alert_metadata or {},
                is_read=False,
                created_at=datetime.now(timezone.utc)
            )
            
            self.db.add(alert)
            await self.db.commit()
            await self.db.refresh(alert)
            
            logger.info(f"✅ Web alert created successfully with ID: {alert.id}")
            return alert
            
        except Exception as e:
            logger.error(f"❌ Error creating web alert: {e}")
            await self.db.rollback()
            raise
