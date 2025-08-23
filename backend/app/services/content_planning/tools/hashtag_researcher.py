"""
Hashtag Researcher Tool - Researches and optimizes hashtag strategies
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from collections import defaultdict
import json
import os
import logging
from datetime import datetime, timezone, timedelta

from ..config.settings import settings, INDUSTRY_HASHTAGS
from ..config.prompts import HASHTAG_RESEARCH_PROMPT

logger = logging.getLogger(__name__)

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
        self.llm = None  # Initialize lazily
        self.supabase_client = None  # Initialize lazily
        
        # Data source tracking
        self.data_source = "mock"
        self.last_supabase_check = None
    
    def _get_supabase_client(self):
        """Lazy initialization of Supabase client"""
        if self.supabase_client is None:
            try:
                from ....core.supabase_client import SupabaseClient
                self.supabase_client = SupabaseClient()
                logger.info("✅ Supabase client initialized successfully for hashtag research")
            except Exception as e:
                logger.warning(f"⚠️ Could not initialize Supabase client: {e}")
                self.supabase_client = None
        return self.supabase_client
    
    def _load_hashtag_data(self):
        """Load hashtag performance data from mock dataset"""
        try:
            # Load from competitor dataset for trending data
            dataset_path = os.path.join(os.path.dirname(__file__), "..", "data", "mock_datasets", "competitors_dataset.json")
            with open(dataset_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.trending_data = data.get("trending_hashtags", {})
                self.performance_data = data.get("content_insights", {}).get("hashtag_performance", {})
                logger.info("📁 Mock hashtag data loaded successfully")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"⚠️ Mock hashtag data file not found, using minimal fallback: {e}")
            self.trending_data = {"technology": ["#AI", "#Innovation", "#TechTrends"]}
            self.performance_data = {}
    
    async def _fetch_supabase_hashtag_data(self, industry: str, time_period: str = "last_30_days") -> Optional[Dict[str, Any]]:
        """Fetch hashtag data from Supabase monitoring data"""
        try:
            client = self._get_supabase_client()
            if not client:
                logger.warning("⚠️ Supabase client not available for hashtag research")
                return None
            
            # Calculate time filter
            if time_period == "last_30_days":
                cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
            elif time_period == "last_7_days":
                cutoff_date = datetime.now(timezone.utc) - timedelta(days=7)
            elif time_period == "last_90_days":
                cutoff_date = datetime.now(timezone.utc) - timedelta(days=90)
            else:
                cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
            
            # First, get competitors in the industry
            competitors_response = await client._make_request("GET", "competitors", params={"industry": f"eq.{industry}"})
            if competitors_response.status_code != 200:
                logger.warning(f"⚠️ Failed to fetch competitors for industry {industry}: {competitors_response.status_code}")
                return None
            
            competitors = competitors_response.json()
            if not competitors:
                logger.info(f"ℹ️ No competitors found for industry {industry} in Supabase")
                return None
            
            competitor_ids = [comp.get("id") for comp in competitors if comp.get("id")]
            if not competitor_ids:
                logger.warning("⚠️ No valid competitor IDs found")
                return None
            
            # Fetch monitoring data for these competitors
            params = {
                "competitor_id": f"in.({','.join(competitor_ids)})",
                "detected_at": f"gte.{cutoff_date.isoformat()}"
            }
            
            monitoring_response = await client._make_request("GET", "monitoring_data", params=params)
            if monitoring_response.status_code != 200:
                logger.warning(f"⚠️ Failed to fetch monitoring data: {monitoring_response.status_code}")
                return None
            
            monitoring_data = monitoring_response.json()
            if not monitoring_data:
                logger.info("ℹ️ No monitoring data found for hashtag analysis")
                return None
            
            # Extract and analyze hashtags
            hashtag_analysis = self._analyze_supabase_hashtags(monitoring_data, industry)
            
            logger.info(f"✅ Successfully fetched hashtag data from Supabase: {len(monitoring_data)} posts analyzed")
            return hashtag_analysis
            
        except Exception as e:
            logger.error(f"❌ Error fetching hashtag data from Supabase: {e}")
            return None
    
    def _analyze_supabase_hashtags(self, monitoring_data: List[Dict], industry: str) -> Dict[str, Any]:
        """Analyze hashtags from Supabase monitoring data"""
        try:
            hashtag_frequency = defaultdict(int)
            hashtag_engagement = defaultdict(list)
            platform_hashtags = defaultdict(lambda: defaultdict(int))
            
            for md in monitoring_data:
                content_text = md.get("content_text", "")
                if not content_text:
                    continue
                
                platform = md.get("platform", "unknown")
                engagement_metrics = md.get("engagement_metrics", {})
                
                # Calculate engagement rate
                view_count = engagement_metrics.get("view_count", 0)
                like_count = engagement_metrics.get("like_count", 0)
                comment_count = engagement_metrics.get("comment_count", 0)
                share_count = engagement_metrics.get("share_count", 0)
                
                engagement_rate = 0.0
                if view_count > 0:
                    engagement_rate = ((like_count + comment_count + share_count) / view_count) * 100
                
                # Extract hashtags
                words = content_text.split()
                hashtags = [word for word in words if word.startswith("#")]
                
                for hashtag in hashtags:
                    hashtag_frequency[hashtag] += 1
                    hashtag_engagement[hashtag].append(engagement_rate)
                    platform_hashtags[platform][hashtag] += 1
            
            # Calculate hashtag performance metrics
            hashtag_performance = {}
            for hashtag, engagement_rates in hashtag_engagement.items():
                if engagement_rates:
                    avg_engagement = sum(engagement_rates) / len(engagement_rates)
                    hashtag_performance[hashtag] = {
                        "frequency": hashtag_frequency[hashtag],
                        "avg_engagement": round(avg_engagement, 2),
                        "reach_potential": hashtag_frequency[hashtag] * avg_engagement
                    }
            
            # Sort hashtags by different metrics
            by_frequency = sorted(hashtag_frequency.items(), key=lambda x: x[1], reverse=True)[:20]
            by_engagement = sorted(hashtag_performance.items(), key=lambda x: x[1]["avg_engagement"], reverse=True)[:15]
            by_potential = sorted(hashtag_performance.items(), key=lambda x: x[1]["reach_potential"], reverse=True)[:15]
            
            # Group by platform
            platform_trends = {}
            for platform, hashtags in platform_hashtags.items():
                platform_trends[platform] = dict(sorted(hashtags.items(), key=lambda x: x[1], reverse=True)[:10])
            
            return {
                "trending_hashtags": {industry: [hashtag for hashtag, count in by_frequency[:10]]},
                "hashtag_performance": {
                    "high_reach_low_competition": [hashtag for hashtag, _ in by_potential[:5]],
                    "trending_emerging": [hashtag for hashtag, _ in by_frequency[:5]],
                    "evergreen_high_engagement": [hashtag for hashtag, _ in by_engagement[:5]]
                },
                "platform_specific_trends": platform_trends,
                "total_hashtags_analyzed": len(hashtag_performance),
                "data_source": "supabase"
            }
            
        except Exception as e:
            logger.error(f"❌ Error analyzing Supabase hashtags: {e}")
            return None
    
    def _get_llm(self):
        """Lazy initialization of LLM"""
        if self.llm is None:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                self.llm = ChatGoogleGenerativeAI(
                    model=settings.model_name,
                    temperature=settings.temperature,
                    max_tokens=settings.max_tokens,
                    top_p=settings.top_p,
                    google_api_key=os.getenv("GOOGLE_API_KEY")
                )
            except Exception as e:
                print(f"Warning: Could not initialize Google AI LLM: {e}")
                self.llm = "mock"  # Use mock mode
        return self.llm

    async def _run(
        self,
        industry: str,
        content_type: str,
        platform: str,
        target_audience: str,
        custom_keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Research optimal hashtags based on inputs"""
        
        try:
            # Try to get data from Supabase first
            supabase_data = await self._fetch_supabase_hashtag_data(industry)
            
            if supabase_data:
                # Use Supabase data
                analysis_data = supabase_data
                self.data_source = "supabase"
                self.last_supabase_check = datetime.now()
                logger.info("🔍 Using Supabase data for hashtag research")
            else:
                # Fallback to mock data
                analysis_data = {
                    "trending_hashtags": self.trending_data,
                    "hashtag_performance": self.performance_data,
                    "platform_specific_trends": {},
                    "total_hashtags_analyzed": 0,
                    "data_source": "mock"
                }
                self.data_source = "mock"
                logger.info("🔍 Using mock data for hashtag research (Supabase fallback)")
            
            # Get base hashtags for industry
            industry_hashtags = INDUSTRY_HASHTAGS.get(industry, [])
            trending_hashtags = analysis_data.get("trending_hashtags", {}).get(industry, [])
            
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
                trending_data=str(analysis_data.get("trending_hashtags", {}))
            )
            
            return {
                "success": True,
                "industry": industry,
                "platform": platform,
                "content_type": content_type,
                "target_audience": target_audience,
                "recommended_hashtags": recommendations,
                "trending_hashtags": trending_hashtags,
                "industry_hashtags": industry_hashtags,
                "ai_insights": ai_recommendations,
                "performance_metrics": hashtag_analysis,
                "data_source": self.data_source,
                "data_freshness": self.last_supabase_check.isoformat() if self.last_supabase_check else None,
                "total_hashtags_analyzed": analysis_data.get("total_hashtags_analyzed", 0)
            }
            
        except Exception as e:
            logger.error(f"❌ Hashtag research failed: {str(e)}")
            return {
                "success": False,
                "error": f"Hashtag research failed: {str(e)}",
                "data_source": self.data_source
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
            llm = self._get_llm()
            if llm == "mock":
                return "AI insights unavailable: Using mock mode"
            else:
                response = llm.invoke(prompt)
                return response.content if hasattr(response, 'content') else str(response)
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
