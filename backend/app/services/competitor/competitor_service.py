"""
Competitor service for business logic
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.competitor import Competitor
from app.schemas.competitor import CompetitorCreate, CompetitorUpdate, CompetitorResponse
import logging

logger = logging.getLogger(__name__)


class CompetitorService:
    """Service for competitor operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_competitors(self, user_id: str) -> List[Competitor]:
        """Get all competitors for a user"""
        try:
            result = await self.db.execute(
                select(Competitor).where(Competitor.user_id == user_id)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching competitors for user {user_id}: {e}")
            raise
    
    async def get_competitor(self, competitor_id: str, user_id: str) -> Optional[Competitor]:
        """Get a specific competitor for a user"""
        try:
            result = await self.db.execute(
                select(Competitor).where(
                    and_(
                        Competitor.id == competitor_id,
                        Competitor.user_id == user_id
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching competitor {competitor_id} for user {user_id}: {e}")
            raise
    
    async def create_competitor(self, competitor_data: CompetitorCreate, user_id: str) -> Competitor:
        """Create a new competitor for a user"""
        try:
            logger.info(f"Creating competitor for user {user_id} with data: {competitor_data}")
            
            # Validate required fields
            if not competitor_data.name or not competitor_data.name.strip():
                raise ValueError("Competitor name is required")
            
            if not user_id:
                raise ValueError("User ID is required")
            
            # Create competitor data dict and ensure all values are properly set
            competitor_dict = competitor_data.dict()
            competitor_dict['user_id'] = user_id
            
            # Ensure scan_frequency_minutes has a default value
            if not competitor_dict.get('scan_frequency_minutes'):
                competitor_dict['scan_frequency_minutes'] = 60
            
            competitor = Competitor(**competitor_dict)
            
            logger.info(f"Adding competitor to database: {competitor}")
            self.db.add(competitor)
            await self.db.commit()
            await self.db.refresh(competitor)
            
            # Ensure all attributes are loaded
            await self.db.refresh(competitor, ['user_id'])
            
            logger.info(f"Successfully created competitor with ID: {competitor.id}")
            return competitor
        except Exception as e:
            logger.error(f"Error creating competitor for user {user_id}: {e}")
            await self.db.rollback()
            raise
    
    async def update_competitor(self, competitor_id: str, competitor_data: CompetitorUpdate, user_id: str) -> Optional[Competitor]:
        """Update a competitor for a user"""
        try:
            competitor = await self.get_competitor(competitor_id, user_id)
            if not competitor:
                return None
            
            # Update fields
            for field, value in competitor_data.dict(exclude_unset=True).items():
                setattr(competitor, field, value)
            
            competitor.updated_at = datetime.now(timezone.utc)
            await self.db.commit()
            await self.db.refresh(competitor)
            return competitor
        except Exception as e:
            logger.error(f"Error updating competitor {competitor_id} for user {user_id}: {e}")
            await self.db.rollback()
            raise
    
    async def delete_competitor(self, competitor_id: str, user_id: str) -> bool:
        """Delete a competitor for a user"""
        try:
            competitor = await self.get_competitor(competitor_id, user_id)
            if not competitor:
                return False
            
            await self.db.delete(competitor)
            await self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting competitor {competitor_id} for user {user_id}: {e}")
            await self.db.rollback()
            raise
    
    async def get_competitor_stats(self, user_id: str) -> Dict[str, Any]:
        """Get competitor statistics for a user"""
        try:
            competitors = await self.get_competitors(user_id)
            
            total_competitors = len(competitors)
            active_competitors = len([c for c in competitors if c.status == 'active'])
            paused_competitors = len([c for c in competitors if c.status == 'paused'])
            error_competitors = len([c for c in competitors if c.status == 'error'])
            
            # Get competitors scanned recently (last 24 hours)
            now = datetime.now(timezone.utc)
            recent_scans = 0
            for c in competitors:
                if c.last_scan_at:
                    # Ensure last_scan_at is timezone-aware
                    last_scan = c.last_scan_at
                    if last_scan.tzinfo is None:
                        last_scan = last_scan.replace(tzinfo=timezone.utc)
                    
                    if (now - last_scan).total_seconds() < 86400:
                        recent_scans += 1
            
            return {
                "total_competitors": total_competitors,
                "active_competitors": active_competitors,
                "paused_competitors": paused_competitors,
                "error_competitors": error_competitors,
                "recent_scans_24h": recent_scans
            }
        except Exception as e:
            logger.error(f"Error getting competitor stats for user {user_id}: {e}")
            raise
    
    async def update_scan_frequency(self, competitor_id: str, frequency_minutes: int, user_id: str) -> Optional[Competitor]:
        """Update scan frequency for a competitor"""
        try:
            competitor = await self.get_competitor(competitor_id, user_id)
            if not competitor:
                return None
            
            competitor.scan_frequency_minutes = frequency_minutes
            competitor.updated_at = datetime.now(timezone.utc)
            
            await self.db.commit()
            await self.db.refresh(competitor)
            return competitor
        except Exception as e:
            logger.error(f"Error updating scan frequency for competitor {competitor_id}: {e}")
            await self.db.rollback()
            raise
    
    async def toggle_competitor_status(self, competitor_id: str, user_id: str) -> Optional[Competitor]:
        """Toggle competitor status between active and paused"""
        try:
            competitor = await self.get_competitor(competitor_id, user_id)
            if not competitor:
                return None
            
            if competitor.status == 'active':
                competitor.status = 'paused'
            else:
                competitor.status = 'active'
            
            competitor.updated_at = datetime.now(timezone.utc)
            await self.db.commit()
            await self.db.refresh(competitor)
            return competitor
        except Exception as e:
            logger.error(f"Error toggling status for competitor {competitor_id}: {e}")
            await self.db.rollback()
            raise
