#!/usr/bin/env python3
"""
Quick YouTube Connectivity Test
"""

import requests
import json
import os
from dotenv import load_dotenv

def test_connectivity():
    load_dotenv()
    
    print('🧪 Testing YouTube API Connectivity...')
    print('=' * 50)

    # Test 1: Backend Health
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print('✅ Backend Server: RUNNING')
        else:
            print(f'❌ Backend Server: ERROR ({response.status_code})')
            return False
    except Exception as e:
        print(f'❌ Backend Server: OFFLINE - {e}')
        return False

    # Test 2: OAuth URL Generation
    try:
        response = requests.get('http://localhost:8000/api/v1/youtube/oauth-url', timeout=10)
        if response.status_code == 200:
            data = response.json()
            print('✅ OAuth URL Generation: SUCCESS')
            print(f'   Auth URL: {data.get("auth_url", "")[:80]}...')
        else:
            print(f'❌ OAuth URL Generation: FAILED ({response.status_code})')
    except Exception as e:
        print(f'❌ OAuth URL Generation: ERROR - {e}')

    # Test 3: Google API Key Validation
    try:
        api_key = os.getenv('GOOGLE_API_KEY')
        if api_key and api_key != 'your_google_api_key_here':
            response = requests.get(
                'https://www.googleapis.com/youtube/v3/search',
                params={
                    'part': 'snippet',
                    'q': 'test',
                    'type': 'video',
                    'maxResults': 1,
                    'key': api_key
                },
                timeout=10
            )
            if response.status_code == 200:
                print('✅ Google API Key: VALID & WORKING')
                data = response.json()
                print(f'   Found {len(data.get("items", []))} test results')
            else:
                print(f'❌ Google API Key: INVALID ({response.status_code})')
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {'error': response.text[:100]}
                print(f'   Error: {error_data}')
        else:
            print('❌ Google API Key: NOT SET PROPERLY')
    except Exception as e:
        print(f'❌ Google API Key Test: ERROR - {e}')

    # Test 4: Debug Endpoint
    try:
        response = requests.get('http://localhost:8000/api/v1/youtube/debug', timeout=10)
        if response.status_code == 200:
            print('✅ YouTube Debug Endpoint: WORKING')
        else:
            print(f'❌ YouTube Debug Endpoint: FAILED ({response.status_code})')
    except Exception as e:
        print(f'❌ YouTube Debug Endpoint: ERROR - {e}')

    print('=' * 50)
    print('📋 NEXT STEPS:')
    print('1. If all tests pass: Go to http://localhost:3000')
    print('2. Connect your YouTube account via OAuth')
    print('3. Copy your access token (from browser dev tools > Network tab)')
    print('4. Run: python youtube_debug_simple.py YOUR_ACCESS_TOKEN')
    print('')
    print('🔧 OR test with our debug endpoint:')
    print('   http://localhost:8000/api/v1/youtube/debug/full-test?access_token=YOUR_TOKEN')

if __name__ == "__main__":
    test_connectivity()
