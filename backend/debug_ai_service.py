#!/usr/bin/env python3
"""
Debug script to test AI service database connection
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_ai_service_database():
    """Test the AI service database queries directly"""
    
    print("🔍 Testing AI Service Database Queries")
    print("=" * 50)
    
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
            
            # Test campaign data query (exactly like AI service)
            print("\n📊 Testing Campaign Data Query...")
            campaign_query = text("""
                SELECT name, date, impressions, clicks, ctr, cpc, spend, budget, 
                       conversions, net_profit, ongoing
                FROM campaign_data 
                ORDER BY date DESC
                LIMIT 50
            """)
            
            result = connection.execute(campaign_query)
            campaigns = []
            
            for row in result:
                campaigns.append({
                    "name": row.name,
                    "date": row.date.isoformat() if row.date else None,
                    "impressions": row.impressions,
                    "clicks": row.clicks,
                    "ctr": row.ctr,
                    "cpc": row.cpc,
                    "spend": row.spend,
                    "budget": row.budget,
                    "conversions": row.conversions,
                    "net_profit": row.net_profit,
                    "ongoing": row.ongoing
                })
            
            print(f"✅ Campaign query successful: {len(campaigns)} campaigns found")
            
            if campaigns:
                print("📋 Sample campaigns:")
                for i, campaign in enumerate(campaigns[:3]):
                    print(f"   {i+1}. {campaign['name']}: ${campaign['spend']:.2f} spent, {campaign['conversions']} conversions")
            else:
                print("❌ No campaigns found!")
            
            # Test competitor data query
            print("\n🏢 Testing Competitor Data Query...")
            competitor_query = text("""
                SELECT name, industry, website_url, social_media_handles, status
                FROM competitors 
                WHERE status = 'active'
                LIMIT 10
            """)
            
            result = connection.execute(competitor_query)
            competitors = []
            
            for row in result:
                competitors.append({
                    "name": row.name,
                    "industry": row.industry,
                    "website": row.website_url,
                    "social_media": row.social_media_handles,
                    "status": row.status
                })
            
            print(f"✅ Competitor query successful: {len(competitors)} competitors found")
            
            if competitors:
                print("📋 Sample competitors:")
                for i, competitor in enumerate(competitors[:3]):
                    print(f"   {i+1}. {competitor['name']} ({competitor['industry']}): {competitor['status']}")
            else:
                print("❌ No competitors found!")
            
            # Test monitoring data query
            print("\n👁️  Testing Monitoring Data Query...")
            monitoring_query = text("""
                SELECT platform, content_text, engagement_metrics, sentiment_score, 
                       posted_at, competitor_id
                FROM monitoring_data 
                ORDER BY posted_at DESC
                LIMIT 20
            """)
            
            result = connection.execute(monitoring_query)
            monitoring_data = []
            
            for row in result:
                monitoring_data.append({
                    "platform": row.platform,
                    "content": row.content_text,
                    "engagement": row.engagement_metrics,
                    "sentiment": row.sentiment_score,
                    "posted_at": row.posted_at.isoformat() if row.posted_at else None,
                    "competitor_id": row.competitor_id
                })
            
            print(f"✅ Monitoring query successful: {len(monitoring_data)} records found")
            
            if monitoring_data:
                print("📋 Sample monitoring data:")
                for i, data in enumerate(monitoring_data[:3]):
                    content_preview = data['content'][:50] + "..." if len(data['content']) > 50 else data['content']
                    print(f"   {i+1}. {data['platform']}: {content_preview}")
            else:
                print("❌ No monitoring data found!")
            
            # Summary
            print("\n📊 Summary:")
            print(f"   Campaigns: {len(campaigns)}")
            print(f"   Competitors: {len(competitors)}")
            print(f"   Monitoring: {len(monitoring_data)}")
            
            if len(campaigns) > 0:
                print("✅ AI service should work with this data!")
            else:
                print("❌ AI service will fail - no campaign data!")
            
            return True
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_ai_service_database()
    
    if success:
        print("\n✅ Debug test completed successfully!")
    else:
        print("\n❌ Debug test failed!")
        sys.exit(1)
