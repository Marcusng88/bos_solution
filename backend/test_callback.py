#!/usr/bin/env python3
"""
Test script for YouTube callback endpoint
"""

import requests
import json

def test_callback_endpoint():
    url = "http://localhost:8000/api/v1/youtube/auth/callback"
    data = {"code": "test_code"}
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_callback_endpoint()
