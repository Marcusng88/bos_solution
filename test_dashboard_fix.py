#!/usr/bin/env python3
"""
Test script to verify dashboard metrics are working
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_dashboard_metrics():
    """Test the dashboard metrics calculation"""
    
    # Get database connection details
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ Error: DATABASE_URL not found in environment variables")
        return
    
    try:
        # Connect to database
        print("🔌 Connecting to database...")
        conn = await asyncpg.connect(database_url)
        print("✅ Database connection successful!")
        
        # Test 1: Check ongoing campaigns and calculate active spend
        print("\n📊 Test 1: Active Spend and Budget Calculation")
        
        # Count ongoing campaigns
        ongoing_count = await conn.fetchval("""
            SELECT COUNT(*) 
            FROM campaign_data 
            WHERE ongoing = 'Yes'
        """)
        print(f"🔄 Ongoing campaigns: {ongoing_count}")
        
        # Calculate active spend and budget
        spend_budget = await conn.fetchrow("""
            SELECT 
                COALESCE(SUM(spend), 0) as active_spend,
                COALESCE(SUM(budget), 0) as active_budget
            FROM campaign_data 
            WHERE ongoing = 'Yes'
        """)
        
        active_spend = spend_budget['active_spend'] if spend_budget else 0
        active_budget = spend_budget['active_budget'] if spend_budget else 0
        
        print(f"💰 Active spend: ${active_spend:,.2f}")
        print(f"💳 Active budget: ${active_budget:,.2f}")
        
        # Calculate budget utilization
        if active_budget > 0:
            utilization = (active_spend / active_budget) * 100
            print(f"📊 Budget utilization: {utilization:.2f}%")
        else:
            print("📊 Budget utilization: 0% (no budget)")
        
        # Test 2: Check if alerts and risks tables exist
        print("\n🚨 Test 2: Alerts and Risks Tables")
        
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('optimization_alerts', 'risk_patterns', 'optimization_recommendations')
        """)
        
        existing_tables = [table['table_name'] for table in tables]
        print(f"Existing tables: {existing_tables}")
        
        # Test 3: Count alerts, risks, and recommendations for a test user
        test_user_id = 'test-user-123'
        print(f"\n👤 Test 3: Counts for user '{test_user_id}'")
        
        if 'optimization_alerts' in existing_tables:
            alerts_count = await conn.fetchval("""
                SELECT COUNT(*) 
                FROM optimization_alerts 
                WHERE user_id = $1 AND is_read = false
            """, test_user_id)
            print(f"🚨 Unread alerts: {alerts_count}")
        else:
            print("🚨 optimization_alerts table does not exist")
        
        if 'risk_patterns' in existing_tables:
            risks_count = await conn.fetchval("""
                SELECT COUNT(*) 
                FROM risk_patterns 
                WHERE user_id = $1 AND resolved = false
            """, test_user_id)
            print(f"⚠️ Unresolved risks: {risks_count}")
        else:
            print("⚠️ risk_patterns table does not exist")
        
        if 'optimization_recommendations' in existing_tables:
            recs_count = await conn.fetchval("""
                SELECT COUNT(*) 
                FROM optimization_recommendations 
                WHERE user_id = $1 AND is_applied = false
            """, test_user_id)
            print(f"💡 Unapplied recommendations: {recs_count}")
        else:
            print("💡 optimization_recommendations table does not exist")
        
        # Test 4: Show sample ongoing campaigns
        print("\n📋 Test 4: Sample Ongoing Campaigns")
        ongoing_campaigns = await conn.fetch("""
            SELECT 
                id,
                name,
                ongoing,
                spend,
                budget,
                date
            FROM campaign_data 
            WHERE ongoing = 'Yes'
            ORDER BY date DESC
            LIMIT 5
        """)
        
        print(f"Found {len(ongoing_campaigns)} ongoing campaigns:")
        for campaign in ongoing_campaigns:
            print(f"  - {campaign['name']}: ${campaign['spend']:,.2f} / ${campaign['budget']:,.2f}")
        
        await conn.close()
        print("\n✅ All tests completed successfully!")
        
        # Summary
        print("\n📊 SUMMARY - Expected Dashboard Values:")
        print(f"Active Spend: ${active_spend:,.2f}")
        print(f"Budget Utilization: {utilization:.2f}%" if active_budget > 0 else "Budget Utilization: 0%")
        print(f"Active Alerts: {alerts_count if 'optimization_alerts' in existing_tables else 0}")
        print(f"Risk Patterns: {risks_count if 'risk_patterns' in existing_tables else 0}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 Test Dashboard Metrics Fix")
    print("=" * 40)
    asyncio.run(test_dashboard_metrics())
