"""
Competitor service for business logic
Updated for Supabase integration without SQLAlchemy
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from app.schemas.competitor import CompetitorCreate, CompetitorUpdate, CompetitorResponse
import logging

logger = logging.getLogger(__name__)

class CompetitorService:
    """Service for competitor operations using Supabase"""
    
    def __init__(self, supabase_client):
        self.db = supabase_client
    
    async def get_competitors(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all competitors for a user"""
        try:
            competitors = await self.db.get_competitors_by_user(user_id)
            return competitors
        except Exception as e:
            logger.error(f"Error fetching competitors for user {user_id}: {e}")
            raise
    
    async def get_competitor(self, competitor_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific competitor for a user"""
        try:
            competitor = await self.db.get_competitor_by_id(competitor_id)
            
            if not competitor:
                return None
            
            # Verify the competitor belongs to the user
            if competitor.get("user_id") != user_id:
                logger.warning(f"Competitor {competitor_id} does not belong to user {user_id}")
                return None
            
            return competitor
        except Exception as e:
            logger.error(f"Error fetching competitor {competitor_id} for user {user_id}: {e}")
            raise
    
    async def create_competitor(self, competitor_data: CompetitorCreate, user_id: str) -> Optional[Dict[str, Any]]:
        """Create a new competitor for a user"""
        try:
            # Prepare competitor data
            competitor_dict = competitor_data.model_dump()
            competitor_dict["user_id"] = user_id
            competitor_dict["status"] = "active"
            
            # Create competitor using Supabase client
            result = await self.db.create_competitor(competitor_dict)
            
            if result:
                logger.info(f"✅ Competitor created successfully: {result.get('name')}")
                return result
            else:
                logger.error("❌ Failed to create competitor")
                return None
                
        except Exception as e:
            logger.error(f"Error creating competitor: {e}")
            raise
    
    async def update_competitor(self, competitor_id: str, competitor_data: CompetitorUpdate, user_id: str) -> Optional[Dict[str, Any]]:
        """Update an existing competitor"""
        try:
            # Verify the competitor exists and belongs to the user
            existing_competitor = await self.get_competitor(competitor_id, user_id)
            if not existing_competitor:
                logger.warning(f"Competitor {competitor_id} not found or access denied for user {user_id}")
                return None
            
            # Prepare update data
            update_data = competitor_data.model_dump(exclude_unset=True)
            
            # Update competitor using Supabase client
            result = await self.db.update_competitor(competitor_id, update_data)
            
            if result:
                logger.info(f"✅ Competitor updated successfully: {result.get('name')}")
                return result
            else:
                logger.error("❌ Failed to update competitor")
                return None
                
        except Exception as e:
            logger.error(f"Error updating competitor: {e}")
            raise
    
    async def delete_competitor(self, competitor_id: str, user_id: str) -> bool:
        """Delete a competitor"""
        try:
            # Verify the competitor exists and belongs to the user
            existing_competitor = await self.get_competitor(competitor_id, user_id)
            if not existing_competitor:
                logger.warning(f"Competitor {competitor_id} not found or access denied for user {user_id}")
                return False
            
            # Delete competitor using Supabase client
            success = await self.db.delete_competitor(competitor_id)
            
            if success:
                logger.info(f"✅ Competitor deleted successfully: {existing_competitor.get('name')}")
                return True
            else:
                logger.error("❌ Failed to delete competitor")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting competitor: {e}")
            raise
    
    async def get_competitor_stats(self, user_id: str) -> Dict[str, Any]:
        """Get competitor statistics for a user"""
        try:
            competitors = await self.get_competitors(user_id)
            
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
            
            stats = {
                "total_competitors": total_competitors,
                "active_competitors": active_competitors,
                "paused_competitors": paused_competitors,
                "error_competitors": error_competitors,
                "average_scan_frequency_minutes": round(avg_scan_frequency, 1),
                "platforms_monitored": list(all_platforms),
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"✅ Competitor stats retrieved for user {user_id}: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting competitor stats for user {user_id}: {e}")
            raise
    
    async def update_scan_time(self, competitor_id: str, user_id: str) -> bool:
        """Update the last scan time for a competitor"""
        try:
            # Verify the competitor exists and belongs to the user
            existing_competitor = await self.get_competitor(competitor_id, user_id)
            if not existing_competitor:
                logger.warning(f"Competitor {competitor_id} not found or access denied for user {user_id}")
                return False
            
            # Update scan time using Supabase client
            success = await self.db.update_competitor_scan_time(competitor_id)
            
            if success:
                logger.info(f"✅ Scan time updated for competitor: {existing_competitor.get('name')}")
                return True
            else:
                logger.error("❌ Failed to update scan time")
                return False
                
        except Exception as e:
            logger.error(f"Error updating scan time: {e}")
            raise
