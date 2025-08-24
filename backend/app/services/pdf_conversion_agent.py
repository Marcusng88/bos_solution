#!/usr/bin/env python3
"""
Minimal PDF Conversion Agent for testing
"""

import os
import sys
from datetime import datetime
from io import BytesIO
from typing import Dict, Any, Optional, Tuple
import json
import logging

# Test xhtml2pdf import
try:
    from xhtml2pdf import pisa
    XHTML2PDF_AVAILABLE = True
    print("✅ xhtml2pdf import successful in minimal agent")
except ImportError:
    XHTML2PDF_AVAILABLE = False
    pisa = None
    print("❌ xhtml2pdf import failed in minimal agent")

# Test Google GenAI import
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
    print("✅ Google GenAI import successful in minimal agent")
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None
    print("⚠️  Google GenAI import failed in minimal agent")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MinimalPDFAgent:
    """Minimal PDF conversion agent for testing"""
    
    def __init__(self):
        self.xhtml2pdf_available = XHTML2PDF_AVAILABLE
        self.gemini_available = GEMINI_AVAILABLE
    
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
                output_path = f"test_report_{timestamp}.pdf"
            
            if output_path:
                with open(output_path, "wb") as f:
                    f.write(pdf_bytes)
            
            return pdf_bytes, output_path
            
        except Exception as e:
            logger.error(f"PDF conversion error: {e}")
            raise
    
    async def create_simple_roi_pdf(self, roi_data: Dict[str, Any], output_path: Optional[str] = None) -> Tuple[bytes, str]:
        """Create a simple ROI PDF without AI (fallback method)"""
        try:
            # Create simple HTML template
            html_content = self._create_simple_html_template(roi_data)
            
            # Convert to PDF
            return await self.convert_html_to_pdf(html_content, output_path)
            
        except Exception as e:
            logger.error(f"Simple PDF generation error: {e}")
            raise
    
    def _create_simple_html_template(self, roi_data: Dict[str, Any]) -> str:
        """Create a simple HTML template for ROI data"""
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
        body {{ font-family: Arial; font-size: 12pt; margin: 20pt; }}
        .title {{ font-size: 18pt; font-weight: bold; text-align: center; }}
        .section {{ font-size: 14pt; font-weight: bold; margin: 15pt 0 8pt 0; }}
        table {{ width: 100%; border-collapse: collapse; margin: 8pt 0; }}
        th, td {{ border: 1pt solid #ccc; padding: 4pt; text-align: left; }}
        th {{ background-color: #f0f0f0; font-weight: bold; }}
        </style>
        </head>
        <body>
        
        <div class="title">ROI Performance Report</div>
        <p style="text-align: center; color: #666;">Generated on {timestamp}</p>
        
        <div class="section">Executive Summary</div>
        <p>This report contains ROI performance data across multiple platforms and campaigns.</p>
        
        """
        
        # Add platform performance if available
        if 'platforms' in roi_data:
            html += """
            <div class="section">Platform Performance</div>
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
                    <td>{platform}</td>
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
        
        html += f"""
        <div style="margin-top: 20pt; padding: 8pt; border: 1pt solid #ccc; background-color: #f8f9fa;">
        <p><strong>Report Generated by:</strong> BOS Solution ROI Analytics System</p>
        <p><strong>Report ID:</strong> {datetime.now().strftime("%Y%m%d_%H%M%S")}</p>
        </div>
        
        </body>
        </html>
        """
        
        return html

# Global instance for easy access
pdf_agent = MinimalPDFAgent()

# Async wrapper functions
async def convert_html_to_pdf_async(html_content: str, output_path: Optional[str] = None) -> Tuple[bytes, str]:
    """Async wrapper for HTML to PDF conversion"""
    return await pdf_agent.convert_html_to_pdf(html_content, output_path)

async def generate_pdf_from_json_async(json_data: Dict[str, Any], output_path: Optional[str] = None) -> Tuple[bytes, str]:
    """Async wrapper for JSON to PDF conversion using AI"""
    # For now, just create a simple PDF from the data
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    body {{ font-family: Arial; font-size: 12pt; margin: 20pt; }}
    .title {{ font-size: 18pt; font-weight: bold; text-align: center; }}
    </style>
    </head>
    <body>
    <div class="title">JSON Data Report</div>
    <pre>{json.dumps(json_data, indent=2)}</pre>
    </body>
    </html>
    """
    return await pdf_agent.convert_html_to_pdf(html_content, output_path)

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
