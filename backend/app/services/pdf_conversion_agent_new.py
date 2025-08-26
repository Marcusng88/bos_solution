"""
PDF Conversion Agent using xhtml2pdf
Converts HTML reports to PDF format with professional styling
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
except ImportError:
    XHTML2PDF_AVAILABLE = False
    pisa = None

# Test Google GenAI import
try:
    import google.generativeai as genai
    from google.genai import types
    from google.adk.agents.callback_context import CallbackContext
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None
    CallbackContext = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFConversionAgent:
    """
    Agent that converts HTML reports to PDF using xhtml2pdf
    Optimized for ROI reports with professional styling
    """
    
    def __init__(self):
        self.instruction_prompt = self._get_instruction_prompt()
        self.default_css = self._get_default_css()
        
    def _get_instruction_prompt(self) -> str:
        """Returns the enhanced xhtml2pdf HTML generation prompt"""
        return """
        # Enhanced xhtml2pdf HTML Generation Prompt

        You are a specialized coding agent that converts JSON data into HTML/CSS optimized for xhtml2pdf conversion. Follow these strict guidelines to ensure professional, readable PDF output.

        ## Core Requirements
        - Convert ALL data from {final_comprehensive_report} into HTML/CSS
        - **NEVER** miss any data from the JSON
        - Output **ONLY** the HTML/CSS code, no explanations or markdown formatting
        - Design must be professional, clean, and PDF-optimized
        - Handle data overflow and text wrapping properly
        - Ensure all numerical data is clearly readable

        ## Critical xhtml2pdf Considerations
        - PDF is designed around pages of specific width and height with absolute positioning
        - xhtml2pdf supports HTML5 and CSS 2.1 (and some CSS 3)
        - Tables must handle wide data without overlap or truncation
        - Use page breaks wisely to prevent data splitting

        ## Supported HTML Tags (Use These Only)
        ```html
        <!-- Structure -->
        <html>, <body>, <div>, <span>, <p>, <br>, <h1> to <h6>

        <!-- Tables -->
        <table>, <tr>, <td>, <th>, <thead>, <tbody>

        <!-- Lists -->
        <ul>, <ol>, <li>

        <!-- Text formatting -->
        <strong>, <em>, <b>, <i>

        <!-- Images (Base64 only) -->
        <img src="data:image/png;base64,..." />

        <!-- Links -->
        <a href="...">text</a>

        <!-- PDF-specific -->
        <pdf:toc />
        <pdf:nextpage />
        ```

        ## Supported CSS Properties (xhtml2pdf Optimized)
        ```css
        /* Typography - Use absolute units only */
        font-family: "Arial", "Helvetica", sans-serif;
        font-size: 10pt; /* Use pt for PDF, not px */
        font-weight: normal | bold;
        line-height: 1.2;
        letter-spacing: 0.5pt;

        /* Colors */
        color: #000000;
        background-color: #ffffff;

        /* Layout - Absolute units only */
        width: 100pt; /* pt, px only - NO %, vw, vh */
        height: 50pt;
        padding: 5pt;
        margin: 5pt;
        min-width: 80pt;
        max-width: 500pt;

        /* Text alignment */
        text-align: left | center | right | justify;
        vertical-align: top | middle | bottom;

        /* Borders */
        border: 1pt solid #000000;
        border-collapse: collapse; /* Essential for tables */
        border-spacing: 0;

        /* Table-specific */
        table-layout: fixed; /* Prevents column overflow */
        word-wrap: break-word;
        overflow-wrap: break-word;

        /* PDF-specific properties */
        -pdf-keep-with-next: true; /* Keep elements together */
        -pdf-outline: true; /* Add to bookmarks */
        -pdf-outline-level: 1;
        page-break-before: auto | always;
        page-break-after: auto | always;
        page-break-inside: avoid;
        ```

        ## CRITICAL Table Handling Rules
        1. **Always use `table-layout: fixed`** to prevent column overflow
        2. **Set explicit column widths** in points (pt)
        3. **Use `word-wrap: break-word`** for long data
        4. **Apply `border-collapse: collapse`** to all tables
        5. **Handle empty cells** with `&nbsp;` to prevent formatting issues
        6. **Limit table width** to 500pt maximum for A4 pages

        ## Data Formatting Standards
        ```css
        /* Headers */
        .report-title { font-size: 16pt; font-weight: bold; text-align: center; margin: 10pt; }
        .section-header { font-size: 12pt; font-weight: bold; margin: 8pt 0 5pt 0; }
        .subsection-header { font-size: 10pt; font-weight: bold; margin: 5pt 0 3pt 0; }

        /* Tables */
        .data-table {
            width: 500pt;
            table-layout: fixed;
            border-collapse: collapse;
            margin: 5pt 0;
            font-size: 8pt;
        }
        .data-table th {
            background-color: #f0f0f0;
            padding: 3pt;
            border: 1pt solid #000;
            font-weight: bold;
            text-align: center;
        }
        .data-table td {
            padding: 3pt;
            border: 1pt solid #ccc;
            word-wrap: break-word;
            vertical-align: top;
        }

        /* Column width distribution for ROI data */
        .col-date { width: 80pt; }
        .col-platform { width: 60pt; }
        .col-campaign { width: 100pt; }
        .col-numeric { width: 50pt; text-align: right; }
        .col-percentage { width: 45pt; text-align: center; }
        .col-status { width: 45pt; text-align: center; }
        ```

        ## RESTRICTIONS - Never Use These
        ```html
        <!-- Forbidden HTML -->
        <video>, <audio>, <canvas>, <svg>, <script>
        <form>, <input>, <button>
        <section>, <article>, <nav>, <main>
        ```

        ```css
        /* Forbidden CSS */
        display: flex; /* No flexbox */
        display: grid; /* No grid */
        :hover, :nth-child(); /* No pseudo-classes */
        font-size: 1rem; /* No relative units */
        width: 50%; /* No percentage widths */
        var(--custom); /* No CSS variables */
        @media queries; /* Not supported */
        ```

        ## Template Structure
        ```html
        <!DOCTYPE html>
        <html>
        <head>
        <style>
        /* CSS styles here - optimized for PDF */
        .report-title { font-size: 16pt; font-weight: bold; text-align: center; margin: 15pt; }
        .data-table {
            width: 500pt;
            table-layout: fixed;
            border-collapse: collapse;
            font-size: 8pt;
            margin: 10pt 0;
        }
        .data-table th {
            background-color: #f0f0f0;
            padding: 4pt;
            border: 1pt solid #000;
            font-weight: bold;
        }
        .data-table td {
            padding: 3pt;
            border: 1pt solid #ccc;
            word-wrap: break-word;
            vertical-align: top;
        }
        </style>
        </head>
        <body>

        <div class="report-title">ROI Performance Report</div>

        <!-- Executive Summary Section -->
        <h2>Executive Summary</h2>
        <!-- Summary content here -->

        <!-- Platform Performance Section -->
        <h2>Platform Performance</h2>
        <table class="data-table">
        <thead>
        <tr>
            <th class="col-platform">Platform</th>
            <th class="col-numeric">Revenue</th>
            <th class="col-numeric">Cost</th>
            <th class="col-numeric">ROI</th>
            <!-- Add other columns based on actual data -->
        </tr>
        </thead>
        <tbody>
        <!-- Populate with actual data -->
        </tbody>
        </table>

        <!-- Add page break if needed -->
        <pdf:nextpage />

        <!-- Detailed Campaign Data Section -->
        <h2>Campaign Performance Details</h2>
        <!-- Table structure here -->

        </body>
        </html>
        ```

        ## Data Processing Rules
        1. **Format dates** consistently (YYYY-MM-DD or DD/MM/YYYY)
        2. **Round numerical values** to 2-3 decimal places for readability
        3. **Replace null/undefined** values with "-" or "N/A"
        4. **Break long text** appropriately using word-wrap
        5. **Group related data** logically with proper headers
        6. **Add page breaks** before new major sections
        7. **Handle boolean values** as "Yes/No" or "True/False"

        ## Quality Checklist
        - [ ] All data is included
        - [ ] Tables use fixed layout with explicit widths
        - [ ] Font sizes are in pt units
        - [ ] No CSS properties that xhtml2pdf doesn't support
        - [ ] Proper page break handling
        - [ ] Clear, readable formatting
        - [ ] Professional appearance
        - [ ] Data doesn't overflow table boundaries

        **Remember: Output ONLY the HTML/CSS code that can be directly passed to xhtml2pdf. No explanations, no markdown formatting, just clean HTML/CSS code.**
        """
    
    def _get_default_css(self) -> str:
        """Returns default CSS optimized for xhtml2pdf"""
        return """
        /* Default CSS for ROI Reports */
        body {
            font-family: "Arial", "Helvetica", sans-serif;
            font-size: 10pt;
            line-height: 1.2;
            color: #000000;
            margin: 20pt;
        }
        
        .report-title {
            font-size: 18pt;
            font-weight: bold;
            text-align: center;
            margin: 15pt 0 20pt 0;
            color: #2c3e50;
        }
        
        .report-subtitle {
            font-size: 12pt;
            text-align: center;
            margin: 10pt 0 15pt 0;
            color: #7f8c8d;
        }
        
        .section-header {
            font-size: 14pt;
            font-weight: bold;
            margin: 15pt 0 8pt 0;
            color: #34495e;
            border-bottom: 2pt solid #3498db;
            padding-bottom: 3pt;
        }
        
        .subsection-header {
            font-size: 12pt;
            font-weight: bold;
            margin: 12pt 0 6pt 0;
            color: #2c3e50;
        }
        
        .data-table {
            width: 500pt;
            table-layout: fixed;
            border-collapse: collapse;
            margin: 8pt 0;
            font-size: 9pt;
        }
        
        .data-table th {
            background-color: #ecf0f1;
            padding: 4pt;
            border: 1pt solid #bdc3c7;
            font-weight: bold;
            text-align: center;
            color: #2c3e50;
        }
        
        .data-table td {
            padding: 3pt;
            border: 1pt solid #ecf0f1;
            word-wrap: break-word;
            vertical-align: top;
        }
        
        .data-table tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        
        .col-date { width: 80pt; }
        .col-platform { width: 70pt; }
        .col-campaign { width: 120pt; }
        .col-numeric { width: 60pt; text-align: right; }
        .col-percentage { width: 50pt; text-align: center; }
        .col-status { width: 50pt; text-align: center; }
        .col-description { width: 150pt; }
        
        .metric-highlight {
            background-color: #e8f5e8;
            padding: 2pt;
            border-radius: 2pt;
            font-weight: bold;
        }
        
        .metric-warning {
            background-color: #fff3cd;
            padding: 2pt;
            border-radius: 2pt;
        }
        
        .metric-danger {
            background-color: #f8d7da;
            padding: 2pt;
            border-radius: 2pt;
        }
        
        .summary-box {
            border: 1pt solid #bdc3c7;
            padding: 8pt;
            margin: 8pt 0;
            background-color: #f8f9fa;
        }
        
        .page-break {
            page-break-before: always;
        }
        
        .keep-together {
            -pdf-keep-with-next: true;
        }
        """
    
    async def convert_html_to_pdf(self, html_content: str, output_path: Optional[str] = None) -> Tuple[bytes, str]:
        """
        Convert HTML content to PDF using xhtml2pdf
        
        Args:
            html_content: HTML string to convert
            output_path: Optional path to save the PDF file
            
        Returns:
            Tuple of (pdf_bytes, filename)
        """
        if not XHTML2PDF_AVAILABLE:
            raise ImportError("xhtml2pdf is not installed. Please install with: pip install xhtml2pdf==0.2.13")
        
        try:
            # Create PDF in memory
            pdf_bytes_io = BytesIO()
            
            # Convert HTML to PDF
            error = pisa.CreatePDF(
                src=html_content,
                dest=pdf_bytes_io,
                show_error_as_pdf=True
            )
            
            if error.err:
                logger.error(f"PDF generation error: {error.err}")
                raise Exception(f"PDF generation failed: {error.err}")
            
            pdf_bytes = pdf_bytes_io.getvalue()
            
            # Generate filename if not provided
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"roi_report_{timestamp}.pdf"
            
            # Save to file if path provided
            if output_path:
                with open(output_path, "wb") as f:
                    f.write(pdf_bytes)
                logger.info(f"✅ PDF saved: {output_path}")
            
            return pdf_bytes, output_path
            
        except Exception as e:
            logger.error(f"PDF conversion error: {e}")
            raise
    
    async def generate_pdf_from_json_data(self, json_data: Dict[str, Any], output_path: Optional[str] = None) -> Tuple[bytes, str]:
        """
        Generate PDF from JSON data using AI to create HTML first
        
        Args:
            json_data: JSON data to convert to PDF
            output_path: Optional path to save the PDF file
            
        Returns:
            Tuple of (pdf_bytes, filename)
        """
        if not GEMINI_AVAILABLE:
            raise ImportError("Google GenAI not available for AI-powered HTML generation")
        
        try:
            # Create AI prompt for HTML generation
            prompt = self.instruction_prompt.format(
                final_comprehensive_report=json.dumps(json_data, indent=2)
            )
            
            # Generate HTML using Gemini
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            
            if not response.text:
                raise Exception("AI failed to generate HTML content")
            
            # Extract HTML content (remove any markdown formatting)
            html_content = response.text.strip()
            if html_content.startswith("```html"):
                html_content = html_content[7:]
            if html_content.endswith("```"):
                html_content = html_content[:-3]
            
            # Convert HTML to PDF
            return await self.convert_html_to_pdf(html_content, output_path)
            
        except Exception as e:
            logger.error(f"AI-powered PDF generation error: {e}")
            raise
    
    async def create_simple_roi_pdf(self, roi_data: Dict[str, Any], output_path: Optional[str] = None) -> Tuple[bytes, str]:
        """
        Create a simple ROI PDF without AI (fallback method)
        
        Args:
            roi_data: ROI data dictionary
            output_path: Optional path to save the PDF file
            
        Returns:
            Tuple of (pdf_bytes, filename)
        """
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
        {self.default_css}
        </style>
        </head>
        <body>
        
        <div class="report-title">ROI Performance Report</div>
        <div class="report-subtitle">Generated on {timestamp}</div>
        
        <div class="summary-box">
        <div class="section-header">Executive Summary</div>
        <p>This report contains ROI performance data across multiple platforms and campaigns.</p>
        </div>
        
        """
        
        # Add platform performance if available
        if 'platforms' in roi_data:
            html += """
            <div class="section-header">Platform Performance</div>
            <table class="data-table">
            <thead>
            <tr>
                <th class="col-platform">Platform</th>
                <th class="col-numeric">Revenue</th>
                <th class="col-numeric">Cost</th>
                <th class="col-numeric">ROI</th>
                <th class="col-percentage">ROI %</th>
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
                    <td class="col-numeric">${revenue:,.2f}</td>
                    <td class="col-numeric">${cost:,.2f}</td>
                    <td class="col-numeric">${roi:,.2f}</td>
                    <td class="col-percentage">{roi_percentage:.1f}%</td>
                </tr>
                """
            
            html += """
            </tbody>
            </table>
            """
        
        # Add campaign details if available
        if 'campaigns' in roi_data:
            html += """
            <div class="page-break"></div>
            <div class="section-header">Campaign Details</div>
            <table class="data-table">
            <thead>
            <tr>
                <th class="col-date">Date</th>
                <th class="col-platform">Platform</th>
                <th class="col-campaign">Campaign</th>
                <th class="col-numeric">Revenue</th>
                <th class="col-numeric">Cost</th>
                <th class="col-numeric">ROI</th>
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
                    <td class="col-numeric">${revenue:,.2f}</td>
                    <td class="col-numeric">${cost:,.2f}</td>
                    <td class="col-numeric">${roi:,.2f}</td>
                </tr>
                """
            
            html += """
            </tbody>
            </table>
            """
        
        html += """
        <div class="page-break"></div>
        <div class="summary-box">
        <p><strong>Report Generated by:</strong> BOS Solution ROI Analytics System</p>
        <p><strong>Report ID:</strong> """ + datetime.now().strftime("%Y%m%d_%H%M%S") + """</p>
        </div>
        
        </body>
        </html>
        """
        
        return html
    
    async def save_generated_report(self, callback_context: CallbackContext) -> bool:
        """
        Save generated PDF report bytes as an artifact (for Google ADK integration)
        
        Args:
            callback_context: Google ADK callback context
            
        Returns:
            True if successful, False otherwise
        """
        if not CallbackContext:
            logger.warning("Google ADK not available - skipping artifact save")
            return False
        
        try:
            html_content = callback_context.state.get("final_html")
            if not html_content:
                logger.error("No HTML content found in callback context")
                return False
            
            # Convert HTML to PDF
            pdf_bytes, _ = await self.convert_html_to_pdf(html_content)
            
            # Save to callback context
            callback_context.state["report_bytes"] = pdf_bytes
            
            # Create artifact
            report_artifact = types.Part.from_bytes(
                data=pdf_bytes, 
                mime_type="application/pdf"
            )
            filename = "generated_report.pdf"
            
            # Save artifact
            version = await callback_context.save_artifact(
                filename=filename, 
                artifact=report_artifact
            )
            
            logger.info(f"✅ Successfully saved PDF artifact '{filename}' as version {version}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving PDF artifact: {e}")
            return False
    
    async def save_generated_report_local(self, html_content: str, output_path: str = "generated_report.pdf") -> bool:
        """
        Save generated PDF report locally as a file
        
        Args:
            html_content: HTML content to convert
            output_path: Path to save the PDF file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            pdf_bytes, _ = await self.convert_html_to_pdf(html_content, output_path)
            logger.info(f"✅ PDF saved locally: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving PDF locally: {e}")
            return False
    
    def save_generated_report_local_sync(self, html_content: str, output_path: str = "generated_report.pdf") -> bool:
        """
        Save generated PDF report locally as a file (synchronous version)
        
        Args:
            html_content: HTML content to convert
            output_path: Path to save the PDF file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import asyncio
            pdf_bytes, _ = asyncio.run(self.convert_html_to_pdf(html_content, output_path))
            logger.info(f"✅ PDF saved locally: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving PDF locally: {e}")
            return False


# Global instance for easy access
pdf_agent = PDFConversionAgent()


async def convert_html_to_pdf_async(html_content: str, output_path: Optional[str] = None) -> Tuple[bytes, str]:
    """
    Async wrapper for HTML to PDF conversion
    
    Args:
        html_content: HTML string to convert
        output_path: Optional path to save the PDF file
        
    Returns:
        Tuple of (pdf_bytes, filename)
    """
    return await pdf_agent.convert_html_to_pdf(html_content, output_path)


async def generate_pdf_from_json_async(json_data: Dict[str, Any], output_path: Optional[str] = None) -> Tuple[bytes, str]:
    """
    Async wrapper for JSON to PDF conversion using AI
    
    Args:
        json_data: JSON data to convert to PDF
        output_path: Optional path to save the PDF file
        
    Returns:
        Tuple of (pdf_bytes, filename)
    """
    return await pdf_agent.generate_pdf_from_json_data(json_data, output_path)


def convert_html_to_pdf_sync(html_content: str, output_path: Optional[str] = None) -> Tuple[bytes, str]:
    """
    Synchronous wrapper for HTML to PDF conversion
    
    Args:
        html_content: HTML string to convert
        output_path: Optional path to save the PDF file
        
    Returns:
        Tuple of (pdf_bytes, filename)
    """
    import asyncio
    return asyncio.run(pdf_agent.convert_html_to_pdf(html_content, output_path))


def generate_pdf_from_json_sync(json_data: Dict[str, Any], output_path: Optional[str] = None) -> Tuple[bytes, str]:
    """
    Synchronous wrapper for JSON to PDF conversion using AI
    
    Args:
        json_data: JSON data to convert to PDF
        output_path: Optional path to save the PDF file
        
    Returns:
        Tuple of (pdf_bytes, filename)
    """
    import asyncio
    return asyncio.run(pdf_agent.generate_pdf_from_json_data(json_data, output_path))
