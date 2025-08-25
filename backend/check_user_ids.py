#!/usr/bin/env python3
"""
Quick test to check what user IDs are in the monitoring_alerts table
"""

import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.services.monitoring.supabase_client import supabase_client

def check_user_ids_in_alerts_table():
    """Check what user IDs exist in monitoring_alerts table"""
    
    print("🔍 Checking User IDs in monitoring_alerts table...")
    
    if not supabase_client or not supabase_client.client:
        print("❌ Supabase client not available")
        return
    
    try:
        # Get unique user IDs from monitoring_alerts table
        response = supabase_client.client.table('monitoring_alerts').select('user_id').execute()
        
        if response.data:
            user_ids = [row['user_id'] for row in response.data if row.get('user_id')]
            unique_user_ids = list(set(user_ids))
            
            print(f"✅ Found {len(response.data)} total alerts")
            print(f"✅ Found {len(unique_user_ids)} unique user IDs:")
            
            for uid in unique_user_ids:
                count = user_ids.count(uid)
                print(f"   - {uid} ({count} alerts)")
                
                # Check if this matches common Clerk formats
                if uid.startswith('user_'):
                    print(f"     ✅ Matches Clerk format")
                else:
                    print(f"     ⚠️ Non-standard format")
        else:
            print("❌ No data found in monitoring_alerts table")
            
    except Exception as e:
        print(f"❌ Error querying monitoring_alerts table: {e}")

if __name__ == "__main__":
    check_user_ids_in_alerts_table()
