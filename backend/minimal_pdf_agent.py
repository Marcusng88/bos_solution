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

# Global instance
minimal_pdf_agent = MinimalPDFAgent()

print(f"Minimal agent created:")
print(f"  XHTML2PDF_AVAILABLE: {XHTML2PDF_AVAILABLE}")
print(f"  GEMINI_AVAILABLE: {GEMINI_AVAILABLE}")
print(f"  Agent xhtml2pdf_available: {minimal_pdf_agent.xhtml2pdf_available}")
