#!/usr/bin/env python3
"""
Gemini PDF Generator - Standalone PDF generation from Gemini output
Generates complete PDF format reports without external dependencies
"""

import os
import sys
import json
import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import io

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent))

class GeminiPDFGenerator:
    """
    Standalone PDF generator that creates professional PDF reports
    from Gemini output without external dependencies
    """
    
    def __init__(self):
        self.pdf_objects = []
        self.object_count = 1
        self.content_streams = []
        self.current_stream = ""
        self.page_objects = []
        self.font_objects = {}
        
    def add_font(self, font_name: str, font_type: str = "Helvetica") -> int:
        """Add a font object and return its ID"""
        if font_name in self.font_objects:
            return self.font_objects[font_name]
            
        font_id = self.object_count
        self.object_count += 1
        
        font_obj = f"{font_id} 0 obj\n<<\n/Type /Font\n/Subtype /Type1\n/BaseFont /{font_type}\n>>\nendobj\n"
        self.pdf_objects.append(font_obj)
        self.font_objects[font_name] = font_id
        
        return font_id
        
    def add_text(self, text: str, x: float, y: float, font_size: int = 12, 
                 font_name: str = "Helvetica", color: str = "000000"):
        """Add text to the current content stream"""
        # Escape special characters in text
        escaped_text = text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
        
        # Add font if not already added
        font_id = self.add_font(font_name, font_name)
        
        # Add text to content stream
        self.current_stream += f"BT\n"
        self.current_stream += f"/F{font_id} {font_size} Tf\n"
        self.current_stream += f"1 0 0 1 {x} {y} Tm\n"
        self.current_stream += f"({escaped_text}) Tj\n"
        self.current_stream += f"ET\n"
        
    def add_line(self, x1: float, y1: float, x2: float, y2: float, 
                 width: float = 1, color: str = "000000"):
        """Add a line to the current content stream"""
        self.current_stream += f"{x1} {y1} m\n"
        self.current_stream += f"{x2} {y2} l\n"
        self.current_stream += f"{width} w\n"
        self.current_stream += f"S\n"
        
    def add_rectangle(self, x: float, y: float, width: float, height: float, 
                     fill: bool = False, stroke: bool = True, 
                     fill_color: str = "FFFFFF", stroke_color: str = "000000"):
        """Add a rectangle to the current content stream"""
        self.current_stream += f"{x} {y} {width} {height} re\n"
        
        if fill:
            self.current_stream += f"f\n"
        if stroke:
            self.current_stream += f"S\n"
            
    def new_page(self):
        """Start a new page"""
        # Save current content stream
        if self.current_stream:
            self.content_streams.append(self.current_stream)
            self.current_stream = ""
            
    def create_content_object(self, content: str) -> int:
        """Create a content stream object and return its ID"""
        content_id = self.object_count
        self.object_count += 1
        
        content_obj = f"{content_id} 0 obj\n<<\n/Length {len(content)}\n>>\nstream\n{content}\nendstream\nendobj\n"
        self.pdf_objects.append(content_obj)
        
        return content_id
        
    def create_page_object(self, content_id: int, media_box: List[float] = None) -> int:
        """Create a page object and return its ID"""
        if media_box is None:
            media_box = [0, 0, 612, 792]  # Letter size
            
        page_id = self.object_count
        self.object_count += 1
        
        # Create font resources
        font_resources = []
        for font_name, font_id in self.font_objects.items():
            font_resources.append(f"/{font_name} {font_id} 0 R")
        
        resources = f"<<\n/Font <<\n{chr(10).join(font_resources)}\n>>\n>>"
        
        page_obj = f"{page_id} 0 obj\n<<\n/Type /Page\n/Parent {self.object_count} 0 R\n/MediaBox {media_box}\n/Contents {content_id} 0 R\n/Resources {resources}\n>>\nendobj\n"
        self.pdf_objects.append(page_obj)
        self.page_objects.append(page_id)
        
        return page_id
        
    def create_pages_object(self, page_ids: List[int]) -> int:
        """Create a pages object and return its ID"""
        pages_id = self.object_count
        self.object_count += 1
        
        page_refs = " ".join([f"{pid} 0 R" for pid in page_ids])
        pages_obj = f"{pages_id} 0 obj\n<<\n/Type /Pages\n/Kids [{page_refs}]\n/Count {len(page_ids)}\n>>\nendobj\n"
        self.pdf_objects.append(pages_obj)
        
        return pages_id
        
    def create_catalog_object(self, pages_id: int) -> int:
        """Create a catalog object and return its ID"""
        catalog_id = self.object_count
        self.object_count += 1
        
        catalog_obj = f"{catalog_id} 0 obj\n<<\n/Type /Catalog\n/Pages {pages_id} 0 R\n>>\nendobj\n"
        self.pdf_objects.append(catalog_obj)
        
        return catalog_id
        
    def generate_pdf_bytes(self) -> bytes:
        """Generate the complete PDF as bytes"""
        # Add any remaining content stream
        if self.current_stream:
            self.content_streams.append(self.current_stream)
            
        # Create content objects
        content_ids = []
        for content in self.content_streams:
            content_id = self.create_content_object(content)
            content_ids.append(content_id)
            
        # Create page objects
        page_ids = []
        for i, content_id in enumerate(content_ids):
            page_id = self.create_page_object(content_id)
            page_ids.append(page_id)
            
        # Create pages object
        pages_id = self.create_pages_object(page_ids)
        
        # Create catalog object
        catalog_id = self.create_catalog_object(pages_id)
        
        # Build PDF content
        pdf_content = "%PDF-1.4\n"
        
        # Add all objects
        for obj in self.pdf_objects:
            pdf_content += obj
            
        # Create xref table
        xref_offset = len(pdf_content)
        xref_entries = []
        
        # Add free entry
        xref_entries.append("0000000000 65535 f ")
        
        # Add object entries
        current_offset = 9  # After PDF header
        for obj in self.pdf_objects:
            xref_entries.append(f"{current_offset:010d} 00000 n ")
            current_offset += len(obj)
            
        # Create xref section
        xref_content = "xref\n"
        xref_content += f"0 {len(xref_entries)}\n"
        xref_content += "".join(xref_entries)
        
        # Create trailer
        trailer_content = "trailer\n"
        trailer_content += f"<<\n/Size {len(xref_entries)}\n/Root {catalog_id} 0 R\n>>\n"
        trailer_content += f"startxref\n{xref_offset}\n%%EOF\n"
        
        pdf_content += xref_content + trailer_content
        
        return pdf_content.encode('latin-1')


def create_roi_pdf_from_gemini(gemini_output: str, report_data: Dict[str, Any] = None) -> bytes:
    """
    Create a professional ROI PDF report from Gemini output
    
    Args:
        gemini_output: The text output from Gemini
        report_data: Optional data for metrics and formatting
        
    Returns:
        PDF content as bytes
    """
    
    # Initialize PDF generator
    pdf_gen = GeminiPDFGenerator()
    
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
    
    # Start first page
    pdf_gen.new_page()
    
    # Add header
    pdf_gen.add_text("ROI Performance Report", 72, 720, 24, "Helvetica-Bold")
    pdf_gen.add_text(f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 72, 690, 12)
    
    # Add separator line
    pdf_gen.add_line(72, 670, 540, 670, 2)
    
    # Add metrics section
    y_pos = 640
    pdf_gen.add_text("Key Performance Metrics", 72, y_pos, 16, "Helvetica-Bold")
    y_pos -= 30
    
    # Create metrics table
    metrics_data = [
        ["Metric", "Value"],
        ["Total Revenue", f"${metrics.get('total_revenue', 0):,.2f}"],
        ["Total Spend", f"${metrics.get('total_spend', 0):,.2f}"],
        ["Total Profit", f"${metrics.get('total_profit', 0):,.2f}"],
        ["ROI Percentage", f"{roi_percentage:.1f}%"]
    ]
    
    # Draw metrics table
    table_x = 72
    table_y = y_pos - 20
    row_height = 25
    col_width = 200
    
    for i, row in enumerate(metrics_data):
        row_y = table_y - (i * row_height)
        
        # Draw row background
        if i == 0:  # Header row
            pdf_gen.add_rectangle(table_x, row_y - 20, col_width * 2, row_height, True, True, "E0E0E0")
            pdf_gen.add_text(row[0], table_x + 10, row_y - 5, 12, "Helvetica-Bold")
            pdf_gen.add_text(row[1], table_x + col_width + 10, row_y - 5, 12, "Helvetica-Bold")
        else:
            pdf_gen.add_rectangle(table_x, row_y - 20, col_width * 2, row_height, False, True)
            pdf_gen.add_text(row[0], table_x + 10, row_y - 5, 12)
            pdf_gen.add_text(row[1], table_x + col_width + 10, row_y - 5, 12)
    
    # Add executive summary section
    y_pos = table_y - (len(metrics_data) * row_height) - 40
    pdf_gen.add_text("Executive Summary", 72, y_pos, 16, "Helvetica-Bold")
    y_pos -= 30
    
    # Add Gemini output content
    lines = gemini_output.split('\n')
    line_height = 16
    
    for line in lines:
        if y_pos < 72:  # Bottom margin reached
            # Start new page
            pdf_gen.new_page()
            y_pos = 720
            
        # Truncate long lines
        if len(line) > 80:
            line = line[:77] + "..."
            
        pdf_gen.add_text(line, 72, y_pos, 12)
        y_pos -= line_height
        
        # Add some spacing for paragraphs
        if line.strip() == "":
            y_pos -= 8
    
    # Add footer
    pdf_gen.new_page()
    pdf_gen.add_text("Generated by BOS Solution ROI Analytics System", 72, 50, 10)
    pdf_gen.add_text(f"Report ID: {datetime.now().strftime('%Y%m%d_%H%M%S')}", 72, 35, 10)
    
    # Generate PDF
    return pdf_gen.generate_pdf_bytes()


def generate_gemini_pdf_report(gemini_output: str, report_data: Dict[str, Any] = None, 
                              output_filename: str = None) -> str:
    """
    Generate a PDF report from Gemini output
    
    Args:
        gemini_output: The text output from Gemini
        report_data: Optional data for metrics and formatting
        output_filename: Optional output filename
        
    Returns:
        Path to the generated PDF file
    """
    
    if output_filename is None:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_filename = f"gemini_roi_report_{timestamp}.pdf"
    
    try:
        # Generate PDF content
        pdf_bytes = create_roi_pdf_from_gemini(gemini_output, report_data)
        
        # Write to file
        with open(output_filename, 'wb') as f:
            f.write(pdf_bytes)
            
        print(f"✅ Gemini PDF generated: {output_filename}")
        return output_filename
        
    except Exception as e:
        print(f"❌ Error generating Gemini PDF: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_simple_html_for_pdf(gemini_output: str, report_data: Dict[str, Any] = None) -> str:
    """
    Create a simple HTML template optimized for PDF conversion
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
            font-size: 12pt;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #333;
            padding-bottom: 20px;
        }}
        
        .header h1 {{
            margin: 0;
            font-size: 24pt;
            color: #2c3e50;
        }}
        
        .header .date {{
            margin-top: 10px;
            font-size: 12pt;
            color: #7f8c8d;
        }}
        
        .metrics {{
            width: 100%;
            margin-bottom: 30px;
            border-collapse: collapse;
        }}
        
        .metrics th, .metrics td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: center;
        }}
        
        .metrics th {{
            background-color: #f5f5f5;
            font-weight: bold;
        }}
        
        .content {{
            margin-top: 30px;
        }}
        
        .content h2 {{
            color: #2c3e50;
            border-bottom: 1px solid #ddd;
            padding-bottom: 10px;
            margin-bottom: 20px;
            font-size: 16pt;
        }}
        
        .report-text {{
            white-space: pre-wrap;
            font-size: 12pt;
            line-height: 1.8;
            background-color: #f8f9fa;
            padding: 20px;
            border-left: 4px solid #3498db;
            border-radius: 4px;
        }}
        
        .footer {{
            margin-top: 40px;
            text-align: center;
            font-size: 10pt;
            color: #7f8c8d;
            border-top: 1px solid #ddd;
            padding-top: 20px;
        }}
        
        @media print {{
            body {{
                margin: 0;
                padding: 10px;
            }}
            
            .metrics {{
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
    
    <table class="metrics">
        <tr>
            <th>Total Revenue</th>
            <th>Total Spend</th>
            <th>Total Profit</th>
            <th>ROI Percentage</th>
        </tr>
        <tr>
            <td>${metrics.get('total_revenue', 0):,.2f}</td>
            <td>${metrics.get('total_spend', 0):,.2f}</td>
            <td>${metrics.get('total_profit', 0):,.2f}</td>
            <td>{roi_percentage:.1f}%</td>
        </tr>
    </table>
    
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


def generate_html_for_pdf_conversion(gemini_output: str, report_data: Dict[str, Any] = None, 
                                   output_filename: str = None) -> str:
    """
    Generate HTML file optimized for PDF conversion
    
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
        html_content = create_simple_html_for_pdf(gemini_output, report_data)
        
        # Write to file
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print(f"✅ HTML for PDF conversion generated: {output_filename}")
        return output_filename
        
    except Exception as e:
        print(f"❌ Error generating HTML for PDF conversion: {e}")
        return None


# Integration with existing ROI system
def integrate_with_roi_system(gemini_output: str, report_data: Dict[str, Any] = None) -> Dict[str, str]:
    """
    Integrate with the existing ROI system to generate both PDF and HTML
    
    Args:
        gemini_output: The text output from Gemini
        report_data: Optional data for metrics and formatting
        
    Returns:
        Dictionary with paths to generated files
    """
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # Generate standalone PDF
    pdf_filename = f"standalone_roi_report_{timestamp}.pdf"
    pdf_path = generate_gemini_pdf_report(gemini_output, report_data, pdf_filename)
    
    # Generate HTML for PDF conversion
    html_filename = f"roi_report_{timestamp}.html"
    html_path = generate_html_for_pdf_conversion(gemini_output, report_data, html_filename)
    
    # Save raw Gemini output
    txt_filename = f"gemini_output_{timestamp}.txt"
    txt_path = None
    try:
        with open(txt_filename, 'w', encoding='utf-8') as f:
            f.write(gemini_output)
        txt_path = txt_filename
        print(f"✅ Raw Gemini output saved: {txt_filename}")
    except Exception as e:
        print(f"❌ Error saving raw output: {e}")
    
    return {
        'pdf': pdf_path,
        'html': html_path,
        'txt': txt_path,
        'timestamp': timestamp
    }


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
    
    # Test integration
    results = integrate_with_roi_system(sample_gemini_output, sample_report_data)
    
    print(f"\n📁 Generated files:")
    for file_type, file_path in results.items():
        if file_path:
            print(f"   • {file_path} - {file_type.upper()}")
    
    print(f"\n✅ Gemini PDF Generator is ready for integration!")
