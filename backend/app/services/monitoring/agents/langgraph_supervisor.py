"""
LangGraph Multi-Agent Supervisor for Competitor Monitoring
This module implements a proper LangGraph agent system with AI-powered routing
"""

import asyncio
import logging
import operator
from typing import Dict, List, Any, Optional, Literal, TypedDict, Annotated
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.competitor import Competitor
from app.models.monitoring import CompetitorMonitoringStatus
from app.core.config import settings

# Import langchain dependencies
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langgraph.graph import StateGraph, MessagesState, START, END
    from langgraph.types import Command
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    from langchain_core.tools import tool
    from langgraph.prebuilt import create_react_agent, InjectedState
    from typing import Annotated
    LANGCHAIN_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("✅ LangChain dependencies loaded successfully for LangGraph supervisor")
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"⚠️  LangChain dependencies not available: {e}")
    LANGCHAIN_AVAILABLE = False
    # Create dummy classes to prevent NameError
    class StateGraph:
        pass
    class MessagesState:
        pass
    class Command:
        pass


# Define the state for our multi-agent system
class SupervisorState(TypedDict):
    """State for the LangGraph supervisor system"""
    competitor_id: str
    competitor_data: Dict[str, Any]
    platforms_to_analyze: List[str]
    platform_results: Dict[str, Any]
    current_platform: Optional[str]
    analysis_complete: bool
    error_occurred: bool
    error_message: Optional[str]
    analysis_log: Annotated[List[str], operator.add]  # Use operator.add reducer for concurrent updates


class LangGraphSupervisorAgent:
    """
    LangGraph-based multi-agent supervisor for competitor monitoring
    Uses AI to route tasks to appropriate platform-specific sub-agents
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        logger.info("🤖 LangGraphSupervisorAgent initializing...")
        
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("LangChain dependencies not available. Install langchain-google-genai and langgraph")
        
        # Initialize LLM
        try:
            logger.info("🧠 Initializing LLM (Gemini 2.5 Flash)...")
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash-lite",
                api_key=settings.GOOGLE_API_KEY,
                temperature=0.3
            )
            logger.info("✅ LLM initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize LLM: {e}")
            raise
        
        # Import platform agents
        from .sub_agents.youtube_agent import YouTubeAgent
        from .sub_agents.instagram_agent import InstagramAgent
        from .sub_agents.twitter_agent import TwitterAgent
        from .sub_agents.browser_agent import BrowserAgent
        from .sub_agents.website_agent import WebsiteAgent
        
        # Platform agent classes
        self.platform_agent_classes = {
            "youtube": YouTubeAgent,
            "instagram": InstagramAgent,
            "twitter": TwitterAgent,
            "web": BrowserAgent,
            "website": WebsiteAgent,
        }
        
        # Build the LangGraph workflow
        self.graph = self._build_graph()
        logger.info("🔧 LangGraph supervisor graph built successfully")
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph multi-agent workflow"""
        
        # Create the state graph
        builder = StateGraph(SupervisorState)
        
        # Add nodes
        builder.add_node("supervisor", self._supervisor_node)
        builder.add_node("youtube_agent", self._create_platform_agent_node("youtube"))
        builder.add_node("instagram_agent", self._create_platform_agent_node("instagram"))
        builder.add_node("twitter_agent", self._create_platform_agent_node("twitter"))
        builder.add_node("web_agent", self._create_platform_agent_node("web"))
        builder.add_node("website_agent", self._create_platform_agent_node("website"))
        builder.add_node("aggregator", self._aggregator_node)
        
        # Define the flow
        builder.add_edge(START, "supervisor")
        
        # All agent nodes return to supervisor for routing decisions
        builder.add_edge("youtube_agent", "supervisor")
        builder.add_edge("instagram_agent", "supervisor")
        builder.add_edge("twitter_agent", "supervisor")
        builder.add_edge("web_agent", "supervisor")
        builder.add_edge("website_agent", "supervisor")
        
        # Supervisor routes to platform agents or aggregator using conditional logic
        def route_supervisor(state):
            platforms_remaining = [p for p in state["platforms_to_analyze"] 
                                 if p not in state["platform_results"]]
            if not platforms_remaining or state.get("error_occurred"):
                return "aggregator"
            else:
                return "continue"  # Let supervisor decide next agent
        
        builder.add_conditional_edges(
            "supervisor",
            route_supervisor,
            {
                "aggregator": "aggregator",
                "continue": "supervisor"  # Will be overridden by Command.goto in supervisor_node
            }
        )
        
        # Aggregator ends the workflow
        builder.add_edge("aggregator", END)
        
        return builder.compile()
    
    def _supervisor_node(self, state: SupervisorState) -> Command:
        """
        AI-powered supervisor that decides which platform agent to call next
        """
        try:
            logger.info("🧠 Supervisor node analyzing current state...")
            
            # Get competitor data and platforms
            platforms_remaining = [p for p in state["platforms_to_analyze"] 
                                 if p not in state["platform_results"]]
            
            if not platforms_remaining:
                logger.info("✅ All platforms analyzed, moving to aggregation")
                return Command(goto="aggregator")
            
            # Use LLM to decide which platform to analyze next
            system_prompt = """You are an AI supervisor managing competitor analysis agents.
            
Available platform agents:
- youtube_agent: Analyzes YouTube channels and videos
- instagram_agent: Analyzes Instagram profiles and posts  
- twitter_agent: Analyzes Twitter/X profiles and tweets
- web_agent: Analyzes web content, news, and general online presence
- website_agent: crawls and analyzes the competitor's official website

Your job is to select the next platform agent to analyze the competitor.

Current situation:
- Competitor: {competitor_name}
- Industry: {industry}
- Platforms to analyze: {platforms_remaining}
- Already analyzed: {completed_platforms}

Select the MOST IMPORTANT platform to analyze next based on:
1. The competitor's industry and likely social media presence
2. Platform relevance for business intelligence
3. Data availability and analysis value

Respond with ONLY the agent name (youtube_agent, instagram_agent, twitter_agent, web_agent, or website_agent)."""

            competitor_data = state["competitor_data"]
            completed_platforms = list(state["platform_results"].keys())
            
            prompt = system_prompt.format(
                competitor_name=competitor_data.get("name", "Unknown"),
                industry=competitor_data.get("industry", "Unknown"),
                platforms_remaining=platforms_remaining,
                completed_platforms=completed_platforms
            )
            
            # Get AI decision
            try:
                messages = [
                    SystemMessage(content=prompt),
                    HumanMessage(content="Which platform agent should analyze this competitor next? Respond with only the agent name.")
                ]
                response = self.llm.invoke(messages)
                next_agent = response.content.strip().lower()
            except Exception as e:
                logger.warning(f"⚠️  AI routing failed: {e}")
                next_agent = "invalid"
            
            # Validate AI response
            valid_agents = ["youtube_agent", "instagram_agent", "twitter_agent", "web_agent", "website_agent"]
            if next_agent not in valid_agents:
                # AI response invalid, log error and continue with next available platform
                logger.error(f"❌ AI response invalid: {next_agent}. Valid agents: {valid_agents}")
                if platforms_remaining:
                    next_agent = f"{platforms_remaining[0]}_agent"
                    logger.info(f"🔄 Continuing with next available platform: {next_agent}")
                else:
                    logger.error("❌ No platforms remaining to analyze")
                    return Command(goto="aggregator")
            
            logger.info(f"🎯 Supervisor decided: {next_agent}")
            
            # Update state with current platform
            current_platform = next_agent.replace("_agent", "")
            
            return Command(
                goto=next_agent,
                update={
                    "current_platform": current_platform,
                    "analysis_log": [
                        f"Supervisor routing to {next_agent} for {competitor_data.get('name', 'competitor')} analysis"
                    ]
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Error in supervisor node: {e}")
            return Command(
                goto="aggregator",
                update={
                    "error_occurred": True,
                    "error_message": str(e)
                }
            )
    
    def _create_platform_agent_node(self, platform: str):
        """Create a platform-specific agent node"""
        
        async def platform_agent_node(state: SupervisorState) -> Command:
            try:
                logger.info(f"🤖 {platform.title()} agent starting analysis...")
                
                competitor_data = state["competitor_data"]
                competitor_id = state["competitor_id"]
                
                if platform == "website":
                    handle = competitor_data.get("website_url")
                elif platform == "web":
                    handle = competitor_data.get("name")  # Use competitor name for web search
                else:
                    social_handles = competitor_data.get("social_media_handles", {})
                    handle = social_handles.get(platform)

                if not handle:
                    logger.warning(f"⚠️  No handle or URL found for {platform} for competitor")
                    return Command(
                        goto="supervisor",
                        update={
                            "platform_results": {
                                **state["platform_results"],
                                platform: {"status": "skipped", "error": f"No handle/URL for {platform}"}
                            }
                        }
                    )
                
                # Create platform agent instance
                agent_class = self.platform_agent_classes[platform]
                agent = agent_class(self.db)
                
                # Run analysis
                logger.info(f"🚀 Running {platform} analysis for: {handle}")
                result = await agent.analyze_competitor(competitor_id, handle)
                
                logger.info(f"✅ {platform.title()} analysis completed")
                
                return Command(
                    goto="supervisor", 
                    update={
                        "platform_results": {
                            **state["platform_results"],
                            platform: result
                        },
                        "analysis_log": [
                            f"{platform.title()} agent completed analysis. Found {len(result.get('posts', result.get('content', [])))} items."
                        ]
                    }
                )
                
            except Exception as e:
                logger.error(f"❌ Error in {platform} agent: {e}")
                return Command(
                    goto="supervisor",
                    update={
                        "platform_results": {
                            **state["platform_results"],
                            platform: {
                                "platform": platform,
                                "status": "failed",
                                "posts": [],
                                "error": str(e)
                            }
                        },
                        "error_occurred": True
                    }
                )
        
        return platform_agent_node
    
    def _aggregator_node(self, state: SupervisorState) -> Command:
        """
        Final aggregation node that compiles results from all platform agents
        """
        try:
            logger.info("📊 Aggregator node compiling final results...")
            
            platform_results = state["platform_results"]
            total_posts = sum(len(result.get("posts", result.get("content", []))) for result in platform_results.values())
            platforms_analyzed = list(platform_results.keys())
            errors = [f"{platform}: {result['error']}" for platform, result in platform_results.items() 
                     if result.get("error")]
            
            # Use AI to generate analysis summary
            summary_prompt = f"""Analyze the competitor monitoring results and provide a brief strategic summary.

Competitor: {state['competitor_data'].get('name', 'Unknown')}
Industry: {state['competitor_data'].get('industry', 'Unknown')}

Results:
- Platforms analyzed: {platforms_analyzed}
- Total posts found: {total_posts}
- Errors: {len(errors)}

Platform breakdown:
{chr(10).join([f"- {platform}: {len(result.get('posts', result.get('content', [])))} items, status: {result.get('status', 'unknown')}" 
               for platform, result in platform_results.items()])}

Provide a 2-3 sentence summary of key insights and recommendations."""

            try:
                messages = [
                    SystemMessage(content=summary_prompt),
                    HumanMessage(content="Provide a strategic summary of these competitor analysis results.")
                ]
                summary_response = self.llm.invoke(messages)
                ai_summary = summary_response.content
            except Exception as e:
                logger.warning(f"⚠️  Failed to generate AI summary: {e}")
                ai_summary = f"Analysis completed for {len(platforms_analyzed)} platforms with {total_posts} total posts found."
            
            final_result = {
                "status": "completed" if not errors else "completed_with_errors",
                "platforms_analyzed": platforms_analyzed,
                "posts_found": total_posts,
                "errors": errors,
                "platform_results": platform_results,
                "ai_summary": ai_summary,
                "analysis_complete": True
            }
            
            logger.info("🎉 Analysis aggregation completed")
            logger.info(f"   📊 Summary: {total_posts} posts across {len(platforms_analyzed)} platforms")
            
            return Command(
                update={
                    "analysis_complete": True,
                    "analysis_log": [
                        f"Analysis complete! {ai_summary}"
                    ],
                    **final_result
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Error in aggregator node: {e}")
            return Command(
                update={
                    "analysis_complete": True,
                    "error_occurred": True,
                    "error_message": str(e),
                    "status": "failed"
                }
            )
    

    
    async def analyze_competitor(self, competitor_id: str) -> Dict[str, Any]:
        """
        Main entry point for competitor analysis using LangGraph
        """
        try:
            logger.info(f"🚀 Starting LangGraph analysis for competitor {competitor_id}")
            
            # Get competitor data
            competitor = await self._get_competitor_data(competitor_id)
            if not competitor:
                return {
                    "competitor_id": competitor_id,
                    "status": "failed",
                    "error": "Competitor not found"
                }
            
            # Determine platforms to analyze
            platforms_to_analyze = self._determine_platforms(competitor)
            
            if not platforms_to_analyze:
                return {
                    "competitor_id": competitor_id,
                    "status": "completed",
                    "message": "No social media platforms configured",
                    "platforms_analyzed": [],
                    "posts_found": 0
                }
            
            # Update scanning status
            await self._update_scanning_status(competitor_id, True)
            
            # Prepare initial state
            initial_state = SupervisorState(
                competitor_id=competitor_id,
                competitor_data={
                    "id": str(competitor.id),
                    "name": competitor.name,
                    "industry": competitor.industry,
                    "description": competitor.description,
                    "website_url": competitor.website_url,
                    "social_media_handles": competitor.social_media_handles or {}
                },
                platforms_to_analyze=platforms_to_analyze,
                platform_results={},
                current_platform=None,
                analysis_complete=False,
                error_occurred=False,
                error_message=None,
                analysis_log=[f"Starting analysis for {competitor.name} across platforms: {', '.join(platforms_to_analyze)}"]
            )
            
            # Run the LangGraph workflow
            logger.info("🔄 Executing LangGraph workflow...")
            final_state = await self.graph.ainvoke(initial_state)
            
            # Debug final state
            logger.info(f"🔍 Final state keys: {list(final_state.keys())}")
            logger.info(f"🔍 Final state platforms_analyzed: {final_state.get('platforms_analyzed', 'NOT_FOUND')}")
            logger.info(f"🔍 Final state posts_found: {final_state.get('posts_found', 'NOT_FOUND')}")
            
            # Extract results
            result = {
                "competitor_id": competitor_id,
                "competitor_name": competitor.name,
                "status": final_state.get("status", "completed"),
                "platforms_analyzed": final_state.get("platforms_analyzed", []),
                "posts_found": final_state.get("posts_found", 0),
                "errors": final_state.get("errors", []),
                "platform_results": final_state.get("platform_results", {}),
                "ai_summary": final_state.get("ai_summary", ""),
                "analysis_log": final_state.get("analysis_log", [])
            }
            
            # Update final scanning status
            await self._update_scanning_status(
                competitor_id,
                False,
                last_successful_scan=datetime.now(timezone.utc) if not final_state.get("error_occurred") else None,
                last_failed_scan=datetime.now(timezone.utc) if final_state.get("error_occurred") else None,
                scan_error_message=final_state.get("error_message")
            )
            
            logger.info(f"🎉 LangGraph analysis completed for {competitor.name}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in LangGraph analysis: {e}")
            await self._update_scanning_status(
                competitor_id,
                False,
                last_failed_scan=datetime.now(timezone.utc),
                scan_error_message=str(e)
            )
            return {
                "competitor_id": competitor_id,
                "status": "failed",
                "error": str(e)
            }
    
    async def _get_competitor_data(self, competitor_id: str) -> Optional[Competitor]:
        """Get competitor data from database"""
        try:
            competitor_query = await self.db.execute(
                select(Competitor).where(Competitor.id == competitor_id)
            )
            return competitor_query.scalar_one_or_none()
        except Exception as e:
            logger.error(f"❌ Error getting competitor data: {e}")
            return None
    
    def _determine_platforms(self, competitor: Competitor) -> List[str]:
        """Determine which platforms need analysis"""
        platforms = []
        
        # Always include web intelligence agent
        platforms.append("web")
        
        # Include website agent if URL is present
        if competitor.website_url:
            platforms.append("website")

        if competitor.social_media_handles:
            for platform, handle in competitor.social_media_handles.items():
                if handle and platform.lower() in self.platform_agent_classes and platform.lower() not in ["web", "website"]:
                    platforms.append(platform.lower())
        
        logger.info(f"🎯 Determined platforms for analysis: {platforms}")
        return list(set(platforms))  # Return unique platforms
    
    async def _update_scanning_status(self, competitor_id: str, is_scanning: bool, **kwargs):
        """Update competitor monitoring status in database"""
        try:
            status_query = await self.db.execute(
                select(CompetitorMonitoringStatus).where(
                    CompetitorMonitoringStatus.competitor_id == competitor_id
                )
            )
            status = status_query.scalar_one_or_none()
            
            if not status:
                status = CompetitorMonitoringStatus(competitor_id=competitor_id)
                self.db.add(status)
            
            status.is_scanning = is_scanning
            if is_scanning:
                status.scan_started_at = datetime.now(timezone.utc)
            
            for field, value in kwargs.items():
                if value is not None:
                    setattr(status, field, value)
            
            await self.db.commit()
            
        except Exception as e:
            logger.error(f"❌ Error updating scanning status: {e}")
            await self.db.rollback()
