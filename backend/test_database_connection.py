#!/usr/bin/env python3
"""
Test script to check database connection and available data
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_database_connection():
    """Test database connection and check available data"""
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    print(f"🔗 Connecting to database: {database_url.split('@')[1] if '@' in database_url else database_url}")
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as connection:
            print("✅ Database connection successful!")
            
            # Check if tables exist
            tables_query = text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            
            result = connection.execute(tables_query)
            tables = [row[0] for row in result]
            
            print(f"\n📋 Available tables: {tables}")
            
            # Check campaign_data table
            if 'campaign_data' in tables:
                print("\n📊 Checking campaign_data table...")
                
                # Count total records
                count_query = text("SELECT COUNT(*) as count FROM campaign_data")
                count_result = connection.execute(count_query)
                total_count = count_result.fetchone()[0]
                print(f"   Total records: {total_count}")
                
                if total_count > 0:
                    # Get sample data
                    sample_query = text("""
                        SELECT name, date, impressions, clicks, ctr, cpc, spend, budget, 
                               conversions, net_profit, ongoing
                        FROM campaign_data 
                        ORDER BY date DESC
                        LIMIT 5
                    """)
                    
                    sample_result = connection.execute(sample_query)
                    print("   Sample records:")
                    for row in sample_result:
                        print(f"     - {row.name}: ${row.spend:.2f} spent, {row.conversions} conversions")
                else:
                    print("   ⚠️  No campaign data found")
            
            # Check competitors table
            if 'competitors' in tables:
                print("\n🏢 Checking competitors table...")
                
                count_query = text("SELECT COUNT(*) as count FROM competitors")
                count_result = connection.execute(count_query)
                total_count = count_result.fetchone()[0]
                print(f"   Total records: {total_count}")
                
                if total_count > 0:
                    sample_query = text("SELECT name, industry, status FROM competitors LIMIT 5")
                    sample_result = connection.execute(sample_query)
                    print("   Sample records:")
                    for row in sample_result:
                        print(f"     - {row.name} ({row.industry}): {row.status}")
                else:
                    print("   ⚠️  No competitor data found")
            
            # Check monitoring_data table
            if 'monitoring_data' in tables:
                print("\n👁️  Checking monitoring_data table...")
                
                count_query = text("SELECT COUNT(*) as count FROM monitoring_data")
                count_result = connection.execute(count_query)
                total_count = count_result.fetchone()[0]
                print(f"   Total records: {total_count}")
                
                if total_count > 0:
                    sample_query = text("SELECT platform, content_text, sentiment_score FROM monitoring_data LIMIT 3")
                    sample_result = connection.execute(sample_query)
                    print("   Sample records:")
                    for row in sample_result:
                        content_preview = row.content_text[:50] + "..." if len(row.content_text) > 50 else row.content_text
                        print(f"     - {row.platform}: {content_preview}")
                else:
                    print("   ⚠️  No monitoring data found")
            
            # Check if we need to seed data
            if 'campaign_data' in tables:
                campaign_count = connection.execute(text("SELECT COUNT(*) FROM campaign_data")).fetchone()[0]
                if campaign_count == 0:
                    print("\n🌱 No campaign data found. Would you like to seed sample data?")
                    print("   Run: python seed_demo_data.py")
            
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Database Connection and Data Availability")
    print("=" * 50)
    
    success = test_database_connection()
    
    if success:
        print("\n✅ Database test completed successfully!")
    else:
        print("\n❌ Database test failed!")
        sys.exit(1)
