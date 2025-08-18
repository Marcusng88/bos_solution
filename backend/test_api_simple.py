#!/usr/bin/env python3
"""
Simple API test script
"""

import requests
import json

def test_api():
    """Test the API directly"""
    
    url = "http://localhost:8000/api/v1/ai-insights/chat"
    headers = {
        "Content-Type": "application/json",
        "X-User-ID": "test_user"
    }
    data = {
        "message": "How are my ongoing campaigns performing?"
    }
    
    try:
        print("🔍 Testing API...")
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API Response:")
            print(f"Success: {result.get('success')}")
            print(f"Response: {result.get('response')[:500]}...")
            
            # Check if it contains real campaign names
            if "Lazada Flash Sales 8.8" in result.get('response', ''):
                print("✅ Contains real campaign data!")
            elif "Error Recovery Campaign" in result.get('response', ''):
                print("❌ Still contains fake data!")
            else:
                print("⚠️  Response unclear")
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    test_api()
