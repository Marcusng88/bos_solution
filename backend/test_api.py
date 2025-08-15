#!/usr/bin/env python3
"""
Direct API endpoint test
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1/dashboard"

def test_endpoint(endpoint, method="GET", data=None):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n🧪 Testing {method} {url}")
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Success!")
            result = response.json()
            if isinstance(result, list):
                print(f"Returned {len(result)} items")
            elif isinstance(result, dict):
                print(f"Keys: {list(result.keys())}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    print("🚀 Testing Dashboard API Endpoints...")
    
    # Test all endpoints
    test_endpoint("/stats")
    test_endpoint("/ai-suggestions")
    test_endpoint("/competitor-gaps")
    test_endpoint("/recent-activities")
    test_endpoint("/competitive-intelligence")
    test_endpoint("/ai-analysis", "POST", {"analysis_type": "competitive"})
    
    print("\n✨ API endpoint testing complete!")

if __name__ == "__main__":
    main()
