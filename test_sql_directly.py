#!/usr/bin/env python3
"""
Direct SQL test script to verify the ongoing campaigns calculation
Run this to check if the SQL queries work correctly
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_sql_directly():
    """Test SQL queries directly against the database"""
    
    # Get database connection details from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("Error: DATABASE_URL not found in environment variables")
        return
    
    try:
        # Connect to database
        print("Connecting to database...")
        conn = await asyncpg.connect(database_url)
        print("✅ Database connection successful!")
        
        # Test 1: Count ongoing campaigns
        print("\n--- Test 1: Count Ongoing Campaigns ---")
        ongoing_count = await conn.fetchval("""
            SELECT COUNT(*) 
            FROM campaign_data 
            WHERE ongoing = 'Yes'
        """)
        print(f"Ongoing campaigns count: {ongoing_count}")
        
        # Test 2: Calculate active spend and budget
        print("\n--- Test 2: Active Spend and Budget ---")
        spend_budget = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_ongoing_campaigns,
                COALESCE(SUM(spend), 0) as total_active_spend,
                COALESCE(SUM(budget), 0) as total_active_budget
            FROM campaign_data 
            WHERE ongoing = 'Yes'
        """)
        
        print(f"Total ongoing campaigns: {spend_budget['total_ongoing_campaigns']}")
        print(f"Total active spend: ${spend_budget['total_active_spend']:,.2f}")
        print(f"Total active budget: ${spend_budget['total_active_budget']:,.2f}")
        
        # Calculate budget utilization
        if spend_budget['total_active_budget'] > 0:
            utilization = (spend_budget['total_active_spend'] / spend_budget['total_active_budget']) * 100
            print(f"Budget utilization: {utilization:.2f}%")
        else:
            print("Budget utilization: 0% (no budget)")
        
        # Test 3: List ongoing campaigns
        print("\n--- Test 3: Ongoing Campaigns Details ---")
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
        """)
        
        print(f"Found {len(ongoing_campaigns)} ongoing campaigns:")
        for campaign in ongoing_campaigns:
            print(f"  - {campaign['name']}: ${campaign['spend']:,.2f} / ${campaign['budget']:,.2f}")
        
        # Test 4: Check if alerts and risk patterns tables exist
        print("\n--- Test 4: Check Alerts and Risk Tables ---")
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('optimization_alerts', 'risk_patterns')
        """)
        
        existing_tables = [table['table_name'] for table in tables]
        print(f"Existing tables: {existing_tables}")
        
        # Check if tables have data
        for table_name in existing_tables:
            count = await conn.fetchval(f"SELECT COUNT(*) FROM {table_name}")
            print(f"  {table_name}: {count} records")
        
        await conn.close()
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Testing SQL Queries Directly...")
    asyncio.run(test_sql_directly())
