"""
PDF Conversion Endpoints
Integrates with ROI system to convert HTML reports to PDF
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.responses import StreamingResponse, FileResponse
from typing import Dict, Any, Optional
import os
import tempfile
from datetime import datetime
import json

from app.services.pdf_conversion_agent import (
    pdf_agent, 
    convert_html_to_pdf_async,
    generate_pdf_from_json_async
)

router = APIRouter()


@router.post("/convert-html-to-pdf", tags=["pdf"])
async def convert_html_to_pdf_endpoint(
    html_content: str,
    filename: Optional[str] = None
):
    """
    Convert HTML content to PDF using xhtml2pdf
    
    Args:
        html_content: HTML string to convert
        filename: Optional filename for the PDF
        
    Returns:
        PDF file as streaming response
    """
    try:
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"roi_report_{timestamp}.pdf"
        
        # Convert HTML to PDF
        pdf_bytes, _ = await convert_html_to_pdf_async(html_content)
        
        # Return PDF as streaming response
        return StreamingResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF conversion failed: {str(e)}")


@router.post("/convert-json-to-pdf", tags=["pdf"])
async def convert_json_to_pdf_endpoint(
    json_data: Dict[str, Any],
    filename: Optional[str] = None
):
    """
    Convert JSON data to PDF using AI-powered HTML generation
    
    Args:
        json_data: JSON data to convert to PDF
        filename: Optional filename for the PDF
        
    Returns:
        PDF file as streaming response
    """
    try:
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"roi_report_{timestamp}.pdf"
        
        # Convert JSON to PDF using AI
        pdf_bytes, _ = await generate_pdf_from_json_async(json_data)
        
        # Return PDF as streaming response
        return StreamingResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF conversion failed: {str(e)}")


@router.post("/upload-html-and-convert", tags=["pdf"])
async def upload_html_and_convert(
    html_file: UploadFile = File(...),
    filename: Optional[str] = None
):
    """
    Upload HTML file and convert to PDF
    
    Args:
        html_file: HTML file to upload
        filename: Optional filename for the PDF
        
    Returns:
        PDF file as streaming response
    """
    try:
        # Read HTML content from uploaded file
        html_content = await html_file.read()
        html_content = html_content.decode('utf-8')
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"roi_report_{timestamp}.pdf"
        
        # Convert HTML to PDF
        pdf_bytes, _ = await convert_html_to_pdf_async(html_content)
        
        # Return PDF as streaming response
        return StreamingResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF conversion failed: {str(e)}")


@router.post("/roi-report-to-pdf", tags=["pdf"])
async def roi_report_to_pdf(
    report_data: Dict[str, Any],
    filename: Optional[str] = None
):
    """
    Convert ROI report data to PDF (specialized for ROI reports)
    
    Args:
        report_data: ROI report data structure
        filename: Optional filename for the PDF
        
    Returns:
        PDF file as streaming response
    """
    try:
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"roi_report_{timestamp}.pdf"
        
        # Create simple ROI PDF (fallback method)
        pdf_bytes, _ = await pdf_agent.create_simple_roi_pdf(report_data)
        
        # Return PDF as streaming response
        return StreamingResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ROI PDF conversion failed: {str(e)}")


@router.post("/save-pdf-locally", tags=["pdf"])
async def save_pdf_locally(
    html_content: str,
    filename: Optional[str] = None
):
    """
    Convert HTML to PDF and save locally
    
    Args:
        html_content: HTML string to convert
        filename: Optional filename for the PDF
        
    Returns:
        JSON response with file path
    """
    try:
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"roi_report_{timestamp}.pdf"
        
        # Create temporary directory for saving
        temp_dir = tempfile.mkdtemp()
        output_path = os.path.join(temp_dir, filename)
        
        # Convert HTML to PDF and save
        pdf_bytes, saved_path = await convert_html_to_pdf_async(html_content, output_path)
        
        return {
            "success": True,
            "message": "PDF saved successfully",
            "file_path": saved_path,
            "file_size": len(pdf_bytes),
            "filename": filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF save failed: {str(e)}")


@router.get("/download-pdf/{filename}", tags=["pdf"])
async def download_pdf(filename: str):
    """
    Download a previously saved PDF file
    
    Args:
        filename: Name of the PDF file to download
        
    Returns:
        PDF file as file response
    """
    try:
        # Look for the file in common locations
        possible_paths = [
            filename,  # Direct path
            os.path.join(os.getcwd(), filename),  # Current directory
            os.path.join(tempfile.gettempdir(), filename),  # Temp directory
        ]
        
        file_path = None
        for path in possible_paths:
            if os.path.exists(path):
                file_path = path
                break
        
        if not file_path:
            raise HTTPException(status_code=404, detail=f"PDF file '{filename}' not found")
        
        return FileResponse(
            path=file_path,
            media_type="application/pdf",
            filename=filename
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF download failed: {str(e)}")


@router.get("/health", tags=["pdf"])
async def pdf_health_check():
    """
    Health check for PDF conversion service
    
    Returns:
        Health status
    """
    try:
        # Test basic PDF conversion with simple HTML
        test_html = """
        <!DOCTYPE html>
        <html>
        <head>
        <style>
        body { font-family: Arial; font-size: 12pt; }
        </style>
        </head>
        <body>
        <h1>Test PDF</h1>
        <p>This is a test PDF generated at """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
        </body>
        </html>
        """
        
        pdf_bytes, _ = await convert_html_to_pdf_async(test_html)
        
        return {
            "status": "healthy",
            "service": "PDF Conversion Agent",
            "timestamp": datetime.now().isoformat(),
            "test_pdf_size": len(pdf_bytes),
            "xhtml2pdf_available": True
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "PDF Conversion Agent",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "xhtml2pdf_available": False
        }
