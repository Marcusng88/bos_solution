#!/usr/bin/env python3
"""
Generate ROI Report and Save to File
"""

import asyncio
import os
import sys
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent))
from app.core.supabase_client import supabase_client
from app.api.v1.endpoints.roi import _fetch_all_roi_data, _summarize_data_by_platform, _calculate_totals, _create_report_prompt_all_data

load_dotenv()

async def generate_roi_report():
    """Generate a ROI report and save it to a file"""
    print("📊 Generating ROI Report")
    print("=" * 50)
    
    try:
        # Check if Gemini API key is available
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            print("❌ GEMINI_API_KEY not found in environment variables")
            print("   Please add GEMINI_API_KEY to your .env file")
            return False
        
        # Import Gemini
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_api_key)
            
            # Try gemini-1.5-flash first, fallback to gemini-pro
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                print("✅ Using Gemini 1.5 Flash model")
            except Exception as flash_error:
                print(f"⚠️  Gemini 1.5 Flash not available, using Gemini Pro: {flash_error}")
                model = genai.GenerativeModel('gemini-pro')
                print("✅ Using Gemini Pro model")
                
        except ImportError as e:
            print(f"❌ Failed to import google.generativeai: {e}")
            print("   Please install: pip install google-generativeai")
            return False
        
        # Fetch all data
        print("\n📋 Fetching data from roi_metrics table...")
        all_data = await _fetch_all_roi_data()
        
        if len(all_data) == 0:
            print("❌ No data found in roi_metrics table")
            return False
        
        print(f"✅ Retrieved {len(all_data)} records")
        
        # Process data
        print("\n📊 Processing data...")
        platform_summary = _summarize_data_by_platform(all_data)
        overall_totals = _calculate_totals(platform_summary)
        
        print(f"✅ Processed data for {len(platform_summary)} platforms")
        print(f"   Total revenue: ${overall_totals.get('total_revenue', 0):,.2f}")
        print(f"   Total spend: ${overall_totals.get('total_spend', 0):,.2f}")
        
        # Prepare report data
        report_data = {
            "all_data": {
                "period": "All available data",
                "platforms": platform_summary,
                "totals": overall_totals,
                "total_records": len(all_data)
            }
        }
        
        # Generate report
        print("\n🤖 Generating report with Gemini...")
        prompt = _create_report_prompt_all_data(report_data)
        
        response = model.generate_content(prompt)
        report_content = response.text
        
        if not report_content:
            print("❌ Gemini API returned empty response")
            return False
        
        print(f"✅ Generated report ({len(report_content)} characters)")
        
        # Save report to file
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        report_filename = f"roi_report_{timestamp}.txt"
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(f"ROI REPORT - Generated on {datetime.now().strftime('%m/%d/%Y')}\n")
            f.write("=" * 80 + "\n\n")
            f.write(report_content)
        
        print(f"\n💾 Report saved to: {report_filename}")
        
        # Also save raw data for reference
        data_filename = f"roi_data_{timestamp}.json"
        with open(data_filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"📊 Raw data saved to: {data_filename}")
        
        # Show report preview
        print(f"\n📝 Report Preview:")
        print("-" * 50)
        lines = report_content.split('\n')[:20]
        for line in lines:
            print(line)
        if len(report_content.split('\n')) > 20:
            print("...")
        
        print(f"\n🎉 ROI Report generated successfully!")
        print(f"📁 Files created:")
        print(f"   • {report_filename} - Full report")
        print(f"   • {data_filename} - Raw data")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating report: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main function"""
    success = await generate_roi_report()
    
    if success:
        print("\n✅ CONCLUSION: ROI report generation is working correctly!")
        return 0
    else:
        print("\n❌ CONCLUSION: ROI report generation failed.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
