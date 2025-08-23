#!/usr/bin/env python3
"""
Script to add sample ROI data for testing the report generator
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

load_dotenv()

async def add_sample_data():
    """Add sample ROI data to the database"""
    
    print("📊 Adding Sample ROI Data")
    print("=" * 50)
    
    try:
        from app.core.supabase_client import supabase_client
        
        # Sample data for different platforms
        platforms = ["facebook", "instagram", "youtube", "tiktok", "twitter"]
        content_types = ["video", "image", "carousel", "story", "reel"]
        content_categories = ["product", "lifestyle", "educational", "entertainment", "promotional"]
        
        # Generate data for current month and previous month
        now = datetime.now(timezone.utc)
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        previous_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
        
        sample_records = []
        
        # Current month data
        for i in range(50):
            platform = platforms[i % len(platforms)]
            content_type = content_types[i % len(content_types)]
            content_category = content_categories[i % len(content_categories)]
            
            # Generate random date within current month
            days_offset = i % 30
            record_date = current_month_start + timedelta(days=days_offset)
            
            # Generate realistic metrics
            views = 1000 + (i * 100)
            likes = int(views * 0.05) + (i * 10)
            comments = int(views * 0.01) + (i * 2)
            shares = int(views * 0.02) + (i * 5)
            clicks = int(views * 0.03) + (i * 3)
            ad_spend = 50.0 + (i * 10.0)
            revenue_generated = ad_spend * (1.5 + (i * 0.1))
            roi_percentage = ((revenue_generated - ad_spend) / ad_spend) * 100
            
            record = {
                "user_id": "sample_user_123",
                "platform": platform,
                "content_type": content_type,
                "content_category": content_category,
                "views": views,
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "clicks": clicks,
                "ad_spend": ad_spend,
                "revenue_generated": revenue_generated,
                "roi_percentage": roi_percentage,
                "roas_ratio": revenue_generated / ad_spend,
                "update_timestamp": record_date.isoformat(),
                "created_at": record_date.isoformat(),
                "updated_at": record_date.isoformat()
            }
            sample_records.append(record)
        
        # Previous month data
        for i in range(30):
            platform = platforms[i % len(platforms)]
            content_type = content_types[i % len(content_types)]
            content_category = content_categories[i % len(content_categories)]
            
            # Generate random date within previous month
            days_offset = i % 30
            record_date = previous_month_start + timedelta(days=days_offset)
            
            # Generate realistic metrics (slightly lower for previous month)
            views = 800 + (i * 80)
            likes = int(views * 0.04) + (i * 8)
            comments = int(views * 0.008) + (i * 1)
            shares = int(views * 0.015) + (i * 3)
            clicks = int(views * 0.025) + (i * 2)
            ad_spend = 40.0 + (i * 8.0)
            revenue_generated = ad_spend * (1.3 + (i * 0.08))
            roi_percentage = ((revenue_generated - ad_spend) / ad_spend) * 100
            
            record = {
                "user_id": "sample_user_123",
                "platform": platform,
                "content_type": content_type,
                "content_category": content_category,
                "views": views,
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "clicks": clicks,
                "ad_spend": ad_spend,
                "revenue_generated": revenue_generated,
                "roi_percentage": roi_percentage,
                "roas_ratio": revenue_generated / ad_spend,
                "update_timestamp": record_date.isoformat(),
                "created_at": record_date.isoformat(),
                "updated_at": record_date.isoformat()
            }
            sample_records.append(record)
        
        print(f"Generated {len(sample_records)} sample records")
        
        # Insert records in batches
        batch_size = 10
        for i in range(0, len(sample_records), batch_size):
            batch = sample_records[i:i + batch_size]
            
            print(f"Inserting batch {i//batch_size + 1}/{(len(sample_records) + batch_size - 1)//batch_size}...")
            
            response = await supabase_client._make_request(
                "POST",
                "roi_metrics",
                data=batch
            )
            
            if response.status_code == 201:
                print(f"✅ Batch {i//batch_size + 1} inserted successfully")
            else:
                print(f"❌ Batch {i//batch_size + 1} failed: {response.status_code}")
                print(f"Response: {response.text}")
        
        print("\n✅ Sample data insertion completed!")
        print(f"📊 Total records added: {len(sample_records)}")
        print(f"📅 Data spans: {previous_month_start.strftime('%B %Y')} to {current_month_start.strftime('%B %Y')}")
        print("\nYou can now test the report generator!")
        
    except Exception as e:
        print(f"❌ Error adding sample data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(add_sample_data())
