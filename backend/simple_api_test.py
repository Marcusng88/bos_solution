"""
Simple API test for user preferences
"""

import httpx
import asyncio

async def test_user_preferences_api():
    """Test the user preferences API endpoint"""
    print("🧪 Testing User Preferences API Fix")
    print("=" * 50)
    
    try:
        # Test data that matches what the frontend would send
        api_data = {
            "industry": "Fashion & Retail",
            "company_size": "small",  # Frontend value that should be transformed
            "marketing_goals": ["brand_awareness", "lead_generation"],
            "monthly_budget": "1000-5000"  # Frontend value that should be transformed
        }
        
        # Simulate a Clerk user ID
        headers = {
            "Content-Type": "application/json",
            "x-user-id": "api_test_user_456"
        }
        
        print(f"🔄 Testing POST to /api/v1/user-preferences/")
        print(f"Request data: {api_data}")
        print(f"Request headers: {headers}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://localhost:8000/api/v1/user-preferences/",
                headers=headers,
                json=api_data
            )
            
            print(f"\n📊 Response:")
            print(f"Status: {response.status_code}")
            print(f"Body: {response.text}")
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"\n✅ Success! User preferences saved:")
                print(f"   User ID: {response_data.get('user_id')}")
                print(f"   Industry: {response_data.get('industry')}")
                print(f"   Company Size: {response_data.get('company_size')} (transformed from 'small')")
                print(f"   Monthly Budget: {response_data.get('monthly_budget')} (transformed from '1000-5000')")
                print(f"   Marketing Goals: {response_data.get('marketing_goals')}")
                return True
            else:
                print(f"❌ Failed with status {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_user_preferences_api())
    
    if success:
        print("\n🎉 The user preferences API is now working correctly!")
        print("💡 The frontend onboarding error should be resolved.")
    else:
        print("\n⚠️  The test failed. Please check the server logs for more details.")
