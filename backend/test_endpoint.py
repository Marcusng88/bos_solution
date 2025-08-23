#!/usr/bin/env python3
"""
Simple test script to test the report generation endpoint
"""

import asyncio
import httpx
import json

async def test_endpoint():
    """Test the report generation endpoint"""
    
    url = "http://localhost:8000/api/v1/roi/generate-report"
    params = {"user_id": "test_user_123"}
    
    print("🧪 Testing ROI Report Generation Endpoint")
    print("=" * 50)
    print(f"URL: {url}")
    print(f"Params: {params}")
    print()
    
    try:
        async with httpx.AsyncClient() as client:
            print("📡 Making POST request...")
            response = await client.post(url, params=params, timeout=60.0)
            
            print(f"📊 Response Status: {response.status_code}")
            print(f"📊 Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                print("✅ Request successful!")
                data = response.json()
                print(f"📄 Response data keys: {list(data.keys())}")
                
                if "report" in data:
                    report = data["report"]
                    print(f"📋 Report sections: {list(report.keys())}")
                    
                    for section, content in report.items():
                        print(f"  - {section}: {len(content)} characters")
                        if content:
                            print(f"    Preview: {content[:100]}...")
                
                if "raw_data" in data:
                    raw_data = data["raw_data"]
                    print(f"📊 Raw data keys: {list(raw_data.keys())}")
                    
                    if "current_month" in raw_data:
                        current = raw_data["current_month"]
                        print(f"  - Current month platforms: {list(current.get('platforms', {}).keys())}")
                        print(f"  - Current month totals: {current.get('totals', {})}")
                
            else:
                print("❌ Request failed!")
                print(f"Error response: {response.text}")
                
    except httpx.ConnectError:
        print("❌ Connection error: Could not connect to the server")
        print("   Make sure the backend server is running on http://localhost:8000")
    except httpx.TimeoutException:
        print("❌ Timeout error: Request took too long")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(test_endpoint())
