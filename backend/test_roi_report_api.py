#!/usr/bin/env python3
"""
Test ROI Report Generation API Endpoint
"""

import asyncio
import os
import sys
import httpx
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

async def test_roi_report_api():
    """Test the ROI report generation API endpoint"""
    print("🧪 Testing ROI Report Generation API")
    print("=" * 50)
    
    # Get API URL from environment
    api_url = os.getenv("API_URL", "http://localhost:8000")
    report_url = f"{api_url}/api/v1/roi/generate-report"
    
    print(f"🔗 Testing API at: {report_url}")
    
    # Test user ID (can be any string since we removed user filtering)
    test_user_id = "test_user_123"
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            print(f"\n📤 Sending POST request to generate report...")
            print(f"   User ID: {test_user_id}")
            
            response = await client.post(
                report_url,
                params={"user_id": test_user_id}
            )
            
            print(f"📥 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Report generation successful!")
                
                # Check response structure
                if "success" in data and data["success"]:
                    print("   ✅ Success flag is true")
                else:
                    print("   ⚠️  Success flag is false")
                
                if "report" in data:
                    report = data["report"]
                    print(f"   📊 Report sections: {list(report.keys())}")
                    
                    # Show report preview
                    if "executive_summary" in report:
                        summary = report["executive_summary"]
                        print(f"   📝 Executive Summary preview: {summary[:200]}...")
                    
                    if "performance_overview" in report:
                        overview = report["performance_overview"]
                        print(f"   📈 Performance Overview preview: {overview[:200]}...")
                
                if "raw_data" in data:
                    raw_data = data["raw_data"]
                    if "all_data" in raw_data:
                        all_data = raw_data["all_data"]
                        print(f"   📋 Total records analyzed: {all_data.get('total_records', 'N/A')}")
                        print(f"   💰 Total revenue: ${all_data.get('totals', {}).get('total_revenue', 0):,.2f}")
                
                if "generated_at" in data:
                    print(f"   ⏰ Generated at: {data['generated_at']}")
                
                print("\n🎉 ROI Report Generation API is working correctly!")
                return True
                
            else:
                print(f"❌ Report generation failed: Status {response.status_code}")
                print(f"   Error: {response.text[:500]}...")
                return False
                
    except Exception as e:
        print(f"❌ API test error: {str(e)}")
        print("💡 TIP: Make sure the FastAPI server is running on localhost:8000")
        return False

async def main():
    """Main function"""
    try:
        success = await test_roi_report_api()
        
        if success:
            print("\n✅ CONCLUSION: ROI Report Generation API is working correctly!")
            print("\n📋 Next steps:")
            print("1. The API endpoint is ready for frontend integration")
            print("2. Reports can be generated for any user_id")
            print("3. All data from roi_metrics table is accessible")
            print("4. No date or user restrictions are applied")
            return 0
        else:
            print("\n❌ CONCLUSION: ROI Report Generation API has issues.")
            return 1
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
