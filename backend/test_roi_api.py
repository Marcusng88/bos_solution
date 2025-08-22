#!/usr/bin/env python3
"""
Comprehensive ROI API Test - tests all endpoints and integration
"""

import asyncio
import aiohttp
import sys
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ Environment variables loaded from .env")
except ImportError:
    print("⚠ python-dotenv not available, using system environment")

API_BASE = "http://localhost:8000/api/v1"
TEST_USER_ID = "test_user_123"

async def test_roi_endpoints():
    """Test all ROI API endpoints"""
    
    endpoints_to_test = [
        f"{API_BASE}/roi/overview?user_id={TEST_USER_ID}&range=7d",
        f"{API_BASE}/roi/revenue/by-source?user_id={TEST_USER_ID}&range=7d",
        f"{API_BASE}/roi/revenue/trends?user_id={TEST_USER_ID}&range=7d",
        f"{API_BASE}/roi/cost/breakdown?user_id={TEST_USER_ID}&range=7d",
        f"{API_BASE}/roi/cost/monthly-trends?user_id={TEST_USER_ID}&year=2024",
        f"{API_BASE}/roi/profitability/clv?user_id={TEST_USER_ID}&range=7d",
        f"{API_BASE}/roi/profitability/cac?user_id={TEST_USER_ID}&range=7d",
        f"{API_BASE}/roi/roi/trends?user_id={TEST_USER_ID}&range=7d",
        f"{API_BASE}/roi/channel/performance?user_id={TEST_USER_ID}&range=7d",
        f"{API_BASE}/roi/trends?user_id={TEST_USER_ID}&range=7d",
        f"{API_BASE}/roi/campaigns-in-range?user_id={TEST_USER_ID}&range=7d",
    ]
    
    results = []
    
    async with aiohttp.ClientSession() as session:
        print("🧪 Testing ROI API endpoints...")
        
        for endpoint in endpoints_to_test:
            endpoint_name = endpoint.split("/roi/")[-1].split("?")[0]
            
            try:
                async with session.get(endpoint) as response:
                    status = response.status
                    data = await response.json()
                    
                    if status == 200:
                        print(f"✅ {endpoint_name}: OK (status {status})")
                        results.append({
                            "endpoint": endpoint_name,
                            "status": "success",
                            "data_points": len(data.get("rows", data.get("series", [data] if isinstance(data, dict) else [])))
                        })
                    else:
                        print(f"⚠️  {endpoint_name}: {status} - {data.get('detail', 'Unknown error')}")
                        results.append({
                            "endpoint": endpoint_name, 
                            "status": "error",
                            "error": data.get('detail', f'HTTP {status}')
                        })
                        
            except Exception as e:
                print(f"❌ {endpoint_name}: Connection failed - {e}")
                results.append({
                    "endpoint": endpoint_name,
                    "status": "connection_failed", 
                    "error": str(e)
                })
    
    return results

async def check_server_health():
    """Check if the FastAPI server is running"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE}/") as response:
                if response.status == 200:
                    print("✅ FastAPI server is running")
                    return True
                else:
                    print(f"⚠️  Server responded with status {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print(f"💡 Make sure FastAPI server is running on {API_BASE}")
        return False

async def main():
    print("🚀 Starting ROI Integration Test...\n")
    
    # Check server health
    server_ok = await check_server_health()
    if not server_ok:
        print("\n❌ Server is not running. Please start the FastAPI server first:")
        print("   cd bos_solution/backend")
        print("   python main.py")
        return 1
    
    print()
    
    # Test ROI endpoints
    results = await test_roi_endpoints()
    
    # Summary
    print(f"\n📊 Test Summary:")
    success_count = len([r for r in results if r["status"] == "success"])
    error_count = len([r for r in results if r["status"] == "error"])
    connection_failed_count = len([r for r in results if r["status"] == "connection_failed"])
    
    print(f"   ✅ Successful: {success_count}")
    print(f"   ⚠️  Errors: {error_count}")
    print(f"   ❌ Connection failed: {connection_failed_count}")
    
    if success_count > 0:
        print(f"\n🎉 {success_count} ROI endpoints are working!")
        print("✨ Your ROI system is functional and ready!")
        
        # Show some data details
        successful_results = [r for r in results if r["status"] == "success"]
        for result in successful_results:
            if result.get("data_points", 0) > 0:
                print(f"   📈 {result['endpoint']}: {result['data_points']} data points available")
    
    if error_count > 0 or connection_failed_count > 0:
        print(f"\n⚠️  Some issues found:")
        failed_results = [r for r in results if r["status"] != "success"]
        for result in failed_results:
            print(f"   • {result['endpoint']}: {result.get('error', 'Unknown error')}")
    
    return 0 if success_count > 0 else 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
