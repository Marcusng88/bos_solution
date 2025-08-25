"""
AI Insights endpoints for campaign analysis and recommendations
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict, Any
from app.core.auth_utils import get_user_id_from_header
from app.core.database import get_db
# Conditional import of AI service - will work when dependencies are installed
try:
    from app.services.optimization.ai_service import ai_service
    AI_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ AI service not available: {e}")
    print("⚠️ Install langchain-google-genai and other dependencies to enable AI features")
    AI_SERVICE_AVAILABLE = False
    ai_service = None
from app.schemas.ai_insights import (
    AIAnalysisRequest,
    AIAnalysisResponse,
    AIChatRequest,
    AIChatResponse,
    AIInsightsResponse
)

router = APIRouter()


@router.post("/analyze", response_model=AIAnalysisResponse)
async def analyze_campaigns(
    request: AIAnalysisRequest,
    background_tasks: BackgroundTasks,
    db = Depends(get_db),
    user_id: str = Depends(get_user_id_from_header)
):
    """
    Analyze campaign data and generate AI insights
    """
    try:
        print(f"🔍 Analyze request from user: {user_id}")
        
        if not AI_SERVICE_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="AI service not available. Please install required dependencies (langchain-google-genai, etc.)"
            )
        
        # Use the actual AI service to analyze campaigns
        analysis = await ai_service.analyze_campaign_data(user_id)
        
        print(f"✅ AI analysis completed successfully")
        print(f"📊 Analysis result: {analysis}")
        
        return AIAnalysisResponse(
            success=True,
            analysis=analysis,
            message="AI analysis completed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in analyze_campaigns: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze campaigns: {str(e)}"
        )


@router.post("/chat", response_model=AIChatResponse)
async def chat_with_ai(
    request: AIChatRequest,
    db = Depends(get_db),
    user_id: str = Depends(get_user_id_from_header)
):
    """
    Chat with AI about campaigns and business questions
    """
    try:
        print(f"🔍 Chat request from user: {user_id}")
        print(f"🔍 Message: {request.message}")
        print(f"🔍 User ID type: {type(user_id)}")
        print(f"🔍 User ID length: {len(user_id) if user_id else 'None'}")
        
        if not AI_SERVICE_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="AI service not available. Please install required dependencies (langchain-google-genai, etc.)"
            )
        
        # Use the actual AI service to generate chat response
        ai_response = await ai_service.chat_with_ai(user_id, request.message)
        
        print(f"✅ AI response generated successfully")
        print(f"📄 Response length: {len(ai_response) if ai_response else 'None'}")
        print(f"📄 Response preview: {ai_response[:200]}..." if ai_response and len(ai_response) > 200 else f"📄 Full response: {ai_response}")
        
        return AIChatResponse(
            success=True,
            response=ai_response,
            message="AI response generated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in chat_with_ai: {e}")
        print(f"❌ Error type: {type(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate AI response: {str(e)}"
        )


@router.get("/insights", response_model=AIInsightsResponse)
async def get_ai_insights(
    db = Depends(get_db),
    user_id: str = Depends(get_user_id_from_header)
):
    """
    Get AI insights for campaigns
    """
    try:
        if not AI_SERVICE_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="AI service not available. Please install required dependencies (langchain-google-genai, etc.)"
            )
        
        # Use the actual AI service to generate insights
        analysis = await ai_service.analyze_campaign_data(user_id)
        
        return AIInsightsResponse(
            success=True,
            insights=analysis,
            message="AI insights generated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate AI insights: {str(e)}"
        )
