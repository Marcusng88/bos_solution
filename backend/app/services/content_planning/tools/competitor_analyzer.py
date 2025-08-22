"""
Competitor Analyzer Tool - Analyzes competitor content for strategic insights
"""

import json
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from collections import defaultdict
import statistics
from datetime import datetime, timedelta
import os

from ..config.settings import settings
from ..config.prompts import COMPETITOR_ANALYSIS_PROMPT, CONTENT_GAP_ANALYSIS_PROMPT


class CompetitorAnalysisInput(BaseModel):
    """Input schema for competitor analysis"""
    industry: str = Field(description="Industry sector to analyze")
    competitor_ids: Optional[List[str]] = Field(description="Specific competitor IDs", default=None)
    analysis_type: str = Field(description="Type of analysis to perform")
    time_period: str = Field(description="Time period for analysis", default="last_30_days")


class CompetitorAnalyzer:
    """
    Tool for analyzing competitor social media content to identify
    strategic opportunities and trends.
    """
    
    def __init__(self):
        # Initialize with mock data for now
        self._load_competitor_data()
    
    def _load_competitor_data(self):
        """Load competitor data from mock dataset"""
        try:
            # Try to load from the file
            dataset_path = os.path.join(os.path.dirname(__file__), "..", "data", "mock_datasets", "competitors_dataset.json")
            with open(dataset_path, 'r', encoding='utf-8') as f:
                self.competitor_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Fallback to minimal data structure if file not found
            self.competitor_data = {
                "competitors": [
                    {
                        "competitor_id": "comp_tech_001",
                        "company_name": "TechFlow Solutions",
                        "industry_sector": "technology",
                        "posts": [
                            {
                                "post_content": "AI-powered automation increases productivity by 80%",
                                "hashtags": ["#AI", "#Automation", "#Productivity"],
                                "platform": "linkedin",
                                "engagement_metrics": {"engagement_rate": 4.2}
                            }
                        ]
                    }
                ],
                "trending_hashtags": {"technology": ["#AI", "#Innovation", "#TechTrends"]},
                "content_insights": {}
            }
    
    def _run(
        self,
        industry: str,
        competitor_ids: Optional[List[str]] = None,
        analysis_type: str = "trend_analysis",
        time_period: str = "last_30_days"
    ) -> Dict[str, Any]:
        """Analyze competitor data based on inputs"""
        
        try:
            # Filter competitors by industry
            relevant_competitors = self._filter_competitors(industry, competitor_ids)
            
            if not relevant_competitors:
                return {
                    "error": f"No competitors found for industry: {industry}",
                    "success": False
                }
            
            # Perform analysis based on type
            if analysis_type == "trend_analysis":
                analysis_result = self._perform_trend_analysis(relevant_competitors)
            elif analysis_type == "content_gap_analysis":
                analysis_result = self._perform_gap_analysis(relevant_competitors)
            elif analysis_type == "hashtag_analysis":
                analysis_result = self._perform_hashtag_analysis(relevant_competitors)
            elif analysis_type == "engagement_analysis":
                analysis_result = self._perform_engagement_analysis(relevant_competitors)
            else:
                analysis_result = self._perform_comprehensive_analysis(relevant_competitors)
            
            # Enhance with AI insights
            ai_insights = self._get_ai_insights(relevant_competitors, analysis_type, time_period)
            
            return {
                "success": True,
                "analysis_type": analysis_type,
                "industry": industry,
                "time_period": time_period,
                "competitor_count": len(relevant_competitors),
                "analysis_data": analysis_result,
                "ai_insights": ai_insights,
                "recommendations": self._generate_recommendations(analysis_result),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "error": f"Analysis failed: {str(e)}",
                "success": False
            }
    
    def _filter_competitors(self, industry: str, competitor_ids: Optional[List[str]]) -> List[Dict]:
        """Filter competitors based on industry and optional IDs"""
        
        competitors = self.competitor_data.get("competitors", [])
        
        # Filter by industry
        filtered = [comp for comp in competitors if comp.get("industry_sector") == industry]
        
        # Further filter by specific IDs if provided
        if competitor_ids:
            filtered = [comp for comp in filtered if comp.get("competitor_id") in competitor_ids]
        
        return filtered
    
    def _perform_trend_analysis(self, competitors: List[Dict]) -> Dict[str, Any]:
        """Analyze content trends across competitors"""
        
        content_types = defaultdict(list)
        tones = defaultdict(int)
        posting_times = defaultdict(int)
        hashtag_usage = defaultdict(int)
        
        for competitor in competitors:
            for post in competitor.get("posts", []):
                # Content type analysis
                content_type = post.get("post_type", "unknown")
                content_types[content_type].append(post.get("engagement_metrics", {}).get("engagement_rate", 0))
                
                # Tone analysis
                tone = post.get("tone", "unknown")
                tones[tone] += 1
                
                # Posting time analysis
                posting_time = post.get("posting_time", "")
                if posting_time:
                    hour = datetime.fromisoformat(posting_time.replace('Z', '+00:00')).hour
                    posting_times[hour] += 1
                
                # Hashtag analysis
                for hashtag in post.get("hashtags", []):
                    hashtag_usage[hashtag] += 1
        
        # Calculate averages and trends
        content_performance = {}
        for content_type, engagement_rates in content_types.items():
            if engagement_rates:
                content_performance[content_type] = {
                    "avg_engagement": round(statistics.mean(engagement_rates), 2),
                    "post_count": len(engagement_rates),
                    "max_engagement": max(engagement_rates),
                    "min_engagement": min(engagement_rates)
                }
        
        return {
            "content_performance": content_performance,
            "popular_tones": dict(sorted(tones.items(), key=lambda x: x[1], reverse=True)[:5]),
            "optimal_posting_hours": dict(sorted(posting_times.items(), key=lambda x: x[1], reverse=True)[:5]),
            "trending_hashtags": dict(sorted(hashtag_usage.items(), key=lambda x: x[1], reverse=True)[:15])
        }
    
    def _perform_gap_analysis(self, competitors: List[Dict]) -> Dict[str, Any]:
        """Identify content gaps and opportunities"""
        
        competitor_topics = set()
        competitor_formats = set()
        underrepresented_times = defaultdict(int)
        
        for competitor in competitors:
            for post in competitor.get("posts", []):
                # Extract topics from content (simplified)
                content = post.get("post_content", "").lower()
                if "product" in content or "launch" in content:
                    competitor_topics.add("product_launches")
                if "tip" in content or "how to" in content:
                    competitor_topics.add("educational_tips")
                if "behind" in content or "team" in content:
                    competitor_topics.add("behind_the_scenes")
                
                competitor_formats.add(post.get("post_type", "unknown"))
                
                # Time gap analysis
                posting_time = post.get("posting_time", "")
                if posting_time:
                    hour = datetime.fromisoformat(posting_time.replace('Z', '+00:00')).hour
                    underrepresented_times[hour] += 1
        
        # Identify gaps (hours with fewer posts)
        all_hours = set(range(24))
        low_activity_hours = []
        avg_posts_per_hour = sum(underrepresented_times.values()) / 24 if underrepresented_times else 0
        
        for hour in all_hours:
            if underrepresented_times.get(hour, 0) < avg_posts_per_hour * 0.5:
                low_activity_hours.append(hour)
        
        return {
            "covered_topics": list(competitor_topics),
            "covered_formats": list(competitor_formats),
            "potential_topic_gaps": [
                "user_testimonials", "industry_news_commentary", "seasonal_content",
                "community_highlights", "expert_interviews", "trend_predictions"
            ],
            "potential_format_gaps": [
                "video_tutorials", "infographics", "polls", "stories", "live_streams"
            ],
            "underutilized_time_slots": low_activity_hours,
            "opportunity_score": len(low_activity_hours) + (6 - len(competitor_topics))
        }
    
    def _perform_hashtag_analysis(self, competitors: List[Dict]) -> Dict[str, Any]:
        """Analyze hashtag usage and performance"""
        
        hashtag_performance = defaultdict(list)
        hashtag_frequency = defaultdict(int)
        
        for competitor in competitors:
            for post in competitor.get("posts", []):
                engagement_rate = post.get("engagement_metrics", {}).get("engagement_rate", 0)
                
                for hashtag in post.get("hashtags", []):
                    hashtag_frequency[hashtag] += 1
                    hashtag_performance[hashtag].append(engagement_rate)
        
        # Calculate hashtag effectiveness
        hashtag_stats = {}
        for hashtag, engagement_rates in hashtag_performance.items():
            if engagement_rates:
                hashtag_stats[hashtag] = {
                    "avg_engagement": round(statistics.mean(engagement_rates), 2),
                    "usage_frequency": hashtag_frequency[hashtag],
                    "reach_potential": hashtag_frequency[hashtag] * statistics.mean(engagement_rates)
                }
        
        # Sort by different metrics
        by_engagement = sorted(hashtag_stats.items(), key=lambda x: x[1]["avg_engagement"], reverse=True)[:10]
        by_frequency = sorted(hashtag_stats.items(), key=lambda x: x[1]["usage_frequency"], reverse=True)[:10]
        by_potential = sorted(hashtag_stats.items(), key=lambda x: x[1]["reach_potential"], reverse=True)[:10]
        
        return {
            "top_performing_hashtags": dict(by_engagement),
            "most_used_hashtags": dict(by_frequency),
            "highest_potential_hashtags": dict(by_potential),
            "total_unique_hashtags": len(hashtag_stats),
            "avg_hashtags_per_post": round(sum(hashtag_frequency.values()) / max(len(competitors), 1), 1)
        }
    
    def _perform_engagement_analysis(self, competitors: List[Dict]) -> Dict[str, Any]:
        """Analyze engagement patterns and drivers"""
        
        engagement_by_platform = defaultdict(list)
        engagement_by_time = defaultdict(list)
        engagement_by_length = defaultdict(list)
        
        for competitor in competitors:
            for post in competitor.get("posts", []):
                engagement_rate = post.get("engagement_metrics", {}).get("engagement_rate", 0)
                platform = post.get("platform", "unknown")
                content_length = post.get("content_length", 0)
                
                engagement_by_platform[platform].append(engagement_rate)
                
                # Time analysis
                posting_time = post.get("posting_time", "")
                if posting_time:
                    hour = datetime.fromisoformat(posting_time.replace('Z', '+00:00')).hour
                    engagement_by_time[hour].append(engagement_rate)
                
                # Length analysis
                length_category = "short" if content_length < 100 else "medium" if content_length < 300 else "long"
                engagement_by_length[length_category].append(engagement_rate)
        
        # Calculate averages
        platform_performance = {}
        for platform, rates in engagement_by_platform.items():
            if rates:
                platform_performance[platform] = round(statistics.mean(rates), 2)
        
        time_performance = {}
        for hour, rates in engagement_by_time.items():
            if rates:
                time_performance[hour] = round(statistics.mean(rates), 2)
        
        length_performance = {}
        for length_cat, rates in engagement_by_length.items():
            if rates:
                length_performance[length_cat] = round(statistics.mean(rates), 2)
        
        return {
            "platform_performance": platform_performance,
            "optimal_posting_hours": dict(sorted(time_performance.items(), key=lambda x: x[1], reverse=True)[:5]),
            "content_length_performance": length_performance,
            "engagement_insights": {
                "best_platform": max(platform_performance.items(), key=lambda x: x[1])[0] if platform_performance else "N/A",
                "best_time": max(time_performance.items(), key=lambda x: x[1])[0] if time_performance else "N/A",
                "optimal_length": max(length_performance.items(), key=lambda x: x[1])[0] if length_performance else "N/A"
            }
        }
    
    def _perform_comprehensive_analysis(self, competitors: List[Dict]) -> Dict[str, Any]:
        """Perform comprehensive analysis combining all methods"""
        
        return {
            "trend_analysis": self._perform_trend_analysis(competitors),
            "gap_analysis": self._perform_gap_analysis(competitors),
            "hashtag_analysis": self._perform_hashtag_analysis(competitors),
            "engagement_analysis": self._perform_engagement_analysis(competitors)
        }
    
    def _get_ai_insights(self, competitors: List[Dict], analysis_type: str, time_period: str) -> str:
        """Get AI-generated insights from competitor analysis"""
        
        # Prepare competitor data summary for AI analysis
        competitor_summary = self._prepare_competitor_summary(competitors)
        
        prompt = COMPETITOR_ANALYSIS_PROMPT.format(
            industry=competitors[0].get("industry_sector", "unknown") if competitors else "unknown",
            competitor_data=competitor_summary,
            analysis_type=analysis_type,
            time_period=time_period
        )
        
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            return f"AI analysis unavailable: {str(e)}"
    
    def _prepare_competitor_summary(self, competitors: List[Dict]) -> str:
        """Prepare a summary of competitor data for AI analysis"""
        
        summary_parts = []
        
        for competitor in competitors[:3]:  # Limit to top 3 for brevity
            comp_summary = f"""
Company: {competitor.get('company_name', 'Unknown')}
Followers: {competitor.get('follower_count', 0):,}
Engagement Rate: {competitor.get('engagement_rate', 0)}%
Posting Frequency: {competitor.get('posting_frequency', 'Unknown')}

Recent Posts:"""
            
            for post in competitor.get("posts", [])[:2]:  # Latest 2 posts
                comp_summary += f"""
- Content: {post.get('post_content', '')[:150]}...
- Platform: {post.get('platform', 'Unknown')}
- Engagement: {post.get('engagement_metrics', {}).get('engagement_rate', 0)}%
- Hashtags: {', '.join(post.get('hashtags', [])[:5])}
"""
            
            summary_parts.append(comp_summary)
        
        return "\n\n".join(summary_parts)
    
    def _generate_recommendations(self, analysis_data: Dict[str, Any]) -> List[str]:
        """Generate strategic recommendations based on analysis"""
        
        recommendations = []
        
        # Content performance recommendations
        if "content_performance" in analysis_data:
            best_content_type = max(
                analysis_data["content_performance"].items(),
                key=lambda x: x[1].get("avg_engagement", 0)
            )[0] if analysis_data["content_performance"] else None
            
            if best_content_type:
                recommendations.append(
                    f"Focus on {best_content_type.replace('_', ' ')} content - it shows the highest engagement rates"
                )
        
        # Hashtag recommendations
        if "trending_hashtags" in analysis_data:
            top_hashtags = list(analysis_data["trending_hashtags"].keys())[:3]
            if top_hashtags:
                recommendations.append(
                    f"Incorporate trending hashtags: {', '.join(top_hashtags)}"
                )
        
        # Timing recommendations
        if "optimal_posting_hours" in analysis_data:
            best_hours = list(analysis_data["optimal_posting_hours"].keys())[:2]
            if best_hours:
                recommendations.append(
                    f"Post during peak hours: {', '.join([f'{h}:00' for h in best_hours])}"
                )
        
        # Gap opportunities
        if "opportunity_score" in analysis_data and analysis_data["opportunity_score"] > 5:
            recommendations.append(
                "High opportunity score detected - consider exploring underutilized content areas"
            )
        
        return recommendations
    
    async def _arun(self, *args, **kwargs) -> Dict[str, Any]:
        """Async version of the tool"""
        return self._run(*args, **kwargs)
