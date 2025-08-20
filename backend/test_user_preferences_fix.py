"""
Test the fixed user preferences endpoint with proper user creation
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

async def test_complete_user_flow():
    """Test the complete user creation and preferences flow"""
    print("🧪 Testing Complete User Flow")
    print("=" * 40)
    
    try:
        from app.core.supabase_client import supabase_client
        
        test_user_id = "test_user_complete_flow"
        
        # Step 1: Create user first
        print("1. Creating user...")
        user_data = {
            "clerk_id": test_user_id,
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "is_active": True
        }
        
        user_result = await supabase_client.upsert_user(user_data)
        print(f"   User creation result: {user_result}")
        
        if not user_result or not user_result.get("success"):
            print("❌ Failed to create user")
            return False
        
        # Step 2: Create user preferences
        print("\n2. Creating user preferences...")
        preferences_data = {
            "user_id": test_user_id,
            "industry": "Fashion & Retail",
            "company_size": "1-10",
            "marketing_goals": ["brand_awareness", "lead_generation"],
            "monthly_budget": "$1,000 - $5,000"
        }
        
        prefs_result = await supabase_client.upsert_user_preferences(test_user_id, preferences_data)
        print(f"   Preferences creation result: {prefs_result}")
        
        if not prefs_result or not prefs_result.get("success"):
            print("❌ Failed to create user preferences")
            return False
        
        # Step 3: Verify we can retrieve the preferences
        print("\n3. Retrieving user preferences...")
        retrieved_prefs = await supabase_client.get_user_preferences(test_user_id)
        print(f"   Retrieved preferences: {retrieved_prefs}")
        
        if not retrieved_prefs:
            print("❌ Failed to retrieve user preferences")
            return False
        
        print("\n✅ Complete user flow test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Complete flow test failed: {e}")
        return False

async def test_api_endpoint():
    """Test the actual API endpoint"""
    print("\n🌐 Testing API Endpoint")
    print("=" * 40)
    
    try:
        import httpx
        
        # Test data that matches what the frontend would send
        api_data = {
            "industry": "Fashion & Retail",
            "company_size": "small",  # Frontend value
            "marketing_goals": ["brand_awareness", "lead_generation"],
            "monthly_budget": "1000-5000"  # Frontend value
        }
        
        # Simulate a valid Clerk user ID in header
        headers = {
            "Content-Type": "application/json",
            "x-user-id": "test_api_user_123"  # This would normally come from Clerk
        }
        
        print(f"🔄 POST to /api/v1/user-preferences/")
        print(f"Data: {api_data}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/v1/user-preferences/",
                headers=headers,
                json=api_data
            )
            
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.text}")
            
            if response.status_code == 200:
                print("✅ API endpoint test successful!")
                return True
            else:
                print(f"❌ API endpoint test failed with status {response.status_code}")
                return False
            
    except Exception as e:
        print(f"❌ API endpoint test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🔧 Testing Fixed User Preferences")
    print("=" * 50)
    
    # Test 1: Complete flow with Supabase client
    flow_test = await test_complete_user_flow()
    
    # Test 2: API endpoint test
    api_test = await test_api_endpoint()
    
    print("\n📊 Test Results")
    print("=" * 30)
    print(f"Complete Flow: {'✅ PASS' if flow_test else '❌ FAIL'}")
    print(f"API Endpoint: {'✅ PASS' if api_test else '❌ FAIL'}")
    
    if flow_test and api_test:
        print("\n🎉 All tests passed! The user preferences issue is fixed.")
        print("💡 Users will now be automatically created if they don't exist when saving preferences.")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main())
