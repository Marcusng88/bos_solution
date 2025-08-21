"""
Intelligent Website Sub-Agent for Competitor Website Intelligence
Uses Crawl4AI intelligently to analyze competitor websites and detect changes
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import hashlib
import json
import re
from urllib.parse import urljoin, urlparse

# Import Windows compatibility utilities
from app.core.windows_compatibility import setup_windows_compatibility

# Import multiprocessing crawler (solves NotImplementedError)
from app.services.monitoring.agents.sub_agents.multiprocessing_crawler import (
    MultiprocessingCrawler, 
    crawl_websites_multiprocessing,
    crawl_websites_multiprocessing_batched
)

# Import crawling dependencies conditionally (for fallback)
try:
    from crawl4ai import AsyncWebCrawler
    from crawl4ai.extraction_strategy import LLMExtractionStrategy
    CRAWL4AI_AVAILABLE = True
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"Crawl4AI dependencies not available: {e}")
    CRAWL4AI_AVAILABLE = False

# Import langchain dependencies conditionally
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"LangChain dependencies not available: {e}")
    LANGCHAIN_AVAILABLE = False

from app.core.config import settings
from app.services.monitoring.supabase_client import supabase_client

logger = logging.getLogger(__name__)


class WebsiteAgent:
    """Intelligent website agent for competitor website intelligence using Crawl4AI"""

    def __init__(self):
        logger.info("🌐 Intelligent WebsiteAgent initializing...")
        self.crawl_count = 0
        self.crawl_limit = 10  # Limit for intelligent crawling
        
        # Crawling strategy configuration
        self.crawling_strategy = "batch"  # Options: "batch", "sequential", "single"
        self.batch_size = 2  # Number of URLs to process in each batch
        self.delay_between_requests = 1.0  # Delay in seconds between requests for multiprocessing isolation

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

        # Check Crawl4AI availability
        if not CRAWL4AI_AVAILABLE:
            logger.warning("Crawl4AI not available - website analysis will be limited")

        logger.info("🌐 Intelligent WebsiteAgent initialization completed")

    def configure_crawling_strategy(self, strategy: str = "batch", batch_size: int = 2, delay: float = 1.0):
        """
        Configure the crawling strategy and parameters
        
        Args:
            strategy: Crawling strategy - "batch", "sequential", or "single"
            batch_size: Number of URLs to process in each batch (for batch strategy)
            delay: Delay in seconds between requests for isolation
        """
        valid_strategies = ["batch", "sequential", "single"]
        if strategy not in valid_strategies:
            logger.warning(f"Invalid strategy '{strategy}'. Using 'batch' instead.")
            strategy = "batch"
        
        self.crawling_strategy = strategy
        self.batch_size = max(1, batch_size)
        self.delay_between_requests = max(0.1, delay)
        
        logger.info(f"🔧 Crawling strategy configured: {strategy}, batch_size: {self.batch_size}, delay: {self.delay_between_requests}s")

    async def analyze_competitor(self, competitor_id: str, competitor_name: str) -> Dict[str, Any]:
        """
        Intelligently analyze a competitor's website for changes and insights
        
        Args:
            competitor_id: Database ID of the competitor
            competitor_name: Name of the competitor to analyze
            
        Returns:
            Dict containing analysis results and extracted content
        """
        self.crawl_count = 0  # Reset crawl count for each analysis

        try:
            logger.info(f"🌐 Starting intelligent website analysis for {competitor_name}")
            
            if not CRAWL4AI_AVAILABLE:
                return {
                    "platform": "website", 
                    "competitor_id": competitor_id,
                    "competitor_name": competitor_name,
                    "status": "completed",
                    "posts": [], 
                    "error": "Crawl4AI not available"
                }

            # Step 1: Generate intelligent URLs to crawl
            urls_to_crawl = await self._generate_intelligent_urls(competitor_name)
            logger.info(f"🔍 Generated {len(urls_to_crawl)} intelligent URLs to crawl")

            if not urls_to_crawl:
                logger.info(f"ℹ️  No URLs found to crawl for {competitor_name}")
                return {
                    "platform": "website",
                    "competitor_id": competitor_id,
                    "competitor_name": competitor_name,
                    "status": "completed",
                    "posts": [],
                    "analysis_summary": f"No crawlable URLs found for {competitor_name}"
                }

            # Step 2: Crawl and analyze websites
            all_content = await self._crawl_websites_intelligently(urls_to_crawl, competitor_name)
            logger.info(f"📰 Crawled {len(all_content)} website pages")

            if not all_content:
                logger.info(f"ℹ️  No website content extracted for {competitor_name}")
                return {
                    "platform": "website",
                    "competitor_id": competitor_id,
                    "competitor_name": competitor_name,
                    "status": "completed",
                    "posts": [],
                    "analysis_summary": f"No website content extracted for {competitor_name}"
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
                        competitor_id, 'website', content_item.get('content_hash', '')
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
                        
                        logger.info(f"✅ Saved website content: {content_item.get('title', 'Unknown')[:50]}...")
                        
                        # Create alert if deemed significant
                        if analysis_result['is_alert_worthy']:
                            await self._create_intelligent_alert(competitor_id, content_item, analysis_result, data_id)
                            alerts_created += 1
                            logger.info(f"🚨 Created alert for significant content: {content_item.get('title', 'Unknown')[:50]}...")

                except Exception as e:
                    logger.error(f"❌ Error processing website content: {e}")
                    continue

            logger.info(f"✅ Website analysis completed for {competitor_name}")
            logger.info(f"   📊 Processed {len(processed_posts)} content items")
            logger.info(f"   🚨 Created {alerts_created} alerts")
            
            return {
                "platform": "website",
                "competitor_id": competitor_id,
                "competitor_name": competitor_name,
                "status": "completed",
                "posts": processed_posts,
                "analysis_summary": f"Intelligently analyzed {len(processed_posts)} website pages for {competitor_name}. Created {alerts_created} alerts for significant content.",
                "insights": {
                    "total_pages_analyzed": len(processed_posts),
                    "alerts_created": alerts_created,
                    "urls_crawled": len(urls_to_crawl),
                    "analysis_timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error in intelligent website analysis for competitor {competitor_id}: {e}")
            return {
                "platform": "website",
                "competitor_id": competitor_id,
                "competitor_name": competitor_name,
                "status": "failed",
                "posts": [],
                "error": str(e)
            }

    async def _generate_intelligent_urls(self, competitor_name: str) -> List[str]:
        """Generate intelligent URLs to crawl using AI or heuristics"""
        try:
            if self.llm:
                # Use AI to generate intelligent URLs
                prompt = f"""
Generate 5-8 intelligent website URLs to crawl for the competitor "{competitor_name}".

The URLs should target:
1. Main company website homepage
2. News/press releases page
3. Products/services page
4. About us page
5. Blog or insights page
6. Careers page
7. Investor relations page

Generate realistic URLs for "{competitor_name}" following common website patterns.
Return only the URLs, one per line, without additional text.

Example format:
https://www.{competitor_name.lower().replace(' ', '')}.com
https://www.{competitor_name.lower().replace(' ', '')}.com/news
https://www.{competitor_name.lower().replace(' ', '')}.com/products
"""
                
                response = await self.llm.ainvoke(prompt)
                urls = [url.strip() for url in response.content.strip().split('\n') if url.strip().startswith('http')]
                
                # Filter and validate URLs
                valid_urls = []
                for url in urls[:8]:  # Limit to 8 URLs
                    if self._is_valid_url(url):
                        valid_urls.append(url)
                
                if valid_urls:
                    logger.info(f"🧠 AI generated {len(valid_urls)} URLs to crawl")
                    return valid_urls
            
            # Fallback to heuristic URLs
            logger.info("🔍 Using heuristic URL generation")
            return self._generate_heuristic_urls(competitor_name)
            
        except Exception as e:
            logger.error(f"❌ Error generating URLs: {e}")
            return self._generate_heuristic_urls(competitor_name)

    def _generate_heuristic_urls(self, competitor_name: str) -> List[str]:
        """Generate URLs using heuristics"""
        # Clean competitor name for URL generation
        clean_name = re.sub(r'[^a-zA-Z0-9]', '', competitor_name.lower())
        
        base_patterns = [
            f"https://www.{clean_name}.com",
            f"https://{clean_name}.com",
            f"https://www.{clean_name}.io",
            f"https://{clean_name}.io"
        ]
        
        # Try to find valid base URL first
        for base_url in base_patterns:
            if self._is_potentially_valid_domain(base_url):
                return [
                    base_url,
                    f"{base_url}/news",
                    f"{base_url}/press",
                    f"{base_url}/products",
                    f"{base_url}/about",
                    f"{base_url}/blog",
                    f"{base_url}/careers",
                    f"{base_url}/investors"
                ]
        
        # If no patterns match, return the first pattern as fallback
        return [base_patterns[0]]

    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

    def _is_potentially_valid_domain(self, url: str) -> bool:
        """Check if domain could potentially be valid (simple heuristic)"""
        try:
            result = urlparse(url)
            domain = result.netloc.lower()
            # Basic checks for common patterns
            return len(domain) > 4 and '.' in domain and not any(char in domain for char in [' ', '<', '>', '"'])
        except:
            return False

    async def _crawl_single_url_multiprocessing(self, url: str, extraction_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Crawl a single URL using multiprocessing crawler for maximum isolation"""
        try:
            logger.info(f"🕷️ Crawling single URL with multiprocessing: {url}")
            
            # Use the multiprocessing crawler for single URL
            results = crawl_websites_multiprocessing(
                urls=[url],
                extraction_config=extraction_config,
                max_workers=1
            )
            
            if results and len(results) > 0:
                return results[0]
            else:
                return {
                    'url': url,
                    'status': 'failed',
                    'error': 'No results returned from multiprocessing crawler'
                }
                
        except Exception as e:
            logger.error(f"❌ Error crawling single URL {url}: {e}")
            return {
                'url': url,
                'status': 'error',
                'error': str(e)
            }

    async def _crawl_urls_sequentially(self, urls: List[str], competitor_name: str) -> List[Dict[str, Any]]:
        """Crawl URLs one by one for maximum isolation and control"""
        try:
            logger.info(f"🔄 Starting sequential crawling for {len(urls)} URLs")
            
            # Prepare extraction configuration
            extraction_config = None
            if self.llm and LANGCHAIN_AVAILABLE:
                extraction_config = {
                    'use_llm': True,
                    'api_key': settings.GOOGLE_API_KEY,
                    'schema': {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "main_content": {"type": "string"},
                            "key_announcements": {"type": "array", "items": {"type": "string"}},
                            "product_updates": {"type": "array", "items": {"type": "string"}},
                            "business_updates": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                }
            
            all_content = []
            
            # Crawl each URL individually
            for i, url in enumerate(urls):
                if self.crawl_count >= self.crawl_limit:
                    logger.info(f"🛑 Reached crawl limit ({self.crawl_limit}), stopping")
                    break
                
                logger.info(f"🔄 Crawling URL {i+1}/{len(urls)}: {url}")
                
                # Crawl single URL with multiprocessing
                result = await self._crawl_single_url_multiprocessing(url, extraction_config)
                
                # Process result immediately
                if result.get('status') == 'success':
                    content_item = {
                        'url': result['url'],
                        'title': result.get('title', ''),
                        'content': result.get('content', ''),
                        'extracted_data': result.get('extracted_data', {}),
                        'crawled_at': result.get('crawled_at', datetime.now(timezone.utc).isoformat()),
                        'content_hash': result.get('content_hash', '')
                    }
                    
                    # Only include if there's meaningful content
                    if len(content_item['content']) > 100:
                        all_content.append(content_item)
                        self.crawl_count += 1
                        logger.info(f"   ✅ Extracted content from {url}")
                    else:
                        logger.info(f"   ⚠️  Insufficient content from {url}")
                else:
                    logger.warning(f"   ❌ Failed to crawl {url}: {result.get('error', 'Unknown error')}")
                
                # Small delay between URLs for isolation
                if i < len(urls) - 1:
                    await asyncio.sleep(1.0)
            
            logger.info(f"📊 Sequential crawling completed: {len(all_content)} successful extractions")
            return all_content
            
        except Exception as e:
            logger.error(f"❌ Error in sequential crawling: {e}")
            return []

    async def _crawl_websites_intelligently(self, urls: List[str], competitor_name: str) -> List[Dict[str, Any]]:
        """Crawl websites using isolated intelligent extraction with configurable orchestration strategy"""
        try:
            logger.info(f"🔒 Using multiprocessing crawler with {self.crawling_strategy} strategy for {len(urls)} URLs")
            
            # Prepare extraction configuration for multiprocessing crawler
            extraction_config = None
            if self.llm and LANGCHAIN_AVAILABLE:
                extraction_config = {
                    'use_llm': True,
                    'api_key': settings.GOOGLE_API_KEY,
                    'schema': {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "main_content": {"type": "string"},
                            "key_announcements": {"type": "array", "items": {"type": "string"}},
                            "product_updates": {"type": "array", "items": {"type": "string"}},
                            "business_updates": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                }
            
            # Use configured crawling strategy
            all_content = []
            try:
                # Limit URLs to crawl limit
                urls_to_crawl = urls[:self.crawl_limit]
                logger.info(f"🕷️ Starting {self.crawling_strategy} crawling for {len(urls_to_crawl)} URLs")
                
                if self.crawling_strategy == "single":
                    # Crawl URLs one by one for maximum isolation
                    all_content = await self._crawl_urls_sequentially(urls_to_crawl, competitor_name)
                    
                elif self.crawling_strategy == "sequential":
                    # Crawl URLs one by one with delays
                    all_content = await self._crawl_urls_sequentially(urls_to_crawl, competitor_name)
                    
                elif self.crawling_strategy == "batch":
                    # Process URLs in configurable batches
                    for i in range(0, len(urls_to_crawl), self.batch_size):
                        batch_urls = urls_to_crawl[i:i + self.batch_size]
                        logger.info(f"🔄 Processing batch {i//self.batch_size + 1}: {len(batch_urls)} URLs")
                        
                        # Call multiprocessing crawler for this batch
                        batch_results = crawl_websites_multiprocessing_batched(
                            urls=batch_urls,
                            extraction_config=extraction_config,
                            max_workers=1,  # Single worker per batch for isolation
                            batch_size=len(batch_urls)
                        )
                        
                        # Process batch results immediately
                        for result in batch_results:
                            if result.get('status') == 'success':
                                content_item = {
                                    'url': result['url'],
                                    'title': result.get('title', ''),
                                    'content': result.get('content', ''),
                                    'extracted_data': result.get('extracted_data', {}),
                                    'crawled_at': result.get('crawled_at', datetime.now(timezone.utc).isoformat()),
                                    'content_hash': result.get('content_hash', '')
                                }
                                
                                # Only include if there's meaningful content
                                if len(content_item['content']) > 100:  # At least 100 characters
                                    all_content.append(content_item)
                                    self.crawl_count += 1
                                    logger.info(f"   ✅ Extracted content from {result['url']}")
                                else:
                                    logger.info(f"   ⚠️  Insufficient content from {result['url']}")
                            else:
                                logger.warning(f"   ❌ Failed to crawl {result['url']}: {result.get('error', 'Unknown error')}")
                        
                        # Delay between batches to ensure isolation
                        if i + self.batch_size < len(urls_to_crawl):
                            await asyncio.sleep(self.delay_between_requests)
                
                logger.info(f"📊 Successfully crawled {len(all_content)} websites using {self.crawling_strategy} strategy")
                
            except Exception as e:
                logger.error(f"❌ Error with {self.crawling_strategy} crawler: {e}")
                # Fallback to sequential crawling if configured strategy fails
                logger.info("🔄 Falling back to sequential crawling...")
                all_content = await self._crawl_urls_sequentially(urls[:self.crawl_limit], competitor_name)
                
                # If sequential crawling also fails, try multiprocessing fallback
                if not all_content:
                    logger.info("🔄 Falling back to multiprocessing fallback...")
                    all_content = await self._fallback_multiprocessing_crawling(urls[:self.crawl_limit])
            
            return all_content
            
        except Exception as e:
            logger.error(f"❌ Error in intelligent website crawling: {e}")
            return []

    async def _fallback_multiprocessing_crawling(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Fallback method using multiprocessing when other methods fail"""
        try:
            logger.info("🔄 Using multiprocessing fallback crawling method")
            
            if not CRAWL4AI_AVAILABLE:
                logger.warning("⚠️  Crawl4AI not available for fallback")
                return []
            
            # Use multiprocessing crawler as fallback
            all_content = crawl_websites_multiprocessing(
                urls=urls[:self.crawl_limit],
                extraction_config=None,  # No LLM extraction for fallback
                max_workers=2  # Use 2 workers for fallback
            )
            
            # Process results
            processed_content = []
            for result in all_content:
                if result.get('status') == 'success':
                    content_item = {
                        'url': result['url'],
                        'title': result.get('title', ''),
                        'content': result.get('content', ''),
                        'extracted_data': result.get('extracted_data', {}),
                        'crawled_at': result.get('crawled_at', datetime.now(timezone.utc).isoformat()),
                        'content_hash': result.get('content_hash', '')
                    }
                    
                    # Only include if there's meaningful content
                    if len(content_item['content']) > 100:
                        processed_content.append(content_item)
                        self.crawl_count += 1
                        logger.info(f"   ✅ Fallback extracted content from {result['url']}")
                    else:
                        logger.info(f"   ⚠️  Insufficient content from {result['url']}")
                else:
                    logger.warning(f"   ❌ Fallback failed to crawl {result['url']}: {result.get('error', 'Unknown error')}")

            logger.info(f"📊 Multiprocessing fallback crawling completed: {len(processed_content)} websites")
            return processed_content
            
        except Exception as e:
            logger.error(f"❌ Error in multiprocessing fallback crawling: {e}")
            return []

    async def _analyze_content_intelligence(self, content_item: Dict[str, Any], competitor_name: str) -> Dict[str, Any]:
        """Analyze website content using AI to determine significance"""
        try:
            if self.llm:
                return await self._ai_content_analysis(content_item, competitor_name)
            else:
                return self._heuristic_content_analysis(content_item, competitor_name)
                
        except Exception as e:
            logger.error(f"❌ Error in content intelligence analysis: {e}")
            return self._heuristic_content_analysis(content_item, competitor_name)

    async def _ai_content_analysis(self, content_item: Dict[str, Any], competitor_name: str) -> Dict[str, Any]:
        """Use AI to analyze website content for competitive intelligence"""
        try:
            title = content_item.get('title', '')
            content = content_item.get('content', '')[:1500]  # First 1500 chars
            url = content_item.get('url', '')
            extracted_data = content_item.get('extracted_data', {})
            
            prompt = f"""
Analyze this website content for competitive intelligence about "{competitor_name}":

URL: {url}
TITLE: {title}
CONTENT: {content}
EXTRACTED DATA: {json.dumps(extracted_data, default=str)[:500]}

Your analysis should determine:
1. Is this content ALERT-WORTHY for competitive intelligence?
2. What are the key business insights about the competitor?
3. What strategic implications does this have?

ALERT-WORTHY criteria for website content:
- New product launches or major updates
- Significant business announcements
- Strategic partnerships or acquisitions
- Major website redesigns or rebranding
- Pricing changes or new service offerings
- Leadership announcements or company pivots
- Crisis communications or negative developments
- Regulatory compliance or legal updates

Provide your response in this JSON format:
{{
    "is_alert_worthy": true/false,
    "alert_reason": "Brief reason if alert-worthy, null if not",
    "significance_score": 1-10,
    "summary": "Brief competitive intelligence summary (max 200 words)",
    "key_insights": ["insight1", "insight2", "insight3"],
    "content_type": "homepage/product/news/blog/about/other",
    "competitive_impact": "high/medium/low",
    "urgency": "immediate/high/medium/low",
    "changes_detected": ["change1", "change2"] or []
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
        url = content_item.get('url', '').lower()
        extracted_data = content_item.get('extracted_data', {})
        
        # Check for alert-worthy keywords
        alert_keywords = [
            'launch', 'new', 'announcement', 'update', 'partnership', 'acquisition',
            'merger', 'funding', 'expansion', 'product', 'service', 'pricing'
        ]
        
        # Check URL type
        url_indicators = {
            'news': 'news' in url or 'press' in url or 'blog' in url,
            'product': 'product' in url or 'service' in url,
            'about': 'about' in url or 'company' in url,
            'homepage': url.count('/') <= 3
        }
        
        # Check for alert keywords in title/content
        has_alert_keywords = any(keyword in title or keyword in content for keyword in alert_keywords)
        
        # Check extracted data for significant information
        has_extracted_updates = any(
            extracted_data.get(key, []) for key in ['key_announcements', 'product_updates', 'business_updates']
        )
        
        # Determine significance
        significance_score = 1
        is_alert_worthy = False
        alert_reason = None
        
        if url_indicators['news'] and has_alert_keywords:
            is_alert_worthy = True
            alert_reason = "News/Press page with significant keywords"
            significance_score = 8
        elif url_indicators['product'] and has_alert_keywords:
            is_alert_worthy = True
            alert_reason = "Product page with update keywords"
            significance_score = 7
        elif has_extracted_updates:
            is_alert_worthy = True
            alert_reason = "Extracted structured business updates"
            significance_score = 6
        elif url_indicators['homepage'] and has_alert_keywords:
            is_alert_worthy = True
            alert_reason = "Homepage with significant announcements"
            significance_score = 7
        
        # Generate summary
        content_type = 'homepage' if url_indicators['homepage'] else (
            'news' if url_indicators['news'] else (
                'product' if url_indicators['product'] else (
                    'about' if url_indicators['about'] else 'other'
                )
            )
        )
        
        summary = f"Website analysis for {competitor_name}: '{title}' from {content_type} page. "
        
        if has_alert_keywords:
            summary += "Contains business-significant keywords. "
        if has_extracted_updates:
            summary += "Structured business updates detected. "
        
        return {
            "is_alert_worthy": is_alert_worthy,
            "alert_reason": alert_reason,
            "significance_score": significance_score,
            "summary": summary,
            "key_insights": [
                f"Content type: {content_type}",
                f"Contains business keywords: {has_alert_keywords}",
                f"Structured updates: {has_extracted_updates}",
                f"URL: {content_item.get('url', '')}"
            ],
            "content_type": content_type,
            "competitive_impact": "high" if significance_score >= 7 else ("medium" if significance_score >= 5 else "low"),
            "urgency": "high" if significance_score >= 8 else ("medium" if significance_score >= 6 else "low"),
            "changes_detected": list(extracted_data.get('key_announcements', [])) + list(extracted_data.get('product_updates', []))
        }

    def _create_monitoring_data(self, content_item: Dict[str, Any], analysis_result: Dict[str, Any], competitor_id: str) -> Dict[str, Any]:
        """Create monitoring data structure for Supabase"""
        content_text = f"{content_item.get('title', '')}\n\n{content_item.get('content', '')[:1000]}"
        
        return {
            'competitor_id': str(competitor_id),
            'platform': 'website',
            'post_id': content_item.get('content_hash', ''),
            'post_url': content_item.get('url', ''),
            'content_text': content_text,
            'content_hash': content_item.get('content_hash', ''),
            'media_urls': [],  # Website content typically doesn't have direct media URLs
            'engagement_metrics': {
                'significance_score': analysis_result.get('significance_score', 0),
                'content_length': len(content_item.get('content', ''))
            },
            'author_username': 'website',
            'author_display_name': 'Official Website',
            'post_type': analysis_result.get('content_type', 'webpage'),
            'language': 'en',  # Default to English
            'sentiment_score': 0.0,  # Default neutral
            'detected_at': datetime.now(timezone.utc).isoformat(),
            'posted_at': content_item.get('crawled_at', datetime.now(timezone.utc).isoformat()),
            'is_new_post': True,
            'is_content_change': False
        }

    def _has_content_changed(self, existing_content: Dict[str, Any], new_content: Dict[str, Any]) -> bool:
        """Check if website content has changed significantly"""
        old_hash = existing_content.get('content_hash', '')
        new_hash = new_content.get('content_hash', '')
        return old_hash != new_hash

    async def _create_intelligent_alert(self, competitor_id: str, content_item: Dict[str, Any], analysis_result: Dict[str, Any], data_id: str):
        """Create an intelligent alert for significant website content"""
        try:
            # Get competitor details to get user_id
            competitor_details = await supabase_client.get_competitor_details(competitor_id)
            user_id = competitor_details.get('user_id') if competitor_details else None
            
            alert_data = {
                'user_id': user_id,
                'competitor_id': str(competitor_id),
                'monitoring_data_id': data_id,
                'alert_type': 'website_intelligence',
                'priority': analysis_result.get('urgency', 'medium'),
                'title': f"Website Alert: {content_item.get('title', 'Significant Content')[:100]}",
                'message': analysis_result.get('alert_reason', 'AI detected significant website activity'),
                'alert_metadata': {
                    'platform': 'website',
                    'content_url': content_item.get('url', ''),
                    'content_type': analysis_result.get('content_type', 'unknown'),
                    'ai_analysis': {
                        'significance_score': analysis_result.get('significance_score', 0),
                        'competitive_impact': analysis_result.get('competitive_impact', 'unknown'),
                        'urgency': analysis_result.get('urgency', 'unknown'),
                        'key_insights': analysis_result.get('key_insights', []),
                        'changes_detected': analysis_result.get('changes_detected', []),
                        'analysis_timestamp': datetime.now(timezone.utc).isoformat()
                    }
                },
                'is_read': False,
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            alert_id = await supabase_client.create_alert(alert_data)
            if alert_id:
                logger.info(f"🚨 Created intelligent website alert: {alert_id}")
            else:
                logger.error("❌ Failed to create alert in Supabase")
                
        except Exception as e:
            logger.error(f"❌ Error creating intelligent alert: {e}")

    async def _create_content_change_alert(self, competitor_id: str, content_item: Dict[str, Any], analysis_result: Dict[str, Any], data_id: str):
        """Create an alert for website content changes"""
        try:
            # Get competitor details to get user_id
            competitor_details = await supabase_client.get_competitor_details(competitor_id)
            user_id = competitor_details.get('user_id') if competitor_details else None
            
            alert_data = {
                'user_id': user_id,
                'competitor_id': str(competitor_id),
                'monitoring_data_id': data_id,
                'alert_type': 'website_content_change',
                'priority': 'medium',
                'title': f"Website Update: {content_item.get('title', 'Content Changed')[:100]}",
                'message': f"Website content has been updated: {analysis_result.get('alert_reason', 'Significant changes detected')}",
                'alert_metadata': {
                    'platform': 'website',
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
                logger.info(f"🔄 Created website content change alert: {alert_id}")
                
        except Exception as e:
            logger.error(f"❌ Error creating content change alert: {e}")

    async def close(self):
        """Close any resources"""
        logger.info("🌐 Intelligent WebsiteAgent closed")
