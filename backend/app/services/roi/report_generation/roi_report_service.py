#!/usr/bin/env python3
"""
ROI Report Generation Service
Main service for generating ROI reports using the PDF generation system
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from app.services.pdf_generation.pdf_generator import PDFGenerator

class ROIReportService:
    """
    Service for generating ROI reports
    """
    
    def __init__(self):
        self.pdf_generator = PDFGenerator()
    
    async def generate_comprehensive_report(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive ROI report with multiple formats
        """
        try:
            # Use the PDF generator service
            result = await self.pdf_generator.generate_roi_report(user_id)
            return result
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to generate report: {str(e)}",
                "error": str(e),
                "generated_at": datetime.now().isoformat()
            }
    
    async def generate_html_only(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate HTML report only (without PDF conversion)
        """
        try:
            from app.services.pdf_generation.ai_agent import ROIReportAgent
            
            agent = ROIReportAgent()
            html_content, report_data = await agent.generate_html_report()
            
            if not html_content:
                return {
                    "success": False,
                    "message": "Failed to generate HTML content",
                    "generated_at": datetime.now().isoformat()
                }
            
            # Save HTML file
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            html_filename = f"roi_report_{timestamp}.html"
            html_path = Path(html_filename)
            html_path.write_text(html_content, encoding='utf-8')
            
            return {
                "success": True,
                "message": "HTML report generated successfully",
                "files": {
                    "html": html_filename
                },
                "generated_at": datetime.now().isoformat(),
                "report_data": report_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to generate HTML report: {str(e)}",
                "error": str(e),
                "generated_at": datetime.now().isoformat()
            }

# Standalone function for backward compatibility
async def generate_roi_report(user_id: Optional[str] = None) -> bool:
    """
    Standalone function for backward compatibility
    Returns True if successful, False otherwise
    """
    try:
        service = ROIReportService()
        result = await service.generate_comprehensive_report(user_id)
        return result.get("success", False)
    except Exception as e:
        print(f"❌ Standalone report generation failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Test the service
    async def test():
        service = ROIReportService()
        result = await service.generate_comprehensive_report()
        print(f"Test result: {result}")
    
    asyncio.run(test())
