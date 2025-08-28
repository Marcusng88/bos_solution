#!/usr/bin/env python3
"""
AI Agent for ROI Report Generation
Analyzes ROI metrics and generates HTML reports optimized for xhtml2pdf conversion
"""

import asyncio
import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import logging

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

try:
    import google.generativeai as genai
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.messages import HumanMessage,SystemMessage
    GOOGLE_GENAI_AVAILABLE = True
    print("✅ Google Generative AI available")
except ImportError:
    GOOGLE_GENAI_AVAILABLE = False
    print("❌ Google Generative AI not available")

from app.core.supabase_client import supabase_client
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ROIReportAgent:
    """
    AI Agent that analyzes ROI metrics and generates HTML reports
    """
    
    def __init__(self):
        self.google_genai_available = GOOGLE_GENAI_AVAILABLE
        self.model = None
        
        if self.google_genai_available:
            try:
                # Configure Google Generative AI
                genai.configure(api_key=settings.GOOGLE_API_KEY)
                self.model = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash-lite",
                    temperature=0.3,  # Very low temperature for highly consistent output
                    max_output_tokens=8192
                )
                logger.info("✅ Google Generative AI model initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Google Generative AI: {e}")
                self.google_genai_available = False
    
    async def generate_html_report(self) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        Main method to generate HTML report:
        1. Fetch ROI metrics data
        2. Analyze the data
        3. Generate HTML optimized for xhtml2pdf
        """
        try:
            logger.info("🚀 Starting HTML report generation...")
            logger.info(f"🤖 AI Model Available: {self.google_genai_available}")
            if self.google_genai_available:
                logger.info(f"🤖 Using: Gemini 2.5 Flash Lite (temperature=0.01)")
            else:
                logger.info("📋 Using: Template-based generation (fallback)")
            
            # Step 1: Fetch ROI metrics data
            logger.info("📊 Step 1: Fetching ROI metrics data...")
            roi_data = await self._fetch_roi_data()
            
            if not roi_data:
                logger.warning("⚠️ No ROI data found, using sample data")
                roi_data = self._get_sample_roi_data()
            
            # Step 2: Analyze ROI data
            logger.info("🔍 Step 2: Analyzing ROI data...")
            analysis = await self._analyze_roi_data(roi_data)
            
            # Step 3: Generate HTML report
            logger.info("📝 Step 3: Generating HTML report...")
            html_content = await self._generate_html_report(roi_data, analysis)
            
            if not html_content:
                raise Exception("Failed to generate HTML content")
            
            logger.info("✅ HTML report generation completed successfully!")
            logger.info(f"📊 Final HTML content: {len(html_content)} characters")
            logger.info(f"📈 Report data includes: {len(roi_data.get('platforms', {}))} platforms, {len(analysis)} analysis components")
            
            return html_content, {
                "roi_data": roi_data,
                "analysis": analysis,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ HTML report generation failed: {str(e)}")
            return None, None
    
    async def _fetch_roi_data(self) -> Optional[Dict[str, Any]]:
        """
        Fetch ROI metrics data from the database
        """
        try:
            logger.info("🔍 Fetching ROI metrics data from database...")
            
            # Query all ROI metrics data
            response = await supabase_client._make_request(
                "GET",
                "roi_metrics",
                params={
                    "select": "platform,views,likes,comments,shares,clicks,ad_spend,revenue_generated,roi_percentage,content_type,content_category,created_at",
                    "order": "created_at.desc",
                    "limit": "1000"
                }
            )
            
            if response.status_code != 200:
                logger.error(f"❌ Database query failed with status {response.status_code}")
                return None
            
            data = response.json()
            logger.info(f"✅ Retrieved {len(data)} ROI metrics records")
            
            # Process and structure the data
            processed_data = self._process_roi_data(data)
            return processed_data
            
        except Exception as e:
            logger.error(f"❌ Error fetching ROI data: {str(e)}")
            return None
    
    def _process_roi_data(self, raw_data: list) -> Dict[str, Any]:
        """
        Process raw ROI data into structured format
        """
        try:
            # Group by platform
            platforms = {}
            totals = {
                "total_views": 0,
                "total_likes": 0,
                "total_comments": 0,
                "total_shares": 0,
                "total_clicks": 0,
                "total_ad_spend": 0,
                "total_revenue": 0
            }
            
            for record in raw_data:
                platform = record.get("platform", "Unknown")
                
                if platform not in platforms:
                    platforms[platform] = {
                        "views": 0,
                        "likes": 0,
                        "comments": 0,
                        "shares": 0,
                        "clicks": 0,
                        "ad_spend": 0,
                        "revenue": 0,
                        "roi_percentage": 0,
                        "content_count": 0
                    }
                
                # Accumulate platform data
                platforms[platform]["views"] += int(record.get("views", 0))
                platforms[platform]["likes"] += int(record.get("likes", 0))
                platforms[platform]["comments"] += int(record.get("comments", 0))
                platforms[platform]["shares"] += int(record.get("shares", 0))
                platforms[platform]["clicks"] += int(record.get("clicks", 0))
                platforms[platform]["ad_spend"] += float(record.get("ad_spend", 0))
                platforms[platform]["revenue"] += float(record.get("revenue_generated", 0))
                platforms[platform]["content_count"] += 1
                
                # Accumulate totals
                totals["total_views"] += int(record.get("views", 0))
                totals["total_likes"] += int(record.get("likes", 0))
                totals["total_comments"] += int(record.get("comments", 0))
                totals["total_shares"] += int(record.get("shares", 0))
                totals["total_clicks"] += int(record.get("clicks", 0))
                totals["total_ad_spend"] += float(record.get("ad_spend", 0))
                totals["total_revenue"] += float(record.get("revenue_generated", 0))
            
            # Calculate ROI percentages for platforms
            for platform_data in platforms.values():
                if platform_data["ad_spend"] > 0:
                    platform_data["roi_percentage"] = (
                        (platform_data["revenue"] - platform_data["ad_spend"]) / 
                        platform_data["ad_spend"]
                    ) * 100
                else:
                    platform_data["roi_percentage"] = 0
            
            # Calculate overall ROI
            overall_roi = 0
            if totals["total_ad_spend"] > 0:
                overall_roi = (
                    (totals["total_revenue"] - totals["total_ad_spend"]) / 
                    totals["total_ad_spend"]
                ) * 100
            
            return {
                "platforms": platforms,
                "totals": totals,
                "overall_roi": overall_roi,
                "record_count": len(raw_data),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing ROI data: {str(e)}")
            return {}
    
    def _format_number(self, value: float) -> str:
        """
        Format large numbers using scientific notation (K, M, B)
        """
        if value >= 1_000_000_000:
            return f"{value / 1_000_000_000:.1f}B"
        elif value >= 1_000_000:
            return f"{value / 1_000_000:.1f}M"
        elif value >= 1_000:
            return f"{value / 1_000:.1f}K"
        else:
            return f"{value:.0f}"
    
    def _format_currency(self, value: float) -> str:
        """
        Format currency values using scientific notation
        """
        if value >= 1_000_000_000:
            return f"${value / 1_000_000_000:.1f}B"
        elif value >= 1_000_000:
            return f"${value / 1_000_000:.1f}M"
        elif value >= 1_000:
            return f"${value / 1_000:.1f}K"
        else:
            return f"${value:.0f}"
    
    def _get_sample_roi_data(self) -> Dict[str, Any]:
        """
        Return sample ROI data for testing/demo purposes
        """
        return {
            "platforms": {
                "Facebook": {
                    "views": 15000,
                    "likes": 1200,
                    "comments": 300,
                    "shares": 150,
                    "clicks": 800,
                    "ad_spend": 2500.0,
                    "revenue": 4500.0,
                    "roi_percentage": 80.0,
                    "content_count": 25
                },
                "Instagram": {
                    "views": 22000,
                    "likes": 1800,
                    "comments": 450,
                    "shares": 220,
                    "clicks": 1200,
                    "ad_spend": 3200.0,
                    "revenue": 5800.0,
                    "roi_percentage": 81.25,
                    "content_count": 30
                },
                "Google Ads": {
                    "views": 8000,
                    "likes": 0,
                    "comments": 0,
                    "shares": 0,
                    "clicks": 600,
                    "ad_spend": 1500.0,
                    "revenue": 2800.0,
                    "roi_percentage": 86.67,
                    "content_count": 15
                }
            },
            "totals": {
                "total_views": 45000,
                "total_likes": 3000,
                "total_comments": 750,
                "total_shares": 370,
                "total_clicks": 2600,
                "total_ad_spend": 7200.0,
                "total_revenue": 13100.0
            },
            "overall_roi": 81.94,
            "record_count": 70,
            "generated_at": datetime.now().isoformat()
        }
    
    async def _analyze_roi_data(self, roi_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze ROI data and generate insights
        """
        try:
            logger.info("🔍 Analyzing ROI data...")
            
            if not self.google_genai_available:
                logger.warning("⚠️ Google Generative AI not available, using basic analysis")
                return self._basic_roi_analysis(roi_data)
            
            # Create analysis prompt
            analysis_prompt = self._create_analysis_prompt(roi_data)
            
            # Generate analysis using AI
            messages = [
                SystemMessage(content="You are an expert marketing analyst specializing in ROI analysis. Provide clear, actionable insights based on the data provided."),
                HumanMessage(content=analysis_prompt)
            ]
            
            response = await self.model.ainvoke(messages)
            analysis_text = response.content
            
            # Parse the analysis response
            analysis = self._parse_ai_analysis(analysis_text, roi_data)
            
            logger.info("✅ ROI data analysis completed")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing ROI data: {str(e)}")
            return self._basic_roi_analysis(roi_data)
    
    def _create_analysis_prompt(self, roi_data: Dict[str, Any]) -> str:
        """
        Create a comprehensive marketing-focused prompt for ROI analysis
        """
        return f"""
        You are a senior marketing strategist and ROI optimization expert. Analyze the following comprehensive marketing ROI data and provide strategic insights that would be valuable for C-level executives and marketing directors.

        COMPREHENSIVE ROI DATA ANALYSIS:

        OVERALL PERFORMANCE METRICS:
        - Overall ROI: {roi_data.get('overall_roi', 0):.2f}%
        - Total Revenue Generated: ${roi_data.get('totals', {}).get('total_revenue', 0):,.2f}
        - Total Marketing Investment: ${roi_data.get('totals', {}).get('total_ad_spend', 0):,.2f}
        - Net Profit: ${roi_data.get('totals', {}).get('total_revenue', 0) - roi_data.get('totals', {}).get('total_ad_spend', 0):,.2f}
        - Total Reach: {roi_data.get('totals', {}).get('total_views', 0):,} impressions
        - Total Engagement: {roi_data.get('totals', {}).get('total_clicks', 0):,} clicks
        - Engagement Rate: {(roi_data.get('totals', {}).get('total_clicks', 0) / max(roi_data.get('totals', {}).get('total_views', 1), 1)) * 100:.2f}%

        PLATFORM PERFORMANCE BREAKDOWN:
        {json.dumps(roi_data.get('platforms', {}), indent=2)}

        CONTENT PERFORMANCE INDICATORS:
        - Total Social Interactions: {roi_data.get('totals', {}).get('total_likes', 0) + roi_data.get('totals', {}).get('total_comments', 0) + roi_data.get('totals', {}).get('total_shares', 0):,}
        - Social Engagement Rate: {((roi_data.get('totals', {}).get('total_likes', 0) + roi_data.get('totals', {}).get('total_comments', 0) + roi_data.get('totals', {}).get('total_shares', 0)) / max(roi_data.get('totals', {}).get('total_views', 1), 1)) * 100:.2f}%
        - Cost per Click: ${roi_data.get('totals', {}).get('total_ad_spend', 0) / max(roi_data.get('totals', {}).get('total_clicks', 1), 1):.2f}
        - Revenue per Click: ${roi_data.get('totals', {}).get('total_revenue', 0) / max(roi_data.get('totals', {}).get('total_clicks', 1), 1):.2f}

        REQUIRED ANALYSIS COMPONENTS:

        1. EXECUTIVE SUMMARY (3-4 sentences):
           - High-level performance assessment
           - Key financial impact
           - Strategic positioning

        2. COMPREHENSIVE PERFORMANCE INSIGHTS (5-6 detailed points):
           - ROI performance analysis
           - Platform effectiveness comparison
           - Content engagement patterns
           - Cost efficiency metrics
           - Market penetration insights
           - Competitive positioning
                       **(For the platform performance analysis table, use scientific notation for ALL metrics instead of writing out the full numbers. For example: 115.9M views, 132.6M likes, $145.5M ad spend, etc.)**

        3. PLATFORM STRATEGY ANALYSIS:
           - Top performing platform with detailed reasoning
           - Platform-specific ROI breakdown
           - Cross-platform synergy opportunities
           - Platform-specific optimization recommendations

        4. STRATEGIC OPPORTUNITIES (4-5 actionable items):
           - Budget reallocation strategies
           - Content optimization opportunities
           - Targeting improvements
           - Performance scaling strategies
           - Risk mitigation approaches

        5. COMPETITIVE INTELLIGENCE INSIGHTS:
           - Market positioning analysis
           - Benchmark performance assessment
           - Competitive advantage identification
           - Market share opportunities

        6. RISK ASSESSMENT & MITIGATION:
           - Current risk factors
           - Potential threats
           - Mitigation strategies
           - Contingency planning

        7. FUTURE ROADMAP RECOMMENDATIONS:
           - Short-term optimizations (30-60 days)
           - Medium-term strategies (3-6 months)
           - Long-term strategic initiatives (6-12 months)
           - Investment priorities

        Format your response as JSON with these keys:
        {{
            "executive_summary": "comprehensive executive summary",
            "key_insights": ["detailed insight 1", "detailed insight 2", "detailed insight 3", "detailed insight 4", "detailed insight 5"],
            "top_performer": "platform name with reasoning",
            "platform_analysis": "detailed platform strategy analysis",
            "strategic_opportunities": ["opportunity 1", "opportunity 2", "opportunity 3", "opportunity 4"],
            "competitive_intelligence": "market positioning and competitive analysis",
            "risk_assessment": "comprehensive risk analysis with mitigation strategies",
            "future_roadmap": "strategic roadmap with timelines and priorities",
            "financial_impact": "projected financial impact of recommendations"
        }}

        Provide analysis that demonstrates deep marketing expertise, strategic thinking, and actionable business intelligence. Focus on insights that drive business growth and competitive advantage.
        """
    
    def _parse_ai_analysis(self, analysis_text: str, roi_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse AI-generated comprehensive analysis response
        """
        try:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            
            if json_match:
                parsed = json.loads(json_match.group())
                
                # Ensure all required fields are present
                required_fields = [
                    "executive_summary", "key_insights", "top_performer", 
                    "platform_analysis", "strategic_opportunities", 
                    "competitive_intelligence", "risk_assessment", 
                    "future_roadmap", "financial_impact"
                ]
                
                missing_fields = [field for field in required_fields if field not in parsed]
                if missing_fields:
                    logger.warning(f"⚠️ AI analysis missing fields: {missing_fields}, using basic analysis for missing parts")
                    basic_analysis = self._basic_roi_analysis(roi_data)
                    
                    # Fill in missing fields with basic analysis
                    for field in missing_fields:
                        if field in basic_analysis:
                            parsed[field] = basic_analysis[field]
                
                return parsed
            else:
                # Fallback to basic analysis
                logger.warning("⚠️ Could not parse AI analysis, using basic analysis")
                return self._basic_roi_analysis(roi_data)
                
        except Exception as e:
            logger.error(f"❌ Error parsing AI analysis: {str(e)}")
            return self._basic_roi_analysis(roi_data)
    
    def _basic_roi_analysis(self, roi_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive basic ROI analysis when AI is not available
        """
        platforms = roi_data.get("platforms", {})
        totals = roi_data.get("totals", {})
        overall_roi = roi_data.get("overall_roi", 0)
        
        # Calculate additional metrics
        net_profit = totals.get("total_revenue", 0) - totals.get("total_ad_spend", 0)
        engagement_rate = (totals.get("total_clicks", 0) / max(totals.get("total_views", 1), 1)) * 100
        social_engagement = totals.get("total_likes", 0) + totals.get("total_comments", 0) + totals.get("total_shares", 0)
        cost_per_click = totals.get("total_ad_spend", 0) / max(totals.get("total_clicks", 1), 1)
        revenue_per_click = totals.get("total_revenue", 0) / max(totals.get("total_clicks", 1), 1)
        
        # Find top performing platform
        top_performer = max(platforms.items(), key=lambda x: x[1].get("roi_percentage", 0))[0] if platforms else "None"
        
        # Comprehensive insights
        insights = []
        if overall_roi > 100:
            insights.append("Exceptional ROI performance exceeding 100% - marketing investment is generating exceptional returns")
        elif overall_roi > 50:
            insights.append("Strong ROI performance above 50% - marketing strategy is effectively driving revenue growth")
        elif overall_roi > 0:
            insights.append("Positive ROI performance - marketing efforts are generating profitable returns")
        else:
            insights.append("Negative ROI detected - immediate strategic review and optimization required")
        
        if totals.get("total_views", 0) > 10000:
            insights.append("High reach with significant market penetration - brand visibility is strong")
        
        if totals.get("total_clicks", 0) > 1000:
            insights.append("Effective click-through rates indicating strong audience targeting and compelling content")
        
        if engagement_rate > 5:
            insights.append("Above-average engagement rates suggest high-quality content and strong audience connection")
        
        if cost_per_click < 2.0:
            insights.append("Cost-efficient click acquisition - advertising spend is well-optimized")
        
        if revenue_per_click > 10.0:
            insights.append("High revenue per click indicates strong conversion optimization and valuable audience")
        
        # Platform analysis
        platform_analysis = f"Platform performance analysis shows {top_performer} as the top performer with {platforms.get(top_performer, {}).get('roi_percentage', 0):.1f}% ROI. "
        if len(platforms) > 1:
            platform_analysis += f"Cross-platform strategy is generating {overall_roi:.1f}% combined ROI, indicating effective multi-channel marketing approach."
        
        # Strategic opportunities
        opportunities = []
        if overall_roi > 0:
            opportunities.append("Scale successful campaigns to increase overall marketing ROI")
            opportunities.append("Optimize underperforming platforms through A/B testing and targeting improvements")
            opportunities.append("Increase budget allocation to top-performing platforms and content types")
            opportunities.append("Implement advanced attribution modeling for better ROI optimization")
        
        # Competitive intelligence
        competitive_intelligence = f"Current ROI of {overall_roi:.1f}% positions the business competitively. "
        if overall_roi > 50:
            competitive_intelligence += "Performance exceeds industry benchmarks, providing competitive advantage."
        elif overall_roi > 20:
            competitive_intelligence += "Performance is competitive with room for optimization."
        else:
            competitive_intelligence += "Performance requires improvement to maintain market competitiveness."
        
        # Risk assessment
        risk_assessment = "Low risk" if overall_roi > 20 else "Medium risk" if overall_roi > 0 else "High risk - negative ROI requires immediate attention"
        
        # Future roadmap
        future_roadmap = "Short-term: Optimize underperforming campaigns. Medium-term: Scale successful strategies. Long-term: Implement advanced marketing automation and AI-driven optimization."
        
        # Financial impact
        financial_impact = f"Optimization recommendations could potentially increase ROI by 15-25%, translating to {self._format_currency(net_profit * 0.2)} additional profit with current spend levels."
        
        return {
            "executive_summary": f"Marketing ROI performance is {overall_roi:.1f}% with {self._format_currency(totals.get('total_revenue', 0))} in revenue from {self._format_currency(totals.get('total_ad_spend', 0))} in marketing investment, generating {self._format_currency(net_profit)} in net profit. The strategy demonstrates {'exceptional' if overall_roi > 100 else 'strong' if overall_roi > 50 else 'positive' if overall_roi > 0 else 'concerning'} performance with significant opportunities for optimization.",
            "key_insights": insights,
            "top_performer": top_performer,
            "platform_analysis": platform_analysis,
            "strategic_opportunities": opportunities,
            "competitive_intelligence": competitive_intelligence,
            "risk_assessment": risk_assessment,
            "future_roadmap": future_roadmap,
            "financial_impact": financial_impact,
            "overall_roi": overall_roi,
            "net_profit": net_profit,
            "total_reach": totals.get("total_views", 0),
            "total_engagement": social_engagement,
            "total_clicks": totals.get("total_clicks", 0),
            "total_revenue": totals.get("total_revenue", 0)
        }
    
    async def _generate_html_report(self, roi_data: Dict[str, Any], analysis: Dict[str, Any]) -> Optional[str]:
        """
        Generate HTML report optimized for xhtml2pdf conversion
        """
        try:
            logger.info("📝 Starting HTML report generation...")
            
            if not self.google_genai_available:
                logger.warning("⚠️ Google Generative AI not available, using template-based generation")
                logger.info("🔄 Generating HTML using FALLBACK TEMPLATE method...")
                template_html = self._generate_template_html(roi_data, analysis)
                logger.info("✅ HTML report generated successfully using TEMPLATE method")
                return template_html
            
            logger.info("🤖 Google Generative AI available, attempting AI-powered HTML generation...")
            
            # Create HTML generation prompt
            html_prompt = self._create_html_generation_prompt(roi_data, analysis)
            logger.info("📋 AI prompt created, invoking Gemini model...")
            
            # Generate HTML using AI
            messages = [
                SystemMessage(content="You are a specialized coding agent that generates HTML/CSS optimized for xhtml2pdf conversion. Follow strict guidelines to ensure professional, readable PDF output."),
                HumanMessage(content=html_prompt)
            ]
            
            logger.info("🚀 Invoking AI model (Gemini 2.5 Flash Lite) with temperature=0.01...")
            response = await self.model.ainvoke(messages)
            html_content = response.content
            
            logger.info(f"🤖 AI model response received: {len(html_content)} characters")
            
            # Clean up the HTML content
            logger.info("🧹 Cleaning and validating AI-generated HTML content...")
            html_content = self._clean_html_content(html_content)
            
            if not html_content or len(html_content) < 100:
                logger.warning("⚠️ AI-generated HTML too short or invalid, falling back to template-based generation")
                logger.info("🔄 Generating HTML using FALLBACK TEMPLATE method...")
                template_html = self._generate_template_html(roi_data, analysis)
                logger.info("✅ HTML report generated successfully using TEMPLATE method (fallback)")
                return template_html
            
            logger.info("✅ HTML report generated successfully using AI method (Gemini 2.5 Flash Lite)")
            return html_content
            
        except Exception as e:
            logger.error(f"❌ Error during AI HTML generation: {str(e)}")
            logger.info("🔄 Falling back to template-based generation due to AI error...")
            template_html = self._generate_template_html(roi_data, analysis)
            logger.info("✅ HTML report generated successfully using TEMPLATE method (error fallback)")
            return template_html
    
    def _create_html_generation_prompt(self, roi_data: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """
        Create a prompt for HTML generation optimized for xhtml2pdf with landscape orientation
        """
        return f"""
        Generate a professional HTML report for ROI marketing data optimized for xhtml2pdf conversion with LANDSCAPE orientation.

        ROI Data:
        {json.dumps(roi_data, indent=2)}

        Analysis:
        {json.dumps(analysis, indent=2)}

        CRITICAL REQUIREMENTS FOR PORTRAIT LAYOUT:
        1. Design for PORTRAIT orientation (taller than wide)
        2. Use ONLY HTML and CSS that xhtml2pdf supports
        3. NO JavaScript, external fonts, or complex CSS
        4. Use inline CSS for styling
        5. Optimize for portrait PDF output (A4 portrait page size)
        6. Layout should utilize the vertical format effectively
        7. Include professional styling with tables, charts, and metrics
        8. Make it visually appealing but simple enough for PDF conversion

        PORTRAIT LAYOUT OPTIMIZATION:
        - Use vertical layouts and stacked content for better readability
        - Tables should be designed to fit portrait orientation
        - Charts and metrics should be arranged vertically when possible
        - Content should flow naturally in portrait format
        - Ensure all content fits within portrait page dimensions

        xhtml2pdf Limitations:
        - Limited CSS support (mostly CSS 2.1)
        - No JavaScript
        - No external resources
        - Limited font support
        - Portrait orientation support

        STRUCTURE REQUIREMENTS:
        - Executive Summary at the top
        - Key Performance Metrics in vertical grid layout
        - Platform Performance Analysis in tables with scientific notation (K, M, B for large numbers)
        - Strategic Insights in organized sections
        - Recommendations and Roadmap in clear format
        - Professional business report styling

        CRITICAL FORMATTING REQUIREMENTS:
        - Use scientific notation for all large numbers in tables (e.g., 23M instead of 23,000,000)
        - Format currency values with $ and scientific notation (e.g., $145.5M instead of $145,500,000)
        - Ensure all metrics in the platform performance table are clearly visible and readable
        - Use consistent formatting across all numerical data

        Output ONLY the complete HTML document with embedded CSS optimized for portrait layout. No explanations or markdown.
        """
    
    def _clean_html_content(self, html_content: str) -> str:
        """
        Clean and validate HTML content
        """
        # Remove markdown code blocks
        import re
        html_content = re.sub(r'```html\s*', '', html_content)
        html_content = re.sub(r'```\s*$', '', html_content)
        
        # Ensure it starts with <!DOCTYPE html>
        if not html_content.strip().startswith('<!DOCTYPE html'):
            html_content = f'<!DOCTYPE html>\n<html>\n<head>\n<meta charset="UTF-8">\n<title>ROI Report</title>\n</head>\n<body>\n{html_content}\n</body>\n</html>'
        
        return html_content
    
    def _generate_template_html(self, roi_data: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """
        Generate HTML using a template when AI is not available
        """
        logger.info("📋 Generating HTML using TEMPLATE method...")
        logger.info(f"📊 Template data: {len(roi_data.get('platforms', {}))} platforms, overall ROI: {roi_data.get('overall_roi', 0):.2f}%")
        
        platforms = roi_data.get("platforms", {})
        totals = roi_data.get("totals", {})
        overall_roi = roi_data.get("overall_roi", 0)
        
        # Create a portrait-optimized professional HTML template with enhanced metrics
        logger.info("🏗️ Building HTML template with scientific notation formatting...")
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ROI Performance Report - Portrait</title>
    <style>
        /* Base styles for screen and print */
        * {{
            box-sizing: border-box;
        }}
        
        body {{
            font-family: Arial, Helvetica, sans-serif;
            margin: 0;
            padding: 15px;
            background-color: #f5f5f5;
            color: #333;
            line-height: 1.4;
            max-width: 800px;
            margin: 0 auto;
        }}
        
        .container {{
            width: 100%;
            background-color: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .header {{
            text-align: center;
            border-bottom: 3px solid #007bff;
            padding-bottom: 15px;
            margin-bottom: 25px;
            page-break-after: avoid;
        }}
        
        .header h1 {{
            color: #007bff;
            margin: 0;
            font-size: 28px;
            font-weight: bold;
        }}
        
        .header p {{
            font-size: 16px;
            color: #6c757d;
            margin: 5px 0 0 0;
        }}
        
        /* Portrait-optimized metrics grid */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 25px;
            page-break-inside: avoid;
        }}
        
        .metric-card {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid #007bff;
            height: 100%;
        }}
        
        .metric-value {{
            font-size: 28px;
            font-weight: bold;
            color: #007bff;
            display: block;
            margin-bottom: 8px;
            line-height: 1.2;
        }}
        
        .metric-label {{
            color: #6c757d;
            font-size: 14px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .metric-subtitle {{
            color: #6b7280;
            font-size: 12px;
            margin-top: 5px;
        }}
        
        /* Portrait-optimized content layout */
        .content-sections {{
            display: block;
            margin-bottom: 20px;
            page-break-inside: avoid;
        }}
        
        .section {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #28a745;
            margin-bottom: 20px;
        }}
        
        .section h3 {{
            color: #0056b3;
            margin-top: 0;
            margin-bottom: 15px;
            font-size: 18px;
            font-weight: bold;
        }}
        
        .platform-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 15px;
            font-size: 14px;
            page-break-inside: avoid;
        }}
        
        .platform-table th, .platform-table td {{
            border: 1px solid #dee2e6;
            padding: 10px 8px;
            text-align: left;
            vertical-align: top;
        }}
        
        .platform-table th {{
            background-color: #007bff;
            color: white;
            font-weight: bold;
        }}
        
        .platform-table tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        
        .insights-section {{
            background-color: #e7f3ff;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 25px;
            page-break-inside: avoid;
        }}
        
        .insights-section h3 {{
            color: #0056b3;
            margin-top: 0;
            font-weight: bold;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 25px;
            padding-top: 15px;
            border-top: 1px solid #dee2e6;
            color: #6c757d;
            page-break-before: avoid;
        }}
        
        /* Executive summary styling */
        .executive-summary {{
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 25px;
            page-break-inside: avoid;
        }}
        
        .executive-summary h2 {{
            color: #856404;
            margin-top: 0;
            font-size: 20px;
            font-weight: bold;
        }}
        
        .executive-summary p {{
            color: #856404;
            font-size: 16px;
            line-height: 1.5;
            margin: 0;
        }}
        
        /* Print-specific styles */
        @media print {{
            body {{
                background-color: white !important;
                padding: 0 !important;
            }}
            
            .container {{
                box-shadow: none !important;
                padding: 15px !important;
                border-radius: 0 !important;
            }}
            
            .metrics-grid, .content-sections {{
                page-break-inside: avoid !important;
            }}
            
            .section, .insights-section, .executive-summary {{
                page-break-inside: avoid !important;
                background-color: white !important;
                border: 1px solid #ddd !important;
            }}
            
            .metric-card {{
                background-color: white !important;
                border: 1px solid #ddd !important;
            }}
            
            .platform-table th {{
                background-color: #f0f0f0 !important;
                color: #333 !important;
            }}
            
            .platform-table tr:nth-child(even) {{
                background-color: #f9f9f9 !important;
            }}
        }}
        
        /* xhtml2pdf compatibility styles */
        .metrics-grid {{
            display: block;
        }}
        
        .metrics-grid > div {{
            display: inline-block;
            width: 32%;
            margin-right: 1%;
            vertical-align: top;
        }}
        
        .metrics-grid > div:last-child {{
            margin-right: 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>ROI Performance Report</h1>
            <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        
        <!-- Executive Summary Section -->
        <div class="executive-summary">
            <h2>Executive Summary</h2>
            <p>{analysis.get('executive_summary', 'Comprehensive ROI analysis of marketing performance across all platforms.')}</p>
        </div>
        
        <!-- Portrait-optimized metrics grid with enhanced formatting -->
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{self._format_number(overall_roi)}%</div>
                <div class="metric-label">Overall ROI</div>
                <div class="metric-subtitle">Performance</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{self._format_currency(totals.get('total_revenue', 0))}</div>
                <div class="metric-label">Total Revenue</div>
                <div class="metric-subtitle">Generated</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{self._format_number(totals.get('total_views', 0))}</div>
                <div class="metric-label">Total Views</div>
                <div class="metric-subtitle">Reach</div>
            </div>
        </div>
        
        <!-- Portrait-optimized content sections -->
        <div class="content-sections">
            <div class="section">
                <h3>Platform Performance</h3>
                <table class="platform-table">
                    <thead>
                        <tr>
                            <th>Platform</th>
                            <th>Views</th>
                            <th>Likes</th>
                            <th>Comments</th>
                            <th>Shares</th>
                            <th>Clicks</th>
                            <th>Ad Spend</th>
                            <th>Revenue</th>
                            <th>ROI %</th>
                            <th>Content Count</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        # Add platform rows with enhanced number formatting
        for platform, data in platforms.items():
            html_content += f"""
                <tr>
                    <td><strong>{platform}</strong></td>
                    <td>{self._format_number(data.get('views', 0))}</td>
                    <td>{self._format_number(data.get('likes', 0))}</td>
                    <td>{self._format_number(data.get('comments', 0))}</td>
                    <td>{self._format_number(data.get('shares', 0))}</td>
                    <td>{self._format_number(data.get('clicks', 0))}</td>
                    <td>{self._format_currency(data.get('ad_spend', 0))}</td>
                    <td>{self._format_currency(data.get('revenue', 0))}</td>
                    <td>{self._format_number(data.get('roi_percentage', 0))}%</td>
                    <td>{data.get('content_count', 0)}</td>
                </tr>
            """
        
        # Add totals row
        html_content += f"""
                <tr style="background-color: #e3f2fd; font-weight: bold;">
                    <td><strong>Totals</strong></td>
                    <td>{self._format_number(totals.get('total_views', 0))}</td>
                    <td>{self._format_number(totals.get('total_likes', 0))}</td>
                    <td>{self._format_number(totals.get('total_comments', 0))}</td>
                    <td>{self._format_number(totals.get('total_shares', 0))}</td>
                    <td>{self._format_number(totals.get('total_clicks', 0))}</td>
                    <td>{self._format_currency(totals.get('total_ad_spend', 0))}</td>
                    <td>{self._format_currency(totals.get('total_revenue', 0))}</td>
                    <td>{self._format_number(overall_roi)}%</td>
                    <td>{sum(data.get('content_count', 0) for data in platforms.values())}</td>
                </tr>
            """
        
        html_content += """
                    </tbody>
                </table>
            </div>
            
            <div class="section">
                <h3>Strategic Insights</h3>
                <div style="margin-bottom: 15px;">
                    <strong>Top Performer:</strong> {analysis.get('top_performer', 'N/A')}
                </div>
                <div style="margin-bottom: 15px;">
                    <strong>Key Insights:</strong>
                    <ul style="margin: 10px 0; padding-left: 20px;">
        """
        
        # Add insights
        for insight in analysis.get('key_insights', []):
            html_content += f"<li>{insight}</li>"
        
        html_content += """
                    </ul>
                </div>
            </div>
        </div>
        
        <!-- Additional landscape sections -->
        <div class="content-sections">
            <div class="section">
                <h3>Strategic Opportunities</h3>
                <ul style="margin: 10px 0; padding-left: 20px;">
        """
        
        # Add strategic opportunities
        for opportunity in analysis.get('strategic_opportunities', []):
            html_content += f"<li>{opportunity}</li>"
        
        html_content += """
                </ul>
            </div>
            
            <div class="section">
                <h3>Risk Assessment & Roadmap</h3>
                <div style="margin-bottom: 15px;">
                    <strong>Risk Level:</strong> {analysis.get('risk_assessment', 'N/A')}
                </div>
                <div style="margin-bottom: 15px;">
                    <strong>Future Roadmap:</strong><br>
                    {analysis.get('future_roadmap', 'Strategic roadmap for optimization and growth.')}
                </div>
            </div>
        </div>
        
        <div class="insights-section">
            <h3>Competitive Intelligence & Financial Impact</h3>
            <div style="margin-bottom: 15px;">
                <strong>Market Position:</strong> {analysis.get('competitive_intelligence', 'Competitive analysis and market positioning insights.')}
            </div>
            <div style="margin-bottom: 15px;">
                <strong>Projected Impact:</strong> {analysis.get('financial_impact', 'Financial impact projections and optimization opportunities.')}
            </div>
        </div>
        
        <div class="footer">
            <p>Report generated by BOS Solution ROI Analytics | Portrait-Optimized Layout</p>
        </div>
    </div>
</body>
</html>
        """
        
        logger.info(f"✅ Template HTML generation completed: {len(html_content)} characters")
        logger.info("📋 HTML includes: Executive Summary, Metrics Grid, Platform Performance Table, Strategic Insights, and more")
        return html_content

if __name__ == "__main__":
    # Test the agent
    async def test():
        agent = ROIReportAgent()
        html_content, report_data = await agent.generate_html_report()
        print(f"HTML generated: {len(html_content) if html_content else 0} characters")
        print(f"Report data: {bool(report_data)}")
    
    asyncio.run(test())
