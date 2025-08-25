#!/usr/bin/env python3
"""
Enhanced PDF Conversion Agent with YouTube and Instagram Data Integration
"""

import os
import sys
from datetime import datetime
from io import BytesIO
from typing import Dict, Any, Optional, Tuple, List
import json
import logging
import re

# Test xhtml2pdf import
try:
    from xhtml2pdf import pisa
    XHTML2PDF_AVAILABLE = True
    print("✅ xhtml2pdf import successful in enhanced agent")
except ImportError:
    XHTML2PDF_AVAILABLE = False
    pisa = None
    print("❌ xhtml2pdf import failed in enhanced agent")

# Test Google GenAI import
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
    print("✅ Google GenAI import successful in enhanced agent")
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None
    print("⚠️  Google GenAI import failed in enhanced agent")

# Import Supabase client and services
try:
    from app.core.supabase_client import supabase_client
    from app.services.youtube_data_service import YouTubeDataService
    SUPABASE_AVAILABLE = True
    print("✅ Supabase client and services imported successfully")
except ImportError as e:
    SUPABASE_AVAILABLE = False
    print(f"⚠️  Supabase imports failed: {e}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedPDFAgent:
    """Enhanced PDF conversion agent with YouTube and Instagram data integration"""
    
    def __init__(self):
        self.xhtml2pdf_available = XHTML2PDF_AVAILABLE
        self.gemini_available = GEMINI_AVAILABLE
        self.supabase_available = SUPABASE_AVAILABLE
        
        if self.supabase_available:
            self.youtube_service = YouTubeDataService()
    
    def clean_text(self, text: str) -> str:
        """
        Clean text by removing asterisks and other formatting issues
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # AGGRESSIVE cleaning to remove ALL markdown formatting
        # First, handle common patterns with **
        text = re.sub(r'\*\s*\*\*([^*]+):\*\*\s*([^*]+?)(?=\s*\*|$)', r'\1: \2', text)
        text = re.sub(r'\*\*([^*]+):\*\*\s*([^*]+?)(?=\s*\*|$)', r'\1: \2', text)
        text = re.sub(r'\*\*([^*]+):\*\*', r'\1:', text)
        
        # Remove all **text** patterns (bold formatting)
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        
        # Remove all *text* patterns (italic formatting)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        
        # Remove all __text__ patterns (underline formatting)
        text = re.sub(r'__(.*?)__', r'\1', text)
        
        # Remove all _text_ patterns (italic formatting)
        text = re.sub(r'_(.*?)_', r'\1', text)
        
        # Remove all ~~text~~ patterns (strikethrough formatting)
        text = re.sub(r'~~(.*?)~~', r'\1', text)
        
        # Remove all `text` patterns (code formatting)
        text = re.sub(r'`(.*?)`', r'\1', text)
        
        # Remove any remaining single asterisks (but be careful with multiplication)
        text = re.sub(r'(?<!\*)\*(?!\*)', '', text)
        
        # Remove any remaining double asterisks
        text = re.sub(r'\*\*', '', text)
        
        # Special handling: Convert ROI metrics into separate lines
        # Look for patterns like "Total Revenue: $18,087,958.79 Total Spend: $4,860,427.43"
        roi_patterns = [
            r'(Total Revenue:\s*\$[0-9,]+\.?[0-9]*)\s*(Total Spend:\s*\$[0-9,]+\.?[0-9]*)',
            r'(Total Spend:\s*\$[0-9,]+\.?[0-9]*)\s*(Total Profit:\s*\$[0-9,]+\.?[0-9]*)',
            r'(Total Profit:\s*\$[0-9,]+\.?[0-9]*)\s*(Overall ROI:\s*[0-9,]+\.?[0-9]*%)',
            r'(Overall ROI:\s*[0-9,]+\.?[0-9]*%)\s*(Overall ROAS:\s*[0-9,]+\.?[0-9]*)',
        ]
        
        for pattern in roi_patterns:
            text = re.sub(pattern, r'\1\n\2', text)
        
        # Remove extra whitespace and normalize line breaks
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Final aggressive cleanup: Remove any remaining markdown symbols
        text = text.replace('**', '')
        text = text.replace('*', '')
        text = text.replace('__', '')
        text = text.replace('_', '')
        text = text.replace('~~', '')
        text = text.replace('`', '')
        
        # Additional cleanup for any remaining asterisks
        text = text.replace('*', '')
        
        return text
    
    def format_roi_metrics(self, text: str) -> str:
        """
        Special formatting for ROI metrics to make them more readable
        
        Args:
            text: Text containing ROI metrics
            
        Returns:
            Formatted ROI metrics
        """
        if not text:
            return ""
        
        # Clean the text first
        cleaned_text = self.clean_text(text)
        
        # Define ROI metric patterns
        roi_metrics = [
            r'Total Revenue:\s*\$([0-9,]+\.?[0-9]*)',
            r'Total Spend:\s*\$([0-9,]+\.?[0-9]*)',
            r'Total Profit:\s*\$([0-9,]+\.?[0-9]*)',
            r'Overall ROI:\s*([0-9,]+\.?[0-9]*%)',
            r'Overall ROAS:\s*([0-9,]+\.?[0-9]*)',
        ]
        
        # Extract and format each metric
        formatted_metrics = []
        
        for pattern in roi_metrics:
            match = re.search(pattern, cleaned_text)
            if match:
                metric_name = pattern.split(':')[0].split('\\')[0]
                metric_value = match.group(1)
                
                if 'Revenue' in metric_name:
                    formatted_metrics.append(f"Total Revenue: ${metric_value}")
                elif 'Spend' in metric_name:
                    formatted_metrics.append(f"Total Spend: ${metric_value}")
                elif 'Profit' in metric_name:
                    formatted_metrics.append(f"Total Profit: ${metric_value}")
                elif 'ROI' in metric_name:
                    formatted_metrics.append(f"Overall ROI: {metric_value}")
                elif 'ROAS' in metric_name:
                    formatted_metrics.append(f"Overall ROAS: {metric_value}")
        
        # If we found metrics, return them formatted
        if formatted_metrics:
            return '\n'.join(formatted_metrics)
        
        # If no specific patterns found, return cleaned text
        return cleaned_text
    
    def clean_data(self, data: Any) -> Any:
        """
        Recursively clean text data in dictionaries, lists, and strings
        
        Args:
            data: Data to clean
            
        Returns:
            Cleaned data
        """
        if isinstance(data, dict):
            return {key: self.clean_data(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.clean_data(item) for item in data]
        elif isinstance(data, str):
            # Check if this string contains ROI metrics and format them specially
            if any(metric in data for metric in ['Total Revenue', 'Total Spend', 'Total Profit', 'Overall ROI', 'Overall ROAS']):
                return self.format_roi_metrics(data)
            else:
                return self.clean_text(data)
        else:
            return data
    
    async def convert_html_to_pdf(self, html_content: str, output_path: Optional[str] = None) -> Tuple[bytes, str]:
        """Convert HTML to PDF"""
        if not self.xhtml2pdf_available:
            raise ImportError("xhtml2pdf not available")
        
        try:
            pdf_bytes_io = BytesIO()
            error = pisa.CreatePDF(src=html_content, dest=pdf_bytes_io)
            
            if error.err:
                raise Exception(f"PDF generation failed: {error.err}")
            
            pdf_bytes = pdf_bytes_io.getvalue()
            
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"enhanced_roi_report_{timestamp}.pdf"
            
            if output_path:
                with open(output_path, "wb") as f:
                    f.write(pdf_bytes)
            
            return pdf_bytes, output_path
            
        except Exception as e:
            logger.error(f"PDF conversion error: {e}")
            raise
    
    async def fetch_youtube_data(self, user_id: str) -> Dict[str, Any]:
        """Fetch YouTube data from Supabase"""
        if not self.supabase_available:
            return {"error": "Supabase not available"}
        
        try:
            youtube_data = {
                "videos": [],
                "channels": [],
                "analytics": {}
            }
            
            # Fetch user's videos
            videos_response = await supabase_client._make_request(
                "GET",
                "videos",
                params={
                    "user_id": f"eq.{user_id}",
                    "order": "published_at.desc",
                    "limit": 50
                }
            )
            
            if videos_response.status_code == 200:
                youtube_data["videos"] = videos_response.json()
            
            # Fetch user's channels
            channels_response = await supabase_client._make_request(
                "GET",
                "channels",
                params={
                    "user_id": f"eq.{user_id}",
                    "order": "created_at.desc"
                }
            )
            
            if channels_response.status_code == 200:
                youtube_data["channels"] = channels_response.json()
            
            # Fetch YouTube ROI metrics
            youtube_roi_response = await supabase_client._make_request(
                "GET",
                "roi_metrics",
                params={
                    "user_id": f"eq.{user_id}",
                    "platform": "eq.youtube",
                    "order": "update_timestamp.desc",
                    "limit": 100
                }
            )
            
            if youtube_roi_response.status_code == 200:
                youtube_data["roi_metrics"] = youtube_roi_response.json()
            
            return youtube_data
            
        except Exception as e:
            logger.error(f"Error fetching YouTube data: {e}")
            return {"error": str(e)}
    
    async def fetch_instagram_data(self, user_id: str) -> Dict[str, Any]:
        """Fetch Instagram data from Supabase"""
        if not self.supabase_available:
            return {"error": "Supabase not available"}
        
        try:
            instagram_data = {
                "monitoring_data": [],
                "roi_metrics": [],
                "social_accounts": []
            }
            
            # Fetch Instagram monitoring data (from competitor monitoring)
            monitoring_response = await supabase_client._make_request(
                "GET",
                "monitoring_data",
                params={
                    "platform": "eq.instagram",
                    "order": "detected_at.desc",
                    "limit": 50
                }
            )
            
            if monitoring_response.status_code == 200:
                instagram_data["monitoring_data"] = monitoring_response.json()
            
            # Fetch Instagram ROI metrics
            instagram_roi_response = await supabase_client._make_request(
                "GET",
                "roi_metrics",
                params={
                    "user_id": f"eq.{user_id}",
                    "platform": "eq.instagram",
                    "order": "update_timestamp.desc",
                    "limit": 100
                }
            )
            
            if instagram_roi_response.status_code == 200:
                instagram_data["roi_metrics"] = instagram_roi_response.json()
            
            # Fetch Instagram social media accounts
            instagram_accounts_response = await supabase_client._make_request(
                "GET",
                "social_media_accounts",
                params={
                    "user_id": f"eq.{user_id}",
                    "platform": "eq.instagram",
                    "order": "created_at.desc"
                }
            )
            
            if instagram_accounts_response.status_code == 200:
                instagram_data["social_accounts"] = instagram_accounts_response.json()
            
            return instagram_data
            
        except Exception as e:
            logger.error(f"Error fetching Instagram data: {e}")
            return {"error": str(e)}
    
    async def fetch_actual_roi_metrics(self, user_id: str) -> Dict[str, Any]:
        """Fetch actual ROI metrics from Supabase to calculate real ROI percentage"""
        if not self.supabase_available:
            return {"error": "Supabase not available"}
        
        try:
            # Fetch ROI metrics from the last 30 days
            from datetime import datetime, timedelta
            cutoff_date = (datetime.now() - timedelta(days=30)).isoformat()
            
            roi_response = await supabase_client._make_request(
                "GET",
                "roi_metrics",
                params={
                    "user_id": f"eq.{user_id}",
                    "update_timestamp": f"gte.{cutoff_date}",
                    "order": "update_timestamp.desc"
                }
            )
            
            if roi_response.status_code != 200:
                return {"error": "Failed to fetch ROI metrics"}
            
            roi_data = roi_response.json()
            
            # Calculate actual ROI metrics
            total_revenue = sum(float(row.get("revenue_generated", 0)) for row in roi_data)
            total_spend = sum(float(row.get("ad_spend", 0)) for row in roi_data)
            total_profit = total_revenue - total_spend
            roi_percentage = (total_profit / total_spend * 100) if total_spend > 0 else 0
            roas_ratio = (total_revenue / total_spend) if total_spend > 0 else 0
            
            return {
                "total_revenue": total_revenue,
                "total_spend": total_spend,
                "total_profit": total_profit,
                "roi_percentage": roi_percentage,
                "roas_ratio": roas_ratio,
                "metrics_count": len(roi_data)
            }
            
        except Exception as e:
            logger.error(f"Error fetching actual ROI metrics: {e}")
            return {"error": str(e)}
    
    async def create_enhanced_roi_pdf(self, user_id: str, roi_data: Dict[str, Any], output_path: Optional[str] = None) -> Tuple[bytes, str]:
        """Create an enhanced ROI PDF with YouTube and Instagram data"""
        try:
            # Clean the data to remove formatting issues
            cleaned_roi_data = self.clean_data(roi_data)
            
            # Fetch additional platform data
            youtube_data = await self.fetch_youtube_data(user_id)
            instagram_data = await self.fetch_instagram_data(user_id)
            
            # Fetch actual ROI metrics from Supabase to get real ROI percentage
            actual_roi_metrics = await self.fetch_actual_roi_metrics(user_id)
            
            # Clean the fetched data
            cleaned_youtube_data = self.clean_data(youtube_data)
            cleaned_instagram_data = self.clean_data(instagram_data)
            
            # Create enhanced HTML template with actual ROI data
            html_content = self._create_enhanced_html_template(cleaned_roi_data, cleaned_youtube_data, cleaned_instagram_data, actual_roi_metrics)
            
            # Convert to PDF
            return await self.convert_html_to_pdf(html_content, output_path)
            
        except Exception as e:
            logger.error(f"Enhanced PDF generation error: {e}")
            raise
    
    def _create_enhanced_html_template(self, roi_data: Dict[str, Any], youtube_data: Dict[str, Any], instagram_data: Dict[str, Any], actual_roi_metrics: Dict[str, Any] = None) -> str:
        """Create an enhanced HTML template with YouTube and Instagram data"""
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
        @page {{
            margin: 1in;
            size: A4;
        }}
        
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            font-size: 11pt; 
            line-height: 1.5;
            color: #2c3e50;
            background-color: #ffffff;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30pt;
            padding-bottom: 20pt;
            border-bottom: 3pt solid #3498db;
        }}
        
        .title {{ 
            font-size: 24pt; 
            font-weight: 700; 
            color: #2c3e50;
            margin-bottom: 8pt;
            letter-spacing: -0.5pt;
        }}
        
        .subtitle {{
            font-size: 16pt;
            font-weight: 600;
            color: #34495e;
            margin: 25pt 0 15pt 0;
            padding-bottom: 8pt;
            border-bottom: 2pt solid #ecf0f1;
            position: relative;
        }}
        
        .subtitle::after {{
            content: '';
            position: absolute;
            bottom: -2pt;
            left: 0;
            width: 60pt;
            height: 2pt;
            background-color: #3498db;
        }}
        
        .section {{ 
            font-size: 14pt; 
            font-weight: 600; 
            margin: 20pt 0 12pt 0; 
            color: #34495e;
            background-color: #f8f9fa;
            padding: 8pt 12pt;
            border-left: 4pt solid #3498db;
            border-radius: 4pt;
        }}
        
        .metric-grid {{
            display: flex;
            flex-wrap: wrap;
            gap: 15pt;
            margin: 15pt 0;
        }}
        
        .metric-card {{
            flex: 1;
            min-width: 200pt;
            border: 1pt solid #e1e8ed;
            border-radius: 8pt;
            padding: 15pt;
            background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
            box-shadow: 0 2pt 8pt rgba(0,0,0,0.1);
        }}
        
        .metric-label {{
            font-weight: 600;
            color: #7f8c8d;
            font-size: 10pt;
            text-transform: uppercase;
            letter-spacing: 0.5pt;
            margin-bottom: 5pt;
        }}
        
        .metric-value {{
            font-size: 18pt;
            font-weight: 700;
            color: #27ae60;
            margin-bottom: 3pt;
        }}
        
        .metric-subtitle {{
            font-size: 9pt;
            color: #95a5a6;
            font-style: italic;
        }}
        
        table {{ 
            width: 100%; 
            border-collapse: collapse; 
            margin: 20pt 0; 
            font-size: 9pt;
            box-shadow: 0 4pt 16pt rgba(0,0,0,0.15);
            border-radius: 8pt;
            overflow: hidden;
            border: 1pt solid #e5e7eb;
        }}
        
        th {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 14pt 10pt; 
            border: none;
            font-weight: 700;
            text-align: center;
            font-size: 10pt;
            text-transform: uppercase;
            letter-spacing: 0.5pt;
            position: relative;
        }}
        
        th:first-child {{
            text-align: left;
        }}
        
        th:not(:last-child)::after {{
            content: '';
            position: absolute;
            right: 0;
            top: 25%;
            bottom: 25%;
            width: 1pt;
            background: rgba(255, 255, 255, 0.3);
        }}
        
        td {{ 
            padding: 12pt 10pt; 
            border-bottom: 1pt solid #e5e7eb; 
            word-wrap: break-word; 
            vertical-align: middle;
            background-color: #ffffff;
            text-align: center;
            font-weight: 500;
            position: relative;
        }}
        
        td:first-child {{
            text-align: left;
            font-weight: 700;
            color: #1f2937;
            background: #f8fafc;
        }}
        
        td:not(:last-child)::after {{
            content: '';
            position: absolute;
            right: 0;
            top: 15%;
            bottom: 15%;
            width: 1pt;
            background: #e5e7eb;
        }}
        
        tr:nth-child(even) td {{
            background-color: #f8fafc;
        }}
        
        tr:nth-child(even) td:first-child {{
            background-color: #f1f5f9;
        }}
        
        tr:hover td {{
            background-color: #f1f5f9;
        }}
        
        /* Platform-specific styling */
        tr:nth-child(1) td:first-child {{
            color: #1877f2;
        }}
        
        tr:nth-child(2) td:first-child {{
            color: #e4405f;
        }}
        
        tr:nth-child(3) td:first-child {{
            color: #ff0000;
        }}
        
        /* Value styling for monetary columns */
        td:nth-child(2),
        td:nth-child(3) {{
            font-family: 'Courier New', monospace;
            font-weight: 600;
            color: #059669;
        }}
        
        /* ROI percentage styling */
        td:nth-child(4) {{
            font-weight: 700;
            color: #059669;
        }}
        
        /* ROAS styling */
        td:nth-child(5) {{
            font-weight: 600;
            color: #7c3aed;
        }}
        
        /* Engagement and CTR styling */
        td:nth-child(6),
        td:nth-child(7) {{
            font-weight: 600;
            color: #dc2626;
        }}
        
        .platform-section {{
            margin: 25pt 0;
            padding: 20pt;
            border: 1pt solid #e1e8ed;
            border-radius: 10pt;
            background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
            box-shadow: 0 4pt 12pt rgba(0,0,0,0.08);
        }}
        
        .platform-header {{
            display: flex;
            align-items: center;
            margin-bottom: 15pt;
            padding-bottom: 10pt;
            border-bottom: 2pt solid #ecf0f1;
        }}
        
        .platform-icon {{
            width: 24pt;
            height: 24pt;
            background-color: #3498db;
            border-radius: 50%;
            margin-right: 10pt;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 12pt;
        }}
        
        .error-message {{
            color: #e74c3c;
            font-style: italic;
            background-color: #fdf2f2;
            padding: 10pt;
            border-radius: 6pt;
            border-left: 4pt solid #e74c3c;
        }}
        
        .summary-section {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 20pt;
            border-radius: 10pt;
            margin: 25pt 0;
        }}
        
        .summary-title {{
            font-size: 16pt;
            font-weight: 600;
            margin-bottom: 15pt;
            text-align: center;
        }}
        
        .footer {{
            margin-top: 30pt;
            padding: 15pt;
            border: 1pt solid #bdc3c7;
            border-radius: 8pt;
            background-color: #f8f9fa;
            font-size: 9pt;
            color: #7f8c8d;
        }}
        
        .footer-item {{
            margin: 3pt 0;
        }}
        
        .positive-value {{
            color: #27ae60;
            font-weight: 600;
        }}
        
        .negative-value {{
            color: #e74c3c;
            font-weight: 600;
        }}
        
        .neutral-value {{
            color: #95a5a6;
        }}
        </style>
        </head>
        <body>
        
        <div class="header">
            <div class="title">Enhanced ROI Performance Report</div>
            <div style="color: #7f8c8d; font-size: 11pt; margin-top: 5pt;">
                Generated on {timestamp}
            </div>
        </div>
        
        <div class="subtitle">Executive Summary</div>
        <p style="font-size: 12pt; line-height: 1.6; color: #34495e;">
            This comprehensive report provides detailed ROI performance analysis across multiple platforms including Facebook, Instagram, YouTube, and other social media channels. The data has been carefully analyzed to provide actionable insights for optimizing your marketing campaigns and maximizing return on investment.
        </p>
        
        <!-- ROI Metrics Section -->
        <div class="section">Key Performance Metrics</div>
        <div class="metric-grid" style="margin: 20pt 0;">
            <div class="metric-card">
                <div class="metric-label">Total Revenue</div>
                <div class="metric-value" style="color: #2ecc71;">${(actual_roi_metrics or {}).get('total_revenue', 0):,.2f}</div>
                <div class="metric-subtitle">Total revenue generated</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Spend</div>
                <div class="metric-value" style="color: #e74c3c;">${(actual_roi_metrics or {}).get('total_spend', 0):,.2f}</div>
                <div class="metric-subtitle">Total advertising spend</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Profit</div>
                <div class="metric-value" style="color: #27ae60;">${(actual_roi_metrics or {}).get('total_profit', 0):,.2f}</div>
                <div class="metric-subtitle">Net profit generated</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Overall ROAS</div>
                <div class="metric-value" style="color: #27ae60;">{(actual_roi_metrics or {}).get('roas_ratio', 0):.2f}</div>
                <div class="metric-subtitle">Return on ad spend</div>
            </div>
        </div>
        
        """
        
        # Add platform performance if available
        if 'platforms' in roi_data:
            html += """
            <div class="section">Platform Performance Overview</div>
            <table>
            <thead>
            <tr>
                <th>Platform</th>
                <th>Revenue</th>
                <th>Cost</th>
                <th>ROI</th>
                <th>ROI %</th>
            </tr>
            </thead>
            <tbody>
            """
            
            for platform, data in roi_data['platforms'].items():
                revenue = data.get('total_revenue', 0)
                cost = data.get('total_cost', 0)
                roi = revenue - cost
                roi_percentage = (roi / cost * 100) if cost > 0 else 0
                roi_class = "positive-value" if roi_percentage > 0 else "negative-value" if roi_percentage < 0 else "neutral-value"
                
                html += f"""
                <tr>
                    <td style="font-weight: 600;">{platform}</td>
                    <td class="positive-value">${revenue:,.2f}</td>
                    <td>${cost:,.2f}</td>
                    <td class="{roi_class}">${roi:,.2f}</td>
                    <td class="{roi_class}">{roi_percentage:.1f}%</td>
                </tr>
                """
            
            html += """
            </tbody>
            </table>
            """
        
        # Add YouTube Data Section
        html += """
        <div class="platform-section">
        <div class="platform-header">
            <div class="platform-icon">YT</div>
            <div class="subtitle" style="margin: 0; border: none; padding: 0;">YouTube Performance Analytics</div>
        </div>
        """
        
        if youtube_data.get("error"):
            html += f'<div class="error-message">YouTube data unavailable: {youtube_data["error"]}</div>'
        else:
            # YouTube Channels Summary
            if youtube_data.get("channels"):
                html += """
                <div class="section">Channel Overview</div>
                <table>
                <thead>
                <tr>
                    <th>Channel Title</th>
                    <th>Subscribers</th>
                    <th>Total Videos</th>
                    <th>Total Views</th>
                    <th>Est. Monthly Revenue</th>
                </tr>
                </thead>
                <tbody>
                """
                
                for channel in youtube_data["channels"]:
                    html += f"""
                    <tr>
                        <td style="font-weight: 600;">{channel.get('channel_title', 'N/A')}</td>
                        <td>{channel.get('total_subscribers', 0):,}</td>
                        <td>{channel.get('total_videos', 0):,}</td>
                        <td>{channel.get('total_views', 0):,}</td>
                        <td class="positive-value">${channel.get('estimated_monthly_revenue', 0):,.2f}</td>
                    </tr>
                    """
                
                html += """
                </tbody>
                </table>
                """
            
            # YouTube Videos Performance
            if youtube_data.get("videos"):
                html += """
                <div class="section">Recent Video Performance</div>
                <table>
                <thead>
                <tr>
                    <th>Video Title</th>
                    <th>Views</th>
                    <th>Likes</th>
                    <th>Comments</th>
                    <th>Engagement Rate</th>
                    <th>ROI Score</th>
                </tr>
                </thead>
                <tbody>
                """
                
                for video in youtube_data["videos"][:10]:  # Show top 10 videos
                    engagement_rate = video.get('engagement_rate', 0) * 100 if video.get('engagement_rate') else 0
                    html += f"""
                    <tr>
                        <td style="font-weight: 600;">{video.get('title', 'N/A')[:50]}...</td>
                        <td>{video.get('views', 0):,}</td>
                        <td>{video.get('likes', 0):,}</td>
                        <td>{video.get('comments', 0):,}</td>
                        <td class="positive-value">{engagement_rate:.2f}%</td>
                        <td class="positive-value">{video.get('roi_score', 0):.2f}</td>
                    </tr>
                    """
                
                html += """
                </tbody>
                </table>
                """
            
            # YouTube ROI Metrics
            if youtube_data.get("roi_metrics"):
                html += """
                <div class="section">YouTube ROI Metrics</div>
                <table>
                <thead>
                <tr>
                    <th>Date</th>
                    <th>Views</th>
                    <th>Revenue Generated</th>
                    <th>Ad Spend</th>
                    <th>ROI %</th>
                    <th>ROAS Ratio</th>
                </tr>
                </thead>
                <tbody>
                """
                
                for metric in youtube_data["roi_metrics"][:10]:  # Show top 10 metrics
                    roi_pct = metric.get('roi_percentage', 0)
                    roas = metric.get('roas_ratio', 0)
                    roi_class = "positive-value" if roi_pct > 0 else "negative-value" if roi_pct < 0 else "neutral-value"
                    roas_class = "positive-value" if roas > 1 else "negative-value" if roas < 1 else "neutral-value"
                    
                    html += f"""
                    <tr>
                        <td>{metric.get('update_timestamp', 'N/A')[:10]}</td>
                        <td>{metric.get('views', 0):,}</td>
                        <td class="positive-value">${metric.get('revenue_generated', 0):,.2f}</td>
                        <td>${metric.get('ad_spend', 0):,.2f}</td>
                        <td class="{roi_class}">{roi_pct:.1f}%</td>
                        <td class="{roas_class}">{roas:.2f}</td>
                    </tr>
                    """
                
                html += """
                </tbody>
                </table>
                """
        
        html += "</div>"
        
        # Add Instagram Data Section
        html += """
        <div class="platform-section">
        <div class="platform-header">
            <div class="platform-icon">IG</div>
            <div class="subtitle" style="margin: 0; border: none; padding: 0;">Instagram Performance Analytics</div>
        </div>
        """
        
        if instagram_data.get("error"):
            html += f'<div class="error-message">Instagram data unavailable: {instagram_data["error"]}</div>'
        else:
            # Instagram ROI Metrics
            if instagram_data.get("roi_metrics"):
                html += """
                <div class="section">Instagram ROI Metrics</div>
                <table>
                <thead>
                <tr>
                    <th>Date</th>
                    <th>Views</th>
                    <th>Likes</th>
                    <th>Comments</th>
                    <th>Revenue Generated</th>
                    <th>Ad Spend</th>
                    <th>ROI %</th>
                </tr>
                </thead>
                <tbody>
                """
                
                for metric in instagram_data["roi_metrics"][:10]:  # Show top 10 metrics
                    roi_pct = metric.get('roi_percentage', 0)
                    roi_class = "positive-value" if roi_pct > 0 else "negative-value" if roi_pct < 0 else "neutral-value"
                    
                    html += f"""
                    <tr>
                        <td>{metric.get('update_timestamp', 'N/A')[:10]}</td>
                        <td>{metric.get('views', 0):,}</td>
                        <td>{metric.get('likes', 0):,}</td>
                        <td>{metric.get('comments', 0):,}</td>
                        <td class="positive-value">${metric.get('revenue_generated', 0):,.2f}</td>
                        <td>${metric.get('ad_spend', 0):,.2f}</td>
                        <td class="{roi_class}">{roi_pct:.1f}%</td>
                    </tr>
                    """
                
                html += """
                </tbody>
                </table>
                """
            
            # Instagram Connected Accounts
            if instagram_data.get("social_accounts"):
                html += """
                <div class="section">Connected Instagram Accounts</div>
                <table>
                <thead>
                <tr>
                    <th>Account Name</th>
                    <th>Username</th>
                    <th>Connected Since</th>
                </tr>
                </thead>
                <tbody>
                """
                
                for account in instagram_data["social_accounts"]:
                    html += f"""
                    <tr>
                        <td style="font-weight: 600;">{account.get('account_name', 'N/A')}</td>
                        <td>@{account.get('username', 'N/A')}</td>
                        <td>{account.get('created_at', 'N/A')[:10]}</td>
                    </tr>
                    """
                
                html += """
                </tbody>
                </table>
                """
            
            # Instagram Monitoring Data
            if instagram_data.get("monitoring_data"):
                html += """
                <div class="section">Instagram Content Monitoring</div>
                <table>
                <thead>
                <tr>
                    <th>Author</th>
                    <th>Content Type</th>
                    <th>Engagement</th>
                    <th>Sentiment</th>
                    <th>Detected</th>
                </tr>
                </thead>
                <tbody>
                """
                
                for data in instagram_data["monitoring_data"][:10]:  # Show top 10
                    engagement = data.get('engagement_metrics', {})
                    engagement_count = engagement.get('like_count', 0) + engagement.get('comment_count', 0) if engagement else 0
                    sentiment = data.get('sentiment_score', 0)
                    sentiment_text = "Positive" if sentiment > 0.1 else "Negative" if sentiment < -0.1 else "Neutral"
                    sentiment_class = "positive-value" if sentiment > 0.1 else "negative-value" if sentiment < -0.1 else "neutral-value"
                    
                    html += f"""
                    <tr>
                        <td style="font-weight: 600;">{data.get('author_username', 'N/A')}</td>
                        <td>{data.get('post_type', 'N/A')}</td>
                        <td>{engagement_count:,}</td>
                        <td class="{sentiment_class}">{sentiment_text}</td>
                        <td>{data.get('detected_at', 'N/A')[:10]}</td>
                    </tr>
                    """
                
                html += """
                </tbody>
                </table>
                """
        
        html += "</div>"
        
        # Add campaign details if available
        if 'campaigns' in roi_data:
            html += """
            <div class="section">Campaign Details</div>
            <table>
            <thead>
            <tr>
                <th>Date</th>
                <th>Platform</th>
                <th>Campaign</th>
                <th>Revenue</th>
                <th>Cost</th>
                <th>ROI</th>
            </tr>
            </thead>
            <tbody>
            """
            
            for campaign in roi_data['campaigns']:
                revenue = campaign.get('revenue', 0)
                cost = campaign.get('cost', 0)
                roi = revenue - cost
                roi_class = "positive-value" if roi > 0 else "negative-value" if roi < 0 else "neutral-value"
                
                html += f"""
                <tr>
                    <td>{campaign.get('date', 'N/A')}</td>
                    <td style="font-weight: 600;">{campaign.get('platform', 'N/A')}</td>
                    <td style="font-weight: 600;">{campaign.get('campaign_name', 'N/A')}</td>
                    <td class="positive-value">${revenue:,.2f}</td>
                    <td>${cost:,.2f}</td>
                    <td class="{roi_class}">${roi:,.2f}</td>
                </tr>
                """
            
            html += """
            </tbody>
            </table>
            """
        
        # Add summary metrics
        html += """
        <div class="summary-section">
        <div class="summary-title">Summary Metrics</div>
        <div class="metric-grid">
        """
        
        # Calculate summary metrics - use actual ROI metrics if available, otherwise fallback to roi_data
        if actual_roi_metrics and not actual_roi_metrics.get('error'):
            total_revenue = actual_roi_metrics.get('total_revenue', 0)
            total_cost = actual_roi_metrics.get('total_spend', 0)
            total_roi = actual_roi_metrics.get('total_profit', 0)
            overall_roi_pct = actual_roi_metrics.get('roi_percentage', 0)
        else:
            total_revenue = sum(data.get('total_revenue', 0) for data in roi_data.get('platforms', {}).values())
            total_cost = sum(data.get('total_cost', 0) for data in roi_data.get('platforms', {}).values())
            total_roi = total_revenue - total_cost
            overall_roi_pct = (total_roi / total_cost * 100) if total_cost > 0 else 0
        
        # YouTube summary
        youtube_videos_count = len(youtube_data.get('videos', []))
        youtube_channels_count = len(youtube_data.get('channels', []))
        youtube_total_views = sum(video.get('views', 0) for video in youtube_data.get('videos', []))
        
        # Instagram summary
        instagram_metrics_count = len(instagram_data.get('roi_metrics', []))
        instagram_accounts_count = len(instagram_data.get('social_accounts', []))
        
        roi_class = "positive-value" if overall_roi_pct > 0 else "negative-value" if overall_roi_pct < 0 else "neutral-value"
        
        html += f"""
        <div class="metric-card">
            <div class="metric-label">Total Revenue</div>
            <div class="metric-value" style="color: #2ecc71;">${total_revenue:,.2f}</div>
            <div class="metric-subtitle">Across all platforms</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Total Cost</div>
            <div class="metric-value" style="color: #e74c3c;">${total_cost:,.2f}</div>
            <div class="metric-subtitle">Total ad spend</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Total ROI</div>
            <div class="metric-value {roi_class}">${total_roi:,.2f}</div>
            <div class="metric-subtitle">{overall_roi_pct:.1f}% return</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">YouTube Videos</div>
            <div class="metric-value" style="color: #3498db;">{youtube_videos_count}</div>
            <div class="metric-subtitle">{youtube_total_views:,} total views</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">YouTube Channels</div>
            <div class="metric-value" style="color: #3498db;">{youtube_channels_count}</div>
            <div class="metric-subtitle">Connected channels</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Instagram Metrics</div>
            <div class="metric-value" style="color: #e91e63;">{instagram_metrics_count}</div>
            <div class="metric-subtitle">Performance records</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Instagram Accounts</div>
            <div class="metric-value" style="color: #e91e63;">{instagram_accounts_count}</div>
            <div class="metric-subtitle">Connected accounts</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Report Generated</div>
            <div class="metric-value" style="color: #95a5a6;">{datetime.now().strftime("%Y-%m-%d")}</div>
            <div class="metric-subtitle">Analysis date</div>
        </div>
        </div>
        </div>
        """
        
        html += f"""
        <div class="footer">
            <div class="footer-item"><strong>Report Generated by:</strong> BOS Solution Enhanced ROI Analytics System</div>
            <div class="footer-item"><strong>Report ID:</strong> {datetime.now().strftime("%Y%m%d_%H%M%S")}</div>
            <div class="footer-item"><strong>Data Sources:</strong> ROI Metrics, YouTube Analytics, Instagram Monitoring, Social Media Accounts</div>
            <div class="footer-item"><strong>Analysis Period:</strong> Comprehensive multi-platform performance review</div>
        </div>
        
        </body>
        </html>
        """
        
        return html
    
    async def create_simple_roi_pdf(self, roi_data: Dict[str, Any], output_path: Optional[str] = None) -> Tuple[bytes, str]:
        """Create a simple ROI PDF without AI (fallback method)"""
        try:
            # Clean the data to remove formatting issues
            cleaned_roi_data = self.clean_data(roi_data)
            
            # Fetch actual ROI metrics from Supabase to get real ROI percentage
            # Note: We need user_id for this, but it's not available in this method
            # For now, we'll use the data from roi_data if available
            actual_roi_metrics = roi_data.get('actual_roi_metrics', {})
            
            # Create simple HTML template
            html_content = self._create_simple_html_template(cleaned_roi_data, actual_roi_metrics)
            
            # Convert to PDF
            return await self.convert_html_to_pdf(html_content, output_path)
            
        except Exception as e:
            logger.error(f"Simple PDF generation error: {e}")
            raise
    
    def _create_simple_html_template(self, roi_data: Dict[str, Any], actual_roi_metrics: Dict[str, Any] = None) -> str:
        """Create a simple HTML template for ROI data"""
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
        @page {{
            margin: 1in;
            size: A4;
        }}
        
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            font-size: 11pt; 
            line-height: 1.5;
            color: #2c3e50;
            background-color: #ffffff;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30pt;
            padding-bottom: 20pt;
            border-bottom: 3pt solid #3498db;
        }}
        
        .title {{ 
            font-size: 24pt; 
            font-weight: 700; 
            color: #2c3e50;
            margin-bottom: 8pt;
            letter-spacing: -0.5pt;
        }}
        
        .subtitle {{
            font-size: 16pt;
            font-weight: 600;
            color: #34495e;
            margin: 25pt 0 15pt 0;
            padding-bottom: 8pt;
            border-bottom: 2pt solid #ecf0f1;
            position: relative;
        }}
        
        .subtitle::after {{
            content: '';
            position: absolute;
            bottom: -2pt;
            left: 0;
            width: 60pt;
            height: 2pt;
            background-color: #3498db;
        }}
        
        .section {{ 
            font-size: 14pt; 
            font-weight: 600; 
            margin: 20pt 0 12pt 0; 
            color: #34495e;
            background-color: #f8f9fa;
            padding: 8pt 12pt;
            border-left: 4pt solid #3498db;
            border-radius: 4pt;
        }}
        
        table {{ 
            width: 100%; 
            border-collapse: collapse; 
            margin: 15pt 0; 
            font-size: 9pt;
            box-shadow: 0 2pt 8pt rgba(0,0,0,0.1);
            border-radius: 6pt;
            overflow: hidden;
        }}
        
        th {{ 
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            color: white;
            padding: 12pt 8pt; 
            border: none;
            font-weight: 600;
            text-align: left;
            font-size: 10pt;
            text-transform: uppercase;
            letter-spacing: 0.3pt;
        }}
        
        td {{ 
            padding: 10pt 8pt; 
            border-bottom: 1pt solid #ecf0f1; 
            word-wrap: break-word; 
            vertical-align: top;
            background-color: #ffffff;
        }}
        
        tr:nth-child(even) td {{
            background-color: #f8f9fa;
        }}
        
        tr:hover td {{
            background-color: #e8f4fd;
        }}
        
        .summary-section {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 20pt;
            border-radius: 10pt;
            margin: 25pt 0;
        }}
        
        .summary-title {{
            font-size: 16pt;
            font-weight: 600;
            margin-bottom: 15pt;
            text-align: center;
        }}
        
        .metric-grid {{
            display: flex;
            flex-wrap: wrap;
            gap: 15pt;
            margin: 15pt 0;
        }}
        
        .metric-card {{
            flex: 1;
            min-width: 200pt;
            border: 1pt solid #e1e8ed;
            border-radius: 8pt;
            padding: 15pt;
            background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
            box-shadow: 0 2pt 8pt rgba(0,0,0,0.1);
        }}
        
        .metric-label {{
            font-weight: 600;
            color: #7f8c8d;
            font-size: 10pt;
            text-transform: uppercase;
            letter-spacing: 0.5pt;
            margin-bottom: 5pt;
        }}
        
        .metric-value {{
            font-size: 18pt;
            font-weight: 700;
            color: #27ae60;
            margin-bottom: 3pt;
        }}
        
        .metric-subtitle {{
            font-size: 9pt;
            color: #95a5a6;
            font-style: italic;
        }}
        
        .footer {{
            margin-top: 30pt;
            padding: 15pt;
            border: 1pt solid #bdc3c7;
            border-radius: 8pt;
            background-color: #f8f9fa;
            font-size: 9pt;
            color: #7f8c8d;
        }}
        
        .footer-item {{
            margin: 3pt 0;
        }}
        
        .positive-value {{
            color: #27ae60;
            font-weight: 600;
        }}
        
        .negative-value {{
            color: #e74c3c;
            font-weight: 600;
        }}
        
        .neutral-value {{
            color: #95a5a6;
        }}
        </style>
        </head>
        <body>
        
        <div class="header">
            <div class="title">ROI Performance Report</div>
            <div style="color: #7f8c8d; font-size: 11pt; margin-top: 5pt;">
                Generated on {timestamp}
            </div>
        </div>
        
        <div class="subtitle">Executive Summary</div>
        <p style="font-size: 12pt; line-height: 1.6; color: #34495e;">
            This comprehensive report provides detailed ROI performance analysis across multiple platforms and campaigns. The data has been carefully analyzed to provide actionable insights for optimizing your marketing strategies and maximizing return on investment.
        </p>
        
        <!-- ROI Metrics Section -->
        <div class="section">Key Performance Metrics</div>
        <div class="metric-grid" style="margin: 20pt 0;">
            <div class="metric-card">
                <div class="metric-label">Total Revenue</div>
                <div class="metric-value" style="color: #2ecc71;">${(actual_roi_metrics or {}).get('total_revenue', 0):,.2f}</div>
                <div class="metric-subtitle">Total revenue generated</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Spend</div>
                <div class="metric-value" style="color: #e74c3c;">${(actual_roi_metrics or {}).get('total_spend', 0):,.2f}</div>
                <div class="metric-subtitle">Total advertising spend</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Profit</div>
                <div class="metric-value" style="color: #27ae60;">${(actual_roi_metrics or {}).get('total_profit', 0):,.2f}</div>
                <div class="metric-subtitle">Net profit generated</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Overall ROAS</div>
                <div class="metric-value" style="color: #27ae60;">{(actual_roi_metrics or {}).get('roas_ratio', 0):.2f}</div>
                <div class="metric-subtitle">Return on ad spend</div>
            </div>
        </div>
        
        """
        
        # Add platform performance if available
        if 'platforms' in roi_data:
            html += """
            <div class="section">Platform Performance Overview</div>
            <table>
            <thead>
            <tr>
                <th>Platform</th>
                <th>Revenue</th>
                <th>Cost</th>
                <th>ROI</th>
                <th>ROI %</th>
            </tr>
            </thead>
            <tbody>
            """
            
            for platform, data in roi_data['platforms'].items():
                revenue = data.get('total_revenue', 0)
                cost = data.get('total_cost', 0)
                roi = revenue - cost
                roi_percentage = (roi / cost * 100) if cost > 0 else 0
                
                html += f"""
                <tr>
                    <td style="font-weight: 600;">{platform}</td>
                    <td>${revenue:,.2f}</td>
                    <td>${cost:,.2f}</td>
                    <td>${roi:,.2f}</td>
                    <td>{roi_percentage:.1f}%</td>
                </tr>
                """
            
            html += """
            </tbody>
            </table>
            """
        
        # Add campaign details if available
        if 'campaigns' in roi_data:
            html += """
            <div class="section">Campaign Details</div>
            <table>
            <thead>
            <tr>
                <th>Date</th>
                <th>Platform</th>
                <th>Campaign</th>
                <th>Revenue</th>
                <th>Cost</th>
                <th>ROI</th>
            </tr>
            </thead>
            <tbody>
            """
            
            for campaign in roi_data['campaigns']:
                revenue = campaign.get('revenue', 0)
                cost = campaign.get('cost', 0)
                roi = revenue - cost
                
                html += f"""
                <tr>
                    <td>{campaign.get('date', 'N/A')}</td>
                    <td>{campaign.get('platform', 'N/A')}</td>
                    <td>{campaign.get('campaign_name', 'N/A')}</td>
                    <td>${revenue:,.2f}</td>
                    <td>${cost:,.2f}</td>
                    <td>${roi:,.2f}</td>
                </tr>
                """
            
            html += """
            </tbody>
            </table>
            """
        
        # Add summary metrics
        html += """
        <div class="summary-section">
        <div class="summary-title">Summary Metrics</div>
        <div class="metric-grid">
        """
        
        # Calculate summary metrics - use actual ROI metrics if available, otherwise fallback to roi_data
        if actual_roi_metrics and not actual_roi_metrics.get('error'):
            total_revenue = actual_roi_metrics.get('total_revenue', 0)
            total_cost = actual_roi_metrics.get('total_spend', 0)
            total_roi = actual_roi_metrics.get('total_profit', 0)
            overall_roi_pct = actual_roi_metrics.get('roi_percentage', 0)
        else:
            total_revenue = sum(data.get('total_revenue', 0) for data in roi_data.get('platforms', {}).values())
            total_cost = sum(data.get('total_cost', 0) for data in roi_data.get('platforms', {}).values())
            total_roi = total_revenue - total_cost
            overall_roi_pct = (total_roi / total_cost * 100) if total_cost > 0 else 0
        campaigns_count = len(roi_data.get('campaigns', []))
        platforms_count = len(roi_data.get('platforms', {}))
        
        roi_class = "positive-value" if overall_roi_pct > 0 else "negative-value" if overall_roi_pct < 0 else "neutral-value"
        
        html += f"""
        <div class="metric-card">
            <div class="metric-label">Total Revenue</div>
            <div class="metric-value" style="color: #2ecc71;">${total_revenue:,.2f}</div>
            <div class="metric-subtitle">Across all platforms</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Total Cost</div>
            <div class="metric-value" style="color: #e74c3c;">${total_cost:,.2f}</div>
            <div class="metric-subtitle">Total ad spend</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Total ROI</div>
            <div class="metric-value {roi_class}">${total_roi:,.2f}</div>
            <div class="metric-subtitle">{overall_roi_pct:.1f}% return</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Platforms</div>
            <div class="metric-value" style="color: #3498db;">{platforms_count}</div>
            <div class="metric-subtitle">Active platforms</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Campaigns</div>
            <div class="metric-value" style="color: #9b59b6;">{campaigns_count}</div>
            <div class="metric-subtitle">Total campaigns</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Report Generated</div>
            <div class="metric-value" style="color: #95a5a6;">{datetime.now().strftime("%Y-%m-%d")}</div>
            <div class="metric-subtitle">Analysis date</div>
        </div>
        </div>
        </div>
        """
        
        html += f"""
        <div class="footer">
            <div class="footer-item"><strong>Report Generated by:</strong> BOS Solution ROI Analytics System</div>
            <div class="footer-item"><strong>Report ID:</strong> {datetime.now().strftime("%Y%m%d_%H%M%S")}</div>
            <div class="footer-item"><strong>Data Sources:</strong> ROI Metrics, Campaign Analytics, Platform Performance</div>
            <div class="footer-item"><strong>Analysis Period:</strong> Comprehensive performance review</div>
        </div>
        
        </body>
        </html>
        """
        
        return html

# Global instance for easy access
pdf_agent = EnhancedPDFAgent()

# Async wrapper functions
async def convert_html_to_pdf_async(html_content: str, output_path: Optional[str] = None) -> Tuple[bytes, str]:
    """Async wrapper for HTML to PDF conversion"""
    return await pdf_agent.convert_html_to_pdf(html_content, output_path)

async def generate_pdf_from_json_async(json_data: Dict[str, Any], output_path: Optional[str] = None) -> Tuple[bytes, str]:
    """Async wrapper for JSON to PDF conversion using AI"""
    # Clean the JSON data
    cleaned_json_data = pdf_agent.clean_data(json_data)
    
    # Create a professional HTML template for JSON data
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    @page {{
        margin: 1in;
        size: A4;
    }}
    
    body {{ 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
        font-size: 11pt; 
        line-height: 1.5;
        color: #2c3e50;
        background-color: #ffffff;
    }}
    
    .header {{
        text-align: center;
        margin-bottom: 30pt;
        padding-bottom: 20pt;
        border-bottom: 3pt solid #3498db;
    }}
    
    .title {{ 
        font-size: 24pt; 
        font-weight: 700; 
        color: #2c3e50;
        margin-bottom: 8pt;
        letter-spacing: -0.5pt;
    }}
    
    .subtitle {{
        font-size: 16pt;
        font-weight: 600;
        color: #34495e;
        margin: 25pt 0 15pt 0;
        padding-bottom: 8pt;
        border-bottom: 2pt solid #ecf0f1;
        position: relative;
    }}
    
    .subtitle::after {{
        content: '';
        position: absolute;
        bottom: -2pt;
        left: 0;
        width: 60pt;
        height: 2pt;
        background-color: #3498db;
    }}
    
    .data-section {{
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        padding: 20pt;
        border-radius: 10pt;
        border: 1pt solid #e1e8ed;
        box-shadow: 0 4pt 12pt rgba(0,0,0,0.08);
    }}
    
    .json-content {{
        background-color: #2c3e50;
        color: #ecf0f1;
        padding: 15pt;
        border-radius: 8pt;
        font-family: 'Courier New', monospace;
        font-size: 9pt;
        line-height: 1.4;
        overflow-x: auto;
        white-space: pre-wrap;
        word-wrap: break-word;
    }}
    
    .footer {{
        margin-top: 30pt;
        padding: 15pt;
        border: 1pt solid #bdc3c7;
        border-radius: 8pt;
        background-color: #f8f9fa;
        font-size: 9pt;
        color: #7f8c8d;
        text-align: center;
    }}
    </style>
    </head>
    <body>
    
    <div class="header">
        <div class="title">JSON Data Report</div>
        <div style="color: #7f8c8d; font-size: 11pt; margin-top: 5pt;">
            Generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
        </div>
    </div>
    
    <div class="subtitle">Data Overview</div>
    <div class="data-section">
        <div class="json-content">{json.dumps(cleaned_json_data, indent=2)}</div>
    </div>
    
    <div class="footer">
        <div><strong>Report Generated by:</strong> BOS Solution Enhanced PDF Generator</div>
        <div><strong>Report ID:</strong> {datetime.now().strftime("%Y%m%d_%H%M%S")}</div>
        <div><strong>Data Type:</strong> JSON Analysis Report</div>
    </div>
    
    </body>
    </html>
    """
    return await pdf_agent.convert_html_to_pdf(html_content, output_path)

async def create_enhanced_roi_pdf_async(user_id: str, roi_data: Dict[str, Any], output_path: Optional[str] = None) -> Tuple[bytes, str]:
    """Async wrapper for enhanced ROI PDF generation"""
    return await pdf_agent.create_enhanced_roi_pdf(user_id, roi_data, output_path)

def convert_html_to_pdf_sync(html_content: str, output_path: Optional[str] = None) -> Tuple[bytes, str]:
    """Synchronous wrapper for HTML to PDF conversion"""
    try:
        import asyncio
        # Check if we're already in an event loop
        try:
            loop = asyncio.get_running_loop()
            # We're in an event loop, so we need to run the coroutine directly
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, pdf_agent.convert_html_to_pdf(html_content, output_path))
                return future.result()
        except RuntimeError:
            # No event loop running, we can use asyncio.run
            return asyncio.run(pdf_agent.convert_html_to_pdf(html_content, output_path))
    except Exception as e:
        logger.error(f"Error in convert_html_to_pdf_sync: {e}")
        raise

def generate_pdf_from_json_sync(json_data: Dict[str, Any], output_path: Optional[str] = None) -> Tuple[bytes, str]:
    """Synchronous wrapper for JSON to PDF conversion using AI"""
    try:
        import asyncio
        # Check if we're already in an event loop
        try:
            loop = asyncio.get_running_loop()
            # We're in an event loop, so we need to run the coroutine directly
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, generate_pdf_from_json_async(json_data, output_path))
                return future.result()
        except RuntimeError:
            # No event loop running, we can use asyncio.run
            return asyncio.run(generate_pdf_from_json_async(json_data, output_path))
    except Exception as e:
        logger.error(f"Error in generate_pdf_from_json_sync: {e}")
        raise

def create_enhanced_roi_pdf_sync(user_id: str, roi_data: Dict[str, Any], output_path: Optional[str] = None) -> Tuple[bytes, str]:
    """Synchronous wrapper for enhanced ROI PDF generation"""
    try:
        import asyncio
        # Check if we're already in an event loop
        try:
            loop = asyncio.get_running_loop()
            # We're in an event loop, so we need to run the coroutine directly
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, pdf_agent.create_enhanced_roi_pdf(user_id, roi_data, output_path))
                return future.result()
        except RuntimeError:
            # No event loop running, we can use asyncio.run
            return asyncio.run(pdf_agent.create_enhanced_roi_pdf(user_id, roi_data, output_path))
    except Exception as e:
        logger.error(f"Error in create_enhanced_roi_pdf_sync: {e}")
        raise
