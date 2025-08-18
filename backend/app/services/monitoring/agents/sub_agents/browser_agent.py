"""
Browser Sub-Agent for Competitor Web Intelligence
Uses Tavily search API with LangGraph agent to analyze web content and news
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta, timezone
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Import langchain dependencies conditionally
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langgraph.prebuilt import create_react_agent
    from langchain_core.tools import tool
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"LangChain dependencies not available: {e}")
    LANGCHAIN_AVAILABLE = False

# Import Tavily dependencies conditionally
try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"Tavily dependencies not available: {e}")
    TAVILY_AVAILABLE = False

from app.models.competitor import Competitor
from app.models.monitoring import MonitoringData
from app.core.config import settings
from ...core_service import MonitoringService

logger = logging.getLogger(__name__)


class BrowserAgent:
    """Browser-based agent for competitor web intelligence using Tavily search"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.monitoring_service = MonitoringService(db)
        self.search_count = 0
        self.search_limit = 10  # Max 10 searches per competitor

        # Initialize LLM only if langchain is available
        self.llm = None
        if LANGCHAIN_AVAILABLE:
            try:
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash-lite",
                    api_key=settings.GOOGLE_API_KEY,
                    temperature=0
                )
            except Exception as e:
                logger.warning(f"Failed to initialize LLM: {e}")

        # Initialize Tavily search client
        self.tavily_client = None
        if TAVILY_AVAILABLE and hasattr(settings, 'TAVILY_API_KEY') and settings.TAVILY_API_KEY:
            try:
                self.tavily_client = TavilyClient(api_key=settings.TAVILY_API_KEY)
                logger.info("Tavily search client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Tavily client: {e}")
        elif not TAVILY_AVAILABLE:
            logger.warning("Tavily search not available - browser analysis will be limited")

        # Initialize agent
        self.agent = None
        self._initialized = False

    async def _initialize_agent(self, competitor: Competitor):
        """Initialize the browser agent with Tavily search tools"""
        if self._initialized:
            return

        try:
            logger.info("Initializing Browser agent with Tavily search tools...")

            if not self.tavily_client:
                raise Exception("Tavily client not available - check TAVILY_API_KEY")

            if not LANGCHAIN_AVAILABLE:
                raise Exception("LangChain dependencies not available - cannot create agent")

            if not self.llm:
                raise Exception("LLM not available - cannot create agent")

            # Create Tavily search tools
            tools = self._create_tavily_tools(competitor)
            logger.info(f"Created {len(tools)} Tavily search tools")

            # Create agent with browser/web search specific prompt
            logger.info("Creating LangGraph ReAct agent...")
            self.agent = create_react_agent(
                model=self.llm,
                tools=tools,
                prompt=self._build_analysis_prompt(competitor),
                name="browser_agent"
            )

            self._initialized = True
            logger.info("Browser agent initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing Browser agent: {e}")
            logger.error(f"Error details: {type(e).__name__}: {str(e)}")
            raise

    def _create_tavily_tools(self, competitor: Competitor) -> List[Any]:
        """Create Tavily search tools for the agent"""

        @tool
        def search_competitor_intel(query: str, search_depth: str = "basic", max_results: int = 5) -> List[Dict]:
            """
            Search the web for competitor intelligence based on a dynamically generated query.
            This is the primary tool for web searches. Do not use for more than 10 times.
            
            Args:
                query: A specific, targeted search query for competitor intelligence.
                search_depth: The depth of the search, either "basic" or "advanced".
                max_results: The maximum number of results to return.
            
            Returns:
                A list of search results.
            """
            if self.search_count >= self.search_limit:
                logger.warning(f"Search limit of {self.search_limit} reached. Aborting search.")
                return [{"error": "Search limit reached."}]

            self.search_count += 1
            logger.info(f"Performing search {self.search_count}/{self.search_limit} with query: {query}")

            try:
                response = self.tavily_client.search(
                    query=query,
                    search_depth=search_depth,
                    max_results=max_results,
                    include_answer=True,
                    include_raw_content=True
                )
                return response.get('results', [])
            except Exception as e:
                logger.error(f"Error during Tavily search: {e}")
                return [{"error": str(e)}]

        return [search_competitor_intel]

    async def analyze_competitor(self, competitor_id: str, competitor_name: str) -> Dict[str, Any]:
        """
        Analyze a competitor's web presence and recent online activity
        
        Args:
            competitor_id: Database ID of the competitor
            competitor_name: Name of the competitor to search for
            
        Returns:
            Dict containing analysis results and extracted content
        """
        self.search_count = 0  # Reset search count for each analysis

        try:
            # Get competitor info for context
            competitor = await self._get_competitor(competitor_id)
            if not competitor:
                logger.error(f"Competitor {competitor_id} not found in database")
                return {"platform": "web", "content": [], "error": "Competitor not found"}

            await self._initialize_agent(competitor)
            
            logger.info(f"Starting web analysis for competitor {competitor.id}, name: {competitor.name}")
            
            # The prompt is now part of the agent initialization
            analysis_prompt = f"Analyze competitor {competitor.name}"

            # Run agent analysis
            logger.info("Invoking Browser agent...")
            start_time = datetime.now(timezone.utc)
            
            result = await self.agent.ainvoke({
                "messages": [{"role": "user", "content": analysis_prompt}]
            })
            
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            logger.info(f"Browser agent execution completed in {duration:.2f}s")
            
            analysis_content = result["messages"][-1].content
            logger.info(f"Processing analysis results (content length: {len(analysis_content)})")
            
            content_items = await self._process_analysis_results(competitor_id, analysis_content, competitor.name)
            
            logger.info(f"Web analysis completed for {competitor.name}: {len(content_items)} items processed")
            
            return {
                "platform": "web",
                "content": content_items,
                "status": "completed",
                "analysis_summary": analysis_content[:500] + "..." if len(analysis_content) > 500 else analysis_content,
                "competitor_name": competitor.name
            }
            
        except Exception as e:
            logger.error(f"Error in web analysis for competitor {competitor_id}: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error details: {str(e)}")
            return {
                "platform": "web",
                "content": [],
                "error": str(e)
            }

    def _build_analysis_prompt(self, competitor: Competitor) -> str:
        """Build a dynamic analysis prompt for the Browser agent"""
        
        return f"""
You are a highly intelligent web analysis agent for competitor intelligence. Your goal is to autonomously discover and analyze recent, significant events related to a competitor.

**Competitor Profile:**
- **Name:** {competitor.name}
- **Industry:** {competitor.industry}
- **Description:** {competitor.description or 'N/A'}

**Your Mission:**
1.  **Strategize:** Based on the competitor profile, formulate a search plan. Think about what kind of information would be most valuable (e.g., product launches in the '{competitor.industry}' sector, recent news about '{competitor.name}', marketing campaigns, etc.).
2.  **Query Dynamically:** Construct specific, targeted search queries using the `search_competitor_intel` tool. Do not use generic queries.
    -   *Good Query Example:* "{competitor.name} new product launch 2024"
    -   *Good Query Example:* "customer reviews {competitor.name} {competitor.industry}"
    -   *Bad Query Example:* "search for news"
3.  **Search Iteratively:** Use the `search_competitor_intel` tool to execute your queries. You have a hard limit of **{self.search_limit} searches**. Use them wisely.
4.  **Analyze Findings:** Scrutinize the search results for actionable intelligence. Focus on content from the **last 24-48 hours**.
5.  **Synthesize and Report:** Consolidate your findings into a comprehensive report. For each significant piece of content, determine if it's **ALERT-WORTHY**.

**Alert-Worthy Criteria (be selective):**
-   Major product/service announcements
-   Significant media coverage (positive or negative) or viral content
-   Strategic partnerships, acquisitions, or funding rounds
-   Negative publicity or crisis situations
-   Changes in pricing strategy
-   Executive team changes or new key hires

Your final output should be a detailed analysis of your findings, highlighting any recommended alerts.
"""
    
    async def _process_analysis_results(self, competitor_id: str, analysis_content: str, competitor_name: str) -> List[Dict[str, Any]]:
        """
        Process agent analysis results and save significant web content as monitoring data
        """
        logger.info(f"🌐 Web analysis completed for {competitor_name}")
        logger.info(f"📝 Analysis summary: {analysis_content[:200]}...")
        
        processed_content = []
        
        try:
            # The agent has already made search calls and found web content during its analysis
            # We need to extract and save significant findings that were mentioned in the analysis
            
            # Since we can't directly access the search results from the agent's tool calls,
            # we'll analyze the agent's response to identify if alerts should be created
            
            # Use LLM to parse the analysis and determine if alerts are needed
            if self.llm:
                alert_assessment = await self._assess_content_for_alerts(analysis_content, competitor_name)
                
                if alert_assessment.get('create_alert', False):
                    # Create a web intelligence alert
                    await self._create_web_alert(competitor_id, alert_assessment, analysis_content)
                    
                    processed_content.append({
                        "type": "web_intelligence",
                        "alert_created": True,
                        "priority": alert_assessment.get('priority', 'medium'),
                        "summary": alert_assessment.get('summary', analysis_content[:200])
                    })
                else:
                    processed_content.append({
                        "type": "web_intelligence",
                        "alert_created": False,
                        "summary": analysis_content[:200]
                    })
            
            logger.info(f"✅ Processed web intelligence for {competitor_name}")
            
        except Exception as e:
            logger.error(f"❌ Error processing web analysis results: {e}")
        
        return processed_content
    
    async def _assess_content_for_alerts(self, analysis_content: str, competitor_name: str) -> Dict:
        """
        Use AI to assess if the web analysis warrants creating an alert
        """
        try:
            prompt = f"""
Analyze this web intelligence report for competitor "{competitor_name}" and determine if it warrants creating an alert.

WEB ANALYSIS CONTENT:
{analysis_content}

ASSESSMENT CRITERIA:
Determine if the content indicates any of the following alert-worthy events:
- Major product launches or announcements
- Significant media coverage or viral content  
- Strategic partnerships or acquisitions
- Crisis situations or negative publicity
- Pricing strategy changes
- Market expansion or competitive threats
- Industry-disrupting innovations

RESPONSE FORMAT:
Provide a JSON response with:
{{
    "create_alert": true/false,
    "priority": "low/medium/high",
    "summary": "Brief summary of why alert is/isn't needed",
    "alert_type": "product_launch/media_coverage/strategic_move/crisis/other",
    "key_insights": ["insight1", "insight2", "..."]
}}

Be selective - only recommend alerts for truly significant competitive events.
"""
            
            response = await self.llm.ainvoke(prompt)
            
            # Try to parse JSON response
            try:
                import json
                # Extract JSON from response if it contains other text
                content = response.content.strip()
                if content.startswith('{') and content.endswith('}'):
                    return json.loads(content)
                else:
                    # Look for JSON within the response
                    start = content.find('{')
                    end = content.rfind('}') + 1
                    if start != -1 and end != 0:
                        json_str = content[start:end]
                        return json.loads(json_str)
            except json.JSONDecodeError:
                logger.error(f"❌ Failed to parse AI response as JSON: {response.content}")
                # Return error response instead of fallback
                return {
                    "create_alert": False,
                    "priority": "low",
                    "summary": "AI response parsing failed",
                    "alert_type": "error"
                }
            
        except Exception as e:
            logger.error(f"Error assessing content for alerts: {e}")
            return {
                "create_alert": False,
                "priority": "low",
                "summary": f"Assessment error: {str(e)}"
            }
    
    async def _create_web_alert(self, competitor_id: str, alert_assessment: Dict, analysis_content: str) -> None:
        """
        Create an alert record for significant web intelligence
        """
        try:
            # Get competitor to access user_id
            competitor = await self._get_competitor(competitor_id)
            if not competitor:
                logger.error(f"Cannot create alert: competitor {competitor_id} not found")
                return
            
            alert_type = f"web_{alert_assessment.get('alert_type', 'intelligence')}"
            priority = alert_assessment.get('priority', 'medium')
            title = f"Web Intelligence Alert: {alert_assessment.get('alert_type', 'Significant Activity').replace('_', ' ').title()}"
            message = alert_assessment.get('summary', 'AI analysis detected significant web activity')
            
            alert_metadata = {
                "platform": "web",
                "analysis_type": "web_intelligence",
                "key_insights": alert_assessment.get('key_insights', []),
                "ai_assessment": alert_assessment,
                "analysis_content_preview": analysis_content[:500] if analysis_content else None
            }
            
            # Create alert using monitoring service with proper parameters
            await self.monitoring_service.create_alert(
                user_id=competitor.user_id,
                competitor_id=competitor_id,
                alert_type=alert_type,
                title=title,
                message=message,
                priority=priority,
                alert_metadata=alert_metadata
            )
            logger.info(f"🚨 Created web intelligence alert: {alert_assessment.get('alert_type', 'significant_activity')}")
            
        except Exception as e:
            logger.error(f"Error creating web alert: {e}")
    
    async def _get_competitor(self, competitor_id: str) -> Competitor:
        """Get competitor from database"""
        try:
            result = await self.db.execute(
                select(Competitor).where(Competitor.id == competitor_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting competitor {competitor_id}: {e}")
            return None
    
    async def close(self):
        """Close any resources"""
        logger.info("BrowserAgent closed")
        pass
