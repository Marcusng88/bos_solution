"""
Self-optimization endpoints for campaign analysis and recommendations
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal

from app.core.auth_utils import get_user_id_from_header
from app.core.supabase_client import supabase_client
from app.schemas.campaign import (
    CampaignDataCreate, CampaignDataResponse, CampaignDataUpdate,
    OptimizationAlertResponse, RiskPatternResponse, OptimizationRecommendationResponse,
    CampaignStatsResponse, DashboardMetrics, BudgetMonitoringResponse,
    CampaignPerformanceResponse
)

router = APIRouter()


@router.get("/dashboard/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    user_id: str = Depends(get_user_id_from_header)
):
    """Get dashboard metrics for self-optimization"""
    try:
        # Handle case when Supabase is not available
        if supabase_client is None:
            # Return mock data for development
            metrics = DashboardMetrics(
                spend_today=Decimal('92750.68'),
                budget_today=Decimal('173900.00'),
                alerts_count=8,
                risk_patterns_count=1,
                recommendations_count=5,
                budget_utilization_pct=Decimal('53.4')
            )
            return metrics
        
        # Get active spend and budget from ongoing campaigns
        response = await supabase_client._make_request(
            "GET", 
            "campaign_data", 
            params={
                "ongoing": "eq.Yes",
                "select": "spend,budget"
            }
        )
        
        if response.status_code != 200:
            # Fallback to mock data if API fails
            metrics = DashboardMetrics(
                spend_today=Decimal('0.00'),
                budget_today=Decimal('0.00'),
                alerts_count=0,
                risk_patterns_count=0,
                recommendations_count=0,
                budget_utilization_pct=Decimal('0.0')
            )
            return metrics
        
        campaigns = response.json()
        active_spend = sum(float(campaign.get('spend', 0) or 0) for campaign in campaigns)
        active_budget = sum(float(campaign.get('budget', 0) or 0) for campaign in campaigns)
        
        # Calculate budget utilization
        budget_utilization_pct = 0.0
        if active_budget > 0:
            budget_utilization_pct = (active_spend / active_budget) * 100
        
        # Check if optimization tables exist and count them
        alerts_count = 0
        risk_patterns_count = 0
        recommendations_count = 0
        
        # Try to get alerts count
        try:
            alerts_response = await supabase_client._make_request(
                "GET", 
                "optimization_alerts", 
                params={
                    "user_id": f"eq.{user_id}",
                    "is_read": "eq.false",
                    "select": "id"
                }
            )
            if alerts_response.status_code == 200:
                alerts_count = len(alerts_response.json())
        except:
            pass
        
        # Try to get risk patterns count
        try:
            risks_response = await supabase_client._make_request(
                "GET", 
                "risk_patterns", 
                params={
                    "user_id": f"eq.{user_id}",
                    "resolved": "eq.false",
                    "select": "id"
                }
            )
            if risks_response.status_code == 200:
                risk_patterns_count = len(risks_response.json())
        except:
            pass
        
        # Try to get recommendations count
        try:
            recs_response = await supabase_client._make_request(
                "GET", 
                "optimization_recommendations", 
                params={
                    "user_id": f"eq.{user_id}",
                    "is_applied": "eq.false",
                    "select": "id"
                }
            )
            if recs_response.status_code == 200:
                recommendations_count = len(recs_response.json())
        except:
            pass
        
        # Create and return the metrics
        metrics = DashboardMetrics(
            spend_today=Decimal(str(active_spend)),
            budget_today=Decimal(str(active_budget)),
            alerts_count=alerts_count,
            risk_patterns_count=risk_patterns_count,
            recommendations_count=recommendations_count,
            budget_utilization_pct=Decimal(str(budget_utilization_pct))
        )
        
        return metrics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch dashboard metrics: {str(e)}"
        )


@router.get("/dashboard/metrics/detailed")
async def get_detailed_dashboard_metrics(
    user_id: str = Depends(get_user_id_from_header)
):
    """Get detailed dashboard metrics including risk and alert breakdowns"""
    try:
        # Get basic metrics
        basic_metrics = await get_dashboard_metrics(user_id)
        
        # Get detailed breakdowns
        risk_breakdown = await get_risk_breakdown(user_id)
        alert_breakdown = await get_alert_breakdown(user_id)
        
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


@router.post("/campaigns")
async def create_campaign(
    campaign_data: dict,
    user_id: str = Depends(get_user_id_from_header)
):
    """Create a new campaign"""
    try:
        # Extract data from request
        campaign_name = campaign_data.get('name', '').strip()
        budget = campaign_data.get('budget', 0)
        ongoing = campaign_data.get('ongoing', 'No')
        
        # Validation
        if not campaign_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Campaign name is required"
            )
        
        try:
            budget = float(budget)
            if budget <= 0:
                raise ValueError("Budget must be positive")
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Budget must be a positive number"
            )
        
        if ongoing not in ['Yes', 'No']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ongoing status must be 'Yes' or 'No'"
            )
        
        # Check if Supabase is available
        if supabase_client is None:
            # Return success response for development without Supabase
            new_campaign = {
                "user_id": user_id,
                "name": campaign_name,
                "date": date.today().isoformat(),
                "impressions": 0,
                "clicks": 0,
                "ctr": 0.0,
                "cpc": 0.0,
                "spend": 0.0,
                "budget": budget,
                "conversions": 0,
                "net_profit": 0.0,
                "ongoing": ongoing,
                "id": f"mock_{campaign_name.replace(' ', '_').lower()}"
            }
            
            return {
                "message": f"Campaign '{campaign_name}' created successfully (mock mode)",
                "campaign": new_campaign
            }
        
        # Check if campaign with same name already exists for this user
        try:
            check_response = await supabase_client._make_request(
                "GET",
                "campaign_data",
                params={
                    "select": "id",
                    "name": f"eq.{campaign_name}",
                    "limit": "1"
                }
            )
            
            if check_response.status_code == 200 and check_response.json():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Campaign '{campaign_name}' already exists"
                )
        except Exception as e:
            # If check fails, continue with creation (better to create than block)
            pass
        
        # Create new campaign with default values
        new_campaign = {
            "user_id": user_id,
            "name": campaign_name,
            "date": date.today().isoformat(),
            "impressions": 0,
            "clicks": 0,
            "ctr": 0.0,
            "cpc": 0.0,
            "spend": 0.0,
            "budget": budget,
            "conversions": 0,
            "net_profit": 0.0,
            "ongoing": ongoing
        }
        
        # Insert the campaign into the campaign_data table
        response = await supabase_client._make_request(
            "POST",
            "campaign_data",
            data=new_campaign
        )
        
        if response.status_code != 201 and response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create campaign: {response.text}"
            )
        
        created_campaign = response.json()
        if isinstance(created_campaign, list) and len(created_campaign) > 0:
            created_campaign = created_campaign[0]
        
        return {
            "message": f"Campaign '{campaign_name}' created successfully",
            "campaign": created_campaign
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create campaign: {str(e)}"
        )


@router.get("/campaigns")
async def get_campaigns(
    user_id: str = Depends(get_user_id_from_header)
):
    """Get list of campaigns with their data"""
    try:
        # Handle case when Supabase is not available
        if supabase_client is None:
            # Return mock data for development
            mock_campaigns = [
                {
                    'name': 'HP Spectre X360',
                    'spend': 8582.0,
                    'budget': 10000.0,
                    'ctr': 2.57,
                    'cpc': 1.57,
                    'conversions': 245,
                    'ongoing': 'Yes',
                    'date': '2025-07-11',
                    'net_profit': -2347.18,
                    'impressions': 551551
                },
                {
                    'name': 'Xiaomi Smart Home',
                    'spend': 14760.0,
                    'budget': 15018.0,
                    'ctr': 4.63,
                    'cpc': 4.29,
                    'conversions': 2149,
                    'ongoing': 'Yes',
                    'date': '2025-02-17',
                    'net_profit': 6015.57,
                    'impressions': 994742
                }
            ]
            return mock_campaigns
        
        # Get campaigns with their latest data
        response = await supabase_client._make_request(
            "GET", 
            "campaign_data", 
            params={
                "select": "name,spend,budget,ctr,cpc,conversions,ongoing,date,net_profit,impressions",
                "order": "date.desc"
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch campaigns"
            )
        
        campaigns_data = response.json()
        
        # Group by campaign name and get the latest entry for each
        campaigns = {}
        for campaign in campaigns_data:
            name = campaign.get('name')
            if name and name not in campaigns:
                campaigns[name] = {
                    'name': name,
                    'spend': float(campaign.get('spend', 0) or 0),
                    'budget': float(campaign.get('budget', 0) or 0),
                    'ctr': float(campaign.get('ctr', 0) or 0),
                    'cpc': float(campaign.get('cpc', 0) or 0),
                    'conversions': int(campaign.get('conversions', 0) or 0),
                    'ongoing': campaign.get('ongoing'),
                    'date': campaign.get('date'),
                    'net_profit': float(campaign.get('net_profit', 0) or 0),
                    'impressions': int(campaign.get('impressions', 0) or 0)
                }
        
        return list(campaigns.values())
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch campaigns: {str(e)}"
        )


@router.get("/overspending-predictions")
async def get_overspending_predictions(
    user_id: str = Depends(get_user_id_from_header)
):
    """Get enhanced overspending predictions with risk analysis"""
    try:
        campaigns = await get_campaigns(user_id)
        
        # Handle case when no campaigns are returned
        if not campaigns:
            return []
        
        # Filter for ongoing campaigns and calculate enhanced risk scores
        predictions = []
        for campaign in campaigns:
            if campaign.get('ongoing') == 'Yes':
                risk_analysis = calculate_enhanced_risk_score(campaign)
                
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
    user_id: str = Depends(get_user_id_from_header)
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
        success = await supabase_client.update_campaign_by_name_and_user(
            user_id=user_id,
            campaign_name=campaign_name,
            update_data={"ongoing": ongoing_status}
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update campaign status"
            )
        
        return {"message": f"Campaign {campaign_name} status updated to {ongoing_status}"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update campaign status: {str(e)}"
        )


@router.put("/campaigns/budget")
async def update_campaign_budget(
    budget_update: dict,
    user_id: str = Depends(get_user_id_from_header)
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
        success = await supabase_client.update_campaign_by_name_and_user(
            user_id=user_id,
            campaign_name=campaign_name,
            update_data={"budget": float(new_budget)}
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update campaign budget"
            )
        
        return {"message": f"Campaign {campaign_name} budget updated to ${new_budget}"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update campaign budget: {str(e)}"
        )


@router.get("/campaigns/stats", response_model=CampaignStatsResponse)
async def get_campaign_stats(
    user_id: str = Depends(get_user_id_from_header),
    days: int = Query(7, ge=1, le=365)
):
    """Get campaign statistics for specified period"""
    try:
        start_date = date.today() - timedelta(days=days)
        
        # Get campaign stats for the specified period
        response = await supabase_client._make_request(
            "GET",
            "campaign_data",
            params={
                "select": "name,spend,budget,ctr,cpc,conversions,ongoing,date",
                "date": f"gte.{start_date.isoformat()}",
                "order": "date.desc"
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch campaign stats"
            )
        
        campaigns_data = response.json()
        
        # Calculate statistics
        total_campaigns = len(set(campaign.get('name') for campaign in campaigns_data if campaign.get('name')))
        total_spend = sum(float(campaign.get('spend', 0) or 0) for campaign in campaigns_data)
        total_budget = sum(float(campaign.get('budget', 0) or 0) for campaign in campaigns_data)
        
        # Calculate averages
        ctr_values = [float(campaign.get('ctr', 0) or 0) for campaign in campaigns_data if campaign.get('ctr')]
        cpc_values = [float(campaign.get('cpc', 0) or 0) for campaign in campaigns_data if campaign.get('cpc')]
        avg_ctr = sum(ctr_values) / len(ctr_values) if ctr_values else 0
        avg_cpc = sum(cpc_values) / len(cpc_values) if cpc_values else 0
        
        total_conversions = sum(int(campaign.get('conversions', 0) or 0) for campaign in campaigns_data)
        
        # Get active campaigns count
        active_response = await supabase_client._make_request(
            "GET",
            "campaign_data",
            params={
                "select": "name",
                "ongoing": "eq.Yes"
            }
        )
        
        active_campaigns = 0
        if active_response.status_code == 200:
            active_campaigns = len(set(campaign.get('name') for campaign in active_response.json() if campaign.get('name')))
        
        # Calculate budget utilization
        budget_utilization = Decimal('0')
        if total_budget > 0:
            budget_utilization = (total_spend / total_budget) * 100
        
        return CampaignStatsResponse(
            total_campaigns=total_campaigns,
            active_campaigns=active_campaigns,
            total_spend=Decimal(str(total_spend)),
            total_budget=Decimal(str(total_budget)),
            avg_ctr=Decimal(str(avg_ctr)),
            avg_cpc=Decimal(str(avg_cpc)),
            total_conversions=total_conversions,
            budget_utilization=budget_utilization
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch campaign stats: {str(e)}"
        )


@router.get("/campaigns/{campaign_name}/performance", response_model=CampaignPerformanceResponse)
async def get_campaign_performance(
    campaign_name: str,
    user_id: str = Depends(get_user_id_from_header),
    days: int = Query(30, ge=1, le=365)
):
    """Get performance trends for a specific campaign"""
    try:
        start_date = date.today() - timedelta(days=days)
        
        response = await supabase_client._make_request(
            "GET",
            "campaign_data",
            params={
                "select": "date,spend,ctr,cpc,conversions",
                "name": f"eq.{campaign_name}",
                "date": f"gte.{start_date.isoformat()}",
                "order": "date.asc"
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch campaign performance"
            )
        
        campaign_data = response.json()
        
        dates = [data.get('date') for data in campaign_data if data.get('date')]
        spend_trend = [float(data.get('spend', 0) or 0) for data in campaign_data]
        ctr_trend = [float(data.get('ctr', 0) or 0) for data in campaign_data]
        cpc_trend = [float(data.get('cpc', 0) or 0) for data in campaign_data]
        conversions_trend = [int(data.get('conversions', 0) or 0) for data in campaign_data]
        
        return CampaignPerformanceResponse(
            campaign_name=campaign_name,
            dates=dates,
            spend_trend=spend_trend,
            ctr_trend=ctr_trend,
            cpc_trend=cpc_trend,
            conversions_trend=conversions_trend
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch campaign performance: {str(e)}"
        )


@router.get("/budget/monitoring", response_model=List[BudgetMonitoringResponse])
async def get_budget_monitoring(
    user_id: str = Depends(get_user_id_from_header),
    days: int = Query(7, ge=1, le=365)
):
    """Get budget monitoring data"""
    try:
        start_date = date.today() - timedelta(days=days)
        
        response = await supabase_client._make_request(
            "GET",
            "campaign_data",
            params={
                "select": "name,date,spend,budget",
                "date": f"gte.{start_date.isoformat()}",
                "order": "date.desc"
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch budget monitoring data"
            )
        
        monitoring_data = []
        for row in response.json():
            spend = float(row.get('spend', 0) or 0)
            budget = float(row.get('budget', 0) or 0)
            utilization_pct = Decimal('0')
            if budget > 0:
                utilization_pct = (spend / budget) * 100
            
            # Determine status
            status = "normal"
            if utilization_pct > 100:
                status = "critical"
            elif utilization_pct > 80:
                status = "warning"
            
            monitoring_data.append(BudgetMonitoringResponse(
                campaign_name=row.get('name', ''),
                date=row.get('date'),
                spend=Decimal(str(spend)),
                budget=Decimal(str(budget)),
                utilization_pct=utilization_pct,
                status=status
            ))
        
        return monitoring_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch budget monitoring data: {str(e)}"
        )


@router.get("/alerts", response_model=List[OptimizationAlertResponse])
async def get_optimization_alerts(
    user_id: str = Depends(get_user_id_from_header),
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=200)
):
    """Get optimization alerts"""
    try:
        params = {
            "select": "*",
            "order": "created_at.desc",
            "limit": str(limit)
        }
        
        if unread_only:
            params["is_read"] = "eq.false"
        
        response = await supabase_client._make_request(
            "GET",
            "optimization_alerts",
            params=params
        )
        
        if response.status_code != 200:
            return []
        
        alerts = response.json()
        return [OptimizationAlertResponse.model_validate(alert) for alert in alerts]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch optimization alerts: {str(e)}"
        )


@router.put("/alerts/{alert_id}/read")
async def mark_alert_as_read(
    alert_id: str,
    user_id: str = Depends(get_user_id_from_header)
):
    """Mark alert as read"""
    try:
        response = await supabase_client._make_request(
            "PATCH",
            "optimization_alerts",
            data={
                "is_read": True,
                "read_at": datetime.utcnow().isoformat()
            },
            params={"id": f"eq.{alert_id}"}
        )
        
        if response.status_code == 200:
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
    unresolved_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=200)
):
    """Get risk patterns"""
    try:
        params = {
            "select": "*",
            "order": "detected_at.desc",
            "limit": str(limit)
        }
        
        if unresolved_only:
            params["resolved"] = "eq.false"
        
        response = await supabase_client._make_request(
            "GET",
            "risk_patterns",
            params=params
        )
        
        if response.status_code != 200:
            return []
        
        patterns = response.json()
        return [RiskPatternResponse.model_validate(pattern) for pattern in patterns]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch risk patterns: {str(e)}"
        )


@router.get("/recommendations", response_model=List[OptimizationRecommendationResponse])
async def get_optimization_recommendations(
    user_id: str = Depends(get_user_id_from_header),
    unapplied_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=200)
):
    """Get optimization recommendations"""
    try:
        params = {
            "select": "*",
            "order": "created_at.desc",
            "limit": str(limit)
        }
        
        if unapplied_only:
            params["is_applied"] = "eq.false"
        
        response = await supabase_client._make_request(
            "GET",
            "optimization_recommendations",
            params=params
        )
        
        if response.status_code != 200:
            return []
        
        recommendations = response.json()
        return [OptimizationRecommendationResponse.model_validate(rec) for rec in recommendations]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch optimization recommendations: {str(e)}"
        )


@router.put("/recommendations/{recommendation_id}/apply")
async def apply_recommendation(
    recommendation_id: str,
    user_id: str = Depends(get_user_id_from_header)
):
    """Apply a recommendation"""
    try:
        response = await supabase_client._make_request(
            "PATCH",
            "optimization_recommendations",
            data={
                "is_applied": True,
                "applied_at": datetime.utcnow().isoformat()
            },
            params={"id": f"eq.{recommendation_id}"}
        )
        
        if response.status_code == 200:
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
    user_id: str = Depends(get_user_id_from_header)
):
    """AI chat assistant for optimization advice"""
    try:
        user_message = message.get("message", "")
        if not user_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message is required"
            )
        
        # Get recent campaign stats for context
        stats = await get_campaign_stats(user_id, 7)
        
        # Generate AI response based on message content
        message_lower = user_message.lower()
        
        if "budget" in message_lower or "spend" in message_lower:
            ai_response = f"Based on your recent data, you've spent ${stats.total_spend:.2f} out of a ${stats.total_budget:.2f} budget ({stats.budget_utilization:.1f}% utilization). I recommend monitoring campaigns with >80% utilization closely to prevent overspending."
        
        elif "performance" in message_lower or "ctr" in message_lower or "cpc" in message_lower:
            ai_response = f"Your average CTR is {stats.avg_ctr:.3f}% and average CPC is ${stats.avg_cpc:.2f}. Industry benchmarks suggest CTR above 2% and CPC below $3 are good targets. Consider testing new creatives if CTR is below 1%."
        
        elif "recommendation" in message_lower or "optimize" in message_lower:
            ai_response = f"I see you have {stats.active_campaigns} active campaigns. Focus on pausing underperforming campaigns with zero conversions and scaling those with CTR >2%. Would you like specific recommendations for any particular campaign?"
        
        elif "alert" in message_lower or "issue" in message_lower:
            # Get alert count
            metrics = await get_dashboard_metrics(user_id)
            ai_response = f"You currently have {metrics.alerts_count} unread alerts and {metrics.risk_patterns_count} risk patterns detected. Check your dashboard for details on overspending or performance issues."
        
        else:
            ai_response = "I'm here to help optimize your campaigns! Ask me about budget utilization, performance metrics, recommendations, or any specific campaign concerns you have."
        
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


async def get_risk_breakdown(user_id: str) -> dict:
    """Get breakdown of risk patterns by severity"""
    try:
        response = await supabase_client._make_request(
            "GET",
            "risk_patterns",
            params={
                "select": "severity",
                "resolved": "eq.false"
            }
        )
        
        if response.status_code != 200:
            return {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        patterns = response.json()
        risk_breakdown = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        for pattern in patterns:
            severity = pattern.get('severity', 'medium').lower()
            if severity in risk_breakdown:
                risk_breakdown[severity] += 1
        
        return risk_breakdown
        
    except Exception:
        return {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}


async def get_alert_breakdown(user_id: str) -> dict:
    """Get breakdown of alerts by priority"""
    try:
        response = await supabase_client._make_request(
            "GET",
            "optimization_alerts",
            params={
                "select": "priority",
                "is_read": "eq.false"
            }
        )
        
        if response.status_code != 200:
            return {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        alerts = response.json()
        alert_breakdown = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        for alert in alerts:
            priority = alert.get('priority', 'medium').lower()
            if priority in alert_breakdown:
                alert_breakdown[priority] += 1
        
        return alert_breakdown
        
    except Exception:
        return {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}


def calculate_enhanced_risk_score(campaign: dict) -> dict:
    """
    Calculate enhanced risk score for a campaign
    """
    current_spend = campaign.get('spend', 0)
    current_budget = campaign.get('budget', 0)
    net_profit = campaign.get('net_profit', 0)
    ctr = campaign.get('ctr', 0)
    cpc = campaign.get('cpc', 0)
    conversions = campaign.get('conversions', 0)
    impressions = campaign.get('impressions', 0)
    
    # Calculate budget utilization
    budget_utilization = (current_spend / current_budget * 100) if current_budget > 0 else 0
    
    # Calculate profit margin
    profit_margin = (net_profit / current_spend * 100) if current_spend > 0 else 0
    
    # Calculate conversion rate
    conversion_rate = (conversions / impressions * 100) if impressions > 0 else 0
    
    # Risk factors and their weights
    risk_factors = []
    risk_score = 0.0
    
    # 1. Budget Utilization Risk (40% weight)
    budget_risk = 0.0
    if budget_utilization > 95:
        budget_risk = 1.0
        risk_factors.append('Critical budget utilization')
    elif budget_utilization > 85:
        budget_risk = 0.8
        risk_factors.append('High budget utilization')
    elif budget_utilization > 75:
        budget_risk = 0.6
        risk_factors.append('Above 75% budget utilization')
    elif budget_utilization > 50:
        budget_risk = 0.3
        risk_factors.append('Moderate budget utilization')
    
    risk_score += budget_risk * 0.4
    
    # 2. Profit Performance Risk (30% weight)
    profit_risk = 0.0
    if profit_margin < -20:
        profit_risk = 1.0
        risk_factors.append('Severe negative profit margin')
    elif profit_margin < -10:
        profit_risk = 0.8
        risk_factors.append('Negative profit margin')
    elif profit_margin < 0:
        profit_risk = 0.6
        risk_factors.append('Low profit margin')
    elif profit_margin < 10:
        profit_risk = 0.3
        risk_factors.append('Below average profit margin')
    
    risk_score += profit_risk * 0.3
    
    # 3. Performance Metrics Risk (20% weight)
    performance_risk = 0.0
    
    # CTR risk (industry average is around 2-3%)
    if ctr < 1.0:
        performance_risk += 0.5
        risk_factors.append('Low CTR')
    elif ctr < 2.0:
        performance_risk += 0.3
        risk_factors.append('Below average CTR')
    
    # CPC risk (high CPC indicates poor efficiency)
    if cpc > 5.0:
        performance_risk += 0.5
        risk_factors.append('High CPC')
    elif cpc > 3.0:
        performance_risk += 0.3
        risk_factors.append('Above average CPC')
    
    # Conversion rate risk
    if conversion_rate < 1.0:
        performance_risk += 0.5
        risk_factors.append('Low conversion rate')
    elif conversion_rate < 2.0:
        performance_risk += 0.3
        risk_factors.append('Below average conversion rate')
    
    performance_risk = min(performance_risk, 1.0)  # Cap at 1.0
    risk_score += performance_risk * 0.2
    
    # 4. Spending Velocity Risk (10% weight)
    velocity_risk = 0.0
    if current_spend > 0 and current_budget > 0:
        remaining_budget = current_budget - current_spend
        if remaining_budget > 0:
            # Estimate daily spend based on current utilization
            estimated_daily_spend = current_spend / 30  # Assume 30-day month
            days_until_overspend = remaining_budget / estimated_daily_spend
            
            if days_until_overspend < 5:
                velocity_risk = 1.0
                risk_factors.append('Extremely rapid spending rate')
            elif days_until_overspend < 10:
                velocity_risk = 0.8
                risk_factors.append('Rapid spending rate')
            elif days_until_overspend < 15:
                velocity_risk = 0.5
                risk_factors.append('Above average spending rate')
    
    risk_score += velocity_risk * 0.1
    
    # Determine risk level
    if risk_score >= 0.8:
        risk_level = 'critical'
    elif risk_score >= 0.6:
        risk_level = 'high'
    elif risk_score >= 0.4:
        risk_level = 'medium'
    else:
        risk_level = 'low'
    
    # Calculate performance score (100 - risk score * 100)
    performance_score = 100 - (risk_score * 100)
    
    # Determine performance category
    if performance_score >= 90:
        performance_category = "Excellent"
    elif performance_score >= 80:
        performance_category = "Good"
    elif performance_score >= 70:
        performance_category = "Fair"
    elif performance_score >= 60:
        performance_category = "Underperform"
    else:
        performance_category = "Poor"
    
    # Calculate days until overspend
    days_until_overspend = calculate_days_until_overspend(campaign, budget_utilization)
    
    return {
        'campaign_name': campaign['name'],
        'current_spend': campaign['spend'],
        'current_budget': campaign['budget'],
        'net_profit': campaign['net_profit'],
        'overspend_risk': risk_level,
        'risk_score': round(risk_score, 3),
        'days_until_overspend': int(days_until_overspend) if days_until_overspend is not None else -1,
        'risk_factors': list(set(risk_factors)),
        'budget_utilization': round(budget_utilization, 1),
        'profit_margin': round(profit_margin, 1),
        'performance_score': round(performance_score, 1),
        'performance_category': performance_category,
        'ctr': round(ctr, 2) if ctr > 0 else None,
        'cpc': round(cpc, 2) if cpc > 0 else None,
        'conversion_rate': round(conversion_rate, 2) if conversion_rate > 0 else None
    }


def calculate_days_until_overspend(campaign: dict, budget_utilization: float) -> int:
    """Calculate days until overspend based on current spending patterns"""
    current_spend = campaign.get('spend', 0)
    current_budget = campaign.get('budget', 0)
    
    if current_spend <= 0 or current_budget <= 0:
        return 30  # Default if no data
    
    remaining_budget = current_budget - current_spend
    
    if remaining_budget <= 0:
        return 0  # Already overspent
    
    # Estimate daily spend based on current utilization and time period
    estimated_daily_spend = current_spend / 30  # Assume 30-day month
    
    if estimated_daily_spend <= 0:
        return 30  # Default if no daily spend
    
    days_until_overspend = remaining_budget / estimated_daily_spend
    
    # Apply some realistic constraints
    if budget_utilization > 95:
        return max(1, int(days_until_overspend))
    elif budget_utilization > 85:
        return max(3, int(days_until_overspend))
    elif budget_utilization > 75:
        return max(7, int(days_until_overspend))
    else:
        return max(10, int(days_until_overspend))