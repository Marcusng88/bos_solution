"""
Competitor Analyzer Tool - Analyzes competitor content for strategic insights
"""

import json
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from collections import defaultdict
import statistics
from datetime import datetime, timedelta, timezone
import os
import logging

from ..config.settings import settings
from ..config.prompts import COMPETITOR_ANALYSIS_PROMPT, CONTENT_GAP_ANALYSIS_PROMPT

logger = logging.getLogger(__name__)

class CompetitorAnalysisInput(BaseModel):
    """Input schema for competitor analysis"""
    clerk_id: str = Field(description="Current user's Clerk ID")
    analysis_type: str = Field(description="Type of analysis to perform")
    time_period: str = Field(description="Time period for analysis", default="last_30_days")
    competitor_ids: Optional[List[str]] = Field(description="Specific competitor IDs", default=None)


class CompetitorAnalyzer:
    """
    Tool for analyzing competitor social media content to identify
    strategic opportunities and trends.
    """
    
    def __init__(self):
        # Initialize with mock data for fallback
        self._load_competitor_data()
        self.llm = None  # Initialize lazily
        self.supabase_client = None  # Initialize lazily
        
        # Data source tracking
        self.data_source = "mock"  # Track which data source is being used
        self.last_supabase_check = None
        
    def _get_supabase_client(self):
        """Lazy initialization of Supabase client"""
        if self.supabase_client is None:
            try:
                from ....core.supabase_client import SupabaseClient
                self.supabase_client = SupabaseClient()
                logger.info("✅ Supabase client initialized successfully")
            except Exception as e:
                logger.warning(f"⚠️ Could not initialize Supabase client: {e}")
                self.supabase_client = None
        return self.supabase_client
    
    def _load_competitor_data(self):
        """Load competitor data from mock dataset as fallback"""
        try:
            # Try to load from the file
            dataset_path = os.path.join(os.path.dirname(__file__), "..", "data", "mock_datasets", "competitors_dataset.json")
            with open(dataset_path, 'r', encoding='utf-8') as f:
                self.competitor_data = json.load(f)
                # Ensure all competitors have clerk_id
                self._ensure_clerk_id_in_mock_data()
                logger.info("📁 Mock competitor data loaded successfully")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            # Fallback to minimal data structure if file not found
            logger.warning(f"⚠️ Mock data file not found, using minimal fallback: {e}")
            self.competitor_data = {
                "competitors": [
                    {
                        "competitor_id": "comp_tech_001",
                        "company_name": "TechFlow Solutions",
                        "clerk_id": "user_123",  # Mock clerk ID
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
    
    def _ensure_clerk_id_in_mock_data(self):
        """Ensure all competitors in mock data have clerk_id field"""
        for competitor in self.competitor_data.get("competitors", []):
            if "clerk_id" not in competitor:
                competitor["clerk_id"] = "user_123"  # Default mock clerk ID
    
    async def _fetch_supabase_competitors(self, clerk_id: str) -> Optional[Dict[str, Any]]:
        """Fetch competitor data from Supabase based on Clerk ID"""
        try:
            client = self._get_supabase_client()
            if not client:
                logger.warning("⚠️ Supabase client not available")
                return None
            
            # Fetch competitors associated with the given clerk_id
            # Note: competitors.user_id references users.clerk_id via foreign key
            response = await client._make_request("GET", "competitors", params={"user_id": f"eq.{clerk_id}"})
            if response.status_code != 200:
                logger.warning(f"⚠️ Failed to fetch competitors from Supabase: {response.status_code}")
                return None
            
            competitors = response.json()
            if not competitors:
                logger.info(f"ℹ️ No competitors found for Clerk ID: {clerk_id}")
                return None
            
            logger.info(f"✅ Fetched {len(competitors)} competitors from Supabase for Clerk ID: {clerk_id}")
            return competitors
            
        except Exception as e:
            logger.error(f"❌ Error fetching competitors from Supabase: {e}")
            return None
    
    async def _fetch_supabase_monitoring_data(self, competitor_ids: List[str], time_period: str = "last_30_days") -> Optional[List[Dict[str, Any]]]:
        """Fetch monitoring data from Supabase"""
        try:
            client = self._get_supabase_client()
            if not client:
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
            
            # Build query parameters
            params = {
                "competitor_id": f"in.({','.join(competitor_ids)})",
                "detected_at": f"gte.{cutoff_date.isoformat()}"
            }
            
            # Fetch monitoring data
            response = await client._make_request("GET", "monitoring_data", params=params)
            if response.status_code != 200:
                logger.warning(f"⚠️ Failed to fetch monitoring data from Supabase: {response.status_code}")
                return None
            
            monitoring_data = response.json()
            logger.info(f"✅ Fetched {len(monitoring_data)} monitoring records from Supabase")
            return monitoring_data
            
        except Exception as e:
            logger.error(f"❌ Error fetching monitoring data from Supabase: {e}")
            return None
    
    def _transform_supabase_data(self, competitors: List[Dict], monitoring_data: List[Dict]) -> Dict[str, Any]:
        """Transform Supabase data to match expected AI agent format"""
        try:
            transformed_competitors = []
            
            for competitor in competitors:
                # Get monitoring data for this competitor
                competitor_monitoring = [
                    md for md in monitoring_data 
                    if md.get("competitor_id") == competitor.get("id")
                ]
                
                # Transform monitoring data to post format
                posts = []
                for md in competitor_monitoring:
                    # Calculate engagement rate
                    engagement_metrics = md.get("engagement_metrics", {})
                    view_count = engagement_metrics.get("view_count", 0)
                    like_count = engagement_metrics.get("like_count", 0)
                    comment_count = engagement_metrics.get("comment_count", 0)
                    share_count = engagement_metrics.get("share_count", 0)
                    
                    # Estimate engagement rate (if we had follower count)
                    engagement_rate = 0.0
                    if view_count > 0:
                        engagement_rate = ((like_count + comment_count + share_count) / view_count) * 100
                    
                    # Extract hashtags from content (basic extraction)
                    content_text = md.get("content_text", "")
                    hashtags = []
                    if content_text:
                        words = content_text.split()
                        hashtags = [word for word in words if word.startswith("#")]
                    
                    post = {
                        "post_id": md.get("post_id", ""),
                        "post_content": content_text,
                        "hashtags": hashtags,
                        "platform": md.get("platform", "unknown"),
                        "post_type": md.get("post_type", "unknown"),
                        "engagement_metrics": {
                            "likes": like_count,
                            "shares": share_count,
                            "comments": comment_count,
                            "views": view_count,
                            "engagement_rate": round(engagement_rate, 2)
                        },
                        "posting_time": md.get("posted_at", md.get("detected_at")),
                        "tone": "professional",  # Default tone
                        "call_to_action": "",  # Extract from content if possible
                        "target_audience": "general",  # Default audience
                        "content_length": len(content_text) if content_text else 0,
                        "emoji_count": sum(1 for char in content_text if char in "😀😃😄😁😆😅😂🤣😊😇🙂🙃😉😌😍🥰😘😗😙😚😋😛😝😜🤪🤨🧐🤓😎🤩🥳😏😒😞😔😟😕🙁☹️😣😖😫😩🥺😢😭😤😠😡🤬🤯😳🥵🥶😱😨😰😥😓🤗🤔🤭🤫🤥😶😐😑😯😦😧😮😲🥱😴🤤😪😵🤐🥴🤢🤮🤧😷🤒🤕🤑🤠💩👻💀☠️👽👾🤖😈👿👹👺") if content_text else 0,
                        "hashtag_count": len(hashtags)
                    }
                    posts.append(post)
                
                # Transform competitor data
                transformed_competitor = {
                    "competitor_id": competitor.get("id", ""),
                    "company_name": competitor.get("name", ""),
                    "industry_sector": competitor.get("industry_sector", competitor.get("industry", "unknown")),
                    "brand_description": competitor.get("description", ""),
                    "follower_count": 0,  # Not available in current schema
                    "engagement_rate": 0.0,  # Will be calculated from posts
                    "posting_frequency": "unknown",  # Can be calculated from posts
                    "posts": posts
                }
                
                # Debug logging to see what fields are available
                logger.debug(f"Competitor data fields: {list(competitor.keys())}")
                logger.debug(f"Competitor industry: {competitor.get('industry')}")
                logger.debug(f"Competitor industry_sector: {competitor.get('industry_sector')}")
                logger.debug(f"Transformed industry_sector: {transformed_competitor['industry_sector']}")
                
                # Calculate average engagement rate
                if posts:
                    avg_engagement = sum(post["engagement_metrics"]["engagement_rate"] for post in posts) / len(posts)
                    transformed_competitor["engagement_rate"] = round(avg_engagement, 2)
                
                transformed_competitors.append(transformed_competitor)
            
            # Generate trending hashtags from monitoring data
            all_hashtags = []
            for md in monitoring_data:
                content_text = md.get("content_text", "")
                if content_text:
                    words = content_text.split()
                    hashtags = [word for word in words if word.startswith("#")]
                    all_hashtags.extend(hashtags)
            
            # Count hashtag frequency
            hashtag_counts = defaultdict(int)
            for hashtag in all_hashtags:
                hashtag_counts[hashtag] += 1
            
            # Get top trending hashtags
            trending_hashtags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:20]
            trending_list = [hashtag for hashtag, count in trending_hashtags]
            
            # Group by industry (using competitor industry if available)
            industry_hashtags = defaultdict(list)
            for competitor in transformed_competitors:
                try:
                    # Get industry with better fallback logic
                    industry = competitor.get("industry_sector") or competitor.get("industry") or "unknown"
                    logger.debug(f"Competitor {competitor.get('name', 'unknown')} has industry: {industry}")
                    
                    # Ensure we have a valid industry string
                    if not industry or industry == "unknown":
                        industry = "general"
                        logger.warning(f"⚠️ Competitor {competitor.get('name', 'unknown')} has no industry, using 'general'")
                    
                    for post in competitor.get("posts", []):
                        industry_hashtags[industry].extend(post.get("hashtags", []))
                except Exception as e:
                    logger.warning(f"⚠️ Error processing competitor {competitor.get('name', 'unknown')}: {e}")
                    # Use default industry for this competitor
                    industry_hashtags["general"].extend(post.get("hashtags", []) if post.get("hashtags") else [])
                    continue
            
            # Remove duplicates and limit per industry
            for industry in industry_hashtags:
                industry_hashtags[industry] = list(set(industry_hashtags[industry]))[:10]
            
            transformed_data = {
                "competitors": transformed_competitors,
                "trending_hashtags": dict(industry_hashtags),
                "content_insights": {
                    "optimal_posting_times": {
                        "linkedin": ["Tuesday-Thursday, 8-10 AM", "Monday-Wednesday, 5-7 PM"],
                        "instagram": ["Wednesday-Friday, 6-8 PM", "Saturday-Sunday, 11 AM-1 PM"],
                        "twitter": ["Monday-Friday, 12-3 PM", "Tuesday-Thursday, 5-6 PM"],
                        "youtube": ["Tuesday-Thursday, 2-4 PM", "Friday-Sunday, 7-9 PM"]
                    },
                    "top_performing_content_types": [
                        {"type": "video", "avg_engagement": 5.2},
                        {"type": "educational", "avg_engagement": 4.8},
                        {"type": "product_announcement", "avg_engagement": 4.5},
                        {"type": "user_generated", "avg_engagement": 4.3}
                    ],
                    "hashtag_performance": {
                        "high_reach_low_competition": trending_list[:5],
                        "trending_emerging": trending_list[5:10],
                        "evergreen_high_engagement": trending_list[10:15]
                    }
                }
            }
            
            logger.info(f"✅ Successfully transformed {len(transformed_competitors)} competitors with {sum(len(c['posts']) for c in transformed_competitors)} posts")
            return transformed_data
            
        except Exception as e:
            logger.error(f"❌ Error transforming Supabase data: {e}")
            return None
    
    async def _get_supabase_analysis_data(self, clerk_id: str, competitor_ids: Optional[List[str]] = None, time_period: str = "last_30_days") -> Optional[Dict[str, Any]]:
        """Get analysis data from Supabase with fallback to mock data"""
        try:
            # Try to fetch from Supabase first
            competitors = await self._fetch_supabase_competitors(clerk_id)
            if not competitors:
                logger.info("ℹ️ No competitors found in Supabase, using mock data")
                return None
            
            # Get competitor IDs for monitoring data
            comp_ids = [comp.get("id") for comp in competitors if comp.get("id")]
            if not comp_ids:
                logger.warning("⚠️ No valid competitor IDs found")
                return None
            
            # Fetch monitoring data
            monitoring_data = await self._fetch_supabase_monitoring_data(comp_ids, time_period)
            if not monitoring_data:
                logger.info("ℹ️ No monitoring data found in Supabase, using mock data")
                return None
            
            # Transform data to expected format
            transformed_data = self._transform_supabase_data(competitors, monitoring_data)
            if transformed_data:
                self.data_source = "supabase"
                self.last_supabase_check = datetime.now()
                logger.info("✅ Successfully using Supabase data for analysis")
                return transformed_data
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting Supabase analysis data: {e}")
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
        clerk_id: str,
        competitor_ids: Optional[List[str]] = None,
        analysis_type: str = "trend_analysis",
        time_period: str = "last_30_days"
    ) -> Dict[str, Any]:
        """Analyze competitor data based on inputs"""
        
        try:
            # Try to get data from Supabase first
            supabase_data = await self._get_supabase_analysis_data(clerk_id, competitor_ids, time_period)
            
            if supabase_data:
                # Use Supabase data
                analysis_data = supabase_data
                self.data_source = "supabase"
                logger.info("🔍 Using Supabase data for competitor analysis")
            else:
                # Fallback to mock data
                analysis_data = self.competitor_data
                self.data_source = "mock"
                logger.info("🔍 Using mock data for competitor analysis (Supabase fallback)")
            
            # Filter competitors by industry
            relevant_competitors = self._filter_competitors(clerk_id, competitor_ids, analysis_data)
            
            if not relevant_competitors:
                return {
                    "error": f"No competitors found for Clerk ID: {clerk_id}",
                    "success": False,
                    "data_source": self.data_source
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
            ai_insights = await self._get_ai_insights(relevant_competitors, analysis_type, time_period)
            
            return {
                "success": True,
                "analysis_type": analysis_type,
                "clerk_id": clerk_id,
                "time_period": time_period,
                "competitor_count": len(relevant_competitors),
                "analysis_data": analysis_result,
                "ai_insights": ai_insights,
                "recommendations": self._generate_recommendations(analysis_result),
                "timestamp": datetime.now().isoformat(),
                "data_source": self.data_source,
                "data_freshness": self.last_supabase_check.isoformat() if self.last_supabase_check else None
            }
            
        except Exception as e:
            logger.error(f"❌ Analysis failed: {str(e)}")
            return {
                "error": f"Analysis failed: {str(e)}",
                "success": False,
                "data_source": self.data_source
            }
    
    def _filter_competitors(self, clerk_id: str, competitor_ids: Optional[List[str]], analysis_data: Dict[str, Any]) -> List[Dict]:
        """Filter competitors based on Clerk ID and optional IDs"""
        
        competitors = analysis_data.get("competitors", [])
        
        # Filter by user_id (which references users.clerk_id via foreign key)
        filtered = [comp for comp in competitors if comp.get("user_id") == clerk_id]
        
        # If no Clerk ID match, try to infer from company name or use all
        if not filtered and clerk_id != "unknown":
            # Try to find partial matches
            filtered = [comp for comp in competitors if clerk_id.lower() in comp.get("company_name", "").lower()]
            
            # If still no matches, use all competitors
            if not filtered:
                filtered = competitors
                logger.info(f"ℹ️ No Clerk ID match found for '{clerk_id}', using all {len(filtered)} competitors")
        
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
    
    async def _get_ai_insights(self, competitors: List[Dict], analysis_type: str, time_period: str) -> str:
        """Get AI-generated insights from competitor analysis"""
        
        # Prepare competitor data summary for AI analysis
        competitor_summary = self._prepare_competitor_summary(competitors)
        
        prompt = COMPETITOR_ANALYSIS_PROMPT.format(
            competitor_data=competitor_summary,
            analysis_type=analysis_type,
            time_period=time_period
        )
        
        try:
            llm = self._get_llm()
            if llm == "mock":
                return "AI analysis unavailable: Using mock mode"
            else:
                response = llm.invoke(prompt)
                return response.content if hasattr(response, 'content') else str(response)
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
        return await self._run(*args, **kwargs)
    
    async def run(self, input_data: CompetitorAnalysisInput) -> Dict[str, Any]:
        """Main entry point for competitor analysis tool"""
        return await self._run(
            clerk_id=input_data.clerk_id,
            competitor_ids=input_data.competitor_ids,
            analysis_type=input_data.analysis_type,
            time_period=input_data.time_period
        )
