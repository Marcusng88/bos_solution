#!/usr/bin/env python3
"""
Create Initial ROI Data - Seeds Supabase with starting metrics
so the automatic updates can begin working.
"""

import asyncio
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import sys
from pathlib import Path
import uuid

# Add the backend directory to the path so we can import the supabase client
sys.path.append(str(Path(__file__).parent))
from app.core.supabase_client import supabase_client

load_dotenv()

async def create_initial_data():
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not supabase_url or not supabase_key:
        print("❌ No SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY found")
        return False
    
    try:
        print("🔗 Connecting to Supabase...")
        
        # Check if we already have data
        count_response = await supabase_client._make_request("GET", "roi_metrics", params={"select": "id"})
        if count_response.status_code == 200:
            existing_count = len(count_response.json())
            if existing_count > 0:
                print(f"ℹ️  ROI metrics table already has {existing_count} records")
                print("🔄 Checking if we can generate new data based on existing...")
                return True
        
        print("📊 No existing ROI data found. Creating initial seed data...")
        
        # Create a demo user if none exists
        demo_user_id = "demo_user_roi_test"
        user_data = {
            "id": str(uuid.uuid4()),
            "clerk_id": demo_user_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        user_response = await supabase_client._make_request("POST", "users", data=user_data)
        if user_response.status_code in [200, 201]:
            print(f"✓ Ensured demo user exists: {demo_user_id}")
        else:
            print(f"⚠️  Demo user creation response: {user_response.status_code}")
        
        # Create initial campaigns
        campaign1_data = {
            "id": str(uuid.uuid4()),
            "user_id": demo_user_id,
            "name": "Demo Campaign 1",
            "start_date": (datetime.now().date() - timedelta(days=3)).isoformat(),
            "budget": 1000,
            "ongoing": True
        }
        
        campaign2_data = {
            "id": str(uuid.uuid4()),
            "user_id": demo_user_id,
            "name": "Demo Campaign 2", 
            "start_date": (datetime.now().date() - timedelta(days=1)).isoformat(),
            "budget": 1500,
            "ongoing": True
        }
        
        campaign1_response = await supabase_client._make_request("POST", "campaigns", data=campaign1_data)
        campaign2_response = await supabase_client._make_request("POST", "campaigns", data=campaign2_data)
        
        campaign1_id = campaign1_data["id"]
        campaign2_id = campaign2_data["id"]
        
        print(f"✓ Created campaigns: {campaign1_id}, {campaign2_id}")
        
        # Create initial ROI metrics for each platform
        platforms = ['facebook', 'instagram', 'youtube']
        base_timestamp = datetime.now() - timedelta(hours=2)  # 2 hours ago
        
        for platform in platforms:
            # Starting values (small but realistic)
            views = 100 + (hash(platform) % 200)  # 100-300 starting views
            likes = 10 + (hash(platform) % 20)    # 10-30 starting likes  
            comments = 2 + (hash(platform) % 8)   # 2-10 starting comments
            shares = 1 + (hash(platform) % 5)     # 1-6 starting shares
            clicks = 5 + (hash(platform) % 15)    # 5-20 starting clicks
            
            # Basic costs
            ad_spend = round(10 + (hash(platform) % 40), 2)  # $10-50
            revenue = round(ad_spend * (1.5 + (hash(platform) % 100) / 100), 2)  # 1.5x-2.5x revenue
            
            roi_percentage = ((revenue - ad_spend) / ad_spend) * 100 if ad_spend > 0 else 0
            roas_ratio = revenue / ad_spend if ad_spend > 0 else 0
            
            # Insert initial metric
            roi_data = {
                "id": str(uuid.uuid4()),
                "user_id": demo_user_id,
                "platform": platform,
                "campaign_id": campaign1_id if platform != 'youtube' else campaign2_id,
                "content_type": "video",
                "content_category": "demo",
                "views": views,
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "saves": 1,
                "clicks": clicks,
                "ad_spend": ad_spend,
                "revenue_generated": revenue,
                "cost_per_click": 1.50,
                "cost_per_impression": 0.010,
                "roi_percentage": roi_percentage,
                "roas_ratio": roas_ratio,
                "update_timestamp": base_timestamp.isoformat()
            }
            
            roi_response = await supabase_client._make_request("POST", "roi_metrics", data=roi_data)
            if roi_response.status_code not in [200, 201]:
                print(f"⚠️  Failed to create {platform} metrics: {roi_response.status_code}")
            else:
                print(f"✓ Created initial {platform} metrics: {views} views, ${revenue:.2f} revenue, {roi_percentage:.1f}% ROI")
            
            print(f"✓ Created initial {platform} metrics: {views} views, ${revenue:.2f} revenue, {roi_percentage:.1f}% ROI")
        
        print("\n🎉 Initial ROI data created successfully!")
        print(f"👤 Demo user: {demo_user_id}")
        print(f"📊 Platforms: {', '.join(platforms)}")
        print(f"🚀 The automatic scheduler can now generate updates!")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create initial data: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(create_initial_data())
    if success:
        print("\n✅ Ready for automatic updates!")
        print("💡 Now you can:")
        print("   1. Run: python generate_roi_data.py (to test manual generation)")
        print("   2. Run: python start_roi_scheduler.py (to start automatic updates)")
    else:
        print("\n❌ Setup failed. Please check the error above.")
