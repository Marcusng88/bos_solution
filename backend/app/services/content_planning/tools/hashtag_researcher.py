"""
Hashtag Researcher Tool - Researches and optimizes hashtag strategies
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from collections import defaultdict
import json
import os

from ..config.settings import settings, INDUSTRY_HASHTAGS
from ..config.prompts import HASHTAG_RESEARCH_PROMPT


class HashtagResearchInput(BaseModel):
    """Input schema for hashtag research"""
    industry: str = Field(description="Target industry sector")
    content_type: str = Field(description="Type of content")
    platform: str = Field(description="Social media platform")
    target_audience: str = Field(description="Target audience description")
    custom_keywords: Optional[List[str]] = Field(description="Custom keywords to include", default=None)


class HashtagResearcher:
    """
    Tool for researching optimal hashtag strategies
    based on industry trends, platform best practices, and competitor usage.
    """
    
    def __init__(self):
        self._load_hashtag_data()
    
    def _load_hashtag_data(self):
        """Load hashtag performance data"""
        try:
            # Load from competitor dataset for trending data
            dataset_path = os.path.join(os.path.dirname(__file__), "..", "data", "mock_datasets", "competitors_dataset.json")
            with open(dataset_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.trending_data = data.get("trending_hashtags", {})
                self.performance_data = data.get("content_insights", {}).get("hashtag_performance", {})
        except (FileNotFoundError, json.JSONDecodeError):
            self.trending_data = {"technology": ["#AI", "#Innovation", "#TechTrends"]}
            self.performance_data = {}
    
    def _run(
        self,
        industry: str,
        content_type: str,
        platform: str,
        target_audience: str,
        custom_keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Research optimal hashtags based on inputs"""
        
        try:
            # Get base hashtags for industry
            industry_hashtags = INDUSTRY_HASHTAGS.get(industry, [])
            trending_hashtags = self.trending_data.get(industry, [])
            
            # Analyze hashtag performance
            hashtag_analysis = self._analyze_hashtag_performance(
                industry_hashtags + trending_hashtags
            )
            
            # Generate strategic hashtag recommendations
            recommendations = self._generate_hashtag_strategy(
                industry=industry,
                content_type=content_type,
                platform=platform,
                target_audience=target_audience,
                analysis_data=hashtag_analysis,
                custom_keywords=custom_keywords or []
            )
            
            # Get AI-enhanced recommendations
            ai_recommendations = self._get_ai_hashtag_insights(
                industry=industry,
                content_type=content_type,
                platform=platform,
                trending_data=str(self.trending_data)
            )
            
            return {
                "success": True,
                "industry": industry,
                "platform": platform,
                "content_type": content_type,
                "recommended_hashtags": recommendations,
                "hashtag_analysis": hashtag_analysis,
                "ai_insights": ai_recommendations,
                "strategy_summary": self._create_strategy_summary(recommendations),
                "timestamp": "2025-08-21T00:00:00Z"
            }
            
        except Exception as e:
            return {
                "error": f"Hashtag research failed: {str(e)}",
                "success": False
            }
    
    def _analyze_hashtag_performance(self, hashtags: List[str]) -> Dict[str, Any]:
        """Analyze hashtag performance metrics"""
        
        performance_analysis = {}
        
        for hashtag in hashtags:
            # Simulate performance metrics (in real implementation, this would query actual APIs)
            performance_analysis[hashtag] = {
                "estimated_reach": self._estimate_reach(hashtag),
                "competition_level": self._estimate_competition(hashtag),
                "trend_momentum": self._estimate_trend_momentum(hashtag),
                "engagement_potential": self._estimate_engagement_potential(hashtag)
            }
        
        # Categorize hashtags
        categorized = self._categorize_hashtags(performance_analysis)
        
        return {
            "individual_performance": performance_analysis,
            "categorized_hashtags": categorized,
            "performance_summary": self._summarize_performance(performance_analysis)
        }
    
    def _estimate_reach(self, hashtag: str) -> str:
        """Estimate reach potential of hashtag"""
        # Simplified estimation based on hashtag characteristics
        if len(hashtag) < 10 and any(word in hashtag.lower() for word in ['ai', 'tech', 'digital']):
            return "High"
        elif len(hashtag) < 15:
            return "Medium"
        else:
            return "Low"
    
    def _estimate_competition(self, hashtag: str) -> str:
        """Estimate competition level for hashtag"""
        # Simplified competition estimation
        if hashtag in ["#AI", "#Technology", "#Innovation", "#Business"]:
            return "High"
        elif len(hashtag) > 20:
            return "Low"
        else:
            return "Medium"
    
    def _estimate_trend_momentum(self, hashtag: str) -> str:
        """Estimate current trend momentum"""
        trending_keywords = ['ai', 'sustainability', 'remote', 'digital', 'innovation']
        if any(keyword in hashtag.lower() for keyword in trending_keywords):
            return "Rising"
        else:
            return "Stable"
    
    def _estimate_engagement_potential(self, hashtag: str) -> float:
        """Estimate engagement potential (0-10 scale)"""
        # Simplified scoring based on hashtag characteristics
        score = 5.0  # Base score
        
        if len(hashtag) < 15:
            score += 1.0  # Shorter hashtags tend to perform better
        
        if hashtag.startswith('#') and hashtag[1:].replace('_', '').replace('-', '').isalnum():
            score += 0.5  # Well-formed hashtags
        
        if any(word in hashtag.lower() for word in ['tip', 'how', 'guide', 'secret']):
            score += 1.0  # Educational content performs well
        
        return min(score, 10.0)
    
    def _categorize_hashtags(self, performance_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Categorize hashtags by type and performance"""
        
        categories = {
            "broad_reach": [],
            "niche_targeted": [],
            "trending": [],
            "branded": [],
            "content_specific": []
        }
        
        for hashtag, metrics in performance_data.items():
            reach = metrics.get("estimated_reach", "Medium")
            competition = metrics.get("competition_level", "Medium")
            trend = metrics.get("trend_momentum", "Stable")
            
            if reach == "High" and competition == "High":
                categories["broad_reach"].append(hashtag)
            elif reach == "Medium" and competition == "Low":
                categories["niche_targeted"].append(hashtag)
            elif trend == "Rising":
                categories["trending"].append(hashtag)
            elif len(hashtag) > 15:
                categories["content_specific"].append(hashtag)
            else:
                categories["niche_targeted"].append(hashtag)
        
        return categories
    
    def _summarize_performance(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create performance summary statistics"""
        
        if not performance_data:
            return {}
        
        engagement_scores = [metrics.get("engagement_potential", 5.0) for metrics in performance_data.values()]
        
        return {
            "total_hashtags_analyzed": len(performance_data),
            "avg_engagement_potential": round(sum(engagement_scores) / len(engagement_scores), 2),
            "high_potential_count": len([score for score in engagement_scores if score >= 7.0]),
            "trending_count": len([metrics for metrics in performance_data.values() if metrics.get("trend_momentum") == "Rising"])
        }
    
    def _generate_hashtag_strategy(
        self,
        industry: str,
        content_type: str,
        platform: str,
        target_audience: str,
        analysis_data: Dict[str, Any],
        custom_keywords: List[str]
    ) -> Dict[str, Any]:
        """Generate strategic hashtag recommendations"""
        
        categorized = analysis_data.get("categorized_hashtags", {})
        
        # Platform-specific optimal counts
        platform_limits = {
            "instagram": 12,
            "linkedin": 5,
            "twitter": 3,
            "facebook": 5,
            "tiktok": 8,
            "youtube": 15
        }
        
        optimal_count = platform_limits.get(platform, 8)
        
        # Strategic mix ratios
        strategy = {
            "primary_hashtags": [],
            "secondary_hashtags": [],
            "trending_hashtags": [],
            "niche_hashtags": [],
            "branded_hashtags": []
        }
        
        # Primary hashtags (40% - broad industry)
        primary_count = max(1, int(optimal_count * 0.4))
        strategy["primary_hashtags"] = categorized.get("broad_reach", [])[:primary_count]
        
        # Secondary hashtags (30% - niche targeted)
        secondary_count = max(1, int(optimal_count * 0.3))
        strategy["secondary_hashtags"] = categorized.get("niche_targeted", [])[:secondary_count]
        
        # Trending hashtags (20% - current trends)
        trending_count = max(1, int(optimal_count * 0.2))
        strategy["trending_hashtags"] = categorized.get("trending", [])[:trending_count]
        
        # Remaining for niche and branded
        remaining = optimal_count - len(strategy["primary_hashtags"]) - len(strategy["secondary_hashtags"]) - len(strategy["trending_hashtags"])
        strategy["niche_hashtags"] = categorized.get("content_specific", [])[:max(0, remaining - 1)]
        
        # Add custom branded hashtag if space
        if remaining > 0:
            branded_hashtag = f"#{industry.replace('_', '')}Content"
            strategy["branded_hashtags"] = [branded_hashtag]
        
        # Include custom keywords if provided
        if custom_keywords:
            custom_hashtags = [f"#{keyword.replace(' ', '').replace('_', '')}" for keyword in custom_keywords]
            strategy["custom_hashtags"] = custom_hashtags[:2]  # Limit to 2
        
        return strategy
    
    def _get_ai_hashtag_insights(
        self,
        industry: str,
        content_type: str,
        platform: str,
        trending_data: str
    ) -> str:
        """Get AI-generated hashtag insights"""
        
        prompt = HASHTAG_RESEARCH_PROMPT.format(
            industry=industry,
            content_type=content_type,
            platform=platform,
            trending_data=trending_data
        )
        
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            return f"AI insights unavailable: {str(e)}"
    
    def _create_strategy_summary(self, recommendations: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of the hashtag strategy"""
        
        all_hashtags = []
        for category, hashtags in recommendations.items():
            all_hashtags.extend(hashtags)
        
        return {
            "total_recommended_hashtags": len(all_hashtags),
            "strategy_breakdown": {
                category: len(hashtags) for category, hashtags in recommendations.items()
            },
            "complete_hashtag_list": all_hashtags,
            "strategy_focus": self._determine_strategy_focus(recommendations)
        }
    
    def _determine_strategy_focus(self, recommendations: Dict[str, Any]) -> str:
        """Determine the main focus of the hashtag strategy"""
        
        category_counts = {category: len(hashtags) for category, hashtags in recommendations.items()}
        
        if not category_counts:
            return "balanced"
        
        max_category = max(category_counts, key=category_counts.get)
        
        focus_map = {
            "primary_hashtags": "reach_focused",
            "secondary_hashtags": "engagement_focused",
            "trending_hashtags": "trend_focused",
            "niche_hashtags": "niche_focused",
            "branded_hashtags": "brand_focused"
        }
        
        return focus_map.get(max_category, "balanced")
    
    async def _arun(self, *args, **kwargs) -> Dict[str, Any]:
        """Async version of the tool"""
        return self._run(*args, **kwargs)


def optimize_hashtags_for_platform(
    hashtags: List[str],
    source_platform: str,
    target_platform: str
) -> List[str]:
    """
    Optimize hashtags when moving content between platforms
    """
    
    platform_limits = {
        "instagram": 12,
        "linkedin": 5,
        "twitter": 3,
        "facebook": 5,
        "tiktok": 8,
        "youtube": 15
    }
    
    target_limit = platform_limits.get(target_platform, 8)
    
    # Platform-specific filtering rules
    if target_platform == "linkedin":
        # LinkedIn prefers professional hashtags
        professional_keywords = ['business', 'professional', 'career', 'industry', 'leadership']
        filtered = [tag for tag in hashtags if any(keyword in tag.lower() for keyword in professional_keywords)]
        return filtered[:target_limit] if filtered else hashtags[:target_limit]
    
    elif target_platform == "twitter":
        # Twitter prefers shorter, more conversational hashtags
        return [tag for tag in hashtags if len(tag) <= 15][:target_limit]
    
    elif target_platform == "instagram":
        # Instagram allows more hashtags and variety
        return hashtags[:target_limit]
    
    else:
        return hashtags[:target_limit]


def generate_seasonal_hashtags(
    base_hashtags: List[str],
    season: str = "current"
) -> List[str]:
    """
    Generate seasonal variations of hashtags
    """
    
    seasonal_modifiers = {
        "spring": ["spring", "fresh", "new", "growth", "bloom"],
        "summer": ["summer", "hot", "vacation", "sunny", "beach"],
        "fall": ["fall", "autumn", "harvest", "cozy", "seasonal"],
        "winter": ["winter", "holiday", "warm", "festive", "year-end"]
    }
    
    if season == "current":
        # Determine current season (simplified)
        import datetime
        month = datetime.datetime.now().month
        if month in [3, 4, 5]:
            season = "spring"
        elif month in [6, 7, 8]:
            season = "summer"
        elif month in [9, 10, 11]:
            season = "fall"
        else:
            season = "winter"
    
    modifiers = seasonal_modifiers.get(season, [])
    seasonal_hashtags = []
    
    for hashtag in base_hashtags[:5]:  # Limit to avoid too many variations
        for modifier in modifiers[:2]:  # Use top 2 modifiers
            seasonal_tag = f"#{modifier.title()}{hashtag[1:]}"  # Remove # and add modifier
            seasonal_hashtags.append(seasonal_tag)
    
    return seasonal_hashtags
