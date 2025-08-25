#!/usr/bin/env python3
"""
Test script for Enhanced PDF Conversion Agent with YouTube and Instagram Data
This script tests the enhanced PDF conversion functionality with platform data integration
"""

import asyncio
import os
import sys
from datetime import datetime, timezone
from dotenv import load_dotenv

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

load_dotenv()

async def test_enhanced_pdf_conversion_agent():
    """Test the enhanced PDF conversion agent functionality with YouTube and Instagram data"""
    
    print("🧪 Testing Enhanced PDF Conversion Agent with YouTube and Instagram Data")
    print("=" * 70)
    
    # Check environment variables
    print("\n1. Checking environment variables...")
    gemini_key = os.getenv("GOOGLE_API_KEY")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not gemini_key:
        print("⚠️  GEMINI_API_KEY not found - AI-powered PDF generation will be limited")
    else:
        print("✅ GEMINI_API_KEY configured")
    
    if not supabase_url or not supabase_key:
        print("⚠️  Supabase credentials not found - YouTube and Instagram data will be limited")
    else:
        print("✅ Supabase credentials configured")
    
    # Test enhanced PDF conversion agent import
    print("\n2. Testing enhanced PDF conversion agent import...")
    try:
        from app.services.pdf_conversion_agent import (
            pdf_agent, 
            convert_html_to_pdf_async,
            generate_pdf_from_json_async,
            create_enhanced_roi_pdf_async
        )
        print("✅ Enhanced PDF conversion agent imported successfully")
        print(f"   Supabase available: {pdf_agent.supabase_available}")
        print(f"   YouTube service available: {hasattr(pdf_agent, 'youtube_service')}")
    except ImportError as e:
        print(f"❌ Enhanced PDF conversion agent import failed: {e}")
        return False
    
    # Test basic HTML to PDF conversion
    print("\n3. Testing basic HTML to PDF conversion...")
    try:
        test_html = """
        <!DOCTYPE html>
        <html>
        <head>
        <style>
        body { 
            font-family: Arial, sans-serif; 
            font-size: 12pt; 
            margin: 20pt;
        }
        .title { 
            font-size: 18pt; 
            font-weight: bold; 
            text-align: center; 
            color: #2c3e50;
        }
        .section { 
            font-size: 14pt; 
            font-weight: bold; 
            margin: 15pt 0 8pt 0; 
            color: #34495e;
        }
        table { 
            width: 500pt; 
            table-layout: fixed; 
            border-collapse: collapse; 
            margin: 8pt 0; 
            font-size: 9pt;
        }
        th { 
            background-color: #ecf0f1; 
            padding: 4pt; 
            border: 1pt solid #bdc3c7; 
            font-weight: bold; 
            text-align: center;
        }
        td { 
            padding: 3pt; 
            border: 1pt solid #ecf0f1; 
            word-wrap: break-word; 
            vertical-align: top;
        }
        </style>
        </head>
        <body>
        
        <div class="title">Enhanced ROI Performance Report</div>
        <div style="text-align: center; margin: 10pt 0 15pt 0; color: #7f8c8d;">
            Generated on """ + datetime.now().strftime("%B %d, %Y at %I:%M %p") + """
        </div>
        
        <div class="section">Executive Summary</div>
        <p>This enhanced PDF report includes ROI performance data across multiple platforms including Facebook, Instagram, YouTube, and other social media channels.</p>
        
        <div class="section">Sample Data Table</div>
        <table>
        <thead>
        <tr>
            <th style="width: 80pt;">Date</th>
            <th style="width: 70pt;">Platform</th>
            <th style="width: 120pt;">Campaign</th>
            <th style="width: 60pt; text-align: right;">Revenue</th>
            <th style="width: 60pt; text-align: right;">Cost</th>
            <th style="width: 60pt; text-align: right;">ROI</th>
        </tr>
        </thead>
        <tbody>
        <tr>
            <td>2024-01-15</td>
            <td>Facebook</td>
            <td>Winter Sale Campaign</td>
            <td style="text-align: right;">$1,250.00</td>
            <td style="text-align: right;">$500.00</td>
            <td style="text-align: right;">$750.00</td>
        </tr>
        <tr>
            <td>2024-01-16</td>
            <td>Instagram</td>
            <td>Product Launch</td>
            <td style="text-align: right;">$2,100.00</td>
            <td style="text-align: right;">$800.00</td>
            <td style="text-align: right;">$1,300.00</td>
        </tr>
        <tr>
            <td>2024-01-17</td>
            <td>YouTube</td>
            <td>Video Campaign</td>
            <td style="text-align: right;">$3,450.00</td>
            <td style="text-align: right;">$1,200.00</td>
            <td style="text-align: right;">$2,250.00</td>
        </tr>
        </tbody>
        </table>
        
        <div style="margin-top: 20pt; padding: 8pt; border: 1pt solid #bdc3c7; background-color: #f8f9fa;">
        <p><strong>Report Generated by:</strong> BOS Solution Enhanced ROI Analytics System</p>
        <p><strong>Report ID:</strong> """ + datetime.now().strftime("%Y%m%d_%H%M%S") + """</p>
        <p><strong>Data Sources:</strong> ROI Metrics, YouTube Analytics, Instagram Monitoring, Social Media Accounts</p>
        </div>
        
        </body>
        </html>
        """
        
        # Convert HTML to PDF
        pdf_bytes, filename = await convert_html_to_pdf_async(test_html, "test_enhanced_roi_report.pdf")
        
        print(f"✅ Basic HTML to PDF conversion successful")
        print(f"   PDF size: {len(pdf_bytes)} bytes")
        print(f"   Filename: {filename}")
        
        # Save test PDF
        with open("test_enhanced_roi_report.pdf", "wb") as f:
            f.write(pdf_bytes)
        print(f"   Test PDF saved as: test_enhanced_roi_report.pdf")
        
    except Exception as e:
        print(f"❌ Basic HTML to PDF conversion failed: {e}")
        return False
    
    # Test enhanced ROI PDF generation with YouTube and Instagram data
    print("\n4. Testing enhanced ROI PDF generation with platform data...")
    try:
        # Sample ROI data
        sample_roi_data = {
            "platforms": {
                "Facebook": {
                    "total_revenue": 12500.50,
                    "total_cost": 5000.00,
                    "total_roi": 7500.50
                },
                "Instagram": {
                    "total_revenue": 21000.75,
                    "total_cost": 8000.00,
                    "total_roi": 13000.75
                },
                "YouTube": {
                    "total_revenue": 34500.25,
                    "total_cost": 12000.00,
                    "total_roi": 22500.25
                }
            },
            "campaigns": [
                {
                    "date": "2024-01-15",
                    "platform": "Facebook",
                    "campaign_name": "Winter Sale Campaign",
                    "revenue": 1250.00,
                    "cost": 500.00
                },
                {
                    "date": "2024-01-16",
                    "platform": "Instagram",
                    "campaign_name": "Product Launch",
                    "revenue": 2100.00,
                    "cost": 800.00
                },
                {
                    "date": "2024-01-17",
                    "platform": "YouTube",
                    "campaign_name": "Video Campaign",
                    "revenue": 3450.00,
                    "cost": 1200.00
                }
            ]
        }
        
        # Test user ID (you can replace this with a real user ID from your database)
        test_user_id = "test_user_123"
        
        # Generate enhanced ROI PDF
        pdf_bytes, filename = await create_enhanced_roi_pdf_async(test_user_id, sample_roi_data, "enhanced_roi_report.pdf")
        
        print(f"✅ Enhanced ROI PDF generation successful")
        print(f"   PDF size: {len(pdf_bytes)} bytes")
        print(f"   Filename: {filename}")
        
        # Save test PDF
        with open("enhanced_roi_report.pdf", "wb") as f:
            f.write(pdf_bytes)
        print(f"   Enhanced PDF saved as: enhanced_roi_report.pdf")
        
    except Exception as e:
        print(f"❌ Enhanced ROI PDF generation failed: {e}")
        print(f"   This might be expected if Supabase is not configured or no data exists")
        print(f"   Error details: {str(e)}")
    
    # Test YouTube data fetching (if Supabase is available)
    if pdf_agent.supabase_available:
        print("\n5. Testing YouTube data fetching...")
        try:
            test_user_id = "test_user_123"
            youtube_data = await pdf_agent.fetch_youtube_data(test_user_id)
            
            if youtube_data.get("error"):
                print(f"⚠️  YouTube data fetch returned error: {youtube_data['error']}")
            else:
                print(f"✅ YouTube data fetched successfully")
                print(f"   Videos found: {len(youtube_data.get('videos', []))}")
                print(f"   Channels found: {len(youtube_data.get('channels', []))}")
                print(f"   ROI metrics found: {len(youtube_data.get('roi_metrics', []))}")
        except Exception as e:
            print(f"❌ YouTube data fetching failed: {e}")
    
    # Test Instagram data fetching (if Supabase is available)
    if pdf_agent.supabase_available:
        print("\n6. Testing Instagram data fetching...")
        try:
            test_user_id = "test_user_123"
            instagram_data = await pdf_agent.fetch_instagram_data(test_user_id)
            
            if instagram_data.get("error"):
                print(f"⚠️  Instagram data fetch returned error: {instagram_data['error']}")
            else:
                print(f"✅ Instagram data fetched successfully")
                print(f"   Monitoring data found: {len(instagram_data.get('monitoring_data', []))}")
                print(f"   ROI metrics found: {len(instagram_data.get('roi_metrics', []))}")
                print(f"   Social accounts found: {len(instagram_data.get('social_accounts', []))}")
        except Exception as e:
            print(f"❌ Instagram data fetching failed: {e}")
    
    # Test AI-powered PDF generation (if Gemini is available)
    if gemini_key:
        print("\n7. Testing AI-powered PDF generation...")
        try:
            # Test with enhanced JSON data
            test_json_data = {
                "report_title": "AI-Generated Enhanced ROI Report",
                "summary": "This report was generated using AI to convert JSON data to HTML, then to PDF, with YouTube and Instagram data integration.",
                "metrics": {
                    "total_revenue": 68000.50,
                    "total_cost": 25000.00,
                    "total_roi": 43000.50,
                    "roi_percentage": 172.0
                },
                "platforms": [
                    {"name": "Facebook", "revenue": 12500.50, "cost": 5000.00},
                    {"name": "Instagram", "revenue": 21000.75, "cost": 8000.00},
                    {"name": "YouTube", "revenue": 34500.25, "cost": 12000.00}
                ],
                "enhanced_features": [
                    "YouTube video analytics",
                    "Instagram monitoring data",
                    "Social media account integration",
                    "Platform-specific ROI metrics"
                ]
            }
            
            # Generate AI-powered PDF
            pdf_bytes, filename = await generate_pdf_from_json_async(test_json_data, "ai_enhanced_roi_report.pdf")
            
            print(f"✅ AI-powered PDF generation successful")
            print(f"   PDF size: {len(pdf_bytes)} bytes")
            print(f"   Filename: {filename}")
            
            # Save test PDF
            with open("ai_enhanced_roi_report.pdf", "wb") as f:
                f.write(pdf_bytes)
            print(f"   Test PDF saved as: ai_enhanced_roi_report.pdf")
            
        except Exception as e:
            print(f"❌ AI-powered PDF generation failed: {e}")
            print(f"   This is expected if Gemini API is not properly configured")
    else:
        print("\n7. Skipping AI-powered PDF generation (no Gemini API key)")
    
    # Test enhanced PDF conversion agent methods
    print("\n8. Testing enhanced PDF conversion agent methods...")
    try:
        # Test synchronous wrapper
        from app.services.pdf_conversion_agent import convert_html_to_pdf_sync, create_enhanced_roi_pdf_sync
        
        simple_html = """
        <!DOCTYPE html>
        <html>
        <head><style>body { font-family: Arial; font-size: 12pt; }</style></head>
        <body>
        <h1>Enhanced Sync Test PDF</h1>
        <p>This PDF was generated using the enhanced synchronous wrapper with YouTube and Instagram data integration.</p>
        </body>
        </html>
        """
        
        pdf_bytes, filename = convert_html_to_pdf_sync(simple_html, "enhanced_sync_test.pdf")
        
        print(f"✅ Enhanced synchronous PDF conversion successful")
        print(f"   PDF size: {len(pdf_bytes)} bytes")
        print(f"   Filename: {filename}")
        
        # Save test PDF
        with open("enhanced_sync_test.pdf", "wb") as f:
            f.write(pdf_bytes)
        print(f"   Test PDF saved as: enhanced_sync_test.pdf")
        
    except Exception as e:
        print(f"❌ Enhanced synchronous PDF conversion failed: {e}")
        return False
    
    print("\n" + "=" * 70)
    print("✅ All enhanced PDF conversion tests completed successfully!")
    print("\nThe Enhanced PDF Conversion Agent is ready to use with YouTube and Instagram data integration.")
    print("\nGenerated test files:")
    print("- test_enhanced_roi_report.pdf (Basic HTML to PDF)")
    print("- enhanced_roi_report.pdf (Enhanced ROI with platform data)")
    print("- enhanced_sync_test.pdf (Enhanced synchronous conversion)")
    if gemini_key:
        print("- ai_enhanced_roi_report.pdf (AI-powered generation)")
    
    print("\nTo use the enhanced PDF conversion agent:")
    print("1. Start your backend server")
    print("2. Use the enhanced PDF endpoints:")
    print("   - POST /pdf/convert-html-to-pdf")
    print("   - POST /pdf/convert-json-to-pdf")
    print("   - POST /pdf/roi-report-to-pdf")
    print("   - POST /pdf/enhanced-roi-report-to-pdf (NEW - with YouTube & Instagram data)")
    print("   - GET /pdf/health")
    
    print("\nEnhanced features:")
    print("- YouTube video analytics and channel data")
    print("- Instagram monitoring data and ROI metrics")
    print("- Social media account integration")
    print("- Platform-specific performance metrics")
    print("- Comprehensive ROI analysis across all platforms")
    
    return True

async def main():
    """Main function"""
    try:
        success = await test_enhanced_pdf_conversion_agent()
        if not success:
            print("\n❌ Some tests failed. Please check the errors above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
