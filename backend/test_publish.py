#!/usr/bin/env python3
"""
Simple test script to verify Facebook posting works with your token
"""
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get token and page ID from environment
META_PAGE_ACCESS_TOKEN = os.getenv('META_PAGE_ACCESS_TOKEN')
META_PAGE_ID = os.getenv('META_PAGE_ID')
META_APP_VERSION = os.getenv('META_APP_VERSION', 'v23.0')

print(f"🔑 Token: {META_PAGE_ACCESS_TOKEN[:20]}...")
print(f"📊 Page ID: {META_PAGE_ID}")
print(f"📡 API Version: {META_APP_VERSION}")

if not META_PAGE_ACCESS_TOKEN or not META_PAGE_ID:
    print("❌ Missing required environment variables")
    exit(1)

# Test Facebook API directly
def test_facebook_post():
    url = f"https://graph.facebook.com/{META_APP_VERSION}/{META_PAGE_ID}/feed"
    data = {
        "message": "Test post from Python script - Token verification",
        "access_token": META_PAGE_ACCESS_TOKEN
    }
    
    try:
        response = requests.post(url, data=data)
        if response.status_code in (200, 201):
            result = response.json()
            print(f"✅ Facebook API Success!")
            print(f"📝 Post ID: {result.get('id')}")
            return True
        else:
            print(f"❌ Facebook API Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Facebook API with your credentials...")
    success = test_facebook_post()
    
    if success:
        print("\n✅ Your Facebook credentials are working perfectly!")
        print("The issue is likely in the backend API endpoint.")
    else:
        print("\n❌ There's an issue with your Facebook credentials.")