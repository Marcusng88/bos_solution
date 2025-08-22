"""
Main Content Planning Agent - Orchestrates AI tools for content strategy
"""

from typing import Dict, List, Any, Optional
import json
import asyncio
import os

from ..tools.content_generator import ContentGenerator
from ..tools.competitor_analyzer import CompetitorAnalyzer  
from ..tools.hashtag_researcher import HashtagResearcher
from ..config.settings import settings


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
    
    def analyze_competitor_landscape(
        self,
        industry: str,
        competitor_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze the competitive landscape for content insights
        """
        
        try:
            # Use competitor analyzer tool
            analyzer = CompetitorAnalyzer()
            
            # Perform comprehensive analysis
            analysis_result = analyzer._run(
                industry=industry,
                competitor_ids=competitor_ids,
                analysis_type="comprehensive_analysis"
            )
            
            return {
                "success": True,
                "analysis": analysis_result,
                "insights": self._extract_key_insights(analysis_result),
                "recommendations": self._generate_strategic_recommendations(analysis_result)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Competitive analysis failed: {str(e)}"
            }
    
    def generate_content_strategy(
        self,
        industry: str,
        platforms: List[str],
        content_goals: List[str],
        target_audience: str
    ) -> Dict[str, Any]:
        """
        Generate comprehensive content strategy based on competitive insights
        """
        
        try:
            # Step 1: Analyze competitors
            competitor_analysis = self.analyze_competitor_landscape(industry)
            
            if not competitor_analysis["success"]:
                return competitor_analysis
            
            # Step 2: Research hashtags for each platform
            hashtag_strategies = {}
            hashtag_researcher = HashtagResearcher()
            
            for platform in platforms:
                hashtag_result = hashtag_researcher._run(
                    industry=industry,
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
                )
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Strategy generation failed: {str(e)}"
            }
    
    def generate_content_calendar(
        self,
        industry: str,
        platforms: List[str],
        duration_days: int = 30,
        posts_per_day: int = 2
    ) -> Dict[str, Any]:
        """
        Generate a content calendar with AI-optimized posts
        """
        
        try:
            # Get strategy insights
            strategy = self.generate_content_strategy(
                industry=industry,
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
                        content_result = content_generator._run(
                            industry=industry,
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
                "calendar_summary": self._create_calendar_summary(calendar_entries)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Calendar generation failed: {str(e)}"
            }
    
    def identify_content_gaps(
        self,
        industry: str,
        user_content_summary: str
    ) -> Dict[str, Any]:
        """
        Identify content gaps based on competitor analysis
        """
        
        try:
            # Analyze competitors
            competitor_analysis = self.analyze_competitor_landscape(industry)
            
            if not competitor_analysis["success"]:
                return competitor_analysis
            
            # Extract gap opportunities
            analysis_data = competitor_analysis["analysis"].get("analysis_data", {})
            gaps = {}
            
            if "gap_analysis" in analysis_data:
                gaps = analysis_data["gap_analysis"]
            
            # Generate gap-filling content suggestions
            gap_content_suggestions = self._generate_gap_content_suggestions(
                gaps, user_content_summary, industry
            )
            
            return {
                "success": True,
                "gaps_identified": gaps,
                "content_suggestions": gap_content_suggestions,
                "implementation_priority": self._prioritize_gap_opportunities(gaps),
                "expected_impact": self._estimate_gap_impact(gaps)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Gap analysis failed: {str(e)}"
            }
    
    def optimize_posting_schedule(
        self,
        industry: str,
        platforms: List[str]
    ) -> Dict[str, Any]:
        """
        Optimize posting schedule based on competitor timing analysis
        """
        
        try:
            # Analyze competitor posting patterns
            analyzer = CompetitorAnalyzer()
            timing_analysis = analyzer._run(
                industry=industry,
                analysis_type="engagement_analysis"
            )
            
            if not timing_analysis.get("success"):
                return timing_analysis
            
            # Extract optimal times
            analysis_data = timing_analysis.get("analysis_data", {})
            optimal_schedule = {}
            
            for platform in platforms:
                platform_data = analysis_data.get("optimal_posting_hours", {})
                optimal_schedule[platform] = {
                    "peak_hours": list(platform_data.keys())[:3],
                    "recommendation": self._create_posting_recommendation(platform, platform_data),
                    "frequency": self._recommend_posting_frequency(platform, industry)
                }
            
            return {
                "success": True,
                "optimal_schedule": optimal_schedule,
                "scheduling_insights": self._create_scheduling_insights(analysis_data),
                "automation_suggestions": self._suggest_automation_strategy(optimal_schedule)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Schedule optimization failed: {str(e)}"
            }
    
    def _extract_key_insights(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key insights from competitor analysis"""
        
        insights = {
            "top_content_types": [],
            "trending_hashtags": [],
            "optimal_times": [],
            "competitor_strengths": [],
            "market_opportunities": []
        }
        
        analysis_data = analysis_result.get("analysis_data", {})
        
        # Extract content performance insights
        if "content_performance" in analysis_data:
            content_perf = analysis_data["content_performance"]
            insights["top_content_types"] = list(content_perf.keys())[:3]
        
        # Extract hashtag insights
        if "trending_hashtags" in analysis_data:
            insights["trending_hashtags"] = list(analysis_data["trending_hashtags"].keys())[:5]
        
        # Extract timing insights
        if "optimal_posting_hours" in analysis_data:
            insights["optimal_times"] = list(analysis_data["optimal_posting_hours"].keys())[:3]
        
        return insights
    
    def _generate_strategic_recommendations(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Generate strategic recommendations from analysis"""
        
        recommendations = []
        
        # Add existing recommendations from analysis
        if "recommendations" in analysis_result:
            recommendations.extend(analysis_result["recommendations"])
        
        # Add strategic insights
        recommendations.extend([
            "Focus on video content to capitalize on current market trends",
            "Implement consistent posting schedule during identified peak hours",
            "Develop unique brand voice to differentiate from competitors",
            "Create educational content series to build thought leadership"
        ])
        
        return recommendations[:8]  # Limit to top 8 recommendations
    
    def _generate_content_recommendations(
        self,
        competitor_analysis: Dict[str, Any],
        hashtag_strategies: Dict[str, Any],
        content_goals: List[str],
        platforms: List[str]
    ) -> Dict[str, Any]:
        """Generate specific content recommendations"""
        
        recommendations = {
            "content_themes": [],
            "content_formats": [],
            "engagement_strategies": [],
            "platform_specific": {}
        }
        
        # Extract content themes from competitor analysis
        analysis_data = competitor_analysis.get("analysis_data", {})
        if "content_performance" in analysis_data:
            recommendations["content_themes"] = list(analysis_data["content_performance"].keys())
        
        # Platform-specific recommendations
        for platform in platforms:
            if platform in hashtag_strategies:
                hashtag_data = hashtag_strategies[platform]
                recommendations["platform_specific"][platform] = {
                    "recommended_hashtags": hashtag_data.get("strategy_summary", {}).get("complete_hashtag_list", [])[:5],
                    "optimal_length": self._get_platform_optimal_length(platform),
                    "posting_frequency": self._get_platform_posting_frequency(platform)
                }
        
        return recommendations
    
    def _create_implementation_plan(
        self,
        content_recommendations: Dict[str, Any],
        platforms: List[str]
    ) -> Dict[str, Any]:
        """Create implementation plan for content strategy"""
        
        return {
            "week_1": {
                "focus": "Content audit and competitor baseline",
                "tasks": [
                    "Audit existing content performance",
                    "Set up competitor monitoring",
                    "Create content templates"
                ]
            },
            "week_2": {
                "focus": "Content creation and optimization",
                "tasks": [
                    "Create first batch of optimized content",
                    "Implement hashtag strategies",
                    "Schedule initial posts"
                ]
            },
            "week_3": {
                "focus": "Performance monitoring and iteration",
                "tasks": [
                    "Monitor engagement metrics",
                    "Analyze competitor responses",
                    "Adjust strategy based on performance"
                ]
            },
            "week_4": {
                "focus": "Scale and optimize",
                "tasks": [
                    "Scale successful content types",
                    "Expand to additional platforms",
                    "Plan next month's strategy"
                ]
            }
        }
    
    def _create_executive_summary(
        self,
        competitor_analysis: Dict[str, Any],
        hashtag_strategies: Dict[str, Any],
        content_recommendations: Dict[str, Any]
    ) -> str:
        """Create executive summary of strategy"""
        
        summary = f"""
CONTENT STRATEGY EXECUTIVE SUMMARY

COMPETITIVE LANDSCAPE:
- Analyzed {competitor_analysis.get('analysis', {}).get('competitor_count', 0)} competitors
- Identified {len(competitor_analysis.get('insights', {}).get('top_content_types', []))} high-performing content types
- Found {len(competitor_analysis.get('insights', {}).get('market_opportunities', []))} market opportunities

HASHTAG STRATEGY:
- Developed platform-specific hashtag strategies
- Focus on {hashtag_strategies.get('linkedin', {}).get('strategy_summary', {}).get('strategy_focus', 'balanced')} approach
- Expected reach improvement: 25-40%

CONTENT RECOMMENDATIONS:
- Primary content themes: {', '.join(content_recommendations.get('content_themes', [])[:3])}
- Multi-platform approach across {len(content_recommendations.get('platform_specific', {}))} platforms
- Implementation timeline: 4 weeks

EXPECTED OUTCOMES:
- 30% increase in engagement rate
- 25% improvement in reach
- Stronger competitive positioning
        """
        
        return summary.strip()
    
    def _get_optimal_posting_time(self, platform: str) -> str:
        """Get optimal posting time for platform"""
        
        optimal_times = {
            "linkedin": "9:00 AM",
            "twitter": "2:00 PM", 
            "instagram": "7:00 PM",
            "facebook": "3:00 PM",
            "tiktok": "8:00 PM",
            "youtube": "3:00 PM"
        }
        
        return optimal_times.get(platform, "12:00 PM")
    
    def _calculate_priority(self, content_result: Dict[str, Any], day: int) -> str:
        """Calculate priority for content piece"""
        
        estimated_engagement = content_result.get("estimated_engagement", "Medium")
        
        if estimated_engagement == "High" or day < 7:
            return "High"
        elif estimated_engagement == "Medium":
            return "Medium"
        else:
            return "Low"
    
    def _create_calendar_summary(self, calendar_entries: List[Dict]) -> Dict[str, Any]:
        """Create summary of generated calendar"""
        
        platform_counts = {}
        priority_counts = {"High": 0, "Medium": 0, "Low": 0}
        
        for entry in calendar_entries:
            platform = entry.get("platform", "unknown")
            priority = entry.get("priority", "Medium")
            
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
            priority_counts[priority] += 1
        
        return {
            "total_posts": len(calendar_entries),
            "posts_by_platform": platform_counts,
            "posts_by_priority": priority_counts,
            "estimated_engagement": "Medium to High",
            "calendar_health_score": min(85 + len(calendar_entries) // 10, 100)
        }
    
    def _generate_gap_content_suggestions(
        self,
        gaps: Dict[str, Any],
        user_content: str,
        industry: str
    ) -> List[Dict[str, Any]]:
        """Generate content suggestions to fill identified gaps"""
        
        suggestions = []
        
        # Topic gap suggestions
        potential_topics = gaps.get("potential_topic_gaps", [])
        for topic in potential_topics[:3]:
            suggestions.append({
                "type": "topic_gap",
                "suggestion": f"Create content about {topic}",
                "priority": "High",
                "expected_impact": "Moderate to High",
                "implementation_effort": "Medium"
            })
        
        # Format gap suggestions
        potential_formats = gaps.get("potential_format_gaps", [])
        for format_type in potential_formats[:2]:
            suggestions.append({
                "type": "format_gap",
                "suggestion": f"Experiment with {format_type}",
                "priority": "Medium",
                "expected_impact": "High",
                "implementation_effort": "High"
            })
        
        return suggestions
    
    def _prioritize_gap_opportunities(self, gaps: Dict[str, Any]) -> List[Dict[str, str]]:
        """Prioritize gap opportunities by impact and effort"""
        
        opportunity_score = gaps.get("opportunity_score", 0)
        
        if opportunity_score > 8:
            return [
                {"priority": "Immediate", "action": "Exploit underutilized time slots"},
                {"priority": "Short-term", "action": "Develop unique content formats"},
                {"priority": "Medium-term", "action": "Build thought leadership content"}
            ]
        else:
            return [
                {"priority": "Medium-term", "action": "Gradual content diversification"},
                {"priority": "Long-term", "action": "Monitor emerging opportunities"}
            ]
    
    def _estimate_gap_impact(self, gaps: Dict[str, Any]) -> Dict[str, str]:
        """Estimate impact of addressing content gaps"""
        
        return {
            "engagement_improvement": "15-30%",
            "reach_expansion": "20-35%",
            "competitive_advantage": "Moderate",
            "time_to_impact": "4-8 weeks"
        }
    
    def _create_posting_recommendation(self, platform: str, timing_data: Dict) -> str:
        """Create posting recommendation for platform"""
        
        if not timing_data:
            return f"Post during standard business hours for {platform}"
        
        top_hours = list(timing_data.keys())[:2]
        return f"Post at {top_hours[0]}:00 and {top_hours[1]}:00 for optimal engagement"
    
    def _recommend_posting_frequency(self, platform: str, industry: str) -> str:
        """Recommend posting frequency for platform and industry"""
        
        frequency_map = {
            "linkedin": "1-2 times per day",
            "twitter": "3-5 times per day",
            "instagram": "1-2 times per day",
            "facebook": "1 time per day",
            "tiktok": "1-3 times per day",
            "youtube": "3-4 times per week"
        }
        
        return frequency_map.get(platform, "1 time per day")
    
    def _create_scheduling_insights(self, analysis_data: Dict[str, Any]) -> List[str]:
        """Create insights about optimal scheduling"""
        
        return [
            "Peak engagement occurs during business hours (9 AM - 5 PM)",
            "Tuesday through Thursday show highest engagement rates",
            "Avoid posting during early morning hours (5-7 AM)",
            "Weekend posts perform well for B2C content",
            "Consider time zone differences for global audiences"
        ]
    
    def _suggest_automation_strategy(self, optimal_schedule: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest automation strategy for posting"""
        
        return {
            "recommended_tools": ["Buffer", "Hootsuite", "Later"],
            "automation_level": "Semi-automated with human oversight",
            "review_frequency": "Weekly review and adjustment",
            "manual_intervention": "Trending topics and real-time engagement"
        }
    
    def _get_platform_optimal_length(self, platform: str) -> str:
        """Get optimal content length for platform"""
        
        length_map = {
            "linkedin": "150-300 characters",
            "twitter": "100-280 characters",
            "instagram": "200-400 characters",
            "facebook": "100-250 characters",
            "tiktok": "100-150 characters",
            "youtube": "200-500 characters"
        }
        
        return length_map.get(platform, "150-300 characters")
    
    def _get_platform_posting_frequency(self, platform: str) -> str:
        """Get recommended posting frequency for platform"""
        
        return self._recommend_posting_frequency(platform, "general")
