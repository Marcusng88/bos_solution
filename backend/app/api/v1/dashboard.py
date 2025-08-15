"""
Dashboard API endpoints for AI-driven content planning
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import os
from ...services.ai_agents import ContentAnalysisAgent, DashboardMetricsGenerator

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# Initialize AI agent
def get_ai_agent():
    """Get AI agent instance"""
    api_key = os.getenv("GOOGLE_GENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GenAI API key not configured")
    return ContentAnalysisAgent(api_key)

def get_metrics_generator():
    """Get metrics generator instance"""
    return DashboardMetricsGenerator()

# Response models
class StatsCardData(BaseModel):
    value: str
    change: str

class StatsCardsResponse(BaseModel):
    scheduled_posts: StatsCardData
    gap_opportunities: StatsCardData
    competitive_edge: StatsCardData
    threat_alerts: StatsCardData

class AISuggestion(BaseModel):
    id: int
    type: str
    platform: str
    title: str
    content: str
    engagement: str
    confidence: int
    gap_type: str
    competitor_insight: str

class CompetitorGap(BaseModel):
    id: int
    gap_type: str
    competitor: str
    opportunity: str
    title: str
    content: str
    platform: str
    impact: str
    difficulty: str
    estimated_reach: str
    confidence: int
    competitor_example: str

class RecentActivity(BaseModel):
    action: str
    content: str
    time: str
    status: str

class AIAnalysisResponse(BaseModel):
    status: str
    analysis: Optional[str] = None
    message: Optional[str] = None

@router.get("/stats", response_model=StatsCardsResponse)
async def get_dashboard_stats():
    """Get dashboard statistics cards data"""
    try:
        metrics_gen = DashboardMetricsGenerator()
        stats_data = metrics_gen.get_stats_cards_data()
        return StatsCardsResponse(
            scheduled_posts=StatsCardData(**stats_data["scheduled_posts"]),
            gap_opportunities=StatsCardData(**stats_data["gap_opportunities"]),
            competitive_edge=StatsCardData(**stats_data["competitive_edge"]),
            threat_alerts=StatsCardData(**stats_data["threat_alerts"])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating stats: {str(e)}")

@router.get("/ai-suggestions", response_model=List[AISuggestion])
async def get_ai_suggestions():
    """Get AI-powered content suggestions"""
    try:
        metrics_gen = DashboardMetricsGenerator()
        suggestions = metrics_gen.get_ai_suggestions()
        return [AISuggestion(**suggestion) for suggestion in suggestions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating AI suggestions: {str(e)}")

@router.get("/competitor-gaps", response_model=List[CompetitorGap])
async def get_competitor_gaps():
    """Get competitor gap analysis data"""
    try:
        metrics_gen = DashboardMetricsGenerator()
        gaps = metrics_gen.get_competitor_gaps()
        return [CompetitorGap(**gap) for gap in gaps]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating competitor gaps: {str(e)}")

@router.get("/recent-activities", response_model=List[RecentActivity])
async def get_recent_activities():
    """Get recent activities data"""
    try:
        metrics_gen = DashboardMetricsGenerator()
        activities = metrics_gen.get_recent_activities()
        return [RecentActivity(**activity) for activity in activities]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recent activities: {str(e)}")

@router.post("/ai-analysis", response_model=AIAnalysisResponse)
async def get_ai_analysis(analysis_request: dict = {"analysis_type": "comprehensive"}):
    """Get comprehensive AI analysis of dashboard data"""
    try:
        api_key = os.getenv("GOOGLE_GENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="GenAI API key not configured")
        
        ai_agent = ContentAnalysisAgent(api_key)
        analysis_type = analysis_request.get("analysis_type", "comprehensive")
        result = ai_agent.analyze_dashboard_data(analysis_type)
        return AIAnalysisResponse(**result)
    except Exception as e:
        return AIAnalysisResponse(status="error", message=str(e))

@router.get("/competitive-intelligence")
async def get_competitive_intelligence():
    """Get competitive intelligence insights"""
    try:
        api_key = os.getenv("GOOGLE_GENAI_API_KEY")
        if not api_key:
            # Return mock data if GenAI not available
            return {
                "status": "success",
                "competitive_analysis": "Mock competitive analysis data",
                "performance_comparison": "Mock performance comparison data",
                "timestamp": "2025-08-16T10:00:00Z"
            }
        
        ai_agent = ContentAnalysisAgent(api_key)
        # Use specific tools for competitive analysis
        competitor_analysis = ai_agent._analyze_competitor_content("")
        performance_analysis = ai_agent._analyze_performance_metrics("")
        
        return {
            "status": "success",
            "competitive_analysis": competitor_analysis,
            "performance_comparison": performance_analysis,
            "timestamp": "2025-08-16T10:00:00Z"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": "2025-08-16T10:00:00Z"
        }

@router.get("/content-opportunities")
async def get_content_opportunities(ai_agent: ContentAnalysisAgent = Depends(get_ai_agent)):
    """Get content opportunities based on gaps and trends"""
    try:
        gaps_analysis = ai_agent._identify_content_gaps("")
        trends_analysis = ai_agent._analyze_trending_topics("")
        
        return {
            "status": "success",
            "content_gaps": gaps_analysis,
            "trending_opportunities": trends_analysis,
            "timestamp": "2025-08-16T10:00:00Z"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting content opportunities: {str(e)}")

@router.get("/engagement-forecast")
async def get_engagement_forecast(ai_agent: ContentAnalysisAgent = Depends(get_ai_agent)):
    """Get engagement predictions and forecasts"""
    try:
        calendar_analysis = ai_agent._review_content_calendar("")
        engagement_prediction = ai_agent._calculate_engagement_prediction("")
        
        return {
            "status": "success",
            "calendar_insights": calendar_analysis,
            "engagement_predictions": engagement_prediction,
            "timestamp": "2025-08-16T10:00:00Z"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating engagement forecast: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Dashboard API",
        "timestamp": "2025-08-16T10:00:00Z",
        "version": "1.0.0"
    }
