"""
Intelligent Twitter/X Sub-Agent for Competitor Social Media Intelligence
Uses intelligent search and AI analysis to monitor Twitter competitor activity
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta, timezone
import hashlib
import json
import re

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

# Import search dependencies conditionally
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


class TwitterAgent:
    """Intelligent Twitter/X agent for competitor social media intelligence"""

    def __init__(self):
        logger.info("🐦 Intelligent TwitterAgent initializing...")
        self.search_count = 0
        self.search_limit = 12  # Limit for intelligent search

        # Initialize LLM for intelligent analysis
        self.llm = None
        if LANGCHAIN_AVAILABLE:
            try:
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash-lite",
                    api_key=settings.GOOGLE_API_KEY,
                    temperature=0.3
                )
                logger.info("✅ LLM initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize LLM: {e}")

        # Initialize search client for finding Twitter content
        self.search_client = None
        if TAVILY_AVAILABLE and hasattr(settings, 'TAVILY_API_KEY') and settings.TAVILY_API_KEY:
            try:
                self.search_client = TavilyClient(api_key=settings.TAVILY_API_KEY)
                logger.info("✅ Search client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize search client: {e}")

        logger.info("🐦 Intelligent TwitterAgent initialization completed")

    async def analyze_competitor(self, competitor_id: str, competitor_name: str) -> Dict[str, Any]:
        """
        Intelligently analyze a competitor's Twitter/X presence and recent activity
        
        Args:
            competitor_id: Database ID of the competitor
            competitor_name: Name of the competitor to search for
            
        Returns:
            Dict containing analysis results and extracted content
        """
        self.search_count = 0  # Reset search count

        try:
            logger.info(f"🐦 Starting intelligent Twitter analysis for {competitor_name}")
            
            if not self.search_client:
                logger.warning("Search client not available - using alternative approach")
                return await self._fallback_analysis(competitor_id, competitor_name)

            # Step 1: Generate intelligent search queries for Twitter content
            search_queries = await self._generate_intelligent_twitter_queries(competitor_name)
            logger.info(f"🔍 Generated {len(search_queries)} intelligent Twitter search queries")

            # Step 2: Search for recent Twitter content and mentions
            all_content = await self._search_twitter_content(search_queries, competitor_name)
            logger.info(f"🐦 Found {len(all_content)} Twitter-related content items")

            if not all_content:
                logger.info(f"ℹ️  No recent Twitter content found for {competitor_name}")
                return {
                    "platform": "twitter",
                    "competitor_id": competitor_id,
                    "competitor_name": competitor_name,
                    "status": "completed",
                    "posts": [],
                    "analysis_summary": f"No recent Twitter content found for {competitor_name}"
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
                    
                    # Check for existing content
                    existing_content = await supabase_client.check_existing_post(
                        competitor_id, 'twitter', content_item.get('content_hash', '')
                    )
                    
                    if existing_content:
                        # Check for content changes
                        if self._has_content_changed(existing_content, post_data):
                            # Update existing content
                            updated = await supabase_client.update_post_content(
                                existing_content['id'], post_data
                            )
                            if updated and analysis_result['is_alert_worthy']:
                                await self._create_content_change_alert(competitor_id, content_item, analysis_result, existing_content['id'])
                                alerts_created += 1
                        continue
                    
                    # Save new content to Supabase
                    data_id = await supabase_client.save_monitoring_data(post_data)
                    
                    if data_id:
                        processed_posts.append({
                            "id": data_id,
                            "post_id": content_item.get('content_hash', ''),
                            "title": content_item.get('title', ''),
                            "url": content_item.get('url', ''),
                            "ai_analysis": analysis_result['summary'],
                            "is_alert_worthy": analysis_result['is_alert_worthy'],
                            "alert_reason": analysis_result.get('alert_reason', '')
                        })
                        
                        logger.info(f"✅ Saved Twitter content: {content_item.get('title', 'Unknown')[:50]}...")
                        
                        # Create alert if deemed significant
                        if analysis_result['is_alert_worthy']:
                            await self._create_intelligent_alert(competitor_id, content_item, analysis_result, data_id)
                            alerts_created += 1
                            logger.info(f"🚨 Created alert for significant Twitter content")

                except Exception as e:
                    logger.error(f"❌ Error processing Twitter content: {e}")
                    continue

            logger.info(f"✅ Twitter analysis completed for {competitor_name}")
            logger.info(f"   📊 Processed {len(processed_posts)} content items")
            logger.info(f"   🚨 Created {alerts_created} alerts")
            
            return {
                "platform": "twitter",
                "competitor_id": competitor_id,
                "competitor_name": competitor_name,
                "status": "completed",
                "posts": processed_posts,
                "analysis_summary": f"Intelligently analyzed {len(processed_posts)} Twitter-related content items for {competitor_name}. Created {alerts_created} alerts for significant activity.",
                "insights": {
                    "total_content_analyzed": len(processed_posts),
                    "alerts_created": alerts_created,
                    "search_queries_used": len(search_queries),
                    "analysis_timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error in intelligent Twitter analysis for competitor {competitor_id}: {e}")
            return {
                "platform": "twitter",
                "competitor_id": competitor_id,
                "competitor_name": competitor_name,
                "status": "failed",
                "posts": [],
                "error": str(e)
            }

    async def _generate_intelligent_twitter_queries(self, competitor_name: str) -> List[str]:
        """Generate intelligent search queries for Twitter content"""
        try:
            if self.llm:
                # Use AI to generate intelligent search queries
                prompt = f"""
Generate 8-10 intelligent search queries to find recent Twitter/X content and mentions about the competitor "{competitor_name}" from today.

The queries should be designed to find:
1. Tweets posted by the competitor's official account
2. Industry mentions and discussions about the competitor
3. Product announcements and updates on Twitter
4. Customer feedback and reviews on Twitter
5. News coverage shared on Twitter
6. Thread discussions about the competitor
7. Competitor mentions in tech Twitter conversations
8. Partnership and collaboration announcements
9. Twitter Spaces or live discussions

Return the queries as a simple list, one per line, without numbers or bullets.
Make the queries specific for Twitter content discovery.

Example format:
{competitor_name} Twitter account
{competitor_name} tweets today
{competitor_name} Twitter announcement
{competitor_name} Twitter discussion
{competitor_name} customer feedback Twitter
"""
                
                response = await self.llm.ainvoke(prompt)
                queries = [q.strip() for q in response.content.strip().split('\n') if q.strip()]
                
                # Filter out empty queries and limit to 10
                queries = [q for q in queries if len(q) > 3][:10]
                
                if queries:
                    logger.info(f"🧠 AI generated {len(queries)} Twitter search queries")
                    return queries
            
            # Fallback to heuristic queries
            logger.info("🔍 Using heuristic Twitter search queries")
            return self._generate_heuristic_twitter_queries(competitor_name)
            
        except Exception as e:
            logger.error(f"❌ Error generating Twitter search queries: {e}")
            return self._generate_heuristic_twitter_queries(competitor_name)

    def _generate_heuristic_twitter_queries(self, competitor_name: str) -> List[str]:
        """Generate Twitter search queries using heuristics"""
        return [
            f"{competitor_name} Twitter posts today",
            f"{competitor_name} tweets",
            f"{competitor_name} Twitter announcement",
            f"{competitor_name} Twitter news",
            f"{competitor_name} Twitter discussion",
            f"{competitor_name} Twitter thread",
            f"{competitor_name} customer Twitter",
            f"{competitor_name} Twitter launch",
            f"{competitor_name} Twitter update",
            f"{competitor_name} Twitter feedback"
        ]

    async def _search_twitter_content(self, search_queries: List[str], competitor_name: str) -> List[Dict[str, Any]]:
        """Search for Twitter content using intelligent queries"""
        try:
            all_content = []
            seen_urls = set()

            for query in search_queries:
                if self.search_count >= self.search_limit:
                    break
                    
                try:
                    logger.info(f"🔍 Searching Twitter content for: '{query}'")
                    
                    search_results = self.search_client.search(
                        query=query,
                        search_depth="advanced",
                        max_results=4,
                        include_answer=True,
                        include_raw_content=True,
                        include_domains=["twitter.com", "x.com", "socialmedia"],
                        exclude_domains=["instagram.com", "youtube.com", "linkedin.com"]
                    )
                    
                    self.search_count += 1
                    
                    results = search_results.get('results', [])
                    logger.info(f"   🐦 Found {len(results)} results for query: '{query}'")
                    
                    for result in results:
                        url = result.get('url', '')
                        if url not in seen_urls:
                            seen_urls.add(url)
                            
                            content_item = {
                                'title': result.get('title', ''),
                                'content': result.get('content', ''),
                                'url': url,
                                'source': result.get('source', ''),
                                'published_date': result.get('published_date', ''),
                                'score': result.get('score', 0),
                                'search_query': query,
                                'content_hash': hashlib.md5(f"{result.get('title', '')}{result.get('content', '')}".encode()).hexdigest()
                            }
                            
                            all_content.append(content_item)
                    
                except Exception as e:
                    logger.error(f"❌ Error searching for Twitter query '{query}': {e}")
                    continue

            # Sort by relevance score
            all_content.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            logger.info(f"📊 Total unique Twitter content items found: {len(all_content)}")
            return all_content
            
        except Exception as e:
            logger.error(f"❌ Error searching Twitter content: {e}")
            return []

    async def _analyze_content_intelligence(self, content_item: Dict[str, Any], competitor_name: str) -> Dict[str, Any]:
        """Analyze Twitter content using AI to determine significance"""
        try:
            if self.llm:
                return await self._ai_content_analysis(content_item, competitor_name)
            else:
                return self._heuristic_content_analysis(content_item, competitor_name)
                
        except Exception as e:
            logger.error(f"❌ Error in Twitter content intelligence analysis: {e}")
            return self._heuristic_content_analysis(content_item, competitor_name)

    async def _ai_content_analysis(self, content_item: Dict[str, Any], competitor_name: str) -> Dict[str, Any]:
        """Use AI to analyze Twitter content for competitive intelligence"""
        try:
            title = content_item.get('title', '')
            content = content_item.get('content', '')[:800]
            url = content_item.get('url', '')
            source = content_item.get('source', '')
            
            prompt = f"""
Analyze this Twitter/X-related content for competitive intelligence about "{competitor_name}":

TITLE: {title}
SOURCE: {source}
URL: {url}
CONTENT: {content}

Your analysis should determine:
1. Is this content ALERT-WORTHY for competitive intelligence?
2. What are the key social media insights about the competitor?
3. What strategic implications does this have for their Twitter strategy?

ALERT-WORTHY criteria for Twitter content:
- Official announcements from competitor's Twitter account
- Viral tweets or trending topics involving the competitor
- Product launches or major updates announced on Twitter
- Customer service issues or crisis communications
- Industry thought leadership positions taken
- Partnership announcements or collaborations
- Significant engagement spikes or community reactions
- Twitter threads revealing strategic insights
- Real-time updates during events or launches
- Negative sentiment trends or PR crisis indicators

Provide your response in this JSON format:
{{
    "is_alert_worthy": true/false,
    "alert_reason": "Brief reason if alert-worthy, null if not",
    "significance_score": 1-10,
    "summary": "Brief competitive intelligence summary (max 200 words)",
    "key_insights": ["insight1", "insight2", "insight3"],
    "content_type": "tweet/thread/announcement/discussion/retweet/mention/other",
    "competitive_impact": "high/medium/low",
    "urgency": "immediate/high/medium/low",
    "engagement_indicators": ["indicator1", "indicator2"],
    "sentiment_analysis": "positive/neutral/negative"
}}

Be selective with alerts - only flag truly significant competitive intelligence from Twitter.
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
                    logger.info(f"🧠 AI Twitter analysis completed: Significance {analysis.get('significance_score', 0)}/10")
                    return analysis
                else:
                    logger.warning(f"⚠️  AI response missing required fields, using fallback")
                    return self._heuristic_content_analysis(content_item, competitor_name)
                    
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"❌ Failed to parse AI response: {e}")
                return self._heuristic_content_analysis(content_item, competitor_name)
                
        except Exception as e:
            logger.error(f"❌ Error in AI Twitter content analysis: {e}")
            return self._heuristic_content_analysis(content_item, competitor_name)

    def _heuristic_content_analysis(self, content_item: Dict[str, Any], competitor_name: str) -> Dict[str, Any]:
        """Heuristic analysis when AI is not available"""
        title = content_item.get('title', '').lower()
        content = content_item.get('content', '').lower()
        url = content_item.get('url', '').lower()
        score = content_item.get('score', 0)
        
        # Check for Twitter-specific alert keywords
        twitter_keywords = [
            'tweet', 'twitter', 'announcement', 'breaking', 'thread', 'viral',
            'trending', 'launch', 'update', 'partnership', 'crisis', 'feedback'
        ]
        
        # Check URL for Twitter-related content
        is_twitter_url = any(domain in url for domain in ['twitter.com', 'x.com'])
        
        # Check for high relevance
        high_relevance = score > 0.7
        
        # Check for alert keywords in title/content
        has_twitter_keywords = any(keyword in title or keyword in content for keyword in twitter_keywords)
        
        # Sentiment indicators
        negative_words = ['crisis', 'issue', 'problem', 'complaint', 'fail', 'down']
        positive_words = ['launch', 'success', 'win', 'great', 'amazing', 'breakthrough']
        
        sentiment = 'neutral'
        if any(word in content for word in negative_words):
            sentiment = 'negative'
        elif any(word in content for word in positive_words):
            sentiment = 'positive'
        
        # Determine if alert-worthy
        is_alert_worthy = False
        alert_reason = None
        significance_score = 1
        
        if is_twitter_url and has_twitter_keywords:
            is_alert_worthy = True
            alert_reason = "Direct Twitter content with significant keywords"
            significance_score = 8
        elif high_relevance and has_twitter_keywords:
            is_alert_worthy = True
            alert_reason = f"High relevance score ({score:.2f}) with Twitter keywords"
            significance_score = 7
        elif has_twitter_keywords and competitor_name.lower() in title:
            is_alert_worthy = True
            alert_reason = "Company mentioned in Twitter-related headline"
            significance_score = 6
        elif sentiment == 'negative' and competitor_name.lower() in content:
            is_alert_worthy = True
            alert_reason = "Negative sentiment detected in Twitter discussion"
            significance_score = 7
        
        # Generate summary
        summary = f"Twitter analysis for {competitor_name}: '{content_item.get('title', 'Unknown')}'. "
        
        if is_twitter_url:
            summary += "Direct Twitter content. "
        if has_twitter_keywords:
            summary += "Contains Twitter activity keywords. "
        if high_relevance:
            summary += f"High relevance score ({score:.2f}). "
        if sentiment != 'neutral':
            summary += f"Sentiment: {sentiment}. "
        
        return {
            "is_alert_worthy": is_alert_worthy,
            "alert_reason": alert_reason,
            "significance_score": significance_score,
            "summary": summary,
            "key_insights": [
                f"Source: {content_item.get('source', '')}",
                f"Relevance score: {score:.2f}",
                f"Twitter URL: {is_twitter_url}",
                f"Contains Twitter keywords: {has_twitter_keywords}",
                f"Sentiment: {sentiment}"
            ],
            "content_type": "twitter_mention" if is_twitter_url else "external_mention",
            "competitive_impact": "high" if significance_score >= 7 else ("medium" if significance_score >= 5 else "low"),
            "urgency": "high" if significance_score >= 8 else ("medium" if significance_score >= 6 else "low"),
            "engagement_indicators": [
                f"Relevance score: {score:.2f}",
                f"Content source: {content_item.get('source', '')}"
            ],
            "sentiment_analysis": sentiment
        }

    def _create_monitoring_data(self, content_item: Dict[str, Any], analysis_result: Dict[str, Any], competitor_id: str) -> Dict[str, Any]:
        """Create monitoring data structure for Supabase"""
        content_text = f"{content_item.get('title', '')}\n\n{content_item.get('content', '')[:500]}"
        
        return {
            'competitor_id': str(competitor_id),
            'platform': 'twitter',
            'post_id': content_item.get('content_hash', ''),
            'post_url': content_item.get('url', ''),
            'content_text': content_text,
            'content_hash': content_item.get('content_hash', ''),
            'media_urls': [],  # Would be populated with actual Twitter media URLs
            'engagement_metrics': {
                'relevance_score': content_item.get('score', 0),
                'significance_score': analysis_result.get('significance_score', 0)
            },
            'author_username': content_item.get('source', ''),
            'author_display_name': content_item.get('source', ''),
            'post_type': analysis_result.get('content_type', 'mention'),
            'language': 'en',  # Default to English
            'sentiment_score': self._convert_sentiment_to_score(analysis_result.get('sentiment_analysis', 'neutral')),
            'detected_at': datetime.now(timezone.utc).isoformat(),
            'posted_at': content_item.get('published_date') or datetime.now(timezone.utc).isoformat(),
            'is_new_post': True,
            'is_content_change': False
        }

    def _convert_sentiment_to_score(self, sentiment: str) -> float:
        """Convert sentiment string to numerical score"""
        sentiment_map = {
            'positive': 0.7,
            'neutral': 0.0,
            'negative': -0.7
        }
        return sentiment_map.get(sentiment.lower(), 0.0)

    def _has_content_changed(self, existing_content: Dict[str, Any], new_content: Dict[str, Any]) -> bool:
        """Check if Twitter content has changed significantly"""
        old_hash = existing_content.get('content_hash', '')
        new_hash = new_content.get('content_hash', '')
        return old_hash != new_hash

    async def _create_intelligent_alert(self, competitor_id: str, content_item: Dict[str, Any], analysis_result: Dict[str, Any], data_id: str):
        """Create an intelligent alert for significant Twitter content"""
        try:
            # Get competitor details to get user_id
            competitor_details = await supabase_client.get_competitor_details(competitor_id)
            user_id = competitor_details.get('user_id') if competitor_details else None
            
            alert_data = {
                'user_id': user_id,
                'competitor_id': str(competitor_id),
                'monitoring_data_id': data_id,
                'alert_type': 'twitter_intelligence',
                'priority': analysis_result.get('urgency', 'medium'),
                'title': f"Twitter Alert: {content_item.get('title', 'Significant Activity')[:100]}",
                'message': analysis_result.get('alert_reason', 'AI detected significant Twitter activity'),
                'alert_metadata': {
                    'platform': 'twitter',
                    'content_url': content_item.get('url', ''),
                    'source': content_item.get('source', ''),
                    'relevance_score': content_item.get('score', 0),
                    'ai_analysis': {
                        'significance_score': analysis_result.get('significance_score', 0),
                        'content_type': analysis_result.get('content_type', 'unknown'),
                        'competitive_impact': analysis_result.get('competitive_impact', 'unknown'),
                        'urgency': analysis_result.get('urgency', 'unknown'),
                        'key_insights': analysis_result.get('key_insights', []),
                        'engagement_indicators': analysis_result.get('engagement_indicators', []),
                        'sentiment_analysis': analysis_result.get('sentiment_analysis', 'neutral'),
                        'analysis_timestamp': datetime.now(timezone.utc).isoformat()
                    }
                },
                'is_read': False,
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            alert_id = await supabase_client.create_alert(alert_data)
            if alert_id:
                logger.info(f"🚨 Created intelligent Twitter alert: {alert_id}")
            else:
                logger.error("❌ Failed to create alert in Supabase")
                
        except Exception as e:
            logger.error(f"❌ Error creating intelligent Twitter alert: {e}")

    async def _create_content_change_alert(self, competitor_id: str, content_item: Dict[str, Any], analysis_result: Dict[str, Any], data_id: str):
        """Create an alert for Twitter content changes"""
        try:
            # Get competitor details to get user_id
            competitor_details = await supabase_client.get_competitor_details(competitor_id)
            user_id = competitor_details.get('user_id') if competitor_details else None
            
            alert_data = {
                'user_id': user_id,
                'competitor_id': str(competitor_id),
                'monitoring_data_id': data_id,
                'alert_type': 'twitter_content_change',
                'priority': 'medium',
                'title': f"Twitter Update: {content_item.get('title', 'Content Changed')[:100]}",
                'message': f"Twitter content has been updated: {analysis_result.get('alert_reason', 'Significant changes detected')}",
                'alert_metadata': {
                    'platform': 'twitter',
                    'content_url': content_item.get('url', ''),
                    'change_type': 'content_update',
                    'ai_analysis': analysis_result,
                    'detected_at': datetime.now(timezone.utc).isoformat()
                },
                'is_read': False,
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            alert_id = await supabase_client.create_alert(alert_data)
            if alert_id:
                logger.info(f"🔄 Created Twitter content change alert: {alert_id}")
                
        except Exception as e:
            logger.error(f"❌ Error creating Twitter content change alert: {e}")

    async def _fallback_analysis(self, competitor_id: str, competitor_name: str) -> Dict[str, Any]:
        """Fallback analysis when search client is not available"""
        logger.info(f"🐦 Using fallback analysis for {competitor_name}")
        
        return {
            "platform": "twitter",
            "competitor_id": competitor_id,
            "competitor_name": competitor_name,
            "status": "completed",
            "posts": [],
            "analysis_summary": f"Twitter monitoring for {competitor_name} completed with limited capabilities. Search client not available.",
            "insights": {
                "note": "Limited analysis due to missing search capabilities",
                "recommendation": "Configure TAVILY_API_KEY for enhanced Twitter intelligence",
                "analysis_timestamp": datetime.now(timezone.utc).isoformat()
            }
        }

    async def close(self):
        """Close any resources"""
        logger.info("🐦 Intelligent TwitterAgent closed")
