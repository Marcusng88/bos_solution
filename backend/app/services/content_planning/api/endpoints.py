"""
Content Planning API Endpoints - FastAPI routes for AI content planning
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
import json
from datetime import datetime, timedelta

from ..agents.main_agent import ContentPlanningAgent
from ..tools.content_generator import ContentGenerator, generate_content_variations
from ..tools.competitor_analyzer import CompetitorAnalyzer
from ..tools.hashtag_researcher import HashtagResearcher
from ..config.settings import settings


# Request Models
class ContentGenerationRequest(BaseModel):
    """Request model for content generation"""
    industry: str = Field(..., description="Target industry sector")
    platform: str = Field(..., description="Social media platform")
    content_type: str = Field(..., description="Type of content to generate")
    tone: str = Field(default="professional", description="Tone of voice")
    target_audience: str = Field(..., description="Target audience description")
    custom_requirements: Optional[str] = Field(None, description="Custom requirements")
    generate_variations: bool = Field(default=False, description="Generate multiple variations")


class CompetitorAnalysisRequest(BaseModel):
    """Request model for competitor analysis"""
    industry: str = Field(..., description="Industry to analyze")
    competitor_ids: Optional[List[str]] = Field(None, description="Specific competitor IDs")
    analysis_type: str = Field(default="comprehensive_analysis", description="Type of analysis")
    time_period: str = Field(default="last_30_days", description="Analysis time period")


class HashtagResearchRequest(BaseModel):
    """Request model for hashtag research"""
    industry: str = Field(..., description="Target industry")
    content_type: str = Field(..., description="Content type")
    platform: str = Field(..., description="Social media platform")
    target_audience: str = Field(..., description="Target audience")
    custom_keywords: Optional[List[str]] = Field(None, description="Custom keywords")


class ContentStrategyRequest(BaseModel):
    """Request model for content strategy generation"""
    industry: str = Field(..., description="Target industry")
    platforms: List[str] = Field(..., description="Target platforms")
    content_goals: List[str] = Field(..., description="Content goals")
    target_audience: str = Field(..., description="Target audience")


class ContentCalendarRequest(BaseModel):
    """Request model for content calendar generation"""
    industry: str = Field(..., description="Target industry")
    platforms: List[str] = Field(..., description="Target platforms")
    duration_days: int = Field(default=30, description="Calendar duration in days")
    posts_per_day: int = Field(default=2, description="Posts per day")


# Response Models
class ContentGenerationResponse(BaseModel):
    """Response model for generated content"""
    success: bool
    content: Optional[Dict[str, Any]] = None
    variations: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None


class CompetitorAnalysisResponse(BaseModel):
    """Response model for competitor analysis"""
    success: bool
    analysis: Optional[Dict[str, Any]] = None
    insights: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[str]] = None
    error: Optional[str] = None


# Initialize router
content_planning_router = APIRouter(prefix="/content-planning", tags=["Content Planning"])

# Initialize agent lazily
agent = None

def get_agent():
    """Get or create the content planning agent"""
    global agent
    if agent is None:
        agent = ContentPlanningAgent()
    return agent


@content_planning_router.post("/generate-content", response_model=ContentGenerationResponse)
async def generate_content(request: ContentGenerationRequest) -> ContentGenerationResponse:
    """
    Generate AI-optimized social media content based on competitor insights
    """
    try:
        # First, get competitor insights for the industry
        competitor_analyzer = CompetitorAnalyzer()
        competitor_analysis = competitor_analyzer._run(
            industry=request.industry,
            analysis_type="trend_analysis"
        )
        
        competitor_insights = json.dumps(competitor_analysis.get("analysis_data", {}))
        
        # Generate content
        content_generator = ContentGenerator()
        content_result = content_generator._run(
            industry=request.industry,
            platform=request.platform,
            content_type=request.content_type,
            tone=request.tone,
            target_audience=request.target_audience,
            competitor_insights=competitor_insights,
            custom_requirements=request.custom_requirements
        )
        
        response_data = {
            "success": content_result.get("success", False),
            "content": content_result if content_result.get("success") else None,
            "error": content_result.get("error") if not content_result.get("success") else None
        }
        
        # Generate variations if requested
        if request.generate_variations and content_result.get("success"):
            variations = generate_content_variations(
                {
                    "industry": request.industry,
                    "platform": request.platform,
                    "content_type": request.content_type,
                    "target_audience": request.target_audience,
                    "competitor_insights": competitor_insights
                },
                variation_count=3
            )
            response_data["variations"] = variations
        
        return ContentGenerationResponse(**response_data)
        
    except Exception as e:
        return ContentGenerationResponse(
            success=False,
            error=f"Content generation failed: {str(e)}"
        )


@content_planning_router.post("/analyze-competitors", response_model=CompetitorAnalysisResponse)
async def analyze_competitors(request: CompetitorAnalysisRequest) -> CompetitorAnalysisResponse:
    """
    Analyze competitor content for strategic insights
    """
    try:
        competitor_analyzer = CompetitorAnalyzer()
        analysis_result = competitor_analyzer._run(
            industry=request.industry,
            competitor_ids=request.competitor_ids,
            analysis_type=request.analysis_type,
            time_period=request.time_period
        )
        
        if analysis_result.get("success"):
            # Extract insights using the main agent
            agent_instance = get_agent()
            insights = agent_instance._extract_key_insights(analysis_result)
            recommendations = agent_instance._generate_strategic_recommendations(analysis_result)
            
            return CompetitorAnalysisResponse(
                success=True,
                analysis=analysis_result.get("analysis_data"),
                insights=insights,
                recommendations=recommendations
            )
        else:
            return CompetitorAnalysisResponse(
                success=False,
                error=analysis_result.get("error", "Analysis failed")
            )
            
    except Exception as e:
        return CompetitorAnalysisResponse(
            success=False,
            error=f"Competitor analysis failed: {str(e)}"
        )


@content_planning_router.post("/research-hashtags")
async def research_hashtags(request: HashtagResearchRequest) -> Dict[str, Any]:
    """
    Research optimal hashtag strategies for content
    """
    try:
        hashtag_researcher = HashtagResearcher()
        hashtag_result = hashtag_researcher._run(
            industry=request.industry,
            content_type=request.content_type,
            platform=request.platform,
            target_audience=request.target_audience,
            custom_keywords=request.custom_keywords
        )
        
        return hashtag_result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Hashtag research failed: {str(e)}"
        }


@content_planning_router.post("/generate-strategy")
async def generate_content_strategy(request: ContentStrategyRequest) -> Dict[str, Any]:
    """
    Generate comprehensive content strategy based on competitive analysis
    """
    try:
        agent_instance = get_agent()
        strategy_result = agent_instance.generate_content_strategy(
            industry=request.industry,
            platforms=request.platforms,
            content_goals=request.content_goals,
            target_audience=request.target_audience
        )
        
        return strategy_result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Strategy generation failed: {str(e)}"
        }


@content_planning_router.post("/generate-calendar")
async def generate_content_calendar(request: ContentCalendarRequest) -> Dict[str, Any]:
    """
    Generate AI-optimized content calendar
    """
    try:
        agent_instance = get_agent()
        calendar_result = agent_instance.generate_content_calendar(
            industry=request.industry,
            platforms=request.platforms,
            duration_days=request.duration_days,
            posts_per_day=request.posts_per_day
        )
        
        return calendar_result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Calendar generation failed: {str(e)}"
        }


@content_planning_router.post("/identify-gaps")
async def identify_content_gaps(
    industry: str,
    user_content_summary: str
) -> Dict[str, Any]:
    """
    Identify content gaps based on competitor analysis
    """
    try:
        agent_instance = get_agent()
        gaps_result = agent_instance.identify_content_gaps(
            industry=industry,
            user_content_summary=user_content_summary
        )
        
        return gaps_result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Gap analysis failed: {str(e)}"
        }


@content_planning_router.post("/optimize-schedule")
async def optimize_posting_schedule(
    industry: str,
    platforms: List[str]
) -> Dict[str, Any]:
    """
    Optimize posting schedule based on competitor timing analysis
    """
    try:
        agent_instance = get_agent()
        schedule_result = agent_instance.optimize_posting_schedule(
            industry=industry,
            platforms=platforms
        )
        
        return schedule_result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Schedule optimization failed: {str(e)}"
        }


@content_planning_router.get("/dashboard-data")
async def get_dashboard_data(industry: str = "technology") -> Dict[str, Any]:
    """
    Get comprehensive dashboard data for the content planning interface
    """
    try:
        # Get competitor analysis
        agent_instance = get_agent()
        competitor_analysis = agent_instance.analyze_competitor_landscape(industry)
        
        # Get hashtag insights
        hashtag_researcher = HashtagResearcher()
        hashtag_insights = hashtag_researcher._run(
            industry=industry,
            content_type="promotional",
            platform="linkedin",
            target_audience="professionals"
        )
        
        # Get content gaps
        gaps_analysis = agent_instance.identify_content_gaps(
            industry=industry,
            user_content_summary="Standard promotional and educational content"
        )
        
        # Prepare dashboard summary
        dashboard_data = {
            "success": True,
            "summary": {
                "scheduled_posts": 24,
                "gap_opportunities": len(gaps_analysis.get("gaps_identified", {}).get("potential_topic_gaps", [])),
                "competitive_edge": "+23%",
                "threat_alerts": 3
            },
            "competitive_intelligence": {
                "new_opportunities": competitor_analysis.get("insights", {}).get("market_opportunities", [])[:3],
                "trending_hashtags": hashtag_insights.get("recommended_hashtags", {}).get("trending_hashtags", [])[:5]
            },
            "content_gaps": gaps_analysis.get("content_suggestions", [])[:5],
            "recent_activity": [
                {
                    "action": "Gap Identified",
                    "content": "Video content opportunity vs competitors",
                    "time": "1 hour ago",
                    "status": "opportunity"
                },
                {
                    "action": "AI Generated",
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
                "content_performance": competitor_analysis.get("analysis", {}).get("analysis_data", {}).get("content_performance", {}),
                "hashtag_effectiveness": hashtag_insights.get("hashtag_analysis", {})
            }
        }
        
        return dashboard_data
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Dashboard data generation failed: {str(e)}"
        }


@content_planning_router.get("/industry-insights/{industry}")
async def get_industry_insights(industry: str) -> Dict[str, Any]:
    """
    Get specific insights for an industry
    """
    try:
        # Analyze the specific industry
        agent_instance = get_agent()
        competitor_analysis = agent_instance.analyze_competitor_landscape(industry)
        
        if not competitor_analysis.get("success"):
            return competitor_analysis
        
        insights = {
            "industry": industry,
            "key_metrics": competitor_analysis.get("insights", {}),
            "content_trends": competitor_analysis.get("analysis", {}).get("analysis_data", {}).get("content_performance", {}),
            "optimal_posting_times": competitor_analysis.get("analysis", {}).get("analysis_data", {}).get("optimal_posting_hours", {}),
            "competitor_count": competitor_analysis.get("analysis", {}).get("competitor_count", 0),
            "recommendations": competitor_analysis.get("recommendations", [])
        }
        
        return {
            "success": True,
            "insights": insights
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Industry insights failed: {str(e)}"
        }


@content_planning_router.get("/supported-options")
async def get_supported_options() -> Dict[str, List[str]]:
    """
    Get supported industries, platforms, content types, and tones
    """
    return {
        "industries": settings.supported_industries,
        "platforms": settings.supported_platforms,
        "content_types": settings.content_types,
        "tones": settings.tone_options
    }
