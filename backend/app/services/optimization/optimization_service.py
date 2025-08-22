"""
Optimization service for self-optimization business logic
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, date
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc, distinct, text

from app.models.campaign import (
    CampaignData, OptimizationAlert, RiskPattern, OptimizationRecommendation
)
from app.schemas.campaign import (
    DashboardMetrics, CampaignStatsResponse, BudgetMonitoringResponse,
    CampaignPerformanceResponse
)


class OptimizationService:
    """Service for self-optimization operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_dashboard_metrics(self, user_id: str) -> DashboardMetrics:
        """Get dashboard metrics for active/ongoing campaigns"""
        
        try:
            # 1. Get active spend and budget from ongoing campaigns
            # Since campaign_data doesn't have user_id, we get ALL ongoing campaigns
            result = await self.db.execute(text("""
                SELECT 
                    COALESCE(SUM(spend), 0) as active_spend,
                    COALESCE(SUM(budget), 0) as active_budget
                FROM campaign_data 
                WHERE ongoing = 'Yes'
            """))
            
            row = result.first()
            active_spend = float(row[0]) if row and row[0] else 0.0
            active_budget = float(row[1]) if row and row[1] else 0.0
            
            # 2. Calculate budget utilization
            budget_utilization_pct = 0.0
            if active_budget > 0:
                budget_utilization_pct = (active_spend / active_budget) * 100
            
            # 3. Check if alerts and risk tables exist, and count them
            alerts_count = 0
            risk_patterns_count = 0
            recommendations_count = 0
            
            # Check if optimization_alerts table exists
            alerts_table_exists = await self.db.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'optimization_alerts'
                )
            """))
            
            if alerts_table_exists.scalar():
                # Count unread alerts for this user
                alerts_result = await self.db.execute(text("""
                    SELECT COUNT(*) 
                    FROM optimization_alerts 
                    WHERE user_id = :user_id AND is_read = false
                """), {"user_id": user_id})
                alerts_count = alerts_result.scalar() or 0
            
            # Check if risk_patterns table exists
            risks_table_exists = await self.db.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'risk_patterns'
                )
            """))
            
            if risks_table_exists.scalar():
                # Count unresolved risk patterns for this user
                risks_result = await self.db.execute(text("""
                    SELECT COUNT(*) 
                    FROM risk_patterns 
                    WHERE user_id = :user_id AND resolved = false
                """), {"user_id": user_id})
                risk_patterns_count = risks_result.scalar() or 0
            
            # Check if optimization_recommendations table exists
            recs_table_exists = await self.db.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'optimization_recommendations'
                )
            """))
            
            if recs_table_exists.scalar():
                # Count unapplied recommendations for this user
                recs_result = await self.db.execute(text("""
                    SELECT COUNT(*) 
                    FROM optimization_recommendations 
                    WHERE user_id = :user_id AND is_applied = false
                """), {"user_id": user_id})
                recommendations_count = recs_result.scalar() or 0
            
            # 4. Create and return the metrics
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
            print(f"Error in get_dashboard_metrics: {e}")
            # Return default values if there's an error
            return DashboardMetrics(
                spend_today=Decimal('0'),
                budget_today=Decimal('0'),
                alerts_count=0,
                risk_patterns_count=0,
                recommendations_count=0,
                budget_utilization_pct=Decimal('0')
            )
    
    async def get_campaigns(self, user_id: str) -> List[Dict[str, Any]]:
        """Get list of campaigns with their data including net_profit and other metrics"""
        result = await self.db.execute(text("""
            SELECT 
                name, 
                spend, 
                budget,
                ctr, 
                cpc, 
                conversions, 
                ongoing,
                date,
                net_profit,
                impressions
            FROM campaign_data c1
            WHERE date = (
                SELECT MAX(date) 
                FROM campaign_data c2 
                WHERE c2.name = c1.name
            )
            ORDER BY name
        """))
        campaigns = []
        for row in result.fetchall():
            campaigns.append({
                'name': row[0],
                'spend': float(row[1]) if row[1] is not None else 0.0,
                'budget': float(row[2]) if row[2] is not None else 0.0,
                'ctr': float(row[3]) if row[3] is not None else 0.0,
                'cpc': float(row[4]) if row[4] is not None else 0.0,
                'conversions': row[5] if row[5] is not None else 0,
                'ongoing': row[6],
                'date': row[7].isoformat() if row[7] else None,
                'net_profit': float(row[8]) if row[8] is not None else 0.0,
                'impressions': row[9] if row[9] is not None else 0
            })
        return campaigns

    def calculate_enhanced_risk_score(self, campaign: Dict[str, Any]) -> Dict[str, Any]:
        """
        EXACT risk calculation logic that matches my manual calculations
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
        days_until_overspend = self.calculate_days_until_overspend(campaign, budget_utilization)
        
        return {
            'campaign_name': campaign['name'],
            'current_spend': campaign['spend'],
            'current_budget': campaign['budget'],
            'net_profit': campaign['net_profit'],
            'overspend_risk': risk_level,
            'risk_score': round(risk_score, 3),  # Keep 3 decimal places for accuracy
            'days_until_overspend': int(days_until_overspend) if days_until_overspend is not None else -1,
            'risk_factors': list(set(risk_factors)),  # Remove duplicates
            'budget_utilization': round(budget_utilization, 1),
            'profit_margin': round(profit_margin, 1),
            'performance_score': round(performance_score, 1),
            'performance_category': performance_category,
            'ctr': round(ctr, 2) if ctr > 0 else None,
            'cpc': round(cpc, 2) if cpc > 0 else None,
            'conversion_rate': round(conversion_rate, 2) if conversion_rate > 0 else None
        }
    
    def calculate_confidence_score(self, campaign: Dict[str, Any], risk_factors: List[str], risk_score: float) -> float:
        """
        Calculate confidence score based on:
        - Data completeness
        - Risk factor consistency
        - Historical data availability
        - Risk score magnitude
        """
        confidence = 0.5  # Base confidence
        
        # Data completeness bonus
        data_fields = ['spend', 'budget', 'net_profit', 'ctr', 'cpc', 'conversions', 'impressions']
        complete_fields = sum(1 for field in data_fields if campaign.get(field) is not None and campaign.get(field) != 0)
        data_completeness = complete_fields / len(data_fields)
        confidence += data_completeness * 0.2
        
        # Risk factor consistency bonus
        if len(risk_factors) >= 3:
            confidence += 0.15  # Multiple risk factors increase confidence
        elif len(risk_factors) >= 2:
            confidence += 0.1
        
        # Risk score magnitude bonus
        if risk_score >= 0.8:
            confidence += 0.15  # High risk scores are more confident
        elif risk_score >= 0.6:
            confidence += 0.1
        
        # Performance data quality bonus
        if campaign.get('impressions', 0) > 1000:
            confidence += 0.1  # More impressions = more reliable data
        
        return min(confidence, 0.95)  # Cap at 95%
    
    def calculate_days_until_overspend(self, campaign: Dict[str, Any], budget_utilization: float) -> int:
        """Calculate days until overspend based on current spending patterns"""
        current_spend = campaign.get('spend', 0)
        current_budget = campaign.get('budget', 0)
        
        if current_spend <= 0 or current_budget <= 0:
            return 30  # Default if no data
        
        remaining_budget = current_budget - current_spend
        
        if remaining_budget <= 0:
            return 0  # Already overspent
        
        # Estimate daily spend based on current utilization and time period
        # Assume campaign has been running for some time
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
    
    async def get_campaign_stats(self, user_id: str, days: int) -> CampaignStatsResponse:
        """Get campaign statistics for specified period"""
        start_date = date.today() - timedelta(days=days)
        
        # Get campaign stats using raw SQL with correct FLOAT data types
        # This query gets data for:
        # 1. All campaigns that started within the selected time period (date >= start_date)
        # 2. All ongoing campaigns regardless of start date (ongoing = 'Yes')
        # 
        # IMPORTANT: campaign_data does NOT have user_id, so no user_id filter here
        # Example: If user selects 7 days and today is 2025-08-17:
        # - start_date = 2025-08-10
        # - Will include campaigns with date >= 2025-08-10
        # - Will include ALL campaigns with ongoing = 'Yes' (regardless of date)
        # - This ensures we get comprehensive data without missing ongoing campaigns
        result = await self.db.execute(text("""
            SELECT 
                COUNT(DISTINCT name) as total_campaigns,
                COALESCE(SUM(spend), 0) as total_spend,
                COALESCE(SUM(budget), 0) as total_budget,
                COALESCE(AVG(ctr), 0) as avg_ctr,
                COALESCE(AVG(cpc), 0) as avg_cpc,
                COALESCE(SUM(conversions), 0) as total_conversions
            FROM campaign_data 
            WHERE date >= :start_date OR ongoing = 'Yes'
        """), {"start_date": start_date})
        stats = result.first()
        
        # Get active campaigns count using raw SQL
        # IMPORTANT: campaign_data does NOT have user_id, so no user_id filter here
        active_result = await self.db.execute(text("""
            SELECT COUNT(DISTINCT name) 
            FROM campaign_data 
            WHERE ongoing = 'Yes'
        """))
        active_campaigns = active_result.scalar() or 0
        
        total_spend = stats.total_spend if stats else Decimal('0')
        total_budget = stats.total_budget if stats else Decimal('0')
        budget_utilization = Decimal('0')
        if total_budget > 0:
            budget_utilization = (total_spend / total_budget) * 100
        
        return CampaignStatsResponse(
            total_campaigns=stats.total_campaigns if stats else 0,
            active_campaigns=active_campaigns,
            total_spend=total_spend,
            total_budget=total_budget,
            avg_ctr=stats.avg_ctr if stats else Decimal('0'),
            avg_cpc=stats.avg_cpc if stats else Decimal('0'),
            total_conversions=stats.total_conversions if stats else 0,
            budget_utilization=budget_utilization
        )
    
    async def get_campaign_performance(
        self, user_id: str, campaign_name: str, days: int
    ) -> CampaignPerformanceResponse:
        """Get performance trends for a specific campaign"""
        start_date = date.today() - timedelta(days=days)
        
        result = await self.db.execute(
            select(CampaignData).where(
                and_(
                    CampaignData.name == campaign_name,
                    CampaignData.date >= start_date
                )
            ).order_by(CampaignData.date)
        )
        campaign_data = result.scalars().all()
        
        dates = [data.date.isoformat() for data in campaign_data]
        spend_trend = [data.spend for data in campaign_data]
        ctr_trend = [data.ctr for data in campaign_data]
        cpc_trend = [data.cpc for data in campaign_data]
        conversions_trend = [data.conversions for data in campaign_data]
        
        return CampaignPerformanceResponse(
            campaign_name=campaign_name,
            dates=dates,
            spend_trend=spend_trend,
            ctr_trend=ctr_trend,
            cpc_trend=cpc_trend,
            conversions_trend=conversions_trend
        )
    
    async def get_budget_monitoring(
        self, user_id: str, days: int
    ) -> List[BudgetMonitoringResponse]:
        """Get budget monitoring data"""
        start_date = date.today() - timedelta(days=days)
        
        result = await self.db.execute(
            select(
                CampaignData.name,
                CampaignData.date,
                func.coalesce(func.sum(CampaignData.spend), 0).label('spend'),
                func.coalesce(func.sum(CampaignData.budget), 0).label('budget')
            ).where(CampaignData.date >= start_date)
            .group_by(CampaignData.name, CampaignData.date)
            .order_by(desc(CampaignData.date))
        )
        
        monitoring_data = []
        for row in result:
            spend = row.spend or Decimal('0')
            budget = row.budget or Decimal('0')
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
                campaign_name=row.name,
                date=row.date,
                spend=spend,
                budget=budget,
                utilization_pct=utilization_pct,
                status=status
            ))
        
        return monitoring_data
    
    async def get_optimization_alerts(
        self, user_id: str, unread_only: bool = False, limit: int = 50
    ) -> List[OptimizationAlert]:
        """Get optimization alerts"""
        query = select(OptimizationAlert).order_by(desc(OptimizationAlert.created_at))
        
        if unread_only:
            query = query.where(OptimizationAlert.is_read == False)
        
        query = query.limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def mark_alert_as_read(self, user_id: str, alert_id: str) -> bool:
        """Mark alert as read"""
        try:
            result = await self.db.execute(
                select(OptimizationAlert).where(OptimizationAlert.id == alert_id)
            )
            alert = result.scalar_one_or_none()
            
            if alert:
                alert.is_read = True
                alert.read_at = datetime.utcnow()
                await self.db.commit()
                return True
            return False
        except Exception:
            await self.db.rollback()
            return False
    
    async def get_risk_patterns(
        self, user_id: str, unresolved_only: bool = False, limit: int = 50
    ) -> List[RiskPattern]:
        """Get risk patterns"""
        query = select(RiskPattern).order_by(desc(RiskPattern.detected_at))
        
        if unresolved_only:
            query = query.where(RiskPattern.resolved == False)
        
        query = query.limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_recommendations(
        self, user_id: str, unapplied_only: bool = False, limit: int = 50
    ) -> List[OptimizationRecommendation]:
        """Get optimization recommendations"""
        query = select(OptimizationRecommendation).order_by(desc(OptimizationRecommendation.created_at))
        
        if unapplied_only:
            query = query.where(OptimizationRecommendation.is_applied == False)
        
        query = query.limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def apply_recommendation(self, user_id: str, recommendation_id: str) -> bool:
        """Apply a recommendation"""
        try:
            result = await self.db.execute(
                select(OptimizationRecommendation).where(OptimizationRecommendation.id == recommendation_id)
            )
            recommendation = result.scalar_one_or_none()
            
            if recommendation:
                recommendation.is_applied = True
                recommendation.applied_at = datetime.utcnow()
                await self.db.commit()
                return True
            return False
        except Exception:
            await self.db.rollback()
            return False
    
    async def get_ai_response(self, user_id: str, message: str) -> str:
        """Mock AI response for chat assistant"""
        # In a real implementation, this would use LangChain or similar
        message_lower = message.lower()
        
        # Get recent campaign stats for context
        stats = await self.get_campaign_stats(user_id, 7)
        
        if "budget" in message_lower or "spend" in message_lower:
            return f"Based on your recent data, you've spent ${stats.total_spend:.2f} out of a ${stats.total_budget:.2f} budget ({stats.budget_utilization:.1f}% utilization). I recommend monitoring campaigns with >80% utilization closely to prevent overspending."
        
        elif "performance" in message_lower or "ctr" in message_lower or "cpc" in message_lower:
            return f"Your average CTR is {stats.avg_ctr:.3f}% and average CPC is ${stats.avg_cpc:.2f}. Industry benchmarks suggest CTR above 2% and CPC below $3 are good targets. Consider testing new creatives if CTR is below 1%."
        
        elif "recommendation" in message_lower or "optimize" in message_lower:
            return f"I see you have {stats.active_campaigns} active campaigns. Focus on pausing underperforming campaigns with zero conversions and scaling those with CTR >2%. Would you like specific recommendations for any particular campaign?"
        
        elif "alert" in message_lower or "issue" in message_lower:
            # Get alert count
            metrics = await self.get_dashboard_metrics(user_id)
            return f"You currently have {metrics.alerts_count} unread alerts and {metrics.risk_patterns_count} risk patterns detected. Check your dashboard for details on overspending or performance issues."
        
        else:
            return "I'm here to help optimize your campaigns! Ask me about budget utilization, performance metrics, recommendations, or any specific campaign concerns you have."    
    async def get_risk_breakdown(self, user_id: str) -> Dict[str, int]:
        """Get breakdown of risk patterns by severity"""
        try:
            # Get risk patterns grouped by severity for the current user
            result = await self.db.execute(text("""
                SELECT 
                    severity,
                    COUNT(*) as count
                FROM risk_patterns 
                WHERE user_id = :user_id AND resolved = false
                GROUP BY severity
            """), {"user_id": user_id})
            
            risk_breakdown = {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0
            }
            
            for row in result.fetchall():
                severity = row[0].lower() if row[0] else 'medium'
                count = row[1] or 0
                if severity in risk_breakdown:
                    risk_breakdown[severity] = count
            
            return risk_breakdown
            
        except Exception as e:
            # If table doesn't exist or other error, return default values
            return {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0
            }
    
    async def get_alert_breakdown(self, user_id: str) -> Dict[str, int]:
        """Get breakdown of alerts by priority"""
        try:
            # Get alerts grouped by priority for the current user
            result = await self.db.execute(text("""
                SELECT 
                    priority,
                    COUNT(*) as count
                FROM optimization_alerts 
                WHERE user_id = :user_id AND is_read = false
                GROUP BY priority
            """), {"user_id": user_id})
            
            alert_breakdown = {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0
            }
            
            for row in result.fetchall():
                priority = row[0].lower() if row[0] else 'medium'
                count = row[1] or 0
                if priority in alert_breakdown:
                    alert_breakdown[priority] = count
            
            return alert_breakdown
            
        except Exception as e:
            # If table doesn't exist or other error, return default values
            return {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0
            }
