"""
Main Content Planning Agent - Orchestrates AI tools for content strategy
"""

from typing import Dict, List, Any, Optional
import json
import asyncio
import os
import logging

from ..tools.content_generator import ContentGenerator
from ..tools.competitor_analyzer import CompetitorAnalyzer  
from ..tools.hashtag_researcher import HashtagResearcher
from ..config.settings import settings

logger = logging.getLogger(__name__)

class ContentPlanningAgent:
    """
    Main agent that orchestrates content planning tools
    to provide comprehensive content strategy insights and generation.
    """
    
    def __init__(self):
        """Initialize the agent with all tools"""
        
        # Initialize tools
        self.content_generator = ContentGenerator()
        self.competitor_analyzer = CompetitorAnalyzer()
        self.hashtag_researcher = HashtagResearcher()
        
        # Data source tracking
        self.data_source = "mock"
        self.last_analysis_check = None
    
    async def analyze_competitor_landscape(
        self,
        clerk_id: str,
        competitor_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze the competitive landscape for content insights
        """
        
        try:
            # Use competitor analyzer tool
            analyzer = CompetitorAnalyzer()
            
            # Perform comprehensive analysis
            analysis_result = await analyzer._arun(
                clerk_id=clerk_id,
                competitor_ids=competitor_ids,
                analysis_type="comprehensive_analysis"
            )
            
            # Update data source tracking
            if analysis_result.get("success"):
                self.data_source = analysis_result.get("data_source", "mock")
                self.last_analysis_check = analysis_result.get("data_freshness")
            
            return {
                "success": True,
                "analysis": analysis_result,
                "insights": self._extract_key_insights(analysis_result),
                "recommendations": self._generate_strategic_recommendations(analysis_result),
                "data_source": self.data_source
            }
            
        except Exception as e:
            logger.error(f"❌ Competitive analysis failed: {str(e)}")
            return {
                "success": False,
                "error": f"Competitive analysis failed: {str(e)}",
                "data_source": self.data_source
            }
    
    async def generate_content_strategy(
        self,
        clerk_id: str,
        platforms: List[str],
        content_goals: List[str],
        target_audience: str
    ) -> Dict[str, Any]:
        """
        Generate comprehensive content strategy based on competitive insights
        """
        
        try:
            # Step 1: Analyze competitors
            competitor_analysis = await self.analyze_competitor_landscape(clerk_id)
            
            if not competitor_analysis["success"]:
                return competitor_analysis
            
            # Step 2: Research hashtags for each platform
            hashtag_strategies = {}
            hashtag_researcher = HashtagResearcher()
            
            for platform in platforms:
                hashtag_result = await hashtag_researcher._arun(
                    clerk_id=clerk_id, # Assuming clerk_id is the industry for hashtag research
                    content_type="promotional",  # Default type
                    platform=platform,
                    target_audience=target_audience
                )
                hashtag_strategies[platform] = hashtag_result
            
            # Step 3: Generate content recommendations
            content_recommendations = self._generate_content_recommendations(
                competitor_analysis["analysis"],
                hashtag_strategies,
                content_goals,
                platforms
            )
            
            return {
                "success": True,
                "strategy": {
                    "competitor_insights": competitor_analysis["insights"],
                    "hashtag_strategies": hashtag_strategies,
                    "content_recommendations": content_recommendations,
                    "implementation_plan": self._create_implementation_plan(
                        content_recommendations, platforms
                    )
                },
                "executive_summary": self._create_executive_summary(
                    competitor_analysis, hashtag_strategies, content_recommendations
                ),
                "data_source": self.data_source
            }
            
        except Exception as e:
            logger.error(f"❌ Strategy generation failed: {str(e)}")
            return {
                "success": False,
                "error": f"Strategy generation failed: {str(e)}",
                "data_source": self.data_source
            }
    
    async def generate_content_calendar(
        self,
        clerk_id: str,
        platforms: List[str],
        duration_days: int = 30,
        posts_per_day: int = 2
    ) -> Dict[str, Any]:
        """
        Generate a content calendar with AI-optimized posts
        """
        
        try:
            # Get strategy insights
            strategy = await self.generate_content_strategy(
                clerk_id=clerk_id,
                platforms=platforms,
                content_goals=["engagement", "reach", "conversions"],
                target_audience="professionals"
            )
            
            if not strategy["success"]:
                return strategy
            
            # Generate calendar entries
            calendar_entries = []
            content_generator = ContentGenerator()
            
            for day in range(duration_days):
                for post_num in range(posts_per_day):
                    for platform in platforms:
                        # Vary content types
                        content_types = ["educational", "promotional", "behind_the_scenes", "trending_topic"]
                        content_type = content_types[day % len(content_types)]
                        
                        # Generate content
                        competitor_insights = json.dumps(strategy["strategy"]["competitor_insights"])
                        content_result = await content_generator._arun(
                            clerk_id=clerk_id,
                            platform=platform,
                            content_type=content_type,
                            tone="professional",
                            target_audience="professionals",
                            competitor_insights=competitor_insights
                        )
                        
                        if content_result.get("success"):
                            calendar_entry = {
                                "day": day + 1,
                                "post_number": post_num + 1,
                                "platform": platform,
                                "content": content_result,
                                "optimal_time": self._get_optimal_posting_time(platform),
                                "priority": self._calculate_priority(content_result, day)
                            }
                            calendar_entries.append(calendar_entry)
            
            return {
                "success": True,
                "calendar": {
                    "duration_days": duration_days,
                    "total_posts": len(calendar_entries),
                    "platforms": platforms,
                    "entries": calendar_entries
                },
                "calendar_summary": self._create_calendar_summary(calendar_entries),
                "data_source": self.data_source
            }
            
        except Exception as e:
            logger.error(f"❌ Calendar generation failed: {str(e)}")
            return {
                "success": False,
                "error": f"Calendar generation failed: {str(e)}",
                "data_source": self.data_source
            }
    
    async def identify_content_gaps(
        self,
        clerk_id: str,
        user_content_summary: str
    ) -> Dict[str, Any]:
        """
        Identify content gaps based on competitor analysis and user content
        """
        
        try:
            # Analyze competitors for gaps
            competitor_analysis = await self.competitor_analyzer._arun(
                clerk_id=clerk_id,
                analysis_type="content_gap_analysis"
            )
            
            if not competitor_analysis.get("success"):
                return competitor_analysis
            
            # Extract gap analysis
            gap_analysis = competitor_analysis.get("analysis_data", {})
            
            # Identify specific gaps for the user
            user_gaps = self._analyze_user_content_gaps(user_content_summary, gap_analysis)
            
            return {
                "success": True,
                "content_gaps": user_gaps,
                "competitor_benchmarks": gap_analysis,
                "recommendations": self._generate_gap_filling_recommendations(user_gaps),
                "data_source": self.data_source
            }
            
        except Exception as e:
            logger.error(f"❌ Content gap analysis failed: {str(e)}")
            return {
                "success": False,
                "error": f"Content gap analysis failed: {str(e)}",
                "data_source": self.data_source
            }
    
    def _extract_key_insights(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key insights from competitor analysis"""
        
        if not analysis_result.get("success"):
            return {}
        
        analysis_data = analysis_result.get("analysis_data", {})
        
        insights = {
            "top_performing_content": [],
            "trending_topics": [],
            "engagement_patterns": {},
            "hashtag_strategies": [],
            "optimal_timing": {}
        }
        
        # Extract content performance insights
        if "content_performance" in analysis_data:
            content_perf = analysis_data["content_performance"]
            insights["top_performing_content"] = [
                {"type": content_type, "engagement": data.get("avg_engagement", 0)}
                for content_type, data in content_perf.items()
            ]
        
        # Extract trending hashtags
        if "trending_hashtags" in analysis_data:
            insights["trending_topics"] = list(analysis_data["trending_hashtags"].keys())[:10]
        
        # Extract engagement patterns
        if "engagement_analysis" in analysis_data:
            eng_analysis = analysis_data["engagement_analysis"]
            insights["engagement_patterns"] = {
                "best_platform": eng_analysis.get("platform_performance", {}),
                "optimal_timing": eng_analysis.get("optimal_posting_hours", {})
            }
        
        return insights
    
    def _generate_strategic_recommendations(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Generate strategic recommendations based on analysis"""
        
        recommendations = []
        
        if not analysis_result.get("success"):
            return ["Unable to generate recommendations due to analysis failure"]
        
        # Get recommendations from the analysis
        analysis_recommendations = analysis_result.get("recommendations", [])
        recommendations.extend(analysis_recommendations)
        
        # Add data source specific recommendations
        data_source = analysis_result.get("data_source", "mock")
        if data_source == "supabase":
            recommendations.append("✅ Using real-time competitor data for accurate insights")
            recommendations.append("🔄 Data is current and reflects latest market trends")
        else:
            recommendations.append("ℹ️ Using mock data - consider connecting to live data sources")
        
        return recommendations
    
    def _generate_content_recommendations(
        self,
        competitor_analysis: Dict[str, Any],
        hashtag_strategies: Dict[str, Any],
        content_goals: List[str],
        platforms: List[str]
    ) -> Dict[str, Any]:
        """Generate content recommendations based on analysis"""
        
        recommendations = {
            "content_types": [],
            "posting_schedule": {},
            "hashtag_strategies": {},
            "engagement_tactics": []
        }
        
        # Content type recommendations based on competitor performance
        if "top_performing_content" in competitor_analysis.get("insights", {}):
            top_content = competitor_analysis["insights"]["top_performing_content"]
            recommendations["content_types"] = [
                content["type"] for content in top_content[:3]
            ]
        
        # Platform-specific hashtag strategies
        for platform, strategy in hashtag_strategies.items():
            if strategy.get("success"):
                recommendations["hashtag_strategies"][platform] = strategy.get("recommended_hashtags", [])
        
        # Engagement tactics
        recommendations["engagement_tactics"] = [
            "Use trending hashtags from competitor analysis",
            "Post during optimal times identified in analysis",
            "Focus on high-performing content types",
            "Include clear calls-to-action in posts"
        ]
        
        return recommendations
    
    def _create_implementation_plan(self, content_recommendations: Dict[str, Any], platforms: List[str]) -> Dict[str, Any]:
        """Create implementation plan for content strategy"""
        
        return {
            "phase_1": {
                "duration": "Week 1-2",
                "tasks": [
                    "Set up content calendar",
                    "Create content templates",
                    "Establish hashtag strategy"
                ]
            },
            "phase_2": {
                "duration": "Week 3-4",
                "tasks": [
                    "Begin content creation",
                    "Monitor performance metrics",
                    "Adjust strategy based on results"
                ]
            },
            "phase_3": {
                "duration": "Week 5-8",
                "tasks": [
                    "Scale successful content types",
                    "Optimize posting schedule",
                    "Expand to additional platforms"
                ]
            }
        }
    
    def _create_executive_summary(
        self,
        competitor_analysis: Dict[str, Any],
        hashtag_strategies: Dict[str, Any],
        content_recommendations: Dict[str, Any]
    ) -> str:
        """Create executive summary of content strategy"""
        
        summary = f"""
Content Strategy Executive Summary

Competitor Analysis Status: {'✅ Complete' if competitor_analysis.get('success') else '❌ Failed'}
Data Source: {competitor_analysis.get('data_source', 'Unknown')}

Key Insights:
- Top performing content types: {', '.join(content_recommendations.get('content_types', [])[:3])}
- Platforms covered: {', '.join(hashtag_strategies.keys())}
- Recommended hashtag strategies: {len(content_recommendations.get('hashtag_strategies', {}))} platforms

Implementation Timeline: 8 weeks
Expected Outcomes: Improved engagement, increased reach, better content performance
        """
        
        return summary.strip()
    
    def _create_calendar_summary(self, calendar_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create summary of content calendar"""
        
        platform_counts = {}
        content_type_counts = {}
        
        for entry in calendar_entries:
            platform = entry.get("platform", "unknown")
            content_type = entry.get("content", {}).get("content_type", "unknown")
            
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
            content_type_counts[content_type] = content_type_counts.get(content_type, 0) + 1
        
        return {
            "total_posts": len(calendar_entries),
            "platform_distribution": platform_counts,
            "content_type_distribution": content_type_counts,
            "average_posts_per_day": len(calendar_entries) / 30 if calendar_entries else 0
        }
    
    def _get_optimal_posting_time(self, platform: str) -> str:
        """Get optimal posting time for platform"""
        
        platform_times = {
            "linkedin": "Tuesday-Thursday, 8-10 AM",
            "instagram": "Wednesday-Friday, 6-8 PM",
            "twitter": "Monday-Friday, 12-3 PM",
            "facebook": "Tuesday-Thursday, 1-4 PM",
            "youtube": "Tuesday-Thursday, 2-4 PM"
        }
        
        return platform_times.get(platform, "Tuesday-Thursday, 9-11 AM")
    
    def _calculate_priority(self, content_result: Dict[str, Any], day: int) -> str:
        """Calculate priority for content based on various factors"""
        
        # Simple priority calculation
        if day < 7:  # First week
            return "High"
        elif day < 21:  # Weeks 2-3
            return "Medium"
        else:  # Week 4+
            return "Low"
    
    def _analyze_user_content_gaps(self, user_content: str, competitor_gaps: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze gaps in user's content compared to competitors"""
        
        gaps = []
        
        # Analyze content types
        covered_topics = competitor_gaps.get("covered_topics", [])
        potential_gaps = competitor_gaps.get("potential_topic_gaps", [])
        
        for gap in potential_gaps:
            if gap not in covered_topics:
                gaps.append({
                    "type": "topic_gap",
                    "description": f"Missing content on {gap}",
                    "priority": "High",
                    "expected_impact": "High",
                    "implementation_effort": "Medium"
                })
        
        # Analyze posting times
        underutilized_times = competitor_gaps.get("underutilized_time_slots", [])
        if underutilized_times:
            gaps.append({
                "type": "timing_gap",
                "description": f"Underutilized posting times: {underutilized_times}",
                "priority": "Medium",
                "expected_impact": "Medium",
                "implementation_effort": "Low"
            })
        
        return gaps
    
    def _generate_gap_filling_recommendations(self, gaps: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations for filling content gaps"""
        
        recommendations = []
        
        for gap in gaps:
            if gap["type"] == "topic_gap":
                recommendations.append(f"Create content focusing on {gap['description']}")
            elif gap["type"] == "timing_gap":
                recommendations.append(f"Schedule posts during {gap['description']}")
        
        return recommendations
