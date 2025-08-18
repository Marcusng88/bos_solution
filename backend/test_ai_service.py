#!/usr/bin/env python3
"""
Test script to verify AI service is working
"""

import os
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from app.services.ai_service import ai_service

# Load environment variables
load_dotenv()

async def test_ai_service():
    """Test the AI service directly"""
    
    print("🔍 Testing AI Service")
    print("=" * 30)
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    try:
        # Create engine and session
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        print("✅ Database session created")
        
        # Test campaign data retrieval
        print("\n📊 Testing campaign data retrieval...")
        campaign_data = await ai_service._get_campaign_data(db, "test_user")
        print(f"✅ Campaign data: {len(campaign_data)} campaigns found")
        
        if campaign_data:
            print("📋 Sample campaigns:")
            for i, campaign in enumerate(campaign_data[:3]):
                print(f"   {i+1}. {campaign['name']}: ${campaign['spend']:.2f} spent")
        else:
            print("❌ No campaign data found!")
        
        # Test competitor data retrieval
        print("\n🏢 Testing competitor data retrieval...")
        competitor_data = await ai_service._get_competitor_data(db, "test_user")
        print(f"✅ Competitor data: {len(competitor_data)} competitors found")
        
        if competitor_data:
            print("📋 Sample competitors:")
            for i, competitor in enumerate(competitor_data[:3]):
                print(f"   {i+1}. {competitor['name']} ({competitor['industry']})")
        else:
            print("❌ No competitor data found!")
        
        # Test monitoring data retrieval
        print("\n👁️  Testing monitoring data retrieval...")
        monitoring_data = await ai_service._get_monitoring_data(db, "test_user")
        print(f"✅ Monitoring data: {len(monitoring_data)} records found")
        
        # Test AI chat response
        print("\n🤖 Testing AI chat response...")
        response = await ai_service.chat_with_ai(db, "test_user", "How are my campaigns performing?")
        print(f"✅ AI response generated: {len(response)} characters")
        print(f"📝 Response preview: {response[:200]}...")
        
        # Check if response mentions empty data
        if "empty" in response.lower() or "no data" in response.lower():
            print("⚠️  AI response mentions empty data - this might indicate an issue")
        else:
            print("✅ AI response appears to have data")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_ai_service())
    
    if success:
        print("\n✅ AI service test completed successfully!")
    else:
        print("\n❌ AI service test failed!")
