#!/usr/bin/env python3
"""
Quick YouTube Test Command Generator
"""

import os
from datetime import datetime

def generate_test_commands():
    print("🎬 YOUTUBE ROI DATA TO JSON - COMMAND GUIDE")
    print("=" * 70)
    print()
    
    print("📋 STEP 1: Get Your Access Token")
    print("─" * 50)
    print("Since you mentioned you connected with YouTube, your token should be available.")
    print("Check browser dev tools (F12) > Application > Local Storage")
    print("Or check Network tab for requests with 'access_token'")
    print()
    
    print("🚀 STEP 2: Run The Test (Replace YOUR_TOKEN)")
    print("─" * 50)
    print("cd \"d:\\Bos_Solution (2)\\bos_solution\\backend\"")
    print("python youtube_test_to_json.py YOUR_ACCESS_TOKEN_HERE")
    print()
    
    print("📊 STEP 3: What You'll Get")
    print("─" * 50)
    print("✅ Complete channel analytics")
    print("✅ Recent activity (views, likes, comments)")
    print("✅ ROI calculations and metrics")
    print("✅ Revenue estimates")
    print("✅ Performance recommendations")
    print("✅ All data saved in JSON format")
    print()
    
    print("💡 ALTERNATIVE: Test Individual Endpoints")
    print("─" * 50)
    print("If you have your access token, you can also test individual endpoints:")
    print()
    
    print("# Test Recent Activity (last 24 hours)")
    print("curl \"http://localhost:8000/api/v1/youtube/recent-activity?access_token=YOUR_TOKEN&hours_back=24\"")
    print()
    
    print("# Test ROI Dashboard (last 7 days)")  
    print("curl \"http://localhost:8000/api/v1/youtube/analytics/roi-dashboard?access_token=YOUR_TOKEN&days_back=7\"")
    print()
    
    print("# Test Debug Endpoint")
    print("curl \"http://localhost:8000/api/v1/youtube/debug/full-test?access_token=YOUR_TOKEN\"")
    print()
    
    print("🔍 EXAMPLE OUTPUT FILES:")
    print("─" * 50)
    print("After running, you'll get files like:")
    print("📁 test_results/youtube_roi_test_results_20250819_HHMMSS.json")
    print()
    print("The JSON will contain:")
    print("  📺 Channel info (subscribers, views, videos)")
    print("  ⏰ Recent activity analysis") 
    print("  💰 ROI metrics and calculations")
    print("  📊 Performance analytics")
    print("  💡 Optimization recommendations")
    print("  💵 Revenue estimates")
    print()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"⏰ Generated at: {timestamp}")

if __name__ == "__main__":
    generate_test_commands()
