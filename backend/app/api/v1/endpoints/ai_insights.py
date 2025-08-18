"""
AI Insights endpoints for campaign analysis and recommendations
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.core.database import get_db
from app.core.auth_utils import get_current_user_id
from app.services.ai_service import ai_service
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
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Analyze campaign data and generate AI insights
    """
    try:
        print(f"🔍 Analyze request from user: {user_id}")
        print(f"🔍 Database session: {db}")
        
        # Run AI analysis
        analysis = await ai_service.analyze_campaign_data(db, user_id)
        
        print(f"✅ AI analysis completed successfully")
        print(f"📊 Analysis result: {analysis}")
        
        return AIAnalysisResponse(
            success=True,
            analysis=analysis,
            message="AI analysis completed successfully"
        )
        
    except Exception as e:
        print(f"❌ Error in analyze_campaigns: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze campaigns: {str(e)}"
        )


@router.post("/chat", response_model=AIChatResponse)
async def chat_with_ai(
    request: AIChatRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Chat with AI about campaigns and business questions
    """
    try:
        print(f"🔍 Chat request from user: {user_id}")
        print(f"🔍 Message: {request.message}")
        print(f"🔍 Database session: {db}")
        
        # Get AI response
        response = await ai_service.chat_with_ai(db, user_id, request.message)
        
        print(f"✅ AI response generated successfully")
        
        return AIChatResponse(
            success=True,
            response=response,
            message="AI response generated successfully"
        )
        
    except Exception as e:
        print(f"❌ Error in chat_with_ai: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate AI response: {str(e)}"
        )


@router.get("/insights", response_model=AIInsightsResponse)
async def get_ai_insights(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get AI insights for campaigns
    """
    try:
        # Generate AI insights
        analysis = await ai_service.analyze_campaign_data(db, user_id)
        
        return AIInsightsResponse(
            success=True,
            insights=analysis,
            message="AI insights generated successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate AI insights: {str(e)}"
        )
