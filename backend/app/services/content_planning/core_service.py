"""
Core Content Planning service for business logic
Follows the same pattern as other services in the app
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import json
import logging

# Don't import AI agents on initialization - only when needed
# from .agents.main_agent import ContentPlanningAgent
# from .tools.content_generator import ContentGenerator, generate_content_variations
# from .tools.competitor_analyzer import CompetitorAnalyzer
# from .tools.hashtag_researcher import HashtagResearcher
from .config.settings import settings

logger = logging.getLogger(__name__)

class ContentPlanningService:
    """Service for content planning operations using AI agents and tools"""
    
    def __init__(self):
        """Initialize the service - AI agents are initialized lazily when needed"""
        # Don't initialize AI agents on startup - only when generate_content is called
        self._agent = None
        self._content_generator = None
        self._competitor_analyzer = None
        self._hashtag_researcher = None
        logger.info("🔧 ContentPlanningService initialized (AI agents will be initialized when needed)")
    
    @property
    def agent(self):
        """Lazy initialization of ContentPlanningAgent"""
        if self._agent is None:
            try:
                from .agents.main_agent import ContentPlanningAgent
                self._agent = ContentPlanningAgent()
                logger.info("🤖 ContentPlanningAgent initialized")
            except ImportError as e:
                logger.warning(f"⚠️ ContentPlanningAgent not available: {e}")
                return None
        return self._agent
    
    @property
    def content_generator(self):
        """Lazy initialization of ContentGenerator"""
        if self._content_generator is None:
            try:
                from .tools.content_generator import ContentGenerator
                self._content_generator = ContentGenerator()
                logger.info("📝 ContentGenerator initialized")
            except ImportError as e:
                logger.warning(f"⚠️ ContentGenerator not available: {e}")
                return None
        return self._content_generator
    
    @property
    def competitor_analyzer(self):
        """Lazy initialization of CompetitorAnalyzer"""
        if self._competitor_analyzer is None:
            try:
                from .tools.competitor_analyzer import CompetitorAnalyzer
                self._competitor_analyzer = CompetitorAnalyzer()
                logger.info("🔍 CompetitorAnalyzer initialized")
            except ImportError as e:
                logger.warning(f"⚠️ CompetitorAnalyzer not available: {e}")
                return None
        return self._competitor_analyzer
    
    @property
    def hashtag_researcher(self):
        """Lazy initialization of HashtagResearcher"""
        if self._hashtag_researcher is None:
            try:
                from .tools.hashtag_researcher import HashtagResearcher
                self._hashtag_researcher = HashtagResearcher()
                logger.info("🏷️ HashtagResearcher initialized")
            except ImportError as e:
                logger.warning(f"⚠️ HashtagResearcher not available: {e}")
                return None
        return self._hashtag_researcher
    
    @property
    def supabase_client(self):
        """Lazy initialization of SupabaseClient"""
        if not hasattr(self, '_supabase_client') or self._supabase_client is None:
            try:
                from app.core.supabase_client import SupabaseClient
                self._supabase_client = SupabaseClient()
                logger.info("🗄️ SupabaseClient initialized for content planning")
            except ImportError as e:
                logger.warning(f"⚠️ SupabaseClient not available: {e}")
                self._supabase_client = None
        return self._supabase_client
    
    async def generate_content(
        self,
        clerk_id: str,
        platform: str,
        content_type: str,
        tone: str,
        target_audience: str,
        custom_requirements: Optional[str] = None,
        generate_variations: bool = False,
        industry: Optional[str] = None  # Add industry parameter
    ) -> Dict[str, Any]:
        """Generate AI-optimized social media content based on competitor insights"""
        try:
            logger.info(f"📝 Generating content for {platform} for Clerk ID: {clerk_id}")
            
            # Check if AI agents are available
            if not self.competitor_analyzer or not self.content_generator:
                logger.warning("⚠️ AI agents not available, returning mock content")
                return {
                    "success": True,
                    "content": {
                        "post_content": f"🎯 {content_type.title()} content for {platform}. This is AI-generated content optimized for {target_audience} with a {tone} tone. {custom_requirements or ''}",
                        "hashtags": [f"#{platform.title()}", f"#{content_type.title()}"],
                        "optimal_posting_time": "Tuesday-Thursday, 9-11 AM",
                        "platform": platform,
                        "content_type": content_type,
                        "tone": tone
                    }
                }
            
            # First, get competitor insights for the user
            competitor_analysis = await self.competitor_analyzer._arun(
                clerk_id=clerk_id,
                analysis_type="trend_analysis"
            )
            
            # Log competitor analysis results for debugging
            logger.info(f"🔍 Competitor analysis result: success={competitor_analysis.get('success')}, data_source={competitor_analysis.get('data_source')}")
            logger.info(f"🔍 Analysis data keys: {list(competitor_analysis.get('analysis_data', {}).keys()) if competitor_analysis.get('analysis_data') else 'None'}")
            
            # Prepare competitor insights with better fallback handling
            if competitor_analysis.get("success") and competitor_analysis.get("analysis_data"):
                competitor_insights = json.dumps(competitor_analysis.get("analysis_data", {}))
                logger.info(f"✅ Using competitor analysis data: {len(competitor_insights)} characters")
            else:
                # Create fallback competitor insights when no data is available
                fallback_insights = {
                    "content_trends": {
                        "successful_content_types": ["educational", "promotional", "behind_the_scenes"],
                        "common_themes": ["innovation", "growth", "industry_trends", "best_practices"],
                        "engagement_drivers": ["practical_tips", "industry_insights", "success_stories"]
                    },
                    "hashtag_analysis": {
                        "trending_hashtags": ["#Innovation", "#Growth", "#IndustryTrends", "#BestPractices", "#Success"],
                        "high_performing": ["#Leadership", "#Technology", "#Business", "#Strategy", "#Future"]
                    },
                    "timing_insights": {
                        "optimal_posting_times": ["Tuesday-Thursday, 9-11 AM", "Monday-Wednesday, 5-7 PM"],
                        "best_days": ["Tuesday", "Wednesday", "Thursday"]
                    },
                    "tone_voice": {
                        "successful_approaches": ["professional", "authentic", "helpful", "insightful"],
                        "engagement_patterns": ["question_posts", "tip_sharing", "industry_commentary"]
                    },
                    "data_source": "fallback_insights",
                    "note": "Using industry best practices and general social media insights"
                }
                competitor_insights = json.dumps(fallback_insights)
                logger.info(f"⚠️ Using fallback competitor insights: {len(competitor_insights)} characters")
            
            # Get user's industry - use provided industry or fetch from preferences
            user_industry = industry
            if not user_industry:
                user_industry = await self._get_user_industry(clerk_id)
                if not user_industry:
                    logger.warning(f"⚠️ Could not determine industry for user {clerk_id}, using default")
                    user_industry = "technology"  # Default fallback
            
            # Generate content
            logger.info(f"🔧 Calling content generator with industry: {user_industry}, platform: {platform}")
            content_result = await self.content_generator._arun(
                industry=user_industry,  # Pass industry instead of clerk_id
                platform=platform,
                content_type=content_type,
                tone=tone,
                target_audience=target_audience,
                competitor_insights=competitor_insights,
                custom_requirements=custom_requirements
            )
            
            # Validate content result
            if not content_result or not content_result.get("success"):
                logger.error(f"❌ Content generation failed: {content_result}")
                return {
                    "success": False,
                    "error": content_result.get("error", "Content generation failed") if content_result else "Content generation failed"
                }
            
            # Ensure content has required fields
            content = content_result.get("content", content_result)
            if not content.get("post_content"):
                logger.error(f"❌ Generated content missing post_content: {content}")
                return {
                    "success": False,
                    "error": "Generated content is missing required fields"
                }
            
            # Log successful content generation
            logger.info(f"✅ Content generated successfully for {platform}")
            logger.info(f"📝 Content length: {len(content.get('post_content', ''))} characters")
            logger.info(f"🏷️ Hashtags count: {len(content.get('hashtags', []))}")
            
            response_data = {
                "success": True,
                "content": content,
                "error": None
            }
            
            # Generate variations if requested
            if generate_variations and content_result.get("success"):
                try:
                    from .tools.content_generator import generate_content_variations
                    variations = await generate_content_variations(
                        {
                            "industry": user_industry,  # Use actual industry instead of clerk_id
                            "platform": platform,
                            "content_type": content_type,
                            "target_audience": target_audience,
                            "competitor_insights": competitor_insights
                        },
                        variation_count=3
                    )
                    response_data["variations"] = variations
                except ImportError:
                    logger.warning("⚠️ Content variations not available")
            
            logger.info(f"✅ Content generated successfully for {platform}")
            return response_data
            
        except Exception as e:
            logger.error(f"❌ Content generation failed: {str(e)}")
            return {
                "success": False,
                "error": f"Content generation failed: {str(e)}"
            }
    
    async def _get_user_industry(self, clerk_id: str) -> Optional[str]:
        """Get user's industry from preferences"""
        try:
            # Try to get from Supabase if available
            if hasattr(self, 'supabase_client') and self.supabase_client:
                # Query user_preferences table
                response = await self.supabase_client.table('user_preferences').select('industry').eq('user_id', clerk_id).execute()
                if response.data:
                    return response.data[0].get('industry')
            
            # Fallback: try to get from competitor analysis if it contains industry info
            try:
                competitor_analysis = await self.competitor_analyzer._arun(
                    clerk_id=clerk_id,
                    analysis_type="trend_analysis"
                )
                
                if competitor_analysis.get("success") and competitor_analysis.get("analysis_data"):
                    # Look for industry in competitor data
                    competitors = competitor_analysis.get("analysis_data", {}).get("competitors", [])
                    for competitor in competitors:
                        if competitor.get("industry") or competitor.get("industry_sector"):
                            return competitor.get("industry") or competitor.get("industry_sector")
            except Exception as e:
                logger.warning(f"⚠️ Could not extract industry from competitor analysis: {e}")
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Could not fetch user industry: {e}")
            return None
    
    async def analyze_competitors(
        self,
        industry: str,
        competitor_ids: Optional[List[str]] = None,
        analysis_type: str = "comprehensive_analysis",
        time_period: str = "last_30_days"
    ) -> Dict[str, Any]:
        """Analyze competitor content for strategic insights"""
        try:
            logger.info(f"🔍 Analyzing competitors for {industry}")
            
            # Check if AI agent is available
            if not self.agent:
                logger.warning("⚠️ AI agent not available, returning mock competitor analysis")
                return {
                    "success": True,
                    "analysis": {
                        "competitor_count": 5,
                        "analysis_type": analysis_type,
                        "time_period": time_period
                    },
                    "insights": {
                        "market_opportunities": ["Video content", "Interactive content", "Educational series"],
                        "content_gaps": [
                            {
                                "type": "topic_gap",
                                "suggestion": "Technical tutorials",
                                "priority": "High",
                                "expected_impact": "High",
                                "implementation_effort": "Medium"
                            }
                        ]
                    },
                    "recommendations": [
                        "Focus on video content creation",
                        "Develop educational content series",
                        "Increase interactive content frequency"
                    ]
                }
            
            # Use AI agent for analysis
            result = self.agent.analyze_competitor_landscape(industry)
            
            if not result.get("success"):
                return result
            
            return {
                "success": True,
                "analysis": result.get("analysis", {}),
                "insights": result.get("insights", {}),
                "recommendations": result.get("recommendations", [])
            }
            
        except Exception as e:
            logger.error(f"❌ Competitor analysis failed: {str(e)}")
            return {
                "success": False,
                "error": f"Competitor analysis failed: {str(e)}"
            }
    
    async def research_hashtags(
        self,
        industry: str,
        content_type: str,
        platform: str,
        target_audience: str,
        custom_keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Research optimal hashtag strategies for content"""
        try:
            logger.info(f"🏷️ Researching hashtags for {platform} in {industry}")
            
            hashtag_result = await self.hashtag_researcher._arun(
                industry=industry,
                content_type=content_type,
                platform=platform,
                target_audience=target_audience,
                custom_keywords=custom_keywords
            )
            
            logger.info(f"✅ Hashtag research completed for {platform}")
            return hashtag_result
            
        except Exception as e:
            logger.error(f"❌ Hashtag research failed: {str(e)}")
            return {
                "success": False,
                "error": f"Hashtag research failed: {str(e)}"
            }
    
    async def generate_content_strategy(
        self,
        clerk_id: str,
        platforms: List[str],
        content_goals: List[str],
        target_audience: str
    ) -> Dict[str, Any]:
        """Generate comprehensive content strategy based on competitive analysis"""
        try:
            logger.info(f"📋 Generating content strategy for Clerk ID: {clerk_id} across {len(platforms)} platforms")
            
            strategy_result = self.agent.generate_content_strategy(
                clerk_id=clerk_id,
                platforms=platforms,
                content_goals=content_goals,
                target_audience=target_audience
            )
            
            logger.info(f"✅ Content strategy generated for Clerk ID: {clerk_id}")
            return strategy_result
            
        except Exception as e:
            logger.error(f"❌ Strategy generation failed: {str(e)}")
            return {
                "success": False,
                "error": f"Strategy generation failed: {str(e)}"
            }
    
    async def generate_content_calendar(
        self,
        clerk_id: str,
        platforms: List[str],
        duration_days: int = 30,
        posts_per_day: int = 2
    ) -> Dict[str, Any]:
        """Generate AI-optimized content calendar"""
        try:
            logger.info(f"📅 Generating content calendar for Clerk ID: {clerk_id} ({duration_days} days)")
            
            calendar_result = self.agent.generate_content_calendar(
                clerk_id=clerk_id,
                platforms=platforms,
                duration_days=duration_days,
                posts_per_day=posts_per_day
            )
            
            logger.info(f"✅ Content calendar generated for Clerk ID: {clerk_id}")
            return calendar_result
            
        except Exception as e:
            logger.error(f"❌ Calendar generation failed: {str(e)}")
            return {
                "success": False,
                "error": f"Calendar generation failed: {str(e)}"
            }
    
    async def identify_content_gaps(
        self,
        clerk_id: str,
        user_content_summary: str
    ) -> Dict[str, Any]:
        """Identify content gaps based on competitor analysis"""
        try:
            logger.info(f"🔍 Identifying content gaps for Clerk ID: {clerk_id}")
            
            gaps_result = self.agent.identify_content_gaps(
                clerk_id=clerk_id,
                user_content_summary=user_content_summary
            )
            
            logger.info(f"✅ Content gaps identified for Clerk ID: {clerk_id}")
            return gaps_result
            
        except Exception as e:
            logger.error(f"❌ Gap analysis failed: {str(e)}")
            return {
                "success": False,
                "error": f"Gap analysis failed: {str(e)}"
            }
    
    async def optimize_posting_schedule(
        self,
        clerk_id: str,
        platforms: List[str]
    ) -> Dict[str, Any]:
        """Optimize posting schedule based on competitor timing analysis"""
        try:
            logger.info(f"⏰ Optimizing posting schedule for Clerk ID: {clerk_id} on {len(platforms)} platforms")
            
            schedule_result = self.agent.optimize_posting_schedule(
                clerk_id=clerk_id,
                platforms=platforms
            )
            
            logger.info(f"✅ Posting schedule optimized for Clerk ID: {clerk_id}")
            return schedule_result
            
        except Exception as e:
            logger.error(f"❌ Schedule optimization failed: {str(e)}")
            return {
                "success": False,
                "error": f"Schedule optimization failed: {str(e)}"
            }
    
    async def get_dashboard_data(self, industry: str) -> Dict[str, Any]:
        """Get comprehensive dashboard data for the content planning interface"""
        try:
            logger.info(f"📊 Getting dashboard data for {industry} (no AI agent invoked)")
            
            # Return static/mock data for dashboard - NO AI agent invocation
            # AI agent only runs when user clicks "Create Content" button
            dashboard_data = {
                "success": True,
                "summary": {
                    "scheduled_posts": 24,
                    "gap_opportunities": 8,
                    "competitive_edge": "+23%",
                    "threat_alerts": 3
                },
                "competitive_intelligence": {
                    "new_opportunities": [
                        "Video content creation",
                        "Interactive polls and surveys", 
                        "Behind-the-scenes content"
                    ],
                    "trending_hashtags": [
                        "#TechInnovation",
                        "#AI",
                        "#DigitalTransformation",
                        "#Innovation",
                        "#TechTrends"
                    ]
                },
                "content_gaps": [
                    {
                        "type": "format_gap",
                        "suggestion": "Educational video content",
                        "priority": "High",
                        "expected_impact": "High",
                        "implementation_effort": "Medium"
                    },
                    {
                        "type": "topic_gap", 
                        "suggestion": "Industry trend analysis",
                        "priority": "High",
                        "expected_impact": "Moderate to High",
                        "implementation_effort": "Medium"
                    },
                    {
                        "type": "topic_gap",
                        "suggestion": "Customer success stories", 
                        "priority": "Medium",
                        "expected_impact": "Moderate",
                        "implementation_effort": "Low"
                    }
                ],
                "recent_activity": [
                    {
                        "action": "Gap Identified",
                        "content": "Video content opportunity vs competitors",
                        "time": "1 hour ago",
                        "status": "opportunity"
                    },
                    {
                        "action": "Content Generated",
                        "content": "Weekly Newsletter Content", 
                        "time": "2 hours ago",
                        "status": "draft"
                    },
                    {
                        "action": "Competitor Alert",
                        "content": "New trending hashtag detected",
                        "time": "3 hours ago", 
                        "status": "alert"
                    }
                ],
                "performance_metrics": {
                    "content_performance": {
                        "engagement_rate": "4.2%",
                        "reach_growth": "+15%",
                        "click_through_rate": "2.8%"
                    },
                    "hashtag_effectiveness": {
                        "top_performing": ["#TechInnovation", "#AI"],
                        "trending": ["#DigitalTransformation", "#Innovation"]
                    }
                }
            }
            
            logger.info(f"✅ Dashboard data loaded for {industry} (static data, no AI agent)")
            return dashboard_data
            
        except Exception as e:
            logger.error(f"❌ Dashboard data loading failed: {str(e)}")
            return {
                "success": False,
                "error": f"Dashboard data loading failed: {str(e)}"
            }
    
    async def get_industry_insights(self, industry: str) -> Dict[str, Any]:
        """Get specific insights for an industry"""
        try:
            logger.info(f"💡 Getting industry insights for {industry} (no AI agent invoked)")
            
            # Return static/mock data for industry insights - NO AI agent invocation
            # AI agent only runs when user clicks "Create Content" button
            insights = {
                "industry": industry,
                "key_metrics": {
                    "market_size": "$2.5T",
                    "growth_rate": "+12%",
                    "competition_level": "High"
                },
                "content_trends": {
                    "video_content": "+45%",
                    "interactive_content": "+32%",
                    "educational_content": "+28%"
                },
                "optimal_posting_times": {
                    "linkedin": "9-11 AM, 1-3 PM",
                    "twitter": "8-10 AM, 2-4 PM",
                    "instagram": "11 AM-1 PM, 7-9 PM"
                },
                "competitor_count": 5,
                "recommendations": [
                    "Focus on video content creation",
                    "Develop educational content series",
                    "Increase interactive content frequency"
                ]
            }
            
            logger.info(f"✅ Industry insights loaded for {industry} (static data, no AI agent)")
            return {
                "success": True,
                "insights": insights
            }
            
        except Exception as e:
            logger.error(f"❌ Industry insights loading failed: {str(e)}")
            return {
                "success": False,
                "error": f"Industry insights loading failed: {str(e)}"
            }
    
    def get_supported_options(self) -> Dict[str, List[str]]:
        """Get supported industries, platforms, content types, and tones"""
        return {
            "industries": settings.supported_industries,
            "platforms": settings.supported_platforms,
            "content_types": settings.content_types,
            "tones": settings.tone_options
        }
