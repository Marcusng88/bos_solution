"""
Intelligent Browser Sub-Agent for Competitor Web Intelligence
Uses Tavily search API intelligently to analyze web content and news from today
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta, timezone
import hashlib
import json

# Import Windows compatibility utilities
from app.core.windows_compatibility import setup_windows_compatibility

# Import langchain dependencies conditionally
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
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

from app.core.config import settings
from app.services.monitoring.supabase_client import supabase_client

logger = logging.getLogger(__name__)


class BrowserAgent:
    """Intelligent browser-based agent for competitor web intelligence using Tavily search"""

    def __init__(self):
        logger.info("🌐 Intelligent BrowserAgent initializing...")
        self.search_count = 0
        self.search_limit = 15  # Increased for intelligent search

        # Initialize LLM for intelligent analysis
        self.llm = None
        if LANGCHAIN_AVAILABLE:
            try:
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash-lite",
                    api_key=settings.GOOGLE_API_KEY,
                    temperature=0.3  # Slightly creative for search terms
                )
                logger.info("✅ LLM initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize LLM: {e}")

        # Initialize Tavily search client
        self.tavily_client = None
        if TAVILY_AVAILABLE and hasattr(settings, 'TAVILY_API_KEY') and settings.TAVILY_API_KEY:
            try:
                self.tavily_client = TavilyClient(api_key=settings.TAVILY_API_KEY)
                logger.info("✅ Tavily search client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Tavily client: {e}")
        elif not TAVILY_AVAILABLE:
            logger.warning("Tavily search not available - browser analysis will be limited")

        logger.info("🌐 Intelligent BrowserAgent initialization completed")

    async def analyze_competitor(self, competitor_id: str, competitor_name: str) -> Dict[str, Any]:
        """
        Intelligently analyze a competitor's web presence and recent online activity
        
        Args:
            competitor_id: Database ID of the competitor
            competitor_name: Name of the competitor to search for
            
        Returns:
            Dict containing analysis results and extracted content
        """
        self.search_count = 0  # Reset search count for each analysis

        try:
            logger.info(f"🌐 Starting intelligent web analysis for {competitor_name}")
            
            if not self.tavily_client:
                return {
                    "platform": "web", 
                    "competitor_id": competitor_id,
                    "competitor_name": competitor_name,
                    "status": "completed",
                    "posts": [], 
                    "error": "Tavily client not available"
                }

            # Step 1: Generate intelligent search queries
            search_queries = await self._generate_intelligent_search_queries(competitor_name)
            logger.info(f"🔍 Generated {len(search_queries)} intelligent search queries")

            # Step 2: Search for recent content (today's focus)
            all_content = await self._search_recent_content(search_queries, competitor_name)
            logger.info(f"📰 Found {len(all_content)} recent web content items")

            if not all_content:
                logger.info(f"ℹ️  No recent web content found for {competitor_name}")
                return {
                    "platform": "web",
                    "competitor_id": competitor_id,
                    "competitor_name": competitor_name,
                    "status": "completed",
                    "posts": [],
                    "analysis_summary": f"No recent web content found for {competitor_name}"
                }

            # Step 3: Analyze and process content
            processed_posts = []
            alerts_created = 0

            for content_item in all_content:
                try:
                    # Analyze content using AI
                    analysis_result = await self._analyze_content_intelligence(content_item, competitor_name)
                    
                    # Create monitoring data
                    post_data = self._create_monitoring_data(content_item, analysis_result, competitor_id)
                    
                    # Save to Supabase
                    data_id = await supabase_client.save_monitoring_data(post_data)
                    
                    if data_id:
                        processed_posts.append({
                            "id": data_id,
                            "post_id": content_item.get('url', ''),
                            "title": content_item.get('title', ''),
                            "url": content_item.get('url', ''),
                            "source": content_item.get('source', ''),
                            "ai_analysis": analysis_result['summary'],
                            "is_alert_worthy": analysis_result['is_alert_worthy'],
                            "alert_reason": analysis_result.get('alert_reason', '')
                        })
                        
                        logger.info(f"✅ Saved web content: {content_item.get('title', 'Unknown')[:50]}...")
                        
                        # Create alert if deemed significant
                        if analysis_result['is_alert_worthy']:
                            await self._create_intelligent_alert(competitor_id, content_item, analysis_result, data_id)
                            alerts_created += 1
                            logger.info(f"🚨 Created alert for significant content: {content_item.get('title', 'Unknown')[:50]}...")

                except Exception as e:
                    logger.error(f"❌ Error processing content item: {e}")
                    continue

            logger.info(f"✅ Web analysis completed for {competitor_name}")
            logger.info(f"   📊 Processed {len(processed_posts)} content items")
            logger.info(f"   🚨 Created {alerts_created} alerts")
            
            return {
                "platform": "web",
                "competitor_id": competitor_id,
                "competitor_name": competitor_name,
                "status": "completed",
                "posts": processed_posts,
                "analysis_summary": f"Intelligently analyzed {len(processed_posts)} web content items for {competitor_name}. Created {alerts_created} alerts for significant content.",
                "insights": {
                    "total_content_analyzed": len(processed_posts),
                    "alerts_created": alerts_created,
                    "search_queries_used": len(search_queries),
                    "analysis_timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error in intelligent web analysis for competitor {competitor_id}: {e}")
            return {
                "platform": "web",
                "competitor_id": competitor_id,
                "competitor_name": competitor_name,
                "status": "failed",
                "posts": [],
                "error": str(e)
            }

    async def _generate_intelligent_search_queries(self, competitor_name: str) -> List[str]:
        """Generate intelligent search queries using AI or heuristics"""
        try:
            if self.llm:
                # Use AI to generate intelligent search queries
                prompt = f"""
Generate 6-8 intelligent web search queries to find recent news and content about the competitor "{competitor_name}" from today.

The queries should be designed to find:
1. Breaking news and announcements
2. Product launches or updates
3. Company developments and changes
4. Industry mentions and discussions
5. Financial news and business moves
6. Press releases and media coverage

Return the queries as a simple list, one per line, without numbers or bullets.
Make the queries specific and likely to return relevant, recent results.

Example format:
{competitor_name} news today
{competitor_name} announcement
{competitor_name} product launch
{competitor_name} press release
{competitor_name} financial news
"""
                
                response = await self.llm.ainvoke(prompt)
                queries = [q.strip() for q in response.content.strip().split('\n') if q.strip()]
                
                # Filter out empty queries and limit to 8
                queries = [q for q in queries if len(q) > 3][:8]
                
                if queries:
                    logger.info(f"🧠 AI generated {len(queries)} search queries")
                    return queries
            
            # Fallback to heuristic queries
            logger.info("🔍 Using heuristic search queries")
            return self._generate_heuristic_queries(competitor_name)
            
        except Exception as e:
            logger.error(f"❌ Error generating search queries: {e}")
            return self._generate_heuristic_queries(competitor_name)

    def _generate_heuristic_queries(self, competitor_name: str) -> List[str]:
        """Generate search queries using heuristics"""
        return [
            f"{competitor_name} news today",
            f"{competitor_name} announcement",
            f"{competitor_name} press release",
            f"{competitor_name} update",
            f"{competitor_name} launch",
            f"{competitor_name} financial",
            f"{competitor_name} business news",
            f"{competitor_name} development"
        ]

    async def _search_recent_content(self, search_queries: List[str], competitor_name: str) -> List[Dict[str, Any]]:
        """Search for recent content using intelligent queries"""
        try:
            all_content = []
            seen_urls = set()

            for query in search_queries:
                if self.search_count >= self.search_limit:
                    break
                    
                try:
                    logger.info(f"🔍 Searching web for: '{query}'")
                    
                    search_results = self.tavily_client.search(
                        query=query,
                        search_depth="advanced",  # More thorough search
                        max_results=5,
                        include_answer=True,
                        include_raw_content=True,
                        include_domains=["news", "business", "tech"],  # Focus on relevant domains
                        exclude_domains=["social"]  # Exclude social media (handled by other agents)
                    )
                    
                    self.search_count += 1
                    
                    results = search_results.get('results', [])
                    logger.info(f"   📰 Found {len(results)} results for query: '{query}'")
                    
                    for result in results:
                        url = result.get('url', '')
                        if url not in seen_urls:
                            seen_urls.add(url)
                            
                            # Filter for recent content (prefer today's content)
                            content_item = {
                                'title': result.get('title', ''),
                                'content': result.get('content', ''),
                                'url': url,
                                'source': result.get('source', ''),
                                'published_date': result.get('published_date', ''),
                                'score': result.get('score', 0),
                                'search_query': query
                            }
                            
                            all_content.append(content_item)
                    
                except Exception as e:
                    logger.error(f"❌ Error searching for query '{query}': {e}")
                    continue

            # Sort by relevance score and recency
            all_content.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            logger.info(f"📊 Total unique content items found: {len(all_content)}")
            return all_content
            
        except Exception as e:
            logger.error(f"❌ Error searching recent content: {e}")
            return []

    async def _analyze_content_intelligence(self, content_item: Dict[str, Any], competitor_name: str) -> Dict[str, Any]:
        """Analyze content using AI to determine significance and generate insights"""
        try:
            if self.llm:
                return await self._ai_content_analysis(content_item, competitor_name)
            else:
                return self._heuristic_content_analysis(content_item, competitor_name)
                
        except Exception as e:
            logger.error(f"❌ Error in content intelligence analysis: {e}")
            return self._heuristic_content_analysis(content_item, competitor_name)

    async def _ai_content_analysis(self, content_item: Dict[str, Any], competitor_name: str) -> Dict[str, Any]:
        """Use AI to analyze content for competitive intelligence"""
        try:
            title = content_item.get('title', '')
            content = content_item.get('content', '')[:800]  # First 800 chars
            source = content_item.get('source', '')
            
            prompt = f"""
Analyze this web content for competitive intelligence about "{competitor_name}":

TITLE: {title}
SOURCE: {source}
CONTENT: {content}

Your analysis should determine:
1. Is this content ALERT-WORTHY for competitive intelligence?
2. What are the key business insights about the competitor?
3. What strategic implications does this have?

ALERT-WORTHY criteria:
- Major product launches or announcements
- Significant business developments or changes
- Financial news (funding, IPO, acquisitions, partnerships)
- Strategic pivots or market moves
- Crisis situations or negative coverage
- Regulatory changes affecting the company
- Leadership changes or organizational restructuring

Provide your response in this JSON format:
{{
    "is_alert_worthy": true/false,
    "alert_reason": "Brief reason if alert-worthy, null if not",
    "significance_score": 1-10,
    "summary": "Brief competitive intelligence summary (max 200 words)",
    "key_insights": ["insight1", "insight2", "insight3"],
    "content_type": "news/announcement/financial/strategic/other",
    "competitive_impact": "high/medium/low",
    "urgency": "immediate/high/medium/low"
}}

Be selective with alerts - only flag truly significant competitive intelligence.
"""
            
            response = await self.llm.ainvoke(prompt)
            
            # Parse JSON response
            try:
                content_str = response.content.strip()
                if content_str.startswith('{') and content_str.endswith('}'):
                    analysis = json.loads(content_str)
                else:
                    # Extract JSON from response
                    start = content_str.find('{')
                    end = content_str.rfind('}') + 1
                    if start != -1 and end != 0:
                        json_str = content_str[start:end]
                        analysis = json.loads(json_str)
                    else:
                        raise ValueError("No JSON found in response")
                
                # Validate required fields
                required_fields = ['is_alert_worthy', 'summary', 'significance_score']
                if all(field in analysis for field in required_fields):
                    logger.info(f"🧠 AI analysis completed: Significance {analysis.get('significance_score', 0)}/10")
                    return analysis
                else:
                    logger.warning(f"⚠️  AI response missing required fields, using fallback")
                    return self._heuristic_content_analysis(content_item, competitor_name)
                    
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"❌ Failed to parse AI response: {e}")
                return self._heuristic_content_analysis(content_item, competitor_name)
                
        except Exception as e:
            logger.error(f"❌ Error in AI content analysis: {e}")
            return self._heuristic_content_analysis(content_item, competitor_name)

    def _heuristic_content_analysis(self, content_item: Dict[str, Any], competitor_name: str) -> Dict[str, Any]:
        """Heuristic analysis when AI is not available"""
        title = content_item.get('title', '').lower()
        content = content_item.get('content', '').lower()
        source = content_item.get('source', '')
        score = content_item.get('score', 0)
        
        # Check for alert-worthy keywords
        alert_keywords = [
            'launch', 'announcement', 'breaking', 'exclusive', 'funding', 'acquisition',
            'partnership', 'merger', 'ipo', 'expansion', 'layoffs', 'ceo', 'revenue'
        ]
        
        # Check for high relevance
        high_relevance = score > 0.8
        
        # Check if it's from authoritative source
        authoritative_sources = ['reuters', 'bloomberg', 'techcrunch', 'wsj', 'forbes']
        is_authoritative = any(auth in source.lower() for auth in authoritative_sources)
        
        # Check for alert keywords in title/content
        has_alert_keywords = any(keyword in title or keyword in content for keyword in alert_keywords)
        
        # Determine if alert-worthy
        is_alert_worthy = False
        alert_reason = None
        significance_score = 1
        
        if is_authoritative and has_alert_keywords:
            is_alert_worthy = True
            alert_reason = "Authoritative source with significant business keywords"
            significance_score = 8
        elif high_relevance and has_alert_keywords:
            is_alert_worthy = True
            alert_reason = f"High relevance score ({score:.2f}) with important keywords"
            significance_score = 7
        elif has_alert_keywords and competitor_name.lower() in title:
            is_alert_worthy = True
            alert_reason = "Company mentioned in headline with significant keywords"
            significance_score = 6
        
        # Generate summary
        summary = f"Web content analysis for {competitor_name}: '{content_item.get('title', 'Unknown')}' from {source}. "
        
        if is_authoritative:
            summary += "Authoritative source. "
        if has_alert_keywords:
            summary += "Contains business-significant keywords. "
        if high_relevance:
            summary += f"High relevance score ({score:.2f}). "
        
        return {
            "is_alert_worthy": is_alert_worthy,
            "alert_reason": alert_reason,
            "significance_score": significance_score,
            "summary": summary,
            "key_insights": [
                f"Source: {source}",
                f"Relevance score: {score:.2f}",
                f"Authoritative source: {is_authoritative}",
                f"Contains business keywords: {has_alert_keywords}"
            ],
            "content_type": "news" if any(news in source.lower() for news in ['news', 'reuters', 'bloomberg']) else "other",
            "competitive_impact": "high" if significance_score >= 7 else ("medium" if significance_score >= 5 else "low"),
            "urgency": "high" if significance_score >= 8 else ("medium" if significance_score >= 6 else "low")
        }

    def _create_monitoring_data(self, content_item: Dict[str, Any], analysis_result: Dict[str, Any], competitor_id: str) -> Dict[str, Any]:
        """Create monitoring data structure for Supabase"""
        content_text = f"{content_item.get('title', '')}\n\n{content_item.get('content', '')[:500]}"
        content_hash = hashlib.md5(content_text.encode()).hexdigest()
        
        return {
            'competitor_id': str(competitor_id),
            'platform': 'web',
            'post_id': content_hash,  # Use content hash as unique ID
            'post_url': content_item.get('url', ''),
            'content_text': content_text,
            'content_hash': content_hash,
            'media_urls': [],  # Web content typically doesn't have direct media URLs
            'engagement_metrics': {
                'relevance_score': content_item.get('score', 0),
                'significance_score': analysis_result.get('significance_score', 0)
            },
            'author_username': content_item.get('source', ''),
            'author_display_name': content_item.get('source', ''),
            'post_type': 'article',
            'language': 'en',  # Default to English
            'sentiment_score': 0.0,  # Default neutral
            'detected_at': datetime.now(timezone.utc).isoformat(),
            'posted_at': content_item.get('published_date') or datetime.now(timezone.utc).isoformat(),
            'is_new_post': True,
            'is_content_change': False
        }

    async def _create_intelligent_alert(self, competitor_id: str, content_item: Dict[str, Any], analysis_result: Dict[str, Any], data_id: str):
        """Create an intelligent alert for significant web content"""
        try:
            # Get competitor details to get user_id
            competitor_details = await supabase_client.get_competitor_details(competitor_id)
            user_id = competitor_details.get('user_id') if competitor_details else None
            
            alert_data = {
                'user_id': user_id,
                'competitor_id': str(competitor_id),
                'monitoring_data_id': data_id,
                'alert_type': 'web_intelligence',
                'priority': analysis_result.get('urgency', 'medium'),
                'title': f"Web Intelligence Alert: {content_item.get('title', 'Significant Content')[:100]}",
                'message': analysis_result.get('alert_reason', 'AI detected significant web activity'),
                'alert_metadata': {
                    'platform': 'web',
                    'content_url': content_item.get('url', ''),
                    'source': content_item.get('source', ''),
                    'relevance_score': content_item.get('score', 0),
                    'ai_analysis': {
                        'significance_score': analysis_result.get('significance_score', 0),
                        'content_type': analysis_result.get('content_type', 'unknown'),
                        'competitive_impact': analysis_result.get('competitive_impact', 'unknown'),
                        'urgency': analysis_result.get('urgency', 'unknown'),
                        'key_insights': analysis_result.get('key_insights', []),
                        'analysis_timestamp': datetime.now(timezone.utc).isoformat()
                    }
                },
                'is_read': False,
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            alert_id = await supabase_client.create_alert(alert_data)
            if alert_id:
                logger.info(f"🚨 Created intelligent web alert: {alert_id}")
            else:
                logger.error("❌ Failed to create alert in Supabase")
                
        except Exception as e:
            logger.error(f"❌ Error creating intelligent alert: {e}")

    async def close(self):
        """Close any resources"""
        logger.info("🌐 Intelligent BrowserAgent closed")
