"""
Simple Sequential Monitoring Service
Runs platform-specific agents one by one instead of complex multi-agent system
"""

import logging
from typing import Dict, List, Any
import hashlib
from datetime import datetime, timezone

from app.services.monitoring.agents.sub_agents.youtube_agent import YouTubeAgent
from app.services.monitoring.agents.sub_agents.website_agent import WebsiteAgent
from app.services.monitoring.agents.sub_agents.browser_agent import BrowserAgent
from app.services.monitoring.agents.sub_agents.instagram_agent import InstagramAgent
from app.services.monitoring.agents.sub_agents.twitter_agent import TwitterAgent
from app.services.monitoring.supabase_client import supabase_client

logger = logging.getLogger(__name__)


class SimpleMonitoringService:
    """Simple sequential monitoring service that runs agents one by one"""
    
    def __init__(self):
        logger.info("🤖 SimpleMonitoringService initializing...")
        
        # Initialize agents
        self.agents = {}
        
        try:
            self.agents['youtube'] = YouTubeAgent()
            logger.info("✅ YouTube agent created")
        except Exception as e:
            logger.error(f"❌ Failed to create YouTube agent: {e}")
            self.agents['youtube'] = None
            
        try:
            self.agents['website'] = WebsiteAgent()
            logger.info("✅ Website agent created")
        except Exception as e:
            logger.error(f"❌ Failed to create Website agent: {e}")
            self.agents['website'] = None
            
        try:
            self.agents['browser'] = BrowserAgent()
            logger.info("✅ Browser agent created (Tavily search)")
        except Exception as e:
            logger.error(f"❌ Failed to create Browser agent: {e}")
            self.agents['browser'] = None
            
        try:
            self.agents['instagram'] = InstagramAgent()
            logger.info("✅ Instagram agent created")
        except Exception as e:
            logger.error(f"❌ Failed to create Instagram agent: {e}")
            self.agents['instagram'] = None
            
        try:
            self.agents['twitter'] = TwitterAgent()
            logger.info("✅ Twitter agent created")
        except Exception as e:
            logger.error(f"❌ Failed to create Twitter agent: {e}")
            self.agents['twitter'] = None
        
        logger.info("🤖 SimpleMonitoringService initialization completed")
    
    async def run_monitoring_for_competitor(self, competitor_id: str, competitor_name: str = None, platforms: List[str] = None) -> Dict[str, Any]:
        """Run monitoring for a specific competitor using the three core agents (youtube, browser, website)"""
        try:
            logger.info(f"🚀 Starting sequential monitoring for competitor {competitor_id}")
            
            # Get competitor details from Supabase
            competitor_details = await supabase_client.get_competitor_details(competitor_id)
            
            if not competitor_details:
                logger.error(f"❌ No database session available - cannot fetch competitor details as the agents cannot get the information from database for current competitor {competitor_id}")
                return {
                    "competitor_id": competitor_id,
                    "status": "failed",
                    "error": "Competitor not found in database"
                }
            
            # Use competitor details from database
            competitor_name = competitor_details.get('name', competitor_name)
            website_url = competitor_details.get('website_url')
            social_media_handles = competitor_details.get('social_media_handles')
            
            # Validate competitor data
            if not competitor_name or competitor_name.strip() == "":
                logger.error(f"❌ Invalid competitor name for {competitor_id}: '{competitor_name}'")
                return {
                    "competitor_id": competitor_id,
                    "status": "failed",
                    "error": "Invalid competitor name"
                }
            
            # Ensure social_media_handles is a dict, not None
            if social_media_handles is None:
                social_media_handles = {}
                logger.info(f"   📱 No social media handles found, using empty dict")
            
            logger.info(f"✅ Retrieved competitor details: {competitor_name} (ID: {competitor_id})")
            logger.info(f"   🌐 Website: {website_url}")
            logger.info(f"   📱 Social handles: {social_media_handles}")
            
            # Use provided platforms or default to all three core agents
            if platforms is None:
                platforms = ["youtube", "browser", "website"]
                logger.info(f"🎯 Using default core monitoring platforms: {platforms}")
            else:
                logger.info(f"🎯 Using specified monitoring platforms: {platforms}")
            
            results = {}
            errors = []
            monitoring_data_count = 0
            
            # Run agents sequentially
            for platform in platforms:
                if platform in self.agents and self.agents[platform] is not None:
                    try:
                        logger.info(f"🔍 Running {platform} agent for competitor {competitor_name}")
                        agent = self.agents[platform]
                        
                        # Prepare platform-specific parameters
                        if platform == 'youtube':
                            # Get YouTube handle from social media handles, handle null case
                            youtube_handle = None
                            if social_media_handles and isinstance(social_media_handles, dict):
                                youtube_handle = social_media_handles.get('youtube')
                            youtube_handle = youtube_handle or competitor_name
                            result = await agent.analyze_competitor(competitor_id, youtube_handle)
                        elif platform == 'website':
                            # Use actual website URL from database
                            target_url = website_url or f"https://{competitor_name.lower().replace(' ', '')}.com"
                            result = await agent.analyze_competitor(competitor_id, target_url)
                        elif platform == 'browser':
                            # Browser agent uses Tavily search for web content discovery
                            result = await agent.analyze_competitor(competitor_id, competitor_name)
                        
                        # Process and save monitoring data
                        if result and result.get('status') == 'completed':
                            platform_data_count = await self._process_agent_results(competitor_id, platform, result)
                            monitoring_data_count += platform_data_count
                        
                        results[platform] = result
                        logger.info(f"✅ {platform} agent completed for competitor {competitor_name}")
                        
                    except Exception as e:
                        error_msg = f"Error in {platform} agent: {str(e)}"
                        logger.error(f"❌ {error_msg}")
                        logger.error(f"   🔍 Error type: {type(e).__name__}")
                        logger.error(f"   📍 Platform: {platform}, Competitor: {competitor_name}")
                        errors.append(error_msg)
                        results[platform] = {
                            "error": str(e),
                            "error_type": type(e).__name__,
                            "platform": platform,
                            "competitor_name": competitor_name
                        }
                elif platform in self.agents and self.agents[platform] is None:
                    error_msg = f"{platform} agent not initialized"
                    logger.warning(f"⚠️ {error_msg}")
                    errors.append(error_msg)
                    results[platform] = {"error": error_msg}
                else:
                    error_msg = f"Unknown platform: {platform}"
                    logger.warning(f"⚠️ {error_msg}")
                    errors.append(error_msg)
            
            # Update competitor's last scan time
            await supabase_client.update_competitor_scan_time(competitor_id)
            
            logger.info(f"✅ Sequential monitoring completed for competitor {competitor_name}")
            
            return {
                "competitor_id": competitor_id,
                "status": "completed",
                "platforms_analyzed": list(results.keys()),
                "platform_results": results,
                "errors": errors,
                "competitor_name": competitor_name,
                "monitoring_data_count": monitoring_data_count
            }
            
        except Exception as e:
            logger.error(f"❌ Error in sequential monitoring for competitor {competitor_id}: {e}")
            return {
                "competitor_id": competitor_id,
                "status": "failed",
                "error": str(e)
            }
    
    async def run_platform_specific_monitoring(self, competitor_id: str, platform: str) -> Dict[str, Any]:
        """Run monitoring for a specific platform and competitor"""
        try:
            logger.info(f"🚀 Starting {platform} monitoring for competitor {competitor_id}")
            
            # Validate platform
            if platform not in self.agents:
                return {
                    "platform": platform,
                    "competitor_id": competitor_id,
                    "status": "failed",
                    "error": f"Unknown platform: {platform}"
                }
            
            if self.agents[platform] is None:
                return {
                    "platform": platform,
                    "competitor_id": competitor_id,
                    "status": "failed",
                    "error": f"{platform} agent not initialized"
                }
            
            # Run monitoring for just this platform
            result = await self.run_monitoring_for_competitor(competitor_id, platforms=[platform])
            
            # Extract platform-specific result
            platform_result = result.get('platform_results', {}).get(platform, {})
            
            # If the platform failed, return the error directly
            if platform in result.get('errors', []):
                return {
                    "platform": platform,
                    "competitor_id": competitor_id,
                    "status": "failed",
                    "error": f"Platform {platform} failed: {result.get('errors', [])}"
                }
            
            return {
                "platform": platform,
                "competitor_id": competitor_id,
                "status": "completed",
                "result": platform_result,
                "message": f"{platform} monitoring completed successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Error in {platform} monitoring for competitor {competitor_id}: {e}")
            return {
                "platform": platform,
                "competitor_id": competitor_id,
                "status": "failed",
                "error": str(e)
            }
    
    async def run_monitoring_for_all_active_competitors(self, user_id: str) -> Dict[str, Any]:
        """Run monitoring for all active competitors of a user"""
        try:
            logger.info(f"🚀 Starting monitoring for all active competitors of user {user_id}")
            
            # Get all active competitors for the user
            competitors = await supabase_client.get_competitors_due_for_scan()
            
            if not competitors:
                logger.info(f"ℹ️ No active competitors found for user {user_id}")
                return {
                    "user_id": user_id,
                    "status": "completed",
                    "total_competitors": 0,
                    "competitors_scanned": 0,
                    "successful_scans": 0,
                    "failed_scans": 0,
                    "message": "No active competitors to scan"
                }
            
            logger.info(f"📊 Found {len(competitors)} active competitors for user {user_id}")
            
            results = {}
            successful_scans = 0
            failed_scans = 0
            
            # Run monitoring for each competitor
            for competitor in competitors:
                competitor_id = competitor['id']
                competitor_name = competitor.get('name', f'Competitor_{competitor_id}')
                
                try:
                    logger.info(f"🔍 Running monitoring for competitor {competitor_name} (ID: {competitor_id})")
                    
                    result = await self.run_monitoring_for_competitor(competitor_id, competitor_name)
                    results[competitor_id] = result
                    
                    if result.get('status') == 'completed':
                        successful_scans += 1
                        logger.info(f"✅ Monitoring completed for {competitor_name}")
                    else:
                        failed_scans += 1
                        logger.error(f"❌ Monitoring failed for {competitor_name}: {result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    failed_scans += 1
                    error_msg = f"Error in monitoring for {competitor_name}: {str(e)}"
                    logger.error(f"❌ {error_msg}")
                    results[competitor_id] = {
                        "status": "failed",
                        "error": error_msg
                    }
            
            logger.info(f"✅ Monitoring completed for all competitors of user {user_id}")
            
            return {
                "user_id": user_id,
                "status": "completed",
                "total_competitors": len(competitors),
                "competitors_scanned": len(competitors),
                "successful_scans": successful_scans,
                "failed_scans": failed_scans,
                "competitor_results": results,
                "message": f"Monitoring completed for {len(competitors)} competitors"
            }
            
        except Exception as e:
            logger.error(f"❌ Error in monitoring for all active competitors of user {user_id}: {e}")
            return {
                "user_id": user_id,
                "status": "failed",
                "error": str(e)
            }
    
    async def _process_agent_results(self, competitor_id: str, platform: str, result: Dict[str, Any]) -> int:
        """Process and save agent results to database"""
        try:
            data_count = 0
            
            # Extract posts/data from agent result
            posts = result.get('posts', [])
            if not posts:
                logger.info(f"   ℹ️ No posts found for {platform}")
                return 0
            
            # Check if posts are already processed (have 'id' field)
            if posts and 'id' in posts[0]:
                logger.info(f"   ℹ️ Posts for {platform} are already processed and saved")
                return len(posts)  # Return count of already processed posts
            
            for post in posts:
                try:
                    # Generate content hash
                    content_text = post.get('content_text', '')
                    content_hash = hashlib.md5(content_text.encode()).hexdigest()
                    
                    # Check if post already exists
                    existing_post = await supabase_client.check_existing_post(
                        competitor_id, platform, post.get('post_id', '')
                    )
                    
                    if existing_post:
                        # Check if content has changed
                        if existing_post.get('content_hash') != content_hash:
                            logger.info(f"   ✏️ Content change detected for {platform} post")
                            
                            # Update existing post
                            updated_data = {
                                'content_hash': content_hash,
                                'content_text': content_text,
                                'is_content_change': True,
                                'previous_content_hash': existing_post.get('content_hash'),
                                'updated_at': datetime.now(timezone.utc).isoformat()
                            }
                            
                            await supabase_client.update_post_content(existing_post['id'], updated_data)
                            
                            # Create content change alert
                            await self._create_content_change_alert(competitor_id, platform, post)
                        else:
                            logger.info(f"   ✅ No changes detected for {platform} post")
                    else:
                        # New post - save to database
                        monitoring_data = {
                            'competitor_id': str(competitor_id),
                            'platform': platform,
                            'post_id': post.get('post_id'),
                            'post_url': post.get('post_url'),
                            'content_text': content_text,
                            'content_hash': content_hash,
                            'media_urls': post.get('media_urls', []),
                            'engagement_metrics': post.get('engagement_metrics', {}),
                            'author_username': post.get('author_username'),
                            'author_display_name': post.get('author_display_name'),
                            'author_avatar_url': post.get('author_avatar_url'),
                            'post_type': post.get('post_type', 'post'),
                            'language': post.get('language', 'en'),
                            'sentiment_score': post.get('sentiment_score', 0.0),
                            'detected_at': datetime.now(timezone.utc).isoformat(),
                            'posted_at': post.get('posted_at'),
                            'is_new_post': True,
                            'is_content_change': False
                        }
                        
                        data_id = await supabase_client.save_monitoring_data(monitoring_data)
                        if data_id:
                            data_count += 1
                            
                            # Create new post alert
                            await self._create_new_post_alert(competitor_id, platform, post, data_id)
                            
                except Exception as e:
                    logger.error(f"   ❌ Error processing {platform} post: {e}")
                    continue
            
            logger.info(f"   📊 Processed {data_count} new posts for {platform}")
            return data_count
            
        except Exception as e:
            logger.error(f"❌ Error processing agent results for {platform}: {e}")
            return 0
    
    async def _create_new_post_alert(self, competitor_id: str, platform: str, post: Dict[str, Any], data_id: str):
        """Create alert for new post"""
        try:
            # Get competitor details to get user_id
            competitor_details = await supabase_client.get_competitor_details(competitor_id)
            user_id = competitor_details.get('user_id') if competitor_details else None
            
            alert_data = {
                'user_id': user_id,
                'competitor_id': str(competitor_id),
                'monitoring_data_id': data_id,
                'alert_type': 'new_post',
                'priority': 'low',
                'title': f'New Post Detected - {platform}',
                'message': f'New post detected on {platform}',
                'alert_metadata': {
                    'platform': platform,
                    'post_id': post.get('post_id'),
                    'content_preview': post.get('content_text', '')[:100] if post.get('content_text') else None
                },
                'is_read': False,
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            await supabase_client.create_alert(alert_data)
            logger.info(f"   🚨 Created new post alert for {platform}")
            
        except Exception as e:
            logger.error(f"   ❌ Error creating new post alert: {e}")
    
    async def _create_content_change_alert(self, competitor_id: str, platform: str, post: Dict[str, Any]):
        """Create alert for content change"""
        try:
            # Get competitor details to get user_id
            competitor_details = await supabase_client.get_competitor_details(competitor_id)
            user_id = competitor_details.get('user_id') if competitor_details else None
            
            alert_data = {
                'user_id': user_id,
                'competitor_id': str(competitor_id),
                'monitoring_data_id': None,  # Content change alerts don't have monitoring data ID
                'alert_type': 'content_change',
                'priority': 'medium',
                'title': f'Content Change Detected - {platform}',
                'message': f'Content has been modified on {platform}',
                'alert_metadata': {
                    'platform': platform,
                    'post_id': post.get('post_id'),
                    'change_type': 'content_modification'
                },
                'is_read': False,
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            await supabase_client.create_alert(alert_data)
            logger.info(f"   🚨 Created content change alert for {platform}")
            
        except Exception as e:
            logger.error(f"   ❌ Error creating content change alert: {e}")
    
    async def close(self):
        """Close all agents"""
        for platform, agent in self.agents.items():
            try:
                if agent is None:
                    logger.info(f"ℹ️  Skipping {platform} agent (not initialized)")
                    continue
                    
                logger.info(f"🔒 Closing {platform} agent...")
                
                if hasattr(agent, 'close'):
                    await agent.close()
                    logger.info(f"✅ Closed {platform} agent")
                else:
                    logger.warning(f"⚠️  {platform} agent does not have close method")
                    
            except Exception as e:
                logger.error(f"❌ Error closing {platform} agent: {e}")
        
        logger.info("🤖 SimpleMonitoringService closed")
