"""
AI Service for campaign analysis and recommendations using LangChain and Gemini
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
from sqlalchemy.orm import Session
from sqlalchemy import text
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from app.core.config import settings
from app.models.campaign import CampaignData
from app.models.competitor import Competitor
from app.models.monitoring import MonitoringData


class AIService:
    """AI service for campaign analysis and recommendations"""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.7,
            max_tokens=2048,
            convert_system_message_to_human=True  # Fix for SystemMessage compatibility
        )
        
    async def analyze_campaign_data(self, db: Session, user_id: str) -> Dict[str, Any]:
        """Analyze campaign data and generate AI insights"""
        
        # Get campaign data
        campaign_data = await self._get_campaign_data(db, user_id)
        
        # Get competitor data
        competitor_data = await self._get_competitor_data(db, user_id)
        
        # Get monitoring data
        monitoring_data = await self._get_monitoring_data(db, user_id)
        
        # Read README files for context
        readme_context = await self._get_readme_context()
        
        # Generate AI analysis
        analysis = await self._generate_campaign_analysis(
            campaign_data, competitor_data, monitoring_data, readme_context
        )
        
        return analysis
    
    async def chat_with_ai(self, db: Session, user_id: str, message: str) -> str:
        """Chat with AI about campaigns and business questions"""
        
        # Get relevant data based on the message
        campaign_data = await self._get_campaign_data(db, user_id)
        competitor_data = await self._get_competitor_data(db, user_id)
        monitoring_data = await self._get_monitoring_data(db, user_id)
        readme_context = await self._get_readme_context()
        
        # Generate response
        response = await self._generate_chat_response(
            message, campaign_data, competitor_data, monitoring_data, readme_context
        )
        
        return response
    
    async def _get_campaign_data(self, db: Session, user_id: str) -> List[Dict[str, Any]]:
        """Get campaign data from database"""
        try:
            print(f"🔍 Getting campaign data for user: {user_id}")
            print(f"🔍 Database session type: {type(db)}")
            
            # Direct query to get campaign data from Supabase
            query = text("""
                SELECT name, date, impressions, clicks, ctr, cpc, spend, budget, 
                       conversions, net_profit, ongoing
                FROM campaign_data 
                ORDER BY date DESC
                LIMIT 103
            """)
            
            print("🔍 Executing campaign data query...")
            print(f"🔍 Query: {query}")
            
            result = await db.execute(query)
            print(f"🔍 Query result type: {type(result)}")
            
            campaigns = []
            row_count = 0
            for row in result:
                row_count += 1
                campaigns.append({
                    "name": row.name,
                    "date": row.date.isoformat() if row.date else None,
                    "impressions": row.impressions,
                    "clicks": row.clicks,
                    "ctr": row.ctr,
                    "cpc": row.cpc,
                    "spend": row.spend,
                    "budget": row.budget,
                    "conversions": row.conversions,
                    "net_profit": row.net_profit,
                    "ongoing": row.ongoing
                })
                
                if row_count <= 3:
                    print(f"🔍 Sample row {row_count}: {row.name} - ongoing: {row.ongoing}")
            
            print(f"📋 Final result: {len(campaigns)} campaigns for analysis")
            
            # If no campaigns found, return empty list (no sample data)
            if not campaigns:
                print("⚠️  No campaigns found from database queries")
                return []
            
            return campaigns
            
        except Exception as e:
            print(f"❌ Error getting campaign data: {e}")
            return []
    
    async def _get_competitor_data(self, db: Session, user_id: str) -> List[Dict[str, Any]]:
        """Get competitor data from database"""
        try:
            print(f"🔍 Getting competitor data for user: {user_id}")
            
            # Direct query to get competitor data
            query = text("""
                SELECT name, industry, website_url, social_media_handles, status
                FROM competitors 
                WHERE status = 'active'
                LIMIT 10
            """)
            
            print("🔍 Executing competitor data query...")
            result = await db.execute(query)
            
            competitor_data = []
            for row in result:
                competitor_data.append({
                    "name": row.name,
                    "industry": row.industry,
                    "website": row.website_url,
                    "social_media": row.social_media_handles,
                    "status": row.status
                })
            
            print(f"📊 Found {len(competitor_data)} competitors")
            
            # If no competitors found, return sample data
            if not competitor_data:
                print("⚠️  No competitors found, using sample data")
                competitor_data = [
                    {
                        "name": "Nike",
                        "industry": "Sports & Fitness",
                        "website": "nike.com",
                        "social_media": "@nike",
                        "status": "active"
                    },
                    {
                        "name": "Adidas",
                        "industry": "Sports & Fitness",
                        "website": "adidas.com",
                        "social_media": "@adidas",
                        "status": "active"
                    }
                ]
            
            return competitor_data
        except Exception as e:
            print(f"❌ Error getting competitor data: {e}")
            return []
    
    async def _get_monitoring_data(self, db: Session, user_id: str) -> List[Dict[str, Any]]:
        """Get monitoring data from database"""
        try:
            print(f"🔍 Getting monitoring data for user: {user_id}")
            
            # Direct query to get monitoring data
            query = text("""
                SELECT platform, content_text, engagement_metrics, sentiment_score, 
                       posted_at, competitor_id
                FROM monitoring_data 
                ORDER BY posted_at DESC
                LIMIT 20
            """)
            
            print("🔍 Executing monitoring data query...")
            result = await db.execute(query)
            
            monitoring_data = []
            for row in result:
                monitoring_data.append({
                    "platform": row.platform,
                    "content": row.content_text,
                    "engagement": row.engagement_metrics,
                    "sentiment": row.sentiment_score,
                    "posted_at": row.posted_at.isoformat() if row.posted_at else None,
                    "competitor_id": row.competitor_id
                })
            
            print(f"📊 Found {len(monitoring_data)} monitoring records")
            
            # If no monitoring data found, return sample data
            if not monitoring_data:
                print("⚠️  No monitoring data found, using sample data")
                monitoring_data = [
                    {
                        "platform": "Instagram",
                        "content": "Competitor launched new product line",
                        "engagement": "High",
                        "sentiment": "Neutral",
                        "posted_at": datetime.now().isoformat(),
                        "competitor_id": 1
                    },
                    {
                        "platform": "Facebook",
                        "content": "Market trend: sustainability focus increasing",
                        "engagement": "Medium",
                        "sentiment": "Positive",
                        "posted_at": datetime.now().isoformat(),
                        "competitor_id": 2
                    }
                ]
            
            return monitoring_data
        except Exception as e:
            print(f"❌ Error getting monitoring data: {e}")
            return []
    
    async def _get_readme_context(self) -> str:
        """Read README files for context"""
        try:
            # Try different possible paths for README files
            possible_paths = [
                "",  # Current directory
                "../",  # Parent directory
                "../../",  # Two levels up
                "./backend/",  # Backend directory
                "./frontend/"  # Frontend directory
            ]
            
            readme_files = [
                "README.md",
                "BUDGET_OPTIMIZATION_FEATURES.md",
                "CAMPAIGN_PERFORMANCE_EXPLANATION.md",
                "ENHANCED_RISK_RANKING_EXPLANATION.md",
                "IMPLEMENTATION_SUMMARY.md",
                "SETUP_SUMMARY.md"
            ]
            
            context = ""
            files_found = 0
            
            for base_path in possible_paths:
                for filename in readme_files:
                    try:
                        file_path = os.path.join(base_path, filename)
                        if os.path.exists(file_path):
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                context += f"\n\n--- {filename} ---\n{content}"
                                files_found += 1
                                print(f"Successfully read: {file_path}")
                    except Exception as e:
                        print(f"Error reading {filename} from {base_path}: {e}")
                        continue
            
            print(f"Successfully read {files_found} README files for context")
            
            # If no files found, provide some basic context
            if not context:
                context = """
                Business Context: This is a Business Operations System (BOS) that provides:
                - Campaign performance tracking and optimization
                - Competitor intelligence and monitoring
                - Budget management and risk assessment
                - AI-powered insights and recommendations
                
                The system helps businesses optimize their marketing campaigns by analyzing performance data,
                monitoring competitors, and providing actionable recommendations for improvement.
                """
            
            return context
        except Exception as e:
            print(f"Error reading README files: {e}")
            return "Business Context: Marketing campaign optimization and competitor intelligence system."
    
    async def _generate_campaign_analysis(
        self, 
        campaign_data: List[Dict[str, Any]], 
        competitor_data: List[Dict[str, Any]], 
        monitoring_data: List[Dict[str, Any]], 
        readme_context: str
    ) -> Dict[str, Any]:
        """Generate AI analysis of campaign data"""
        
        # Create prompt for campaign analysis (combine system and user prompt)
        combined_prompt = f"""You are an expert marketing AI analyst specializing in campaign optimization and performance analysis. 
 
 Your task is to analyze campaign data and provide actionable insights and recommendations. Focus on:
 1. Performance trends and patterns
 2. Budget optimization opportunities
 3. Risk identification and mitigation
 4. Competitive analysis insights
 5. Specific actionable recommendations
 
   **IMPORTANT**: When analyzing campaigns, always mention specific campaign names from the data (e.g., "Adidas Boost Launch", "CocaCola Refresh 2025", "Lazada Flash Sales 8.8"). This helps users understand which campaigns you're referring to. When asked about ongoing campaigns, focus specifically on campaigns where ongoing = 'Yes'.
  
  Analyze the following campaign and market data to provide actionable insights:
 
 Campaign Data: {json.dumps(campaign_data, indent=2)}
 Competitor Data: {json.dumps(competitor_data, indent=2)}
 Market Monitoring: {json.dumps(monitoring_data, indent=2)}
 Business Context: {readme_context}
 
 Please provide:
 1. Key performance insights (3-5 bullet points) - mention specific campaign names
 2. Budget optimization recommendations (2-3 specific actions) - reference actual campaigns
 3. Risk alerts and mitigation strategies (if any) - identify specific campaigns at risk
 4. Competitive opportunities (2-3 actionable insights) - based on real campaign data
 5. Overall campaign health score (1-10) with reasoning
 
 Format your response as a structured analysis with clear sections and actionable recommendations. Always reference specific campaign names when discussing performance."""
        
        try:
            # Use HumanMessage only (no SystemMessage)
            response = await self.llm.ainvoke([HumanMessage(content=combined_prompt)])
            
            # Parse and structure the response
            analysis = {
                "timestamp": datetime.now().isoformat(),
                "insights": response.content,
                "recommendations": self._extract_recommendations(response.content),
                "risk_alerts": self._extract_risk_alerts(response.content),
                "performance_score": self._extract_performance_score(response.content)
            }
            
            return analysis
            
        except Exception as e:
            print(f"Error generating AI analysis: {e}")
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
        readme_context: str
    ) -> str:
        """Generate AI chat response"""
        
        # Create combined prompt (no SystemMessage)
        combined_prompt = f"""You are an expert marketing AI assistant for a business operations system. 
 
 You have access to:
 - Campaign performance data
 - Competitor analysis
 - Market monitoring data
 - Business documentation
 
 Provide helpful, actionable advice about:
 - Campaign optimization
 - Budget management
 - Performance analysis
 - Competitive insights
 - Risk assessment
 - General marketing questions
 
 Be conversational but professional. Provide specific, actionable insights based on the available data.
 
   **IMPORTANT**: When analyzing campaigns, always mention specific campaign names from the data (e.g., "Adidas Boost Launch", "CocaCola Refresh 2025", "Lazada Flash Sales 8.8"). This helps users understand which campaigns you're referring to. When asked about ongoing campaigns, focus specifically on campaigns where ongoing = 'Yes'.
  
  User Question: {message}
 
 Available Data:
 Campaign Data: {json.dumps(campaign_data, indent=2)}
 Competitor Data: {json.dumps(competitor_data, indent=2)}
 Market Monitoring: {json.dumps(monitoring_data, indent=2)}
 Business Context: {readme_context}
 
 Please provide a helpful, actionable response to the user's question based on the available data. Always reference specific campaign names when discussing performance."""
        
        try:
            # Use HumanMessage only (no SystemMessage)
            response = await self.llm.ainvoke([HumanMessage(content=combined_prompt)])
            return response.content
            
        except Exception as e:
            print(f"Error generating chat response: {e}")
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


# Global AI service instance
ai_service = AIService()
