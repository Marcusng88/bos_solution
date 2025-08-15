#!/usr/bin/env python3
"""
Direct test of the YouTube callback endpoint using Python requests
"""

import requests
import json
import time

def test_callback():
    print("Testing YouTube callback endpoint...")
    
    # Wait a moment for server to start
    time.sleep(1)
    
    url = "http://localhost:8000/api/v1/youtube/auth/callback"
    data = {"code": "test_code"}
    
    try:
        print(f"Making POST request to: {url}")
        print(f"Data: {data}")
        
        response = requests.post(url, json=data, timeout=5)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 422:
            print("422 Unprocessable Content - Let's check the expected format")
            
        return response
        
    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error: {e}")
        print("Server might not be running or might have crashed")
    except requests.exceptions.Timeout as e:
        print(f"Timeout Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")
        
    return None

if __name__ == "__main__":
    test_callback()
