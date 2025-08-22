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
    
    async def generate_content(
        self,
        industry: str,
        platform: str,
        content_type: str,
        tone: str,
        target_audience: str,
        custom_requirements: Optional[str] = None,
        generate_variations: bool = False
    ) -> Dict[str, Any]:
        """Generate AI-optimized social media content based on competitor insights"""
        try:
            logger.info(f"📝 Generating content for {platform} in {industry} industry")
            
            # Check if AI agents are available
            if not self.competitor_analyzer or not self.content_generator:
                logger.warning("⚠️ AI agents not available, returning mock content")
                return {
                    "success": True,
                    "content": {
                        "post_content": f"🎯 {content_type.title()} content for {platform} in the {industry} industry. This is AI-generated content optimized for {target_audience} with a {tone} tone. {custom_requirements or ''}",
                        "hashtags": [f"#{industry.title()}", f"#{platform.title()}", f"#{content_type.title()}"],
                        "optimal_posting_time": "Tuesday-Thursday, 9-11 AM",
                        "platform": platform,
                        "content_type": content_type,
                        "tone": tone
                    }
                }
            
            # First, get competitor insights for the industry
            competitor_analysis = self.competitor_analyzer._run(
                industry=industry,
                analysis_type="trend_analysis"
            )
            
            competitor_insights = json.dumps(competitor_analysis.get("analysis_data", {}))
            
            # Generate content
            content_result = self.content_generator._run(
                industry=industry,
                platform=platform,
                content_type=content_type,
                tone=tone,
                target_audience=target_audience,
                competitor_insights=competitor_insights,
                custom_requirements=custom_requirements
            )
            
            response_data = {
                "success": content_result.get("success", False),
                "content": content_result if content_result.get("success") else None,
                "error": content_result.get("error") if not content_result.get("success") else None
            }
            
            # Generate variations if requested
            if generate_variations and content_result.get("success"):
                try:
                    from .tools.content_generator import generate_content_variations
                    variations = generate_content_variations(
                        {
                            "industry": industry,
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
            
            hashtag_result = self.hashtag_researcher._run(
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
        industry: str,
        platforms: List[str],
        content_goals: List[str],
        target_audience: str
    ) -> Dict[str, Any]:
        """Generate comprehensive content strategy based on competitive analysis"""
        try:
            logger.info(f"📋 Generating content strategy for {industry} across {len(platforms)} platforms")
            
            strategy_result = self.agent.generate_content_strategy(
                industry=industry,
                platforms=platforms,
                content_goals=content_goals,
                target_audience=target_audience
            )
            
            logger.info(f"✅ Content strategy generated for {industry}")
            return strategy_result
            
        except Exception as e:
            logger.error(f"❌ Strategy generation failed: {str(e)}")
            return {
                "success": False,
                "error": f"Strategy generation failed: {str(e)}"
            }
    
    async def generate_content_calendar(
        self,
        industry: str,
        platforms: List[str],
        duration_days: int = 30,
        posts_per_day: int = 2
    ) -> Dict[str, Any]:
        """Generate AI-optimized content calendar"""
        try:
            logger.info(f"📅 Generating content calendar for {industry} ({duration_days} days)")
            
            calendar_result = self.agent.generate_content_calendar(
                industry=industry,
                platforms=platforms,
                duration_days=duration_days,
                posts_per_day=posts_per_day
            )
            
            logger.info(f"✅ Content calendar generated for {industry}")
            return calendar_result
            
        except Exception as e:
            logger.error(f"❌ Calendar generation failed: {str(e)}")
            return {
                "success": False,
                "error": f"Calendar generation failed: {str(e)}"
            }
    
    async def identify_content_gaps(
        self,
        industry: str,
        user_content_summary: str
    ) -> Dict[str, Any]:
        """Identify content gaps based on competitor analysis"""
        try:
            logger.info(f"🔍 Identifying content gaps for {industry}")
            
            gaps_result = self.agent.identify_content_gaps(
                industry=industry,
                user_content_summary=user_content_summary
            )
            
            logger.info(f"✅ Content gaps identified for {industry}")
            return gaps_result
            
        except Exception as e:
            logger.error(f"❌ Gap analysis failed: {str(e)}")
            return {
                "success": False,
                "error": f"Gap analysis failed: {str(e)}"
            }
    
    async def optimize_posting_schedule(
        self,
        industry: str,
        platforms: List[str]
    ) -> Dict[str, Any]:
        """Optimize posting schedule based on competitor timing analysis"""
        try:
            logger.info(f"⏰ Optimizing posting schedule for {industry} on {len(platforms)} platforms")
            
            schedule_result = self.agent.optimize_posting_schedule(
                industry=industry,
                platforms=platforms
            )
            
            logger.info(f"✅ Posting schedule optimized for {industry}")
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
