"""
Intelligent YouTube Sub-Agent for Competitor Analysis
Uses YouTube Data API intelligently to analyze competitor videos from today only
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta, timezone
import hashlib
import json


# Set up logger for this module
logger = logging.getLogger(__name__)

# Import langchain dependencies conditionally
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️  LangChain dependencies not available: {e}")
    LANGCHAIN_AVAILABLE = False

# Import Google API dependencies conditionally
try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_API_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️  Google API dependencies not available: {e}")
    GOOGLE_API_AVAILABLE = False

from app.core.config import settings
from app.services.monitoring.supabase_client import supabase_client


class YouTubeAgent:
    """Intelligent YouTube agent for competitor analysis using YouTube Data API"""
    
    def __init__(self):
        logger.info("🎬 Intelligent YouTubeAgent initializing...")
        
        # Initialize LLM for intelligent analysis
        self.llm = None
        if LANGCHAIN_AVAILABLE:
            try:
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash-lite",
                    api_key=settings.GOOGLE_API_KEY,
                    temperature=0.3  # Slightly more creative for search terms
                )
                logger.info("✅ LLM initialized successfully")
            except Exception as e:
                logger.warning(f"⚠️  Failed to initialize LLM: {e}")
        else:
            logger.info("ℹ️  LLM not available - will use heuristic analysis")
        
        # Initialize YouTube API client
        self.youtube_api = None
        if GOOGLE_API_AVAILABLE and hasattr(settings, 'youtube_api_key') and settings.youtube_api_key:
            try:
                self.youtube_api = build('youtube', 'v3', developerKey=settings.youtube_api_key)
                logger.info("✅ YouTube Data API client initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize YouTube API client: {e}")
        elif not GOOGLE_API_AVAILABLE:
            logger.warning("⚠️  Google API client not available - YouTube analysis will be limited")
        elif not hasattr(settings, 'youtube_api_key') or not settings.youtube_api_key:
            logger.warning("⚠️  No YouTube API key configured - YouTube analysis will be limited")
        
        # Log the final status
        if self.youtube_api:
            logger.info("🎬 YouTube API client is ready for analysis")
        else:
            logger.warning("⚠️  YouTube API client is not available - will return empty results")
        
        logger.info("🎬 Intelligent YouTubeAgent initialization completed")
    
    async def analyze_competitor(self, competitor_id: str, competitor_name: str = None) -> Dict[str, Any]:
        """
        Intelligently analyze a competitor's YouTube presence
        
        Args:
            competitor_id: Database ID of the competitor
            competitor_name: Name of the competitor to search for
            
        Returns:
            Dict containing analysis results and extracted videos
        """
        try:
            logger.info(f"🎬 Starting intelligent YouTube analysis for competitor {competitor_id}")
            
            # Use provided competitor name or fallback
            if not competitor_name or not isinstance(competitor_name, str) or competitor_name.strip() == "":
                logger.warning(f"⚠️  No competitor name available for {competitor_id}")
                competitor_name = f"Competitor_{competitor_id}"
            else:
                # Clean the competitor name
                competitor_name = competitor_name.strip()
            
            logger.info(f"🎯 Analyzing YouTube content for: {competitor_name}")
            
            # Check if we have a valid competitor name to search for
            if not competitor_name or competitor_name.strip() == "":
                logger.warning("⚠️  Invalid competitor name - returning empty analysis")
                return {
                    "platform": "youtube",
                    "competitor_id": competitor_id,
                    "competitor_name": competitor_name or "Unknown",
                    "status": "completed",
                    "posts": [],
                    "analysis_summary": "Invalid competitor name provided",
                    "error": "Competitor name is empty or invalid"
                }
            
            if not self.youtube_api:
                logger.warning("⚠️  YouTube API not available - returning empty analysis")
                return {
                    "platform": "youtube",
                    "competitor_id": competitor_id,
                    "competitor_name": competitor_name,
                    "status": "completed",
                    "posts": [],
                    "analysis_summary": "YouTube API not available",
                    "error": "YouTube API client not initialized"
                }
            

            
            # Step 1: Generate intelligent search queries
            search_queries = await self._generate_intelligent_search_queries(competitor_name)
            logger.info(f"🔍 Generated {len(search_queries)} intelligent search queries")
            
            # Validate search queries
            if not search_queries or len(search_queries) == 0:
                logger.warning("⚠️  No valid search queries generated")
                return {
                    "platform": "youtube",
                    "competitor_id": competitor_id,
                    "competitor_name": competitor_name,
                    "status": "completed",
                    "posts": [],
                    "analysis_summary": f"No valid search queries could be generated for '{competitor_name}'",
                    "error": "Failed to generate search queries"
                }
            
            # Step 2: Search for videos from today only
            today_videos = await self._search_todays_videos(search_queries)
            logger.info(f"📹 Found {len(today_videos)} videos from today")
            
            if not today_videos:
                logger.info(f"ℹ️  No videos found from today for {competitor_name}")
                return {
                    "platform": "youtube",
                    "competitor_id": competitor_id,
                    "competitor_name": competitor_name,
                    "status": "completed",
                    "posts": [],
                    "analysis_summary": f"No YouTube videos found from today for {competitor_name}"
                }
            
            # Step 2.5: Filter videos for relevance to competitor
            relevant_videos = await self._filter_relevant_videos_ai(today_videos, competitor_name)
            logger.info(f"🎯 Filtered to {len(relevant_videos)} relevant videos for {competitor_name}")
            
            if not relevant_videos:
                logger.info(f"ℹ️  No relevant videos found for {competitor_name}")
                return {
                    "platform": "youtube",
                    "competitor_id": competitor_id,
                    "competitor_name": competitor_name,
                    "status": "completed",
                    "posts": [],
                    "analysis_summary": f"No relevant YouTube videos found from today for {competitor_name} (found {len(today_videos)} total videos but none met relevance criteria)",
                    "insights": {
                        "total_videos_found": len(today_videos),
                        "relevant_videos_analyzed": 0,
                        "relevance_filtering_applied": True,
                        "search_queries_used": len(search_queries),
                        "analysis_timestamp": datetime.now(timezone.utc).isoformat()
                    }
                }
            
            # Step 3: Analyze each video and determine significance
            processed_posts = []
            alerts_created = 0
            
            for video in relevant_videos:
                try:
                    # Get detailed video information
                    video_details = await self._get_video_details(video['video_id'])
                    if not video_details:
                        continue
                    
                    # Analyze the video content using AI
                    analysis_result = await self._analyze_video_intelligence(video_details, competitor_name)
                    
                    # Create monitoring data
                    post_data = self._create_monitoring_data(video_details, analysis_result, competitor_id)
                    
                    # Save to Supabase
                    data_id = await supabase_client.save_monitoring_data(post_data)
                    
                    if data_id:
                        processed_posts.append({
                            "id": data_id,
                            "post_id": video_details['video_id'],
                            "title": video_details['title'],
                            "url": video_details['url'],
                            "engagement": post_data["engagement_metrics"],
                            "ai_analysis": analysis_result['summary'],
                            "is_alert_worthy": analysis_result['is_alert_worthy'],
                            "alert_reason": analysis_result.get('alert_reason', '')
                        })
                        
                        logger.info(f"✅ Saved video: {video_details['title'][:50]}...")
                        
                        # Create alert if deemed significant
                        if analysis_result['is_alert_worthy']:
                            await self._create_intelligent_alert(competitor_id, video_details, analysis_result, data_id)
                            alerts_created += 1
                            logger.info(f"🚨 Created alert for significant video: {video_details['title'][:50]}...")
                
                except Exception as e:
                    logger.error(f"❌ Error processing video: {e}")
                    continue
            
            logger.info(f"✅ YouTube analysis completed for {competitor_name}")
            logger.info(f"   📊 Processed {len(processed_posts)} videos")
            logger.info(f"   🚨 Created {alerts_created} alerts")
            
            return {
                "platform": "youtube",
                "competitor_id": competitor_id,
                "competitor_name": competitor_name,
                "status": "completed",
                "posts": processed_posts,
                "analysis_summary": f"Intelligently analyzed {len(processed_posts)} relevant YouTube videos from today for {competitor_name} (filtered from {len(today_videos)} total videos). Created {alerts_created} alerts for significant content.",
                "insights": {
                    "total_videos_found": len(today_videos),
                    "relevant_videos_analyzed": len(processed_posts),
                    "alerts_created": alerts_created,
                    "search_queries_used": len(search_queries),
                    "relevance_filtering_applied": True,
                    "analysis_timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
                
        except Exception as e:
            logger.error(f"❌ Error in intelligent YouTube analysis for competitor {competitor_id}: {e}")
            return {
                "platform": "youtube",
                "competitor_id": competitor_id,
                "competitor_name": competitor_name or f"Competitor_{competitor_id}",
                "status": "failed",
                "posts": [],
                "error": str(e)
            }
    
    async def _generate_intelligent_search_queries(self, competitor_name: str) -> List[str]:
        """Generate intelligent search queries using AI or heuristics"""
        try:
            # Validate competitor name
            if not competitor_name or not isinstance(competitor_name, str) or competitor_name.strip() == "":
                logger.error(f"❌ Invalid competitor name: {competitor_name}")
                return []
            
            competitor_name = competitor_name.strip()
            
            if self.llm:
                # Use AI to generate intelligent search queries
                prompt = f"""
Generate 5-7 highly specific YouTube search queries to find videos DIRECTLY about the company "{competitor_name}" that were published today.

The queries MUST be designed to find ONLY content that is directly related to {competitor_name}:
1. Official company announcements and news
2. Product launches and updates from {competitor_name}
3. Reviews of {competitor_name} products
4. Company earnings, partnerships, or business news
5. Official {competitor_name} channel content

IMPORTANT: Make queries VERY specific to avoid unrelated results. Use quotes and exact company names.
Focus on finding content that is clearly about {competitor_name}, not just mentioning similar words.

Example format:
"{competitor_name}" official
"{competitor_name}" company news today
"{competitor_name}" product announcement
"{competitor_name}" earnings report
"{competitor_name}" partnership
"""
                
                response = await self.llm.ainvoke(prompt)
                queries = [q.strip() for q in response.content.strip().split('\n') if q.strip()]
                
                # Filter out empty queries and limit to 7
                queries = [q for q in queries if len(q) > 3][:7]
                
                if queries:
                    logger.info(f"🧠 AI generated {len(queries)} search queries")
                    return queries
            
            # Fallback to heuristic queries
            logger.info("🔍 Using heuristic search queries")
            heuristic_queries = self._generate_heuristic_queries(competitor_name)
            
            if not heuristic_queries:
                logger.error("❌ Failed to generate heuristic queries")
                return []
            
            return heuristic_queries
            
        except Exception as e:
            logger.error(f"❌ Error generating search queries: {e}")
            return self._generate_heuristic_queries(competitor_name)
    
    def _generate_heuristic_queries(self, competitor_name: str) -> List[str]:
        """Generate search queries using heuristics"""
        # Validate competitor name
        if not competitor_name or not isinstance(competitor_name, str) or competitor_name.strip() == "":
            logger.error(f"❌ Invalid competitor name for heuristic queries: {competitor_name}")
            return []
        
        competitor_name = competitor_name.strip()
        
        # Generate highly specific queries to avoid unrelated results
        queries = [
            f'"{competitor_name}" official',
            f'"{competitor_name}" company news',
            f'"{competitor_name}" announcement',
            f'"{competitor_name}" product launch',
            f'"{competitor_name}" earnings',
            f'"{competitor_name}" partnership',
            f'"{competitor_name}" business update'
        ]
        
        logger.info(f"🔍 Generated {len(queries)} heuristic search queries for '{competitor_name}'")
        return queries
    
    async def _search_todays_videos(self, search_queries: List[str]) -> List[Dict[str, Any]]:
        """Search for videos published today using the generated queries"""
        try:
            # Validate search queries
            if not search_queries or not isinstance(search_queries, list) or len(search_queries) == 0:
                logger.warning("⚠️  No search queries provided for video search")
                return []
            
            # Calculate today's date range
            today = datetime.now(timezone.utc)
            today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
            published_after = today_start.isoformat().replace('+00:00', 'Z')
            
            all_videos = []
            seen_video_ids = set()
            
            for query in search_queries:
                try:
                    logger.info(f"🔍 Searching YouTube for: '{query}' (today only)")
                    
                    search_response = self.youtube_api.search().list(
                        q=query,
                        part='snippet',
                        type='video',
                        publishedAfter=published_after,
                        order='relevance',
                        maxResults=10
                    ).execute()
                    
                    videos = search_response.get('items', [])
                    logger.info(f"   📹 Found {len(videos)} videos for query: '{query}'")
                    
                    for video in videos:
                        video_id = video['id']['videoId']
                        if video_id not in seen_video_ids:
                            seen_video_ids.add(video_id)
                            all_videos.append({
                                'video_id': video_id,
                                'search_query': query,
                                'snippet': video['snippet']
                            })
                    
                except HttpError as e:
                    logger.error(f"❌ YouTube API error for query '{query}': {e}")
                    continue
                except Exception as e:
                    logger.error(f"❌ Error searching for query '{query}': {e}")
                    continue
            
            logger.info(f"📊 Total unique videos found from today: {len(all_videos)}")
            return all_videos
            
        except Exception as e:
            logger.error(f"❌ Error searching today's videos: {e}")
            return []
    
    async def _filter_relevant_videos_ai(self, videos: List[Dict[str, Any]], competitor_name: str) -> List[Dict[str, Any]]:
        """Use AI to filter videos for relevance to the competitor in batches of 5"""
        try:
            if not videos:
                return []
            
            if not self.llm:
                logger.info("🤖 LLM not available, using heuristic filtering")
                return self._filter_relevant_videos_heuristic(videos, competitor_name)
            
            relevant_videos = []
            competitor_name_lower = competitor_name.lower()
            
            logger.info(f"🧠 Using AI to filter {len(videos)} videos for relevance to {competitor_name} in batches of 5")
            
            # Process videos in batches of 5
            batch_size = 5
            total_batches = (len(videos) + batch_size - 1) // batch_size
            logger.info(f"📦 Starting batch processing: {len(videos)} videos in {total_batches} batches of {batch_size}")
            
            for i in range(0, len(videos), batch_size):
                batch = videos[i:i + batch_size]
                current_batch = i//batch_size + 1
                batch_range = f"{i+1}-{min(i+batch_size, len(videos))}"
                logger.info(f"📦 Processing batch {current_batch}/{total_batches}: videos {batch_range}")
                
                try:
                    # Process batch of 5 videos together
                    batch_results = await self._ai_video_relevance_check_batch(batch, competitor_name)
                    
                    # Add relevant videos from this batch
                    batch_relevant = 0
                    for j, is_relevant in enumerate(batch_results):
                        if is_relevant:
                            relevant_videos.append(batch[j])
                            batch_relevant += 1
                            title = batch[j].get('snippet', {}).get('title', 'Unknown')[:50]
                            logger.info(f"   ✅ AI Relevant: {title}...")
                        else:
                            title = batch[j].get('snippet', {}).get('title', 'Unknown')[:50]
                            logger.info(f"   ❌ AI Irrelevant: {title}...")
                    
                    logger.info(f"   📊 Batch {current_batch} results: {batch_relevant}/{len(batch)} videos relevant")
                            
                except Exception as e:
                    logger.error(f"   ❌ Error in AI relevance check for batch {current_batch}: {e}")
                    # Fallback to individual heuristic checks for this batch
                    logger.info(f"   🔄 Falling back to heuristic checks for batch {current_batch}")
                    batch_relevant = 0
                    for video in batch:
                        try:
                            snippet = video.get('snippet', {})
                            title = snippet.get('title', '')
                            description = snippet.get('description', '')
                            channel_title = snippet.get('channelTitle', '')
                            
                            if self._is_video_relevant_to_competitor_heuristic(
                                title, description, channel_title, competitor_name_lower
                            ):
                                relevant_videos.append(video)
                                batch_relevant += 1
                                logger.info(f"   ✅ Heuristic Relevant: {title[:50]}...")
                            else:
                                logger.info(f"   ❌ Heuristic Irrelevant: {title[:50]}...")
                        except Exception as batch_e:
                            logger.error(f"   ❌ Error in heuristic check: {batch_e}")
                            continue
                    
                    logger.info(f"   📊 Batch {current_batch} heuristic results: {batch_relevant}/{len(batch)} videos relevant")
            
            logger.info(f"🧠 AI filtered {len(videos)} videos to {len(relevant_videos)} relevant ones")
            
            # Log batch processing efficiency
            if len(videos) > 0:
                efficiency = (len(relevant_videos) / len(videos)) * 100
                logger.info(f"📊 Batch processing efficiency: {efficiency:.1f}% of videos were relevant")
                logger.info(f"📊 Processed {len(videos)} videos in {total_batches} batches of {batch_size}")
            
            return relevant_videos
            
        except Exception as e:
            logger.error(f"❌ Error in AI video filtering: {e}")
            logger.info("🔄 Falling back to heuristic filtering")
            return self._filter_relevant_videos_heuristic(videos, competitor_name)

    def _filter_relevant_videos_heuristic(self, videos: List[Dict[str, Any]], competitor_name: str) -> List[Dict[str, Any]]:
        """Fallback heuristic filtering when AI is not available"""
        return self._filter_relevant_videos(videos, competitor_name)

    def _filter_relevant_videos(self, videos: List[Dict[str, Any]], competitor_name: str) -> List[Dict[str, Any]]:
        """Filter videos to only include those relevant to the competitor using heuristics"""
        try:
            if not videos:
                return []
            
            relevant_videos = []
            competitor_name_lower = competitor_name.lower()
            
            for video in videos:
                try:
                    snippet = video.get('snippet', {})
                    title = snippet.get('title', '').lower()
                    description = snippet.get('description', '').lower()
                    channel_title = snippet.get('channelTitle', '').lower()
                    
                    # Check if video is relevant to the competitor
                    is_relevant = self._is_video_relevant_to_competitor_heuristic(
                        title, description, channel_title, competitor_name_lower
                    )
                    
                    if is_relevant:
                        relevant_videos.append(video)
                        logger.info(f"   ✅ Heuristic Relevant: {snippet.get('title', 'Unknown')[:50]}...")
                    else:
                        logger.info(f"   ❌ Heuristic Irrelevant: {snippet.get('title', 'Unknown')[:50]}...")
                        
                except Exception as e:
                    logger.error(f"   ❌ Error filtering video: {e}")
                    continue
            
            logger.info(f"🎯 Heuristic filtered {len(videos)} videos to {len(relevant_videos)} relevant ones")
            return relevant_videos
            
        except Exception as e:
            logger.error(f"❌ Error filtering relevant videos: {e}")
            return videos  # Return all videos if filtering fails

    def _is_video_relevant_to_competitor_heuristic(self, title: str, description: str, channel_title: str, competitor_name: str) -> bool:
        """Heuristic method for determining video relevance (fallback)"""
        try:
            # Must contain competitor name in title or description
            if competitor_name not in title and competitor_name not in description:
                return False
            
            # Check for official company indicators
            official_indicators = [
                'official', 'company', 'corporate', 'business', 'news', 'announcement',
                'earnings', 'quarterly', 'annual', 'report', 'update', 'launch'
            ]
            
            # Check for product-related indicators
            product_indicators = [
                'product', 'launch', 'release', 'new', 'announcement', 'update',
                'review', 'unboxing', 'test', 'comparison'
            ]
            
            # Check for business indicators
            business_indicators = [
                'earnings', 'revenue', 'profit', 'partnership', 'acquisition',
                'merger', 'investment', 'funding', 'ipo', 'stock'
            ]
            
            # Video must contain at least one relevant indicator
            has_official = any(indicator in title or indicator in description for indicator in official_indicators)
            has_product = any(indicator in title or indicator in description for indicator in product_indicators)
            has_business = any(indicator in title or indicator in description for indicator in business_indicators)
            
            # Must have at least one relevant indicator to be considered relevant
            return has_official or has_product or has_business
            
        except Exception as e:
            logger.error(f"❌ Error checking video relevance: {e}")
            return False
    
    async def _get_video_details(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific video including captions"""
        try:
            # Get basic video information
            video_response = self.youtube_api.videos().list(
                part='snippet,statistics,contentDetails',
                id=video_id
            ).execute()
            
            if not video_response.get('items'):
                return None
            
            video = video_response['items'][0]
            snippet = video['snippet']
            statistics = video.get('statistics', {})
            
            # Get video captions/transcripts if available
            captions = await self._get_video_captions(video_id)
            
            return {
                'video_id': video_id,
                'title': snippet.get('title', ''),
                'description': snippet.get('description', ''),
                'channel_title': snippet.get('channelTitle', ''),
                'published_at': snippet.get('publishedAt', ''),
                'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                'url': f"https://www.youtube.com/watch?v={video_id}",
                'view_count': int(statistics.get('viewCount', 0)),
                'like_count': int(statistics.get('likeCount', 0)),
                'comment_count': int(statistics.get('commentCount', 0)),
                'duration': video.get('contentDetails', {}).get('duration', ''),
                'tags': snippet.get('tags', []),
                'captions': captions
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting video details for {video_id}: {e}")
            return None

    async def _get_video_captions(self, video_id: str) -> str:
        """Get video captions/transcripts if available"""
        try:
            # First, check if captions are available
            captions_response = self.youtube_api.captions().list(
                part='snippet',
                videoId=video_id
            ).execute()
            
            if not captions_response.get('items'):
                logger.info(f"📝 No captions available for video {video_id}")
                return ""
            
            # Get the first available caption track (usually auto-generated)
            caption_id = captions_response['items'][0]['id']
            
            # Download the caption content
            caption_response = self.youtube_api.captions().download(
                id=caption_id,
                tfmt='srt'
            ).execute()
            
            if caption_response:
                # Parse SRT format and extract text
                caption_text = self._parse_srt_captions(caption_response.decode('utf-8'))
                logger.info(f"📝 Retrieved captions for video {video_id}: {len(caption_text)} characters")
                return caption_text
            else:
                return ""
                
        except Exception as e:
            logger.warning(f"⚠️  Could not retrieve captions for video {video_id}: {e}")
            return ""

    def _parse_srt_captions(self, srt_content: str) -> str:
        """Parse SRT caption format and extract clean text"""
        try:
            lines = srt_content.split('\n')
            text_lines = []
            
            for i, line in enumerate(lines):
                # Skip timestamp lines and empty lines
                if (line.strip().isdigit() or 
                    '-->' in line or 
                    not line.strip()):
                    continue
                text_lines.append(line.strip())
            
            return ' '.join(text_lines)
        except Exception as e:
            logger.warning(f"⚠️  Error parsing SRT captions: {e}")
            return srt_content
    
    async def _analyze_video_intelligence(self, video_details: Dict[str, Any], competitor_name: str) -> Dict[str, Any]:
        """Analyze video content using AI to determine significance and generate insights"""
        try:
            if self.llm:
                # Use AI for intelligent analysis
                return await self._ai_video_analysis(video_details, competitor_name)
            else:
                # Use heuristic analysis
                return self._heuristic_video_analysis(video_details, competitor_name)
                
        except Exception as e:
            logger.error(f"❌ Error in video intelligence analysis: {e}")
            return self._heuristic_video_analysis(video_details, competitor_name)
    
    async def _ai_video_analysis(self, video_details: Dict[str, Any], competitor_name: str) -> Dict[str, Any]:
        """Use AI to analyze video content for competitive intelligence and sentiment"""
        try:
            title = video_details.get('title', '')
            description = video_details.get('description', '')
            captions = video_details.get('captions', '')
            channel = video_details.get('channel_title', '')
            views = video_details.get('view_count', 0)
            likes = video_details.get('like_count', 0)
            
            # Combine all content for comprehensive analysis
            full_content = f"Title: {title}\nDescription: {description}\nCaptions: {captions}"
            
            prompt = f"""
Analyze this YouTube video for competitive intelligence about "{competitor_name}":

TITLE: {title}
CHANNEL: {channel}
DESCRIPTION: {description}
CAPTIONS: {captions[:1000] if captions else "No captions available"}
ENGAGEMENT: {views} views, {likes} likes
PUBLISHED: Today

Your analysis should determine:
1. Is this video ALERT-WORTHY for competitive intelligence?
2. What are the key insights about the competitor?
3. What marketing/business strategies can be observed?
4. What is the sentiment of this content?

IMPORTANT: Only analyze videos that are DIRECTLY about the competitor company. If the video is not clearly about the company, mark it as not alert-worthy.

ALERT-WORTHY criteria:
- Major product launches or announcements from the company
- Significant company news or changes (earnings, partnerships, etc.)
- High engagement suggesting viral/trending company content
- Strategic partnerships or collaborations involving the company
- Crisis management or negative coverage about the company
- Competitive moves or market positioning by the company

SENTIMENT ANALYSIS:
Analyze the overall tone and sentiment of the content, considering:
- Language used (positive, negative, neutral)
- Context and implications for the company
- Public reaction indicators

Provide your response in this JSON format:
{{
    "is_alert_worthy": true/false,
    "alert_reason": "Brief reason if alert-worthy, null if not",
    "significance_score": 1-10,
    "summary": "Brief competitive intelligence summary (max 200 words)",
    "key_insights": ["insight1", "insight2", "insight3"],
    "content_type": "announcement/review/news/official/other",
    "competitive_impact": "high/medium/low",
    "sentiment_analysis": {{
        "overall_sentiment": "positive/negative/neutral",
        "sentiment_score": -1.0 to 1.0,
        "sentiment_reason": "Brief explanation of sentiment",
        "key_sentiment_indicators": ["indicator1", "indicator2"]
    }}
}}

Be selective with alerts - only flag truly significant competitive intelligence.
"""
            
            response = await self.llm.ainvoke(prompt)
            
            # Parse JSON response
            try:
                content = response.content.strip()
                if content.startswith('{') and content.endswith('}'):
                    analysis = json.loads(content)
                else:
                    # Extract JSON from response
                    start = content.find('{')
                    end = content.rfind('}') + 1
                    if start != -1 and end != 0:
                        json_str = content[start:end]
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
                    return self._heuristic_video_analysis(video_details, competitor_name)
                    
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"❌ Failed to parse AI response: {e}")
                return self._heuristic_video_analysis(video_details, competitor_name)
                
        except Exception as e:
            logger.error(f"❌ Error in AI video analysis: {e}")
            return self._heuristic_video_analysis(video_details, competitor_name)
    
    def _heuristic_video_analysis(self, video_details: Dict[str, Any], competitor_name: str) -> Dict[str, Any]:
        """Heuristic analysis when AI is not available"""
        title = video_details.get('title', '').lower()
        description = video_details.get('description', '').lower()
        channel = video_details.get('channel_title', '')
        views = video_details.get('view_count', 0)
        likes = video_details.get('like_count', 0)
        
        # Check for alert-worthy keywords
        alert_keywords = [
            'launch', 'announcement', 'breaking', 'exclusive', 'new', 'unveiling',
            'partnership', 'acquisition', 'merger', 'funding', 'ipo', 'expansion'
        ]
        
        # Check for high engagement
        like_ratio = (likes / views * 100) if views > 0 else 0
        high_engagement = views > 10000 or like_ratio > 2.0
        
        # Check if it's from official channel (contains company name)
        is_official_channel = competitor_name.lower() in channel.lower()
        
        # Check for alert keywords in title/description
        has_alert_keywords = any(keyword in title or keyword in description for keyword in alert_keywords)
        
        # Determine if alert-worthy - must be clearly about the competitor
        is_alert_worthy = False
        alert_reason = None
        significance_score = 1
        
        # Must contain competitor name to be considered
        if competitor_name.lower() not in title and competitor_name.lower() not in description:
            is_alert_worthy = False
            alert_reason = "Video does not contain competitor name"
            significance_score = 1
        elif is_official_channel and has_alert_keywords:
            is_alert_worthy = True
            alert_reason = "Official channel with announcement keywords"
            significance_score = 8
        elif high_engagement and has_alert_keywords:
            is_alert_worthy = True
            alert_reason = f"High engagement ({views} views) with significant keywords"
            significance_score = 7
        elif is_official_channel and views > 5000:
            is_alert_worthy = True
            alert_reason = "Official channel content with decent reach"
            significance_score = 5
        
        # Generate summary
        summary = f"Video analysis for {competitor_name}: '{video_details.get('title', 'Unknown')}' by {channel}. "
        summary += f"Engagement: {views:,} views, {likes:,} likes. "
        
        if competitor_name.lower() not in title and competitor_name.lower() not in description:
            summary += "WARNING: Video may not be directly about the competitor. "
        if is_official_channel:
            summary += "Official channel content. "
        if has_alert_keywords:
            summary += "Contains announcement keywords. "
        if high_engagement:
            summary += "High engagement metrics. "
        
        return {
            "is_alert_worthy": is_alert_worthy,
            "alert_reason": alert_reason,
            "significance_score": significance_score,
            "summary": summary,
            "key_insights": [
                f"Published by: {channel}",
                f"Engagement: {views:,} views, {likes:,} likes",
                f"Official channel: {is_official_channel}",
                f"Contains announcements: {has_alert_keywords}",
                f"Relevance to competitor: {'High' if competitor_name.lower() in title or competitor_name.lower() in description else 'Low'}"
            ],
            "content_type": "official" if is_official_channel else "external",
            "competitive_impact": "high" if significance_score >= 7 else ("medium" if significance_score >= 5 else "low"),
            "relevance_score": 10 if competitor_name.lower() in title and competitor_name.lower() in description else (5 if competitor_name.lower() in title or competitor_name.lower() in description else 1)
        }
    
    def _create_monitoring_data(self, video_details: Dict[str, Any], analysis_result: Dict[str, Any], competitor_id: str) -> Dict[str, Any]:
        """Create monitoring data structure for Supabase with full content"""
        # Combine all available content without truncation
        content_parts = [video_details.get('title', '')]
        
        if video_details.get('description'):
            content_parts.append(video_details.get('description'))
        
        if video_details.get('captions'):
            content_parts.append(f"Captions: {video_details.get('captions')}")
        
        content_text = '\n\n'.join(content_parts)
        content_hash = hashlib.md5(content_text.encode()).hexdigest()
        
        # Extract sentiment score from AI analysis
        sentiment_score = 0.0
        if analysis_result.get('sentiment_analysis'):
            sentiment_score = analysis_result['sentiment_analysis'].get('sentiment_score', 0.0)
        
        return {
            'competitor_id': str(competitor_id),
            'platform': 'youtube',
            'post_id': video_details['video_id'],
            'post_url': video_details['url'],
            'content_text': content_text,  # Full content without truncation
            'content_hash': content_hash,
            'media_urls': [video_details.get('thumbnail', '')],
            'engagement_metrics': {
                'view_count': video_details.get('view_count', 0),
                'like_count': video_details.get('like_count', 0),
                'comment_count': video_details.get('comment_count', 0)
            },
            'author_username': video_details.get('channel_title', ''),
            'author_display_name': video_details.get('channel_title', ''),
            'post_type': 'video',
            'language': 'en',  # Default to English
            'sentiment_score': sentiment_score,  # AI-determined sentiment
            'detected_at': datetime.now(timezone.utc).isoformat(),
            'posted_at': video_details.get('published_at'),
            'is_new_post': True,
            'is_content_change': False
        }
    
    async def _create_intelligent_alert(self, competitor_id: str, video_details: Dict[str, Any], analysis_result: Dict[str, Any], data_id: str):
        """Create an intelligent alert for significant videos"""
        try:
            # Get competitor details to get user_id
            competitor_details = await supabase_client.get_competitor_details(competitor_id)
            user_id = competitor_details.get('user_id') if competitor_details else None
            
            alert_data = {
                'user_id': user_id,
                'competitor_id': str(competitor_id),
                'monitoring_data_id': data_id,
                'alert_type': 'youtube_intelligence',
                'priority': 'high' if analysis_result.get('significance_score', 0) >= 7 else 'medium',
                'title': f"YouTube Intelligence Alert: {video_details.get('title', 'Significant Video')[:100]}",
                'message': analysis_result.get('alert_reason', 'AI detected significant YouTube activity'),
                'alert_metadata': {
                    'platform': 'youtube',
                    'video_id': video_details['video_id'],
                    'video_url': video_details['url'],
                    'channel_title': video_details.get('channel_title', ''),
                    'engagement_metrics': {
                        'views': video_details.get('view_count', 0),
                        'likes': video_details.get('like_count', 0),
                        'comments': video_details.get('comment_count', 0)
                    },
                    'ai_analysis': {
                        'significance_score': analysis_result.get('significance_score', 0),
                        'content_type': analysis_result.get('content_type', 'unknown'),
                        'competitive_impact': analysis_result.get('competitive_impact', 'unknown'),
                        'key_insights': analysis_result.get('key_insights', []),
                        'analysis_timestamp': datetime.now(timezone.utc).isoformat()
                    }
                },
                'is_read': False,
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            alert_id = await supabase_client.create_alert(alert_data)
            if alert_id:
                logger.info(f"🚨 Created intelligent YouTube alert: {alert_id}")
            else:
                logger.error("❌ Failed to create alert in Supabase")
                
        except Exception as e:
            logger.error(f"❌ Error creating intelligent alert: {e}")

    async def _ai_video_relevance_check_batch(self, videos: List[Dict[str, Any]], competitor_name: str) -> List[bool]:
        """Use AI to determine relevance for a batch of 5 videos at once"""
        try:
            if not videos or len(videos) == 0:
                return []
            
            # Prepare batch data for AI analysis
            batch_data = []
            for i, video in enumerate(videos):
                snippet = video.get('snippet', {})
                title = snippet.get('title', '')
                description = snippet.get('description', '')
                channel_title = snippet.get('channelTitle', '')
                
                batch_data.append({
                    'index': i + 1,
                    'title': title,
                    'description': description[:500] if description else '',
                    'channel': channel_title
                })
            
            # Create comprehensive prompt for batch analysis
            prompt = f"""
Analyze these 5 YouTube videos to determine if they are DIRECTLY relevant to the company "{competitor_name}".

For each video, determine if it is ONLY relevant if it is:
1. DIRECTLY about the company "{competitor_name}" (not just similar words)
2. Contains official company announcements, news, or content
3. Is a review or analysis specifically about the company
4. Discusses the company's products, services, or business activities

The video is NOT relevant if it:
1. Only mentions similar words but is about different companies
2. Is generic content that happens to use similar terminology
3. Is unrelated content from a channel with a similar name

VIDEO BATCH:
"""
            
            # Add each video to the prompt
            for video_data in batch_data:
                prompt += f"""
VIDEO {video_data['index']}:
Title: {video_data['title']}
Description: {video_data['description']}
Channel: {video_data['channel']}
"""
            
            prompt += f"""
Respond with ONLY a JSON array of 5 boolean values (true/false) indicating relevance for each video in order.
Example: [true, false, true, false, true]

Be selective - only mark as relevant if the video is clearly and directly about "{competitor_name}".
"""
            
            response = await self.llm.ainvoke(prompt)
            
            # Parse JSON response
            try:
                content = response.content.strip()
                if content.startswith('[') and content.endswith(']'):
                    results = json.loads(content)
                else:
                    # Extract JSON array from response
                    start = content.find('[')
                    end = content.rfind(']') + 1
                    if start != -1 and end != 0:
                        json_str = content[start:end]
                        results = json.loads(json_str)
                    else:
                        raise ValueError("No JSON array found in response")
                
                # Validate response format
                if isinstance(results, list) and len(results) == len(videos):
                    # Ensure all values are boolean
                    boolean_results = [bool(result) for result in results]
                    logger.info(f"🧠 Batch AI relevance check completed for {len(videos)} videos")
                    return boolean_results
                else:
                    logger.warning(f"⚠️  AI response format invalid, using fallback for batch")
                    return [False] * len(videos)
                    
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"❌ Failed to parse AI batch response: {e}")
                return [False] * len(videos)
                
        except Exception as e:
            logger.error(f"❌ Error in AI batch relevance check: {e}")
            return [False] * len(videos)

    async def _ai_video_relevance_check(self, title: str, description: str, channel_title: str, competitor_name: str) -> bool:
        """Use AI to determine if a video is relevant to the competitor (fallback for individual checks)"""
        try:
            prompt = f"""
Determine if this YouTube video is DIRECTLY relevant to the company "{competitor_name}":

TITLE: {title}
DESCRIPTION: {description[:500]}
CHANNEL: {channel_title}

The video is ONLY relevant if it is:
1. DIRECTLY about the company "{competitor_name}" (not just similar words)
2. Contains official company announcements, news, or content
3. Is a review or analysis specifically about the company
4. Discusses the company's products, services, or business activities

The video is NOT relevant if it:
1. Only mentions similar words but is about different companies
2. Is generic content that happens to use similar terminology
3. Is unrelated content from a channel with a similar name

Respond with ONLY "RELEVANT" or "NOT_RELEVANT".
"""
            
            response = await self.llm.ainvoke(prompt)
            result = response.content.strip().upper()
            
            return result == "RELEVANT"
            
        except Exception as e:
            logger.error(f"❌ Error in AI relevance check: {e}")
            return False

    async def close(self):
        """Close any resources"""
        logger.info("🎬 Intelligent YouTubeAgent closed")
