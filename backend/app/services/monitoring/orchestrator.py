"""
Agent-based Monitoring Service using LangGraph and AI Agents
Hierarchical agent architecture with AI-powered supervisor and platform-specific sub-agents
"""

import logging
from typing import Dict, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.competitor import Competitor
from app.models.monitoring import CompetitorMonitoringStatus
from .agents.supervisor import SupervisorAgent

logger = logging.getLogger(__name__)


class AgentMonitoringService:
    """AI-powered service to manage monitoring using LangGraph and AI agents"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.supervisor_agent = SupervisorAgent(db)
        logger.info("🤖 AgentMonitoringService initialized with AI-powered supervisor")
    
    async def run_monitoring_for_competitor(self, competitor_id: str) -> Dict[str, Any]:
        """Run AI-powered monitoring for a specific competitor using LangGraph agents"""
        try:
            logger.info(f"🚀 Starting AI-powered monitoring for competitor {competitor_id}")
            
            # Get competitor data
            competitor_query = await self.db.execute(
                select(Competitor).where(Competitor.id == competitor_id)
            )
            competitor = competitor_query.scalar_one_or_none()
            
            if not competitor:
                return {
                    "competitor_id": competitor_id,
                    "status": "failed",
                    "error": f"Competitor {competitor_id} not found"
                }
            
            # Run AI-powered analysis via LangGraph supervisor
            result = await self.supervisor_agent.analyze_competitor(competitor_id)
            
            logger.info(f"✅ AI monitoring completed for competitor {competitor_id}")
            
            return {
                "competitor_id": competitor_id,
                "status": result.get("status", "unknown"),
                "platforms_scanned": len(result.get("platforms_analyzed", [])),
                "posts_found": result.get("posts_found", 0),
                "errors": result.get("errors", []),
                "details": result
            }
            
        except Exception as e:
            logger.error(f"❌ Error in AI monitoring for competitor {competitor_id}: {e}")
            return {
                "competitor_id": competitor_id,
                "status": "failed",
                "error": str(e)
            }
    
    async def run_monitoring_for_all_active_competitors(self, user_id: str) -> List[Dict[str, Any]]:
        """Run AI-powered monitoring for all active competitors of a user"""
        try:
            # Convert Clerk user ID to database UUID if it's a string
            from app.core.auth_utils import get_db_user_id
            if isinstance(user_id, str) and user_id.startswith('user_'):
                # This is a Clerk user ID, convert it
                db_user_id = await get_db_user_id(user_id, self.db)
            else:
                # This is already a database UUID
                db_user_id = user_id
            
            # Get all active competitors for the user
            competitors_query = await self.db.execute(
                select(Competitor).where(
                    Competitor.user_id == db_user_id,
                    Competitor.status == 'active'
                )
            )
            competitors = competitors_query.scalars().all()
            
            logger.info(f"🚀 Running AI-powered monitoring for {len(competitors)} competitors for user {user_id}")
            
            results = []
            for competitor in competitors:
                try:
                    # Create supervisor agent for this competitor
                    supervisor = SupervisorAgent(self.db)
                    
                    # Run AI analysis for this competitor
                    result = await supervisor.analyze_competitor(str(competitor.id))
                    
                    results.append({
                        "competitor_id": str(competitor.id),
                        "competitor_name": competitor.name,
                        "status": "completed",
                        "result": result
                    })
                    
                except Exception as e:
                    logger.error(f"❌ Error running AI monitoring for competitor {competitor.id}: {e}")
                    results.append({
                        "competitor_id": str(competitor.id),
                        "competitor_name": competitor.name,
                        "status": "failed",
                        "error": str(e)
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error in run_monitoring_for_all_active_competitors: {e}")
            return [{
                "status": "failed",
                "error": str(e)
            }]
