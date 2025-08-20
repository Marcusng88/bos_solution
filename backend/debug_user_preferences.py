"""
Debug script to test user preferences creation and identify the exact error
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

async def test_user_preferences_api():
    """Test the user preferences API directly"""
    print("🧪 Testing User Preferences API")
    print("=" * 40)
    
    try:
        import httpx
        
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not supabase_url or not supabase_key:
            print("❌ Missing Supabase configuration")
            return False
        
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json"
        }
        
        # Test data (sample user preferences)
        test_preferences = {
            "user_id": "test_user_123",
            "industry": "Fashion & Retail",
            "company_size": "1-10",
            "marketing_goals": ["brand_awareness", "lead_generation"],
            "monthly_budget": "$1,000 - $5,000"
        }
        
        print(f"🔄 Testing POST to user_preferences table...")
        print(f"Data: {test_preferences}")
        
        async with httpx.AsyncClient() as client:
            # First, check if table exists and is accessible
            print("\n1. Testing table access...")
            response = await client.get(f"{supabase_url}/rest/v1/user_preferences?limit=1", headers=headers)
            print(f"   GET user_preferences: {response.status_code}")
            if response.status_code != 200:
                print(f"   Error: {response.text}")
                return False
            
            # Now try to create a preference
            print("\n2. Testing POST (create)...")
            response = await client.post(f"{supabase_url}/rest/v1/user_preferences", headers=headers, json=test_preferences)
            print(f"   POST user_preferences: {response.status_code}")
            print(f"   Response: {response.text}")
            
            if response.status_code not in [200, 201, 204]:
                print(f"❌ Failed to create user preferences")
                
                # Check if it's a constraint error
                if "violates" in response.text.lower():
                    print("🔍 This appears to be a database constraint violation")
                    print("   Possible issues:")
                    print("   - Invalid company_size value")
                    print("   - Invalid monthly_budget value") 
                    print("   - Missing required fields")
                    print("   - Foreign key constraint (user doesn't exist)")
                
                return False
            else:
                print("✅ Successfully created user preferences")
                
                # Clean up test data
                print("\n3. Cleaning up test data...")
                delete_response = await client.delete(
                    f"{supabase_url}/rest/v1/user_preferences?user_id=eq.test_user_123", 
                    headers=headers
                )
                print(f"   DELETE: {delete_response.status_code}")
                
                return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

async def test_with_supabase_client():
    """Test using our Supabase client"""
    print("\n🧪 Testing with Supabase Client")
    print("=" * 40)
    
    try:
        from app.core.supabase_client import supabase_client
        
        test_preferences = {
            "user_id": "test_user_456",
            "industry": "Fashion & Retail",
            "company_size": "1-10",
            "marketing_goals": ["brand_awareness", "lead_generation"],
            "monthly_budget": "$1,000 - $5,000"
        }
        
        print("🔄 Testing upsert_user_preferences...")
        result = await supabase_client.upsert_user_preferences("test_user_456", test_preferences)
        print(f"Result: {result}")
        
        if result and result.get("success"):
            print("✅ Supabase client test successful")
            
            # Clean up
            print("🧹 Cleaning up...")
            # Note: We'd need a delete method in the client, but for now just report success
            return True
        else:
            print("❌ Supabase client test failed")
            return False
        
    except Exception as e:
        print(f"❌ Supabase client test failed: {e}")
        print(f"   Error details: {str(e)}")
        return False

async def main():
    """Run all tests"""
    print("🔧 Debugging User Preferences API Issue")
    print("=" * 50)
    
    # Test 1: Direct API test
    api_test = await test_user_preferences_api()
    
    # Test 2: Supabase client test
    client_test = await test_with_supabase_client()
    
    print("\n📊 Debug Results")
    print("=" * 30)
    print(f"Direct API Test: {'✅ PASS' if api_test else '❌ FAIL'}")
    print(f"Client Test: {'✅ PASS' if client_test else '❌ FAIL'}")
    
    if not api_test and not client_test:
        print("\n🔍 Recommended fixes:")
        print("1. Check if user_preferences table exists in Supabase")
        print("2. Verify table schema matches expected fields")
        print("3. Check database constraints (company_size, monthly_budget)")
        print("4. Ensure RLS (Row Level Security) policies are correct")

if __name__ == "__main__":
    asyncio.run(main())
