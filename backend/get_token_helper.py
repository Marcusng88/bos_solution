#!/usr/bin/env python3
"""
Get YouTube Access Token Helper
This script helps you get the access token from your browser
"""

import json
import time
from datetime import datetime

def show_token_instructions():
    print("🎯 HOW TO GET YOUR YOUTUBE ACCESS TOKEN:")
    print("=" * 60)
    print()
    
    print("📱 METHOD 1: From Frontend (Easiest)")
    print("─" * 40)
    print("1. Open: http://localhost:3000")
    print("2. Connect your YouTube account")
    print("3. Press F12 (Open Developer Tools)")
    print("4. Go to 'Application' or 'Storage' tab")
    print("5. Look in 'Local Storage' for 'youtube_token' or similar")
    print("6. Copy the token value")
    print()
    
    print("🌐 METHOD 2: From Network Tab")
    print("─" * 40)
    print("1. Open: http://localhost:3000") 
    print("2. Press F12 (Open Developer Tools)")
    print("3. Go to 'Network' tab")
    print("4. Connect your YouTube account")
    print("5. Look for requests containing 'access_token'")
    print("6. Copy the token from the request")
    print()
    
    print("🔗 METHOD 3: Direct OAuth")
    print("─" * 40)
    print("1. Go to this URL:")
    
    # Generate OAuth URL
    from urllib.parse import urlencode
    
    client_id = "326775019777-v43jhcbs891rtv00p5vevif0ss57gc0r.apps.googleusercontent.com"
    scopes = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.readonly"]
    redirect_uri = "http://localhost:3000/auth/callback/youtube"
    
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": " ".join(scopes),
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent",
        "state": "test_state"
    }
    
    oauth_url = "https://accounts.google.com/o/oauth2/auth?" + urlencode(params)
    print(f"   {oauth_url}")
    print()
    print("2. Authorize the app")
    print("3. Copy the 'code' from the redirect URL")
    print("4. Exchange it for access token using backend API")
    print()
    
    print("💡 ONCE YOU HAVE THE TOKEN:")
    print("─" * 40)
    print("Run this command:")
    print("   python youtube_test_to_json.py YOUR_ACCESS_TOKEN_HERE")
    print()
    print("The token should start with: ya29.")
    print("Example: ya29.a0ARrdaM-xBPvzQ7...")
    print()

def create_sample_test_results():
    """Create sample test results to show the structure"""
    sample_results = {
        "test_info": {
            "timestamp": datetime.now().isoformat(),
            "base_url": "http://localhost:8000",
            "test_version": "1.0",
            "note": "This is a SAMPLE - replace with real token to get actual data"
        },
        "connectivity_tests": {
            "backend_server": {
                "status": "SUCCESS",
                "response_time": 0.123,
                "data": "OK"
            },
            "google_api": {
                "status": "PENDING",
                "note": "Need valid access token"
            },
            "recent_activity": {
                "status": "PENDING", 
                "note": "Need valid access token"
            },
            "roi_dashboard": {
                "status": "PENDING",
                "note": "Need valid access token"
            }
        },
        "youtube_data": {
            "note": "This will contain your actual YouTube ROI data when you provide a valid token",
            "expected_structure": {
                "channel_overview": {
                    "channel_id": "UC...",
                    "title": "Your Channel Name",
                    "subscribers": 1234,
                    "total_videos": 56,
                    "total_views": 123456
                },
                "recent_activity": {
                    "total_activities": 10,
                    "roi_summary": {
                        "total_recent_views": 5000,
                        "total_recent_likes": 150,
                        "total_recent_comments": 25,
                        "avg_engagement_rate": 3.5
                    },
                    "recent_activity": [
                        {
                            "type": "video_upload",
                            "title": "Your Video Title",
                            "video_id": "dQw4w9WgXcQ",
                            "roi_metrics": {
                                "views": 1000,
                                "likes": 50,
                                "comments": 10,
                                "engagement_rate": 6.0
                            }
                        }
                    ]
                },
                "roi_analytics": {
                    "roi_analytics": {
                        "performance_metrics": {
                            "total_views_period": 10000,
                            "total_likes_period": 300,
                            "total_comments_period": 50,
                            "avg_engagement_rate": 3.5,
                            "videos_analyzed": 5
                        },
                        "revenue_estimates": {
                            "estimated_monthly_revenue": 25.50,
                            "estimated_annual_revenue": 306.00,
                            "revenue_per_subscriber": 0.0207
                        },
                        "roi_recommendations": [
                            {
                                "priority": "HIGH",
                                "category": "Content Optimization", 
                                "recommendation": "Upload more frequently to improve engagement"
                            }
                        ]
                    }
                }
            }
        },
        "errors": [],
        "test_summary": {
            "total_tests": 4,
            "successful_tests": 1,
            "failed_tests": 0,
            "error_tests": 0,
            "total_errors": 0,
            "data_retrieved": False,
            "note": "Provide access token to retrieve actual data"
        }
    }
    
    # Save sample results
    filename = f"youtube_roi_sample_structure_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        import os
        os.makedirs("test_results", exist_ok=True)
        
        with open(f"test_results/{filename}", 'w', encoding='utf-8') as f:
            json.dump(sample_results, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Sample structure saved to: test_results/{filename}")
        return f"test_results/{filename}"
    except Exception as e:
        print(f"❌ Could not save sample: {e}")
        return None

def main():
    print("🎬 YouTube Access Token Helper")
    print("=" * 60)
    
    show_token_instructions()
    
    print("📋 CREATING SAMPLE JSON STRUCTURE...")
    sample_file = create_sample_test_results()
    
    if sample_file:
        print(f"✅ Sample JSON created: {sample_file}")
        print()
        print("🚀 NEXT STEPS:")
        print("1. Get your access token using one of the methods above")
        print("2. Run: python youtube_test_to_json.py YOUR_TOKEN")
        print("3. Your actual YouTube ROI data will be saved to JSON!")

if __name__ == "__main__":
    main()
