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
    
    async def _initialize_agent(self):
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
            tools = self._create_tavily_tools()
            logger.info(f"Created {len(tools)} Tavily search tools")
            
            # Create agent with browser/web search specific prompt
            logger.info("Creating LangGraph ReAct agent...")
            self.agent = create_react_agent(
                model=self.llm,
                tools=tools,
                prompt=(
                    "You are a web intelligence agent for competitor analysis. Your job is to search the web for competitor-related content and analyze marketing strategies.\n\n"
                    "INSTRUCTIONS:\n"
                    "1. Use Tavily search tools to find recent web content about competitors\n"
                    "2. Focus ONLY on content from the last 24 hours\n"
                    "3. Search for news articles, blog posts, social media mentions, and press releases\n"
                    "4. Analyze content for:\n"
                    "   - Product launches and announcements\n"
                    "   - Marketing campaigns and messaging\n"
                    "   - Public sentiment and brand perception\n"
                    "   - Strategic partnerships and collaborations\n"
                    "   - Pricing changes and competitive moves\n"
                    "   - Industry trends and market positioning\n"
                    "5. Determine if content is ALERT-WORTHY based on:\n"
                    "   - Major product or service announcements\n"
                    "   - Significant media coverage or viral content\n"
                    "   - Strategic partnerships or acquisitions\n"
                    "   - Negative publicity or crisis situations\n"
                    "   - Pricing strategy changes\n"
                    "   - Market expansion or new product categories\n"
                    "6. Return structured analysis with clear alert recommendations\n\n"
                    "Remember: Focus on actionable competitive intelligence that could impact business strategy."
                ),
                name="browser_agent"
            )
            
            self._initialized = True
            logger.info("Browser agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Browser agent: {e}")
            logger.error(f"Error details: {type(e).__name__}: {str(e)}")
            raise
    
    def _create_tavily_tools(self):
        """Create Tavily search tools for the agent"""
        
        @tool
        def search_competitor_news(competitor_name: str, days_back: int = 1, max_results: int = 10) -> List[Dict]:
            """
            Search for recent news and articles about a competitor.
            
            Args:
                competitor_name: Name of the competitor to search for
                days_back: How many days back to search (default 1)
                max_results: Maximum number of results (default 10)
            
            Returns:
                List of news articles and web content
            """
            try:
                logger.info(f"Searching for news about: {competitor_name}")
                
                # Create search query
                query = f"{competitor_name} news announcement launch"
                
                # Search using Tavily
                response = self.tavily_client.search(
                    query=query,
                    search_depth="advanced",
                    max_results=max_results,
                    include_domains=None,  # Search all domains
                    exclude_domains=None,
                    include_answer=True,
                    include_raw_content=True
                )
                
                results = []
                for item in response.get('results', []):
                    # Filter by date if possible (Tavily doesn't always provide dates)
                    result_data = {
                        'title': item.get('title', ''),
                        'url': item.get('url', ''),
                        'content': item.get('content', ''),
                        'raw_content': item.get('raw_content', ''),
                        'published_date': item.get('published_date'),
                        'score': item.get('score', 0),
                        'source': 'tavily_news_search'
                    }
                    results.append(result_data)
                
                logger.info(f"Found {len(results)} news results for {competitor_name}")
                return results
                
            except Exception as e:
                logger.error(f"Error searching competitor news: {e}")
                return []
        
        @tool
        def search_competitor_mentions(competitor_name: str, context: str = "", max_results: int = 8) -> List[Dict]:
            """
            Search for recent mentions and discussions about a competitor.
            
            Args:
                competitor_name: Name of the competitor to search for
                context: Additional context for the search (e.g., "social media", "reviews")
                max_results: Maximum number of results (default 8)
            
            Returns:
                List of web mentions and discussions
            """
            try:
                logger.info(f"Searching for mentions of: {competitor_name} with context: {context}")
                
                # Create contextual search query
                if context:
                    query = f"{competitor_name} {context}"
                else:
                    query = f"{competitor_name} viral trending popular"
                
                # Search using Tavily
                response = self.tavily_client.search(
                    query=query,
                    search_depth="basic",
                    max_results=max_results,
                    include_answer=True,
                    include_raw_content=False  # Lighter for mentions
                )
                
                results = []
                for item in response.get('results', []):
                    result_data = {
                        'title': item.get('title', ''),
                        'url': item.get('url', ''),
                        'content': item.get('content', ''),
                        'published_date': item.get('published_date'),
                        'score': item.get('score', 0),
                        'source': 'tavily_mentions_search',
                        'search_context': context
                    }
                    results.append(result_data)
                
                logger.info(f"Found {len(results)} mentions for {competitor_name}")
                return results
                
            except Exception as e:
                logger.error(f"Error searching competitor mentions: {e}")
                return []
        
        @tool
        def search_competitor_products(competitor_name: str, product_keywords: str = "", max_results: int = 8) -> List[Dict]:
            """
            Search for recent product-related content about a competitor.
            
            Args:
                competitor_name: Name of the competitor to search for
                product_keywords: Specific product keywords to search for
                max_results: Maximum number of results (default 8)
            
            Returns:
                List of product-related web content
            """
            try:
                logger.info(f"Searching for product content: {competitor_name} {product_keywords}")
                
                # Create product-focused search query
                if product_keywords:
                    query = f"{competitor_name} {product_keywords} launch release new product"
                else:
                    query = f"{competitor_name} new product launch release announcement"
                
                # Search using Tavily
                response = self.tavily_client.search(
                    query=query,
                    search_depth="advanced",
                    max_results=max_results,
                    include_answer=True,
                    include_raw_content=True
                )
                
                results = []
                for item in response.get('results', []):
                    result_data = {
                        'title': item.get('title', ''),
                        'url': item.get('url', ''),
                        'content': item.get('content', ''),
                        'raw_content': item.get('raw_content', ''),
                        'published_date': item.get('published_date'),
                        'score': item.get('score', 0),
                        'source': 'tavily_products_search',
                        'product_keywords': product_keywords
                    }
                    results.append(result_data)
                
                logger.info(f"Found {len(results)} product results for {competitor_name}")
                return results
                
            except Exception as e:
                logger.error(f"Error searching competitor products: {e}")
                return []
        
        @tool
        def get_search_summary(query: str, max_results: int = 5) -> Dict:
            """
            Get a general search summary with answer for a competitor query.
            
            Args:
                query: Search query
                max_results: Maximum number of results (default 5)
            
            Returns:
                Search summary with answer and key results
            """
            try:
                logger.info(f"Getting search summary for: {query}")
                
                # Search using Tavily with answer generation
                response = self.tavily_client.search(
                    query=query,
                    search_depth="basic",
                    max_results=max_results,
                    include_answer=True,
                    include_raw_content=False
                )
                
                summary = {
                    'query': query,
                    'answer': response.get('answer', ''),
                    'results_count': len(response.get('results', [])),
                    'key_results': response.get('results', [])[:3],  # Top 3 results
                    'source': 'tavily_summary_search'
                }
                
                logger.info(f"Generated search summary for: {query}")
                return summary
                
            except Exception as e:
                logger.error(f"Error getting search summary: {e}")
                return {'query': query, 'error': str(e), 'source': 'tavily_summary_search'}
        
        return [search_competitor_news, search_competitor_mentions, search_competitor_products, get_search_summary]
    
    async def analyze_competitor(self, competitor_id: str, competitor_name: str) -> Dict[str, Any]:
        """
        Analyze a competitor's web presence and recent online activity
        
        Args:
            competitor_id: Database ID of the competitor
            competitor_name: Name of the competitor to search for
            
        Returns:
            Dict containing analysis results and extracted content
        """
        try:
            await self._initialize_agent()
            
            logger.info(f"Starting web analysis for competitor {competitor_id}, name: {competitor_name}")
            
            # Get competitor info for context
            competitor = await self._get_competitor(competitor_id)
            if not competitor:
                logger.error(f"Competitor {competitor_id} not found in database")
                return {
                    "platform": "web",
                    "content": [],
                    "error": "Competitor not found"
                }
            
            logger.info(f"Analyzing competitor: {competitor.name} (Industry: {competitor.industry})")
            
            # Construct analysis prompt
            analysis_prompt = self._build_analysis_prompt(competitor, competitor_name)
            logger.info(f"Analysis prompt length: {len(analysis_prompt)} characters")
            logger.debug(f"Analysis prompt: {analysis_prompt[:500]}...")
            
            # Run agent analysis
            logger.info("Invoking Browser agent with analysis prompt...")
            start_time = datetime.now(timezone.utc)
            
            result = await self.agent.ainvoke({
                "messages": [{"role": "user", "content": analysis_prompt}]
            })
            
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            logger.info(f"Browser agent execution completed in {duration:.2f}s")
            
            # Log agent response details
            logger.info(f"Agent response contains {len(result.get('messages', []))} messages")
            if result.get('messages'):
                last_message = result["messages"][-1]
                logger.info(f"Last message role: {getattr(last_message, 'type', 'unknown')}")
                logger.info(f"Last message content length: {len(getattr(last_message, 'content', ''))}")
                logger.debug(f"Last message content preview: {getattr(last_message, 'content', '')[:300] if getattr(last_message, 'content', '') else ''}...")
            
            # Extract and process results
            analysis_content = result["messages"][-1].content
            logger.info(f"Processing analysis results (content length: {len(analysis_content)})")
            
            content_items = await self._process_analysis_results(competitor_id, analysis_content, competitor_name)
            
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
    
    def _build_analysis_prompt(self, competitor: Competitor, competitor_name: str) -> str:
        """Build analysis prompt for the Browser agent"""
        
        return f"""
Analyze the recent web presence and online activity of competitor "{competitor.name}" in the {competitor.industry} industry.

COMPETITOR DETAILS:
- Name: {competitor.name}
- Industry: {competitor.industry}
- Description: {competitor.description or 'N/A'}

ANALYSIS TASKS:
1. Use search_competitor_news to find recent news and announcements about "{competitor_name}"
2. Use search_competitor_mentions to find trending discussions and social mentions
3. Use search_competitor_products to find any new product launches or releases
4. Use get_search_summary for general competitive intelligence

FOCUS ON CONTENT FROM THE LAST 24 HOURS:
- News articles and press releases
- Blog posts and industry coverage
- Social media viral content
- Product announcements and launches
- Strategic partnerships or collaborations
- Market analysis and industry reports

ALERT ASSESSMENT:
For each significant piece of content found, determine if it's ALERT-WORTHY based on:
- Major announcements or product launches
- Significant media coverage or viral content
- Strategic business moves (partnerships, acquisitions)
- Negative publicity or crisis situations
- Pricing strategy changes
- Market expansion or competitive threats

Provide a comprehensive analysis with specific insights and clear alert recommendations.
Be selective with alerts - only flag truly significant competitive events.
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
