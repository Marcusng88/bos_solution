#!/usr/bin/env python3
"""
Test script to debug AI endpoint directly
"""

import os
import asyncio
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from app.services.ai_service import ai_service

# Load environment variables
load_dotenv()

async def test_ai_endpoint():
    """Test the AI endpoint directly"""
    
    print("🔍 Testing AI Endpoint Directly")
    print("=" * 40)
    
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
        
        # Test the exact same call that the endpoint makes
        print("\n🤖 Testing AI chat response...")
        response = await ai_service.chat_with_ai(db, "test_user", "How are my campaigns performing?")
        
        print(f"✅ AI response generated: {len(response)} characters")
        print(f"📝 Response preview: {response[:500]}...")
        
        # Check if response mentions real data
        if "Adidas Boost Launch" in response or "CocaCola Refresh 2025" in response:
            print("✅ AI response contains real campaign data!")
        elif "Error Recovery Campaign" in response:
            print("❌ AI response contains sample data instead of real data")
        elif "empty" in response.lower() or "no data" in response.lower():
            print("❌ AI response mentions empty data")
        else:
            print("⚠️  AI response content unclear")
        
        # Test campaign analysis
        print("\n📊 Testing campaign analysis...")
        analysis = await ai_service.analyze_campaign_data(db, "test_user")
        
        print(f"✅ Analysis generated: {len(analysis.get('insights', ''))} characters")
        print(f"📊 Performance score: {analysis.get('performance_score', 'N/A')}")
        print(f"📋 Recommendations: {len(analysis.get('recommendations', []))}")
        print(f"⚠️  Risk alerts: {len(analysis.get('risk_alerts', []))}")
        
        # Show some insights to verify real data
        insights = analysis.get('insights', '')
        if "Adidas Boost Launch" in insights or "CocaCola Refresh 2025" in insights:
            print("✅ Analysis contains real campaign data!")
        else:
            print("❌ Analysis might not contain real campaign data")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_ai_endpoint())
    
    if success:
        print("\n✅ Endpoint test completed successfully!")
    else:
        print("\n❌ Endpoint test failed!")
