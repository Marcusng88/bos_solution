#!/usr/bin/env python3
"""
Standalone PDF Generator - Only depends on Gemini output
Generates a complete PDF format report without external dependencies
"""

import os
import sys
import json
import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import io

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent))

class StandalonePDFGenerator:
    """
    Standalone PDF generator that creates professional PDF reports
    using only Python standard library and minimal dependencies
    """
    
    def __init__(self):
        self.pdf_content = []
        self.current_y = 750  # Starting Y position (points)
        self.page_height = 792  # Letter size height
        self.margin = 72  # 1 inch margins
        self.line_height = 14
        self.font_size = 12
        self.bold_font_size = 14
        
    def add_text(self, text: str, x: int = None, y: int = None, 
                 font_size: int = None, bold: bool = False, 
                 center: bool = False, color: str = "000000"):
        """Add text to PDF content"""
        if x is None:
            x = self.margin
        if y is None:
            y = self.current_y
        if font_size is None:
            font_size = self.bold_font_size if bold else self.font_size
            
        font_name = "Helvetica-Bold" if bold else "Helvetica"
        
        # Handle text centering
        if center:
            # Simple centering - in a real implementation, you'd calculate text width
            x = 396  # Center of page (612/2)
        
        text_obj = {
            'type': 'text',
            'x': x,
            'y': y,
            'text': text,
            'font': font_name,
            'font_size': font_size,
            'color': color
        }
        
        self.pdf_content.append(text_obj)
        self.current_y -= font_size + 4
        
    def add_line(self, y: int = None, color: str = "000000"):
        """Add a horizontal line"""
        if y is None:
            y = self.current_y + 10
            
        line_obj = {
            'type': 'line',
            'x1': self.margin,
            'y1': y,
            'x2': 612 - self.margin,  # Page width - margin
            'y2': y,
            'color': color,
            'width': 1
        }
        
        self.pdf_content.append(line_obj)
        self.current_y -= 20
        
    def add_rectangle(self, x: int, y: int, width: int, height: int, 
                     fill_color: str = None, stroke_color: str = "000000"):
        """Add a rectangle"""
        rect_obj = {
            'type': 'rectangle',
            'x': x,
            'y': y,
            'width': width,
            'height': height,
            'fill_color': fill_color,
            'stroke_color': stroke_color
        }
        
        self.pdf_content.append(rect_obj)
        
    def add_table(self, data: list, x: int = None, y: int = None):
        """Add a simple table"""
        if x is None:
            x = self.margin
        if y is None:
            y = self.current_y
            
        table_obj = {
            'type': 'table',
            'x': x,
            'y': y,
            'data': data
        }
        
        self.pdf_content.append(table_obj)
        
        # Estimate table height and adjust current_y
        rows = len(data)
        self.current_y -= (rows * 20) + 20
        
    def new_page(self):
        """Start a new page"""
        self.pdf_content.append({'type': 'new_page'})
        self.current_y = 750
        
    def generate_pdf_bytes(self) -> bytes:
        """Generate PDF as bytes using minimal PDF format"""
        pdf_content = self._create_pdf_header()
        pdf_content += self._create_pdf_objects()
        pdf_content += self._create_pdf_trailer()
        return pdf_content.encode('latin-1')
        
    def _create_pdf_header(self) -> str:
        """Create PDF header"""
        return "%PDF-1.4\n"
        
    def _create_pdf_objects(self) -> str:
        """Create PDF objects for content"""
        objects = []
        object_count = 1
        
        # Add font objects
        helvetica_obj = f"{object_count} 0 obj\n<<\n/Type /Font\n/Subtype /Type1\n/BaseFont /Helvetica\n>>\nendobj\n"
        objects.append(helvetica_obj)
        object_count += 1
        
        helvetica_bold_obj = f"{object_count} 0 obj\n<<\n/Type /Font\n/Subtype /Type1\n/BaseFont /Helvetica-Bold\n>>\nendobj\n"
        objects.append(helvetica_bold_obj)
        object_count += 1
        
        # Add content stream
        content_stream = self._create_content_stream()
        content_obj = f"{object_count} 0 obj\n<<\n/Length {len(content_stream)}\n>>\nstream\n{content_stream}\nendstream\nendobj\n"
        objects.append(content_obj)
        content_obj_id = object_count
        object_count += 1
        
        # Add page object
        page_obj = f"{object_count} 0 obj\n<<\n/Type /Page\n/Parent 4 0 R\n/MediaBox [0 0 612 792]\n/Contents {content_obj_id} 0 R\n/Resources <<\n/Font <<\n/F1 1 0 R\n/F2 2 0 R\n>>\n>>\n>>\nendobj\n"
        objects.append(page_obj)
        page_obj_id = object_count
        object_count += 1
        
        # Add pages object
        pages_obj = f"{object_count} 0 obj\n<<\n/Type /Pages\n/Kids [{page_obj_id} 0 R]\n/Count 1\n>>\nendobj\n"
        objects.append(pages_obj)
        pages_obj_id = object_count
        object_count += 1
        
        # Add catalog object
        catalog_obj = f"{object_count} 0 obj\n<<\n/Type /Catalog\n/Pages {pages_obj_id} 0 R\n>>\nendobj\n"
        objects.append(catalog_obj)
        catalog_obj_id = object_count
        
        return "".join(objects)
        
    def _create_content_stream(self) -> str:
        """Create PDF content stream"""
        stream = "BT\n"  # Begin text
        
        for item in self.pdf_content:
            if item['type'] == 'text':
                stream += f"/F{item['font'] == 'Helvetica-Bold' and '2' or '1'} {item['font_size']} Tf\n"
                stream += f"1 0 0 1 {item['x']} {item['y']} Tm\n"
                stream += f"({item['text']}) Tj\n"
            elif item['type'] == 'line':
                stream += "ET\n"  # End text
                stream += f"{item['x1']} {item['y1']} m\n"
                stream += f"{item['x2']} {item['y2']} l\n"
                stream += "S\n"  # Stroke
                stream += "BT\n"  # Begin text again
            elif item['type'] == 'new_page':
                stream += "ET\n"  # End text
                stream += "showpage\n"  # Show page
                stream += "BT\n"  # Begin text for new page
                
        stream += "ET\n"  # End text
        return stream
        
    def _create_pdf_trailer(self) -> str:
        """Create PDF trailer"""
        return "xref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000068 00000 n \n0000000127 00000 n \n0000000186 00000 n \n0000000245 00000 n \ntrailer\n<<\n/Size 5\n/Root 5 0 R\n>>\nstartxref\n300\n%%EOF\n"


def create_simple_pdf_from_gemini_output(gemini_output: str, report_data: Dict[str, Any] = None) -> bytes:
    """
    Create a simple PDF from Gemini output without external dependencies
    
    Args:
        gemini_output: The text output from Gemini
        report_data: Optional data for metrics and formatting
        
    Returns:
        PDF content as bytes
    """
    
    # Create a simple text-based PDF
    pdf_lines = []
    
    # PDF Header
    pdf_lines.append("%PDF-1.4")
    pdf_lines.append("1 0 obj")
    pdf_lines.append("<<")
    pdf_lines.append("/Type /Catalog")
    pdf_lines.append("/Pages 2 0 R")
    pdf_lines.append(">>")
    pdf_lines.append("endobj")
    
    # Pages object
    pdf_lines.append("2 0 obj")
    pdf_lines.append("<<")
    pdf_lines.append("/Type /Pages")
    pdf_lines.append("/Kids [3 0 R]")
    pdf_lines.append("/Count 1")
    pdf_lines.append(">>")
    pdf_lines.append("endobj")
    
    # Page object
    pdf_lines.append("3 0 obj")
    pdf_lines.append("<<")
    pdf_lines.append("/Type /Page")
    pdf_lines.append("/Parent 2 0 R")
    pdf_lines.append("/MediaBox [0 0 612 792]")
    pdf_lines.append("/Contents 4 0 R")
    pdf_lines.append("/Resources <<")
    pdf_lines.append("/Font <<")
    pdf_lines.append("/F1 <<")
    pdf_lines.append("/Type /Font")
    pdf_lines.append("/Subtype /Type1")
    pdf_lines.append("/BaseFont /Helvetica")
    pdf_lines.append(">>")
    pdf_lines.append(">>")
    pdf_lines.append(">>")
    pdf_lines.append(">>")
    pdf_lines.append("endobj")
    
    # Content stream
    content = "BT\n"
    content += "/F1 12 Tf\n"
    
    # Add title
    content += "1 0 0 1 72 720 Tm\n"
    content += "(ROI Performance Report) Tj\n"
    
    # Add date
    content += "1 0 0 1 72 700 Tm\n"
    content += f"({datetime.now().strftime('%B %d, %Y at %I:%M %p')}) Tj\n"
    
    # Add Gemini output content
    y_position = 660
    lines = gemini_output.split('\n')
    
    for line in lines[:50]:  # Limit to first 50 lines to fit on page
        if y_position < 72:  # Bottom margin
            break
        content += f"1 0 0 1 72 {y_position} Tm\n"
        content += f"({line[:80]}) Tj\n"  # Limit line length
        y_position -= 20
        
    content += "ET\n"
    
    # Content object
    pdf_lines.append("4 0 obj")
    pdf_lines.append(f"<<\n/Length {len(content)}\n>>")
    pdf_lines.append("stream")
    pdf_lines.append(content)
    pdf_lines.append("endstream")
    pdf_lines.append("endobj")
    
    # XRef table
    pdf_lines.append("xref")
    pdf_lines.append("0 5")
    pdf_lines.append("0000000000 65535 f ")
    pdf_lines.append("0000000009 00000 n ")
    pdf_lines.append("0000000068 00000 n ")
    pdf_lines.append("0000000127 00000 n ")
    pdf_lines.append("0000000186 00000 n ")
    
    # Trailer
    pdf_lines.append("trailer")
    pdf_lines.append("<<")
    pdf_lines.append("/Size 5")
    pdf_lines.append("/Root 1 0 R")
    pdf_lines.append(">>")
    pdf_lines.append("startxref")
    pdf_lines.append("300")
    pdf_lines.append("%%EOF")
    
    return "\n".join(pdf_lines).encode('latin-1')


def generate_standalone_pdf_report(gemini_output: str, report_data: Dict[str, Any] = None, 
                                 output_filename: str = None) -> str:
    """
    Generate a standalone PDF report from Gemini output
    
    Args:
        gemini_output: The text output from Gemini
        report_data: Optional data for metrics and formatting
        output_filename: Optional output filename
        
    Returns:
        Path to the generated PDF file
    """
    
    if output_filename is None:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_filename = f"standalone_roi_report_{timestamp}.pdf"
    
    try:
        # Generate PDF content
        pdf_bytes = create_simple_pdf_from_gemini_output(gemini_output, report_data)
        
        # Write to file
        with open(output_filename, 'wb') as f:
            f.write(pdf_bytes)
            
        print(f"✅ Standalone PDF generated: {output_filename}")
        return output_filename
        
    except Exception as e:
        print(f"❌ Error generating standalone PDF: {e}")
        return None


def create_html_template_for_pdf(gemini_output: str, report_data: Dict[str, Any] = None) -> str:
    """
    Create a simple HTML template that can be easily converted to PDF
    """
    
    # Extract metrics if available
    metrics = {}
    if report_data:
        totals = report_data.get('all_data', {}).get('totals', {})
        metrics = {
            'total_revenue': totals.get('total_revenue', 0),
            'total_spend': totals.get('total_spend', 0),
            'total_profit': totals.get('total_profit', 0),
            'total_roi': totals.get('total_roi', 0)
        }
    
    # Calculate ROI percentage
    roi_percentage = 0
    if metrics.get('total_spend', 0) > 0:
        roi_percentage = (metrics.get('total_roi', 0) / metrics.get('total_spend', 0)) * 100
    
    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ROI Performance Report</title>
    <style>
        @page {{
            size: A4;
            margin: 1in;
        }}
        
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #333;
            padding-bottom: 20px;
        }}
        
        .header h1 {{
            margin: 0;
            font-size: 24px;
            color: #2c3e50;
        }}
        
        .header .date {{
            margin-top: 10px;
            font-size: 14px;
            color: #7f8c8d;
        }}
        
        .metrics {{
            display: table;
            width: 100%;
            margin-bottom: 30px;
            border-collapse: collapse;
        }}
        
        .metric {{
            display: table-cell;
            text-align: center;
            padding: 15px;
            border: 1px solid #ddd;
            background-color: #f9f9f9;
        }}
        
        .metric .label {{
            font-size: 12px;
            color: #666;
            margin-bottom: 5px;
        }}
        
        .metric .value {{
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
        }}
        
        .content {{
            margin-top: 30px;
        }}
        
        .content h2 {{
            color: #2c3e50;
            border-bottom: 1px solid #ddd;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        
        .report-text {{
            white-space: pre-wrap;
            font-size: 14px;
            line-height: 1.8;
            background-color: #f8f9fa;
            padding: 20px;
            border-left: 4px solid #3498db;
            border-radius: 4px;
        }}
        
        .footer {{
            margin-top: 40px;
            text-align: center;
            font-size: 12px;
            color: #7f8c8d;
            border-top: 1px solid #ddd;
            padding-top: 20px;
        }}
        
        @media print {{
            body {{
                margin: 0;
                padding: 10px;
            }}
            
            .metric {{
                page-break-inside: avoid;
            }}
            
            .content {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 ROI Performance Report</h1>
        <div class="date">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</div>
    </div>
    
    <div class="metrics">
        <div class="metric">
            <div class="label">Total Revenue</div>
            <div class="value">${metrics.get('total_revenue', 0):,.2f}</div>
        </div>
        <div class="metric">
            <div class="label">Total Spend</div>
            <div class="value">${metrics.get('total_spend', 0):,.2f}</div>
        </div>
        <div class="metric">
            <div class="label">Total Profit</div>
            <div class="value">${metrics.get('total_profit', 0):,.2f}</div>
        </div>
        <div class="metric">
            <div class="label">ROI Percentage</div>
            <div class="value">{roi_percentage:.1f}%</div>
        </div>
    </div>
    
    <div class="content">
        <h2>📋 Executive Summary</h2>
        <div class="report-text">{gemini_output}</div>
    </div>
    
    <div class="footer">
        <p>Generated by BOS Solution ROI Analytics System</p>
        <p>Report ID: {datetime.now().strftime('%Y%m%d_%H%M%S')}</p>
    </div>
</body>
</html>
"""
    
    return html_template


def generate_html_for_pdf(gemini_output: str, report_data: Dict[str, Any] = None, 
                         output_filename: str = None) -> str:
    """
    Generate HTML file that can be easily converted to PDF
    
    Args:
        gemini_output: The text output from Gemini
        report_data: Optional data for metrics and formatting
        output_filename: Optional output filename
        
    Returns:
        Path to the generated HTML file
    """
    
    if output_filename is None:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_filename = f"roi_report_{timestamp}.html"
    
    try:
        # Generate HTML content
        html_content = create_html_template_for_pdf(gemini_output, report_data)
        
        # Write to file
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print(f"✅ HTML for PDF generated: {output_filename}")
        return output_filename
        
    except Exception as e:
        print(f"❌ Error generating HTML for PDF: {e}")
        return None


# Example usage and testing
if __name__ == "__main__":
    # Test with sample Gemini output
    sample_gemini_output = """
ROI Performance Analysis Report

Executive Summary:
This comprehensive ROI analysis covers all marketing campaigns across multiple platforms. The data shows strong performance with an overall positive return on investment.

Key Findings:
- Total revenue generated: $125,000
- Total marketing spend: $45,000
- Net profit: $80,000
- Overall ROI: 177.8%

Platform Performance:
1. YouTube: Highest performing platform with 245% ROI
2. Facebook: Strong performance with 156% ROI
3. Instagram: Moderate performance with 89% ROI
4. Google Ads: Lower performance with 67% ROI

Recommendations:
1. Increase investment in YouTube campaigns
2. Optimize Google Ads targeting
3. Expand Facebook presence
4. Review Instagram strategy

This analysis demonstrates excellent overall performance with opportunities for further optimization.
"""
    
    sample_report_data = {
        'all_data': {
            'totals': {
                'total_revenue': 125000,
                'total_spend': 45000,
                'total_profit': 80000,
                'total_roi': 80000
            }
        }
    }
    
    # Generate standalone PDF
    pdf_file = generate_standalone_pdf_report(sample_gemini_output, sample_report_data)
    
    # Generate HTML for PDF
    html_file = generate_html_for_pdf(sample_gemini_output, sample_report_data)
    
    print(f"\n📁 Generated files:")
    if pdf_file:
        print(f"   • {pdf_file} - Standalone PDF")
    if html_file:
        print(f"   • {html_file} - HTML for PDF conversion")
