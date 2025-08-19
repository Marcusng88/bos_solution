"""
Supabase Client for Monitoring Agents
Direct database operations without SQLAlchemy sessions
"""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import asyncio
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class SupabaseMonitoringClient:
    """Direct Supabase client for monitoring operations"""
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        logger.info("✅ Supabase monitoring client initialized")
    
    async def get_competitor_details(self, competitor_id: str) -> Optional[Dict[str, Any]]:
        """Get competitor details by ID"""
        try:
            response = self.client.table('competitors').select('*').eq('id', competitor_id).execute()
            
            if response.data and len(response.data) > 0:
                competitor = response.data[0]
                logger.info(f"✅ Retrieved competitor details for {competitor_id}: {competitor.get('name', 'Unknown')}")
                return competitor
            else:
                logger.warning(f"⚠️ No competitor found with ID: {competitor_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting competitor details for {competitor_id}: {e}")
            return None
    
    async def get_competitors_due_for_scan(self) -> List[Dict[str, Any]]:
        """Get all active competitors that are due for scanning"""
        try:
            current_time = datetime.utcnow()
            
            # Get all active competitors
            response = self.client.table('competitors').select('*').eq('status', 'active').execute()
            
            if not response.data:
                return []
            
            competitors_due = []
            
            for competitor in response.data:
                try:
                    # Check if due for scan (24 hours since last scan)
                    last_scan_at = competitor.get('last_scan_at')
                    
                    if not last_scan_at:
                        # Never scanned before
                        competitors_due.append(competitor)
                        continue
                    
                    # Parse last scan time
                    if isinstance(last_scan_at, str):
                        last_scan_time = datetime.fromisoformat(last_scan_at.replace('Z', '+00:00'))
                    else:
                        last_scan_time = last_scan_at
                    
                    # Check if 24 hours have passed
                    next_scan_time = last_scan_time + timedelta(hours=24)
                    
                    if current_time >= next_scan_time:
                        competitors_due.append(competitor)
                        
                except Exception as e:
                    logger.error(f"❌ Error processing competitor {competitor.get('id')}: {e}")
                    continue
            
            logger.info(f"✅ Found {len(competitors_due)} competitors due for scanning")
            return competitors_due
            
        except Exception as e:
            logger.error(f"❌ Error getting competitors due for scan: {e}")
            return []
    
    async def save_monitoring_data(self, monitoring_data: Dict[str, Any]) -> Optional[str]:
        """Save monitoring data to database"""
        try:
            response = self.client.table('monitoring_data').insert(monitoring_data).execute()
            
            if response.data and len(response.data) > 0:
                data_id = response.data[0]['id']
                logger.info(f"✅ Saved monitoring data with ID: {data_id}")
                return data_id
            else:
                logger.error("❌ Failed to save monitoring data - no response data")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error saving monitoring data: {e}")
            return None
    
    async def create_alert(self, alert_data: Dict[str, Any]) -> Optional[str]:
        """Create a monitoring alert"""
        try:
            response = self.client.table('monitoring_alerts').insert(alert_data).execute()
            
            if response.data and len(response.data) > 0:
                alert_id = response.data[0]['id']
                logger.info(f"✅ Created alert with ID: {alert_id}")
                return alert_id
            else:
                logger.error("❌ Failed to create alert - no response data")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error creating alert: {e}")
            return None
    
    async def update_competitor_scan_time(self, competitor_id: str) -> bool:
        """Update competitor's last scan time"""
        try:
            current_time = datetime.utcnow().isoformat()
            
            response = self.client.table('competitors').update({
                'last_scan_at': current_time,
                'updated_at': current_time
            }).eq('id', competitor_id).execute()
            
            if response.data and len(response.data) > 0:
                logger.info(f"✅ Updated scan time for competitor {competitor_id}")
                return True
            else:
                logger.warning(f"⚠️ No competitor updated for ID: {competitor_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error updating competitor scan time: {e}")
            return False
    
    async def get_monitoring_stats(self, user_id: str) -> Dict[str, int]:
        """Get monitoring statistics for a user"""
        try:
            stats = {
                "total_competitors": 0,
                "total_monitoring_data": 0,
                "unread_alerts": 0,
                "recent_activity_24h": 0
            }
            
            # Get total competitors
            competitors_response = self.client.table('competitors').select('id', count='exact').eq('user_id', user_id).execute()
            stats["total_competitors"] = competitors_response.count or 0
            
            # Get total monitoring data
            data_response = self.client.table('monitoring_data').select('id', count='exact').execute()
            stats["total_monitoring_data"] = data_response.count or 0
            
            # Get unread alerts
            alerts_response = self.client.table('monitoring_alerts').select('id', count='exact').eq('user_id', user_id).eq('is_read', False).execute()
            stats["unread_alerts"] = alerts_response.count or 0
            
            # Get recent activity (last 24 hours)
            yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()
            recent_response = self.client.table('monitoring_data').select('id', count='exact').gte('detected_at', yesterday).execute()
            stats["recent_activity_24h"] = recent_response.count or 0
            
            logger.info(f"✅ Retrieved monitoring stats: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error getting monitoring stats: {e}")
            return {
                "total_competitors": 0,
                "total_monitoring_data": 0,
                "unread_alerts": 0,
                "recent_activity_24h": 0
            }
    
    async def check_existing_post(self, competitor_id: str, platform: str, post_id: str) -> Optional[Dict[str, Any]]:
        """Check if a post already exists in monitoring data"""
        try:
            response = self.client.table('monitoring_data').select('*').eq('competitor_id', competitor_id).eq('platform', platform).eq('post_id', post_id).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
            
        except Exception as e:
            logger.error(f"❌ Error checking existing post: {e}")
            return None
    
    async def update_post_content(self, data_id: str, updated_data: Dict[str, Any]) -> bool:
        """Update existing post content"""
        try:
            response = self.client.table('monitoring_data').update(updated_data).eq('id', data_id).execute()
            
            if response.data and len(response.data) > 0:
                logger.info(f"✅ Updated post content for ID: {data_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ Error updating post content: {e}")
            return False


# Global client instance
supabase_client = SupabaseMonitoringClient()
