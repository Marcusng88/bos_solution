#!/usr/bin/env python3
"""
Check ROI Data in Supabase - Debug script to see current state
"""

import asyncio
import os
from dotenv import load_dotenv
from datetime import datetime
import sys
from pathlib import Path

# Add the backend directory to the path so we can import the supabase client
sys.path.append(str(Path(__file__).parent))
from app.core.supabase_client import supabase_client

load_dotenv()

async def check_database():
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not supabase_url or not supabase_key:
        print("❌ No SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY found")
        return
    
    try:
        print("🔗 Connecting to Supabase...")
        
        # Check if tables exist by trying to query them
        print("\n📊 Checking table existence...")
        
        # Check roi_metrics table
        try:
            roi_response = await supabase_client._make_request("GET", "roi_metrics", params={"limit": "1"})
            if roi_response.status_code == 200:
                print("✅ roi_metrics table exists")
                
                # Get count
                count_response = await supabase_client._make_request("GET", "roi_metrics", params={"select": "id"})
                if count_response.status_code == 200:
                    total_records = len(count_response.json())
                    print(f"Total ROI records: {total_records}")
                    
                    if total_records > 0:
                        # Get latest data
                        latest_response = await supabase_client._make_request(
                            "GET", 
                            "roi_metrics", 
                            params={
                                "select": "user_id,platform,update_timestamp",
                                "order": "update_timestamp.desc",
                                "limit": "10"
                            }
                        )
                        
                        if latest_response.status_code == 200:
                            latest_results = latest_response.json()
                            print("\n📅 Latest data:")
                            for row in latest_results:
                                print(f"  • {row.get('platform', 'unknown')} (user: {row.get('user_id', '')[:8]}...): latest: {row.get('update_timestamp', '')}")
                        else:
                            print("⚠️  Could not fetch latest data")
                    else:
                        print("⚠️  No data in roi_metrics table")
                else:
                    print("⚠️  Could not get record count")
            else:
                print("❌ roi_metrics table does not exist or is not accessible")
        except Exception as e:
            print(f"❌ Error checking roi_metrics: {e}")
        
        # Check users table
        try:
            users_response = await supabase_client._make_request("GET", "users", params={"select": "clerk_id", "limit": "5"})
            if users_response.status_code == 200:
                users = users_response.json()
                print(f"\n👥 Found {len(users)} users: {[u.get('clerk_id', '') for u in users]}")
            else:
                print("❌ users table does not exist or is not accessible")
        except Exception as e:
            print(f"❌ Error checking users: {e}")
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")

if __name__ == "__main__":
    asyncio.run(check_database())
