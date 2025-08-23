"""
AI Service for campaign analysis and recommendations using LangChain and Gemini
"""

import os
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
from decimal import Decimal
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from app.core.config import settings
from app.services.monitoring.supabase_client import supabase_client
import uuid

# Set up logging
logger = logging.getLogger(__name__)

def convert_decimal_to_float(obj):
    """Convert non-JSON-serializable objects to JSON-serializable types"""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, uuid.UUID):
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: convert_decimal_to_float(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimal_to_float(item) for item in obj]
    elif hasattr(obj, '__dict__'):
        # Handle custom objects by converting to dict
        return convert_decimal_to_float(obj.__dict__)
    else:
        return obj


class AIService:
    """AI service for campaign analysis and recommendations"""
    
    def __init__(self):
        try:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash-lite",
                google_api_key=settings.GOOGLE_API_KEY,
                temperature=0.7,
                max_tokens=2048
                # Removed deprecated convert_system_message_to_human parameter
            )
            logger.info("✅ AI Service initialized successfully with Gemini")
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI Service: {e}")
            raise ValueError(f"Failed to initialize AI Service: {e}")
        
    async def analyze_campaign_data(self, user_id: str) -> Dict[str, Any]:
        """Analyze campaign data and generate AI insights"""
        
        # Get campaign data
        campaign_data = await self._get_campaign_data(user_id)
        
        # Get competitor data
        competitor_data = await self._get_competitor_data(user_id)
        
        # Get monitoring data
        monitoring_data = await self._get_monitoring_data(user_id)
        
        # Get risk calculation context (not old data, just the calculation logic)
        risk_context = await self._get_risk_calculation_context()
        
        # Generate AI analysis
        analysis = await self._generate_campaign_analysis(
            campaign_data, competitor_data, monitoring_data, risk_context
        )
        
        return analysis
    
    async def chat_with_ai(self, user_id: str, message: str) -> str:
        """Chat with AI about campaigns and business questions"""
        
        # Get relevant data based on the message
        campaign_data = await self._get_campaign_data(user_id)
        competitor_data = await self._get_competitor_data(user_id)
        monitoring_data = await self._get_monitoring_data(user_id)
        risk_context = await self._get_risk_calculation_context()
        
        # Generate response
        response = await self._generate_chat_response(
            message, campaign_data, competitor_data, monitoring_data, risk_context
        )
        
        return response
    
    async def _get_campaign_data(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Get campaign data from Supabase - all campaigns"""
        try:
            logger.info("🔍 Getting all campaign data from Supabase")
            
            if not supabase_client:
                logger.warning("⚠️ Supabase client not available, using sample data")
                return self._get_sample_campaign_data()
            
            # Query all campaign data from Supabase (no user_id filter)
            response = supabase_client.client.table('campaign_data').select('*').order('date', desc=True).limit(500).execute()
            
            if not response.data:
                logger.warning("⚠️ No campaigns found in database, using sample data")
                return self._get_sample_campaign_data()
            
            campaigns = []
            for row in response.data:
                campaign_dict = {
                    "name": row.get('name'),
                    "date": row.get('date'),
                    "impressions": row.get('impressions'),
                    "clicks": row.get('clicks'),
                    "ctr": row.get('ctr'),
                    "cpc": row.get('cpc'),
                    "spend": row.get('spend'),
                    "budget": row.get('budget'),
                    "conversions": row.get('conversions'),
                    "net_profit": row.get('net_profit'),
                    "ongoing": row.get('ongoing')
                }
                # Convert any non-JSON-serializable objects
                campaign_dict = convert_decimal_to_float(campaign_dict)
                campaigns.append(campaign_dict)
            
            logger.info(f"📋 Found {len(campaigns)} campaigns for analysis")
            return campaigns
            
        except Exception as e:
            logger.error(f"❌ Error getting campaign data: {e}")
            return self._get_sample_campaign_data()
    
    def _get_sample_campaign_data(self) -> List[Dict[str, Any]]:
        """Return sample campaign data when database is unavailable"""
        return [
            {
                "name": "HP Spectre X360",
                "date": "2025-07-11",
                "impressions": 551551,
                "clicks": 13946,
                "ctr": 2.57,
                "cpc": 1.57,
                "spend": 8582,
                "budget": 10000,
                "conversions": 245,
                "net_profit": -2347.18,
                "ongoing": "Yes"
            },
            {
                "name": "Tiger Beer Street Party",
                "date": "2025-05-02",
                "impressions": 455662,
                "clicks": 7008,
                "ctr": 1.54,
                "cpc": 1.67,
                "spend": 11703.36,
                "budget": 28968,
                "conversions": 1353,
                "net_profit": 4549.37,
                "ongoing": "No"
            }
        ]
    
    async def _get_competitor_data(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Get competitor data from Supabase - all active competitors"""
        try:
            logger.info("🔍 Getting all competitor data from Supabase")
            
            if not supabase_client:
                logger.warning("⚠️ Supabase client not available, using sample data")
                return self._get_sample_competitor_data()
            
            # Query all active competitor data from Supabase (no user_id filter)
            response = supabase_client.client.table('competitors').select('*').eq('status', 'active').limit(10).execute()
            
            if not response.data:
                logger.warning("⚠️ No competitors found in database, using sample data")
                return self._get_sample_competitor_data()
            
            competitor_data = []
            for row in response.data:
                competitor_dict = {
                    "name": row.get('name'),
                    "industry": row.get('industry'),
                    "website": row.get('website_url'),
                    "social_media": row.get('social_media_handles'),
                    "status": row.get('status')
                }
                # Convert any non-JSON-serializable objects
                competitor_dict = convert_decimal_to_float(competitor_dict)
                competitor_data.append(competitor_dict)
            
            logger.info(f"📊 Found {len(competitor_data)} competitors")
            return competitor_data
            
        except Exception as e:
            logger.error(f"❌ Error getting competitor data: {e}")
            return self._get_sample_competitor_data()
    
    def _get_sample_competitor_data(self) -> List[Dict[str, Any]]:
        """Return sample competitor data when database is unavailable"""
        return [
            {
                "name": "Apple",
                "industry": "Technology",
                "website": "https://apple.com",
                "social_media": {"youtube": "", "instagram": ""},
                "status": "active"
            },
            {
                "name": "Nike",
                "industry": "Sports & Fitness",
                "website": "nike.com",
                "social_media": {"instagram": "@nike", "youtube": "@nike"},
                "status": "active"
            }
        ]
    
    async def _get_monitoring_data(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Get monitoring data from Supabase - all monitoring data"""
        try:
            logger.info("🔍 Getting all monitoring data from Supabase")
            
            if not supabase_client:
                logger.warning("⚠️ Supabase client not available, using sample data")
                return self._get_sample_monitoring_data()
            
            # Query all monitoring data from Supabase (no user_id filter)
            response = supabase_client.client.table('monitoring_data').select('*').order('detected_at', desc=True).limit(20).execute()
            
            if not response.data:
                logger.warning("⚠️ No monitoring data found, using sample data")
                return self._get_sample_monitoring_data()
            
            monitoring_data = []
            for row in response.data:
                monitoring_dict = {
                    "platform": row.get('platform'),
                    "content": row.get('content_text'),
                    "engagement": row.get('engagement_metrics'),
                    "sentiment": row.get('sentiment_score'),
                    "posted_at": row.get('posted_at'),
                    "competitor_id": row.get('competitor_id')
                }
                # Convert any non-JSON-serializable objects
                monitoring_dict = convert_decimal_to_float(monitoring_dict)
                monitoring_data.append(monitoring_dict)
            
            logger.info(f"📊 Found {len(monitoring_data)} monitoring records")
            return monitoring_data
            
        except Exception as e:
            logger.error(f"❌ Error getting monitoring data: {e}")
            return self._get_sample_monitoring_data()
    
    def _get_sample_monitoring_data(self) -> List[Dict[str, Any]]:
        """Return sample monitoring data when database is unavailable"""
        return [
            {
                "platform": "Instagram",
                "content": "Competitor launched new product line",
                "engagement": {"likes": 150, "comments": 25, "shares": 10},
                "sentiment": 0.8,
                "posted_at": datetime.now().isoformat(),
                "competitor_id": "sample-1"
            },
            {
                "platform": "Facebook",
                "content": "Market trend: sustainability focus increasing",
                "engagement": {"likes": 89, "comments": 12, "shares": 5},
                "sentiment": 0.6,
                "posted_at": datetime.now().isoformat(),
                "competitor_id": "sample-2"
            }
        ]
    
    async def _get_risk_calculation_context(self) -> str:
        """Get risk calculation logic context (not old data)"""
        return """
        RISK CALCULATION METHODOLOGY:
        
        The system calculates risk scores using a weighted algorithm:
        
        1. Budget Utilization Risk (40% Weight):
        - Critical (95%+): 1.0 risk score
        - High (85-95%): 0.8 risk score  
        - Medium (75-85%): 0.6 risk score
        - Low (50-75%): 0.3 risk score
        - Safe (<50%): 0.0 risk score
        
        2. Profit Performance Risk (30% Weight):
        - Severe Loss (-20%+): 1.0 risk score
        - Significant Loss (-10% to -20%): 0.8 risk score
        - Loss (0% to -10%): 0.6 risk score
        - Low Profit (0% to 10%): 0.3 risk score
        - Good Profit (10%+): 0.0 risk score
        
        3. Performance Metrics Risk (20% Weight):
        - CTR < 1%: +0.5 risk
        - CTR 1-2%: +0.3 risk
        - CPC > $5: +0.5 risk
        - CPC $3-5: +0.3 risk
        - Conversion Rate < 1%: +0.5 risk
        - Conversion Rate 1-2%: +0.3 risk
        
        4. Spending Velocity Risk (10% Weight):
        - Extremely Rapid (<5 days): 1.0 risk score
        - Rapid (5-10 days): 0.8 risk score
        - Above Average (10-15 days): 0.5 risk score
        - Normal (>15 days): 0.0 risk score
        
        Final Risk Levels:
        - Critical Risk: 0.8+ (80%+ overall risk)
        - High Risk: 0.6-0.79 (60-79% overall risk)
        - Medium Risk: 0.4-0.59 (40-59% overall risk)
        - Low Risk: <0.4 (<40% overall risk)
        
        PERFORMANCE SCORE CALCULATION:
        
        Performance scores are calculated based on:
        - CTR performance (target: 2%+)
        - CPC efficiency (target: <$3)
        - Conversion rate (target: 1%+)
        - Profit margin (target: 10%+)
        - Budget utilization efficiency
        
        Each metric contributes to an overall performance score from 1-10.
        """
    
    async def _generate_campaign_analysis(
        self, 
        campaign_data: List[Dict[str, Any]], 
        competitor_data: List[Dict[str, Any]], 
        monitoring_data: List[Dict[str, Any]], 
        risk_context: str
    ) -> Dict[str, Any]:
        """Generate AI analysis of campaign data"""
        
        # Create prompt for campaign analysis (combine system and user prompt)
        try:
            campaign_data_json = json.dumps(convert_decimal_to_float(campaign_data), indent=2, default=str)
            competitor_data_json = json.dumps(convert_decimal_to_float(competitor_data), indent=2, default=str)
            monitoring_data_json = json.dumps(convert_decimal_to_float(monitoring_data), indent=2, default=str)
        except Exception as json_error:
            logger.error(f"JSON serialization error: {json_error}")
            # Fallback to string representation
            campaign_data_json = str(convert_decimal_to_float(campaign_data))
            competitor_data_json = str(convert_decimal_to_float(competitor_data))
            monitoring_data_json = str(convert_decimal_to_float(monitoring_data))
        
        combined_prompt = f"""You are an expert marketing AI analyst specializing in campaign optimization and performance analysis.

Please list any recommendation actions or optimization steps that can be taken to improve the performance of all my ongoing campaigns. Please summarize your recommendation actions into high priority and medium priority. Please give your response in a structured JSON output format.

**IMPORTANT**: 
- Focus ONLY on campaigns where ongoing = 'Yes' in the data
- Always mention specific campaign names from the data
- Provide actionable, specific recommendations with clear reasoning
- Use the exact JSON format specified below

Available REAL-TIME Data:
Campaign Data: {campaign_data_json}
Competitor Data: {competitor_data_json}
Market Monitoring: {monitoring_data_json}
Risk Calculation Context: {risk_context}

Please provide your response in this EXACT JSON format:

{{
  "recommendations": {{
    "high_priority": [
      {{
        "campaign_name": "Campaign Name Here",
        "action": "Specific actionable recommendation here",
        "reasoning": "Clear reasoning for why this action is needed and its expected impact"
      }}
    ],
    "medium_priority": [
      {{
        "campaign_name": "Campaign Name Here", 
        "action": "Specific actionable recommendation here",
        "reasoning": "Clear reasoning for why this action is needed and its expected impact"
      }}
    ]
  }}
}}

Only include campaigns where ongoing = 'Yes'. Categorize recommendations by priority based on potential impact and urgency."""
        
        try:
            # Use HumanMessage only (no SystemMessage)
            response = await self.llm.ainvoke([HumanMessage(content=combined_prompt)])
            
            # Try to parse JSON response
            json_recommendations = self._parse_json_recommendations(response.content)
            
            # Parse and structure the response
            analysis = {
                "timestamp": datetime.now().isoformat(),
                "insights": response.content,
                "recommendations": json_recommendations,
                "raw_response": response.content,  # Keep raw response for fallback
                "risk_alerts": self._extract_risk_alerts(response.content),
                "performance_score": self._extract_performance_score(response.content)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error generating AI analysis: {e}")
            logger.error(f"Error type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "timestamp": datetime.now().isoformat(),
                "insights": "Unable to generate AI analysis at this time.",
                "recommendations": [],
                "risk_alerts": [],
                "performance_score": 5
            }
    
    async def _generate_chat_response(
        self, 
        message: str, 
        campaign_data: List[Dict[str, Any]], 
        competitor_data: List[Dict[str, Any]], 
        monitoring_data: List[Dict[str, Any]], 
        risk_context: str
    ) -> str:
        """Generate AI chat response"""
        
        # Create combined prompt (no SystemMessage)
        try:
            campaign_data_json = json.dumps(convert_decimal_to_float(campaign_data), indent=2, default=str)
            competitor_data_json = json.dumps(convert_decimal_to_float(competitor_data), indent=2, default=str)
            monitoring_data_json = json.dumps(convert_decimal_to_float(monitoring_data), indent=2, default=str)
        except Exception as json_error:
            logger.error(f"JSON serialization error: {json_error}")
            # Fallback to string representation
            campaign_data_json = str(convert_decimal_to_float(campaign_data))
            competitor_data_json = str(convert_decimal_to_float(competitor_data))
            monitoring_data_json = str(convert_decimal_to_float(monitoring_data))
        
        combined_prompt = f"""You are an expert marketing AI assistant for a business operations system. 
 
 You have access to REAL-TIME data from:
 - Campaign performance data (from Supabase campaign_data table)
 - Competitor analysis
 - Market monitoring data
 - Risk calculation methodology
 
 Provide helpful, actionable advice about:
 - Campaign optimization
 - Budget management
 - Performance analysis
 - Competitive insights
 - Risk assessment
 - General marketing questions
 
 Be conversational but professional. Provide specific, actionable insights based on the REAL-TIME data available.
 
   **IMPORTANT**: When analyzing campaigns, always mention specific campaign names from the data (e.g., "Adidas Boost Launch", "CocaCola Refresh 2025", "Lazada Flash Sales 8.8"). This helps users understand which campaigns you're referring to. When asked about ongoing campaigns, focus specifically on campaigns where ongoing = 'Yes'.
  
  User Question: {message}
 
 Available REAL-TIME Data:
 Campaign Data: {campaign_data_json}
 Competitor Data: {competitor_data_json}
 Market Monitoring: {monitoring_data_json}
 Risk Calculation Context: {risk_context}
 
 Please provide a helpful, actionable response to the user's question based on the REAL-TIME data available. Always reference specific campaign names when discussing performance."""
        
        try:
            # Use HumanMessage only (no SystemMessage)
            response = await self.llm.ainvoke([HumanMessage(content=combined_prompt)])
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating chat response: {e}")
            logger.error(f"Error type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return "I'm sorry, I'm having trouble processing your request right now. Please try again later."
    
    def _extract_recommendations(self, content: str) -> List[str]:
        """Extract recommendations from AI response"""
        recommendations = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['recommend', 'suggest', 'should', 'consider', 'optimize']):
                if line and not line.startswith('#'):
                    recommendations.append(line)
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    def _extract_risk_alerts(self, content: str) -> List[str]:
        """Extract risk alerts from AI response"""
        alerts = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['risk', 'alert', 'warning', 'danger', 'critical']):
                if line and not line.startswith('#'):
                    alerts.append(line)
        
        return alerts[:3]  # Limit to 3 alerts
    
    def _extract_performance_score(self, content: str) -> int:
        """Extract performance score from AI response"""
        try:
            # Look for score patterns like "score: 8" or "8/10"
            import re
            score_patterns = [
                r'score[:\s]*(\d+)',
                r'(\d+)/10',
                r'performance[:\s]*(\d+)',
                r'health[:\s]*(\d+)'
            ]
            
            for pattern in score_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    score = int(match.group(1))
                    return max(1, min(10, score))  # Ensure score is between 1-10
            
            return 5  # Default score
        except:
            return 5

    def _parse_json_recommendations(self, content: str) -> Dict[str, Any]:
        """Parse JSON recommendations from AI response"""
        try:
            # Look for JSON content in the response
            import re
            
            # Find JSON block in response (between ```json and ``` or just { and })
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL | re.IGNORECASE)
            if not json_match:
                # Try to find JSON object directly
                json_match = re.search(r'(\{.*\})', content, re.DOTALL)
            
            if json_match:
                json_text = json_match.group(1)
                parsed_json = json.loads(json_text)
                
                # Validate structure
                if "recommendations" in parsed_json:
                    recommendations = parsed_json["recommendations"]
                    
                    # Ensure both priority levels exist
                    if "high_priority" not in recommendations:
                        recommendations["high_priority"] = []
                    if "medium_priority" not in recommendations:
                        recommendations["medium_priority"] = []
                    
                    # Validate each recommendation has required fields
                    for priority_level in ["high_priority", "medium_priority"]:
                        valid_recs = []
                        for rec in recommendations[priority_level]:
                            if isinstance(rec, dict) and all(key in rec for key in ["campaign_name", "action", "reasoning"]):
                                valid_recs.append(rec)
                        recommendations[priority_level] = valid_recs
                    
                    return recommendations
                else:
                    logger.warning("⚠️ JSON response missing 'recommendations' key")
                    return self._fallback_recommendations(content)
            else:
                logger.warning("⚠️ No JSON found in AI response")
                return self._fallback_recommendations(content)
                
        except json.JSONDecodeError as e:
            logger.warning(f"⚠️ JSON parsing error: {e}")
            return self._fallback_recommendations(content)
        except Exception as e:
            logger.warning(f"⚠️ Error parsing recommendations: {e}")
            return self._fallback_recommendations(content)
    
    def _fallback_recommendations(self, content: str) -> Dict[str, Any]:
        """Create fallback recommendations structure from plain text"""
        # Extract traditional recommendations and try to categorize them
        traditional_recs = self._extract_recommendations(content)
        
        # Simple heuristic: first half are high priority, second half are medium
        mid_point = len(traditional_recs) // 2 if len(traditional_recs) > 2 else 1
        
        high_priority = []
        medium_priority = []
        
        for i, rec in enumerate(traditional_recs):
            rec_dict = {
                "campaign_name": "General",
                "action": rec,
                "reasoning": "Extracted from AI analysis"
            }
            
            if i < mid_point or "critical" in rec.lower() or "urgent" in rec.lower():
                high_priority.append(rec_dict)
            else:
                medium_priority.append(rec_dict)
        
        return {
            "high_priority": high_priority,
            "medium_priority": medium_priority
        }


# Global AI service instance
try:
    ai_service = AIService()
    logger.info("✅ Global AI service instance created successfully")
except Exception as e:
    logger.error(f"❌ Failed to create global AI service instance: {e}")
    ai_service = None
