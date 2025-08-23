"""
Content Planning endpoints for AI content planning and strategy
Follows the same pattern as other endpoints in the app
"""

from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import List, Optional
import logging

from app.services.content_planning.core_service import ContentPlanningService
from app.services.content_planning.models import (
    ContentGenerationRequest, ContentGenerationResponse,
    CompetitorAnalysisRequest, CompetitorAnalysisResponse,
    HashtagResearchRequest, HashtagResearchResponse,
    ContentStrategyRequest, ContentStrategyResponse,
    ContentCalendarRequest, ContentCalendarResponse,
    ContentGapsRequest, ContentGapsResponse,
    ScheduleOptimizationRequest, ScheduleOptimizationResponse,
    DashboardDataResponse, IndustryInsightsResponse, SupportedOptionsResponse
)
from app.core.supabase_client import supabase_client

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize content planning service
content_planning_service = ContentPlanningService()


@router.post("/generate-content", response_model=ContentGenerationResponse)
async def generate_content(request: ContentGenerationRequest) -> ContentGenerationResponse:
    """
    Generate AI-optimized social media content based on competitor insights
    """
    try:
        logger.info(f"📝 Content generation request for {request.platform} in {request.industry}")
        
        result = await content_planning_service.generate_content(
            industry=request.industry,
            platform=request.platform,
            content_type=request.content_type,
            tone=request.tone,
            target_audience=request.target_audience,
            custom_requirements=request.custom_requirements,
            generate_variations=request.generate_variations
        )
        
        return ContentGenerationResponse(**result)
        
    except Exception as e:
        logger.error(f"❌ Content generation endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {str(e)}"
        )


@router.post("/save-content-suggestion")
async def save_content_suggestion(
    request: dict
):
    """
    Save generated content suggestion to ai_content_suggestions table
    """
    try:
        user_id = request.get("user_id")
        suggested_content = request.get("suggested_content")
        platform = request.get("platform")
        industry = request.get("industry")
        content_type = request.get("content_type")
        tone = request.get("tone")
        target_audience = request.get("target_audience")
        hashtags = request.get("hashtags", [])
        custom_requirements = request.get("custom_requirements")
        
        if not all([user_id, suggested_content, platform, industry, content_type, tone, target_audience]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required parameters"
            )
        
        # Validate and clean data
        if not isinstance(hashtags, list):
            hashtags = [hashtags] if hashtags else []
        
        if not isinstance(platform, str):
            platform = str(platform)
        
        # Ensure platform is not empty
        if not platform.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Platform cannot be empty"
            )
        
        logger.info(f"💾 Saving content suggestion for user {user_id}")
        logger.info(f"📝 Platform: {platform}, Industry: {industry}, Content Type: {content_type}")
        
        supabase = supabase_client
        
        # First, verify that the user exists
        logger.info(f"🔍 Verifying user exists: {user_id}")
        user_check_response = await supabase._make_request(
            "GET",
            "users",
            params={"clerk_id": f"eq.{user_id}"}
        )
        
        if user_check_response.status_code != 200 or not user_check_response.json():
            logger.error(f"❌ User not found: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not found"
            )
        
        logger.info(f"✅ User verified: {user_id}")
        
        # First, create a user_post record
        user_post_data = {
            "user_id": user_id,
            "content_text": suggested_content,
            "hashtags": hashtags,
            "is_ai_generated": True,
            "ai_prompt": f"Generate {content_type} content for {platform} in {industry} industry with {tone} tone for {target_audience}",
            "ai_model_used": "content_planning_agent",
            "target_platforms": [platform],
            "post_status": "ai_suggested",
            "competitor_sources": {
                "industry": industry,
                "platform": platform,
                "content_type": content_type,
                "tone": tone,
                "target_audience": target_audience,
                "custom_requirements": custom_requirements
            }
        }
        
        logger.info(f"📋 Creating user_post with data: {user_post_data}")
        
        # Create user_post record
        user_post_response = await supabase._make_request(
            "POST",
            "user_posts",
            data=user_post_data
        )
        
        logger.info(f"📤 User post response status: {user_post_response.status_code}")
        logger.info(f"📤 User post response: {user_post_response.text}")
        
        if user_post_response.status_code != 201:
            logger.error(f"❌ Failed to create user_post: {user_post_response.status_code}")
            logger.error(f"❌ Response text: {user_post_response.text}")
            
            # Try to provide a more helpful error message
            if "target_platforms" in user_post_response.text:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid target_platforms format. Must be a non-empty array."
                )
            elif "user_id" in user_post_response.text:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid user_id format or user does not exist."
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to create user post record: {user_post_response.text}"
                )
        
        user_post_response_data = user_post_response.json() if user_post_response.json() else []
        logger.info(f"📋 User post response data: {user_post_response_data}")
        
        user_post_id = user_post_response_data[0]["id"] if user_post_response_data else None
        if not user_post_id:
            logger.error("❌ No user_post_id returned from user_posts creation")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get user post ID from response"
            )
        
        logger.info(f"✅ User post created successfully with ID: {user_post_id}")
        
        # Double-check that user_post_id is a valid UUID
        try:
            import uuid
            uuid.UUID(str(user_post_id))
        except ValueError:
            logger.error(f"❌ Invalid UUID format for user_post_id: {user_post_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid user post ID format"
            )
        
        # Prepare data for ai_content_suggestions table
        suggestion_data = {
            "user_post_id": str(user_post_id),  # Ensure it's a string
            "user_id": user_id,
            "suggestion_version": 1,
            "suggested_content": suggested_content,
            "suggested_hashtags": hashtags,
            "suggested_media_types": ["text"],  # Default to text for now
            "model_used": "content_planning_agent",
            "prompt_used": f"Generate {content_type} content for {platform} in {industry} industry with {tone} tone for {target_audience}",
            "temperature": 0.7,
            "max_tokens": 500,
            "competitor_analysis": {
                "industry": industry,
                "platform": platform,
                "content_type": content_type,
                "tone": tone,
                "target_audience": target_audience,
                "custom_requirements": custom_requirements
            },
            "content_strategy": {
                "platform": platform,
                "content_type": content_type,
                "tone": tone,
                "target_audience": target_audience
            },
            "predicted_engagement": {
                "estimated_reach": "medium",
                "estimated_engagement_rate": "high",
                "confidence_score": 85
            },
            "was_accepted": False,
            "processing_time_ms": 2000  # Mock processing time
        }
        
        logger.info(f"📋 Saving AI content suggestion with data: {suggestion_data}")
        
        # Insert into ai_content_suggestions table
        response = await supabase._make_request(
            "POST",
            "ai_content_suggestions",
            data=suggestion_data
        )
        
        logger.info(f"📤 AI suggestion response status: {response.status_code}")
        logger.info(f"📤 AI suggestion response: {response.text}")
        
        if response.status_code == 201:
            logger.info(f"✅ Content suggestion saved successfully for user {user_id}")
            return {
                "success": True,
                "message": "Content suggestion saved successfully",
                "suggestion_id": response.json()[0]["id"] if response.json() else None,
                "user_post_id": user_post_id
            }
        else:
            logger.error(f"❌ Failed to save content suggestion: {response.status_code}")
            logger.error(f"❌ Response text: {response.text}")
            
            # Try to provide a more helpful error message
            if "user_post_id" in response.text:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid user_post_id format or user_post does not exist."
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to save content suggestion: {response.text}"
                )
            
    except Exception as e:
        logger.error(f"❌ Save content suggestion error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save content suggestion: {str(e)}"
        )


@router.get("/get-content-suggestions")
async def get_content_suggestions(user_id: str = Query(..., description="User ID"), limit: int = Query(3, description="Number of suggestions to return")):
    """
    Get latest content suggestions for a user from ai_content_suggestions table
    """
    try:
        logger.info(f"📋 Fetching content suggestions for user {user_id}")
        
        supabase = supabase_client
        
        # Query ai_content_suggestions table for the user, ordered by creation date
        response = await supabase._make_request(
            "GET",
            "ai_content_suggestions",
            params={
                "user_id": f"eq.{user_id}",
                "order": "created_at.desc",
                "limit": str(limit)
            }
        )
        
        if response.status_code == 200:
            suggestions = response.json() if response.json() else []
            logger.info(f"✅ Retrieved {len(suggestions)} content suggestions for user {user_id}")
            return {
                "success": True,
                "suggestions": suggestions
            }
        else:
            logger.error(f"❌ Failed to fetch content suggestions: {response.status_code}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch content suggestions"
            )
            
    except Exception as e:
        logger.error(f"❌ Get content suggestions error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch content suggestions: {str(e)}"
        )


@router.post("/analyze-competitors", response_model=CompetitorAnalysisResponse)
async def analyze_competitors(request: CompetitorAnalysisRequest) -> CompetitorAnalysisResponse:
    """
    Analyze competitor content for strategic insights
    """
    try:
        logger.info(f"🔍 Competitor analysis request for {request.industry}")
        
        result = await content_planning_service.analyze_competitors(
            industry=request.industry,
            competitor_ids=request.competitor_ids,
            analysis_type=request.analysis_type,
            time_period=request.time_period
        )
        
        return CompetitorAnalysisResponse(**result)
        
    except Exception as e:
        logger.error(f"❌ Competitor analysis endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Competitor analysis failed: {str(e)}"
        )


@router.post("/research-hashtags", response_model=HashtagResearchResponse)
async def research_hashtags(request: HashtagResearchRequest) -> HashtagResearchResponse:
    """
    Research optimal hashtag strategies for content
    """
    try:
        logger.info(f"🏷️ Hashtag research request for {request.platform} in {request.industry}")
        
        result = await content_planning_service.research_hashtags(
            industry=request.industry,
            content_type=request.content_type,
            platform=request.platform,
            target_audience=request.target_audience,
            custom_keywords=request.custom_keywords
        )
        
        return HashtagResearchResponse(**result)
        
    except Exception as e:
        logger.error(f"❌ Hashtag research endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hashtag research failed: {str(e)}"
        )


@router.post("/generate-strategy", response_model=ContentStrategyResponse)
async def generate_content_strategy(request: ContentStrategyRequest) -> ContentStrategyResponse:
    """
    Generate comprehensive content strategy based on competitive analysis
    """
    try:
        logger.info(f"📋 Content strategy request for {request.industry}")
        
        result = await content_planning_service.generate_content_strategy(
            industry=request.industry,
            platforms=request.platforms,
            content_goals=request.content_goals,
            target_audience=request.target_audience
        )
        
        return ContentStrategyResponse(**result)
        
    except Exception as e:
        logger.error(f"❌ Content strategy endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Strategy generation failed: {str(e)}"
        )


@router.post("/generate-calendar", response_model=ContentCalendarResponse)
async def generate_content_calendar(request: ContentCalendarRequest) -> ContentCalendarResponse:
    """
    Generate AI-optimized content calendar
    """
    try:
        logger.info(f"📅 Content calendar request for {request.industry}")
        
        result = await content_planning_service.generate_content_calendar(
            industry=request.industry,
            platforms=request.platforms,
            duration_days=request.duration_days,
            posts_per_day=request.posts_per_day
        )
        
        return ContentCalendarResponse(**result)
        
    except Exception as e:
        logger.error(f"❌ Content calendar endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Calendar generation failed: {str(e)}"
        )


@router.post("/identify-gaps", response_model=ContentGapsResponse)
async def identify_content_gaps(request: ContentGapsRequest) -> ContentGapsResponse:
    """
    Identify content gaps based on competitor analysis
    """
    try:
        logger.info(f"🔍 Content gaps analysis request for {request.industry}")
        
        result = await content_planning_service.identify_content_gaps(
            industry=request.industry,
            user_content_summary=request.user_content_summary
        )
        
        return ContentGapsResponse(**result)
        
    except Exception as e:
        logger.error(f"❌ Content gaps endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gap analysis failed: {str(e)}"
        )


@router.post("/optimize-schedule", response_model=ScheduleOptimizationResponse)
async def optimize_posting_schedule(request: ScheduleOptimizationRequest) -> ScheduleOptimizationResponse:
    """
    Optimize posting schedule based on competitor timing analysis
    """
    try:
        logger.info(f"⏰ Schedule optimization request for {request.industry}")
        
        result = await content_planning_service.optimize_posting_schedule(
            industry=request.industry,
            platforms=request.platforms
        )
        
        return ScheduleOptimizationResponse(**result)
        
    except Exception as e:
        logger.error(f"❌ Schedule optimization endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Schedule optimization failed: {str(e)}"
        )


@router.get("/dashboard-data", response_model=DashboardDataResponse)
async def get_dashboard_data(industry: str = Query("technology", description="Target industry")) -> DashboardDataResponse:
    """
    Get comprehensive dashboard data for the content planning interface
    """
    try:
        logger.info(f"📊 Dashboard data request for {industry}")
        
        result = await content_planning_service.get_dashboard_data(industry)
        
        return DashboardDataResponse(**result)
        
    except Exception as e:
        logger.error(f"❌ Dashboard data endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Dashboard data generation failed: {str(e)}"
        )


@router.get("/industry-insights/{industry}", response_model=IndustryInsightsResponse)
async def get_industry_insights(industry: str) -> IndustryInsightsResponse:
    """
    Get specific insights for an industry
    """
    try:
        logger.info(f"💡 Industry insights request for {industry}")
        
        result = await content_planning_service.get_industry_insights(industry)
        
        return IndustryInsightsResponse(**result)
        
    except Exception as e:
        logger.error(f"❌ Industry insights endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Industry insights failed: {str(e)}"
        )


@router.get("/supported-options", response_model=SupportedOptionsResponse)
async def get_supported_options() -> SupportedOptionsResponse:
    """
    Get supported industries, platforms, content types, and tones
    """
    try:
        logger.info("🔧 Supported options request")
        
        result = content_planning_service.get_supported_options()
        
        return SupportedOptionsResponse(**result)
        
    except Exception as e:
        logger.error(f"❌ Supported options endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get supported options: {str(e)}"
        )
