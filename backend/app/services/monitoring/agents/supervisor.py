"""
Supervisor Agent for Competitor Monitoring
This agent serves as the entry point and coordinates platform-specific sub-agents
Uses LangGraph-based AI supervisor for intelligent routing and analysis
"""

import logging
from typing import Dict, Any
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.competitor import Competitor
from app.models.monitoring import CompetitorMonitoringStatus
from app.core.config import settings

logger = logging.getLogger(__name__)

# Import LangGraph supervisor
from .langgraph_supervisor import LangGraphSupervisorAgent


class SupervisorAgent:
    """
    Supervisor agent that coordinates platform-specific sub-agents
    Uses AI-powered LangGraph routing for intelligent task management
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        logger.info("🤖 SupervisorAgent initializing with LangGraph AI routing...")
        
        try:
            self.langgraph_supervisor = LangGraphSupervisorAgent(db)
            logger.info("✅ LangGraph supervisor initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize LangGraph supervisor: {e}")
            raise
    
    async def analyze_competitor(self, competitor_id: str) -> Dict[str, Any]:
        """
        Main entry point for competitor analysis
        Routes to LangGraph AI supervisor for intelligent analysis
        """
        logger.info(f"🤖 Using LangGraph AI supervisor for competitor {competitor_id}")
        return await self.langgraph_supervisor.analyze_competitor(competitor_id)
    
    async def _get_competitor_data(self, competitor_id: str) -> Competitor:
        """Get competitor data from database"""
        try:
            logger.debug(f"🔍 Fetching competitor data for ID: {competitor_id}")
            
            competitor_query = await self.db.execute(
                select(Competitor).where(Competitor.id == competitor_id)
            )
            competitor = competitor_query.scalar_one_or_none()
            
            if competitor:
                logger.debug(f"✅ Competitor data retrieved: {competitor.name}")
            else:
                logger.debug(f"❌ No competitor found for ID: {competitor_id}")
                
            return competitor
        except Exception as e:
            logger.error(f"❌ Error getting competitor data: {e}")
            return None
    
    async def _update_scanning_status(self, competitor_id: str, is_scanning: bool, **kwargs):
        """Update competitor monitoring status in database"""
        try:
            status_action = "Starting" if is_scanning else "Completing"
            logger.debug(f"📊 {status_action} scanning status update for competitor {competitor_id}")
            
            
            status_query = await self.db.execute(
                select(CompetitorMonitoringStatus).where(
                    CompetitorMonitoringStatus.competitor_id == competitor_id
                )
            )
            status = status_query.scalar_one_or_none()
            
            if not status:
                logger.debug(f"   🆕 Creating new monitoring status record")
                status = CompetitorMonitoringStatus(competitor_id=competitor_id)
                self.db.add(status)
            
            # Update scanning status
            status.is_scanning = is_scanning
            if is_scanning:
                status.scan_started_at = datetime.now(timezone.utc)
                logger.debug(f"   🕐 Scan started at: {status.scan_started_at}")
            
            # Update other provided fields
            for field, value in kwargs.items():
                if value is not None:
                    setattr(status, field, value)
                    logger.debug(f"   📝 Updated {field}: {value}")
            
            await self.db.commit()
            logger.debug(f"✅ Scanning status updated successfully")
            
        except Exception as e:
            logger.error(f"❌ Error updating scanning status: {e}")
            await self.db.rollback()
