#!/usr/bin/env python3
"""
Test ROI API Endpoints - Test the actual API endpoints for ROI data retrieval
"""

import asyncio
import os
import sys
import httpx
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

async def test_roi_api_endpoints():
    """Test ROI API endpoints"""
    print("🌐 Testing ROI API Endpoints")
    print("=" * 50)
    
    # Get API URL from environment
    api_url = os.getenv("API_URL", "http://localhost:8000")
    base_url = f"{api_url}/api/v1/roi"
    
    print(f"🔗 Testing API at: {base_url}")
    
    # Test user ID (you can replace this with a real user ID)
    test_user_id = "test_user_123"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        endpoints_to_test = [
            {
                "name": "Overview",
                "url": f"{base_url}/overview",
                "params": {"user_id": test_user_id, "range": "7d"}
            },
            {
                "name": "Trends",
                "url": f"{base_url}/trends",
                "params": {"user_id": test_user_id, "range": "7d"}
            },
            {
                "name": "Revenue by Source",
                "url": f"{base_url}/revenue/by-source",
                "params": {"user_id": test_user_id, "range": "7d"}
            },
            {
                "name": "Revenue Trends",
                "url": f"{base_url}/revenue/trends",
                "params": {"user_id": test_user_id, "range": "7d"}
            },
            {
                "name": "Cost Breakdown",
                "url": f"{base_url}/cost/breakdown",
                "params": {"user_id": test_user_id, "range": "7d"}
            },
            {
                "name": "Channel Performance",
                "url": f"{base_url}/channel/performance",
                "params": {"user_id": test_user_id, "range": "7d"}
            },
            {
                "name": "Monthly Spend Trends",
                "url": f"{base_url}/monthly-spend-trends",
                "params": {"user_id": test_user_id, "range": "7d"}
            },
            {
                "name": "ROI Trends",
                "url": f"{base_url}/roi-trends",
                "params": {"user_id": test_user_id, "range": "7d"}
            },
            {
                "name": "Campaigns in Range",
                "url": f"{base_url}/campaigns-in-range",
                "params": {"user_id": test_user_id, "range": "7d"}
            }
        ]
        
        results = []
        
        for endpoint in endpoints_to_test:
            try:
                print(f"\n🔍 Testing {endpoint['name']}...")
                response = await client.get(endpoint['url'], params=endpoint['params'])
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ {endpoint['name']}: Success (Status {response.status_code})")
                    
                    # Show some data structure info
                    if isinstance(data, dict):
                        keys = list(data.keys())
                        print(f"   📊 Response keys: {keys[:5]}{'...' if len(keys) > 5 else ''}")
                        
                        # Check for specific data patterns
                        if 'series' in data:
                            series_count = len(data['series']) if isinstance(data['series'], list) else 0
                            print(f"   📈 Series data points: {series_count}")
                        elif 'rows' in data:
                            rows_count = len(data['rows']) if isinstance(data['rows'], list) else 0
                            print(f"   📋 Rows data points: {rows_count}")
                        elif 'total_revenue' in data:
                            print(f"   💰 Total revenue: ${data.get('total_revenue', 0):.2f}")
                    elif isinstance(data, list):
                        print(f"   📋 List response with {len(data)} items")
                    
                    results.append({"endpoint": endpoint['name'], "success": True, "status": response.status_code})
                else:
                    print(f"❌ {endpoint['name']}: Failed (Status {response.status_code})")
                    print(f"   Error: {response.text[:200]}...")
                    results.append({"endpoint": endpoint['name'], "success": False, "status": response.status_code})
                    
            except Exception as e:
                print(f"❌ {endpoint['name']}: Error - {str(e)}")
                results.append({"endpoint": endpoint['name'], "success": False, "error": str(e)})
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 API ENDPOINTS TEST SUMMARY")
        print("=" * 50)
        
        successful = sum(1 for r in results if r["success"])
        total = len(results)
        
        print(f"Endpoints Tested: {total}")
        print(f"Successful: {successful}")
        print(f"Failed: {total - successful}")
        print(f"Success Rate: {(successful/total)*100:.1f}%")
        
        if successful == total:
            print("\n🎉 ALL API ENDPOINTS WORKING!")
        else:
            print("\n⚠️  Some endpoints failed:")
            for result in results:
                if not result["success"]:
                    print(f"   • {result['endpoint']}: {result.get('error', f'Status {result.get('status', 'Unknown')}')}")
        
        return successful == total

async def main():
    """Main function"""
    try:
        success = await test_roi_api_endpoints()
        
        if success:
            print("\n✅ CONCLUSION: All ROI API endpoints are working correctly!")
            return 0
        else:
            print("\n❌ CONCLUSION: Some ROI API endpoints have issues.")
            return 1
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("💡 TIP: Make sure the FastAPI server is running on localhost:8000")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
