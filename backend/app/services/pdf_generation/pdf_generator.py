#!/usr/bin/env python3
"""
PDF Generation Service using xhtml2pdf
Handles the agent flow: analyze ROI metrics -> generate HTML -> convert to PDF
"""

import asyncio
import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import logging

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

# Import xhtml2pdf first
try:
    from xhtml2pdf import pisa
    XHTML2PDF_AVAILABLE = True
    print("✅ xhtml2pdf import successful")
except ImportError as e:
    XHTML2PDF_AVAILABLE = False
    print(f"❌ xhtml2pdf import failed: {e}")
    # Try alternative import
    try:
        import xhtml2pdf
        from xhtml2pdf import pisa
        XHTML2PDF_AVAILABLE = True
        print("✅ xhtml2pdf import successful (alternative method)")
    except ImportError:
        XHTML2PDF_AVAILABLE = False
        print("❌ xhtml2pdf import failed (alternative method also failed)")

# Now import app modules
from app.core.supabase_client import supabase_client
from app.services.pdf_generation.ai_agent import ROIReportAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFGenerator:
    """
    Main PDF generation service that orchestrates the agent flow
    """
    
    def __init__(self):
        self.xhtml2pdf_available = XHTML2PDF_AVAILABLE
        self.ai_agent = ROIReportAgent()
        
        if not self.xhtml2pdf_available:
            logger.warning("xhtml2pdf not available. PDF generation will be limited.")
    
    async def generate_roi_report(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Main method to generate ROI report using the agent flow:
        1. Analyze ROI metrics
        2. Generate HTML report
        3. Convert HTML to PDF
        4. Return content for download (no server storage)
        """
        try:
            logger.info("🚀 Starting ROI report generation with agent flow...")
            
            # Step 1: Analyze ROI metrics and generate HTML
            logger.info("📊 Step 1: Analyzing ROI metrics and generating HTML...")
            html_content, report_data = await self.ai_agent.generate_html_report()
            
            if not html_content:
                raise Exception("Failed to generate HTML content")
            
            # Step 2: Convert HTML to PDF using xhtml2pdf
            logger.info("📄 Step 2: Converting HTML to PDF...")
            pdf_bytes = await self.convert_html_to_pdf(html_content)
            
            if not pdf_bytes:
                raise Exception("Failed to convert HTML to PDF")
            
            # Step 3: Extract text content
            logger.info("💾 Step 3: Preparing content for download...")
            text_content = self.extract_text_from_html(html_content)
            
            logger.info("✅ Report generation completed successfully!")
            
            # Convert PDF bytes to base64 string for JSON serialization
            import base64
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
            
            return {
                "success": True,
                "message": "ROI report generated successfully in multiple formats",
                "content": {
                    "html": html_content,
                    "pdf": pdf_base64,  # Base64 encoded string instead of binary bytes
                    "text": text_content,
                    "json": json.dumps(report_data, indent=2, default=str)
                },
                "filenames": {
                    "html": f"roi_report_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.html",
                    "pdf": f"roi_report_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf",
                    "text": f"roi_report_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt",
                    "json": f"roi_data_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
                },
                "generated_at": datetime.now().isoformat(),
                "report_data": report_data
            }
            
        except Exception as e:
            logger.error(f"❌ Report generation failed: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to generate report: {str(e)}",
                "error": str(e),
                "generated_at": datetime.now().isoformat()
            }
    
    async def convert_html_to_pdf(self, html_content: str) -> Optional[bytes]:
        """
        Convert HTML content to PDF using xhtml2pdf with landscape orientation
        """
        if not self.xhtml2pdf_available:
            raise ImportError("xhtml2pdf is not installed. Please install with: pip install xhtml2pdf==0.2.13")
        
        try:
            logger.info("🔄 Converting HTML to PDF using xhtml2pdf with portrait orientation...")
            
            # Create a BytesIO object to store the PDF
            from io import BytesIO
            pdf_buffer = BytesIO()
            
             # Convert HTML to PDF with portrait orientation
            conversion_result = pisa.CreatePDF(
                 html_content,
                 dest=pdf_buffer,
                 encoding='utf-8',
                 showBoundary=0,  # Hide page boundaries
                 pdf_background=None,  # No background
                 # Portrait orientation settings
                 orientation='portrait'
             )
            
            if conversion_result.err:
                logger.error(f"❌ PDF conversion failed: {conversion_result.err}")
                return None
            
            # Get the PDF bytes
            pdf_bytes = pdf_buffer.getvalue()
            pdf_buffer.close()
            
            logger.info(f"✅ PDF conversion successful with portrait orientation. Size: {len(pdf_bytes)} bytes")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"❌ PDF conversion error: {str(e)}")
            return None
    
    def extract_text_from_html(self, html_content: str) -> str:
        """
        Extract plain text from HTML content for text report
        """
        try:
            from bs4 import BeautifulSoup
            
            # Parse HTML and extract text
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text and clean it up
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text
            
        except ImportError:
            # Fallback: simple regex-based text extraction
            import re
            # Remove HTML tags
            text = re.sub(r'<[^>]+>', '', html_content)
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            return text
        except Exception as e:
            logger.error(f"❌ Text extraction failed: {str(e)}")
            return "Text extraction failed. Please view the HTML version."

# Standalone function for backward compatibility
async def generate_roi_report(user_id: Optional[str] = None) -> bool:
    """
    Standalone function for backward compatibility
    Returns True if successful, False otherwise
    """
    try:
        pdf_generator = PDFGenerator()
        result = await pdf_generator.generate_roi_report(user_id)
        return result.get("success", False)
    except Exception as e:
        logger.error(f"❌ Standalone report generation failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Test the PDF generator
    async def test():
        pdf_generator = PDFGenerator()
        result = await pdf_generator.generate_roi_report()
        print(f"Test result: {result}")
    
    asyncio.run(test())
