"""
Core Monitoring service for business logic
Updated for Supabase integration without SQLAlchemy
"""

import sys
import asyncio
import platform
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
import hashlib
import logging
import sys

# Import and setup Windows compatibility early
# from app.core.windows_compatibility import setup_windows_compatibility
# setup_windows_compatibility()

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
    """Service for monitoring operations using Supabase"""
    
    def __init__(self, supabase_client):
        self.db = supabase_client
        logger.info("🔧 MonitoringService initialized with Supabase client")
    
    async def process_social_media_post(
        self, 
        competitor_id: str, 
        platform: str, 
        post_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Process a new social media post and detect changes"""
        try:
            logger.info(f"📝 Processing {platform} post for competitor {competitor_id}")
            logger.info(f"   📊 Post data: {post_data.get('post_type', 'unknown')} | {post_data.get('author_username', 'unknown')}")
            
            # Generate content hash
            content_text = post_data.get("content_text", "")
            content_hash = hashlib.md5(content_text.encode()).hexdigest()
            logger.debug(f"   🔐 Content hash generated: {content_hash[:8]}...")
            
            # Check if this post already exists by querying monitoring data
            existing_posts = await self.db.get_monitoring_data_by_competitor(competitor_id, limit=1000)
            
            # Find existing post by post_id and platform
            existing = None
            for post in existing_posts:
                if (post.get("post_id") == post_data.get("post_id") and 
                    post.get("platform") == platform):
                    existing = post
                    break
            
            if existing:
                logger.info(f"   🔍 Existing post found, checking for changes...")
                # Check if content has changed
                if existing.get("content_hash") != content_hash:
                    logger.info(f"   ✏️  Content change detected!")
                    # Content has changed - update the record
                    update_data = {
                        "is_content_change": True,
                        "previous_content_hash": existing.get("content_hash"),
                        "content_hash": content_hash,
                        "content_text": content_text,
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                    
                    # Update the existing record
                    updated_post = await self.db.update_monitoring_data(existing["id"], update_data)
                    if updated_post:
                        logger.info(f"   ✅ Content change processed and stored (no alert created)")
                        return updated_post
                    else:
                        logger.error(f"   ❌ Failed to update existing post")
                        return None
                else:
                    logger.info(f"   ✅ No changes detected, returning existing post")
                    return existing
            else:
                logger.info(f"   🆕 New post detected, creating record...")
                # New post - prepare data for insertion
                monitoring_data = {
                    "competitor_id": competitor_id,
                    "platform": platform,
                    "content_hash": content_hash,
                    "is_new_post": True,
                    **post_data
                }
                
                # Save to database
                new_post_id = await self.db.save_monitoring_data(monitoring_data)
                
                if new_post_id:
                    # Create alert for new post
                    await self._create_new_post_alert(competitor_id, new_post_id, platform, post_data)
                    
                    logger.info(f"   ✅ New post created with ID: {new_post_id}")
                    
                    # Get the created post data
                    created_post = await self.db.get_monitoring_data_by_id(new_post_id)
                    return created_post
                else:
                    logger.error(f"   ❌ Failed to create new post")
                    return None
                
        except Exception as e:
            logger.error(f"❌ Error processing social media post: {e}")
            raise
    
    async def _create_website_change_alert(self, competitor_id: str, monitoring_data_id: str, platform: str):
        """Create alert for website layout/design changes"""
        try:
            logger.info(f"   🚨 Creating website change alert...")
            
            # Get the competitor to access user_id and name
            competitor = await self.db.get_competitor_by_id(competitor_id)
            
            if not competitor:
                logger.error(f"   ❌ Competitor not found for monitoring data {monitoring_data_id}")
                return
            
            alert_data = {
                "user_id": competitor.get("user_id"),
                "competitor_id": competitor_id,
                "monitoring_data_id": monitoring_data_id,
                "alert_type": "website_change",
                "priority": "medium",
                "title": f"Website Change Detected - {platform}",
                "message": f"Website layout or design has been modified for {competitor.get('name', 'Unknown')}",
                "alert_metadata": {
                    "platform": platform,
                    "change_type": "website_layout_modification"
                }
            }
            
            alert_id = await self.db.create_monitoring_alert(alert_data)
            if alert_id:
                logger.info(f"   ✅ Website change alert created")
            else:
                logger.error(f"   ❌ Failed to create website change alert")
            
        except Exception as e:
            logger.error(f"❌ Error creating website change alert: {e}")
    
    async def _create_new_post_alert(self, competitor_id: str, monitoring_data_id: str, platform: str, post_data: Dict[str, Any]):
        """Create alert for new post"""
        try:
            logger.info(f"   🚨 Creating new post alert...")
            
            # Get the competitor to access user_id and name
            competitor = await self.db.get_competitor_by_id(competitor_id)
            
            if not competitor:
                logger.error(f"   ❌ Competitor not found for monitoring data {monitoring_data_id}")
                return
            
            alert_data = {
                "user_id": competitor.get("user_id"),
                "competitor_id": competitor_id,
                "monitoring_data_id": monitoring_data_id,
                "alert_type": "new_post",
                "priority": "low",
                "title": f"New Post Detected - {platform}",
                "message": f"New post detected for {competitor.get('name', 'Unknown')} on {platform}",
                "alert_metadata": {
                    "platform": platform,
                    "post_id": post_data.get("post_id"),
                    "content_preview": post_data.get("content_text", "")[:100] if post_data.get("content_text") else None
                }
            }
            
            alert_id = await self.db.create_monitoring_alert(alert_data)
            if alert_id:
                logger.info(f"   ✅ New post alert created")
            else:
                logger.error(f"   ❌ Failed to create new post alert")
            
        except Exception as e:
            logger.error(f"❌ Error creating new post alert: {e}")
    
    async def get_monitoring_stats(self, user_id: str) -> Dict[str, int]:
        """Get monitoring statistics for a user"""
        try:
            logger.info(f"📊 Getting monitoring stats for user: {user_id}")
            
            # Log the type and value of user_id for debugging
            logger.debug(f"   🔍 User ID type: {type(user_id)}, value: {user_id}")
            
            # Ensure user_id is provided
            if not user_id:
                raise ValueError("user_id is required")
            
            # user_id should be a string (clerk_id) since competitors.user_id references users.clerk_id
            if not isinstance(user_id, str):
                raise ValueError(f"user_id must be a string (clerk_id), got {type(user_id)}")
            
            logger.info(f"   🔍 Querying database for user {user_id}")
            
            # Get total competitors
            competitors = await self.db.get_competitors_by_user(user_id)
            total_competitors = len(competitors)
            logger.info(f"   👥 Found {total_competitors} competitors")
            
            # Get total monitoring data across all competitors
            total_data = 0
            for competitor in competitors:
                competitor_data = await self.db.get_monitoring_data_by_competitor(competitor["id"], limit=10000)
                total_data += len(competitor_data)
            
            logger.info(f"   📝 Found {total_data} monitoring data records")
            
            # Note: Alerts functionality would need to be implemented in the Supabase client
            # For now, return 0 for alerts
            unread_alerts = 0
            logger.info(f"   🚨 Found {unread_alerts} unread alerts (not implemented yet)")
            
            # Get recent activity (last 24 hours) - would need date filtering in Supabase client
            recent_activity = 0
            logger.info(f"   ⏰ Found {recent_activity} recent activities (24h) (not implemented yet)")
            
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
    ) -> Optional[str]:
        """Create a web alert for monitoring events"""
        try:
            logger.info(f"🚨 Creating web alert: {alert_type} - {title}")
            
            # user_id should be a string (clerk_id) since MonitoringAlert.user_id references users.clerk_id
            if not isinstance(user_id, str):
                raise ValueError(f"user_id must be a string (clerk_id), got {type(user_id)}")
            
            # Create the alert data
            alert_data = {
                "user_id": user_id,
                "competitor_id": competitor_id,
                "monitoring_data_id": monitoring_data_id,
                "alert_type": alert_type,
                "priority": priority,
                "title": title,
                "message": message,
                "alert_metadata": alert_metadata or {},
                "is_read": False
            }
            
            # Create alert using Supabase client
            alert_id = await self.db.create_monitoring_alert(alert_data)
            
            if alert_id:
                logger.info(f"✅ Web alert created successfully with ID: {alert_id}")
                return alert_id
            else:
                logger.error(f"❌ Failed to create web alert")
                return None
            
        except Exception as e:
            logger.error(f"❌ Error creating web alert: {e}")
            raise
