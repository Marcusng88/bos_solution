"""
Self-optimization endpoints for campaign analysis and recommendations
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc, text
from typing import List, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal

from app.core.database import get_db
from app.core.auth_utils import get_user_id_from_header
from app.models.campaign import (
    CampaignData, OptimizationAlert, RiskPattern, OptimizationRecommendation
)
from app.schemas.campaign import (
    CampaignDataCreate, CampaignDataResponse, CampaignDataUpdate,
    OptimizationAlertResponse, RiskPatternResponse, OptimizationRecommendationResponse,
    CampaignStatsResponse, DashboardMetrics, BudgetMonitoringResponse,
    CampaignPerformanceResponse
)
from app.services.optimization.optimization_service import OptimizationService

router = APIRouter()


@router.get("/dashboard/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard metrics for self-optimization"""
    try:
        optimization_service = OptimizationService(db)
        metrics = await optimization_service.get_dashboard_metrics(user_id)
        return metrics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch dashboard metrics: {str(e)}"
        )


@router.get("/dashboard/metrics/detailed")
async def get_detailed_dashboard_metrics(
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed dashboard metrics including risk and alert breakdowns"""
    try:
        optimization_service = OptimizationService(db)
        
        # Get basic metrics
        basic_metrics = await optimization_service.get_dashboard_metrics(user_id)
        
        # Get detailed breakdowns
        risk_breakdown = await optimization_service.get_risk_breakdown(user_id)
        alert_breakdown = await optimization_service.get_alert_breakdown(user_id)
        
        return {
            "basic_metrics": basic_metrics,
            "risk_breakdown": risk_breakdown,
            "alert_breakdown": alert_breakdown
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch detailed dashboard metrics: {str(e)}"
        )


@router.get("/campaigns")
async def get_campaigns(
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Get list of campaigns with their data"""
    try:
        optimization_service = OptimizationService(db)
        campaigns = await optimization_service.get_campaigns(user_id)
        return campaigns
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch campaigns: {str(e)}"
        )


@router.get("/overspending-predictions")
async def get_overspending_predictions(
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Get enhanced overspending predictions with risk analysis"""
    try:
        optimization_service = OptimizationService(db)
        campaigns = await optimization_service.get_campaigns(user_id)
        
        # Filter for ongoing campaigns and calculate enhanced risk scores
        predictions = []
        for campaign in campaigns:
            if campaign.get('ongoing') == 'Yes':
                risk_analysis = optimization_service.calculate_enhanced_risk_score(campaign)
                
                # Include ALL ongoing campaigns with their risk scores
                predictions.append({
                    'campaign_name': risk_analysis['campaign_name'],
                    'current_spend': risk_analysis['current_spend'],
                    'current_budget': risk_analysis['current_budget'],
                    'net_profit': risk_analysis['net_profit'],
                    'overspend_risk': risk_analysis['overspend_risk'],
                    'days_until_overspend': risk_analysis['days_until_overspend'],
                    'risk_factors': risk_analysis['risk_factors'],
                    'budget_utilization': risk_analysis['budget_utilization'],
                    'profit_margin': risk_analysis['profit_margin'],
                    'risk_score': risk_analysis['risk_score'],
                    'performance_score': risk_analysis['performance_score'],
                    'performance_category': risk_analysis['performance_category'],
                    'ctr': risk_analysis['ctr'],
                    'cpc': risk_analysis['cpc'],
                    'conversion_rate': risk_analysis['conversion_rate']
                })
        
        # Sort by risk score (highest first)
        predictions.sort(key=lambda x: x['risk_score'], reverse=True)
        
        return predictions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch overspending predictions: {str(e)}"
        )


@router.put("/campaigns/status")
async def update_campaign_status(
    campaign_update: dict,
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Update campaign ongoing status"""
    try:
        campaign_name = campaign_update.get('campaign_name')
        ongoing_status = campaign_update.get('ongoing')
        
        if not campaign_name or ongoing_status not in ['Yes', 'No']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid campaign name or status"
            )
        
        # Update the ongoing field in campaign_data table
        result = await db.execute(text("""
            UPDATE campaign_data 
            SET ongoing = :ongoing_status 
            WHERE name = :campaign_name
        """), {
            "ongoing_status": ongoing_status,
            "campaign_name": campaign_name
        })
        
        await db.commit()
        
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        return {"message": f"Campaign {campaign_name} status updated to {ongoing_status}"}
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update campaign status: {str(e)}"
        )


@router.put("/campaigns/budget")
async def update_campaign_budget(
    budget_update: dict,
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Update campaign budget"""
    try:
        campaign_name = budget_update.get('campaign_name')
        new_budget = budget_update.get('budget')
        
        if not campaign_name or not new_budget or new_budget <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid campaign name or budget amount"
            )
        
        # Update the budget field in campaign_data table
        result = await db.execute(text("""
            UPDATE campaign_data 
            SET budget = :new_budget 
            WHERE name = :campaign_name
        """), {
            "new_budget": float(new_budget),
            "campaign_name": campaign_name
        })
        
        await db.commit()
        
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        return {"message": f"Campaign {campaign_name} budget updated to ${new_budget}"}
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update campaign budget: {str(e)}"
        )


@router.get("/campaigns/stats", response_model=CampaignStatsResponse)
async def get_campaign_stats(
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db),
    days: int = Query(7, ge=1, le=365)
):
    """Get campaign statistics for specified period"""
    try:
        optimization_service = OptimizationService(db)
        stats = await optimization_service.get_campaign_stats(user_id, days)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch campaign stats: {str(e)}"
        )


@router.get("/campaigns/{campaign_name}/performance", response_model=CampaignPerformanceResponse)
async def get_campaign_performance(
    campaign_name: str,
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db),
    days: int = Query(30, ge=1, le=365)
):
    """Get performance trends for a specific campaign"""
    try:
        optimization_service = OptimizationService(db)
        performance = await optimization_service.get_campaign_performance(user_id, campaign_name, days)
        return performance
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch campaign performance: {str(e)}"
        )


@router.get("/budget/monitoring", response_model=List[BudgetMonitoringResponse])
async def get_budget_monitoring(
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db),
    days: int = Query(7, ge=1, le=365)
):
    """Get budget monitoring data"""
    try:
        optimization_service = OptimizationService(db)
        monitoring_data = await optimization_service.get_budget_monitoring(user_id, days)
        return monitoring_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch budget monitoring data: {str(e)}"
        )


@router.get("/alerts", response_model=List[OptimizationAlertResponse])
async def get_optimization_alerts(
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db),
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=200)
):
    """Get optimization alerts"""
    try:
        optimization_service = OptimizationService(db)
        alerts = await optimization_service.get_optimization_alerts(user_id, unread_only, limit)
        return alerts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch optimization alerts: {str(e)}"
        )


@router.put("/alerts/{alert_id}/read")
async def mark_alert_as_read(
    alert_id: str,
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Mark alert as read"""
    try:
        optimization_service = OptimizationService(db)
        success = await optimization_service.mark_alert_as_read(user_id, alert_id)
        if success:
            return {"message": "Alert marked as read"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark alert as read: {str(e)}"
        )


@router.get("/risk-patterns", response_model=List[RiskPatternResponse])
async def get_risk_patterns(
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db),
    unresolved_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=200)
):
    """Get risk patterns"""
    try:
        optimization_service = OptimizationService(db)
        patterns = await optimization_service.get_risk_patterns(user_id, unresolved_only, limit)
        return patterns
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch risk patterns: {str(e)}"
        )


@router.get("/recommendations", response_model=List[OptimizationRecommendationResponse])
async def get_optimization_recommendations(
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db),
    unapplied_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=200)
):
    """Get optimization recommendations"""
    try:
        optimization_service = OptimizationService(db)
        recommendations = await optimization_service.get_recommendations(user_id, unapplied_only, limit)
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch optimization recommendations: {str(e)}"
        )


@router.put("/recommendations/{recommendation_id}/apply")
async def apply_recommendation(
    recommendation_id: str,
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Apply a recommendation"""
    try:
        optimization_service = OptimizationService(db)
        success = await optimization_service.apply_recommendation(user_id, recommendation_id)
        if success:
            return {"message": "Recommendation applied successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recommendation not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply recommendation: {str(e)}"
        )


@router.post("/ai/chat")
async def ai_chat_assistant(
    message: dict,
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """AI chat assistant for optimization advice"""
    try:
        user_message = message.get("message", "")
        if not user_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message is required"
            )
        
        optimization_service = OptimizationService(db)
        ai_response = await optimization_service.get_ai_response(user_id, user_message)
        
        return {
            "response": ai_response,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get AI response: {str(e)}"
        )