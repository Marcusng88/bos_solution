#!/usr/bin/env python3
"""
Demo script to showcase the different ROI report formats
"""

import asyncio
import os
import sys
import webbrowser
from pathlib import Path
from datetime import datetime

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent))
from generate_roi_report import generate_roi_report

async def demo_report_formats():
    """Demonstrate the different report formats"""
    print("🎯 ROI Report Format Demo")
    print("=" * 50)
    
    # Generate the report
    print("📊 Generating ROI report in all formats...")
    success = await generate_roi_report()
    
    if not success:
        print("❌ Failed to generate report")
        return
    
    # Find the latest generated files
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    txt_file = f"roi_report_{timestamp}.txt"
    html_file = f"roi_report_{timestamp}.html"
    pdf_file = f"roi_report_{timestamp}.pdf"
    json_file = f"roi_data_{timestamp}.json"
    
    print(f"\n📁 Generated Files:")
    print(f"   📄 Text Report: {txt_file}")
    print(f"   🌐 HTML Report: {html_file}")
    print(f"   📊 PDF Report: {pdf_file}")
    print(f"   📋 Raw Data: {json_file}")
    
    # Show file sizes
    for file_path in [txt_file, html_file, pdf_file, json_file]:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            size_mb = size / (1024 * 1024)
            print(f"   📏 {file_path}: {size_mb:.2f} MB")
    
    print(f"\n🎨 Report Format Features:")
    print(f"   📄 Text (.txt):")
    print(f"      • Simple, readable format")
    print(f"      • Easy to copy/paste")
    print(f"      • Works in any text editor")
    print(f"      • Small file size")
    
    print(f"\n   🌐 HTML (.html):")
    print(f"      • Professional, modern design")
    print(f"      • Interactive elements")
    print(f"      • Responsive layout")
    print(f"      • Can be opened in any browser")
    print(f"      • Print-friendly styling")
    
    print(f"\n   📊 PDF (.pdf):")
    print(f"      • Professional document format")
    print(f"      • Consistent appearance across devices")
    print(f"      • Easy to share and archive")
    print(f"      • Print-ready")
    print(f"      • Password protection possible")
    
    print(f"\n   📋 JSON (.json):")
    print(f"      • Raw data for further analysis")
    print(f"      • Machine-readable format")
    print(f"      • Can be imported into other tools")
    print(f"      • Contains all metrics and calculations")
    
    # Offer to open files
    print(f"\n🚀 Actions:")
    
    # Open HTML in browser
    if os.path.exists(html_file):
        try:
            print(f"   🌐 Opening HTML report in browser...")
            webbrowser.open(f"file://{os.path.abspath(html_file)}")
        except Exception as e:
            print(f"   ⚠️  Could not open browser: {e}")
    
    # Show file locations
    print(f"\n📂 File Locations:")
    for file_path in [txt_file, html_file, pdf_file, json_file]:
        if os.path.exists(file_path):
            abs_path = os.path.abspath(file_path)
            print(f"   📁 {file_path}: {abs_path}")
    
    print(f"\n💡 Usage Tips:")
    print(f"   • HTML reports are best for viewing on screen")
    print(f"   • PDF reports are best for printing and sharing")
    print(f"   • Text reports are best for quick reading")
    print(f"   • JSON files are best for data analysis")
    
    print(f"\n✅ Demo completed successfully!")

async def main():
    """Main function"""
    await demo_report_formats()

if __name__ == "__main__":
    asyncio.run(main())


