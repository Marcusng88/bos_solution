#!/usr/bin/env python3
"""
Simple PDF Integration - Easy integration with existing ROI system
Replaces external PDF dependencies with standalone Gemini PDF generator
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent))

# Import the standalone PDF generator
from gemini_pdf_generator import (
    generate_gemini_pdf_report,
    generate_html_for_pdf_conversion,
    integrate_with_roi_system
)


def simple_pdf_from_gemini(gemini_output: str, report_data: Dict[str, Any] = None) -> Dict[str, str]:
    """
    Simple function to generate PDF from Gemini output
    This can be easily integrated into existing ROI systems
    
    Args:
        gemini_output: The text output from Gemini
        report_data: Optional data for metrics and formatting
        
    Returns:
        Dictionary with paths to generated files
    """
    
    print("🚀 Generating standalone PDF from Gemini output...")
    
    # Generate all formats
    results = integrate_with_roi_system(gemini_output, report_data)
    
    print("✅ PDF generation completed!")
    return results


def replace_existing_pdf_generation(gemini_output: str, report_data: Dict[str, Any] = None) -> str:
    """
    Drop-in replacement for existing PDF generation
    Returns only the PDF file path for backward compatibility
    
    Args:
        gemini_output: The text output from Gemini
        report_data: Optional data for metrics and formatting
        
    Returns:
        Path to the generated PDF file
    """
    
    # Generate PDF using standalone generator
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    pdf_filename = f"roi_report_{timestamp}.pdf"
    
    pdf_path = generate_gemini_pdf_report(gemini_output, report_data, pdf_filename)
    
    if pdf_path:
        print(f"✅ Standalone PDF generated: {pdf_path}")
        return pdf_path
    else:
        print("❌ PDF generation failed")
        return None


def generate_minimal_pdf(gemini_output: str) -> str:
    """
    Generate minimal PDF with just Gemini output
    No external dependencies, no complex formatting
    
    Args:
        gemini_output: The text output from Gemini
        
    Returns:
        Path to the generated PDF file
    """
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    pdf_filename = f"minimal_roi_report_{timestamp}.pdf"
    
    # Use minimal report data
    minimal_data = {
        'all_data': {
            'totals': {
                'total_revenue': 0,
                'total_spend': 0,
                'total_profit': 0,
                'total_roi': 0
            }
        }
    }
    
    pdf_path = generate_gemini_pdf_report(gemini_output, minimal_data, pdf_filename)
    
    if pdf_path:
        print(f"✅ Minimal PDF generated: {pdf_path}")
        return pdf_path
    else:
        print("❌ Minimal PDF generation failed")
        return None


def generate_html_only(gemini_output: str, report_data: Dict[str, Any] = None) -> str:
    """
    Generate only HTML file for PDF conversion
    Useful when you want to use browser print-to-PDF
    
    Args:
        gemini_output: The text output from Gemini
        report_data: Optional data for metrics and formatting
        
    Returns:
        Path to the generated HTML file
    """
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    html_filename = f"roi_report_{timestamp}.html"
    
    html_path = generate_html_for_pdf_conversion(gemini_output, report_data, html_filename)
    
    if html_path:
        print(f"✅ HTML for PDF conversion generated: {html_path}")
        print("💡 Open this file in a browser and use Print > Save as PDF")
        return html_path
    else:
        print("❌ HTML generation failed")
        return None


# Integration examples for existing ROI system
def example_integration_with_existing_system():
    """
    Example of how to integrate with existing ROI system
    """
    
    # This is how you would replace the existing PDF generation
    # in generate_roi_report.py or similar files
    
    # 1. Replace the complex PDF generation code with this simple call:
    def old_pdf_generation_method(gemini_output, report_data):
        # OLD CODE (complex, with external dependencies):
        # try:
        #     import weasyprint
        #     HTML(string=html_content).write_pdf(pdf_filename, stylesheets=[pdf_css])
        # except ImportError:
        #     try:
        #         from reportlab.lib.pagesizes import A4
        #         # ... complex ReportLab code ...
        #     except ImportError:
        #         print("No PDF library available")
        
        # NEW CODE (simple, standalone):
        return replace_existing_pdf_generation(gemini_output, report_data)
    
    # 2. Or use the full integration for multiple formats:
    def new_full_integration(gemini_output, report_data):
        return simple_pdf_from_gemini(gemini_output, report_data)
    
    # 3. Or just get HTML for browser-based PDF conversion:
    def html_only_integration(gemini_output, report_data):
        return generate_html_only(gemini_output, report_data)


# Quick test function
def quick_test():
    """
    Quick test of the standalone PDF generation
    """
    
    print("🧪 Testing standalone PDF generation...")
    
    # Sample Gemini output
    test_output = """
ROI Performance Analysis Report

Executive Summary:
This comprehensive ROI analysis demonstrates excellent performance across all marketing channels.

Key Findings:
- Total revenue: $150,000
- Total spend: $50,000
- Net profit: $100,000
- ROI: 200%

Platform Performance:
1. YouTube: 250% ROI
2. Facebook: 180% ROI
3. Instagram: 120% ROI

Recommendations:
1. Increase YouTube investment
2. Optimize Facebook campaigns
3. Review Instagram strategy

This analysis shows strong overall performance with room for optimization.
"""
    
    # Test minimal PDF generation
    pdf_path = generate_minimal_pdf(test_output)
    
    # Test HTML generation
    html_path = generate_html_only(test_output)
    
    # Test full integration
    results = simple_pdf_from_gemini(test_output)
    
    print(f"\n📁 Test Results:")
    if pdf_path:
        print(f"   ✅ Minimal PDF: {pdf_path}")
    if html_path:
        print(f"   ✅ HTML: {html_path}")
    if results:
        print(f"   ✅ Full integration: {results}")
    
    print(f"\n🎉 Standalone PDF generation test completed!")


if __name__ == "__main__":
    # Run quick test
    quick_test()
    
    print(f"\n📋 Integration Instructions:")
    print(f"1. Replace existing PDF generation with replace_existing_pdf_generation()")
    print(f"2. Use simple_pdf_from_gemini() for full integration")
    print(f"3. Use generate_html_only() for browser-based PDF conversion")
    print(f"4. Use generate_minimal_pdf() for simplest PDF generation")
    print(f"\n✅ No external dependencies required!")
