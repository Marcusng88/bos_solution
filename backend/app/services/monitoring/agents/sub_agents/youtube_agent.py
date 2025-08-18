"""
YouTube Sub-Agent for Competitor Analysis
Uses YouTube Data API with LangGraph agent to analyze YouTube channels and videos
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta, timezone
import hashlib
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
logger = logging.getLogger(__name__)
# Import langchain dependencies conditionally
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langgraph.prebuilt import create_react_agent
    from langchain_core.tools import tool
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    logger.warning(f"LangChain dependencies not available: {e}")
    LANGCHAIN_AVAILABLE = False

# Import Google API dependencies conditionally
try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_API_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Google API dependencies not available: {e}")
    GOOGLE_API_AVAILABLE = False

from app.models.competitor import Competitor
from app.models.monitoring import MonitoringData, MonitoringAlert
from app.core.config import settings
from ...core_service import MonitoringService

logger = logging.getLogger(__name__)


class YouTubeAgent:
    """YouTube-specific agent for competitor analysis using YouTube Data API"""
    
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
        
        # Initialize YouTube API client
        self.youtube_api = None
        if GOOGLE_API_AVAILABLE and settings.youtube_api_key:
            try:
                self.youtube_api = build('youtube', 'v3', developerKey=settings.youtube_api_key)
                logger.info("YouTube Data API client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize YouTube API client: {e}")
        elif not GOOGLE_API_AVAILABLE:
            logger.warning("Google API client not available - YouTube analysis will be limited")
        
        # Initialize agent
        self.agent = None
        self._initialized = False
    
    async def _initialize_agent(self):
        """Initialize the YouTube agent with YouTube API tools"""
        if self._initialized:
            return
        
        try:
            logger.info("Initializing YouTube agent with API tools...")
            
            if not self.youtube_api:
                raise Exception("YouTube API client not available - check YOUTUBE_API_KEY")
            
            if not LANGCHAIN_AVAILABLE:
                raise Exception("LangChain dependencies not available - cannot create agent")
            
            if not self.llm:
                raise Exception("LLM not available - cannot create agent")
            
            # Create YouTube API tools
            tools = self._create_youtube_tools()
            logger.info(f"Created {len(tools)} YouTube API tools")
            
            # Create agent with YouTube-specific prompt
            logger.info("Creating LangGraph ReAct agent...")
            self.agent = create_react_agent(
                model=self.llm,
                tools=tools,
                prompt=(
                    "You are a YouTube competitor analysis agent. Your job is to analyze YouTube channels and videos to extract valuable competitive intelligence.\n\n"
                    "INSTRUCTIONS:\n"
                    "1. Use the provided YouTube API tools to search for channels and analyze videos\n"
                    "2. Focus ONLY on content from the last 24 hours (current day only)\n"
                    "3. Search for up to 5 relevant channels associated with the competitor (not just one official channel)\n"
                    "4. For each video found, analyze:\n"
                    "   - Video content (title, description, captions)\n"
                    "   - Engagement metrics (views, likes, comments)\n"
                    "   - Comment sentiment and audience reaction\n"
                    "   - Marketing strategy and messaging\n"
                    "5. Use AI analysis to determine if each video represents a significant marketing event\n"
                    "6. Only flag content as 'ALERT-WORTHY' if it shows:\n"
                    "   - Unusually high engagement for the channel\n"
                    "   - New product launches or announcements\n"
                    "   - Viral marketing campaigns\n"
                    "   - Significant strategic shifts\n"
                    "   - Major brand partnerships or collaborations\n"
                    "7. Return structured data with clear alert recommendations\n\n"
                    "Remember: Be selective with alerts - only flag truly significant competitive events, not routine content."
                ),
                name="youtube_agent"
            )
            
            self._initialized = True
            logger.info("YouTube agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing YouTube agent: {e}")
            logger.error(f"Error details: {type(e).__name__}: {str(e)}")
            raise
    
    def _create_youtube_tools(self):
        """Create YouTube API tools for the agent"""
        
        @tool
        def search_youtube_channels(query: str, max_results: int = 10) -> List[Dict]:
            """
            Search for YouTube channels by name or keywords.
            
            Args:
                query: Search query for channels
                max_results: Maximum number of results (default 10, max 50)
            
            Returns:
                List of channel information dictionaries
            """
            try:
                logger.info(f"Searching YouTube channels for: {query}")
                
                search_response = self.youtube_api.search().list(
                    q=query,
                    part='snippet',
                    type='channel',
                    maxResults=min(max_results, 50)
                ).execute()
                
                channels = []
                for item in search_response.get('items', []):
                    channels.append({
                        'channel_id': item['id']['channelId'],
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'thumbnail': item['snippet']['thumbnails'].get('default', {}).get('url'),
                        'published_at': item['snippet']['publishedAt']
                    })
                
                logger.info(f"Found {len(channels)} channels")
                return channels
                
            except HttpError as e:
                logger.error(f"YouTube API error in search_channels: {e}")
                return []
            except Exception as e:
                logger.error(f"Error searching channels: {e}")
                return []
        
        @tool
        def get_channel_details(channel_id: str) -> Dict:
            """
            Get detailed information about a specific YouTube channel.
            
            Args:
                channel_id: YouTube channel ID
            
            Returns:
                Channel details dictionary with statistics and info
            """
            try:
                logger.info(f"Getting channel details for: {channel_id}")
                
                channel_response = self.youtube_api.channels().list(
                    part='snippet,statistics,contentDetails,brandingSettings',
                    id=channel_id
                ).execute()
                
                if not channel_response.get('items'):
                    logger.warning(f"No channel found for ID: {channel_id}")
                    return {}
                
                channel = channel_response['items'][0]
                
                details = {
                    'channel_id': channel['id'],
                    'title': channel['snippet']['title'],
                    'description': channel['snippet']['description'],
                    'custom_url': channel['snippet'].get('customUrl'),
                    'published_at': channel['snippet']['publishedAt'],
                    'thumbnail': channel['snippet']['thumbnails'].get('default', {}).get('url'),
                    'country': channel['snippet'].get('country'),
                    'view_count': channel['statistics'].get('viewCount'),
                    'subscriber_count': channel['statistics'].get('subscriberCount'),
                    'video_count': channel['statistics'].get('videoCount'),
                    'uploads_playlist_id': channel['contentDetails']['relatedPlaylists']['uploads']
                }
                
                logger.info(f"Retrieved channel details: {details['title']}")
                return details
                
            except HttpError as e:
                logger.error(f"YouTube API error in get_channel_details: {e}")
                return {}
            except Exception as e:
                logger.error(f"Error getting channel details: {e}")
                return {}
        
        @tool
        def get_video_captions(video_id: str) -> str:
            """
            Get captions/transcript for a YouTube video.
            
            Args:
                video_id: YouTube video ID
            
            Returns:
                Video captions text or empty string if not available
            """
            try:
                logger.info(f"Getting captions for video: {video_id}")
                
                # Get caption tracks for the video
                captions_response = self.youtube_api.captions().list(
                    part='snippet',
                    videoId=video_id
                ).execute()
                
                caption_tracks = captions_response.get('items', [])
                if not caption_tracks:
                    logger.info(f"No captions available for video: {video_id}")
                    return ""
                
                # Try to find English captions first, then any available
                english_track = None
                for track in caption_tracks:
                    if track['snippet']['language'] == 'en':
                        english_track = track
                        break
                
                # Use first available track if no English found
                selected_track = english_track or caption_tracks[0]
                caption_id = selected_track['id']
                
                # Download the caption content
                caption_content = self.youtube_api.captions().download(
                    id=caption_id,
                    tfmt='srt'  # SubRip format
                ).execute()
                
                # Clean up the SRT format (remove timestamps)
                import re
                clean_text = re.sub(r'\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n', '', caption_content)
                clean_text = re.sub(r'\n+', ' ', clean_text).strip()
                
                logger.info(f"Retrieved captions for video {video_id}: {len(clean_text)} characters")
                return clean_text[:1000]  # Limit to first 1000 characters
                
            except Exception as e:
                logger.info(f"Could not retrieve captions for video {video_id}: {e}")
                return ""
        
        @tool
        def get_channel_videos(channel_id: str, max_results: int = 20) -> List[Dict]:
            """
            Get recent videos from a YouTube channel (last 24 hours only).
            
            Args:
                channel_id: YouTube channel ID
                max_results: Maximum number of videos (default 20, max 50)
            
            Returns:
                List of video information dictionaries from the last 24 hours only
            """
            try:
                logger.info(f"Getting videos for channel: {channel_id} (last 24 hours only)")
                
                # First get the uploads playlist ID
                channel_response = self.youtube_api.channels().list(
                    part='contentDetails',
                    id=channel_id
                ).execute()
                
                if not channel_response.get('items'):
                    return []
                
                uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
                
                # Get videos from uploads playlist - only last 24 hours
                published_after = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat() + 'Z'
                
                playlist_response = self.youtube_api.playlistItems().list(
                    part='snippet',
                    playlistId=uploads_playlist_id,
                    maxResults=min(max_results, 50)
                ).execute()
                
                video_ids = []
                videos_basic = []
                
                for item in playlist_response.get('items', []):
                    # Only include videos from the last 24 hours
                    published_at = datetime.fromisoformat(item['snippet']['publishedAt'].replace('Z', '+00:00'))
                    if published_at >= datetime.now(timezone.utc) - timedelta(days=1):
                        video_id = item['snippet']['resourceId']['videoId']
                        video_ids.append(video_id)
                        videos_basic.append({
                            'video_id': video_id,
                            'title': item['snippet']['title'],
                            'description': item['snippet']['description'],
                            'published_at': item['snippet']['publishedAt'],
                            'thumbnail': item['snippet']['thumbnails'].get('default', {}).get('url')
                        })
                
                # Get detailed statistics for videos
                if video_ids:
                    videos_response = self.youtube_api.videos().list(
                        part='statistics,contentDetails',
                        id=','.join(video_ids)
                    ).execute()
                    
                    # Merge statistics with basic info
                    stats_dict = {item['id']: item for item in videos_response.get('items', [])}
                    
                    for video in videos_basic:
                        video_id = video['video_id']
                        if video_id in stats_dict:
                            stats = stats_dict[video_id]['statistics']
                            content = stats_dict[video_id]['contentDetails']
                            
                            video.update({
                                'view_count': stats.get('viewCount'),
                                'like_count': stats.get('likeCount'),
                                'comment_count': stats.get('commentCount'),
                                'duration': content.get('duration'),
                                'video_url': f"https://www.youtube.com/watch?v={video_id}"
                            })
                
                logger.info(f"Retrieved {len(videos_basic)} videos from last 24 hours")
                return videos_basic
                
            except HttpError as e:
                logger.error(f"YouTube API error in get_channel_videos: {e}")
                return []
            except Exception as e:
                logger.error(f"Error getting channel videos: {e}")
                return []
        
        @tool
        def search_channel_by_handle(handle: str) -> Dict:
            """
            Search for a YouTube channel by its handle (e.g., @nike).
            
            Args:
                handle: Channel handle with or without @ symbol
            
            Returns:
                Channel information dictionary
            """
            try:
                # Clean handle (remove @ if present)
                clean_handle = handle.lstrip('@')
                logger.info(f"Searching for channel with handle: {clean_handle}")
                
                # Search for channel by handle/name
                search_response = self.youtube_api.search().list(
                    q=clean_handle,
                    part='snippet',
                    type='channel',
                    maxResults=5
                ).execute()
                
                # Look for exact or close match
                for item in search_response.get('items', []):
                    title = item['snippet']['title'].lower()
                    if clean_handle.lower() in title or title in clean_handle.lower():
                        return {
                            'channel_id': item['id']['channelId'],
                            'title': item['snippet']['title'],
                            'description': item['snippet']['description'],
                            'thumbnail': item['snippet']['thumbnails'].get('default', {}).get('url'),
                            'published_at': item['snippet']['publishedAt']
                        }
                
                # If no good match, return first result
                if search_response.get('items'):
                    item = search_response['items'][0]
                    return {
                        'channel_id': item['id']['channelId'],
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'thumbnail': item['snippet']['thumbnails'].get('default', {}).get('url'),
                        'published_at': item['snippet']['publishedAt']
                    }
                
                logger.warning(f"No channel found for handle: {handle}")
                return {}
                
            except HttpError as e:
                logger.error(f"YouTube API error in search_channel_by_handle: {e}")
                return {}
            except Exception as e:
                logger.error(f"Error searching channel by handle: {e}")
                return {}
        
        @tool
        def search_competitor_channels(competitor_name: str, max_channels: int = 5) -> List[Dict]:
            """
            Search for multiple YouTube channels related to a competitor brand.
            Finds official channels, news coverage, and influencer content.
            
            Args:
                competitor_name: Brand/competitor name to search for
                max_channels: Maximum number of channels to find (default 5)
            
            Returns:
                List of relevant channel information dictionaries
            """
            try:
                logger.info(f"Searching for multiple channels related to: {competitor_name}")
                
                all_channels = []
                search_terms = [
                    competitor_name,  # Official brand name
                    f"{competitor_name} official",  # Official channel
                    f"{competitor_name} news",  # News coverage
                    f"{competitor_name} review",  # Review channels
                    f"{competitor_name} unboxing"  # Unboxing/influencer content
                ]
                
                for term in search_terms:
                    if len(all_channels) >= max_channels:
                        break
                    
                    search_response = self.youtube_api.search().list(
                        q=term,
                        part='snippet',
                        type='channel',
                        maxResults=3  # Limit per search term
                    ).execute()
                    
                    for item in search_response.get('items', []):
                        if len(all_channels) >= max_channels:
                            break
                        
                        channel_info = {
                            'channel_id': item['id']['channelId'],
                            'title': item['snippet']['title'],
                            'description': item['snippet']['description'],
                            'thumbnail': item['snippet']['thumbnails'].get('default', {}).get('url'),
                            'published_at': item['snippet']['publishedAt'],
                            'search_term': term
                        }
                        
                        # Avoid duplicates
                        if not any(ch['channel_id'] == channel_info['channel_id'] for ch in all_channels):
                            all_channels.append(channel_info)
                
                logger.info(f"Found {len(all_channels)} unique channels for {competitor_name}")
                return all_channels
                
            except HttpError as e:
                logger.error(f"YouTube API error in search_competitor_channels: {e}")
                return []
            except Exception as e:
                logger.error(f"Error searching competitor channels: {e}")
                return []
        
        return [search_youtube_channels, get_channel_details, get_channel_videos, search_channel_by_handle, get_video_captions, search_competitor_channels]
    
    async def analyze_competitor(self, competitor_id: str, youtube_handle: str) -> Dict[str, Any]:
        """
        Analyze a competitor's YouTube presence using the YouTube Data API
        
        Args:
            competitor_id: Database ID of the competitor
            youtube_handle: YouTube channel handle or name
            
        Returns:
            Dict containing analysis results and extracted posts
        """
        try:
            await self._initialize_agent()
            
            logger.info(f"Starting YouTube analysis for competitor {competitor_id}, handle: {youtube_handle}")
            
            # Get competitor info for context
            competitor = await self._get_competitor(competitor_id)
            if not competitor:
                logger.error(f"Competitor {competitor_id} not found in database")
                return {
                    "platform": "youtube",
                    "posts": [],
                    "error": "Competitor not found"
                }
            
            logger.info(f"Analyzing competitor: {competitor.name} (Industry: {competitor.industry})")
            
            # Construct analysis prompt
            analysis_prompt = self._build_analysis_prompt(competitor, youtube_handle)
            logger.info(f"Analysis prompt length: {len(analysis_prompt)} characters")
            logger.debug(f"Analysis prompt: {analysis_prompt[:500]}...")
            
            # Run agent analysis
            logger.info("Invoking YouTube agent with analysis prompt...")
            start_time = datetime.now(timezone.utc)
            
            result = await self.agent.ainvoke({
                "messages": [{"role": "user", "content": analysis_prompt}]
            })
            
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            logger.info(f"YouTube agent execution completed in {duration:.2f}s")
            
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
            
            posts = await self._process_analysis_results(competitor_id, analysis_content, youtube_handle)
            
            logger.info(f"YouTube analysis completed for {competitor.name}: {len(posts)} posts processed")
            
            return {
                "platform": "youtube",
                "posts": posts,
                "status": "completed",
                "analysis_summary": analysis_content[:500] + "..." if len(analysis_content) > 500 else analysis_content,
                "competitor_name": competitor.name,
                "channel_handle": youtube_handle
            }
            
        except Exception as e:
            logger.error(f"Error in YouTube analysis for competitor {competitor_id}: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error details: {str(e)}")
            return {
                "platform": "youtube",
                "posts": [],
                "error": str(e)
            }
    
    def _build_analysis_prompt(self, competitor: Competitor, youtube_handle: str) -> str:
        """Build analysis prompt for the YouTube agent"""
        
        return f"""
Analyze the YouTube presence of competitor "{competitor.name}" in the {competitor.industry} industry.

COMPETITOR DETAILS:
- Name: {competitor.name}
- Industry: {competitor.industry}
- Description: {competitor.description or 'N/A'}
- YouTube Handle: {youtube_handle}

ANALYSIS TASKS:
1. Use search_competitor_channels to find up to 5 relevant channels for "{competitor.name}"
2. For each channel found, get recent videos from the last 24 hours only
3. Analyze video content using captions and engagement metrics
4. Determine if any videos are ALERT-WORTHY based on:
   - Significant engagement spikes
   - Product launches or major announcements
   - Viral content or trending topics
   - Strategic marketing campaigns
   - Brand partnerships or collaborations

CRITICAL REQUIREMENTS:
- Focus ONLY on content from the last 24 hours
- Be selective with alerts - flag only truly significant events
- Analyze video captions for marketing insights
- Consider engagement relative to channel's typical performance
- Look for strategic marketing patterns and messaging

ALERT CRITERIA:
Mark content as ALERT-WORTHY only if it represents a significant competitive development, not routine content.

Provide a comprehensive analysis with clear alert recommendations and actionable insights.
"""
    
    async def _process_analysis_results(self, competitor_id: str, analysis_content: str, youtube_handle: str) -> List[Dict[str, Any]]:
        """
        Process agent analysis results and extract videos from the agent's API calls
        Save actual YouTube videos found during analysis as monitoring data
        """
        logger.info(f"📊 Analysis completed for {youtube_handle}")
        logger.info(f"📝 Analysis summary: {analysis_content[:200]}...")
        
        processed_posts = []
        
        try:
            # The agent has already made API calls and found videos during its analysis
            # We need to extract video information that was mentioned in the analysis
            # and also check if we can find videos that should be saved
            
            # Try to find the channel again and get recent videos to save as monitoring data
            # This ensures we capture the videos that the agent analyzed
            
            # Search for the channel using our tools
            search_tools = self._create_youtube_tools()
            search_func = next((tool for tool in search_tools if tool.name == "search_channel_by_handle"), None)
            get_videos_func = next((tool for tool in search_tools if tool.name == "get_channel_videos"), None)
            
            if search_func and get_videos_func:
                logger.info(f"🔍 Finding and saving videos for {youtube_handle}")
                
                # Search for the channel
                channel_info = search_func.invoke({"handle": youtube_handle})
                
                if channel_info and 'channel_id' in channel_info:
                    channel_id = channel_info['channel_id']
                    logger.info(f"📺 Found channel {channel_id}, retrieving videos...")
                    
                    # Get recent videos (last 24 hours only)
                    videos = get_videos_func.invoke({"channel_id": channel_id, "max_results": 20})
                    
                    logger.info(f"🎬 Found {len(videos)} videos to process")
                    
                    # Process each video and save as monitoring data
                    for video in videos:
                        try:
                            # Try to get captions for marketing insights
                            captions = ""
                            video_id = video.get('video_id')
                            if video_id:
                                try:
                                    captions_func = next((tool for tool in search_tools if tool.name == "get_video_captions"), None)
                                    if captions_func:
                                        captions = captions_func.invoke({"video_id": video_id})
                                except Exception as e:
                                    logger.debug(f"Could not get captions for video {video_id}: {e}")
                            
                            # Generate marketing summary and alert assessment using LLM
                            marketing_summary, is_alert_worthy, alert_reason = await self._analyze_video_for_alerts(
                                video.get('title', ''),
                                video.get('description', ''),
                                captions,
                                video.get('view_count', 0),
                                video.get('like_count', 0),
                                video.get('comment_count', 0)
                            )
                            
                            post_data = {
                                "post_id": video.get('video_id'),
                                "post_url": video.get('video_url', f"https://www.youtube.com/watch?v={video.get('video_id')}"),
                                "content_text": marketing_summary,
                                "author_username": channel_info.get('title', ''),
                                "author_display_name": channel_info.get('title', ''),
                                "post_type": "video",
                                "engagement_metrics": {
                                    "view_count": int(video.get('view_count', 0)) if video.get('view_count') else 0,
                                    "like_count": int(video.get('like_count', 0)) if video.get('like_count') else 0,
                                    "comment_count": int(video.get('comment_count', 0)) if video.get('comment_count') else 0
                                },
                                "media_urls": [video.get('thumbnail')] if video.get('thumbnail') else [],
                                "posted_at": datetime.fromisoformat(video['published_at'].replace('Z', '+00:00')) if video.get('published_at') else None
                            }
                            
                            # Save the post using MonitoringService
                            saved_post = await self.monitoring_service.process_social_media_post(
                                competitor_id=competitor_id,
                                platform="youtube",
                                post_data=post_data
                            )
                            
                            # Create intelligent alert if the video is deemed alert-worthy
                            if is_alert_worthy and saved_post and alert_reason:
                                await self._create_intelligent_alert(competitor_id, saved_post, video, alert_reason)
                            
                            if saved_post:
                                processed_posts.append({
                                    "id": str(saved_post.id),
                                    "post_id": saved_post.post_id,
                                    "title": video.get('title'),
                                    "url": saved_post.post_url,
                                    "engagement": saved_post.engagement_metrics,
                                    "is_alert_worthy": is_alert_worthy,
                                    "alert_reason": alert_reason if is_alert_worthy else None
                                })
                                logger.info(f"✅ Saved video: {video.get('title', 'Unknown')} (ID: {saved_post.id})")
                            
                        except Exception as e:
                            logger.error(f"❌ Error processing video {video.get('video_id', 'unknown')}: {e}")
                            continue
                    
                else:
                    logger.warning(f"❌ Could not find channel for handle: {youtube_handle}")
            
            logger.info(f"✅ Processed {len(processed_posts)} YouTube videos for {youtube_handle}")
            
        except Exception as e:
            logger.error(f"❌ Error processing analysis results: {e}")
        
        return processed_posts
    
    async def _analyze_video_for_alerts(self, title: str, description: str, captions: str, view_count: int, like_count: int, comment_count: int) -> tuple[str, bool, str]:
        """
        Analyze video content to determine if it should trigger an alert and generate marketing summary
        
        Returns:
            tuple: (marketing_summary, is_alert_worthy, alert_reason)
        """
        try:
            # Prepare content for analysis
            content_parts = [f"Title: {title}"]
            if description:
                content_parts.append(f"Description: {description[:300]}")
            if captions:
                content_parts.append(f"Video Content/Captions: {captions}")
            
            content_text = "\n\n".join(content_parts)
            
            prompt = f"""
Analyze this YouTube video for competitive intelligence and alert assessment:

ENGAGEMENT METRICS:
- Views: {view_count}
- Likes: {like_count}
- Comments: {comment_count}

VIDEO CONTENT:
{content_text}

ANALYSIS TASKS:
1. Create a marketing-focused summary highlighting:
   - Key marketing messages and value propositions
   - Target audience insights
   - Content strategy patterns
   - Competitive advantages or opportunities

2. Determine if this video is ALERT-WORTHY based on:
   - Unusually high engagement for typical YouTube content
   - New product launches or major announcements
   - Viral marketing campaigns or trending content
   - Significant strategic shifts or messaging changes
   - Major brand partnerships or collaborations
   - Content that could impact competitive positioning

RESPONSE FORMAT:
First provide the marketing summary (max 300 words), then on a new line state:
ALERT_ASSESSMENT: YES or NO
ALERT_REASON: [Brief reason if YES, or "None" if NO]

Be selective - only flag truly significant competitive events, not routine content.
"""
            
            response = await self.llm.ainvoke(prompt)
            full_response = response.content.strip()
            
            # Parse response to extract summary and alert assessment
            lines = full_response.split('\n')
            alert_line = next((line for line in lines if line.startswith('ALERT_ASSESSMENT:')), '')
            reason_line = next((line for line in lines if line.startswith('ALERT_REASON:')), '')
            
            is_alert_worthy = 'YES' in alert_line.upper()
            alert_reason = reason_line.replace('ALERT_REASON:', '').strip() if reason_line else ""
            
            # Remove alert assessment lines from summary
            marketing_summary = '\n'.join(line for line in lines 
                                        if not line.startswith('ALERT_ASSESSMENT:') 
                                        and not line.startswith('ALERT_REASON:'))
            
            # Add performance metrics
            performance_note = f"\n\n📊 Performance: {view_count} views, {like_count} likes, {comment_count} comments"
            alert_indicator = " 🚨 ALERT-WORTHY" if is_alert_worthy else ""
            
            final_summary = f"🎯 Marketing Analysis{alert_indicator}:\n{marketing_summary.strip()}{performance_note}"
            
            return final_summary, is_alert_worthy, alert_reason
            
        except Exception as e:
            logger.error(f"❌ Error analyzing video for alerts: {e}")
            # Return basic summary on error
            basic_summary = f"📺 {title}\n\n📝 {description[:200] if description else 'No description available'}\n\n📊 Performance: {view_count} views, {like_count} likes, {comment_count} comments"
            return basic_summary, False, ""
    
    async def _create_intelligent_alert(self, competitor_id: str, saved_post, video: Dict, alert_reason: str) -> None:
        """
        Create an intelligent alert record for a significant video based on AI analysis
        """
        try:
            # Get competitor info for alert context
            competitor = await self._get_competitor(competitor_id)
            if not competitor:
                logger.error(f"Could not find competitor {competitor_id} for alert creation")
                return
            
            # Create intelligent alert data
            alert_data = {
                "competitor_id": competitor_id,
                "alert_type": "youtube_significant_content",
                "priority": "high",  # AI determined this is alert-worthy
                "title": f"Significant YouTube Activity: {video.get('title', 'Unknown Title')}",
                "description": f"AI analysis flagged this video as strategically significant: {alert_reason}. Video has {video.get('view_count', 0)} views and {video.get('like_count', 0)} likes.",
                "metadata": {
                    "platform": "youtube",
                    "post_id": saved_post.post_id,
                    "video_url": video.get('video_url'),
                    "engagement_metrics": {
                        "views": video.get('view_count', 0),
                        "likes": video.get('like_count', 0),
                        "comments": video.get('comment_count', 0)
                    },
                    "ai_analysis": {
                        "alert_reason": alert_reason,
                        "analysis_timestamp": datetime.now(timezone.utc).isoformat()
                    }
                },
                "source_url": video.get('video_url'),
                "detected_at": datetime.utcnow()
            }
            
            # Create alert using monitoring service
            await self.monitoring_service.create_alert(alert_data)
            logger.info(f"🚨 Created intelligent alert for significant YouTube video: {video.get('title', 'Unknown')}")
            logger.info(f"   📝 Alert reason: {alert_reason}")
            
        except Exception as e:
            logger.error(f"Error creating intelligent alert for video: {e}")
    
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
        logger.info("YouTubeAgent closed")
        pass