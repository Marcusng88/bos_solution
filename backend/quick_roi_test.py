#!/usr/bin/env python3
"""
Quick ROI Metrics Test - Simple test to check if data can be retrieved
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent))
from app.core.supabase_client import supabase_client

load_dotenv()

async def quick_roi_test():
    """Quick test to check ROI metrics data retrieval"""
    print("🔍 Quick ROI Metrics Data Retrieval Test")
    print("=" * 50)
    
    # Check environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Missing environment variables:")
        print(f"   SUPABASE_URL: {'✅' if supabase_url else '❌'}")
        print(f"   SUPABASE_SERVICE_ROLE_KEY: {'✅' if supabase_key else '❌'}")
        return False
    
    print("✅ Environment variables found")
    
    try:
        # Test 1: Check if table exists
        print("\n📊 Testing table access...")
        response = await supabase_client._make_request("GET", "roi_metrics", params={"limit": "1"})
        
        if response.status_code != 200:
            print(f"❌ Table access failed: Status {response.status_code}")
            return False
        
        print("✅ roi_metrics table is accessible")
        
        # Test 2: Check data count
        print("\n📈 Checking data count...")
        count_response = await supabase_client._make_request("GET", "roi_metrics", params={"select": "id"})
        
        if count_response.status_code == 200:
            data = count_response.json()
            count = len(data)
            print(f"✅ Found {count} records in roi_metrics table")
            
            if count == 0:
                print("⚠️  Table is empty - no data to retrieve")
                return True  # Table exists but empty is still a success
        else:
            print(f"❌ Count query failed: Status {count_response.status_code}")
            return False
        
        # Test 3: Get sample data
        print("\n📋 Getting sample data...")
        sample_response = await supabase_client._make_request(
            "GET", 
            "roi_metrics", 
            params={
                "select": "id,platform,views,revenue_generated,update_timestamp",
                "limit": "3",
                "order": "update_timestamp.desc"
            }
        )
        
        if sample_response.status_code == 200:
            sample_data = sample_response.json()
            print(f"✅ Successfully retrieved {len(sample_data)} sample records")
            
            if sample_data:
                print("\n📊 Sample data preview:")
                for i, record in enumerate(sample_data[:2], 1):
                    print(f"   Record {i}:")
                    print(f"     Platform: {record.get('platform', 'N/A')}")
                    print(f"     Views: {record.get('views', 0)}")
                    print(f"     Revenue: ${record.get('revenue_generated', 0):.2f}")
                    print(f"     Updated: {record.get('update_timestamp', 'N/A')}")
        else:
            print(f"❌ Sample data retrieval failed: Status {sample_response.status_code}")
            return False
        
        # Test 4: Test filtered query
        print("\n🔍 Testing filtered query...")
        filter_response = await supabase_client._make_request(
            "GET",
            "roi_metrics",
            params={
                "platform": "eq.youtube",
                "select": "platform,views",
                "limit": "5"
            }
        )
        
        if filter_response.status_code == 200:
            filter_data = filter_response.json()
            print(f"✅ Filtered query returned {len(filter_data)} YouTube records")
        else:
            print(f"❌ Filtered query failed: Status {filter_response.status_code}")
            return False
        
        print("\n" + "=" * 50)
        print("🎉 SUCCESS: ROI metrics data can be retrieved successfully!")
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

async def main():
    """Main function"""
    success = await quick_roi_test()
    
    if success:
        print("\n✅ CONCLUSION: ROI metrics data retrieval is working properly!")
        return 0
    else:
        print("\n❌ CONCLUSION: Issues found with ROI metrics data retrieval.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
